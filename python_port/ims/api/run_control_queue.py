from __future__ import annotations

import argparse
import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from ims.api.metadata import METADATA_SCHEMA_VERSION
from ims.api.metadata_import import MetadataImportError
from ims.api.metadata_repository import connect_metadata_db, metadata_source_payload
from ims.api.run_control_requests import (
    WorkbenchRunControlRequest,
    validate_run_control_request,
    validate_run_control_request_payload,
)
from ims.api.sqlite_readonly import readonly_sqlite_uri


RUN_CONTROL_QUEUE_SCHEMA = """
CREATE TABLE IF NOT EXISTS run_control_queue (
    queue_id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL,
    scenario_id TEXT NOT NULL,
    metadata_db TEXT,
    requested_by TEXT NOT NULL,
    created_at TEXT NOT NULL,
    status TEXT NOT NULL,
    execution_enabled INTEGER NOT NULL CHECK (execution_enabled IN (0, 1)),
    execution_performed INTEGER NOT NULL CHECK (execution_performed IN (0, 1))
)
"""
RUN_CONTROL_QUEUE_STATUSES = ("planned", "blocked", "validated")


@dataclass(frozen=True)
class WorkbenchRunControlQueueEntry:
    queue_id: str
    request: WorkbenchRunControlRequest
    status: str
    execution_performed: bool = False

    def to_dict(self) -> dict[str, object]:
        return {
            "queue_id": self.queue_id,
            "request": self.request.to_dict(),
            "status": self.status,
            "execution_enabled": self.request.execution_enabled,
            "execution_performed": self.execution_performed,
        }


@dataclass(frozen=True)
class WorkbenchRunControlQueueResult:
    mode: str
    db_path: str
    entry: WorkbenchRunControlQueueEntry | None = None
    entries: tuple[WorkbenchRunControlQueueEntry, ...] = ()
    writes_performed: bool = False
    execution_performed: bool = False

    def to_dict(self) -> dict[str, object]:
        payload: dict[str, object] = {
            "status": "ok",
            "mode": self.mode,
            "schema_version": METADATA_SCHEMA_VERSION,
            "db_path": self.db_path,
            "writes_performed": self.writes_performed,
            "execution_performed": self.execution_performed,
        }
        if self.entry is not None:
            payload["entry"] = self.entry.to_dict()
        payload["entries"] = [entry.to_dict() for entry in self.entries]
        return payload


class WorkbenchRunControlQueueRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def metadata_source(self) -> dict[str, object]:
        return metadata_source_payload(_connection_path(self._connection))

    def initialize(self) -> None:
        with self._connection:
            self._connection.execute(RUN_CONTROL_QUEUE_SCHEMA)

    def enqueue(self, request: WorkbenchRunControlRequest, *, status: str = "planned") -> WorkbenchRunControlQueueEntry:
        _validate_queue_status(status)
        if request.execution_enabled:
            raise MetadataImportError("run control queue refuses execution_enabled=true")
        entry = WorkbenchRunControlQueueEntry(
            queue_id=request.run_id,
            request=request,
            status=status,
        )
        self.initialize()
        with self._connection:
            self._connection.execute(
                """
                INSERT INTO run_control_queue (
                    queue_id,
                    run_id,
                    scenario_id,
                    metadata_db,
                    requested_by,
                    created_at,
                    status,
                    execution_enabled,
                    execution_performed
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(queue_id) DO UPDATE SET
                    run_id = excluded.run_id,
                    scenario_id = excluded.scenario_id,
                    metadata_db = excluded.metadata_db,
                    requested_by = excluded.requested_by,
                    created_at = excluded.created_at,
                    status = excluded.status,
                    execution_enabled = excluded.execution_enabled,
                    execution_performed = excluded.execution_performed
                """,
                _entry_values(entry),
            )
        return entry

    def list_entries(self) -> tuple[WorkbenchRunControlQueueEntry, ...]:
        try:
            rows = self._connection.execute(
                """
                SELECT
                    queue_id,
                    run_id,
                    scenario_id,
                    metadata_db,
                    requested_by,
                    created_at,
                    status,
                    execution_enabled,
                    execution_performed
                FROM run_control_queue
                ORDER BY queue_id
                """
            ).fetchall()
        except sqlite3.DatabaseError as exc:
            raise MetadataImportError(f"run control queue database is not readable or initialized: {exc}") from exc
        return tuple(_row_to_entry(row) for row in rows)

    def get_entry(self, queue_id: str) -> WorkbenchRunControlQueueEntry | None:
        try:
            row = self._connection.execute(
                """
                SELECT
                    queue_id,
                    run_id,
                    scenario_id,
                    metadata_db,
                    requested_by,
                    created_at,
                    status,
                    execution_enabled,
                    execution_performed
                FROM run_control_queue
                WHERE queue_id = ?
                """,
                (queue_id,),
            ).fetchone()
        except sqlite3.DatabaseError as exc:
            raise MetadataImportError(f"run control queue database is not readable or initialized: {exc}") from exc
        if row is None:
            return None
        return _row_to_entry(row)


