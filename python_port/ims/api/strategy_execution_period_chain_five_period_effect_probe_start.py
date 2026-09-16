from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sqlite3
from typing import Callable, Mapping

from ims.api.metadata_repository import connect_metadata_db
from ims.api.sqlite_readonly import readonly_sqlite_uri
from ims.api.strategy_execution_period_chain_build import (
    calculate_strategy_execution_period_chain_content_digest,
    strategy_execution_period_chain_id_from_digest,
)
from ims.api.strategy_execution_period_chain_effect_probe import (
    StrategyExecutionPeriodChainEffectProbeRunner,
)
from ims.api.strategy_execution_period_chain_five_period_build import (
    FIVE_PERIOD_CHAIN_PERIOD_COUNT,
    FIVE_PERIOD_CHAIN_TRANSITION_COUNT,
    build_strategy_execution_five_period_chain,
)
from ims.api.strategy_execution_period_chain_five_period_effect_probe import (
    STRATEGY_EXECUTION_FIVE_PERIOD_EFFECT_PROBE_REQUEST_VERSION,
    STRATEGY_EXECUTION_FIVE_PERIOD_EFFECT_PROBE_RESULT_VERSION,
    StrategyExecutionFivePeriodEffectProbeError,
    StrategyExecutionFivePeriodEffectProbeRequest,
    parse_strategy_execution_five_period_effect_probe_request,
    run_strategy_execution_five_period_effect_probe,
)
from ims.api.strategy_execution_period_chain_run_control import (
    STRATEGY_EXECUTION_PERIOD_CHAIN_RUN_CONTROL_REQUEST_VERSION,
    StrategyExecutionPeriodChainRunControlError,
    StrategyExecutionPeriodChainRunControlRequest,
    parse_strategy_execution_period_chain_run_control_request,
)
from ims.strategies.execution_period_chain_contract import (
    STRATEGY_EXECUTION_PERIOD_CHAIN_VERSION,
)


STRATEGY_EXECUTION_FIVE_PERIOD_EFFECT_PROBE_START_CONTRACT_VERSION = (
    "ims.strategy-execution-five-period-effect-probe-start-contract.v1"
)
STRATEGY_EXECUTION_FIVE_PERIOD_EFFECT_PROBE_START_REQUEST_VERSION = (
    "ims.strategy-execution-five-period-effect-probe-start-request.v1"
)
STRATEGY_EXECUTION_FIVE_PERIOD_EFFECT_PROBE_START_RESULT_VERSION = (
    "ims.strategy-execution-five-period-effect-probe-start-result.v1"
)
STRATEGY_EXECUTION_FIVE_PERIOD_EFFECT_PROBE_STORED_RESULT_VERSION = (
    "ims.strategy-execution-five-period-effect-probe-stored-result.v1"
)
STRATEGY_EXECUTION_FIVE_PERIOD_EFFECT_PROBE_HISTORY_VERSION = (
    "ims.strategy-execution-five-period-effect-probe-history.v1"
)

_REQUEST_FIELDS = frozenset(
    {
        "schema_version",
        "effect_probe_request",
        "release",
        "explicit_five_period_effect_probe_start",
    }
)
_CHAIN_ID_PATTERN = re.compile(r"strategy-period-chain-[0-9a-f]{24}\Z")

STRATEGY_EXECUTION_FIVE_PERIOD_EFFECT_PROBE_ATTEMPT_SCHEMA = """
CREATE TABLE IF NOT EXISTS strategy_execution_five_period_effect_probe_attempts (
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
        runner_invocation_count BETWEEN 0 AND 5
    ),
    carryover_invocation_count INTEGER NOT NULL CHECK (
        carryover_invocation_count BETWEEN 0 AND 8
    ),
    candidate_reverified_count INTEGER NOT NULL CHECK (
        candidate_reverified_count BETWEEN 0 AND 5
    ),
    prefix_baseline_verified INTEGER NOT NULL CHECK (
        prefix_baseline_verified IN (0, 1)
    ),
    result_persisted INTEGER NOT NULL CHECK (result_persisted IN (0, 1)),
    simulation_performed INTEGER NOT NULL CHECK (simulation_performed IN (0, 1)),
    UNIQUE(chain_id, idempotency_key)
)
"""

STRATEGY_EXECUTION_FIVE_PERIOD_EFFECT_PROBE_RESULT_SCHEMA = """
CREATE TABLE IF NOT EXISTS strategy_execution_five_period_effect_probe_results (
    chain_id TEXT PRIMARY KEY,
    attempt_id TEXT NOT NULL UNIQUE,
    idempotency_key TEXT NOT NULL,
    content_digest TEXT NOT NULL,
    request_fingerprint TEXT NOT NULL,
    persisted_at TEXT NOT NULL,
    result_digest TEXT NOT NULL UNIQUE,
    request_payload_json TEXT NOT NULL,
    period_chain_payload_json TEXT NOT NULL,
    result_payload_json TEXT NOT NULL
)
"""


class StrategyExecutionFivePeriodEffectProbeStartError(ValueError):
    def __init__(
        self,
        code: str,
        message: str,
        *,
        chain_id: str | None = None,
        attempt_id: str | None = None,
        runner_invocation_count: int = 0,
        carryover_invocation_count: int = 0,
        candidate_reverified_count: int = 0,
        prefix_baseline_verified: bool = False,
        period_chain_digest_reverified: bool = False,
        writes_performed: bool = False,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.chain_id = chain_id
        self.attempt_id = attempt_id
        self.runner_invocation_count = runner_invocation_count
        self.carryover_invocation_count = carryover_invocation_count
        self.candidate_reverified_count = candidate_reverified_count
        self.prefix_baseline_verified = prefix_baseline_verified
        self.period_chain_digest_reverified = period_chain_digest_reverified
        self.writes_performed = writes_performed


@dataclass(frozen=True, slots=True)
class StrategyExecutionFivePeriodEffectProbeStartRequest:
    effect_probe_request: StrategyExecutionFivePeriodEffectProbeRequest
    release: StrategyExecutionPeriodChainRunControlRequest
    explicit_five_period_effect_probe_start: bool
    schema_version: str = (
        STRATEGY_EXECUTION_FIVE_PERIOD_EFFECT_PROBE_START_REQUEST_VERSION
    )

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "effect_probe_request": self.effect_probe_request.to_dict(),
            "release": self.release.to_dict(),
            "explicit_five_period_effect_probe_start": (
                self.explicit_five_period_effect_probe_start
            ),
        }


