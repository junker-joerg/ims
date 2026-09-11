from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sqlite3
from typing import Callable, Mapping

from ims.api.metadata_repository import connect_metadata_db
from ims.api.sqlite_readonly import readonly_sqlite_uri
from ims.api.strategy_execution_candidate_effect_probe import (
    STRATEGY_EXECUTION_CANDIDATE_EFFECT_PROBE_REQUEST_VERSION,
    STRATEGY_EXECUTION_CANDIDATE_EFFECT_PROBE_RESULT_VERSION,
    StrategyExecutionCandidateEffectProbeError,
    StrategyExecutionCandidateEffectProbeRequest,
    StrategyExecutionCandidateEffectProbeRunner,
    run_strategy_execution_candidate_effect_probe,
)
from ims.api.strategy_execution_candidate_run_control import (
    STRATEGY_EXECUTION_CANDIDATE_RUN_CONTROL_REQUEST_VERSION,
    StrategyExecutionCandidateRunControlResult,
    check_strategy_execution_candidate_run_control_release,
)
from ims.api.strategy_execution_candidate_store import (
    StrategyExecutionCandidateStoreError,
    StrategyExecutionCandidateStoreRecord,
    get_strategy_execution_candidate,
)
from ims.strategies.execution_candidate_contract import (
    STRATEGY_EXECUTION_CANDIDATE_VERSION,
)


STRATEGY_EXECUTION_CANDIDATE_EFFECT_PROBE_START_CONTRACT_VERSION = (
    "ims.strategy-execution-candidate-effect-probe-start-contract.v1"
)
STRATEGY_EXECUTION_CANDIDATE_EFFECT_PROBE_START_RESULT_VERSION = (
    "ims.strategy-execution-candidate-effect-probe-start-result.v1"
)
STRATEGY_EXECUTION_CANDIDATE_EFFECT_PROBE_STORED_RESULT_VERSION = (
    "ims.strategy-execution-candidate-effect-probe-stored-result.v1"
)
STRATEGY_EXECUTION_CANDIDATE_EFFECT_PROBE_HISTORY_VERSION = (
    "ims.strategy-execution-candidate-effect-probe-history.v1"
)

STRATEGY_EXECUTION_CANDIDATE_EFFECT_PROBE_ATTEMPT_SCHEMA = """
CREATE TABLE IF NOT EXISTS strategy_execution_candidate_effect_probe_attempts (
    attempt_id TEXT PRIMARY KEY,
    candidate_id TEXT NOT NULL,
    content_digest TEXT NOT NULL,
    idempotency_key TEXT NOT NULL,
    request_fingerprint TEXT NOT NULL,
    status TEXT NOT NULL CHECK (
        status IN ('starting', 'failed', 'result_persisted')
    ),
    released_by TEXT NOT NULL,
    released_at TEXT NOT NULL,
    release_reason TEXT NOT NULL,
    started_at TEXT NOT NULL,
    completed_at TEXT,
    failure_code TEXT,
    failure_message TEXT,
    runner_invocation_performed INTEGER NOT NULL CHECK (
        runner_invocation_performed IN (0, 1)
    ),
    result_persisted INTEGER NOT NULL CHECK (result_persisted IN (0, 1)),
    simulation_performed INTEGER NOT NULL CHECK (simulation_performed IN (0, 1)),
    UNIQUE(candidate_id, idempotency_key)
)
"""

STRATEGY_EXECUTION_CANDIDATE_EFFECT_PROBE_RESULT_SCHEMA = """
CREATE TABLE IF NOT EXISTS strategy_execution_candidate_effect_probe_results (
    candidate_id TEXT PRIMARY KEY,
    attempt_id TEXT NOT NULL UNIQUE,
    idempotency_key TEXT NOT NULL,
    content_digest TEXT NOT NULL,
    persisted_at TEXT NOT NULL,
    result_digest TEXT NOT NULL UNIQUE,
    result_payload_json TEXT NOT NULL
)
"""