def initialize_run_control_queue(db_path: Path | str) -> WorkbenchRunControlQueueResult:
    repository = _queue_repository(db_path, create=True)
    repository.initialize()
    return WorkbenchRunControlQueueResult(
        mode="run_control_queue_init",
        db_path=str(Path(db_path).expanduser().resolve()),
        writes_performed=True,
    )


def enqueue_run_control_request(
    path: Path | str,
    *,
    db_path: Path | str,
) -> WorkbenchRunControlQueueResult:
    request = validate_run_control_request(path).request
    return enqueue_run_control_request_object(request, db_path=db_path)


def enqueue_run_control_request_payload(
    payload: object,
    *,
    db_path: Path | str,
) -> WorkbenchRunControlQueueResult:
    request = validate_run_control_request_payload(payload).request
    return enqueue_run_control_request_object(request, db_path=db_path)


def enqueue_run_control_request_object(
    request: WorkbenchRunControlRequest,
    *,
    db_path: Path | str,
) -> WorkbenchRunControlQueueResult:
    repository = _queue_repository(db_path, create=True)
    entry = repository.enqueue(request)
    return WorkbenchRunControlQueueResult(
        mode="run_control_queue_enqueue",
        db_path=str(Path(db_path).expanduser().resolve()),
        entry=entry,
        writes_performed=True,
    )


def list_run_control_queue(db_path: Path | str) -> WorkbenchRunControlQueueResult:
    repository = _queue_repository(db_path, create=False)
    return WorkbenchRunControlQueueResult(
        mode="run_control_queue_list",
        db_path=str(Path(db_path).expanduser().resolve()),
        entries=repository.list_entries(),
    )


