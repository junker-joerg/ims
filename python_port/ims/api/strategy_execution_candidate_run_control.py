from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import re

from ims.api.strategy_execution_candidate_store import (
    StrategyExecutionCandidateStoreError,
    StrategyExecutionCandidateStoreRecord,
    get_strategy_execution_candidate,
)
from ims.strategies.execution_candidate_build import (
    strategy_execution_candidate_id_from_digest,
)
from ims.strategies.execution_candidate_contract import (
    STRATEGY_EXECUTION_CANDIDATE_VERSION,
)


STRATEGY_EXECUTION_CANDIDATE_RUN_CONTROL_CONTRACT_VERSION = (
    "ims.strategy-execution-candidate-run-control-contract.v1"
)
STRATEGY_EXECUTION_CANDIDATE_RUN_CONTROL_REQUEST_VERSION = (
    "ims.strategy-execution-candidate-run-control-request.v1"
)
STRATEGY_EXECUTION_CANDIDATE_RUN_CONTROL_CHECK_VERSION = (
    "ims.strategy-execution-candidate-run-control-check.v1"
)

_REQUEST_FIELDS = frozenset(
    {
        "schema_version",
        "candidate_id",
        "expected_content_digest",
        "idempotency_key",
        "explicit_run_control_release",
        "released_by",
        "released_at",
        "release_reason",
    }
)
_DIGEST_PATTERN = re.compile(r"sha256:[0-9a-f]{64}\Z")
_CANDIDATE_ID_PATTERN = re.compile(r"strategy-candidate-[0-9a-f]{24}\Z")
_CLOSED_CANDIDATE_BOUNDARIES = (
    "run_control_enabled",
    "runner_enabled",
    "carryover_enabled",
    "output_files_enabled",
    "legacy_comparison_enabled",
)


class StrategyExecutionCandidateRunControlError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


@dataclass(frozen=True, slots=True)
class StrategyExecutionCandidateRunControlRequest:
    candidate_id: str
    expected_content_digest: str
    idempotency_key: str
    explicit_run_control_release: bool
    released_by: str
    released_at: str
    release_reason: str
    schema_version: str = STRATEGY_EXECUTION_CANDIDATE_RUN_CONTROL_REQUEST_VERSION

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "candidate_id": self.candidate_id,
            "expected_content_digest": self.expected_content_digest,
            "idempotency_key": self.idempotency_key,
            "explicit_run_control_release": self.explicit_run_control_release,
            "released_by": self.released_by,
            "released_at": self.released_at,
            "release_reason": self.release_reason,
        }


@dataclass(frozen=True, slots=True)
class StrategyExecutionCandidateRunControlCheck:
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
class StrategyExecutionCandidateRunControlResult:
    request: StrategyExecutionCandidateRunControlRequest
    checks: tuple[StrategyExecutionCandidateRunControlCheck, ...]
    candidate: dict[str, object] | None
    release_ready: bool

    @property
    def issues(self) -> tuple[dict[str, str], ...]:
        return tuple(
            {"code": check.code, "message": check.message}
            for check in self.checks
            if not check.passed
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": STRATEGY_EXECUTION_CANDIDATE_RUN_CONTROL_CHECK_VERSION,
            "request_schema_version": (
                STRATEGY_EXECUTION_CANDIDATE_RUN_CONTROL_REQUEST_VERSION
            ),
            "candidate_schema_version": STRATEGY_EXECUTION_CANDIDATE_VERSION,
            "mode": "strategy_execution_candidate_run_control_release_check",
            "status": "ready" if self.release_ready else "blocked",
            "request": self.request.to_dict(),
            "candidate": dict(self.candidate) if self.candidate is not None else None,
            "checks": [check.to_dict() for check in self.checks],
            "issue_count": len(self.issues),
            "issues": [dict(issue) for issue in self.issues],
            "candidate_resolved": self.candidate is not None,
            "candidate_digest_reverified": self.candidate is not None,
            "run_control_release_checked": True,
            "release_ready": self.release_ready,
            "queue_entry_created": False,
            "preflight_performed": False,
            "adapter_start_allowed": False,
            "adapter_started": False,
            "runner_invocation_performed": False,
            "writes_performed": False,
            "execution_performed": False,
            "simulation_performed": False,
            "automatic_historical_rule_selection_performed": False,
            "historical_rng_equality_claim": False,
            "historical_full_equality_claim": False,
            "next_gate": "PR130",
        }