@dataclass(frozen=True, slots=True)
class StrategyExecutionFivePeriodEffectProbeStoredResult:
    chain_id: str
    attempt_id: str
    idempotency_key: str
    content_digest: str
    persisted_at: str
    result_digest: str
    request_payload: dict[str, object]
    period_chain_payload: dict[str, object]
    result_payload: dict[str, object]

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": (
                STRATEGY_EXECUTION_FIVE_PERIOD_EFFECT_PROBE_STORED_RESULT_VERSION
            ),
            "chain_id": self.chain_id,
            "attempt_id": self.attempt_id,
            "idempotency_key": self.idempotency_key,
            "content_digest": self.content_digest,
            "persisted_at": self.persisted_at,
            "result_digest": self.result_digest,
            "request_payload": deepcopy(self.request_payload),
            "period_chain_payload": deepcopy(self.period_chain_payload),
            "result_payload": deepcopy(self.result_payload),
        }


@dataclass(frozen=True, slots=True)
class StrategyExecutionFivePeriodEffectProbeAttempt:
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
    prefix_baseline_verified: bool
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
            "prefix_baseline_verified": self.prefix_baseline_verified,
            "result_persisted": self.result_persisted,
            "simulation_performed": self.simulation_performed,
        }


@dataclass(frozen=True, slots=True)
class StrategyExecutionFivePeriodEffectProbeStartResult:
    record: StrategyExecutionFivePeriodEffectProbeStoredResult
    replayed: bool

    def to_dict(self) -> dict[str, object]:
        payload = self.record.result_payload
        runner_count = int(payload.get("runner_invocation_count", 0))
        carryover_count = int(payload.get("carryover_invocation_count", 0))
        candidate_count = int(payload.get("candidate_reverified_count", 0))
        return {
            "status": "ok",
            "schema_version": (
                STRATEGY_EXECUTION_FIVE_PERIOD_EFFECT_PROBE_START_RESULT_VERSION
            ),
            "request_schema_version": (
                STRATEGY_EXECUTION_FIVE_PERIOD_EFFECT_PROBE_START_REQUEST_VERSION
            ),
            "mode": "strategy_execution_five_period_effect_probe_start",
            "chain_id": self.record.chain_id,
            "content_digest": self.record.content_digest,
            "attempt_id": self.record.attempt_id,
            "idempotency_key": self.record.idempotency_key,
            "replayed": self.replayed,
            "record": self.record.to_dict(),
            "period_chain_digest_reverified": True,
            "immutable_period_chain_snapshot_persisted": True,
            "prefix_baseline_verified": True,
            "candidate_reverified_count": candidate_count,
            "idempotency_persisted": True,
            "attempt_persisted": True,
            "result_persisted": True,
            "runner_invocation_count": 0 if self.replayed else runner_count,
            "runner_invocation_performed": not self.replayed,
            "carryover_invocation_count": 0 if self.replayed else carryover_count,
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
            "ui_start_enabled": True,
            "historical_rng_equality_claim": False,
            "historical_full_equality_claim": False,
            "next_gate": "PR147",
        }


@dataclass(frozen=True, slots=True)
class StrategyExecutionFivePeriodEffectProbeResultRead:
    chain_id: str
    db_path: str
    record: StrategyExecutionFivePeriodEffectProbeStoredResult | None

    def to_dict(self) -> dict[str, object]:
        return {
            "status": "ok",
            "schema_version": (
                STRATEGY_EXECUTION_FIVE_PERIOD_EFFECT_PROBE_STORED_RESULT_VERSION
            ),
            "mode": "strategy_execution_five_period_effect_probe_result_read_only",
            "chain_id": self.chain_id,
            "db_path": self.db_path,
            "result_available": self.record is not None,
            "record": self.record.to_dict() if self.record is not None else None,
            "writes_performed": False,
            "execution_performed": False,
            "simulation_performed": False,
            "historical_full_equality_claim": False,
        }


@dataclass(frozen=True, slots=True)
class StrategyExecutionFivePeriodEffectProbeHistory:
    chain_id: str
    db_path: str
    attempts: tuple[StrategyExecutionFivePeriodEffectProbeAttempt, ...]
    record: StrategyExecutionFivePeriodEffectProbeStoredResult | None

    def to_dict(self) -> dict[str, object]:
        latest = self.attempts[0] if self.attempts else None
        return {
            "status": "ok",
            "schema_version": (
                STRATEGY_EXECUTION_FIVE_PERIOD_EFFECT_PROBE_HISTORY_VERSION
            ),
            "mode": "strategy_execution_five_period_effect_probe_history_read_only",
            "chain_id": self.chain_id,
            "db_path": self.db_path,
            "attempt_count": len(self.attempts),
            "attempts": [attempt.to_dict() for attempt in self.attempts],
            "latest_attempt": latest.to_dict() if latest is not None else None,
            "result_available": self.record is not None,
            "persisted_at": self.record.persisted_at if self.record else None,
            "result_digest": self.record.result_digest if self.record else None,
            "automatic_retry_enabled": False,
            "queue_worker_enabled": False,
            "writes_performed": False,
            "execution_performed": False,
            "simulation_performed": False,
            "historical_full_equality_claim": False,
        }


