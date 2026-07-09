from dataclasses import dataclass, field
import argparse
import json
from pathlib import Path
from typing import Any

from ims.engine.explicit_period_plan import build_explicit_period_fixture_from_plan
from ims.engine.explicit_period_transition_diagnostics import (
    ExplicitPeriodTransitionIssue,
    VU_CARRYOVER_SOURCE_FIELDS,
    VN_CARRYOVER_INSURER_SOURCE_FIELDS,
    VN_CARRYOVER_POLICYHOLDER_SOURCE_FIELDS,
    diagnose_explicit_period_transitions,
)
from ims.engine.vn_rule_runner import apply_vn_state_carryover
from ims.engine.vu_rule_runner import apply_vu_foreign_info_carryover
from ims.io.scenario_loader import LoadedScenario, load_scenario_from_mapping
from ims.model.agrsich_export import compute_global_period
from ims.model.entities import Insurer, Policyholder


@dataclass(slots=True)
class FixtureVUCarryoverSource:
    """Explizite Fixture-Quelle fuer einen VU-Carryover-Probe."""

    context_period: int
    context_global_period: int
    insurers: list[Insurer]


@dataclass(slots=True)
class FixtureVNCarryoverSource:
    """Explizite Fixture-Quelle fuer einen VN-Carryover-Probe."""

    period: int
    global_period: int
    insurers: list[Insurer]
    policyholders: list[Policyholder]


@dataclass(slots=True)
class ExplicitTransitionCarryoverProbeIssue:
    code: str
    message: str
    severity: str = "warning"
    from_global_period: int | None = None
    to_global_period: int | None = None

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "code": self.code,
            "severity": self.severity,
            "message": self.message,
        }
        if self.from_global_period is not None:
            payload["from_global_period"] = self.from_global_period
        if self.to_global_period is not None:
            payload["to_global_period"] = self.to_global_period
        return payload


@dataclass(slots=True)
class ExplicitTransitionCarryoverProbeTransition:
    from_period: int
    to_period: int
    from_global_period: int
    to_global_period: int
    vu_carryover_requested: bool
    vn_carryover_requested: bool
    vu_carryover_planned: bool
    vn_carryover_planned: bool
    vu_carryover_executed: bool = False
    vn_carryover_executed: bool = False
    carried_insurer_ids: list[int] = field(default_factory=list)
    carried_policyholder_ids: list[int] = field(default_factory=list)
    diagnostic_candidate_ids_match: bool = True
    previous_result_source: str = "none"
    source_fields: dict[str, list[str]] = field(default_factory=dict)
    carried_insurer_state: dict[str, dict[str, Any]] = field(default_factory=dict)
    carried_policyholder_state: dict[str, dict[str, Any]] = field(default_factory=dict)
    issues: list[ExplicitTransitionCarryoverProbeIssue] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "from_period": self.from_period,
            "to_period": self.to_period,
            "from_global_period": self.from_global_period,
            "to_global_period": self.to_global_period,
            "vu_carryover_requested": self.vu_carryover_requested,
            "vn_carryover_requested": self.vn_carryover_requested,
            "vu_carryover_planned": self.vu_carryover_planned,
            "vn_carryover_planned": self.vn_carryover_planned,
            "vu_carryover_executed": self.vu_carryover_executed,
            "vn_carryover_executed": self.vn_carryover_executed,
            "carried_insurer_ids": list(self.carried_insurer_ids),
            "carried_policyholder_ids": list(self.carried_policyholder_ids),
            "diagnostic_candidate_ids_match": self.diagnostic_candidate_ids_match,
            "previous_result_source": self.previous_result_source,
            "source_fields": {
                key: list(value) for key, value in self.source_fields.items()
            },
            "carried_insurer_state": {
                key: dict(value) for key, value in self.carried_insurer_state.items()
            },
            "carried_policyholder_state": {
                key: dict(value) for key, value in self.carried_policyholder_state.items()
            },
            "issues": [issue.to_dict() for issue in self.issues],
        }


