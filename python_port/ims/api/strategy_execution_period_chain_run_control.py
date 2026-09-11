from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
import re

from ims.api.strategy_execution_period_chain_build import (
    strategy_execution_period_chain_id_from_digest,
)
from ims.api.strategy_execution_period_chain_store import (
    STRATEGY_EXECUTION_PERIOD_CHAIN_STORE_VERSION,
    StrategyExecutionPeriodChainStoreError,
    StrategyExecutionPeriodChainStoreRecord,
    get_strategy_execution_period_chain,
)
from ims.strategies.execution_period_chain_contract import (
    STRATEGY_EXECUTION_PERIOD_CHAIN_VERSION,
)


STRATEGY_EXECUTION_PERIOD_CHAIN_RUN_CONTROL_CONTRACT_VERSION = (
    "ims.strategy-execution-period-chain-run-control-contract.v1"
)
STRATEGY_EXECUTION_PERIOD_CHAIN_RUN_CONTROL_REQUEST_VERSION = (
    "ims.strategy-execution-period-chain-run-control-request.v1"
)
STRATEGY_EXECUTION_PERIOD_CHAIN_RUN_CONTROL_CHECK_VERSION = (
    "ims.strategy-execution-period-chain-run-control-check.v1"
)

_REQUEST_FIELDS = frozenset(
    {
        "schema_version",
        "chain_id",
        "expected_content_digest",
        "idempotency_key",
        "explicit_run_control_release",
        "released_by",
        "released_at",
        "release_reason",
    }
)
_DIGEST_PATTERN = re.compile(r"sha256:[0-9a-f]{64}\Z")
_CHAIN_ID_PATTERN = re.compile(r"strategy-period-chain-[0-9a-f]{24}\Z")
_CLOSED_CHAIN_BOUNDARIES = (
    "persistence_enabled",
    "runner_enabled",
    "ui_start_enabled",
    "carryover_execution_enabled",
    "multi_period_execution_enabled",
    "output_files_enabled",
    "simulation_performed",
)


class StrategyExecutionPeriodChainRunControlError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


@dataclass(frozen=True, slots=True)
class StrategyExecutionPeriodChainRunControlRequest:
    chain_id: str
    expected_content_digest: str
    idempotency_key: str
    explicit_run_control_release: bool
    released_by: str
    released_at: str
    release_reason: str
    schema_version: str = STRATEGY_EXECUTION_PERIOD_CHAIN_RUN_CONTROL_REQUEST_VERSION

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "chain_id": self.chain_id,
            "expected_content_digest": self.expected_content_digest,
            "idempotency_key": self.idempotency_key,
            "explicit_run_control_release": self.explicit_run_control_release,
            "released_by": self.released_by,
            "released_at": self.released_at,
            "release_reason": self.release_reason,
        }


@dataclass(frozen=True, slots=True)
class StrategyExecutionPeriodChainRunControlCheck:
    code: str
    passed: bool
    message: str

    def to_dict(self) -> dict[str, object]:
        return {
            "code": self.code,
            "passed": self.passed,
            "message": self.message,
        }


@dataclass(frozen=True, slots=True)
class StrategyExecutionPeriodChainRunControlResult:
    request: StrategyExecutionPeriodChainRunControlRequest
    checks: tuple[StrategyExecutionPeriodChainRunControlCheck, ...]
    period_chain: dict[str, object] | None
    release_ready: bool
    record: StrategyExecutionPeriodChainStoreRecord | None = field(
        default=None,
        repr=False,
        compare=False,
    )

    @property
    def issues(self) -> tuple[dict[str, str], ...]:
        return tuple(
            {"code": check.code, "message": check.message}
            for check in self.checks
            if not check.passed
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": (
                STRATEGY_EXECUTION_PERIOD_CHAIN_RUN_CONTROL_CHECK_VERSION
            ),
            "request_schema_version": (
                STRATEGY_EXECUTION_PERIOD_CHAIN_RUN_CONTROL_REQUEST_VERSION
            ),
            "period_chain_schema_version": STRATEGY_EXECUTION_PERIOD_CHAIN_VERSION,
            "period_chain_store_schema_version": (
                STRATEGY_EXECUTION_PERIOD_CHAIN_STORE_VERSION
            ),
            "mode": "strategy_execution_period_chain_run_control_release_check",
            "status": "ready" if self.release_ready else "blocked",
            "request": self.request.to_dict(),
            "period_chain": (
                dict(self.period_chain) if self.period_chain is not None else None
            ),
            "checks": [check.to_dict() for check in self.checks],
            "issue_count": len(self.issues),
            "issues": [dict(issue) for issue in self.issues],
            "period_chain_resolved": self.period_chain is not None,
            "period_chain_digest_reverified": self.period_chain is not None,
            "run_control_release_checked": True,
            "release_ready": self.release_ready,
            "queue_entry_created": False,
            "preflight_performed": False,
            "period_chain_start_allowed": False,
            "carryover_invocation_performed": False,
            "runner_invocation_performed": False,
            "writes_performed": False,
            "execution_performed": False,
            "simulation_performed": False,
            "automatic_historical_rule_selection_performed": False,
            "historical_rng_equality_claim": False,
            "historical_full_equality_claim": False,
            "next_gate": "PR139",
        }