def parse_strategy_execution_five_period_effect_probe_start_request(
    value: object,
) -> StrategyExecutionFivePeriodEffectProbeStartRequest:
    if not isinstance(value, dict):
        raise StrategyExecutionFivePeriodEffectProbeStartError(
            "request_object_required",
            "Fuenf-Perioden-Start verlangt ein JSON-Objekt",
        )
    unknown = sorted(field for field in value if field not in _REQUEST_FIELDS)
    missing = sorted(field for field in _REQUEST_FIELDS if field not in value)
    if unknown:
        raise StrategyExecutionFivePeriodEffectProbeStartError(
            "unknown_request_fields",
            "Fuenf-Perioden-Start enthaelt unbekannte Felder: " + ", ".join(unknown),
        )
    if missing:
        raise StrategyExecutionFivePeriodEffectProbeStartError(
            "missing_request_fields",
            "Fuenf-Perioden-Start vermisst Pflichtfelder: " + ", ".join(missing),
        )
    if value["schema_version"] != (
        STRATEGY_EXECUTION_FIVE_PERIOD_EFFECT_PROBE_START_REQUEST_VERSION
    ):
        raise StrategyExecutionFivePeriodEffectProbeStartError(
            "unsupported_schema_version",
            "Fuenf-Perioden-Start erwartet schema_version "
            f"{STRATEGY_EXECUTION_FIVE_PERIOD_EFFECT_PROBE_START_REQUEST_VERSION}",
        )
    if value["explicit_five_period_effect_probe_start"] is not True:
        raise StrategyExecutionFivePeriodEffectProbeStartError(
            "five_period_effect_probe_start_release_required",
            "Fuenf-Perioden-Start muss explizit freigegeben sein",
        )
    try:
        probe_request = parse_strategy_execution_five_period_effect_probe_request(
            value["effect_probe_request"]
        )
    except StrategyExecutionFivePeriodEffectProbeError as exc:
        raise StrategyExecutionFivePeriodEffectProbeStartError(
            exc.code,
            str(exc),
        ) from exc
    try:
        release = parse_strategy_execution_period_chain_run_control_request(
            value["release"]
        )
    except StrategyExecutionPeriodChainRunControlError as exc:
        raise StrategyExecutionFivePeriodEffectProbeStartError(
            exc.code,
            str(exc),
        ) from exc
    return StrategyExecutionFivePeriodEffectProbeStartRequest(
        effect_probe_request=probe_request,
        release=release,
        explicit_five_period_effect_probe_start=True,
    )


def start_strategy_execution_five_period_effect_probe(
    request: StrategyExecutionFivePeriodEffectProbeStartRequest,
    *,
    db_path: Path | str,
    runner: StrategyExecutionPeriodChainEffectProbeRunner | None = None,
    timestamp_factory: Callable[[], str] = lambda: _utc_now(),
) -> StrategyExecutionFivePeriodEffectProbeStartResult:
    resolved_path = Path(db_path).expanduser().resolve()
    release = request.release
    fingerprint = _digest_mapping(request.to_dict())
    attempt_id = _attempt_id(release.chain_id, release.idempotency_key)
    try:
        replay = _claim_or_replay(
            request,
            db_path=resolved_path,
            request_fingerprint=fingerprint,
            attempt_id=attempt_id,
            started_at=timestamp_factory(),
        )
    except StrategyExecutionFivePeriodEffectProbeStartError as exc:
        raise _with_start_context(exc, request=request) from exc
    if replay:
        stored = get_strategy_execution_five_period_effect_probe_result(
            release.chain_id,
            db_path=resolved_path,
        ).record
        if stored is None:  # pragma: no cover - guarded by the claim invariant.
            raise StrategyExecutionFivePeriodEffectProbeStartError(
                "replayed_result_missing",
                "Erfolgreicher Idempotenztreffer hat kein gespeichertes Ergebnis",
                chain_id=release.chain_id,
                attempt_id=attempt_id,
            )
        return StrategyExecutionFivePeriodEffectProbeStartResult(
            record=stored,
            replayed=True,
        )

    runner_count = 0
    carryover_count = 0
    candidate_count = 0
    prefix_verified = False
    chain_verified = False
    try:
        chain_payload, candidate_count = _build_and_verify_released_chain(
            request,
            db_path=resolved_path,
        )
        chain_verified = True
        probe = run_strategy_execution_five_period_effect_probe(
            request.effect_probe_request,
            db_path=resolved_path,
            runner=runner,
        )
        result_payload = probe.to_dict()
        runner_count = int(result_payload["runner_invocation_count"])
        carryover_count = int(result_payload["carryover_invocation_count"])
        candidate_count = int(result_payload["candidate_reverified_count"])
        prefix_verified = result_payload.get("two_period_prefix_verified") is True
        if not probe.execution_performed:
            raise StrategyExecutionFivePeriodEffectProbeStartError(
                "five_period_effect_probe_blocked",
                "Fuenf-Perioden-Wirkungsprobe wurde blockiert",
                chain_id=release.chain_id,
                attempt_id=attempt_id,
                runner_invocation_count=runner_count,
                carryover_invocation_count=carryover_count,
                candidate_reverified_count=candidate_count,
                prefix_baseline_verified=prefix_verified,
            )
        if probe.period_chain != chain_payload:
            raise StrategyExecutionFivePeriodEffectProbeStartError(
                "five_period_chain_changed_before_execution",
                "Kanonische Fuenf-Perioden-Kette hat sich vor der Ausfuehrung geaendert",
                chain_id=release.chain_id,
                attempt_id=attempt_id,
                runner_invocation_count=runner_count,
                carryover_invocation_count=carryover_count,
                candidate_reverified_count=candidate_count,
                prefix_baseline_verified=prefix_verified,
            )
        stored = _complete_attempt(
            request,
            attempt_id=attempt_id,
            request_fingerprint=fingerprint,
            period_chain_payload=chain_payload,
            result_payload=result_payload,
            persisted_at=timestamp_factory(),
            runner_invocation_count=runner_count,
            carryover_invocation_count=carryover_count,
            candidate_reverified_count=candidate_count,
            prefix_baseline_verified=prefix_verified,
            db_path=resolved_path,
        )
    except Exception as exc:
        if isinstance(exc, StrategyExecutionFivePeriodEffectProbeStartError):
            code = exc.code
            message = str(exc)
            runner_count = exc.runner_invocation_count or runner_count
            carryover_count = exc.carryover_invocation_count or carryover_count
            candidate_count = exc.candidate_reverified_count or candidate_count
            prefix_verified = exc.prefix_baseline_verified or prefix_verified
            chain_verified = exc.period_chain_digest_reverified or chain_verified
        elif isinstance(exc, StrategyExecutionFivePeriodEffectProbeError):
            code = exc.code
            message = str(exc)
            runner_count = exc.runner_invocation_count
            carryover_count = exc.carryover_invocation_count
            candidate_count = exc.candidate_reverified_count
            prefix_verified = exc.prefix_baseline_verified
        else:
            code = "five_period_effect_probe_start_failed"
            message = f"Fuenf-Perioden-Start konnte nicht abgeschlossen werden: {exc}"
        _fail_attempt(
            attempt_id,
            code=code,
            message=message,
            completed_at=timestamp_factory(),
            runner_invocation_count=runner_count,
            carryover_invocation_count=carryover_count,
            candidate_reverified_count=candidate_count,
            prefix_baseline_verified=prefix_verified,
            db_path=resolved_path,
        )
        raise StrategyExecutionFivePeriodEffectProbeStartError(
            code,
            message,
            chain_id=release.chain_id,
            attempt_id=attempt_id,
            runner_invocation_count=runner_count,
            carryover_invocation_count=carryover_count,
            candidate_reverified_count=candidate_count,
            prefix_baseline_verified=prefix_verified,
            period_chain_digest_reverified=chain_verified,
            writes_performed=True,
        ) from exc

    return StrategyExecutionFivePeriodEffectProbeStartResult(
        record=stored,
        replayed=False,
    )


