from __future__ import annotations

import argparse
import hmac
import json
import logging
from logging.handlers import RotatingFileHandler
import os
from pathlib import Path
import secrets
import socket
import sys
import threading
import time
import webbrowser

from ims.desktop.data import export_diagnostics, import_database
from ims.desktop.instance import InstanceLock, existing_instance, local_request
from ims.desktop.paths import resource_root, user_root


def bind_loopback(port: int) -> socket.socket:
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if hasattr(socket, "SO_EXCLUSIVEADDRUSE"):
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
    try:
        listener.bind(("127.0.0.1", port))
        listener.listen(128)
        listener.setblocking(False)
        return listener
    except OSError:
        listener.close()
        raise RuntimeError(
            f"Port {port} wird bereits verwendet. Die andere Anwendung schließen "
            "oder IMS mit einem anderen lokalen Port starten."
        ) from None


def configure_logging(root: Path) -> None:
    logs = root / "logs"
    logs.mkdir(exist_ok=True)
    handler = RotatingFileHandler(logs / "desktop.log", maxBytes=1_000_000,
                                  backupCount=3, encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logging.basicConfig(level=logging.INFO, handlers=[handler], force=True)


def wait_ready(url: str, thread: threading.Thread, timeout: float = 30) -> None:
    deadline = time.monotonic() + timeout
    while thread.is_alive() and time.monotonic() < deadline:
        try:
            health = local_request(url + "api/health")
            if (health.get("service") == "ims-workbench-api"
                    and health.get("status") == "ok" and health.get("frontend_available")):
                return
        except (OSError, ValueError):
            pass
        time.sleep(0.1)
    raise RuntimeError("IMS konnte nicht starten. Details stehen im Diagnoseprotokoll.")


def add_controls(app: object, server: object, token: str, url: str) -> None:
    from starlette.responses import JSONResponse
    from starlette.routing import Route

    async def control(request):
        supplied = request.headers.get("X-IMS-Desktop-Token", "")
        if not hmac.compare_digest(supplied, token):
            return JSONResponse({"error": "forbidden"}, status_code=403)
        command = (await request.body()).decode("ascii", errors="replace")
        if command == "stop":
            server.should_exit = True
        elif command == "open":
            webbrowser.open(url)
        elif command != "ping":
            return JSONResponse({"error": "unknown_command"}, status_code=400)
        return JSONResponse({"service": "ims-desktop", "command": command})

    app.router.routes.insert(0, Route("/_desktop/control", control, methods=["POST"]))


def show_window(server: object, thread: threading.Thread, url: str,
                data_root: Path, version: str) -> None:
    import tkinter as tk
    from tkinter import filedialog, messagebox, ttk

    window = tk.Tk()
    window.title("IMS Workbench")
    window.geometry("490x300")
    window.minsize(490, 300)
    frame = ttk.Frame(window, padding=24)
    frame.pack(fill="both", expand=True)
    ttk.Label(frame, text="IMS Workbench", font=("Segoe UI", 18)).pack(anchor="w")
    status = ttk.Label(frame, text="IMS läuft lokal. Dieses Fenster beendet die Anwendung.")
    status.pack(anchor="w", pady=(12, 16))
    ttk.Button(frame, text="Oberfläche öffnen", command=lambda: webbrowser.open(url)).pack(fill="x", pady=4)

    def diagnose():
        path = filedialog.asksaveasfilename(title="Diagnose speichern", defaultextension=".zip",
                                          initialfile="IMS-Diagnose.zip")
        if path:
            try:
                export_diagnostics(data_root, Path(path), version)
                messagebox.showinfo("IMS", "Diagnose gespeichert. Modell- und Nutzerdaten sind nicht enthalten.")
            except OSError as exc:
                messagebox.showerror("IMS", f"Diagnose konnte nicht gespeichert werden: {exc}")

    ttk.Button(frame, text="Diagnose exportieren", command=diagnose).pack(fill="x", pady=4)
    ttk.Button(frame, text="Hilfe öffnen", command=lambda: os.startfile(
        resource_root() / "help.html"
    )).pack(fill="x", pady=4)

    def close():
        status.configure(text="IMS wird beendet. Laufende Berechnungen dürfen abschließen.")
        server.should_exit = True

    ttk.Button(frame, text="IMS beenden", command=close).pack(fill="x", pady=4)
    window.protocol("WM_DELETE_WINDOW", close)

    def poll():
        if not thread.is_alive():
            window.destroy()
        else:
            window.after(150, poll)

    window.after(150, poll)
    window.mainloop()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="IMS Workbench für Windows")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--data-dir", type=Path, help="Separate Test-/Benutzerablage")
    parser.add_argument("--headless", action="store_true", help="Automatisierte Abnahme ohne Fenster")
    parser.add_argument("--no-browser", action="store_true")
    parser.add_argument("--stop", action="store_true")
    parser.add_argument("--diagnostics", type=Path)
    parser.add_argument("--import-data", type=Path)
    parser.add_argument("--choose-import", action="store_true")
    args = parser.parse_args(argv)
    lock = None
    thread = None
    listener = None
    server = None
    owned = False
    root = None
    try:
        if not 1 <= args.port <= 65535:
            raise ValueError("Port muss zwischen 1 und 65535 liegen.")
        root = user_root(args.data_dir)
        if args.diagnostics:
            from ims.api.app import APP_VERSION

            export_diagnostics(root, args.diagnostics, APP_VERSION)
            return 0
        if args.stop:
            lock = InstanceLock(root)
            if lock.acquire():
                return 0  # Already stopped; stale state is never used to stop another process.
            if not existing_instance(root, "stop"):
                raise RuntimeError("Laufende IMS-Instanz antwortet nicht. Bitte über ihr Fenster beenden.")
            deadline = time.monotonic() + 60
            while not lock.acquire():
                if time.monotonic() >= deadline:
                    raise RuntimeError("IMS rechnet noch. Update/Deinstallation bitte später erneut ausführen.")
                time.sleep(0.1)
            return 0
        lock = InstanceLock(root)
        if not lock.acquire():
            if args.import_data or args.choose_import:
                raise RuntimeError("IMS vor der Datenübernahme über sein Fenster beenden.")
            if not existing_instance(root, "ping" if args.no_browser else "open"):
                raise RuntimeError("IMS startet bereits oder antwortet nicht. Diagnoseprotokoll prüfen.")
            return 0
        owned = True
        configure_logging(root)
        from ims.api.app import APP_VERSION

        if args.choose_import:
            import tkinter as tk
            from tkinter import filedialog, messagebox

            picker = tk.Tk()
            picker.withdraw()
            chosen = filedialog.askopenfilename(title="Bestehende IMS-Datenbank wählen",
                                               filetypes=[("SQLite-Datenbank", "*.sqlite")])
            if not chosen or not messagebox.askyesno("Datenübernahme", "Bestehende Daten übernehmen? "
                    "Die aktuelle Datenbank wird vorher gesichert. Alte IMS-Anwendung zuerst beenden."):
                picker.destroy()
                return 0
            args.import_data = Path(chosen)
            picker.destroy()
        if args.import_data:
            backup = import_database(args.import_data, root)
            logging.info("Explizite Datenübernahme abgeschlossen; Backup: %s", backup.name)
            return 0
        resources = resource_root()
        frontend = resources / "frontend" / "dist"
        if not (frontend / "index.html").is_file():
            raise RuntimeError("Anwendungsdateien fehlen. IMS bitte neu installieren; Nutzerdaten bleiben erhalten.")
        # Existing diagnostic APIs deliberately use repository-relative resources.
        # Their read-only fixture semantics stay unchanged in the distribution.
        os.chdir(resources)
        os.environ["IMS_METADATA_DB"] = str(root / "metadata.sqlite")
        os.environ["IMS_FRONTEND_DIST"] = str(frontend)
        from ims.api.app import create_app
        import uvicorn

        try:
            listener = bind_loopback(args.port)
        except RuntimeError:
            if args.headless:
                raise
            import tkinter as tk
            from tkinter import simpledialog
            picker = tk.Tk()
            picker.withdraw()
            port = simpledialog.askinteger("Port bereits belegt", "Anderen lokalen Port für IMS wählen:",
                                           initialvalue=8001, minvalue=1, maxvalue=65535)
            picker.destroy()
            if port is None:
                return 1
            listener = bind_loopback(port)
        port = listener.getsockname()[1]
        url = f"http://127.0.0.1:{port}/"
        token = secrets.token_hex(32)
        app = create_app(frontend_dist=frontend)
        server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=port,
            loop="asyncio", http="h11", ws="none", log_config=None, access_log=False,
            timeout_graceful_shutdown=30))
        add_controls(app, server, token, url)
        thread = threading.Thread(target=server.run, kwargs={"sockets": [listener]}, name="ims-backend")
        thread.start()
        wait_ready(url, thread)
        state = root / "instance.new.json"
        state.write_text(json.dumps({"port": port, "token": token, "pid": os.getpid(),
                                    "version": APP_VERSION}), encoding="utf-8")
        state.replace(root / "instance.json")
        logging.info("IMS %s bereit auf Loopback-Port %s", APP_VERSION, port)
        if not args.no_browser:
            webbrowser.open(url)
        if args.headless:
            while thread.is_alive():
                thread.join(0.2)
        else:
            show_window(server, thread, url, root, APP_VERSION)
        return 0
    except Exception as exc:
        logging.exception("IMS-Start fehlgeschlagen")
        if args.headless:
            if sys.stderr is not None:
                print(str(exc), file=sys.stderr)
        else:
            import tkinter.messagebox
            tkinter.messagebox.showerror("IMS konnte nicht starten", str(exc))
        return 1
    finally:
        if server is not None:
            server.should_exit = True
        if thread is not None:
            thread.join()  # Do not release the instance lock while calculations still run.
        if listener is not None:
            listener.close()
        if owned and root is not None:
            (root / "instance.json").unlink(missing_ok=True)
        if lock is not None:
            lock.release()


if __name__ == "__main__":
    raise SystemExit(main())