def parse_strategy_execution_period_chain_run_control_request(
    value: object,
) -> StrategyExecutionPeriodChainRunControlRequest:
    if not isinstance(value, dict):
        raise StrategyExecutionPeriodChainRunControlError(
            "request_object_required",
            "Run-Control-Ketteneingang muss ein JSON-Objekt sein",
        )
    unknown_fields = sorted(field for field in value if field not in _REQUEST_FIELDS)
    if unknown_fields:
        raise StrategyExecutionPeriodChainRunControlError(
            "unknown_request_fields",
            "Run-Control-Ketteneingang enthaelt unbekannte Felder: "
            + ", ".join(unknown_fields),
        )
    missing_fields = sorted(field for field in _REQUEST_FIELDS if field not in value)
    if missing_fields:
        raise StrategyExecutionPeriodChainRunControlError(
            "missing_request_fields",
            "Run-Control-Ketteneingang vermisst Pflichtfelder: "
            + ", ".join(missing_fields),
        )

    schema_version = _required_text(value, "schema_version")
    if schema_version != STRATEGY_EXECUTION_PERIOD_CHAIN_RUN_CONTROL_REQUEST_VERSION:
        raise StrategyExecutionPeriodChainRunControlError(
            "unsupported_schema_version",
            "Run-Control-Ketteneingang erwartet schema_version "
            f"{STRATEGY_EXECUTION_PERIOD_CHAIN_RUN_CONTROL_REQUEST_VERSION}",
        )
    chain_id = _required_text(value, "chain_id")
    if _CHAIN_ID_PATTERN.fullmatch(chain_id) is None:
        raise StrategyExecutionPeriodChainRunControlError(
            "chain_id_invalid",
            "Ketten-ID muss dem gespeicherten strategy-period-chain-Format "
            "entsprechen",
        )
    content_digest = _required_text(value, "expected_content_digest")
    if _DIGEST_PATTERN.fullmatch(content_digest) is None:
        raise StrategyExecutionPeriodChainRunControlError(
            "content_digest_invalid",
            "Erwarteter Kettendigest muss ein kleingeschriebener "
            "SHA-256-Digest sein",
        )
    explicit_release = value["explicit_run_control_release"]
    if not isinstance(explicit_release, bool) or not explicit_release:
        raise StrategyExecutionPeriodChainRunControlError(
            "run_control_release_required",
            "Run-Control-Kettenfreigabe muss explizit true sein",
        )
    released_at = _required_text(value, "released_at")
    _validate_utc_timestamp(released_at)
    return StrategyExecutionPeriodChainRunControlRequest(
        schema_version=schema_version,
        chain_id=chain_id,
        expected_content_digest=content_digest,
        idempotency_key=_required_text(value, "idempotency_key"),
        explicit_run_control_release=explicit_release,
        released_by=_required_text(value, "released_by"),
        released_at=released_at,
        release_reason=_required_text(value, "release_reason"),
    )