def parse_strategy_execution_candidate_run_control_request(
    value: object,
) -> StrategyExecutionCandidateRunControlRequest:
    if not isinstance(value, dict):
        raise StrategyExecutionCandidateRunControlError(
            "request_object_required",
            "Run-Control-Kandidateneingang muss ein JSON-Objekt sein",
        )
    unknown_fields = sorted(field for field in value if field not in _REQUEST_FIELDS)
    if unknown_fields:
        raise StrategyExecutionCandidateRunControlError(
            "unknown_request_fields",
            "Run-Control-Kandidateneingang enthaelt unbekannte Felder: "
            + ", ".join(unknown_fields),
        )
    missing_fields = sorted(field for field in _REQUEST_FIELDS if field not in value)
    if missing_fields:
        raise StrategyExecutionCandidateRunControlError(
            "missing_request_fields",
            "Run-Control-Kandidateneingang vermisst Pflichtfelder: "
            + ", ".join(missing_fields),
        )

    schema_version = _required_text(value, "schema_version")
    if schema_version != STRATEGY_EXECUTION_CANDIDATE_RUN_CONTROL_REQUEST_VERSION:
        raise StrategyExecutionCandidateRunControlError(
            "unsupported_schema_version",
            "Run-Control-Kandidateneingang erwartet schema_version "
            f"{STRATEGY_EXECUTION_CANDIDATE_RUN_CONTROL_REQUEST_VERSION}",
        )
    candidate_id = _required_text(value, "candidate_id")
    if _CANDIDATE_ID_PATTERN.fullmatch(candidate_id) is None:
        raise StrategyExecutionCandidateRunControlError(
            "candidate_id_invalid",
            "Kandidaten-ID muss dem gespeicherten strategy-candidate-Format entsprechen",
        )
    content_digest = _required_text(value, "expected_content_digest")
    if _DIGEST_PATTERN.fullmatch(content_digest) is None:
        raise StrategyExecutionCandidateRunControlError(
            "content_digest_invalid",
            "Erwarteter Kandidatendigest muss ein kleingeschriebener SHA-256-Digest sein",
        )
    explicit_release = value["explicit_run_control_release"]
    if not isinstance(explicit_release, bool) or not explicit_release:
        raise StrategyExecutionCandidateRunControlError(
            "run_control_release_required",
            "Run-Control-Kandidatenfreigabe muss explizit true sein",
        )
    released_at = _required_text(value, "released_at")
    _validate_utc_timestamp(released_at)
    return StrategyExecutionCandidateRunControlRequest(
        schema_version=schema_version,
        candidate_id=candidate_id,
        expected_content_digest=content_digest,
        idempotency_key=_required_text(value, "idempotency_key"),
        explicit_run_control_release=explicit_release,
        released_by=_required_text(value, "released_by"),
        released_at=released_at,
        release_reason=_required_text(value, "release_reason"),
    )


def check_strategy_execution_candidate_run_control_release(
    request: StrategyExecutionCandidateRunControlRequest,
    *,
    db_path: Path | str,
) -> StrategyExecutionCandidateRunControlResult:
    checks: list[StrategyExecutionCandidateRunControlCheck] = []
    _add_check(
        checks,
        "run_control_release_explicit",
        request.explicit_run_control_release,
        "Explizite Run-Control-Kandidatenfreigabe fehlt",
    )
    identity_matches = request.candidate_id == strategy_execution_candidate_id_from_digest(
        request.expected_content_digest
    )
    _add_check(
        checks,
        "request_identity_consistent",
        identity_matches,
        "Kandidaten-ID passt nicht zum erwarteten Digest",
    )
    if not identity_matches:
        return _result(request, checks, candidate=None)

    try:
        stored = get_strategy_execution_candidate(
            request.candidate_id,
            db_path=db_path,
        )
    except StrategyExecutionCandidateStoreError as exc:
        _add_check(checks, exc.code, False, str(exc))
        return _result(request, checks, candidate=None)

    record = stored.record
    _add_check(
        checks,
        "candidate_resolved",
        True,
        "Gespeicherter Kandidat konnte nicht aufgeloest werden",
    )
    _add_check(
        checks,
        "candidate_id_verified",
        record.candidate_id == request.candidate_id,
        "Gespeicherte Kandidaten-ID weicht vom Request ab",
    )
    _add_check(
        checks,
        "candidate_digest_reverified",
        stored.post_storage_digest_verified,
        "Gespeicherter Kandidatendigest konnte nicht erneut bestaetigt werden",
    )
    _add_check(
        checks,
        "expected_digest_matches",
        record.content_digest == request.expected_content_digest,
        "Gespeicherter Kandidatendigest weicht vom erwarteten Digest ab",
    )
    boundaries = record.candidate.get("execution_boundaries")
    boundaries_closed = isinstance(boundaries, dict) and all(
        boundaries.get(field) is False for field in _CLOSED_CANDIDATE_BOUNDARIES
    )
    _add_check(
        checks,
        "candidate_execution_boundaries_closed",
        boundaries_closed,
        "Gespeicherter Kandidat hat unerwartet offene Ausfuehrungsgrenzen",
    )
    return _result(request, checks, candidate=_candidate_summary(record))


