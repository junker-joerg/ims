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
from ims.api.strategy_execution_period_chain_effect_probe import (
    STRATEGY_EXECUTION_PERIOD_CHAIN_EFFECT_PROBE_REQUEST_VERSION,
    STRATEGY_EXECUTION_PERIOD_CHAIN_EFFECT_PROBE_RESULT_VERSION,
    StrategyExecutionPeriodChainEffectProbeError,
    StrategyExecutionPeriodChainEffectProbeRequest,
    StrategyExecutionPeriodChainEffectProbeRunner,
    run_strategy_execution_period_chain_effect_probe,
)
from ims.api.strategy_execution_period_chain_run_control import (
    STRATEGY_EXECUTION_PERIOD_CHAIN_RUN_CONTROL_REQUEST_VERSION,
    StrategyExecutionPeriodChainRunControlResult,
    check_strategy_execution_period_chain_run_control_release,
)
from ims.api.strategy_execution_period_chain_store import (
    StrategyExecutionPeriodChainStoreError,
    StrategyExecutionPeriodChainStoreRecord,
    get_strategy_execution_period_chain,
)
from ims.strategies.execution_period_chain_contract import (
    STRATEGY_EXECUTION_PERIOD_CHAIN_VERSION,
)


STRATEGY_EXECUTION_PERIOD_CHAIN_EFFECT_PROBE_START_CONTRACT_VERSION = (
    "ims.strategy-execution-period-chain-effect-probe-start-contract.v1"
)
STRATEGY_EXECUTION_PERIOD_CHAIN_EFFECT_PROBE_START_RESULT_VERSION = (
    "ims.strategy-execution-period-chain-effect-probe-start-result.v1"
)
STRATEGY_EXECUTION_PERIOD_CHAIN_EFFECT_PROBE_STORED_RESULT_VERSION = (
    "ims.strategy-execution-period-chain-effect-probe-stored-result.v1"
)
STRATEGY_EXECUTION_PERIOD_CHAIN_EFFECT_PROBE_HISTORY_VERSION = (
    "ims.strategy-execution-period-chain-effect-probe-history.v1"
)

STRATEGY_EXECUTION_PERIOD_CHAIN_EFFECT_PROBE_ATTEMPT_SCHEMA = """
CREATE TABLE IF NOT EXISTS strategy_execution_period_chain_effect_probe_attempts (
    attempt_id TEXT PRIMARY KEY,
    chain_id TEXT NOT NULL,
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
    runner_invocation_count INTEGER NOT NULL CHECK (
        runner_invocation_count BETWEEN 0 AND 2
    ),
    carryover_invocation_count INTEGER NOT NULL CHECK (
        carryover_invocation_count BETWEEN 0 AND 2
    ),
    candidate_reverified_count INTEGER NOT NULL CHECK (
        candidate_reverified_count BETWEEN 0 AND 2
    ),
    result_persisted INTEGER NOT NULL CHECK (result_persisted IN (0, 1)),
    simulation_performed INTEGER NOT NULL CHECK (simulation_performed IN (0, 1)),
    UNIQUE(chain_id, idempotency_key)
)
"""

STRATEGY_EXECUTION_PERIOD_CHAIN_EFFECT_PROBE_RESULT_SCHEMA = """
CREATE TABLE IF NOT EXISTS strategy_execution_period_chain_effect_probe_results (
    chain_id TEXT PRIMARY KEY,
    attempt_id TEXT NOT NULL UNIQUE,
    idempotency_key TEXT NOT NULL,
    content_digest TEXT NOT NULL,
    persisted_at TEXT NOT NULL,
    result_digest TEXT NOT NULL UNIQUE,
    result_payload_json TEXT NOT NULL
)
"""


class StrategyExecutionPeriodChainEffectProbeStartError(ValueError):
    def __init__(
        self,
        code: str,
        message: str,
        *,
        chain_id: str | None = None,
        attempt_id: str | None = None,
        release_check: StrategyExecutionPeriodChainRunControlResult | None = None,
        runner_invocation_count: int = 0,
        carryover_invocation_count: int = 0,
        candidate_reverified_count: int = 0,
        writes_performed: bool = False,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.chain_id = chain_id
        self.attempt_id = attempt_id
        self.release_check = release_check
        self.runner_invocation_count = runner_invocation_count
        self.carryover_invocation_count = carryover_invocation_count
        self.candidate_reverified_count = candidate_reverified_count
        self.writes_performed = writes_performed


@dataclass(frozen=True, slots=True)
class StrategyExecutionPeriodChainEffectProbeStoredResult:
    chain_id: str
    attempt_id: str
    idempotency_key: str
    content_digest: str
    persisted_at: str
    result_digest: str
    result_payload: dict[str, object]

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": (
                STRATEGY_EXECUTION_PERIOD_CHAIN_EFFECT_PROBE_STORED_RESULT_VERSION
            ),
            "chain_id": self.chain_id,
            "attempt_id": self.attempt_id,
            "idempotency_key": self.idempotency_key,
            "content_digest": self.content_digest,
            "persisted_at": self.persisted_at,
            "result_digest": self.result_digest,
            "result_payload": deepcopy(self.result_payload),
        }


