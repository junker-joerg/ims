from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path

from ims.api.metadata import METADATA_SCHEMA_VERSION
from ims.api.metadata_import import MetadataImportError
from ims.api.sqlite_readonly import readonly_sqlite_uri


@dataclass(frozen=True)
class RunControlExecutionAttemptRecord:
    attempt_id: str
    queue_id: str
    idempotency_key: str
    status: str
    released_by: str
    released_at: str
    release_reason: str
    started_at: str
    completed_at: str | None
    failure_message: str | None
    adapter_started: bool
    result_persisted: bool
    simulation_performed: bool

    def to_dict(self) -> dict[str, object]:
        return {
            "attempt_id": self.attempt_id,
            "queue_id": self.queue_id,
            "idempotency_key": self.idempotency_key,
            "status": self.status,
            "released_by": self.released_by,
            "released_at": self.released_at,
            "release_reason": self.release_reason,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "failure_message": self.failure_message,
            "adapter_started": self.adapter_started,
            "result_persisted": self.result_persisted,
            "simulation_performed": self.simulation_performed,
        }


@dataclass(frozen=True)
class RunControlExecutionHistoryResult:
    db_path: str
    queue_id: str
    queue_status: str
    attempts: tuple[RunControlExecutionAttemptRecord, ...]
    persisted_result_available: bool
    persisted_at: str | None
    mode: str = "run_control_execution_history"

    def to_dict(self) -> dict[str, object]:
        latest_attempt = self.attempts[0] if self.attempts else None
        return {
            "status": "ok",
            "mode": self.mode,
            "schema_version": METADATA_SCHEMA_VERSION,
            "db_path": self.db_path,
            "queue_id": self.queue_id,
            "queue_status": self.queue_status,
            "attempt_count": len(self.attempts),
            "attempts": [attempt.to_dict() for attempt in self.attempts],
            "latest_attempt": latest_attempt.to_dict() if latest_attempt is not None else None,
            "persisted_result_available": self.persisted_result_available,
            "persisted_at": self.persisted_at,
            "automatic_retry_enabled": False,
            "queue_worker_enabled": False,
            "writes_performed": False,
            "execution_performed": False,
            "adapter_started": False,
            "simulation_performed": False,
            "automatic_historical_rule_selection_performed": False,
            "historical_full_equality_claimed": False,
        }


def get_run_control_execution_history(
    queue_id: str,
    *,
    db_path: Path | str,
) -> RunControlExecutionHistoryResult:
    if not queue_id.strip():
        raise MetadataImportError("run control queue id must not be empty")
    resolved_path = Path(db_path).expanduser().resolve()
    if not resolved_path.is_file():
        raise MetadataImportError(f"run control execution history database does not exist: {resolved_path}")

    connection = sqlite3.connect(
        readonly_sqlite_uri(resolved_path, description="run control execution history"),
        uri=True,
        check_same_thread=False,
    )
    connection.row_factory = sqlite3.Row
    try:
        queue_row = connection.execute(
            "SELECT queue_id, status FROM run_control_queue WHERE queue_id = ?",
            (queue_id,),
        ).fetchone()
        if queue_row is None:
            raise MetadataImportError(f"run control queue entry not found: {queue_id}")

        attempts = _read_attempts(connection, queue_id)
        result_row = _read_persisted_result(connection, queue_id)
    except sqlite3.DatabaseError as exc:
        raise MetadataImportError(
            f"run control execution history database is not readable or initialized: {exc}"
        ) from exc
    finally:
        connection.close()

    return RunControlExecutionHistoryResult(
        db_path=str(resolved_path),
        queue_id=str(queue_row["queue_id"]),
        queue_status=str(queue_row["status"]),
        attempts=attempts,
        persisted_result_available=result_row is not None,
        persisted_at=str(result_row["persisted_at"]) if result_row is not None else None,
    )


def _read_attempts(
    connection: sqlite3.Connection,
    queue_id: str,
) -> tuple[RunControlExecutionAttemptRecord, ...]:
    if not _table_exists(connection, "run_control_execution_attempts"):
        return ()
    rows = connection.execute(
        """
        SELECT
            attempt_id,
            queue_id,
            idempotency_key,
            status,
            released_by,
            released_at,
            release_reason,
            started_at,
            completed_at,
            failure_message,
            adapter_started,
            result_persisted,
            simulation_performed
        FROM run_control_execution_attempts
        WHERE queue_id = ?
        ORDER BY started_at DESC, attempt_id DESC
        """,
        (queue_id,),
    ).fetchall()
    return tuple(_row_to_attempt(row) for row in rows)


def _read_persisted_result(connection: sqlite3.Connection, queue_id: str) -> sqlite3.Row | None:
    if not _table_exists(connection, "run_control_execution_results"):
        return None
    return connection.execute(
        "SELECT persisted_at FROM run_control_execution_results WHERE queue_id = ?",
        (queue_id,),
    ).fetchone()


def _table_exists(connection: sqlite3.Connection, table_name: str) -> bool:
    row = connection.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?",
        (table_name,),
    ).fetchone()
    return row is not None


def _row_to_attempt(row: sqlite3.Row) -> RunControlExecutionAttemptRecord:
    return RunControlExecutionAttemptRecord(
        attempt_id=str(row["attempt_id"]),
        queue_id=str(row["queue_id"]),
        idempotency_key=str(row["idempotency_key"]),
        status=str(row["status"]),
        released_by=str(row["released_by"]),
        released_at=str(row["released_at"]),
        release_reason=str(row["release_reason"]),
        started_at=str(row["started_at"]),
        completed_at=str(row["completed_at"]) if row["completed_at"] is not None else None,
        failure_message=str(row["failure_message"]) if row["failure_message"] is not None else None,
        adapter_started=bool(row["adapter_started"]),
        result_persisted=bool(row["result_persisted"]),
        simulation_performed=bool(row["simulation_performed"]),
    )
