from dataclasses import dataclass, field
import argparse
import json
from pathlib import Path
from typing import Any

from ims.engine.context import SimulationContext
from ims.engine.explicit_period_plan import (
    ExplicitPeriodPlan,
    ExplicitPeriodPlanUpdate,
    build_explicit_period_fixture_from_plan,
    load_explicit_period_plan_from_mapping,
)
from ims.model.agrsich_export import compute_global_period


VU_CARRYOVER_SOURCE_FIELDS = (
    "active",
    "advertising_current_sector",
    "policyholders_current",
    "policyholders_current_sector",
    "premiums_current_sector",
    "reserves_current",
)
VN_CARRYOVER_INSURER_SOURCE_FIELDS = (
    "active",
    "advertising_current_sector",
    "claims_count_current",
    "claims_sum_current",
    "policyholders_current",
    "policyholders_current_sector",
    "premiums_current_sector",
    "reserves_current",
)
VN_CARRYOVER_POLICYHOLDER_SOURCE_FIELDS = (
    "active",
    "chosen_insurer_current",
    "chosen_insurer_sector_current",
    "claim_sum_current",
    "end_wealth_current",
    "end_wealth_sector_current",
    "insured_current",
    "insured_current_sector",
    "insurer_id",
    "paid_premium_current",
    "self_damage_current",
)


@dataclass(slots=True)
class ExplicitPeriodTransitionIssue:
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
class ExplicitPeriodTransitionSummary:
    from_period: int
    to_period: int
    from_global_period: int
    to_global_period: int
    insurer_ids: list[int]
    policyholder_ids: list[int]
    explicit_insurer_update_ids: list[int]
    explicit_policyholder_update_ids: list[int]
    explicit_input_fields: dict[str, list[str]]
    vu_carryover_planned: bool
    vn_carryover_planned: bool
    vu_carryover_candidate_insurer_ids: list[int] = field(default_factory=list)
    vn_carryover_candidate_insurer_ids: list[int] = field(default_factory=list)
    vn_carryover_candidate_policyholder_ids: list[int] = field(default_factory=list)
    carryover_source_fields: dict[str, list[str]] = field(default_factory=dict)
    vu_carryover_executed: bool = False
    vn_carryover_executed: bool = False
    writes_performed: bool = False
    execution_performed: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "from_period": self.from_period,
            "to_period": self.to_period,
            "from_global_period": self.from_global_period,
            "to_global_period": self.to_global_period,
            "insurer_ids": list(self.insurer_ids),
            "policyholder_ids": list(self.policyholder_ids),
            "explicit_insurer_update_ids": list(self.explicit_insurer_update_ids),
            "explicit_policyholder_update_ids": list(self.explicit_policyholder_update_ids),
            "explicit_input_fields": {
                key: list(value) for key, value in self.explicit_input_fields.items()
            },
            "vu_carryover_planned": self.vu_carryover_planned,
            "vn_carryover_planned": self.vn_carryover_planned,
            "vu_carryover_candidate_insurer_ids": list(
                self.vu_carryover_candidate_insurer_ids
            ),
            "vn_carryover_candidate_insurer_ids": list(
                self.vn_carryover_candidate_insurer_ids
            ),
            "vn_carryover_candidate_policyholder_ids": list(
                self.vn_carryover_candidate_policyholder_ids
            ),
            "carryover_source_fields": {
                key: list(value) for key, value in self.carryover_source_fields.items()
            },
            "vu_carryover_executed": self.vu_carryover_executed,
            "vn_carryover_executed": self.vn_carryover_executed,
            "writes_performed": self.writes_performed,
            "execution_performed": self.execution_performed,
        }