@dataclass(frozen=True, slots=True)
class StrategyExecutionPeriodChainEffectProbeAttempt:
    attempt_id: str
    chain_id: str
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
    runner_invocation_count: int
    carryover_invocation_count: int
    candidate_reverified_count: int
    result_persisted: bool
    simulation_performed: bool

    def to_dict(self) -> dict[str, object]:
        return {
            "attempt_id": self.attempt_id,
            "chain_id": self.chain_id,
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
            "runner_invocation_count": self.runner_invocation_count,
            "carryover_invocation_count": self.carryover_invocation_count,
            "candidate_reverified_count": self.candidate_reverified_count,
            "result_persisted": self.result_persisted,
            "simulation_performed": self.simulation_performed,
        }


@dataclass(frozen=True, slots=True)
class StrategyExecutionPeriodChainEffectProbeStartResult:
    chain_id: str
    content_digest: str
    attempt_id: str
    idempotency_key: str
    record: StrategyExecutionPeriodChainEffectProbeStoredResult
    replayed: bool

    def to_dict(self) -> dict[str, object]:
        payload = self.record.result_payload
        runner_count = int(payload.get("runner_invocation_count", 0))
        carryover_count = int(payload.get("carryover_invocation_count", 0))
        candidate_count = int(payload.get("candidate_reverified_count", 0))
        return {
            "status": "ok",
            "schema_version": (
                STRATEGY_EXECUTION_PERIOD_CHAIN_EFFECT_PROBE_START_RESULT_VERSION
            ),
            "request_schema_version": (
                STRATEGY_EXECUTION_PERIOD_CHAIN_EFFECT_PROBE_REQUEST_VERSION
            ),
            "mode": "strategy_execution_period_chain_effect_probe_start",
            "chain_id": self.chain_id,
            "content_digest": self.content_digest,
            "attempt_id": self.attempt_id,
            "idempotency_key": self.idempotency_key,
            "replayed": self.replayed,
            "record": self.record.to_dict(),
            "period_chain_digest_reverified": True,
            "candidate_reverified_count": candidate_count,
            "idempotency_persisted": True,
            "attempt_persisted": True,
            "result_persisted": True,
            "runner_invocation_count": 0 if self.replayed else runner_count,
            "runner_invocation_performed": not self.replayed,
            "carryover_invocation_count": (
                0 if self.replayed else carryover_count
            ),
            "carryover_invocation_performed": (
                not self.replayed and carryover_count > 0
            ),
            "writes_performed": not self.replayed,
            "execution_performed": True,
            "partial_result_returned": False,
            "output_files_written": False,
            "legacy_comparison_performed": False,
            "simulation_performed": False,
            "automatic_retry_enabled": False,
            "queue_worker_enabled": False,
            "historical_rng_equality_claim": False,
            "historical_full_equality_claim": False,
            "next_gate": "PR141",
        }