def get_strategy_execution_five_period_effect_probe_result(
    chain_id: str,
    *,
    db_path: Path | str,
) -> StrategyExecutionFivePeriodEffectProbeResultRead:
    _validate_chain_id(chain_id)
    resolved_path = Path(db_path).expanduser().resolve()
    connection = _connect_readonly(resolved_path)
    try:
        if not _table_exists(
            connection,
            "strategy_execution_five_period_effect_probe_results",
        ):
            record = None
        else:
            row = connection.execute(
                """
                SELECT chain_id, attempt_id, idempotency_key, content_digest,
                       request_fingerprint, persisted_at, result_digest,
                       request_payload_json, period_chain_payload_json,
                       result_payload_json
                FROM strategy_execution_five_period_effect_probe_results
                WHERE chain_id = ?
                """,
                (chain_id,),
            ).fetchone()
            record = _row_to_verified_result(row) if row is not None else None
    except sqlite3.DatabaseError as exc:
        raise StrategyExecutionFivePeriodEffectProbeStartError(
            "five_period_effect_probe_result_store_unreadable",
            f"Fuenf-Perioden-Ergebnisablage ist nicht lesbar: {exc}",
            chain_id=chain_id,
        ) from exc
    finally:
        connection.close()
    return StrategyExecutionFivePeriodEffectProbeResultRead(
        chain_id=chain_id,
        db_path=str(resolved_path),
        record=record,
    )


def get_strategy_execution_five_period_effect_probe_history(
    chain_id: str,
    *,
    db_path: Path | str,
) -> StrategyExecutionFivePeriodEffectProbeHistory:
    _validate_chain_id(chain_id)
    resolved_path = Path(db_path).expanduser().resolve()
    connection = _connect_readonly(resolved_path)
    try:
        if _table_exists(
            connection,
            "strategy_execution_five_period_effect_probe_attempts",
        ):
            rows = connection.execute(
                """
                SELECT attempt_id, chain_id, content_digest, idempotency_key,
                       status, released_by, released_at, release_reason,
                       started_at, completed_at, failure_code, failure_message,
                       runner_invocation_count, carryover_invocation_count,
                       candidate_reverified_count, prefix_baseline_verified,
                       result_persisted, simulation_performed
                FROM strategy_execution_five_period_effect_probe_attempts
                WHERE chain_id = ?
                ORDER BY started_at DESC, attempt_id DESC
                """,
                (chain_id,),
            ).fetchall()
            attempts = tuple(_row_to_attempt(row) for row in rows)
        else:
            attempts = ()
        if _table_exists(
            connection,
            "strategy_execution_five_period_effect_probe_results",
        ):
            row = connection.execute(
                """
                SELECT chain_id, attempt_id, idempotency_key, content_digest,
                       request_fingerprint, persisted_at, result_digest,
                       request_payload_json, period_chain_payload_json,
                       result_payload_json
                FROM strategy_execution_five_period_effect_probe_results
                WHERE chain_id = ?
                """,
                (chain_id,),
            ).fetchone()
            record = _row_to_verified_result(row) if row is not None else None
        else:
            record = None
    except sqlite3.DatabaseError as exc:
        raise StrategyExecutionFivePeriodEffectProbeStartError(
            "five_period_effect_probe_history_store_unreadable",
            f"Fuenf-Perioden-Versuchsverlauf ist nicht lesbar: {exc}",
            chain_id=chain_id,
        ) from exc
    finally:
        connection.close()
    return StrategyExecutionFivePeriodEffectProbeHistory(
        chain_id=chain_id,
        db_path=str(resolved_path),
        attempts=attempts,
        record=record,
    )


