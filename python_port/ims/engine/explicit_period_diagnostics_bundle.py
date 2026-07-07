from dataclasses import dataclass, field
import argparse
import json
from pathlib import Path
from typing import Any

from ims.engine.explicit_period_diagnostics import (
    ExplicitPeriodDiagnosticIssue,
    ExplicitPeriodDiagnosticsResult,
    diagnose_explicit_period_plan,
)


@dataclass(slots=True)
class ExplicitPeriodDiagnosticsBundleResult:
    status: str
    mode: str
    plan_count: int
    ok_plan_count: int = 0
    warning_plan_count: int = 0
    error_plan_count: int = 0
    total_period_count: int = 0
    global_periods: list[int] = field(default_factory=list)
    snapshot_families: list[str] = field(default_factory=list)
    legacy_target_count: int = 0
    plans: list[ExplicitPeriodDiagnosticsResult] = field(default_factory=list)
    issues: list[ExplicitPeriodDiagnosticIssue] = field(default_factory=list)
    writes_performed: bool = False
    execution_performed: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "mode": self.mode,
            "plan_count": self.plan_count,
            "ok_plan_count": self.ok_plan_count,
            "warning_plan_count": self.warning_plan_count,
            "error_plan_count": self.error_plan_count,
            "total_period_count": self.total_period_count,
            "global_periods": list(self.global_periods),
            "snapshot_families": list(self.snapshot_families),
            "legacy_target_count": self.legacy_target_count,
            "plans": [plan.to_dict() for plan in self.plans],
            "issues": [issue.to_dict() for issue in self.issues],
            "writes_performed": self.writes_performed,
            "execution_performed": self.execution_performed,
        }


def _bundle_status(results: list[ExplicitPeriodDiagnosticsResult]) -> str:
    if any(result.status == "error" for result in results):
        return "error"
    if any(result.status == "warning" for result in results):
        return "warning"
    return "ok"


def _bundle_issues(results: list[ExplicitPeriodDiagnosticsResult]) -> list[ExplicitPeriodDiagnosticIssue]:
    issues: list[ExplicitPeriodDiagnosticIssue] = []
    for result in results:
        for issue in result.issues:
            issues.append(
                ExplicitPeriodDiagnosticIssue(
                    code=issue.code,
                    severity=issue.severity,
                    message=f"{Path(result.plan_path).name}: {issue.message}",
                    period=issue.period,
                    global_period=issue.global_period,
                )
            )
    return issues


def build_explicit_period_diagnostics_bundle(
    plan_paths: list[str | Path],
) -> ExplicitPeriodDiagnosticsBundleResult:
    if not plan_paths:
        return ExplicitPeriodDiagnosticsBundleResult(
            status="error",
            mode="explicit_period_diagnostics_bundle",
            plan_count=0,
            issues=[
                ExplicitPeriodDiagnosticIssue(
                    code="explicit_period_diagnostics_bundle_empty",
                    severity="error",
                    message="explicit period diagnostics bundle requires at least one plan path",
                )
            ],
        )
    results = [diagnose_explicit_period_plan(path) for path in plan_paths]
    return ExplicitPeriodDiagnosticsBundleResult(
        status=_bundle_status(results),
        mode="explicit_period_diagnostics_bundle",
        plan_count=len(results),
        ok_plan_count=sum(1 for result in results if result.status == "ok"),
        warning_plan_count=sum(1 for result in results if result.status == "warning"),
        error_plan_count=sum(1 for result in results if result.status == "error"),
        total_period_count=sum(result.period_count for result in results),
        global_periods=sorted({period for result in results for period in result.global_periods}),
        snapshot_families=sorted({family for result in results for family in result.snapshot_families}),
        legacy_target_count=sum(len(result.legacy_targets) for result in results),
        plans=results,
        issues=_bundle_issues(results),
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Bundle explicit IMS period plan diagnostics without execution.",
    )
    parser.add_argument("plan_paths", nargs="+", help="Paths to explicit period plan JSON files.")
    args = parser.parse_args(argv)

    result = build_explicit_period_diagnostics_bundle(args.plan_paths)
    print(json.dumps(result.to_dict(), indent=2, sort_keys=True))
    return 2 if result.status == "error" else 0


if __name__ == "__main__":
    raise SystemExit(main())
