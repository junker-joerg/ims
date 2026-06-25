from dataclasses import dataclass, field
import argparse
import json
from pathlib import Path
from typing import Any

from ims.engine.context import SimulationContext
from ims.engine.explicit_period_plan import (
    ExplicitPeriodPlan,
    build_explicit_period_fixture_from_plan,
    explicit_period_snapshot_keys,
    load_explicit_period_plan_from_mapping,
)
from ims.io.scenario_loader import load_scenario_from_mapping
from ims.model.agrsich_export import compute_global_period


_SNAPSHOT_KEYS = explicit_period_snapshot_keys()
VU_SNAPSHOT_KEYS = tuple(key for key in _SNAPSHOT_KEYS if key.startswith("vu_"))
VN_INSURANCE_SNAPSHOT_KEY = "vn_insurance_rule_snapshots"
VN_SETTLEMENT_SNAPSHOT_KEY = "vn_settlement_snapshots"
VN_DAMAGE_SETTLEMENT_SNAPSHOT_KEY = "vn_damage_settlement_snapshots"


@dataclass(slots=True)
class ExplicitPeriodDiagnosticIssue:
    code: str
    message: str
    severity: str = "warning"
    period: int | None = None
    global_period: int | None = None

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "code": self.code,
            "severity": self.severity,
            "message": self.message,
        }
        if self.period is not None:
            payload["period"] = self.period
        if self.global_period is not None:
            payload["global_period"] = self.global_period
        return payload


@dataclass(slots=True)
class ExplicitPeriodActionSummary:
    period: int
    global_period: int
    logtime: int
    max_periods: int
    run_index: int
    rng_seed: int
    insurer_update_count: int
    policyholder_update_count: int
    snapshot_families: list[str]
    vu_rule_application_count: int
    vn_insurance_rule_application_count: int
    vn_settlement_application_count: int
    vn_damage_settlement_application_count: int
    execution_allowed: bool = False
    writes_performed: bool = False
    execution_performed: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "period": self.period,
            "global_period": self.global_period,
            "logtime": self.logtime,
            "max_periods": self.max_periods,
            "run_index": self.run_index,
            "rng_seed": self.rng_seed,
            "insurer_update_count": self.insurer_update_count,
            "policyholder_update_count": self.policyholder_update_count,
            "snapshot_families": list(self.snapshot_families),
            "vu_rule_application_count": self.vu_rule_application_count,
            "vn_insurance_rule_application_count": self.vn_insurance_rule_application_count,
            "vn_settlement_application_count": self.vn_settlement_application_count,
            "vn_damage_settlement_application_count": self.vn_damage_settlement_application_count,
            "execution_allowed": self.execution_allowed,
            "writes_performed": self.writes_performed,
            "execution_performed": self.execution_performed,
        }


@dataclass(slots=True)
class ExplicitPeriodDiagnosticsResult:
    status: str
    mode: str
    plan_path: str
    metadata: dict[str, Any] = field(default_factory=dict)
    period_count: int = 0
    periods: list[ExplicitPeriodActionSummary] = field(default_factory=list)
    global_periods: list[int] = field(default_factory=list)
    carry_forward_vu_state: bool = False
    carry_forward_vn_state: bool = False
    snapshot_families: list[str] = field(default_factory=list)
    supported_snapshot_families: list[str] = field(default_factory=lambda: list(_SNAPSHOT_KEYS))
    legacy_targets: list[dict[str, Any]] = field(default_factory=list)
    issues: list[ExplicitPeriodDiagnosticIssue] = field(default_factory=list)
    writes_performed: bool = False
    execution_performed: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "mode": self.mode,
            "plan_path": self.plan_path,
            "metadata": dict(self.metadata),
            "period_count": self.period_count,
            "periods": [period.to_dict() for period in self.periods],
            "global_periods": list(self.global_periods),
            "carry_forward_vu_state": self.carry_forward_vu_state,
            "carry_forward_vn_state": self.carry_forward_vn_state,
            "snapshot_families": list(self.snapshot_families),
            "supported_snapshot_families": list(self.supported_snapshot_families),
            "legacy_targets": list(self.legacy_targets),
            "issues": [issue.to_dict() for issue in self.issues],
            "writes_performed": self.writes_performed,
            "execution_performed": self.execution_performed,
        }


def _context_from_period_snapshot(snapshot: dict[str, Any]) -> SimulationContext:
    context = snapshot.get("context", {})
    if not isinstance(context, dict):
        raise ValueError("explicit period diagnostics snapshot context must be an object")
    return SimulationContext(
        period=int(context.get("period", 0)),
        logtime=int(context.get("logtime", 0)),
        max_periods=int(context.get("max_periods", 0)),
        run_index=int(context.get("run_index", 0)),
        rng_seed=int(context.get("rng_seed", 0)),
    )


def _snapshot_families(snapshot: dict[str, Any]) -> list[str]:
    return [key for key in _SNAPSHOT_KEYS if isinstance(snapshot.get(key), list) and snapshot[key]]


def _snapshot_count(snapshot: dict[str, Any], key: str) -> int:
    value = snapshot.get(key, [])
    return len(value) if isinstance(value, list) else 0


def _legacy_references(data: dict[str, Any]) -> list[dict[str, Any]]:
    references: list[dict[str, Any]] = []
    legacy_window = data.get("legacy_window")
    if isinstance(legacy_window, dict):
        references.append({"kind": "legacy_window", **dict(legacy_window)})
    legacy_targets = data.get("legacy_targets", [])
    if isinstance(legacy_targets, list):
        for item in legacy_targets:
            if isinstance(item, dict):
                references.append({"kind": "legacy_target", **dict(item)})
    return references


