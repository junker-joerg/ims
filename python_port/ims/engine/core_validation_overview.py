from dataclasses import dataclass, field
import argparse
import json
from pathlib import Path
from typing import Any

from ims.engine.explicit_period_diagnostics_bundle import (
    ExplicitPeriodDiagnosticsBundleResult,
    build_explicit_period_diagnostics_bundle,
)
from ims.model.legacy_validation_coverage import (
    LegacyValidationCoverageMatrixResult,
    build_legacy_validation_coverage_matrix,
)
from ims.model.legacy_validation_next_family import (
    LegacyValidationNextFamilyPlan,
    build_legacy_validation_next_family_plan,
)
from ims.model.legacy_validation_overview import (
    LegacyValidationOverviewResult,
    build_legacy_validation_overview,
)


@dataclass(slots=True)
class CoreValidationOverviewIssue:
    source: str
    code: str
    message: str
    severity: str

    def to_dict(self) -> dict[str, str]:
        return {
            "source": self.source,
            "code": self.code,
            "severity": self.severity,
            "message": self.message,
        }


@dataclass(slots=True)
class CoreValidationOverviewResult:
    status: str
    mode: str
    plan_count: int
    legacy_fixture_path: str
    period_plan_paths: list[str]
    reference_dir: str | None = None
    period_count: int = 0
    global_periods: list[int] = field(default_factory=list)
    legacy_reference_count: int = 0
    legacy_covered_rows: int = 0
    legacy_covered_periods: int = 0
    next_validation_actions: list[str] = field(default_factory=list)
    period_diagnostics: ExplicitPeriodDiagnosticsBundleResult | None = None
    legacy_validation: LegacyValidationOverviewResult | None = None
    coverage_matrix: LegacyValidationCoverageMatrixResult | None = None
    next_family_plan: LegacyValidationNextFamilyPlan | None = None
    issues: list[CoreValidationOverviewIssue] = field(default_factory=list)
    writes_performed: bool = False
    execution_performed: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "mode": self.mode,
            "plan_count": self.plan_count,
            "legacy_fixture_path": self.legacy_fixture_path,
            "period_plan_paths": list(self.period_plan_paths),
            "reference_dir": self.reference_dir,
            "period_count": self.period_count,
            "global_periods": list(self.global_periods),
            "legacy_reference_count": self.legacy_reference_count,
            "legacy_covered_rows": self.legacy_covered_rows,
            "legacy_covered_periods": self.legacy_covered_periods,
            "next_validation_actions": list(self.next_validation_actions),
            "period_diagnostics": None
            if self.period_diagnostics is None
            else self.period_diagnostics.to_dict(),
            "legacy_validation": None
            if self.legacy_validation is None
            else self.legacy_validation.to_dict(),
            "coverage_matrix": None if self.coverage_matrix is None else self.coverage_matrix.to_dict(),
            "next_family_plan": None if self.next_family_plan is None else self.next_family_plan.to_dict(),
            "issues": [issue.to_dict() for issue in self.issues],
            "writes_performed": self.writes_performed,
            "execution_performed": self.execution_performed,
        }


def _status_from_parts(statuses: list[str]) -> str:
    if "error" in statuses:
        return "error"
    if "warning" in statuses:
        return "warning"
    return "ok"


def _issues_from_payload(source: str, payload: dict[str, Any]) -> list[CoreValidationOverviewIssue]:
    issues: list[CoreValidationOverviewIssue] = []
    for item in payload.get("issues", []):
        if not isinstance(item, dict):
            continue
        issues.append(
            CoreValidationOverviewIssue(
                source=source,
                code=str(item.get("code", "unknown")),
                severity=str(item.get("severity", "warning")),
                message=str(item.get("message", "")),
            )
        )
    return issues


def build_core_validation_overview(
    *,
    legacy_fixture_path: str | Path,
    period_plan_paths: list[str | Path],
    reference_dir: str | Path | None = None,
) -> CoreValidationOverviewResult:
    period_diagnostics = build_explicit_period_diagnostics_bundle(period_plan_paths)
    legacy_validation = build_legacy_validation_overview(legacy_fixture_path)
    coverage_matrix = build_legacy_validation_coverage_matrix(legacy_fixture_path, reference_dir=reference_dir)
    next_family_plan = build_legacy_validation_next_family_plan(legacy_fixture_path, reference_dir=reference_dir)

    issues = (
        _issues_from_payload("period_diagnostics", period_diagnostics.to_dict())
        + _issues_from_payload("legacy_validation", legacy_validation.to_dict())
        + _issues_from_payload("coverage_matrix", coverage_matrix.to_dict())
        + _issues_from_payload("next_family_plan", next_family_plan.to_dict())
    )
    statuses = [
        period_diagnostics.status,
        legacy_validation.status,
        coverage_matrix.status,
        next_family_plan.status,
    ]
    resolved_period_paths = [str(Path(path).expanduser().resolve()) for path in period_plan_paths]
    resolved_reference_dir = None if reference_dir is None else str(Path(reference_dir).expanduser().resolve())
    return CoreValidationOverviewResult(
        status=_status_from_parts(statuses),
        mode="ims_core_validation_overview",
        plan_count=period_diagnostics.plan_count,
        legacy_fixture_path=str(Path(legacy_fixture_path).expanduser().resolve()),
        period_plan_paths=resolved_period_paths,
        reference_dir=resolved_reference_dir,
        period_count=period_diagnostics.total_period_count,
        global_periods=period_diagnostics.global_periods,
        legacy_reference_count=coverage_matrix.reference_count,
        legacy_covered_rows=coverage_matrix.covered_rows,
        legacy_covered_periods=coverage_matrix.covered_periods,
        next_validation_actions=sorted({action.next_action for action in next_family_plan.actions}),
        period_diagnostics=period_diagnostics,
        legacy_validation=legacy_validation,
        coverage_matrix=coverage_matrix,
        next_family_plan=next_family_plan,
        issues=issues,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Summarize IMS core validation diagnostics without execution or writes.",
    )
    parser.add_argument(
        "--legacy-fixture",
        required=True,
        help="Path to the Legacy-Agrsich validation fixture JSON file.",
    )
    parser.add_argument(
        "--reference-dir",
        help="Optional directory containing historical Legacy-Agrsich reference files.",
    )
    parser.add_argument("period_plan_paths", nargs="+", help="Paths to explicit period plan JSON files.")
    args = parser.parse_args(argv)

    result = build_core_validation_overview(
        legacy_fixture_path=args.legacy_fixture,
        period_plan_paths=args.period_plan_paths,
        reference_dir=args.reference_dir,
    )
    print(json.dumps(result.to_dict(), indent=2, sort_keys=True))
    return 2 if result.status == "error" else 0


if __name__ == "__main__":
    raise SystemExit(main())