@dataclass(slots=True)
class ExplicitTransitionCarryoverProbeResult:
    status: str
    mode: str
    plan_path: str
    transition_count: int = 0
    vu_carryover_requested: bool = False
    vn_carryover_requested: bool = False
    in_memory_carryover_performed: bool = False
    transitions: list[ExplicitTransitionCarryoverProbeTransition] = field(default_factory=list)
    issues: list[ExplicitTransitionCarryoverProbeIssue] = field(default_factory=list)
    writes_performed: bool = False
    execution_performed: bool = False
    simulation_performed: bool = False
    automatic_historical_rule_selection_performed: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "mode": self.mode,
            "plan_path": self.plan_path,
            "transition_count": self.transition_count,
            "vu_carryover_requested": self.vu_carryover_requested,
            "vn_carryover_requested": self.vn_carryover_requested,
            "in_memory_carryover_performed": self.in_memory_carryover_performed,
            "transitions": [transition.to_dict() for transition in self.transitions],
            "issues": [issue.to_dict() for issue in self.issues],
            "writes_performed": self.writes_performed,
            "execution_performed": self.execution_performed,
            "simulation_performed": self.simulation_performed,
            "automatic_historical_rule_selection_performed": (
                self.automatic_historical_rule_selection_performed
            ),
        }


def _issue_from_diagnostic(issue: ExplicitPeriodTransitionIssue) -> ExplicitTransitionCarryoverProbeIssue:
    return ExplicitTransitionCarryoverProbeIssue(
        code=issue.code,
        message=issue.message,
        severity=issue.severity,
        from_global_period=issue.from_global_period,
        to_global_period=issue.to_global_period,
    )


def _source_fields(*, include_vu: bool, include_vn: bool) -> dict[str, list[str]]:
    fields: dict[str, list[str]] = {}
    if include_vu:
        fields["vu_insurers"] = list(VU_CARRYOVER_SOURCE_FIELDS)
    if include_vn:
        fields["vn_insurers"] = list(VN_CARRYOVER_INSURER_SOURCE_FIELDS)
        fields["vn_policyholders"] = list(VN_CARRYOVER_POLICYHOLDER_SOURCE_FIELDS)
    return fields


def _loaded_periods_from_plan(plan_path: Path) -> list[LoadedScenario]:
    with plan_path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    fixture = build_explicit_period_fixture_from_plan(data)
    periods = fixture.get("periods", [])
    if not isinstance(periods, list):
        raise ValueError("explicit transition carryover probe fixture periods must be a list")
    return [load_scenario_from_mapping(period) for period in periods if isinstance(period, dict)]


def _insurer_state_preview(insurer: Insurer) -> dict[str, Any]:
    return {
        "active_prev": insurer.active_prev,
        "premiums_prev": insurer.premiums_prev,
        "premiums_current": insurer.premiums_current,
        "premiums_current_sector": list(insurer.premiums_current_sector),
        "policyholders_current": insurer.policyholders_current,
        "policyholders_current_sector": list(insurer.policyholders_current_sector),
        "reserves_current": list(insurer.reserves_current),
    }


def _policyholder_state_preview(policyholder: Policyholder) -> dict[str, Any]:
    return {
        "active_prev": policyholder.active_prev,
        "insurer_id": policyholder.insurer_id,
        "chosen_insurer_current": policyholder.chosen_insurer_current,
        "insured_prev": policyholder.insured_prev,
        "insured_current": policyholder.insured_current,
        "insured_current_sector": list(policyholder.insured_current_sector),
        "end_wealth_current": policyholder.end_wealth_current,
    }


def _status_from_issues(issues: list[ExplicitTransitionCarryoverProbeIssue]) -> str:
    if any(issue.severity == "error" for issue in issues):
        return "error"
    if issues:
        return "warning"
    return "ok"


