from __future__ import annotations

from contextlib import closing
from datetime import datetime, timezone
import json
from pathlib import Path
import sqlite3
import uuid
import zipfile


def sqlite_snapshot(source: Path, target: Path) -> None:
    """SQLite's backup API includes committed WAL pages; never copy sidecars."""
    with closing(sqlite3.connect(source.resolve().as_uri() + "?mode=ro", uri=True)) as src:
        with closing(sqlite3.connect(target)) as dst:
            src.backup(dst)
            if dst.execute("PRAGMA quick_check").fetchone() != ("ok",):
                raise ValueError("SQLite-Prüfung fehlgeschlagen.")


def import_database(source: Path, data_root: Path) -> Path:
    """Explicit offline adoption, with snapshots of source and previous target."""
    source = source.resolve()
    if source.is_dir():
        source /= "metadata.sqlite"
    target = data_root / "metadata.sqlite"
    if not source.is_file() or source == target.resolve():
        raise ValueError("Bitte eine bestehende IMS-Datenbank außerhalb der neuen Ablage wählen.")
    backup = data_root / "backups" / (
        datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ-") + uuid.uuid4().hex[:8]
    )
    backup.mkdir(parents=True)
    imported = backup / "imported.sqlite"
    sqlite_snapshot(source, imported)
    with closing(sqlite3.connect(imported)) as db:
        tables = {row[0] for row in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        if not tables.intersection({"scenarios", "runs", "health_chain_results", "life_chain_results"}):
            raise ValueError("Die gewählte Datei enthält keine bekannten IMS-Datentabellen.")
    if target.exists():
        sqlite_snapshot(target, backup / "previous.sqlite")
    # Replace only after both backups succeeded and the offline lock is held.
    staging = data_root / "metadata.import.sqlite"
    sqlite_snapshot(imported, staging)
    if target.exists():
        with closing(sqlite3.connect(target)) as db:
            # Checkpoint safely; do not delete an old WAL before replacement.
            if db.execute("PRAGMA journal_mode=DELETE").fetchone() != ("delete",):
                raise ValueError("Vorige IMS-Datenbank konnte nicht geschlossen werden.")
    staging.replace(target)
    (backup / "adoption.json").write_text(json.dumps({
        "source": str(source), "target": str(target), "source_unchanged": True,
        "sqlite_backup_api": True,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    return backup


def export_diagnostics(data_root: Path, destination: Path, version: str) -> Path:
    """Support export excludes user databases, backups and the control token."""
    with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("diagnosis.json", json.dumps({
            "version": version, "database_present": (data_root / "metadata.sqlite").is_file(),
            "user_data_included": False, "control_token_included": False,
        }, indent=2))
        for log in sorted((data_root / "logs").glob("*.log*")):
            archive.write(log, "logs/" + log.name)
    return destination