@dataclass(slots=True)
class ExplicitPeriodTransitionDiagnosticsResult:
    status: str
    mode: str
    plan_path: str
    metadata: dict[str, Any] = field(default_factory=dict)
    period_count: int = 0
    transition_count: int = 0
    global_periods: list[int] = field(default_factory=list)
    transitions: list[ExplicitPeriodTransitionSummary] = field(default_factory=list)
    issues: list[ExplicitPeriodTransitionIssue] = field(default_factory=list)
    writes_performed: bool = False
    execution_performed: bool = False
    simulation_performed: bool = False
    automatic_historical_rule_selection_performed: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "mode": self.mode,
            "plan_path": self.plan_path,
            "metadata": dict(self.metadata),
            "period_count": self.period_count,
            "transition_count": self.transition_count,
            "global_periods": list(self.global_periods),
            "transitions": [transition.to_dict() for transition in self.transitions],
            "issues": [issue.to_dict() for issue in self.issues],
            "writes_performed": self.writes_performed,
            "execution_performed": self.execution_performed,
            "simulation_performed": self.simulation_performed,
            "automatic_historical_rule_selection_performed": (
                self.automatic_historical_rule_selection_performed
            ),
        }


def _context_from_snapshot(snapshot: dict[str, Any]) -> SimulationContext:
    context = snapshot.get("context", {})
    if not isinstance(context, dict):
        raise ValueError("explicit period transition diagnostics snapshot context must be an object")
    return SimulationContext(
        period=int(context.get("period", 0)),
        logtime=int(context.get("logtime", 0)),
        max_periods=int(context.get("max_periods", 0)),
        run_index=int(context.get("run_index", 0)),
        rng_seed=int(context.get("rng_seed", 0)),
    )


def _entity_ids(snapshot: dict[str, Any], key: str) -> list[int]:
    entities = snapshot.get(key, [])
    if not isinstance(entities, list):
        raise ValueError(f"explicit period transition diagnostics {key} must be a list")
    return sorted(int(entity["entity_id"]) for entity in entities if isinstance(entity, dict))


def _update_ids(updates: list[dict]) -> list[int]:
    return sorted(int(update["entity_id"]) for update in updates if isinstance(update, dict))


def _updated_fields(updates: list[dict]) -> list[str]:
    fields: set[str] = set()
    for update in updates:
        if not isinstance(update, dict):
            continue
        fields.update(str(key) for key in update if key != "entity_id")
    return sorted(fields)


def _intersection_ids(previous_snapshot: dict[str, Any], current_snapshot: dict[str, Any], key: str) -> list[int]:
    return sorted(set(_entity_ids(previous_snapshot, key)) & set(_entity_ids(current_snapshot, key)))


def _carryover_source_fields(plan: ExplicitPeriodPlan) -> dict[str, list[str]]:
    fields: dict[str, list[str]] = {}
    if plan.carry_forward_vu_state:
        fields["vu_insurers"] = list(VU_CARRYOVER_SOURCE_FIELDS)
    if plan.carry_forward_vn_state:
        fields["vn_insurers"] = list(VN_CARRYOVER_INSURER_SOURCE_FIELDS)
        fields["vn_policyholders"] = list(VN_CARRYOVER_POLICYHOLDER_SOURCE_FIELDS)
    return fields


def _transition_summaries(
    plan: ExplicitPeriodPlan,
    snapshots: list[dict[str, Any]],
) -> tuple[list[int], list[ExplicitPeriodTransitionSummary]]:
    contexts = [_context_from_snapshot(snapshot) for snapshot in snapshots]
    global_periods = [compute_global_period(context) for context in contexts]
    transitions: list[ExplicitPeriodTransitionSummary] = []

    for index in range(1, len(snapshots)):
        previous_snapshot = snapshots[index - 1]
        current_snapshot = snapshots[index]
        previous_context = contexts[index - 1]
        current_context = contexts[index]
        update = plan.period_updates[index]
        shared_insurer_ids = _intersection_ids(previous_snapshot, current_snapshot, "insurers")
        shared_policyholder_ids = _intersection_ids(previous_snapshot, current_snapshot, "policyholders")
        transitions.append(
            ExplicitPeriodTransitionSummary(
                from_period=previous_context.period,
                to_period=current_context.period,
                from_global_period=global_periods[index - 1],
                to_global_period=global_periods[index],
                insurer_ids=sorted(
                    set(_entity_ids(previous_snapshot, "insurers"))
                    | set(_entity_ids(current_snapshot, "insurers"))
                ),
                policyholder_ids=sorted(
                    set(_entity_ids(previous_snapshot, "policyholders"))
                    | set(_entity_ids(current_snapshot, "policyholders"))
                ),
                explicit_insurer_update_ids=_update_ids(update.insurer_updates),
                explicit_policyholder_update_ids=_update_ids(update.policyholder_updates),
                explicit_input_fields={
                    "insurers": _updated_fields(update.insurer_updates),
                    "policyholders": _updated_fields(update.policyholder_updates),
                },
                vu_carryover_planned=plan.carry_forward_vu_state,
                vn_carryover_planned=plan.carry_forward_vn_state,
                vu_carryover_candidate_insurer_ids=(
                    shared_insurer_ids if plan.carry_forward_vu_state else []
                ),
                vn_carryover_candidate_insurer_ids=(
                    shared_insurer_ids if plan.carry_forward_vn_state else []
                ),
                vn_carryover_candidate_policyholder_ids=(
                    shared_policyholder_ids if plan.carry_forward_vn_state else []
                ),
                carryover_source_fields=_carryover_source_fields(plan),
            )
        )
    return global_periods, transitions


