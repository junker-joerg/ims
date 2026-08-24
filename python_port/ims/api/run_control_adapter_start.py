from __future__ import annotations

import hashlib
import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Mapping, Protocol

from ims.api.controlled_execution_adapter import ControlledExecutionAdapterResult
from ims.api.metadata import METADATA_SCHEMA_VERSION
from ims.api.metadata_import import MetadataImportError
from ims.api.metadata_repository import connect_metadata_db
from ims.api.run_control_adapter_result_contract import (
    validate_run_control_adapter_result_payload,
)
from ims.api.run_control_execution_release import RunControlExecutionReleaseResult
from ims.api.run_control_execution_result_store import (
    RUN_CONTROL_EXECUTION_RESULT_SCHEMA,
    RunControlExecutionResultRecord,
    build_run_control_execution_result_record,
    get_run_control_execution_result,
    upsert_run_control_execution_result_record,
)


RUN_CONTROL_EXECUTION_ATTEMPT_SCHEMA = """
CREATE TABLE IF NOT EXISTS run_control_execution_attempts (
    attempt_id TEXT PRIMARY KEY,
    queue_id TEXT NOT NULL,
    idempotency_key TEXT NOT NULL,
    request_fingerprint TEXT NOT NULL,
    status TEXT NOT NULL,
    released_by TEXT NOT NULL,
    released_at TEXT NOT NULL,
    release_reason TEXT NOT NULL,
    started_at TEXT NOT NULL,
    completed_at TEXT,
    failure_message TEXT,
    adapter_started INTEGER NOT NULL CHECK (adapter_started IN (0, 1)),
    result_persisted INTEGER NOT NULL CHECK (result_persisted IN (0, 1)),
    simulation_performed INTEGER NOT NULL CHECK (simulation_performed IN (0, 1)),
    UNIQUE(queue_id, idempotency_key)
)
"""


class AdapterRunner(Protocol):
    def __call__(
        self,
        fixture_path: str | Path,
        *,
        adapter_mode: str,
        explicit_execution_release: bool,
        carry_forward_vu_state: bool,
        carry_forward_vn_state: bool,
    ) -> ControlledExecutionAdapterResult | Mapping[str, object]:
        ...


class RunControlAdapterStartError(MetadataImportError):
    def __init__(self, message: str, *, adapter_started: bool) -> None:
        super().__init__(message)
        self.adapter_started = adapter_started
        self.writes_performed = adapter_started


@dataclass(frozen=True)
class RunControlAdapterStartResult:
    attempt_id: str
    queue_id: str
    idempotency_key: str
    record: RunControlExecutionResultRecord
    replayed: bool
    completed_at: str
    mode: str = "run_control_adapter_start"

    def to_dict(self) -> dict[str, object]:
        return {
            "status": "ok",
            "mode": self.mode,
            "schema_version": METADATA_SCHEMA_VERSION,
            "attempt_id": self.attempt_id,
            "queue_id": self.queue_id,
            "idempotency_key": self.idempotency_key,
            "replayed": self.replayed,
            "queue_status": "result_persisted",
            "completed_at": self.completed_at,
            "record": self.record.to_dict(),
            "adapter_started": not self.replayed,
            "result_persisted": True,
            "writes_performed": not self.replayed,
            "execution_performed": True,
            "simulation_performed": self.record.simulation_performed,
            "automatic_historical_rule_selection_performed": (
                self.record.automatic_historical_rule_selection_performed
            ),
            "historical_full_equality_claimed": self.record.historical_full_equality_claimed,
        }


