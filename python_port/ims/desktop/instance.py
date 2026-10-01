from __future__ import annotations

import json
from pathlib import Path
import time
from urllib.error import URLError
from urllib.request import Request, build_opener, ProxyHandler


class InstanceLock:
    """Per-user OS lock, automatically released if the process crashes."""

    def __init__(self, root: Path) -> None:
        self.path = root / "instance.lock"
        self.file = None

    def acquire(self) -> bool:
        import msvcrt

        handle = self.path.open("a+b")
        if self.path.stat().st_size == 0:
            handle.write(b"0")
            handle.flush()
        handle.seek(0)
        try:
            msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
        except OSError:
            handle.close()
            return False
        self.file = handle
        return True

    def release(self) -> None:
        if self.file is not None:
            import msvcrt

            self.file.seek(0)
            msvcrt.locking(self.file.fileno(), msvcrt.LK_UNLCK, 1)
            self.file.close()
            self.file = None


def local_request(url: str, *, token: str | None = None, command: str | None = None) -> dict:
    headers = {"X-IMS-Desktop-Token": token} if token else {}
    request = Request(url, data=command.encode() if command else None, headers=headers)
    # Corporate proxies and inherited HTTP_PROXY must never intercept Loopback.
    with build_opener(ProxyHandler({})).open(request, timeout=1) as response:
        return json.load(response)


def existing_instance(root: Path, command: str, timeout: float = 20) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            state = json.loads((root / "instance.json").read_text(encoding="utf-8"))
            port = state["port"]
            if not isinstance(port, int) or not 1 <= port <= 65535:
                raise ValueError("Ungültiger Port")
            reply = local_request(
                f"http://127.0.0.1:{port}/_desktop/control",
                token=state["token"], command=command,
            )
            if reply.get("service") == "ims-desktop":
                return True
        except (OSError, ValueError, KeyError, URLError):
            time.sleep(0.1)
    return False