def strategy_execution_candidate_run_control_contract_payload() -> dict[str, object]:
    return {
        "schema_version": STRATEGY_EXECUTION_CANDIDATE_RUN_CONTROL_CONTRACT_VERSION,
        "request_schema_version": (
            STRATEGY_EXECUTION_CANDIDATE_RUN_CONTROL_REQUEST_VERSION
        ),
        "check_schema_version": STRATEGY_EXECUTION_CANDIDATE_RUN_CONTROL_CHECK_VERSION,
        "candidate_schema_version": STRATEGY_EXECUTION_CANDIDATE_VERSION,
        "mode": "strategy_execution_candidate_run_control_contract_read_only",
        "contract_endpoint": "/api/run-control/strategy-candidate-contract",
        "release_check_endpoint": (
            "/api/run-control/strategy-candidate-release-check"
        ),
        "accepted_request_fields": sorted(_REQUEST_FIELDS),
        "required_request_fields": sorted(_REQUEST_FIELDS),
        "authoritative_identity_fields": [
            "candidate_id",
            "expected_content_digest",
        ],
        "audit_fields": [
            "idempotency_key",
            "released_by",
            "released_at",
            "release_reason",
        ],
        "forbidden_request_fields": [
            "candidate",
            "candidate_input",
            "metadata_db",
            "db_path",
            "queue_id",
            "run_id",
            "scenario_id",
            "fixture_path",
            "output_dir",
            "execution_enabled",
        ],
        "release_ready_meaning": (
            "candidate_identity_storage_integrity_and_closed_boundaries_verified"
        ),
        "explicit_run_control_release_required": True,
        "candidate_resolution_enabled": True,
        "candidate_digest_reverification_enabled": True,
        "run_control_release_check_enabled": True,
        "queue_write_enabled": False,
        "preflight_enabled": False,
        "adapter_start_allowed": False,
        "runner_enabled": False,
        "writes_enabled": False,
        "execution_enabled": False,
        "simulation_performed": False,
        "historical_rng_equality_claim": False,
        "historical_full_equality_claim": False,
        "next_gate": "PR130",
    }


def strategy_execution_candidate_run_control_error_payload(
    code: str,
    message: str,
) -> dict[str, object]:
    return {
        "schema_version": STRATEGY_EXECUTION_CANDIDATE_RUN_CONTROL_CHECK_VERSION,
        "request_schema_version": (
            STRATEGY_EXECUTION_CANDIDATE_RUN_CONTROL_REQUEST_VERSION
        ),
        "candidate_schema_version": STRATEGY_EXECUTION_CANDIDATE_VERSION,
        "mode": "strategy_execution_candidate_run_control_release_check",
        "status": "error",
        "candidate": None,
        "checks": [],
        "issue_count": 1,
        "issues": [{"code": code, "message": message}],
        "candidate_resolved": False,
        "candidate_digest_reverified": False,
        "run_control_release_checked": False,
        "release_ready": False,
        "queue_entry_created": False,
        "preflight_performed": False,
        "adapter_start_allowed": False,
        "adapter_started": False,
        "runner_invocation_performed": False,
        "writes_performed": False,
        "execution_performed": False,
        "simulation_performed": False,
        "automatic_historical_rule_selection_performed": False,
        "historical_rng_equality_claim": False,
        "historical_full_equality_claim": False,
        "next_gate": "PR130",
    }


def _result(
    request: StrategyExecutionCandidateRunControlRequest,
    checks: list[StrategyExecutionCandidateRunControlCheck],
    *,
    candidate: dict[str, object] | None,
) -> StrategyExecutionCandidateRunControlResult:
    return StrategyExecutionCandidateRunControlResult(
        request=request,
        checks=tuple(checks),
        candidate=candidate,
        release_ready=candidate is not None and all(check.passed for check in checks),
    )


def _candidate_summary(
    record: StrategyExecutionCandidateStoreRecord,
) -> dict[str, object]:
    return {
        "candidate_id": record.candidate_id,
        "candidate_schema_version": record.candidate_schema_version,
        "draft_id": record.draft_id,
        "period": record.period,
        "profile_id": record.profile_id,
        "profile_content_digest": record.profile_content_digest,
        "content_digest": record.content_digest,
        "stored_at": record.stored_at,
        "storage_status": "persisted_immutable",
    }


def _add_check(
    checks: list[StrategyExecutionCandidateRunControlCheck],
    code: str,
    passed: bool,
    message: str,
) -> None:
    checks.append(
        StrategyExecutionCandidateRunControlCheck(
            code=code,
            passed=passed,
            message=message,
        )
    )


def _required_text(value: dict[str, object], field_name: str) -> str:
    field_value = value[field_name]
    if not isinstance(field_value, str) or not field_value.strip():
        raise StrategyExecutionCandidateRunControlError(
            f"{field_name}_required",
            f"Run-Control-Kandidateneingang verlangt Textfeld {field_name}",
        )
    return field_value.strip()


def _validate_utc_timestamp(value: str) -> None:
    if not value.endswith("Z"):
        raise StrategyExecutionCandidateRunControlError(
            "released_at_invalid",
            "Run-Control-Kandidatenfreigabe verlangt released_at als UTC-Zeit mit Z",
        )
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise StrategyExecutionCandidateRunControlError(
            "released_at_invalid",
            "Run-Control-Kandidatenfreigabe verlangt einen gueltigen UTC-Zeitpunkt",
        ) from exc
    if parsed.utcoffset() != timezone.utc.utcoffset(parsed):
        raise StrategyExecutionCandidateRunControlError(
            "released_at_invalid",
            "Run-Control-Kandidatenfreigabe verlangt UTC",
        )