def get_run_control_queue_entry(queue_id: str, *, db_path: Path | str) -> WorkbenchRunControlQueueResult:
    if not queue_id.strip():
        raise MetadataImportError("run control queue id must not be empty")
    repository = _queue_repository(db_path, create=False)
    entry = repository.get_entry(queue_id)
    if entry is None:
        raise MetadataImportError(f"run control queue entry not found: {queue_id}")
    return WorkbenchRunControlQueueResult(
        mode="run_control_queue_show",
        db_path=str(Path(db_path).expanduser().resolve()),
        entry=entry,
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "init":
            _print_json(initialize_run_control_queue(args.db).to_dict())
        elif args.command == "enqueue":
            _print_json(enqueue_run_control_request(args.path, db_path=args.db).to_dict())
        elif args.command == "list":
            _print_json(list_run_control_queue(args.db).to_dict())
        elif args.command == "show":
            _print_json(get_run_control_queue_entry(args.queue_id, db_path=args.db).to_dict())
        else:  # pragma: no cover - argparse prevents this branch
            raise MetadataImportError(f"unsupported run control queue command: {args.command}")
    except MetadataImportError as exc:
        _print_json(
            {
                "status": "error",
                "mode": f"run_control_queue_{args.command}",
                "message": str(exc),
                "issues": [str(exc)],
                "writes_performed": False,
                "execution_performed": False,
            }
        )
        return 2
    return 0


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m ims.api.run_control_queue",
        description="Verwaltet lokale Run-Control-Queue-Metadaten ohne Ausfuehrung.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="Queue-Schema in expliziter SQLite-Datei anlegen.")
    init_parser.add_argument("--db", required=True, type=Path, help="Expliziter SQLite-Zielpfad.")

    enqueue_parser = subparsers.add_parser("enqueue", help="Validierten Request in die Queue schreiben.")
    enqueue_parser.add_argument("path", type=Path, help="Run-Control-Request-JSON.")
    enqueue_parser.add_argument("--db", required=True, type=Path, help="Expliziter SQLite-Zielpfad.")

    list_parser = subparsers.add_parser("list", help="Queue lesend auflisten.")
    list_parser.add_argument("--db", required=True, type=Path, help="Expliziter SQLite-Quellpfad.")

    show_parser = subparsers.add_parser("show", help="Queue-Eintrag lesend anzeigen.")
    show_parser.add_argument("queue_id", help="Queue-ID.")
    show_parser.add_argument("--db", required=True, type=Path, help="Expliziter SQLite-Quellpfad.")
    return parser


def _queue_repository(db_path: Path | str, *, create: bool) -> WorkbenchRunControlQueueRepository:
    resolved_path = Path(db_path).expanduser().resolve()
    if not create and not resolved_path.is_file():
        raise MetadataImportError(f"run control queue database does not exist: {resolved_path}")
    connection = connect_metadata_db(resolved_path) if create else _connect_queue_db_readonly(resolved_path)
    return WorkbenchRunControlQueueRepository(connection)


def _connect_queue_db_readonly(path: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(
        _readonly_queue_sqlite_uri(path),
        uri=True,
        check_same_thread=False,
    )
    connection.row_factory = sqlite3.Row
    return connection


def _readonly_queue_sqlite_uri(path: Path) -> str:
    return readonly_sqlite_uri(path, description="run control queue")


def _validate_queue_status(status: str) -> None:
    if status not in RUN_CONTROL_QUEUE_STATUSES:
        raise MetadataImportError(f"run control queue status is not supported: {status}")


def _entry_values(entry: WorkbenchRunControlQueueEntry) -> tuple[object, ...]:
    return (
        entry.queue_id,
        entry.request.run_id,
        entry.request.scenario_id,
        entry.request.metadata_db,
        entry.request.requested_by,
        entry.request.created_at,
        entry.status,
        int(entry.request.execution_enabled),
        int(entry.execution_performed),
    )


def _row_to_entry(row: sqlite3.Row) -> WorkbenchRunControlQueueEntry:
    request = WorkbenchRunControlRequest(
        run_id=row["run_id"],
        scenario_id=row["scenario_id"],
        metadata_db=row["metadata_db"],
        requested_by=row["requested_by"],
        created_at=row["created_at"],
        execution_enabled=bool(row["execution_enabled"]),
    )
    return WorkbenchRunControlQueueEntry(
        queue_id=row["queue_id"],
        request=request,
        status=row["status"],
        execution_performed=bool(row["execution_performed"]),
    )


def _connection_path(connection: sqlite3.Connection) -> Path | str:
    rows = connection.execute("PRAGMA database_list").fetchall()
    for row in rows:
        if row["name"] == "main":
            file_path = row["file"]
            if file_path:
                return Path(file_path).resolve()
    return ":memory:"


def _print_json(payload: dict[str, object]) -> None:
    print(json.dumps(payload, ensure_ascii=True, sort_keys=True))


if __name__ == "__main__":
    raise SystemExit(main())