class StrategyExecutionCandidateEffectProbeStartError(ValueError):
    def __init__(
        self,
        code: str,
        message: str,
        *,
        candidate_id: str | None = None,
        attempt_id: str | None = None,
        release_check: StrategyExecutionCandidateRunControlResult | None = None,
        runner_invocation_performed: bool = False,
        writes_performed: bool = False,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.candidate_id = candidate_id
        self.attempt_id = attempt_id
        self.release_check = release_check
        self.runner_invocation_performed = runner_invocation_performed
        self.writes_performed = writes_performed


@dataclass(frozen=True, slots=True)
class StrategyExecutionCandidateEffectProbeStoredResult:
    candidate_id: str
    attempt_id: str
    idempotency_key: str
    content_digest: str
    persisted_at: str
    result_digest: str
    result_payload: dict[str, object]

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": (
                STRATEGY_EXECUTION_CANDIDATE_EFFECT_PROBE_STORED_RESULT_VERSION
            ),
            "candidate_id": self.candidate_id,
            "attempt_id": self.attempt_id,
            "idempotency_key": self.idempotency_key,
            "content_digest": self.content_digest,
            "persisted_at": self.persisted_at,
            "result_digest": self.result_digest,
            "result_payload": deepcopy(self.result_payload),
        }


@dataclass(frozen=True, slots=True)
class StrategyExecutionCandidateEffectProbeAttempt:
    attempt_id: str
    candidate_id: str
    content_digest: str
    idempotency_key: str
    status: str
    released_by: str
    released_at: str
    release_reason: str
    started_at: str
    completed_at: str | None
    failure_code: str | None
    failure_message: str | None
    runner_invocation_performed: bool
    result_persisted: bool
    simulation_performed: bool

    def to_dict(self) -> dict[str, object]:
        return {
            "attempt_id": self.attempt_id,
            "candidate_id": self.candidate_id,
            "content_digest": self.content_digest,
            "idempotency_key": self.idempotency_key,
            "status": self.status,
            "released_by": self.released_by,
            "released_at": self.released_at,
            "release_reason": self.release_reason,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "failure_code": self.failure_code,
            "failure_message": self.failure_message,
            "runner_invocation_performed": self.runner_invocation_performed,
            "result_persisted": self.result_persisted,
            "simulation_performed": self.simulation_performed,
        }


@dataclass(frozen=True, slots=True)
class StrategyExecutionCandidateEffectProbeStartResult:
    candidate_id: str
    content_digest: str
    attempt_id: str
    idempotency_key: str
    record: StrategyExecutionCandidateEffectProbeStoredResult
    replayed: bool

    def to_dict(self) -> dict[str, object]:
        return {
            "status": "ok",
            "schema_version": (
                STRATEGY_EXECUTION_CANDIDATE_EFFECT_PROBE_START_RESULT_VERSION
            ),
            "request_schema_version": (
                STRATEGY_EXECUTION_CANDIDATE_EFFECT_PROBE_REQUEST_VERSION
            ),
            "mode": "strategy_execution_candidate_effect_probe_start",
            "candidate_id": self.candidate_id,
            "content_digest": self.content_digest,
            "attempt_id": self.attempt_id,
            "idempotency_key": self.idempotency_key,
            "replayed": self.replayed,
            "record": self.record.to_dict(),
            "candidate_digest_reverified": True,
            "idempotency_persisted": True,
            "attempt_persisted": True,
            "result_persisted": True,
            "runner_invocation_count": 0 if self.replayed else 1,
            "runner_invocation_performed": not self.replayed,
            "writes_performed": not self.replayed,
            "execution_performed": True,
            "carryover_performed": False,
            "output_files_written": False,
            "legacy_comparison_performed": False,
            "simulation_performed": False,
            "automatic_retry_enabled": False,
            "queue_worker_enabled": False,
            "historical_rng_equality_claim": False,
            "historical_full_equality_claim": False,
            "next_gate": "PR133",
        }


@dataclass(frozen=True, slots=True)
class StrategyExecutionCandidateEffectProbeResultRead:
    candidate_id: str
    content_digest: str
    db_path: str
    record: StrategyExecutionCandidateEffectProbeStoredResult | None

    def to_dict(self) -> dict[str, object]:
        return {
            "status": "ok",
            "schema_version": (
                STRATEGY_EXECUTION_CANDIDATE_EFFECT_PROBE_STORED_RESULT_VERSION
            ),
            "mode": "strategy_execution_candidate_effect_probe_result_read_only",
            "candidate_id": self.candidate_id,
            "content_digest": self.content_digest,
            "db_path": self.db_path,
            "result_available": self.record is not None,
            "record": self.record.to_dict() if self.record is not None else None,
            "writes_performed": False,
            "execution_performed": False,
            "simulation_performed": False,
            "historical_full_equality_claim": False,
        }