def check_strategy_execution_period_chain_run_control_release(
    request: StrategyExecutionPeriodChainRunControlRequest,
    *,
    db_path: Path | str,
) -> StrategyExecutionPeriodChainRunControlResult:
    checks: list[StrategyExecutionPeriodChainRunControlCheck] = []
    _add_check(
        checks,
        "run_control_release_explicit",
        request.explicit_run_control_release,
        "Explizite Run-Control-Kettenfreigabe fehlt",
    )
    identity_matches = request.chain_id == (
        strategy_execution_period_chain_id_from_digest(
            request.expected_content_digest
        )
    )
    _add_check(
        checks,
        "request_identity_consistent",
        identity_matches,
        "Ketten-ID passt nicht zum erwarteten Digest",
    )
    if not identity_matches:
        return _result(request, checks, period_chain=None, record=None)

    try:
        stored = get_strategy_execution_period_chain(
            request.chain_id,
            db_path=db_path,
        )
    except StrategyExecutionPeriodChainStoreError as exc:
        _add_check(checks, exc.code, False, str(exc))
        return _result(request, checks, period_chain=None, record=None)

    record = stored.record
    _add_check(
        checks,
        "period_chain_resolved",
        True,
        "Gespeicherte Periodenkette konnte nicht aufgeloest werden",
    )
    _add_check(
        checks,
        "period_chain_id_verified",
        record.chain_id == request.chain_id,
        "Gespeicherte Ketten-ID weicht vom Request ab",
    )
    _add_check(
        checks,
        "period_chain_digest_reverified",
        stored.post_storage_digest_verified,
        "Gespeicherter Kettendigest konnte nicht erneut bestaetigt werden",
    )
    _add_check(
        checks,
        "expected_digest_matches",
        record.content_digest == request.expected_content_digest,
        "Gespeicherter Kettendigest weicht vom erwarteten Digest ab",
    )
    horizon_consistent = (
        record.first_period == 1
        and record.last_period == record.period_count
        and record.period_count == record.max_periods
    )
    _add_check(
        checks,
        "period_chain_horizon_verified",
        horizon_consistent,
        "Gespeicherter Kettenhorizont ist nicht konsistent",
    )
    boundaries = record.period_chain.get("execution_boundaries")
    boundaries_closed = isinstance(boundaries, dict) and all(
        boundaries.get(field) is False for field in _CLOSED_CHAIN_BOUNDARIES
    )
    _add_check(
        checks,
        "period_chain_execution_boundaries_closed",
        boundaries_closed,
        "Gespeicherte Periodenkette hat unerwartet offene "
        "Ausfuehrungsgrenzen",
    )
    return _result(
        request,
        checks,
        period_chain=_period_chain_summary(record),
        record=record,
    )


def strategy_execution_period_chain_run_control_contract_payload() -> dict[
    str, object
]:
    return {
        "schema_version": (
            STRATEGY_EXECUTION_PERIOD_CHAIN_RUN_CONTROL_CONTRACT_VERSION
        ),
        "request_schema_version": (
            STRATEGY_EXECUTION_PERIOD_CHAIN_RUN_CONTROL_REQUEST_VERSION
        ),
        "check_schema_version": (
            STRATEGY_EXECUTION_PERIOD_CHAIN_RUN_CONTROL_CHECK_VERSION
        ),
        "period_chain_schema_version": STRATEGY_EXECUTION_PERIOD_CHAIN_VERSION,
        "period_chain_store_schema_version": (
            STRATEGY_EXECUTION_PERIOD_CHAIN_STORE_VERSION
        ),
        "mode": "strategy_execution_period_chain_run_control_contract_read_only",
        "contract_endpoint": "/api/run-control/strategy-period-chain-contract",
        "release_check_endpoint": (
            "/api/run-control/strategy-period-chain-release-check"
        ),
        "accepted_request_fields": sorted(_REQUEST_FIELDS),
        "required_request_fields": sorted(_REQUEST_FIELDS),
        "authoritative_identity_fields": [
            "chain_id",
            "expected_content_digest",
        ],
        "audit_fields": [
            "idempotency_key",
            "released_by",
            "released_at",
            "release_reason",
        ],
        "forbidden_request_fields": [
            "period_chain",
            "period_chain_input",
            "candidate",
            "candidate_payload",
            "metadata_db",
            "db_path",
            "queue_id",
            "run_id",
            "fixture_path",
            "output_dir",
            "execution_enabled",
        ],
        "release_ready_meaning": (
            "period_chain_identity_storage_integrity_horizon_and_closed_"
            "boundaries_verified"
        ),
        "explicit_run_control_release_required": True,
        "period_chain_resolution_enabled": True,
        "period_chain_digest_reverification_enabled": True,
        "period_chain_horizon_check_enabled": True,
        "candidate_re_resolution_enabled": False,
        "run_control_release_check_enabled": True,
        "queue_write_enabled": False,
        "preflight_enabled": False,
        "period_chain_start_allowed": False,
        "carryover_invocation_enabled": False,
        "runner_enabled": False,
        "writes_enabled": False,
        "execution_enabled": False,
        "simulation_performed": False,
        "historical_rng_equality_claim": False,
        "historical_full_equality_claim": False,
        "next_gate": "PR139",
    }