def start_run_control_adapter(
    release: RunControlExecutionReleaseResult,
    *,
    db_path: Path | str,
    adapter_runner: AdapterRunner,
    timestamp_factory: Callable[[], str] = lambda: _utc_now(),
) -> RunControlAdapterStartResult:
    request = release.request
    resolved_db_path = Path(db_path).expanduser().resolve()
    fingerprint = _request_fingerprint(request.to_dict())
    attempt_id = _attempt_id(request.queue_id, request.idempotency_key)
    started_at = timestamp_factory()

    replay = _claim_or_replay(
        release,
        db_path=resolved_db_path,
        attempt_id=attempt_id,
        fingerprint=fingerprint,
        started_at=started_at,
    )
    if replay is not None:
        return replay

    profile = release.profile
    if profile is None:  # guarded by release_ready, retained as a defensive boundary
        raise MetadataImportError("run control adapter start requires a known release profile")

    try:
        raw_result = adapter_runner(
            profile.fixture_path,
            adapter_mode=request.expected_adapter_mode,
            explicit_execution_release=True,
            carry_forward_vu_state=request.carry_forward_vu_state,
            carry_forward_vn_state=request.carry_forward_vn_state,
        )
        payload = _adapter_result_payload(raw_result)
        validation = validate_run_control_adapter_result_payload(payload)
        if not validation.result_accepted:
            codes = ", ".join(issue.code for issue in validation.issues)
            raise MetadataImportError(f"adapter result does not match the Run-Control contract: {codes}")
        _validate_result_against_release(payload, release)
        completed_at = timestamp_factory()
        record = _complete_attempt(
            request.queue_id,
            attempt_id,
            payload,
            validation.to_dict(),
            completed_at,
            db_path=resolved_db_path,
        )
    except Exception as exc:
        _fail_attempt(
            request.queue_id,
            attempt_id,
            str(exc),
            timestamp_factory(),
            db_path=resolved_db_path,
        )
        message = (
            str(exc)
            if isinstance(exc, MetadataImportError)
            else f"run control adapter start failed: {exc}"
        )
        raise RunControlAdapterStartError(message, adapter_started=True) from exc

    return RunControlAdapterStartResult(
        attempt_id=attempt_id,
        queue_id=request.queue_id,
        idempotency_key=request.idempotency_key,
        record=record,
        replayed=False,
        completed_at=completed_at,
    )


def _claim_or_replay(
    release: RunControlExecutionReleaseResult,
    *,
    db_path: Path,
    attempt_id: str,
    fingerprint: str,
    started_at: str,
) -> RunControlAdapterStartResult | None:
    request = release.request
    connection = connect_metadata_db(db_path)
    try:
        connection.execute("BEGIN IMMEDIATE")
        connection.execute(RUN_CONTROL_EXECUTION_ATTEMPT_SCHEMA)
        connection.execute(RUN_CONTROL_EXECUTION_RESULT_SCHEMA)
        existing = connection.execute(
            """
            SELECT request_fingerprint, status, completed_at
            FROM run_control_execution_attempts
            WHERE queue_id = ? AND idempotency_key = ?
            """,
            (request.queue_id, request.idempotency_key),
        ).fetchone()
        if existing is not None:
            if existing["request_fingerprint"] != fingerprint:
                raise MetadataImportError(
                    "idempotency key was already used with a different release payload"
                )
            if existing["status"] != "result_persisted":
                raise MetadataImportError(
                    f"run control adapter attempt is already {existing['status']}"
                )
            connection.commit()
            stored = get_run_control_execution_result(request.queue_id, db_path=db_path)
            if stored.record is None:  # pragma: no cover - schema invariant
                raise MetadataImportError("persisted adapter attempt has no result record")
            return RunControlAdapterStartResult(
                attempt_id=attempt_id,
                queue_id=request.queue_id,
                idempotency_key=request.idempotency_key,
                record=stored.record,
                replayed=True,
                completed_at=str(existing["completed_at"]),
            )

        if not release.release_ready:
            raise MetadataImportError(
                "run control adapter start requires a passing execution release check"
            )
        queue_row = connection.execute(
            """
            SELECT status, execution_enabled, execution_performed
            FROM run_control_queue
            WHERE queue_id = ?
            """,
            (request.queue_id,),
        ).fetchone()
        if queue_row is None:
            raise MetadataImportError(f"run control queue entry not found: {request.queue_id}")
        if queue_row["status"] != "validated":
            raise MetadataImportError("run control adapter start requires queue status validated")
        if bool(queue_row["execution_enabled"]) or bool(queue_row["execution_performed"]):
            raise MetadataImportError("run control queue entry is not eligible for adapter start")

        connection.execute(
            """
            INSERT INTO run_control_execution_attempts (
                attempt_id, queue_id, idempotency_key, request_fingerprint, status,
                released_by, released_at, release_reason, started_at, completed_at,
                failure_message, adapter_started, result_persisted, simulation_performed
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, NULL, NULL, 1, 0, 0)
            """,
            (
                attempt_id,
                request.queue_id,
                request.idempotency_key,
                fingerprint,
                "starting",
                request.released_by,
                request.released_at,
                request.release_reason,
                started_at,
            ),
        )
        updated = connection.execute(
            """
            UPDATE run_control_queue
            SET status = 'starting'
            WHERE queue_id = ? AND status = 'validated' AND execution_performed = 0
            """,
            (request.queue_id,),
        )
        if updated.rowcount != 1:  # pragma: no cover - protected by BEGIN IMMEDIATE
            raise MetadataImportError("run control adapter start lost its atomic queue claim")
        connection.commit()
        return None
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def _complete_attempt(
    queue_id: str,
    attempt_id: str,
    payload: dict[str, object],
    validation_payload: dict[str, object],
    completed_at: str,
    *,
    db_path: Path,
) -> RunControlExecutionResultRecord:
    connection = connect_metadata_db(db_path)
    try:
        connection.execute("BEGIN IMMEDIATE")
        queue_row = connection.execute(
            """
            SELECT queue_id, run_id, scenario_id, status, execution_enabled, execution_performed
            FROM run_control_queue WHERE queue_id = ?
            """,
            (queue_id,),
        ).fetchone()
        if queue_row is None or queue_row["status"] != "starting":
            raise MetadataImportError("run control adapter completion requires queue status starting")
        record = build_run_control_execution_result_record(
            queue_row, payload, validation_payload, completed_at
        )
        upsert_run_control_execution_result_record(connection, record)
        attempt_update = connection.execute(
            """
            UPDATE run_control_execution_attempts
            SET status = 'result_persisted', completed_at = ?, result_persisted = 1,
                simulation_performed = ?
            WHERE attempt_id = ? AND status = 'starting'
            """,
            (completed_at, int(record.simulation_performed), attempt_id),
        )
        if attempt_update.rowcount != 1:
            raise MetadataImportError("run control adapter attempt lost its atomic completion")
        queue_update = connection.execute(
            """
            UPDATE run_control_queue
            SET status = 'result_persisted', execution_performed = 1
            WHERE queue_id = ? AND status = 'starting'
            """,
            (queue_id,),
        )
        if queue_update.rowcount != 1:
            raise MetadataImportError("run control adapter queue lost its atomic completion")
        connection.commit()
        return record
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def _fail_attempt(
    queue_id: str,
    attempt_id: str,
    message: str,
    completed_at: str,
    *,
    db_path: Path,
) -> None:
    connection = connect_metadata_db(db_path)
    try:
        with connection:
            connection.execute(
                """
                UPDATE run_control_execution_attempts
                SET status = 'failed', completed_at = ?, failure_message = ?
                WHERE attempt_id = ? AND status = 'starting'
                """,
                (completed_at, message[:1000], attempt_id),
            )
            connection.execute(
                """
                UPDATE run_control_queue SET status = 'failed'
                WHERE queue_id = ? AND status = 'starting'
                """,
                (queue_id,),
            )
    finally:
        connection.close()