@dataclass(frozen=True, slots=True)
class StrategyExecutionPeriodChainEffectProbeResultRead:
    chain_id: str
    content_digest: str
    db_path: str
    record: StrategyExecutionPeriodChainEffectProbeStoredResult | None

    def to_dict(self) -> dict[str, object]:
        return {
            "status": "ok",
            "schema_version": (
                STRATEGY_EXECUTION_PERIOD_CHAIN_EFFECT_PROBE_STORED_RESULT_VERSION
            ),
            "mode": "strategy_execution_period_chain_effect_probe_result_read_only",
            "chain_id": self.chain_id,
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
class StrategyExecutionPeriodChainEffectProbeHistory:
    chain_id: str
    content_digest: str
    db_path: str
    attempts: tuple[StrategyExecutionPeriodChainEffectProbeAttempt, ...]
    record: StrategyExecutionPeriodChainEffectProbeStoredResult | None

    def to_dict(self) -> dict[str, object]:
        latest_attempt = self.attempts[0] if self.attempts else None
        return {
            "status": "ok",
            "schema_version": (
                STRATEGY_EXECUTION_PERIOD_CHAIN_EFFECT_PROBE_HISTORY_VERSION
            ),
            "mode": "strategy_execution_period_chain_effect_probe_history_read_only",
            "chain_id": self.chain_id,
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


def start_strategy_execution_period_chain_effect_probe(
    request: StrategyExecutionPeriodChainEffectProbeRequest,
    *,
    db_path: Path | str,
    runner: StrategyExecutionPeriodChainEffectProbeRunner | None = None,
    timestamp_factory: Callable[[], str] = lambda: _utc_now(),
) -> StrategyExecutionPeriodChainEffectProbeStartResult:
    resolved_path = Path(db_path).expanduser().resolve()
    release_check = check_strategy_execution_period_chain_run_control_release(
        request.release,
        db_path=resolved_path,
    )
    if not release_check.release_ready:
        issue = release_check.issues[0] if release_check.issues else None
        raise StrategyExecutionPeriodChainEffectProbeStartError(
            str(issue["code"]) if issue is not None else "release_check_blocked",
            (
                str(issue["message"])
                if issue is not None
                else "Periodenkettenfreigabe ist blockiert"
            ),
            chain_id=request.release.chain_id,
            release_check=release_check,
        )

    fingerprint = _digest_mapping(request.to_dict())
    attempt_id = _attempt_id(
        request.release.chain_id,
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
    except StrategyExecutionPeriodChainEffectProbeStartError as exc:
        raise StrategyExecutionPeriodChainEffectProbeStartError(
            exc.code,
            str(exc),
            chain_id=exc.chain_id or request.release.chain_id,
            attempt_id=exc.attempt_id,
            release_check=release_check,
            runner_invocation_count=exc.runner_invocation_count,
            carryover_invocation_count=exc.carryover_invocation_count,
            candidate_reverified_count=exc.candidate_reverified_count,
            writes_performed=exc.writes_performed,
        ) from exc
    if replay:
        stored = get_strategy_execution_period_chain_effect_probe_result(
            request.release.chain_id,
            db_path=resolved_path,
        ).record
        if stored is None:  # pragma: no cover - guarded by the claim invariant.
            raise StrategyExecutionPeriodChainEffectProbeStartError(
                "replayed_result_missing",
                "Erfolgreicher Idempotenztreffer hat kein gespeichertes Ergebnis",
                chain_id=request.release.chain_id,
                attempt_id=attempt_id,
                release_check=release_check,
            )
        return StrategyExecutionPeriodChainEffectProbeStartResult(
            chain_id=request.release.chain_id,
            content_digest=request.release.expected_content_digest,
            attempt_id=attempt_id,
            idempotency_key=request.release.idempotency_key,
            record=stored,
            replayed=True,
        )

    runner_count = 0
    carryover_count = 0
    candidate_count = 0
    try:
        probe = run_strategy_execution_period_chain_effect_probe(
            request,
            db_path=resolved_path,
            runner=runner,
        )
        result_payload = probe.to_dict()
        runner_count = int(result_payload["runner_invocation_count"])
        carryover_count = int(result_payload["carryover_invocation_count"])
        candidate_count = int(result_payload["candidate_reverified_count"])
        if not probe.execution_performed:
            issue = probe.release_check.issues[0] if probe.release_check.issues else None
            raise StrategyExecutionPeriodChainEffectProbeStartError(
                str(issue["code"]) if issue is not None else "effect_probe_blocked",
                (
                    str(issue["message"])
                    if issue is not None
                    else "Zwei-Perioden-Wirkungsprobe wurde blockiert"
                ),
                chain_id=request.release.chain_id,
                attempt_id=attempt_id,
                release_check=probe.release_check,
                runner_invocation_count=runner_count,
                carryover_invocation_count=carryover_count,
                candidate_reverified_count=candidate_count,
            )
        stored = _complete_attempt(
            request,
            attempt_id=attempt_id,
            result_payload=result_payload,
            persisted_at=timestamp_factory(),
            runner_invocation_count=runner_count,
            carryover_invocation_count=carryover_count,
            candidate_reverified_count=candidate_count,
            db_path=resolved_path,
        )
    except Exception as exc:
        if isinstance(exc, StrategyExecutionPeriodChainEffectProbeStartError):
            code = exc.code
            message = str(exc)
            runner_count = exc.runner_invocation_count or runner_count
            carryover_count = exc.carryover_invocation_count or carryover_count
            candidate_count = exc.candidate_reverified_count or candidate_count
            effective_release_check = exc.release_check or release_check
        elif isinstance(exc, StrategyExecutionPeriodChainEffectProbeError):
            code = exc.code
            message = str(exc)
            runner_count = exc.runner_invocation_count
            carryover_count = exc.carryover_invocation_count
            candidate_count = exc.candidate_reverified_count
            effective_release_check = exc.release_check or release_check
        else:
            code = "effect_probe_start_failed"
            message = (
                "Zwei-Perioden-Wirkungsprobe konnte nicht abgeschlossen werden: "
                f"{exc}"
            )
            effective_release_check = release_check
        _fail_attempt(
            attempt_id,
            code=code,
            message=message,
            completed_at=timestamp_factory(),
            runner_invocation_count=runner_count,
            carryover_invocation_count=carryover_count,
            candidate_reverified_count=candidate_count,
            db_path=resolved_path,
        )
        raise StrategyExecutionPeriodChainEffectProbeStartError(
            code,
            message,
            chain_id=request.release.chain_id,
            attempt_id=attempt_id,
            release_check=effective_release_check,
            runner_invocation_count=runner_count,
            carryover_invocation_count=carryover_count,
            candidate_reverified_count=candidate_count,
            writes_performed=True,
        ) from exc

    return StrategyExecutionPeriodChainEffectProbeStartResult(
        chain_id=request.release.chain_id,
        content_digest=request.release.expected_content_digest,
        attempt_id=attempt_id,
        idempotency_key=request.release.idempotency_key,
        record=stored,
        replayed=False,
    )


def get_strategy_execution_period_chain_effect_probe_result(
    chain_id: str,
    *,
    db_path: Path | str,
) -> StrategyExecutionPeriodChainEffectProbeResultRead:
    chain = _verified_period_chain(chain_id, db_path=db_path)
    resolved_path = Path(db_path).expanduser().resolve()
    connection = _connect_readonly(resolved_path)
    try:
        if not _table_exists(
            connection,
            "strategy_execution_period_chain_effect_probe_results",
        ):
            record = None
        else:
            row = connection.execute(
                """
                SELECT chain_id, attempt_id, idempotency_key, content_digest,
                       persisted_at, result_digest, result_payload_json
                FROM strategy_execution_period_chain_effect_probe_results
                WHERE chain_id = ?
                """,
                (chain_id,),
            ).fetchone()
            record = (
                _row_to_verified_result(row, chain.content_digest)
                if row is not None
                else None
            )
    except sqlite3.DatabaseError as exc:
        raise StrategyExecutionPeriodChainEffectProbeStartError(
            "effect_probe_result_store_unreadable",
            f"Zwei-Perioden-Ergebnisablage ist nicht lesbar: {exc}",
            chain_id=chain_id,
        ) from exc
    finally:
        connection.close()
    return StrategyExecutionPeriodChainEffectProbeResultRead(
        chain_id=chain_id,
        content_digest=chain.content_digest,
        db_path=str(resolved_path),
        record=record,
    )


def get_strategy_execution_period_chain_effect_probe_history(
    chain_id: str,
    *,
    db_path: Path | str,
) -> StrategyExecutionPeriodChainEffectProbeHistory:
    chain = _verified_period_chain(chain_id, db_path=db_path)
    resolved_path = Path(db_path).expanduser().resolve()
    connection = _connect_readonly(resolved_path)
    try:
        if _table_exists(
            connection,
            "strategy_execution_period_chain_effect_probe_attempts",
        ):
            rows = connection.execute(
                """
                SELECT attempt_id, chain_id, content_digest, idempotency_key,
                       status, released_by, released_at, release_reason,
                       started_at, completed_at, failure_code, failure_message,
                       runner_invocation_count, carryover_invocation_count,
                       candidate_reverified_count, result_persisted,
                       simulation_performed
                FROM strategy_execution_period_chain_effect_probe_attempts
                WHERE chain_id = ?
                ORDER BY started_at DESC, attempt_id DESC
                """,
                (chain_id,),
            ).fetchall()
            attempts = tuple(
                _row_to_attempt(row, chain.content_digest) for row in rows
            )
        else:
            attempts = ()
        if _table_exists(
            connection,
            "strategy_execution_period_chain_effect_probe_results",
        ):
            result_row = connection.execute(
                """
                SELECT chain_id, attempt_id, idempotency_key, content_digest,
                       persisted_at, result_digest, result_payload_json
                FROM strategy_execution_period_chain_effect_probe_results
                WHERE chain_id = ?
                """,
                (chain_id,),
            ).fetchone()
            record = (
                _row_to_verified_result(result_row, chain.content_digest)
                if result_row is not None
                else None
            )
        else:
            record = None
    except sqlite3.DatabaseError as exc:
        raise StrategyExecutionPeriodChainEffectProbeStartError(
            "effect_probe_history_store_unreadable",
            f"Zwei-Perioden-Versuchsverlauf ist nicht lesbar: {exc}",
            chain_id=chain_id,
        ) from exc
    finally:
        connection.close()
    return StrategyExecutionPeriodChainEffectProbeHistory(
        chain_id=chain_id,
        content_digest=chain.content_digest,
        db_path=str(resolved_path),
        attempts=attempts,
        record=record,
    )


def strategy_execution_period_chain_effect_probe_start_contract_payload(
) -> dict[str, object]:
    boundary_flags = {
        "ui_start_enabled": True,
        "explicit_run_control_release_required": True,
        "explicit_two_period_effect_probe_execution_required": True,
        "period_chain_digest_reverification_required": True,
        "atomic_idempotency_claim_enabled": True,
        "idempotency_persistence_enabled": True,
        "immutable_result_persistence_enabled": True,
        "attempt_history_enabled": True,
        "read_only_result_enabled": True,
        "read_only_history_enabled": True,
        "exact_two_period_horizon_required": True,
        "isolated_candidate_copies_required": True,
        "stored_transition_flags_authoritative": True,
        "automatic_retry_enabled": False,
        "queue_worker_enabled": False,
        "output_files_enabled": False,
        "legacy_comparison_enabled": False,
        "general_multi_period_execution_enabled": False,
        "simulation_performed": False,
        "historical_rng_equality_claim": False,
        "historical_full_equality_claim": False,
    }
    return {
        "status": "ok",
        "schema_version": (
            STRATEGY_EXECUTION_PERIOD_CHAIN_EFFECT_PROBE_START_CONTRACT_VERSION
        ),
        "request_schema_version": (
            STRATEGY_EXECUTION_PERIOD_CHAIN_EFFECT_PROBE_REQUEST_VERSION
        ),
        "release_request_schema_version": (
            STRATEGY_EXECUTION_PERIOD_CHAIN_RUN_CONTROL_REQUEST_VERSION
        ),
        "effect_result_schema_version": (
            STRATEGY_EXECUTION_PERIOD_CHAIN_EFFECT_PROBE_RESULT_VERSION
        ),
        "stored_result_schema_version": (
            STRATEGY_EXECUTION_PERIOD_CHAIN_EFFECT_PROBE_STORED_RESULT_VERSION
        ),
        "history_schema_version": (
            STRATEGY_EXECUTION_PERIOD_CHAIN_EFFECT_PROBE_HISTORY_VERSION
        ),
        "period_chain_schema_version": STRATEGY_EXECUTION_PERIOD_CHAIN_VERSION,
        "mode": "strategy_execution_period_chain_effect_probe_start_contract",
        "start_endpoint": (
            "/api/run-control/strategy-period-chain-effect-probe-start"
        ),
        "result_endpoint_template": (
            "/api/run-control/strategy-period-chain-effect-probe-result/{chain_id}"
        ),
        "history_endpoint_template": (
            "/api/run-control/strategy-period-chain-effect-probe-history/{chain_id}"
        ),
        "request_source": "pr139_effect_probe_request_unchanged",
        "authoritative_identity_fields": [
            "release.chain_id",
            "release.expected_content_digest",
        ],
        "audit_fields": [
            "release.idempotency_key",
            "release.released_by",
            "release.released_at",
            "release.release_reason",
        ],
        "forbidden_request_fields": [
            "period_chain",
            "period_chain_input",
            "candidate",
            "candidate_payload",
            "db_path",
            "fixture_path",
            "output_dir",
            "carry_forward_vu_state",
            "carry_forward_vn_state",
            "legacy_targets",
        ],
        "next_gate": "PR141",
        "boundary_flags": boundary_flags,
        **boundary_flags,
    }


def strategy_execution_period_chain_effect_probe_start_error_payload(
    code: str,
    message: str,
    *,
    chain_id: str | None = None,
    attempt_id: str | None = None,
    release_check: StrategyExecutionPeriodChainRunControlResult | None = None,
    runner_invocation_count: int = 0,
    carryover_invocation_count: int = 0,
    candidate_reverified_count: int = 0,
    writes_performed: bool = False,
) -> dict[str, object]:
    return {
        "status": "error",
        "schema_version": (
            STRATEGY_EXECUTION_PERIOD_CHAIN_EFFECT_PROBE_START_RESULT_VERSION
        ),
        "mode": "strategy_execution_period_chain_effect_probe_start",
        "chain_id": chain_id,
        "attempt_id": attempt_id,
        "issue_count": 1,
        "issues": [{"code": code, "message": message}],
        "release_check": (
            release_check.to_dict() if release_check is not None else None
        ),
        "period_chain_digest_reverified": (
            release_check is not None and release_check.release_ready
        ),
        "candidate_reverified_count": candidate_reverified_count,
        "idempotency_persisted": attempt_id is not None and writes_performed,
        "attempt_persisted": attempt_id is not None and writes_performed,
        "result_persisted": False,
        "runner_invocation_count": runner_invocation_count,
        "runner_invocation_performed": runner_invocation_count > 0,
        "carryover_invocation_count": carryover_invocation_count,
        "carryover_invocation_performed": carryover_invocation_count > 0,
        "writes_performed": writes_performed,
        "execution_performed": False,
        "partial_result_returned": False,
        "output_files_written": False,
        "legacy_comparison_performed": False,
        "simulation_performed": False,
        "automatic_retry_enabled": False,
        "queue_worker_enabled": False,
        "historical_full_equality_claim": False,
        "next_gate": "PR141",
    }


def _claim_or_replay(
    request: StrategyExecutionPeriodChainEffectProbeRequest,
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
        connection.execute(
            STRATEGY_EXECUTION_PERIOD_CHAIN_EFFECT_PROBE_ATTEMPT_SCHEMA
        )
        connection.execute(
            STRATEGY_EXECUTION_PERIOD_CHAIN_EFFECT_PROBE_RESULT_SCHEMA
        )
        existing = connection.execute(
            """
            SELECT attempt_id, request_fingerprint, status
            FROM strategy_execution_period_chain_effect_probe_attempts
            WHERE chain_id = ? AND idempotency_key = ?
            """,
            (release.chain_id, release.idempotency_key),
        ).fetchone()
        if existing is not None:
            if existing["request_fingerprint"] != request_fingerprint:
                raise StrategyExecutionPeriodChainEffectProbeStartError(
                    "idempotency_payload_conflict",
                    "Idempotenzschluessel wurde mit anderer Freigabe verwendet",
                    chain_id=release.chain_id,
                    attempt_id=str(existing["attempt_id"]),
                )
            if existing["status"] != "result_persisted":
                raise StrategyExecutionPeriodChainEffectProbeStartError(
                    "idempotency_attempt_not_replayable",
                    "Vorhandener Startversuch ist nicht erfolgreich wiederholbar: "
                    f"{existing['status']}",
                    chain_id=release.chain_id,
                    attempt_id=str(existing["attempt_id"]),
                )
            result_exists = connection.execute(
                """
                SELECT 1
                FROM strategy_execution_period_chain_effect_probe_results
                WHERE chain_id = ? AND attempt_id = ?
                """,
                (release.chain_id, existing["attempt_id"]),
            ).fetchone()
            if result_exists is None:
                raise StrategyExecutionPeriodChainEffectProbeStartError(
                    "replayed_result_missing",
                    "Erfolgreicher Startversuch hat kein gespeichertes Ergebnis",
                    chain_id=release.chain_id,
                    attempt_id=str(existing["attempt_id"]),
                )
            connection.commit()
            return True

        result_exists = connection.execute(
            """
            SELECT attempt_id
            FROM strategy_execution_period_chain_effect_probe_results
            WHERE chain_id = ?
            """,
            (release.chain_id,),
        ).fetchone()
        if result_exists is not None:
            raise StrategyExecutionPeriodChainEffectProbeStartError(
                "period_chain_result_already_persisted",
                "Periodenkette hat bereits ein Ergebnis; nur der urspruengliche "
                "Idempotenzschluessel darf es wiederholen",
                chain_id=release.chain_id,
                attempt_id=str(result_exists["attempt_id"]),
            )
        active = connection.execute(
            """
            SELECT attempt_id
            FROM strategy_execution_period_chain_effect_probe_attempts
            WHERE chain_id = ? AND status = 'starting'
            """,
            (release.chain_id,),
        ).fetchone()
        if active is not None:
            raise StrategyExecutionPeriodChainEffectProbeStartError(
                "period_chain_effect_probe_already_starting",
                "Fuer diese Periodenkette laeuft bereits eine Wirkungsprobe",
                chain_id=release.chain_id,
                attempt_id=str(active["attempt_id"]),
            )
        connection.execute(
            """
            INSERT INTO strategy_execution_period_chain_effect_probe_attempts (
                attempt_id, chain_id, content_digest, idempotency_key,
                request_fingerprint, status, released_by, released_at,
                release_reason, started_at, completed_at, failure_code,
                failure_message, runner_invocation_count,
                carryover_invocation_count, candidate_reverified_count,
                result_persisted, simulation_performed
            ) VALUES (?, ?, ?, ?, ?, 'starting', ?, ?, ?, ?, NULL, NULL, NULL,
                      0, 0, 0, 0, 0)
            """,
            (
                attempt_id,
                release.chain_id,
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
    request: StrategyExecutionPeriodChainEffectProbeRequest,
    *,
    attempt_id: str,
    result_payload: dict[str, object],
    persisted_at: str,
    runner_invocation_count: int,
    carryover_invocation_count: int,
    candidate_reverified_count: int,
    db_path: Path,
) -> StrategyExecutionPeriodChainEffectProbeStoredResult:
    release = request.release
    payload_json = _stable_json(result_payload)
    result_digest = _digest_text(payload_json)
    record = StrategyExecutionPeriodChainEffectProbeStoredResult(
        chain_id=release.chain_id,
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
            FROM strategy_execution_period_chain_effect_probe_attempts
            WHERE attempt_id = ? AND chain_id = ?
            """,
            (attempt_id, release.chain_id),
        ).fetchone()
        if attempt is None or attempt["status"] != "starting":
            raise StrategyExecutionPeriodChainEffectProbeStartError(
                "effect_probe_attempt_completion_conflict",
                "Startversuch ist nicht mehr atomar abschliessbar",
                chain_id=release.chain_id,
                attempt_id=attempt_id,
                runner_invocation_count=runner_invocation_count,
                carryover_invocation_count=carryover_invocation_count,
                candidate_reverified_count=candidate_reverified_count,
            )
        if attempt["content_digest"] != release.expected_content_digest:
            raise StrategyExecutionPeriodChainEffectProbeStartError(
                "effect_probe_attempt_digest_conflict",
                "Startversuch verweist auf einen anderen Kettendigest",
                chain_id=release.chain_id,
                attempt_id=attempt_id,
                runner_invocation_count=runner_invocation_count,
                carryover_invocation_count=carryover_invocation_count,
                candidate_reverified_count=candidate_reverified_count,
            )
        connection.execute(
            """
            INSERT INTO strategy_execution_period_chain_effect_probe_results (
                chain_id, attempt_id, idempotency_key, content_digest,
                persisted_at, result_digest, result_payload_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                record.chain_id,
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
            UPDATE strategy_execution_period_chain_effect_probe_attempts
            SET status = 'result_persisted', completed_at = ?,
                runner_invocation_count = ?, carryover_invocation_count = ?,
                candidate_reverified_count = ?, result_persisted = 1
            WHERE attempt_id = ? AND status = 'starting'
            """,
            (
                persisted_at,
                runner_invocation_count,
                carryover_invocation_count,
                candidate_reverified_count,
                attempt_id,
            ),
        )
        if updated.rowcount != 1:
            raise StrategyExecutionPeriodChainEffectProbeStartError(
                "effect_probe_attempt_completion_lost",
                "Startversuch verlor seinen atomaren Abschluss",
                chain_id=release.chain_id,
                attempt_id=attempt_id,
                runner_invocation_count=runner_invocation_count,
                carryover_invocation_count=carryover_invocation_count,
                candidate_reverified_count=candidate_reverified_count,
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
    runner_invocation_count: int,
    carryover_invocation_count: int,
    candidate_reverified_count: int,
    db_path: Path,
) -> None:
    connection = connect_metadata_db(db_path)
    try:
        with connection:
            connection.execute(
                """
                UPDATE strategy_execution_period_chain_effect_probe_attempts
                SET status = 'failed', completed_at = ?, failure_code = ?,
                    failure_message = ?, runner_invocation_count = ?,
                    carryover_invocation_count = ?, candidate_reverified_count = ?
                WHERE attempt_id = ? AND status = 'starting'
                """,
                (
                    completed_at,
                    code[:100],
                    message[:1000],
                    runner_invocation_count,
                    carryover_invocation_count,
                    candidate_reverified_count,
                    attempt_id,
                ),
            )
    finally:
        connection.close()


def _verified_period_chain(
    chain_id: str,
    *,
    db_path: Path | str,
) -> StrategyExecutionPeriodChainStoreRecord:
    try:
        return get_strategy_execution_period_chain(
            chain_id,
            db_path=db_path,
        ).record
    except StrategyExecutionPeriodChainStoreError as exc:
        raise StrategyExecutionPeriodChainEffectProbeStartError(
            exc.code,
            str(exc),
            chain_id=chain_id,
        ) from exc


def _connect_readonly(path: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(
        readonly_sqlite_uri(
            path,
            description="strategy period chain effect probe evidence",
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
) -> StrategyExecutionPeriodChainEffectProbeStoredResult:
    chain_id = str(row["chain_id"])
    try:
        payload = json.loads(row["result_payload_json"])
    except (TypeError, json.JSONDecodeError) as exc:
        raise StrategyExecutionPeriodChainEffectProbeStartError(
            "effect_probe_result_payload_invalid",
            "Gespeichertes Zwei-Perioden-Ergebnis ist kein gueltiges JSON",
            chain_id=chain_id,
        ) from exc
    if not isinstance(payload, dict):
        raise StrategyExecutionPeriodChainEffectProbeStartError(
            "effect_probe_result_payload_invalid",
            "Gespeichertes Zwei-Perioden-Ergebnis muss ein JSON-Objekt sein",
            chain_id=chain_id,
        )
    request_payload = payload.get("request")
    release_payload = (
        request_payload.get("release")
        if isinstance(request_payload, dict)
        else None
    )
    period_effects = payload.get("period_effects")
    transition = payload.get("transition_effect")
    periods = (
        [effect.get("period") for effect in period_effects]
        if isinstance(period_effects, list)
        and all(isinstance(effect, dict) for effect in period_effects)
        else []
    )
    calculated_digest = _digest_text(_stable_json(payload))
    checks = {
        "effect_probe_result_digest_mismatch": (
            str(row["result_digest"]) == calculated_digest
        ),
        "effect_probe_period_chain_digest_mismatch": (
            str(row["content_digest"]) == expected_content_digest
        ),
        "effect_probe_result_period_chain_mismatch": (
            isinstance(release_payload, dict)
            and release_payload.get("chain_id") == chain_id
            and release_payload.get("expected_content_digest")
            == expected_content_digest
            and release_payload.get("idempotency_key")
            == str(row["idempotency_key"])
        ),
        "effect_probe_result_schema_mismatch": (
            payload.get("schema_version")
            == STRATEGY_EXECUTION_PERIOD_CHAIN_EFFECT_PROBE_RESULT_VERSION
        ),
        "effect_probe_result_horizon_mismatch": (
            periods == [1, 2]
            and isinstance(transition, dict)
            and transition.get("from_period") == 1
            and transition.get("to_period") == 2
        ),
        "effect_probe_result_status_mismatch": (
            payload.get("status") == "ok"
            and payload.get("period_count") == 2
            and payload.get("runner_invocation_count") == 2
            and payload.get("execution_performed") is True
            and payload.get("partial_result_returned") is False
            and payload.get("output_files_written") is False
            and payload.get("simulation_performed") is False
        ),
    }
    failed = next((code for code, passed in checks.items() if not passed), None)
    if failed is not None:
        raise StrategyExecutionPeriodChainEffectProbeStartError(
            failed,
            "Gespeichertes Zwei-Perioden-Ergebnis verletzt seine Integritaetsgrenze",
            chain_id=chain_id,
        )
    return StrategyExecutionPeriodChainEffectProbeStoredResult(
        chain_id=chain_id,
        attempt_id=str(row["attempt_id"]),
        idempotency_key=str(row["idempotency_key"]),
        content_digest=str(row["content_digest"]),
        persisted_at=str(row["persisted_at"]),
        result_digest=str(row["result_digest"]),
        result_payload=payload,
    )


def _row_to_attempt(
    row: sqlite3.Row,
    expected_content_digest: str,
) -> StrategyExecutionPeriodChainEffectProbeAttempt:
    chain_id = str(row["chain_id"])
    if str(row["content_digest"]) != expected_content_digest:
        raise StrategyExecutionPeriodChainEffectProbeStartError(
            "effect_probe_attempt_digest_mismatch",
            "Gespeicherter Startversuch verweist auf einen anderen Kettendigest",
            chain_id=chain_id,
            attempt_id=str(row["attempt_id"]),
        )
    return StrategyExecutionPeriodChainEffectProbeAttempt(
        attempt_id=str(row["attempt_id"]),
        chain_id=chain_id,
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
        runner_invocation_count=int(row["runner_invocation_count"]),
        carryover_invocation_count=int(row["carryover_invocation_count"]),
        candidate_reverified_count=int(row["candidate_reverified_count"]),
        result_persisted=bool(row["result_persisted"]),
        simulation_performed=bool(row["simulation_performed"]),
    )


def _attempt_id(chain_id: str, idempotency_key: str) -> str:
    digest = hashlib.sha256(
        f"{chain_id}\0{idempotency_key}".encode("utf-8")
    ).hexdigest()
    return f"strategy-chain-probe-{digest[:24]}"


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