def strategy_execution_period_chain_run_control_error_payload(
    code: str,
    message: str,
) -> dict[str, object]:
    return {
        "schema_version": (
            STRATEGY_EXECUTION_PERIOD_CHAIN_RUN_CONTROL_CHECK_VERSION
        ),
        "request_schema_version": (
            STRATEGY_EXECUTION_PERIOD_CHAIN_RUN_CONTROL_REQUEST_VERSION
        ),
        "period_chain_schema_version": STRATEGY_EXECUTION_PERIOD_CHAIN_VERSION,
        "mode": "strategy_execution_period_chain_run_control_release_check",
        "status": "error",
        "period_chain": None,
        "checks": [],
        "issue_count": 1,
        "issues": [{"code": code, "message": message}],
        "period_chain_resolved": False,
        "period_chain_digest_reverified": False,
        "run_control_release_checked": False,
        "release_ready": False,
        "queue_entry_created": False,
        "preflight_performed": False,
        "period_chain_start_allowed": False,
        "carryover_invocation_performed": False,
        "runner_invocation_performed": False,
        "writes_performed": False,
        "execution_performed": False,
        "simulation_performed": False,
        "automatic_historical_rule_selection_performed": False,
        "historical_rng_equality_claim": False,
        "historical_full_equality_claim": False,
        "next_gate": "PR139",
    }


def _result(
    request: StrategyExecutionPeriodChainRunControlRequest,
    checks: list[StrategyExecutionPeriodChainRunControlCheck],
    *,
    period_chain: dict[str, object] | None,
    record: StrategyExecutionPeriodChainStoreRecord | None,
) -> StrategyExecutionPeriodChainRunControlResult:
    return StrategyExecutionPeriodChainRunControlResult(
        request=request,
        checks=tuple(checks),
        period_chain=period_chain,
        release_ready=period_chain is not None and all(
            check.passed for check in checks
        ),
        record=record,
    )


def _period_chain_summary(
    record: StrategyExecutionPeriodChainStoreRecord,
) -> dict[str, object]:
    return {
        "chain_id": record.chain_id,
        "chain_schema_version": record.chain_schema_version,
        "content_digest": record.content_digest,
        "first_period": record.first_period,
        "last_period": record.last_period,
        "period_count": record.period_count,
        "run_index": record.run_index,
        "max_periods": record.max_periods,
        "stored_at": record.stored_at,
        "storage_status": "persisted_immutable",
    }


def _add_check(
    checks: list[StrategyExecutionPeriodChainRunControlCheck],
    code: str,
    passed: bool,
    message: str,
) -> None:
    checks.append(
        StrategyExecutionPeriodChainRunControlCheck(
            code=code,
            passed=passed,
            message=message,
        )
    )


def _required_text(value: dict[str, object], field_name: str) -> str:
    field_value = value[field_name]
    if not isinstance(field_value, str) or not field_value.strip():
        raise StrategyExecutionPeriodChainRunControlError(
            f"{field_name}_required",
            f"Run-Control-Ketteneingang verlangt Textfeld {field_name}",
        )
    return field_value.strip()


def _validate_utc_timestamp(value: str) -> None:
    if not value.endswith("Z"):
        raise StrategyExecutionPeriodChainRunControlError(
            "released_at_invalid",
            "Run-Control-Kettenfreigabe verlangt released_at als UTC-Zeit mit Z",
        )
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise StrategyExecutionPeriodChainRunControlError(
            "released_at_invalid",
            "Run-Control-Kettenfreigabe verlangt einen gueltigen UTC-Zeitpunkt",
        ) from exc
    if parsed.utcoffset() != timezone.utc.utcoffset(parsed):
        raise StrategyExecutionPeriodChainRunControlError(
            "released_at_invalid",
            "Run-Control-Kettenfreigabe verlangt UTC",
        )