def _adapter_result_payload(
    result: ControlledExecutionAdapterResult | Mapping[str, object],
) -> dict[str, object]:
    if isinstance(result, ControlledExecutionAdapterResult):
        return result.to_dict()
    return dict(result)


def _validate_result_against_release(
    payload: Mapping[str, object],
    release: RunControlExecutionReleaseResult,
) -> None:
    profile = release.profile
    if profile is None:
        raise MetadataImportError("adapter result cannot be matched without a release profile")
    expected_path = profile.fixture_path.resolve()
    actual_path = Path(str(payload.get("fixture_path", ""))).resolve()
    checks = {
        "adapter mode": payload.get("adapter_mode") == profile.adapter_mode,
        "fixture path": actual_path == expected_path,
        "fixture kind": payload.get("fixture_kind") == profile.fixture_kind,
        "VU carryover": payload.get("requested_carry_forward_vu_state")
        == release.request.carry_forward_vu_state,
        "VN carryover": payload.get("requested_carry_forward_vn_state")
        == release.request.carry_forward_vn_state,
    }
    mismatches = [name for name, matches in checks.items() if not matches]
    if mismatches:
        raise MetadataImportError(
            "adapter result does not match the released " + ", ".join(mismatches)
        )


def _attempt_id(queue_id: str, idempotency_key: str) -> str:
    digest = hashlib.sha256(f"{queue_id}\0{idempotency_key}".encode("utf-8")).hexdigest()
    return f"adapter-{digest[:24]}"


def _request_fingerprint(payload: Mapping[str, object]) -> str:
    serialized = json.dumps(payload, ensure_ascii=True, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