def _ordering_issues(global_periods: list[int]) -> list[ExplicitPeriodTransitionIssue]:
    issues: list[ExplicitPeriodTransitionIssue] = []
    for previous, current in zip(global_periods, global_periods[1:], strict=False):
        if current <= previous:
            issues.append(
                ExplicitPeriodTransitionIssue(
                    code="explicit_period_transition_non_increasing_global_period",
                    severity="error",
                    message="explicit period transition diagnostics requires increasing global periods",
                    from_global_period=previous,
                    to_global_period=current,
                )
            )
    return issues


def _status_from_issues(issues: list[ExplicitPeriodTransitionIssue]) -> str:
    if any(issue.severity == "error" for issue in issues):
        return "error"
    if issues:
        return "warning"
    return "ok"


def diagnose_explicit_period_transitions(path: str | Path) -> ExplicitPeriodTransitionDiagnosticsResult:
    plan_path = Path(path).expanduser().resolve()
    try:
        with plan_path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        if not isinstance(data, dict):
            raise ValueError("explicit period transition diagnostics plan must be a JSON object")
        plan = load_explicit_period_plan_from_mapping(data)
        fixture = build_explicit_period_fixture_from_plan(data)
        snapshots = fixture.get("periods", [])
        if not isinstance(snapshots, list):
            raise ValueError("explicit period transition diagnostics fixture periods must be a list")
        if any(not isinstance(snapshot, dict) for snapshot in snapshots):
            raise ValueError("explicit period transition diagnostics period snapshot must be an object")
        typed_snapshots = [snapshot for snapshot in snapshots if isinstance(snapshot, dict)]
        global_periods, transitions = _transition_summaries(plan, typed_snapshots)
        issues = _ordering_issues(global_periods)
        if not any(transition.policyholder_ids for transition in transitions):
            issues.append(
                ExplicitPeriodTransitionIssue(
                    code="explicit_period_transition_no_policyholders",
                    message="explicit period transition diagnostics found no VN policyholders in this fixture",
                )
            )
        return ExplicitPeriodTransitionDiagnosticsResult(
            status=_status_from_issues(issues),
            mode="explicit_period_transition_diagnostics",
            plan_path=str(plan_path),
            metadata=dict(plan.metadata),
            period_count=len(typed_snapshots),
            transition_count=len(transitions),
            global_periods=global_periods,
            transitions=transitions,
            issues=issues,
        )
    except Exception as exc:
        return ExplicitPeriodTransitionDiagnosticsResult(
            status="error",
            mode="explicit_period_transition_diagnostics",
            plan_path=str(plan_path),
            issues=[
                ExplicitPeriodTransitionIssue(
                    code="explicit_period_transition_diagnostics_failed",
                    severity="error",
                    message=str(exc),
                )
            ],
        )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Inspect transitions in an explicit IMS period plan without execution."
    )
    parser.add_argument("plan_path", help="Path to an explicit period plan JSON file.")
    args = parser.parse_args(argv)

    result = diagnose_explicit_period_transitions(args.plan_path)
    print(json.dumps(result.to_dict(), indent=2, sort_keys=True))
    return 2 if result.status == "error" else 0


if __name__ == "__main__":
    raise SystemExit(main())
