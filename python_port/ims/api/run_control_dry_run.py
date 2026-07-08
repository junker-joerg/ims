from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from ims.api.run_control_preflight import (
    WorkbenchRunControlPreflightResult,
    preflight_run_control_from_repository,
)
from ims.api.run_control_requests import WorkbenchRunControlRequest, parse_run_control_request_payload


class RunControlDryRunRepository(Protocol):
    def get_run(self, run_id: str) -> dict[str, object] | None:
        ...

    def get_scenario(self, scenario_id: str) -> dict[str, object] | None:
        ...

    def metadata_source(self) -> dict[str, object]:
        ...


@dataclass(frozen=True)
class WorkbenchRunControlDryRunResult:
    mode: str
    request: WorkbenchRunControlRequest
    preflight: WorkbenchRunControlPreflightResult
    request_accepted: bool
    preflight_passed: bool
    scenario_matches_request: bool
    issues: tuple[str, ...]
    dry_run_allowed: bool = False
    writes_enabled: bool = False
    execution_enabled: bool = False
    writes_performed: bool = False
    execution_performed: bool = False

    def to_dict(self) -> dict[str, object]:
        return {
            "status": "ok" if not self.issues else "error",
            "mode": self.mode,
            "request": self.request.to_dict(),
            "preflight": self.preflight.to_dict(),
            "request_accepted": self.request_accepted,
            "preflight_passed": self.preflight_passed,
            "scenario_matches_request": self.scenario_matches_request,
            "dry_run_allowed": self.dry_run_allowed,
            "issues": list(self.issues),
            "writes_enabled": self.writes_enabled,
            "execution_enabled": self.execution_enabled,
            "writes_performed": self.writes_performed,
            "execution_performed": self.execution_performed,
        }


def dry_run_run_control_request(
    payload: object,
    repository: RunControlDryRunRepository,
) -> WorkbenchRunControlDryRunResult:
    request = parse_run_control_request_payload(payload)
    preflight = preflight_run_control_from_repository(request.run_id, repository)
    issues = list(preflight.issues)
    scenario_matches_request = preflight.scenario_id == request.scenario_id
    if preflight.run_found and not scenario_matches_request:
        issues.append(
            "run control dry-run scenario_id does not match run metadata: "
            f"{request.scenario_id} != {preflight.scenario_id}"
        )

    return WorkbenchRunControlDryRunResult(
        mode="run_control_dry_run",
        request=request,
        preflight=preflight,
        request_accepted=True,
        preflight_passed=not preflight.issues,
        scenario_matches_request=scenario_matches_request,
        issues=tuple(issues),
    )


def dry_run_run_control_request_payload(
    payload: object,
    repository: RunControlDryRunRepository,
) -> dict[str, object]:
    return dry_run_run_control_request(payload, repository).to_dict()
