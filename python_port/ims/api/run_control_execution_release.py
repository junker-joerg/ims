from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Mapping

from ims.api.controlled_execution_adapter import (
    EXPLICIT_MULTI_PERIOD_FIXTURE_KIND,
    detect_controlled_execution_fixture_kind,
)
from ims.api.metadata import METADATA_SCHEMA_VERSION
from ims.api.metadata_import import MetadataImportError
from ims.api.run_control_adapter_start_contract import (
    build_run_control_adapter_start_contract,
)
from ims.api.run_control_preflight import WorkbenchRunControlPreflightResult
from ims.api.run_control_queue import WorkbenchRunControlQueueEntry


RUN_CONTROL_EXECUTION_RELEASE_FIELDS = frozenset(
    {
        "schema_version",
        "queue_id",
        "run_id",
        "scenario_id",
        "release_profile_id",
        "expected_adapter_mode",
        "explicit_execution_release",
        "released_by",
        "released_at",
        "release_reason",
        "carry_forward_vu_state",
        "carry_forward_vn_state",
    }
)
REQUIRED_RUN_CONTROL_EXECUTION_RELEASE_FIELDS = frozenset(
    RUN_CONTROL_EXECUTION_RELEASE_FIELDS
    - {"schema_version", "carry_forward_vu_state", "carry_forward_vn_state"}
)


@dataclass(frozen=True)
class RunControlExecutionReleaseProfile:
    profile_id: str
    run_id: str
    scenario_id: str
    fixture_path: Path
    fixture_kind: str
    adapter_mode: str
    allow_carry_forward_vu_state: bool = False
    allow_carry_forward_vn_state: bool = False

    def to_dict(self) -> dict[str, object]:
        return {
            "profile_id": self.profile_id,
            "run_id": self.run_id,
            "scenario_id": self.scenario_id,
            "fixture_path": str(self.fixture_path),
            "fixture_kind": self.fixture_kind,
            "adapter_mode": self.adapter_mode,
            "allow_carry_forward_vu_state": self.allow_carry_forward_vu_state,
            "allow_carry_forward_vn_state": self.allow_carry_forward_vn_state,
        }


@dataclass(frozen=True)
class RunControlExecutionReleaseRequest:
    queue_id: str
    run_id: str
    scenario_id: str
    release_profile_id: str
    expected_adapter_mode: str
    explicit_execution_release: bool
    released_by: str
    released_at: str
    release_reason: str
    carry_forward_vu_state: bool = False
    carry_forward_vn_state: bool = False
    schema_version: str = METADATA_SCHEMA_VERSION

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "queue_id": self.queue_id,
            "run_id": self.run_id,
            "scenario_id": self.scenario_id,
            "release_profile_id": self.release_profile_id,
            "expected_adapter_mode": self.expected_adapter_mode,
            "explicit_execution_release": self.explicit_execution_release,
            "released_by": self.released_by,
            "released_at": self.released_at,
            "release_reason": self.release_reason,
            "carry_forward_vu_state": self.carry_forward_vu_state,
            "carry_forward_vn_state": self.carry_forward_vn_state,
        }


@dataclass(frozen=True)
class RunControlExecutionReleaseCheck:
    code: str
    passed: bool
    message: str

    def to_dict(self) -> dict[str, object]:
        return {"code": self.code, "passed": self.passed, "message": self.message}


@dataclass(frozen=True)
class RunControlExecutionReleaseResult:
    request: RunControlExecutionReleaseRequest
    profile: RunControlExecutionReleaseProfile | None
    checks: tuple[RunControlExecutionReleaseCheck, ...]
    release_ready: bool
    mode: str = "run_control_execution_release_check"
    endpoint: str = "/api/run-control/adapter-release-check"
    adapter_start_endpoint: str = "/api/run-control/adapter-start"
    adapter_start_allowed: bool = False
    adapter_started: bool = False
    result_persisted: bool = False
    writes_performed: bool = False
    execution_performed: bool = False
    simulation_performed: bool = False
    automatic_historical_rule_selection_performed: bool = False
    historical_full_equality_claimed: bool = False

    @property
    def issues(self) -> tuple[str, ...]:
        return tuple(check.message for check in self.checks if not check.passed)

    def to_dict(self) -> dict[str, object]:
        return {
            "status": "ready" if self.release_ready else "blocked",
            "mode": self.mode,
            "schema_version": METADATA_SCHEMA_VERSION,
            "endpoint": self.endpoint,
            "adapter_start_endpoint": self.adapter_start_endpoint,
            "request": self.request.to_dict(),
            "profile": self.profile.to_dict() if self.profile is not None else None,
            "checks": [check.to_dict() for check in self.checks],
            "issues": list(self.issues),
            "release_ready": self.release_ready,
            "adapter_start_allowed": self.adapter_start_allowed,
            "adapter_started": self.adapter_started,
            "result_persisted": self.result_persisted,
            "writes_performed": self.writes_performed,
            "execution_performed": self.execution_performed,
            "simulation_performed": self.simulation_performed,
            "automatic_historical_rule_selection_performed": (
                self.automatic_historical_rule_selection_performed
            ),
            "historical_full_equality_claimed": self.historical_full_equality_claimed,
        }