def strategy_execution_five_period_effect_probe_start_contract_payload(
) -> dict[str, object]:
    boundary_flags = {
        "server_start_enabled": True,
        "ui_start_enabled": True,
        "explicit_run_control_release_required": True,
        "explicit_five_period_effect_probe_start_required": True,
        "exact_five_period_horizon_required": True,
        "stored_two_period_prefix_baseline_required": True,
        "period_chain_digest_reverification_required": True,
        "atomic_idempotency_claim_enabled": True,
        "idempotency_persistence_enabled": True,
        "immutable_period_chain_snapshot_persistence_enabled": True,
        "immutable_result_persistence_enabled": True,
        "attempt_history_enabled": True,
        "read_only_result_enabled": True,
        "read_only_history_enabled": True,
        "isolated_candidate_copies_required": True,
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
            STRATEGY_EXECUTION_FIVE_PERIOD_EFFECT_PROBE_START_CONTRACT_VERSION
        ),
        "request_schema_version": (
            STRATEGY_EXECUTION_FIVE_PERIOD_EFFECT_PROBE_START_REQUEST_VERSION
        ),
        "release_request_schema_version": (
            STRATEGY_EXECUTION_PERIOD_CHAIN_RUN_CONTROL_REQUEST_VERSION
        ),
        "effect_probe_request_schema_version": (
            STRATEGY_EXECUTION_FIVE_PERIOD_EFFECT_PROBE_REQUEST_VERSION
        ),
        "effect_result_schema_version": (
            STRATEGY_EXECUTION_FIVE_PERIOD_EFFECT_PROBE_RESULT_VERSION
        ),
        "stored_result_schema_version": (
            STRATEGY_EXECUTION_FIVE_PERIOD_EFFECT_PROBE_STORED_RESULT_VERSION
        ),
        "history_schema_version": (
            STRATEGY_EXECUTION_FIVE_PERIOD_EFFECT_PROBE_HISTORY_VERSION
        ),
        "period_chain_schema_version": STRATEGY_EXECUTION_PERIOD_CHAIN_VERSION,
        "mode": "strategy_execution_five_period_effect_probe_start_contract",
        "start_endpoint": (
            "/api/run-control/strategy-period-chain-five-period-effect-probe-start"
        ),
        "result_endpoint_template": (
            "/api/run-control/strategy-period-chain-five-period-effect-probe-result/{chain_id}"
        ),
        "history_endpoint_template": (
            "/api/run-control/strategy-period-chain-five-period-effect-probe-history/{chain_id}"
        ),
        "request_source": "pr144_effect_probe_request_wrapped_unchanged",
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
        "result_digest_scope": [
            "storage_identity_and_persisted_at",
            "complete_start_request",
            "canonical_five_period_chain_snapshot",
            "complete_five_period_effect_result",
        ],
        "next_gate": "PR147",
        "boundary_flags": boundary_flags,
        **boundary_flags,
    }


def strategy_execution_five_period_effect_probe_start_error_payload(
    code: str,
    message: str,
    *,
    chain_id: str | None = None,
    attempt_id: str | None = None,
    runner_invocation_count: int = 0,
    carryover_invocation_count: int = 0,
    candidate_reverified_count: int = 0,
    prefix_baseline_verified: bool = False,
    period_chain_digest_reverified: bool = False,
    writes_performed: bool = False,
) -> dict[str, object]:
    return {
        "status": "error",
        "schema_version": (
            STRATEGY_EXECUTION_FIVE_PERIOD_EFFECT_PROBE_START_RESULT_VERSION
        ),
        "mode": "strategy_execution_five_period_effect_probe_start",
        "chain_id": chain_id,
        "attempt_id": attempt_id,
        "issue_count": 1,
        "issues": [{"code": code, "message": message}],
        "period_chain_digest_reverified": period_chain_digest_reverified,
        "prefix_baseline_verified": prefix_baseline_verified,
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
        "ui_start_enabled": True,
        "historical_full_equality_claim": False,
        "next_gate": "PR147",
    }


def _build_and_verify_released_chain(
    request: StrategyExecutionFivePeriodEffectProbeStartRequest,
    *,
    db_path: Path,
) -> tuple[dict[str, object], int]:
    build = build_strategy_execution_five_period_chain(
        request.effect_probe_request.period_chain_input,
        db_path=db_path,
    )
    if not build.build_complete or build.chain is None:
        issue = build.issues[0] if build.issues else None
        raise StrategyExecutionFivePeriodEffectProbeStartError(
            issue.code if issue is not None else "five_period_chain_not_ready",
            issue.message if issue is not None else "Fuenf-Perioden-Kette ist nicht bereit",
            chain_id=request.release.chain_id,
            candidate_reverified_count=build.resolved_candidate_count,
        )
    chain = build.chain
    if (
        chain.chain_id != request.release.chain_id
        or chain.content_digest != request.release.expected_content_digest
    ):
        raise StrategyExecutionFivePeriodEffectProbeStartError(
            "five_period_release_identity_mismatch",
            "Run-Control-Freigabe passt nicht zur kanonischen Fuenf-Perioden-Kette",
            chain_id=request.release.chain_id,
            candidate_reverified_count=build.resolved_candidate_count,
        )
    return chain.to_dict(), build.resolved_candidate_count