def probe_explicit_transition_carryover(
    path: str | Path,
    *,
    apply_vu: bool = False,
    apply_vn: bool = False,
) -> ExplicitTransitionCarryoverProbeResult:
    plan_path = Path(path).expanduser().resolve()
    diagnostics = diagnose_explicit_period_transitions(plan_path)
    issues = [_issue_from_diagnostic(issue) for issue in diagnostics.issues]
    if diagnostics.status == "error":
        return ExplicitTransitionCarryoverProbeResult(
            status="error",
            mode="explicit_transition_carryover_probe",
            plan_path=str(plan_path),
            vu_carryover_requested=apply_vu,
            vn_carryover_requested=apply_vn,
            issues=issues,
        )

    try:
        loaded_periods = _loaded_periods_from_plan(plan_path)
    except Exception as exc:
        return ExplicitTransitionCarryoverProbeResult(
            status="error",
            mode="explicit_transition_carryover_probe",
            plan_path=str(plan_path),
            vu_carryover_requested=apply_vu,
            vn_carryover_requested=apply_vn,
            issues=[
                *issues,
                ExplicitTransitionCarryoverProbeIssue(
                    code="explicit_transition_carryover_probe_failed",
                    severity="error",
                    message=str(exc),
                ),
            ],
        )

    probe_transitions: list[ExplicitTransitionCarryoverProbeTransition] = []
    for index, diagnostic_transition in enumerate(diagnostics.transitions):
        previous_loaded = loaded_periods[index]
        current_loaded = loaded_periods[index + 1]
        transition_issues: list[ExplicitTransitionCarryoverProbeIssue] = []
        carried_insurer_ids: set[int] = set()
        carried_policyholder_ids: set[int] = set()
        vu_executed = False
        vn_executed = False
        previous_result_source = "none"

        if apply_vu:
            if not diagnostic_transition.vu_carryover_planned:
                transition_issues.append(
                    ExplicitTransitionCarryoverProbeIssue(
                        code="explicit_transition_carryover_vu_not_planned",
                        message="VU carryover probe was requested but the plan does not enable VU carryover.",
                        from_global_period=diagnostic_transition.from_global_period,
                        to_global_period=diagnostic_transition.to_global_period,
                    )
                )
            else:
                carryover = apply_vu_foreign_info_carryover(
                    FixtureVUCarryoverSource(
                        context_period=previous_loaded.context.period,
                        context_global_period=compute_global_period(previous_loaded.context),
                        insurers=previous_loaded.insurers,
                    ),
                    current_loaded,
                )
                if carryover is not None:
                    vu_executed = True
                    previous_result_source = "explicit_fixture_snapshot"
                    carried_insurer_ids.update(carryover.insurer_ids)

        if apply_vn:
            if not diagnostic_transition.vn_carryover_planned:
                transition_issues.append(
                    ExplicitTransitionCarryoverProbeIssue(
                        code="explicit_transition_carryover_vn_not_planned",
                        message="VN carryover probe was requested but the plan does not enable VN carryover.",
                        from_global_period=diagnostic_transition.from_global_period,
                        to_global_period=diagnostic_transition.to_global_period,
                    )
                )
            else:
                carryover = apply_vn_state_carryover(
                    FixtureVNCarryoverSource(
                        period=previous_loaded.context.period,
                        global_period=compute_global_period(previous_loaded.context),
                        insurers=previous_loaded.insurers,
                        policyholders=previous_loaded.policyholders,
                    ),
                    current_loaded,
                )
                if carryover is not None:
                    vn_executed = True
                    previous_result_source = "explicit_fixture_snapshot"
                    carried_insurer_ids.update(carryover.insurer_ids)
                    carried_policyholder_ids.update(carryover.policyholder_ids)

        carried_insurer_ids_list = sorted(carried_insurer_ids)
        carried_policyholder_ids_list = sorted(carried_policyholder_ids)
        expected_insurer_ids = set()
        if vu_executed:
            expected_insurer_ids.update(diagnostic_transition.vu_carryover_candidate_insurer_ids)
        if vn_executed:
            expected_insurer_ids.update(diagnostic_transition.vn_carryover_candidate_insurer_ids)
        expected_policyholder_ids = (
            set(diagnostic_transition.vn_carryover_candidate_policyholder_ids)
            if vn_executed
            else set()
        )
        candidate_ids_match = (
            set(carried_insurer_ids_list) == expected_insurer_ids
            and set(carried_policyholder_ids_list) == expected_policyholder_ids
        )
        if (vu_executed or vn_executed) and not candidate_ids_match:
            transition_issues.append(
                ExplicitTransitionCarryoverProbeIssue(
                    code="explicit_transition_carryover_candidate_mismatch",
                    severity="error",
                    message="Carryover probe result differs from transition diagnostic candidate ids.",
                    from_global_period=diagnostic_transition.from_global_period,
                    to_global_period=diagnostic_transition.to_global_period,
                )
            )

        current_insurers = {insurer.entity_id: insurer for insurer in current_loaded.insurers}
        current_policyholders = {
            policyholder.entity_id: policyholder for policyholder in current_loaded.policyholders
        }
        probe_transitions.append(
            ExplicitTransitionCarryoverProbeTransition(
                from_period=diagnostic_transition.from_period,
                to_period=diagnostic_transition.to_period,
                from_global_period=diagnostic_transition.from_global_period,
                to_global_period=diagnostic_transition.to_global_period,
                vu_carryover_requested=apply_vu,
                vn_carryover_requested=apply_vn,
                vu_carryover_planned=diagnostic_transition.vu_carryover_planned,
                vn_carryover_planned=diagnostic_transition.vn_carryover_planned,
                vu_carryover_executed=vu_executed,
                vn_carryover_executed=vn_executed,
                carried_insurer_ids=carried_insurer_ids_list,
                carried_policyholder_ids=carried_policyholder_ids_list,
                diagnostic_candidate_ids_match=candidate_ids_match,
                previous_result_source=previous_result_source,
                source_fields=_source_fields(include_vu=vu_executed, include_vn=vn_executed),
                carried_insurer_state={
                    str(entity_id): _insurer_state_preview(current_insurers[entity_id])
                    for entity_id in carried_insurer_ids_list
                    if entity_id in current_insurers
                },
                carried_policyholder_state={
                    str(entity_id): _policyholder_state_preview(current_policyholders[entity_id])
                    for entity_id in carried_policyholder_ids_list
                    if entity_id in current_policyholders
                },
                issues=transition_issues,
            )
        )
        issues.extend(transition_issues)

    return ExplicitTransitionCarryoverProbeResult(
        status=_status_from_issues(issues),
        mode="explicit_transition_carryover_probe",
        plan_path=str(plan_path),
        transition_count=len(probe_transitions),
        vu_carryover_requested=apply_vu,
        vn_carryover_requested=apply_vn,
        in_memory_carryover_performed=any(
            transition.vu_carryover_executed or transition.vn_carryover_executed
            for transition in probe_transitions
        ),
        transitions=probe_transitions,
        issues=issues,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Probe explicit IMS transition carryover in memory without simulation."
    )
    parser.add_argument("plan_path", help="Path to an explicit period plan JSON file.")
    parser.add_argument("--apply-vu", action="store_true", help="Apply planned VU carryover in memory.")
    parser.add_argument("--apply-vn", action="store_true", help="Apply planned VN carryover in memory.")
    args = parser.parse_args(argv)

    result = probe_explicit_transition_carryover(
        args.plan_path,
        apply_vu=args.apply_vu,
        apply_vn=args.apply_vn,
    )
    print(json.dumps(result.to_dict(), indent=2, sort_keys=True))
    return 2 if result.status == "error" else 0


if __name__ == "__main__":
    raise SystemExit(main())