def build_default_execution_release_profiles(
    repo_root: str | Path,
) -> dict[str, RunControlExecutionReleaseProfile]:
    root = Path(repo_root).resolve()
    profile = RunControlExecutionReleaseProfile(
        profile_id="vu14-calculated-diagnostic",
        run_id="baseline-python-tests",
        scenario_id="agrsich-reference-window",
        fixture_path=root / "tests" / "fixtures" / "calculated_vu14_explicit_slice.json",
        fixture_kind=EXPLICIT_MULTI_PERIOD_FIXTURE_KIND,
        adapter_mode="explicit_multi_period_fixture_adapter",
    )
    return {profile.profile_id: profile}


def parse_run_control_execution_release_payload(
    payload: object,
) -> RunControlExecutionReleaseRequest:
    if not isinstance(payload, dict):
        raise MetadataImportError("run control execution release payload must be a JSON object")

    unknown_fields = sorted(field for field in payload if field not in RUN_CONTROL_EXECUTION_RELEASE_FIELDS)
    if unknown_fields:
        raise MetadataImportError(
            f"run control execution release rejected fields: {', '.join(unknown_fields)}"
        )
    missing_fields = sorted(
        field for field in REQUIRED_RUN_CONTROL_EXECUTION_RELEASE_FIELDS if field not in payload
    )
    if missing_fields:
        raise MetadataImportError(
            "run control execution release missing required fields: " + ", ".join(missing_fields)
        )

    schema_version = _optional_text(payload, "schema_version", METADATA_SCHEMA_VERSION)
    if schema_version != METADATA_SCHEMA_VERSION:
        raise MetadataImportError(
            f"run control execution release schema_version must be {METADATA_SCHEMA_VERSION}: "
            f"{schema_version}"
        )

    explicit_release = _required_bool(payload, "explicit_execution_release")
    if not explicit_release:
        raise MetadataImportError(
            "run control execution release explicit_execution_release must be true"
        )

    return RunControlExecutionReleaseRequest(
        schema_version=schema_version,
        queue_id=_required_text(payload, "queue_id"),
        run_id=_required_text(payload, "run_id"),
        scenario_id=_required_text(payload, "scenario_id"),
        release_profile_id=_required_text(payload, "release_profile_id"),
        expected_adapter_mode=_required_text(payload, "expected_adapter_mode"),
        explicit_execution_release=explicit_release,
        released_by=_required_text(payload, "released_by"),
        released_at=_required_utc_timestamp(payload, "released_at"),
        release_reason=_required_text(payload, "release_reason"),
        carry_forward_vu_state=_optional_bool(payload, "carry_forward_vu_state"),
        carry_forward_vn_state=_optional_bool(payload, "carry_forward_vn_state"),
    )


def check_run_control_execution_release(
    request: RunControlExecutionReleaseRequest,
    *,
    queue_entry: WorkbenchRunControlQueueEntry | None,
    preflight: WorkbenchRunControlPreflightResult,
    profiles: Mapping[str, RunControlExecutionReleaseProfile],
    trusted_fixture_root: str | Path,
) -> RunControlExecutionReleaseResult:
    profile = profiles.get(request.release_profile_id)
    checks: list[RunControlExecutionReleaseCheck] = []
    _add_check(checks, "release_explicit", request.explicit_execution_release, "explicit release is required")
    _add_check(
        checks,
        "adapter_mode_expected",
        request.expected_adapter_mode == build_run_control_adapter_start_contract().expected_adapter_mode,
        "expected adapter mode does not match the start contract",
    )
    _add_check(checks, "queue_entry_exists", queue_entry is not None, "queue entry does not exist")
    if queue_entry is not None:
        _add_check(checks, "queue_id_matches", queue_entry.queue_id == request.queue_id, "queue id does not match")
        _add_check(checks, "queue_run_matches", queue_entry.request.run_id == request.run_id, "queue run does not match")
        _add_check(
            checks,
            "queue_scenario_matches",
            queue_entry.request.scenario_id == request.scenario_id,
            "queue scenario does not match",
        )
        _add_check(checks, "queue_status_validated", queue_entry.status == "validated", "queue status must be validated")
        _add_check(
            checks,
            "queue_execution_disabled",
            not queue_entry.request.execution_enabled,
            "queue metadata must keep execution_enabled=false",
        )
        _add_check(
            checks,
            "queue_not_executed",
            not queue_entry.execution_performed,
            "queue entry already reports execution_performed=true",
        )

    _add_check(checks, "preflight_run_found", preflight.run_found, "preflight run was not found")
    _add_check(checks, "preflight_scenario_found", preflight.scenario_found, "preflight scenario was not found")
    _add_check(checks, "preflight_run_matches", preflight.run_id == request.run_id, "preflight run does not match")
    _add_check(
        checks,
        "preflight_scenario_matches",
        preflight.scenario_id == request.scenario_id,
        "preflight scenario does not match",
    )
    _add_check(checks, "preflight_clear", not preflight.issues, "preflight contains blocking issues")

    _add_check(checks, "release_profile_exists", profile is not None, "release profile is not known locally")
    if profile is not None:
        _check_profile(request, profile, Path(trusted_fixture_root).resolve(), checks)

    release_ready = all(check.passed for check in checks)
    return RunControlExecutionReleaseResult(
        request=request,
        profile=profile,
        checks=tuple(checks),
        release_ready=release_ready,
    )