@dataclass(frozen=True, slots=True)
class StrategyExecutionCandidateEffectProbeHistory:
    candidate_id: str
    content_digest: str
    db_path: str
    attempts: tuple[StrategyExecutionCandidateEffectProbeAttempt, ...]
    record: StrategyExecutionCandidateEffectProbeStoredResult | None

    def to_dict(self) -> dict[str, object]:
        latest_attempt = self.attempts[0] if self.attempts else None
        return {
            "status": "ok",
            "schema_version": (
                STRATEGY_EXECUTION_CANDIDATE_EFFECT_PROBE_HISTORY_VERSION
            ),
            "mode": "strategy_execution_candidate_effect_probe_history_read_only",
            "candidate_id": self.candidate_id,
            "content_digest": self.content_digest,
            "db_path": self.db_path,
            "attempt_count": len(self.attempts),
            "attempts": [attempt.to_dict() for attempt in self.attempts],
            "latest_attempt": (
                latest_attempt.to_dict() if latest_attempt is not None else None
            ),
            "result_available": self.record is not None,
            "persisted_at": (
                self.record.persisted_at if self.record is not None else None
            ),
            "result_digest": (
                self.record.result_digest if self.record is not None else None
            ),
            "automatic_retry_enabled": False,
            "queue_worker_enabled": False,
            "writes_performed": False,
            "execution_performed": False,
            "simulation_performed": False,
            "historical_full_equality_claim": False,
        }


def start_strategy_execution_candidate_effect_probe(
    request: StrategyExecutionCandidateEffectProbeRequest,
    *,
    db_path: Path | str,
    runner: StrategyExecutionCandidateEffectProbeRunner | None = None,
    timestamp_factory: Callable[[], str] = lambda: _utc_now(),
) -> StrategyExecutionCandidateEffectProbeStartResult:
    resolved_path = Path(db_path).expanduser().resolve()
    release_check = check_strategy_execution_candidate_run_control_release(
        request.release,
        db_path=resolved_path,
    )
    if not release_check.release_ready:
        issue = release_check.issues[0] if release_check.issues else None
        raise StrategyExecutionCandidateEffectProbeStartError(
            str(issue["code"]) if issue is not None else "release_check_blocked",
            (
                str(issue["message"])
                if issue is not None
                else "Kandidatenfreigabe ist blockiert"
            ),
            candidate_id=request.release.candidate_id,
            release_check=release_check,
        )

    fingerprint = _digest_mapping(request.to_dict())
    attempt_id = _attempt_id(
        request.release.candidate_id,
        request.release.idempotency_key,
    )
    try:
        replay = _claim_or_replay(
            request,
            db_path=resolved_path,
            request_fingerprint=fingerprint,
            attempt_id=attempt_id,
            started_at=timestamp_factory(),
        )
    except StrategyExecutionCandidateEffectProbeStartError as exc:
        raise StrategyExecutionCandidateEffectProbeStartError(
            exc.code,
            str(exc),
            candidate_id=exc.candidate_id or request.release.candidate_id,
            attempt_id=exc.attempt_id,
            release_check=release_check,
            runner_invocation_performed=exc.runner_invocation_performed,
            writes_performed=exc.writes_performed,
        ) from exc
    if replay:
        stored = get_strategy_execution_candidate_effect_probe_result(
            request.release.candidate_id,
            db_path=resolved_path,
        ).record
        if stored is None:  # pragma: no cover - guarded by the attempt invariant.
            raise StrategyExecutionCandidateEffectProbeStartError(
                "replayed_result_missing",
                "Erfolgreicher Idempotenztreffer hat kein gespeichertes Ergebnis",
                candidate_id=request.release.candidate_id,
                attempt_id=attempt_id,
                release_check=release_check,
            )
        return StrategyExecutionCandidateEffectProbeStartResult(
            candidate_id=request.release.candidate_id,
            content_digest=request.release.expected_content_digest,
            attempt_id=attempt_id,
            idempotency_key=request.release.idempotency_key,
            record=stored,
            replayed=True,
        )

    try:
        probe = run_strategy_execution_candidate_effect_probe(
            request,
            db_path=resolved_path,
            runner=runner,
        )
        if not probe.execution_performed:
            issue = probe.release_check.issues[0] if probe.release_check.issues else None
            code = str(issue["code"]) if issue is not None else "effect_probe_blocked"
            message = (
                str(issue["message"])
                if issue is not None
                else "Einperioden-Wirkungsprobe wurde vor dem Runner blockiert"
            )
            raise StrategyExecutionCandidateEffectProbeStartError(
                code,
                message,
                candidate_id=request.release.candidate_id,
                attempt_id=attempt_id,
                release_check=probe.release_check,
            )
        result_payload = probe.to_dict()
        completed_at = timestamp_factory()
        stored = _complete_attempt(
            request,
            attempt_id=attempt_id,
            result_payload=result_payload,
            persisted_at=completed_at,
            db_path=resolved_path,
        )
    except Exception as exc:
        if isinstance(exc, StrategyExecutionCandidateEffectProbeStartError):
            code = exc.code
            message = str(exc)
            runner_invoked = exc.runner_invocation_performed
            effective_release_check = exc.release_check or release_check
        elif isinstance(exc, StrategyExecutionCandidateEffectProbeError):
            code = exc.code
            message = str(exc)
            runner_invoked = exc.runner_invocation_performed
            effective_release_check = exc.release_check or release_check
        else:
            code = "effect_probe_start_failed"
            message = f"Einperioden-Wirkungsprobe konnte nicht abgeschlossen werden: {exc}"
            runner_invoked = True
            effective_release_check = release_check
        _fail_attempt(
            attempt_id,
            code=code,
            message=message,
            completed_at=timestamp_factory(),
            runner_invocation_performed=runner_invoked,
            db_path=resolved_path,
        )
        raise StrategyExecutionCandidateEffectProbeStartError(
            code,
            message,
            candidate_id=request.release.candidate_id,
            attempt_id=attempt_id,
            release_check=effective_release_check,
            runner_invocation_performed=runner_invoked,
            writes_performed=True,
        ) from exc

    return StrategyExecutionCandidateEffectProbeStartResult(
        candidate_id=request.release.candidate_id,
        content_digest=request.release.expected_content_digest,
        attempt_id=attempt_id,
        idempotency_key=request.release.idempotency_key,
        record=stored,
        replayed=False,
    )