def _period_summaries(plan: ExplicitPeriodPlan, fixture: dict[str, Any]) -> list[ExplicitPeriodActionSummary]:
    summaries: list[ExplicitPeriodActionSummary] = []
    snapshots = fixture.get("periods", [])
    if not isinstance(snapshots, list):
        raise ValueError("explicit period diagnostics fixture periods must be a list")
    for update, snapshot in zip(plan.period_updates, snapshots, strict=True):
        if not isinstance(snapshot, dict):
            raise ValueError("explicit period diagnostics period snapshot must be an object")
        context = _context_from_period_snapshot(snapshot)
        families = _snapshot_families(snapshot)
        summaries.append(
            ExplicitPeriodActionSummary(
                period=context.period,
                global_period=compute_global_period(context),
                logtime=context.logtime,
                max_periods=context.max_periods,
                run_index=context.run_index,
                rng_seed=context.rng_seed,
                insurer_update_count=len(update.insurer_updates),
                policyholder_update_count=len(update.policyholder_updates),
                snapshot_families=families,
                vu_rule_application_count=sum(_snapshot_count(snapshot, key) for key in VU_SNAPSHOT_KEYS),
                vn_insurance_rule_application_count=_snapshot_count(snapshot, VN_INSURANCE_SNAPSHOT_KEY),
                vn_settlement_application_count=_snapshot_count(snapshot, VN_SETTLEMENT_SNAPSHOT_KEY),
                vn_damage_settlement_application_count=_snapshot_count(snapshot, VN_DAMAGE_SETTLEMENT_SNAPSHOT_KEY),
            )
        )
    return summaries


def _snapshot_validation_issues(fixture: dict[str, Any]) -> list[ExplicitPeriodDiagnosticIssue]:
    snapshots = fixture.get("periods", [])
    if not isinstance(snapshots, list):
        raise ValueError("explicit period diagnostics fixture periods must be a list")
    issues: list[ExplicitPeriodDiagnosticIssue] = []
    for snapshot in snapshots:
        if not isinstance(snapshot, dict):
            raise ValueError("explicit period diagnostics period snapshot must be an object")
        try:
            load_scenario_from_mapping(snapshot)
        except Exception as exc:
            period: int | None = None
            global_period: int | None = None
            try:
                context = _context_from_period_snapshot(snapshot)
                period = context.period
                global_period = compute_global_period(context)
            except Exception:
                pass
            issues.append(
                ExplicitPeriodDiagnosticIssue(
                    code="explicit_period_snapshot_invalid",
                    severity="error",
                    message=str(exc),
                    period=period,
                    global_period=global_period,
                )
            )
    return issues


def _ordering_issues(periods: list[ExplicitPeriodActionSummary]) -> list[ExplicitPeriodDiagnosticIssue]:
    global_periods = [period.global_period for period in periods]
    if len(set(global_periods)) != len(global_periods):
        return [
            ExplicitPeriodDiagnosticIssue(
                code="explicit_period_duplicate_global_period",
                severity="error",
                message="explicit period diagnostics found duplicate global periods",
            )
        ]
    if global_periods != sorted(global_periods):
        return [
            ExplicitPeriodDiagnosticIssue(
                code="explicit_period_non_increasing_global_periods",
                severity="error",
                message="explicit period diagnostics found non-increasing global periods",
            )
        ]
    return []


def _status_from_issues(issues: list[ExplicitPeriodDiagnosticIssue]) -> str:
    if any(issue.severity == "error" for issue in issues):
        return "error"
    if issues:
        return "warning"
    return "ok"


def diagnose_explicit_period_plan(path: str | Path) -> ExplicitPeriodDiagnosticsResult:
    plan_path = Path(path).expanduser().resolve()
    try:
        with plan_path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        if not isinstance(data, dict):
            raise ValueError("explicit period diagnostics plan must be a JSON object")
        plan = load_explicit_period_plan_from_mapping(data)
        fixture = build_explicit_period_fixture_from_plan(data)
        issues = _snapshot_validation_issues(fixture)
        periods = [] if _status_from_issues(issues) == "error" else _period_summaries(plan, fixture)
        issues.extend(_ordering_issues(periods))
        legacy_targets = _legacy_references(data)
        if not legacy_targets:
            issues.append(
                ExplicitPeriodDiagnosticIssue(
                    code="explicit_period_no_legacy_reference",
                    severity="warning",
                    message="explicit period diagnostics found no legacy target or legacy window reference",
                )
            )
        used_families = sorted({family for period in periods for family in period.snapshot_families})
        return ExplicitPeriodDiagnosticsResult(
            status=_status_from_issues(issues),
            mode="explicit_period_diagnostics",
            plan_path=str(plan_path),
            metadata=dict(plan.metadata),
            period_count=len(periods),
            periods=periods,
            global_periods=[period.global_period for period in periods],
            carry_forward_vu_state=plan.carry_forward_vu_state,
            carry_forward_vn_state=plan.carry_forward_vn_state,
            snapshot_families=used_families,
            legacy_targets=legacy_targets,
            issues=issues,
        )
    except Exception as exc:
        return ExplicitPeriodDiagnosticsResult(
            status="error",
            mode="explicit_period_diagnostics",
            plan_path=str(plan_path),
            issues=[
                ExplicitPeriodDiagnosticIssue(
                    code="explicit_period_diagnostics_failed",
                    severity="error",
                    message=str(exc),
                )
            ],
        )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Inspect an explicit IMS period plan without execution.")
    parser.add_argument("plan_path", help="Path to an explicit period plan JSON file.")
    args = parser.parse_args(argv)

    result = diagnose_explicit_period_plan(args.plan_path)
    print(json.dumps(result.to_dict(), indent=2, sort_keys=True))
    return 2 if result.status == "error" else 0


if __name__ == "__main__":
    raise SystemExit(main())