def _check_profile(
    request: RunControlExecutionReleaseRequest,
    profile: RunControlExecutionReleaseProfile,
    trusted_fixture_root: Path,
    checks: list[RunControlExecutionReleaseCheck],
) -> None:
    fixture_path = profile.fixture_path.resolve()
    _add_check(checks, "profile_run_matches", profile.run_id == request.run_id, "release profile run does not match")
    _add_check(
        checks,
        "profile_scenario_matches",
        profile.scenario_id == request.scenario_id,
        "release profile scenario does not match",
    )
    _add_check(
        checks,
        "profile_adapter_mode_matches",
        profile.adapter_mode == request.expected_adapter_mode,
        "release profile adapter mode does not match",
    )
    _add_check(
        checks,
        "fixture_path_trusted",
        fixture_path.is_relative_to(trusted_fixture_root),
        "release profile fixture is outside the trusted local fixture root",
    )
    _add_check(checks, "fixture_exists", fixture_path.is_file(), "release profile fixture does not exist")
    fixture_kind_matches = False
    if fixture_path.is_file() and fixture_path.is_relative_to(trusted_fixture_root):
        try:
            fixture_kind_matches = detect_controlled_execution_fixture_kind(fixture_path) == profile.fixture_kind
        except (OSError, ValueError):
            fixture_kind_matches = False
    _add_check(
        checks,
        "fixture_kind_matches",
        fixture_kind_matches,
        "release profile fixture kind does not match",
    )
    _add_check(
        checks,
        "vu_carryover_allowed",
        not request.carry_forward_vu_state or profile.allow_carry_forward_vu_state,
        "VU carryover is not allowed by the release profile",
    )
    _add_check(
        checks,
        "vn_carryover_allowed",
        not request.carry_forward_vn_state or profile.allow_carry_forward_vn_state,
        "VN carryover is not allowed by the release profile",
    )


def _add_check(
    checks: list[RunControlExecutionReleaseCheck],
    code: str,
    passed: bool,
    message: str,
) -> None:
    checks.append(RunControlExecutionReleaseCheck(code=code, passed=passed, message=message))


def _required_text(payload: dict[str, object], field: str) -> str:
    value = payload[field]
    if not isinstance(value, str) or not value.strip():
        raise MetadataImportError(
            f"run control execution release {field} must be a non-empty string"
        )
    return value.strip()


def _optional_text(payload: dict[str, object], field: str, default: str) -> str:
    if field not in payload:
        return default
    return _required_text(payload, field)


def _required_utc_timestamp(payload: dict[str, object], field: str) -> str:
    value = _required_text(payload, field)
    if not value.endswith("Z"):
        raise MetadataImportError(
            f"run control execution release {field} must be an ISO-8601 UTC timestamp ending in Z"
        )
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise MetadataImportError(
            f"run control execution release {field} must be a valid ISO-8601 UTC timestamp"
        ) from exc
    if parsed.utcoffset() != timezone.utc.utcoffset(parsed):
        raise MetadataImportError(
            f"run control execution release {field} must use UTC"
        )
    return value


def _required_bool(payload: dict[str, object], field: str) -> bool:
    value = payload[field]
    if not isinstance(value, bool):
        raise MetadataImportError(f"run control execution release {field} must be a boolean")
    return value


def _optional_bool(payload: dict[str, object], field: str) -> bool:
    if field not in payload:
        return False
    return _required_bool(payload, field)
