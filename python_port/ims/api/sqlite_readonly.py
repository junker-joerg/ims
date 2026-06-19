from __future__ import annotations

from pathlib import Path

from ims.api.metadata_import import MetadataImportError


def readonly_sqlite_uri(path: Path, *, description: str) -> str:
    wal_exists, shm_exists = _sqlite_sidecar_state(path)
    if wal_exists != shm_exists:
        raise MetadataImportError(f"{description} database has incomplete WAL sidecar state")
    if wal_exists and shm_exists:
        return f"{path.as_uri()}?mode=ro"
    if _sqlite_file_uses_wal(path, description=description):
        return f"{path.as_uri()}?mode=ro&immutable=1"
    return f"{path.as_uri()}?mode=ro"


def _sqlite_sidecar_state(path: Path) -> tuple[bool, bool]:
    return Path(f"{path}-wal").exists(), Path(f"{path}-shm").exists()


def _sqlite_file_uses_wal(path: Path, *, description: str = "SQLite read-only") -> bool:
    try:
        with path.open("rb") as db_file:
            header = db_file.read(20)
    except OSError as exc:
        raise MetadataImportError(f"{description} database header is not readable: {exc}") from exc
    if len(header) < 20 or not header.startswith(b"SQLite format 3\x00"):
        return False
    return header[18] == 2 and header[19] == 2