def get_strategy_execution_candidate_effect_probe_result(
    candidate_id: str,
    *,
    db_path: Path | str,
) -> StrategyExecutionCandidateEffectProbeResultRead:
    candidate = _verified_candidate(candidate_id, db_path=db_path)
    resolved_path = Path(db_path).expanduser().resolve()
    connection = _connect_readonly(resolved_path)
    try:
        if not _table_exists(
            connection,
            "strategy_execution_candidate_effect_probe_results",
        ):
            record = None
        else:
            row = connection.execute(
                """
                SELECT candidate_id, attempt_id, idempotency_key, content_digest,
                       persisted_at, result_digest, result_payload_json
                FROM strategy_execution_candidate_effect_probe_results
                WHERE candidate_id = ?
                """,
                (candidate_id,),
            ).fetchone()
            record = (
                _row_to_verified_result(row, candidate.content_digest)
                if row is not None
                else None
            )
    except sqlite3.DatabaseError as exc:
        raise StrategyExecutionCandidateEffectProbeStartError(
            "effect_probe_result_store_unreadable",
            f"Ergebnisablage ist nicht lesbar: {exc}",
            candidate_id=candidate_id,
        ) from exc
    finally:
        connection.close()
    return StrategyExecutionCandidateEffectProbeResultRead(
        candidate_id=candidate_id,
        content_digest=candidate.content_digest,
        db_path=str(resolved_path),
        record=record,
    )


def get_strategy_execution_candidate_effect_probe_history(
    candidate_id: str,
    *,
    db_path: Path | str,
) -> StrategyExecutionCandidateEffectProbeHistory:
    candidate = _verified_candidate(candidate_id, db_path=db_path)
    resolved_path = Path(db_path).expanduser().resolve()
    connection = _connect_readonly(resolved_path)
    try:
        if _table_exists(
            connection,
            "strategy_execution_candidate_effect_probe_attempts",
        ):
            rows = connection.execute(
                """
                SELECT attempt_id, candidate_id, content_digest, idempotency_key,
                       status, released_by, released_at, release_reason,
                       started_at, completed_at, failure_code, failure_message,
                       runner_invocation_performed, result_persisted,
                       simulation_performed
                FROM strategy_execution_candidate_effect_probe_attempts
                WHERE candidate_id = ?
                ORDER BY started_at DESC, attempt_id DESC
                """,
                (candidate_id,),
            ).fetchall()
            attempts = tuple(_row_to_attempt(row) for row in rows)
        else:
            attempts = ()
        if _table_exists(
            connection,
            "strategy_execution_candidate_effect_probe_results",
        ):
            result_row = connection.execute(
                """
                SELECT candidate_id, attempt_id, idempotency_key, content_digest,
                       persisted_at, result_digest, result_payload_json
                FROM strategy_execution_candidate_effect_probe_results
                WHERE candidate_id = ?
                """,
                (candidate_id,),
            ).fetchone()
            record = (
                _row_to_verified_result(result_row, candidate.content_digest)
                if result_row is not None
                else None
            )
        else:
            record = None
    except sqlite3.DatabaseError as exc:
        raise StrategyExecutionCandidateEffectProbeStartError(
            "effect_probe_history_store_unreadable",
            f"Versuchsverlauf ist nicht lesbar: {exc}",
            candidate_id=candidate_id,
        ) from exc
    finally:
        connection.close()
    return StrategyExecutionCandidateEffectProbeHistory(
        candidate_id=candidate_id,
        content_digest=candidate.content_digest,
        db_path=str(resolved_path),
        attempts=attempts,
        record=record,
    )