def _claim_or_replay(
    request: StrategyExecutionFivePeriodEffectProbeStartRequest,
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
        connection.execute(STRATEGY_EXECUTION_FIVE_PERIOD_EFFECT_PROBE_ATTEMPT_SCHEMA)
        connection.execute(STRATEGY_EXECUTION_FIVE_PERIOD_EFFECT_PROBE_RESULT_SCHEMA)
        existing = connection.execute(
            """
            SELECT attempt_id, request_fingerprint, status
            FROM strategy_execution_five_period_effect_probe_attempts
            WHERE chain_id = ? AND idempotency_key = ?
            """,
            (release.chain_id, release.idempotency_key),
        ).fetchone()
        if existing is not None:
            if existing["request_fingerprint"] != request_fingerprint:
                raise StrategyExecutionFivePeriodEffectProbeStartError(
                    "idempotency_payload_conflict",
                    "Idempotenzschluessel wurde mit anderem Fuenf-Perioden-Request verwendet",
                    chain_id=release.chain_id,
                    attempt_id=str(existing["attempt_id"]),
                )
            if existing["status"] != "result_persisted":
                raise StrategyExecutionFivePeriodEffectProbeStartError(
                    "idempotency_attempt_not_replayable",
                    "Vorhandener Startversuch ist nicht erfolgreich wiederholbar: "
                    f"{existing['status']}",
                    chain_id=release.chain_id,
                    attempt_id=str(existing["attempt_id"]),
                )
            result_exists = connection.execute(
                """
                SELECT 1
                FROM strategy_execution_five_period_effect_probe_results
                WHERE chain_id = ? AND attempt_id = ?
                """,
                (release.chain_id, existing["attempt_id"]),
            ).fetchone()
            if result_exists is None:
                raise StrategyExecutionFivePeriodEffectProbeStartError(
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
            FROM strategy_execution_five_period_effect_probe_results
            WHERE chain_id = ?
            """,
            (release.chain_id,),
        ).fetchone()
        if result_exists is not None:
            raise StrategyExecutionFivePeriodEffectProbeStartError(
                "five_period_result_already_persisted",
                "Fuenf-Perioden-Kette hat bereits ein unveraenderliches Ergebnis",
                chain_id=release.chain_id,
                attempt_id=str(result_exists["attempt_id"]),
            )
        active = connection.execute(
            """
            SELECT attempt_id
            FROM strategy_execution_five_period_effect_probe_attempts
            WHERE chain_id = ? AND status = 'starting'
            """,
            (release.chain_id,),
        ).fetchone()
        if active is not None:
            raise StrategyExecutionFivePeriodEffectProbeStartError(
                "five_period_effect_probe_already_starting",
                "Fuer diese Fuenf-Perioden-Kette laeuft bereits ein Start",
                chain_id=release.chain_id,
                attempt_id=str(active["attempt_id"]),
            )
        connection.execute(
            """
            INSERT INTO strategy_execution_five_period_effect_probe_attempts (
                attempt_id, chain_id, content_digest, idempotency_key,
                request_fingerprint, status, released_by, released_at,
                release_reason, started_at, completed_at, failure_code,
                failure_message, runner_invocation_count,
                carryover_invocation_count, candidate_reverified_count,
                prefix_baseline_verified, result_persisted, simulation_performed
            ) VALUES (?, ?, ?, ?, ?, 'starting', ?, ?, ?, ?, NULL, NULL, NULL,
                      0, 0, 0, 0, 0, 0)
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
    request: StrategyExecutionFivePeriodEffectProbeStartRequest,
    *,
    attempt_id: str,
    request_fingerprint: str,
    period_chain_payload: dict[str, object],
    result_payload: dict[str, object],
    persisted_at: str,
    runner_invocation_count: int,
    carryover_invocation_count: int,
    candidate_reverified_count: int,
    prefix_baseline_verified: bool,
    db_path: Path,
) -> StrategyExecutionFivePeriodEffectProbeStoredResult:
    release = request.release
    request_payload = request.to_dict()
    envelope = _result_digest_envelope(
        chain_id=release.chain_id,
        attempt_id=attempt_id,
        idempotency_key=release.idempotency_key,
        content_digest=release.expected_content_digest,
        persisted_at=persisted_at,
        request_payload=request_payload,
        period_chain_payload=period_chain_payload,
        result_payload=result_payload,
    )
    result_digest = _digest_mapping(envelope)
    record = StrategyExecutionFivePeriodEffectProbeStoredResult(
        chain_id=release.chain_id,
        attempt_id=attempt_id,
        idempotency_key=release.idempotency_key,
        content_digest=release.expected_content_digest,
        persisted_at=persisted_at,
        result_digest=result_digest,
        request_payload=deepcopy(request_payload),
        period_chain_payload=deepcopy(period_chain_payload),
        result_payload=deepcopy(result_payload),
    )
    connection = connect_metadata_db(db_path)
    try:
        connection.execute("BEGIN IMMEDIATE")
        attempt = connection.execute(
            """
            SELECT status, content_digest, request_fingerprint
            FROM strategy_execution_five_period_effect_probe_attempts
            WHERE attempt_id = ? AND chain_id = ?
            """,
            (attempt_id, release.chain_id),
        ).fetchone()
        if attempt is None or attempt["status"] != "starting":
            raise StrategyExecutionFivePeriodEffectProbeStartError(
                "five_period_attempt_completion_conflict",
                "Fuenf-Perioden-Startversuch ist nicht mehr atomar abschliessbar",
                chain_id=release.chain_id,
                attempt_id=attempt_id,
            )
        if (
            attempt["content_digest"] != release.expected_content_digest
            or attempt["request_fingerprint"] != request_fingerprint
        ):
            raise StrategyExecutionFivePeriodEffectProbeStartError(
                "five_period_attempt_identity_conflict",
                "Fuenf-Perioden-Startversuch verweist auf einen anderen Inhalt",
                chain_id=release.chain_id,
                attempt_id=attempt_id,
            )
        connection.execute(
            """
            INSERT INTO strategy_execution_five_period_effect_probe_results (
                chain_id, attempt_id, idempotency_key, content_digest,
                request_fingerprint, persisted_at, result_digest,
                request_payload_json, period_chain_payload_json,
                result_payload_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                record.chain_id,
                record.attempt_id,
                record.idempotency_key,
                record.content_digest,
                request_fingerprint,
                record.persisted_at,
                record.result_digest,
                _stable_json(record.request_payload),
                _stable_json(record.period_chain_payload),
                _stable_json(record.result_payload),
            ),
        )
        updated = connection.execute(
            """
            UPDATE strategy_execution_five_period_effect_probe_attempts
            SET status = 'result_persisted', completed_at = ?,
                runner_invocation_count = ?, carryover_invocation_count = ?,
                candidate_reverified_count = ?, prefix_baseline_verified = ?,
                result_persisted = 1
            WHERE attempt_id = ? AND status = 'starting'
            """,
            (
                persisted_at,
                runner_invocation_count,
                carryover_invocation_count,
                candidate_reverified_count,
                int(prefix_baseline_verified),
                attempt_id,
            ),
        )
        if updated.rowcount != 1:
            raise StrategyExecutionFivePeriodEffectProbeStartError(
                "five_period_attempt_completion_lost",
                "Fuenf-Perioden-Startversuch verlor seinen atomaren Abschluss",
                chain_id=release.chain_id,
                attempt_id=attempt_id,
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
    prefix_baseline_verified: bool,
    db_path: Path,
) -> None:
    connection = connect_metadata_db(db_path)
    try:
        with connection:
            connection.execute(
                """
                UPDATE strategy_execution_five_period_effect_probe_attempts
                SET status = 'failed', completed_at = ?, failure_code = ?,
                    failure_message = ?, runner_invocation_count = ?,
                    carryover_invocation_count = ?, candidate_reverified_count = ?,
                    prefix_baseline_verified = ?
                WHERE attempt_id = ? AND status = 'starting'
                """,
                (
                    completed_at,
                    code[:100],
                    message[:1000],
                    runner_invocation_count,
                    carryover_invocation_count,
                    candidate_reverified_count,
                    int(prefix_baseline_verified),
                    attempt_id,
                ),
            )
    finally:
        connection.close()


def _row_to_verified_result(
    row: sqlite3.Row,
) -> StrategyExecutionFivePeriodEffectProbeStoredResult:
    chain_id = str(row["chain_id"])
    request_payload = _decode_object(
        row["request_payload_json"],
        code="five_period_result_request_invalid",
        label="Gespeicherter Fuenf-Perioden-Startrequest",
        chain_id=chain_id,
    )
    chain_payload = _decode_object(
        row["period_chain_payload_json"],
        code="five_period_result_chain_invalid",
        label="Gespeicherte Fuenf-Perioden-Kette",
        chain_id=chain_id,
    )
    result_payload = _decode_object(
        row["result_payload_json"],
        code="five_period_result_payload_invalid",
        label="Gespeichertes Fuenf-Perioden-Ergebnis",
        chain_id=chain_id,
    )
    try:
        request = parse_strategy_execution_five_period_effect_probe_start_request(
            request_payload
        )
    except StrategyExecutionFivePeriodEffectProbeStartError as exc:
        raise StrategyExecutionFivePeriodEffectProbeStartError(
            "five_period_result_request_invalid",
            "Gespeicherter Fuenf-Perioden-Startrequest verletzt seinen Vertrag",
            chain_id=chain_id,
        ) from exc
    identity = chain_payload.get("identity")
    sections = {
        key: deepcopy(value)
        for key, value in chain_payload.items()
        if key not in {"schema_version", "mode", "base_model", "identity"}
    }
    try:
        calculated_content_digest = (
            calculate_strategy_execution_period_chain_content_digest(
                sections=sections,
                period_chain_schema_version=str(chain_payload.get("schema_version")),
                base_model=str(chain_payload.get("base_model")),
            )
        )
    except (TypeError, ValueError, OverflowError) as exc:
        raise StrategyExecutionFivePeriodEffectProbeStartError(
            "five_period_result_chain_not_canonicalizable",
            "Gespeicherte Fuenf-Perioden-Kette ist nicht kanonisierbar",
            chain_id=chain_id,
        ) from exc
    period_effects = result_payload.get("period_effects")
    transition_effects = result_payload.get("transition_effects")
    periods = (
        [effect.get("period") for effect in period_effects]
        if isinstance(period_effects, list)
        and all(isinstance(effect, dict) for effect in period_effects)
        else []
    )
    transition_pairs = (
        [
            [effect.get("from_period"), effect.get("to_period")]
            for effect in transition_effects
        ]
        if isinstance(transition_effects, list)
        and all(isinstance(effect, dict) for effect in transition_effects)
        else []
    )
    prefix_proof = result_payload.get("prefix_proof")
    envelope = _result_digest_envelope(
        chain_id=chain_id,
        attempt_id=str(row["attempt_id"]),
        idempotency_key=str(row["idempotency_key"]),
        content_digest=str(row["content_digest"]),
        persisted_at=str(row["persisted_at"]),
        request_payload=request_payload,
        period_chain_payload=chain_payload,
        result_payload=result_payload,
    )
    checks = {
        "five_period_result_request_fingerprint_mismatch": (
            str(row["request_fingerprint"]) == _digest_mapping(request_payload)
        ),
        "five_period_result_digest_mismatch": (
            str(row["result_digest"]) == _digest_mapping(envelope)
        ),
        "five_period_result_release_mismatch": (
            request.release.chain_id == chain_id
            and request.release.expected_content_digest == str(row["content_digest"])
            and request.release.idempotency_key == str(row["idempotency_key"])
        ),
        "five_period_result_attempt_identity_mismatch": (
            str(row["attempt_id"])
            == _attempt_id(chain_id, str(row["idempotency_key"]))
        ),
        "five_period_result_chain_identity_mismatch": (
            isinstance(identity, dict)
            and identity.get("chain_id") == chain_id
            and identity.get("content_digest") == str(row["content_digest"])
            and calculated_content_digest == str(row["content_digest"])
            and strategy_execution_period_chain_id_from_digest(
                calculated_content_digest
            )
            == chain_id
        ),
        "five_period_result_chain_schema_mismatch": (
            chain_payload.get("schema_version") == STRATEGY_EXECUTION_PERIOD_CHAIN_VERSION
            and chain_payload.get("mode") == "strategy_execution_period_chain"
            and chain_payload.get("base_model") == "Vdefmd6"
        ),
        "five_period_result_schema_mismatch": (
            result_payload.get("schema_version")
            == STRATEGY_EXECUTION_FIVE_PERIOD_EFFECT_PROBE_RESULT_VERSION
        ),
        "five_period_result_request_mismatch": (
            result_payload.get("request") == request.effect_probe_request.to_dict()
        ),
        "five_period_result_identity_mismatch": (
            result_payload.get("period_chain_identity") == identity
        ),
        "five_period_result_horizon_mismatch": (
            periods == [1, 2, 3, 4, 5]
            and transition_pairs == [[1, 2], [2, 3], [3, 4], [4, 5]]
        ),
        "five_period_result_prefix_mismatch": (
            isinstance(prefix_proof, dict)
            and prefix_proof.get("prefix_equal") is True
            and result_payload.get("two_period_prefix_verified") is True
        ),
        "five_period_result_status_mismatch": (
            result_payload.get("status") == "ok"
            and result_payload.get("period_count") == 5
            and result_payload.get("runner_invocation_count") == 5
            and result_payload.get("transition_count") == 4
            and result_payload.get("execution_performed") is True
            and result_payload.get("partial_result_returned") is False
            and result_payload.get("output_files_written") is False
            and result_payload.get("simulation_performed") is False
        ),
    }
    failed = next((code for code, passed in checks.items() if not passed), None)
    if failed is not None:
        raise StrategyExecutionFivePeriodEffectProbeStartError(
            failed,
            "Gespeichertes Fuenf-Perioden-Ergebnis verletzt seine Integritaetsgrenze",
            chain_id=chain_id,
        )
    return StrategyExecutionFivePeriodEffectProbeStoredResult(
        chain_id=chain_id,
        attempt_id=str(row["attempt_id"]),
        idempotency_key=str(row["idempotency_key"]),
        content_digest=str(row["content_digest"]),
        persisted_at=str(row["persisted_at"]),
        result_digest=str(row["result_digest"]),
        request_payload=request_payload,
        period_chain_payload=chain_payload,
        result_payload=result_payload,
    )


def _row_to_attempt(row: sqlite3.Row) -> StrategyExecutionFivePeriodEffectProbeAttempt:
    return StrategyExecutionFivePeriodEffectProbeAttempt(
        attempt_id=str(row["attempt_id"]),
        chain_id=str(row["chain_id"]),
        content_digest=str(row["content_digest"]),
        idempotency_key=str(row["idempotency_key"]),
        status=str(row["status"]),
        released_by=str(row["released_by"]),
        released_at=str(row["released_at"]),
        release_reason=str(row["release_reason"]),
        started_at=str(row["started_at"]),
        completed_at=str(row["completed_at"]) if row["completed_at"] else None,
        failure_code=str(row["failure_code"]) if row["failure_code"] else None,
        failure_message=(
            str(row["failure_message"]) if row["failure_message"] else None
        ),
        runner_invocation_count=int(row["runner_invocation_count"]),
        carryover_invocation_count=int(row["carryover_invocation_count"]),
        candidate_reverified_count=int(row["candidate_reverified_count"]),
        prefix_baseline_verified=bool(row["prefix_baseline_verified"]),
        result_persisted=bool(row["result_persisted"]),
        simulation_performed=bool(row["simulation_performed"]),
    )


def _with_start_context(
    exc: StrategyExecutionFivePeriodEffectProbeStartError,
    *,
    request: StrategyExecutionFivePeriodEffectProbeStartRequest,
) -> StrategyExecutionFivePeriodEffectProbeStartError:
    return StrategyExecutionFivePeriodEffectProbeStartError(
        exc.code,
        str(exc),
        chain_id=exc.chain_id or request.release.chain_id,
        attempt_id=exc.attempt_id,
        runner_invocation_count=exc.runner_invocation_count,
        carryover_invocation_count=exc.carryover_invocation_count,
        candidate_reverified_count=exc.candidate_reverified_count,
        prefix_baseline_verified=exc.prefix_baseline_verified,
        period_chain_digest_reverified=exc.period_chain_digest_reverified,
        writes_performed=exc.writes_performed,
    )


def _decode_object(
    value: object,
    *,
    code: str,
    label: str,
    chain_id: str,
) -> dict[str, object]:
    try:
        payload = json.loads(value)
    except (TypeError, json.JSONDecodeError) as exc:
        raise StrategyExecutionFivePeriodEffectProbeStartError(
            code,
            f"{label} ist kein gueltiges JSON",
            chain_id=chain_id,
        ) from exc
    if not isinstance(payload, dict):
        raise StrategyExecutionFivePeriodEffectProbeStartError(
            code,
            f"{label} muss ein JSON-Objekt sein",
            chain_id=chain_id,
        )
    return payload


def _validate_chain_id(chain_id: str) -> None:
    if _CHAIN_ID_PATTERN.fullmatch(chain_id) is None:
        raise StrategyExecutionFivePeriodEffectProbeStartError(
            "chain_id_invalid",
            "Fuenf-Perioden-Ketten-ID hat nicht das erwartete Format",
            chain_id=chain_id,
        )


def _connect_readonly(path: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(
        readonly_sqlite_uri(
            path,
            description="five period strategy effect probe evidence",
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


def _attempt_id(chain_id: str, idempotency_key: str) -> str:
    digest = hashlib.sha256(
        f"{chain_id}\0{idempotency_key}".encode("utf-8")
    ).hexdigest()
    return f"strategy-five-chain-probe-{digest[:24]}"


def _digest_mapping(payload: Mapping[str, object]) -> str:
    return "sha256:" + hashlib.sha256(_stable_json(payload).encode("ascii")).hexdigest()


def _result_digest_envelope(
    *,
    chain_id: str,
    attempt_id: str,
    idempotency_key: str,
    content_digest: str,
    persisted_at: str,
    request_payload: dict[str, object],
    period_chain_payload: dict[str, object],
    result_payload: dict[str, object],
) -> dict[str, object]:
    return {
        "storage_identity": {
            "chain_id": chain_id,
            "attempt_id": attempt_id,
            "idempotency_key": idempotency_key,
            "content_digest": content_digest,
            "persisted_at": persisted_at,
        },
        "request_payload": request_payload,
        "period_chain_payload": period_chain_payload,
        "result_payload": result_payload,
    }


def _stable_json(payload: Mapping[str, object]) -> str:
    return json.dumps(
        payload,
        ensure_ascii=True,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