def strategy_execution_candidate_effect_probe_start_contract_payload(
) -> dict[str, object]:
    boundary_flags = {
        "ui_start_enabled": True,
        "explicit_run_control_release_required": True,
        "explicit_effect_probe_execution_required": True,
        "candidate_digest_reverification_required": True,
        "atomic_idempotency_claim_enabled": True,
        "idempotency_persistence_enabled": True,
        "immutable_result_persistence_enabled": True,
        "attempt_history_enabled": True,
        "read_only_result_enabled": True,
        "read_only_history_enabled": True,
        "single_period_only": True,
        "isolated_candidate_copy_required": True,
        "automatic_retry_enabled": False,
        "queue_worker_enabled": False,
        "carryover_enabled": False,
        "output_files_enabled": False,
        "legacy_comparison_enabled": False,
        "multi_period_execution_enabled": False,
        "simulation_performed": False,
        "historical_rng_equality_claim": False,
        "historical_full_equality_claim": False,
    }
    return {
        "status": "ok",
        "schema_version": (
            STRATEGY_EXECUTION_CANDIDATE_EFFECT_PROBE_START_CONTRACT_VERSION
        ),
        "request_schema_version": (
            STRATEGY_EXECUTION_CANDIDATE_EFFECT_PROBE_REQUEST_VERSION
        ),
        "release_request_schema_version": (
            STRATEGY_EXECUTION_CANDIDATE_RUN_CONTROL_REQUEST_VERSION
        ),
        "effect_result_schema_version": (
            STRATEGY_EXECUTION_CANDIDATE_EFFECT_PROBE_RESULT_VERSION
        ),
        "stored_result_schema_version": (
            STRATEGY_EXECUTION_CANDIDATE_EFFECT_PROBE_STORED_RESULT_VERSION
        ),
        "history_schema_version": (
            STRATEGY_EXECUTION_CANDIDATE_EFFECT_PROBE_HISTORY_VERSION
        ),
        "candidate_schema_version": STRATEGY_EXECUTION_CANDIDATE_VERSION,
        "mode": "strategy_execution_candidate_effect_probe_start_contract",
        "start_endpoint": (
            "/api/run-control/strategy-candidate-effect-probe-start"
        ),
        "result_endpoint_template": (
            "/api/run-control/strategy-candidate-effect-probe-result/{candidate_id}"
        ),
        "history_endpoint_template": (
            "/api/run-control/strategy-candidate-effect-probe-history/{candidate_id}"
        ),
        "request_source": "pr130_effect_probe_request_unchanged",
        "authoritative_identity_fields": [
            "release.candidate_id",
            "release.expected_content_digest",
        ],
        "audit_fields": [
            "release.idempotency_key",
            "release.released_by",
            "release.released_at",
            "release.release_reason",
        ],
        "forbidden_request_fields": [
            "candidate",
            "candidate_input",
            "db_path",
            "fixture_path",
            "output_dir",
            "carry_forward_vu_state",
            "carry_forward_vn_state",
            "legacy_targets",
        ],
        "next_gate": "PR133",
        "boundary_flags": boundary_flags,
        **boundary_flags,
    }


def strategy_execution_candidate_effect_probe_start_error_payload(
    code: str,
    message: str,
    *,
    candidate_id: str | None = None,
    attempt_id: str | None = None,
    release_check: StrategyExecutionCandidateRunControlResult | None = None,
    runner_invocation_performed: bool = False,
    writes_performed: bool = False,
) -> dict[str, object]:
    return {
        "status": "error",
        "schema_version": (
            STRATEGY_EXECUTION_CANDIDATE_EFFECT_PROBE_START_RESULT_VERSION
        ),
        "mode": "strategy_execution_candidate_effect_probe_start",
        "candidate_id": candidate_id,
        "attempt_id": attempt_id,
        "issue_count": 1,
        "issues": [{"code": code, "message": message}],
        "release_check": (
            release_check.to_dict() if release_check is not None else None
        ),
        "candidate_digest_reverified": (
            release_check is not None and release_check.release_ready
        ),
        "idempotency_persisted": attempt_id is not None and writes_performed,
        "attempt_persisted": attempt_id is not None and writes_performed,
        "result_persisted": False,
        "runner_invocation_count": int(runner_invocation_performed),
        "runner_invocation_performed": runner_invocation_performed,
        "writes_performed": writes_performed,
        "execution_performed": False,
        "carryover_performed": False,
        "output_files_written": False,
        "legacy_comparison_performed": False,
        "simulation_performed": False,
        "automatic_retry_enabled": False,
        "queue_worker_enabled": False,
        "historical_full_equality_claim": False,
        "next_gate": "PR133",
    }


def _claim_or_replay(
    request: StrategyExecutionCandidateEffectProbeRequest,
    *,
    db_path: Path,
    request_fingerprint: str,
    attempt_id: str,
    started_at: str,
) -> bool:
    release = request.release
    connection = connect_metadata_db(db_path)
    try:
        connection.execute("BEGIN IMMEDIATE")
        connection.execute(STRATEGY_EXECUTION_CANDIDATE_EFFECT_PROBE_ATTEMPT_SCHEMA)
        connection.execute(STRATEGY_EXECUTION_CANDIDATE_EFFECT_PROBE_RESULT_SCHEMA)
        existing = connection.execute(
            """
            SELECT attempt_id, request_fingerprint, status
            FROM strategy_execution_candidate_effect_probe_attempts
            WHERE candidate_id = ? AND idempotency_key = ?
            """,
            (release.candidate_id, release.idempotency_key),
        ).fetchone()
        if existing is not None:
            if existing["request_fingerprint"] != request_fingerprint:
                raise StrategyExecutionCandidateEffectProbeStartError(
                    "idempotency_payload_conflict",
                    "Idempotenzschluessel wurde bereits mit anderer Freigabe verwendet",
                    candidate_id=release.candidate_id,
                    attempt_id=str(existing["attempt_id"]),
                )
            if existing["status"] != "result_persisted":
                raise StrategyExecutionCandidateEffectProbeStartError(
                    "idempotency_attempt_not_replayable",
                    "Vorhandener Startversuch ist nicht erfolgreich wiederholbar: "
                    f"{existing['status']}",
                    candidate_id=release.candidate_id,
                    attempt_id=str(existing["attempt_id"]),
                )
            result_exists = connection.execute(
                """
                SELECT 1
                FROM strategy_execution_candidate_effect_probe_results
                WHERE candidate_id = ? AND attempt_id = ?
                """,
                (release.candidate_id, existing["attempt_id"]),
            ).fetchone()
            if result_exists is None:
                raise StrategyExecutionCandidateEffectProbeStartError(
                    "replayed_result_missing",
                    "Erfolgreicher Startversuch hat kein gespeichertes Ergebnis",
                    candidate_id=release.candidate_id,
                    attempt_id=str(existing["attempt_id"]),
                )
            connection.commit()
            return True

        result_exists = connection.execute(
            """
            SELECT attempt_id
            FROM strategy_execution_candidate_effect_probe_results
            WHERE candidate_id = ?
            """,
            (release.candidate_id,),
        ).fetchone()
        if result_exists is not None:
            raise StrategyExecutionCandidateEffectProbeStartError(
                "candidate_result_already_persisted",
                "Kandidat hat bereits ein Ergebnis; nur der urspruengliche "
                "Idempotenzschluessel darf es wiederholen",
                candidate_id=release.candidate_id,
                attempt_id=str(result_exists["attempt_id"]),
            )
        active = connection.execute(
            """
            SELECT attempt_id
            FROM strategy_execution_candidate_effect_probe_attempts
            WHERE candidate_id = ? AND status = 'starting'
            """,
            (release.candidate_id,),
        ).fetchone()
        if active is not None:
            raise StrategyExecutionCandidateEffectProbeStartError(
                "candidate_effect_probe_already_starting",
                "Fuer diesen Kandidaten laeuft bereits eine Einperiodenprobe",
                candidate_id=release.candidate_id,
                attempt_id=str(active["attempt_id"]),
            )
        connection.execute(
            """
            INSERT INTO strategy_execution_candidate_effect_probe_attempts (
                attempt_id, candidate_id, content_digest, idempotency_key,
                request_fingerprint, status, released_by, released_at,
                release_reason, started_at, completed_at, failure_code,
                failure_message, runner_invocation_performed,
                result_persisted, simulation_performed
            ) VALUES (?, ?, ?, ?, ?, 'starting', ?, ?, ?, ?, NULL, NULL, NULL, 0, 0, 0)
            """,
            (
                attempt_id,
                release.candidate_id,
                release.expected_content_digest,
                release.idempotency_key,
                request_fingerprint,
                release.released_by,
                release.released_at,
                release.release_reason,
                started_at,
            ),
        )
        connection.commit()
        return False
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def _complete_attempt(
    request: StrategyExecutionCandidateEffectProbeRequest,
    *,
    attempt_id: str,
    result_payload: dict[str, object],
    persisted_at: str,
    db_path: Path,
) -> StrategyExecutionCandidateEffectProbeStoredResult:
    release = request.release
    payload_json = _stable_json(result_payload)
    result_digest = _digest_text(payload_json)
    record = StrategyExecutionCandidateEffectProbeStoredResult(
        candidate_id=release.candidate_id,
        attempt_id=attempt_id,
        idempotency_key=release.idempotency_key,
        content_digest=release.expected_content_digest,
        persisted_at=persisted_at,
        result_digest=result_digest,
        result_payload=deepcopy(result_payload),
    )
    connection = connect_metadata_db(db_path)
    try:
        connection.execute("BEGIN IMMEDIATE")
        attempt = connection.execute(
            """
            SELECT status, content_digest
            FROM strategy_execution_candidate_effect_probe_attempts
            WHERE attempt_id = ? AND candidate_id = ?
            """,
            (attempt_id, release.candidate_id),
        ).fetchone()
        if attempt is None or attempt["status"] != "starting":
            raise StrategyExecutionCandidateEffectProbeStartError(
                "effect_probe_attempt_completion_conflict",
                "Startversuch ist nicht mehr atomar abschliessbar",
                candidate_id=release.candidate_id,
                attempt_id=attempt_id,
                runner_invocation_performed=True,
            )
        if attempt["content_digest"] != release.expected_content_digest:
            raise StrategyExecutionCandidateEffectProbeStartError(
                "effect_probe_attempt_digest_conflict",
                "Startversuch verweist auf einen anderen Kandidatendigest",
                candidate_id=release.candidate_id,
                attempt_id=attempt_id,
                runner_invocation_performed=True,
            )
        connection.execute(
            """
            INSERT INTO strategy_execution_candidate_effect_probe_results (
                candidate_id, attempt_id, idempotency_key, content_digest,
                persisted_at, result_digest, result_payload_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                record.candidate_id,
                record.attempt_id,
                record.idempotency_key,
                record.content_digest,
                record.persisted_at,
                record.result_digest,
                payload_json,
            ),
        )
        updated = connection.execute(
            """
            UPDATE strategy_execution_candidate_effect_probe_attempts
            SET status = 'result_persisted', completed_at = ?,
                runner_invocation_performed = 1, result_persisted = 1
            WHERE attempt_id = ? AND status = 'starting'
            """,
            (persisted_at, attempt_id),
        )
        if updated.rowcount != 1:
            raise StrategyExecutionCandidateEffectProbeStartError(
                "effect_probe_attempt_completion_lost",
                "Startversuch verlor seinen atomaren Abschluss",
                candidate_id=release.candidate_id,
                attempt_id=attempt_id,
                runner_invocation_performed=True,
            )
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()
    return record


def _fail_attempt(
    attempt_id: str,
    *,
    code: str,
    message: str,
    completed_at: str,
    runner_invocation_performed: bool,
    db_path: Path,
) -> None:
    connection = connect_metadata_db(db_path)
    try:
        with connection:
            connection.execute(
                """
                UPDATE strategy_execution_candidate_effect_probe_attempts
                SET status = 'failed', completed_at = ?, failure_code = ?,
                    failure_message = ?, runner_invocation_performed = ?
                WHERE attempt_id = ? AND status = 'starting'
                """,
                (
                    completed_at,
                    code[:100],
                    message[:1000],
                    int(runner_invocation_performed),
                    attempt_id,
                ),
            )
    finally:
        connection.close()


def _verified_candidate(
    candidate_id: str,
    *,
    db_path: Path | str,
) -> StrategyExecutionCandidateStoreRecord:
    try:
        return get_strategy_execution_candidate(
            candidate_id,
            db_path=db_path,
        ).record
    except StrategyExecutionCandidateStoreError as exc:
        raise StrategyExecutionCandidateEffectProbeStartError(
            exc.code,
            str(exc),
            candidate_id=candidate_id,
        ) from exc


def _connect_readonly(path: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(
        readonly_sqlite_uri(
            path,
            description="strategy execution candidate effect probe evidence",
        ),
        uri=True,
        check_same_thread=False,
    )
    connection.row_factory = sqlite3.Row
    return connection


def _table_exists(connection: sqlite3.Connection, table_name: str) -> bool:
    return connection.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?",
        (table_name,),
    ).fetchone() is not None


def _row_to_verified_result(
    row: sqlite3.Row,
    expected_content_digest: str,
) -> StrategyExecutionCandidateEffectProbeStoredResult:
    try:
        payload = json.loads(row["result_payload_json"])
    except (TypeError, json.JSONDecodeError) as exc:
        raise StrategyExecutionCandidateEffectProbeStartError(
            "effect_probe_result_payload_invalid",
            "Gespeichertes Einperiodenergebnis ist kein gueltiges JSON",
            candidate_id=str(row["candidate_id"]),
        ) from exc
    if not isinstance(payload, dict):
        raise StrategyExecutionCandidateEffectProbeStartError(
            "effect_probe_result_payload_invalid",
            "Gespeichertes Einperiodenergebnis muss ein JSON-Objekt sein",
            candidate_id=str(row["candidate_id"]),
        )
    request_payload = payload.get("request")
    release_payload = (
        request_payload.get("release")
        if isinstance(request_payload, dict)
        else None
    )
    calculated_digest = _digest_text(_stable_json(payload))
    checks = {
        "effect_probe_result_digest_mismatch": (
            str(row["result_digest"]) == calculated_digest
        ),
        "effect_probe_candidate_digest_mismatch": (
            str(row["content_digest"]) == expected_content_digest
        ),
        "effect_probe_result_candidate_mismatch": (
            isinstance(release_payload, dict)
            and release_payload.get("candidate_id") == str(row["candidate_id"])
            and release_payload.get("expected_content_digest")
            == expected_content_digest
        ),
        "effect_probe_result_schema_mismatch": (
            payload.get("schema_version")
            == STRATEGY_EXECUTION_CANDIDATE_EFFECT_PROBE_RESULT_VERSION
        ),
        "effect_probe_result_status_mismatch": (
            payload.get("status") == "ok"
            and payload.get("execution_performed") is True
            and payload.get("simulation_performed") is False
        ),
    }
    failed = next((code for code, passed in checks.items() if not passed), None)
    if failed is not None:
        raise StrategyExecutionCandidateEffectProbeStartError(
            failed,
            "Gespeichertes Einperiodenergebnis verletzt seine Integritaetsgrenze",
            candidate_id=str(row["candidate_id"]),
        )
    return StrategyExecutionCandidateEffectProbeStoredResult(
        candidate_id=str(row["candidate_id"]),
        attempt_id=str(row["attempt_id"]),
        idempotency_key=str(row["idempotency_key"]),
        content_digest=str(row["content_digest"]),
        persisted_at=str(row["persisted_at"]),
        result_digest=str(row["result_digest"]),
        result_payload=payload,
    )


def _row_to_attempt(
    row: sqlite3.Row,
) -> StrategyExecutionCandidateEffectProbeAttempt:
    return StrategyExecutionCandidateEffectProbeAttempt(
        attempt_id=str(row["attempt_id"]),
        candidate_id=str(row["candidate_id"]),
        content_digest=str(row["content_digest"]),
        idempotency_key=str(row["idempotency_key"]),
        status=str(row["status"]),
        released_by=str(row["released_by"]),
        released_at=str(row["released_at"]),
        release_reason=str(row["release_reason"]),
        started_at=str(row["started_at"]),
        completed_at=(
            str(row["completed_at"]) if row["completed_at"] is not None else None
        ),
        failure_code=(
            str(row["failure_code"]) if row["failure_code"] is not None else None
        ),
        failure_message=(
            str(row["failure_message"])
            if row["failure_message"] is not None
            else None
        ),
        runner_invocation_performed=bool(row["runner_invocation_performed"]),
        result_persisted=bool(row["result_persisted"]),
        simulation_performed=bool(row["simulation_performed"]),
    )


def _attempt_id(candidate_id: str, idempotency_key: str) -> str:
    digest = hashlib.sha256(
        f"{candidate_id}\0{idempotency_key}".encode("utf-8")
    ).hexdigest()
    return f"strategy-probe-{digest[:24]}"


def _digest_mapping(payload: Mapping[str, object]) -> str:
    return _digest_text(_stable_json(payload))


def _digest_text(value: str) -> str:
    return "sha256:" + hashlib.sha256(value.encode("utf-8")).hexdigest()


def _stable_json(payload: Mapping[str, object]) -> str:
    return json.dumps(
        payload,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    )


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
