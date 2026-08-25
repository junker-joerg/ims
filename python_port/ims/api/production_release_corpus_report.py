from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Sequence

from ims.model.legacy_calculated_deviation_report import (
    CalculatedLegacyDeviationReport,
    build_calculated_legacy_deviation_report,
)
from ims.model.legacy_validation_coverage import (
    build_legacy_validation_coverage_matrix,
)


REPORT_CONTRACT_VERSION = "pr69-v1"
DEFAULT_BUNDLE_PATH = Path("tests/fixtures/legacy_validation_bundle.json")
DEFAULT_REFERENCE_DIR = Path("tests/references/legacy_agrsich")
OPERATIONAL_EVIDENCE_PATHS = {
    "backend_api": Path("python_port/ims/api/app.py"),
    "frontend_ui": Path("frontend/src/main.tsx"),
    "start_script": Path("scripts/workbench/start-workbench.cmd"),
    "check_script": Path("scripts/workbench/check-workbench.cmd"),
    "release_checklist": Path("docs/migration/workbench_release_checklist.md"),
    "metadata_recovery": Path("docs/migration/workbench_metadata_recovery.md"),
}


@dataclass(frozen=True)
class ProductionReleaseEvidence:
    name: str
    path: str
    available: bool
    scope: str = "technical_workbench_evidence"

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "path": self.path,
            "available": self.available,
            "scope": self.scope,
        }


@dataclass(frozen=True)
class ProductionReleaseCorpusIssue:
    code: str
    message: str
    severity: str = "error"
    path: str | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "code": self.code,
            "severity": self.severity,
            "message": self.message,
            "path": self.path,
        }


@dataclass(frozen=True)
class ProductionReleaseCorpusReport:
    repo_root: str
    fixture_path: str
    reference_dir: str
    status: str
    release_decision: str
    reference_count: int
    available_reference_count: int
    covered_file_count: int
    covered_rows: int
    covered_periods: int
    coverage_complete: bool
    required_calculated_export_count: int
    supplied_calculated_export_count: int
    missing_calculated_export_count: int
    missing_calculated_exports: tuple[str, ...]
    calculated_comparison_status: str
    calculated_comparison_performed: bool
    calculated_core_validation_complete: bool
    operational_evidence: tuple[ProductionReleaseEvidence, ...]
    operational_evidence_complete: bool
    issues: tuple[ProductionReleaseCorpusIssue, ...] = field(default_factory=tuple)
    mode: str = "production_release_corpus_report"

    def to_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "mode": self.mode,
            "report_contract_version": REPORT_CONTRACT_VERSION,
            "repo_root": self.repo_root,
            "fixture_path": self.fixture_path,
            "reference_dir": self.reference_dir,
            "release_decision": self.release_decision,
            "production_release_approved": False,
            "reference_count": self.reference_count,
            "available_reference_count": self.available_reference_count,
            "covered_file_count": self.covered_file_count,
            "covered_rows": self.covered_rows,
            "covered_periods": self.covered_periods,
            "coverage_complete": self.coverage_complete,
            "required_calculated_export_count": self.required_calculated_export_count,
            "supplied_calculated_export_count": self.supplied_calculated_export_count,
            "missing_calculated_export_count": self.missing_calculated_export_count,
            "missing_calculated_exports": list(self.missing_calculated_exports),
            "calculated_comparison_status": self.calculated_comparison_status,
            "calculated_comparison_performed": self.calculated_comparison_performed,
            "calculated_core_validation_complete": self.calculated_core_validation_complete,
            "operational_evidence": [item.to_dict() for item in self.operational_evidence],
            "operational_evidence_complete": self.operational_evidence_complete,
            "reviewable_demo_evidence_complete": (
                self.coverage_complete and self.operational_evidence_complete
            ),
            "issues": [issue.to_dict() for issue in self.issues],
            "writes_performed": False,
            "execution_performed": False,
            "adapter_started": False,
            "simulation_performed": False,
            "automatic_historical_rule_selection_performed": False,
            "historical_full_equality_claimed": False,
        }


def build_production_release_corpus_report(
    repo_root: Path | str,
    *,
    fixture_path: Path | str | None = None,
    reference_dir: Path | str | None = None,
) -> ProductionReleaseCorpusReport:
    root = Path(repo_root).expanduser().resolve()
    resolved_fixture = _resolve_path(root, fixture_path, DEFAULT_BUNDLE_PATH)
    resolved_reference_dir = _resolve_path(root, reference_dir, DEFAULT_REFERENCE_DIR)
    evidence = _build_operational_evidence(root)
    issues = _operational_issues(evidence)

    coverage = build_legacy_validation_coverage_matrix(
        resolved_fixture,
        reference_dir=resolved_reference_dir,
    )
    coverage_complete = (
        coverage.status == "ok"
        and coverage.reference_count > 0
        and coverage.available_reference_count == coverage.reference_count
        and coverage.covered_file_count == coverage.reference_count
        and not coverage.gaps
    )
    if not coverage_complete:
        issues.append(
            ProductionReleaseCorpusIssue(
                code="core_reference_coverage_incomplete",
                message="the production legacy core corpus coverage is incomplete",
                path=str(resolved_fixture),
            )
        )
    issues.extend(
        ProductionReleaseCorpusIssue(
            code=f"coverage_{item.code}",
            message=item.message,
            severity=item.severity,
            path=str(resolved_fixture),
        )
        for item in coverage.issues
    )

    deviation = None
    if coverage.status != "error":
        try:
            deviation = build_calculated_legacy_deviation_report(
                resolved_fixture,
                [],
                calculation_origin="production_release_corpus_report_no_exports_supplied",
            )
        except (OSError, TypeError, ValueError) as exc:
            issues.append(
                ProductionReleaseCorpusIssue(
                    code="calculated_core_report_failed",
                    message=str(exc),
                    path=str(resolved_fixture),
                )
            )

    required_export_count = deviation.required_export_count if deviation is not None else 0
    supplied_export_count = deviation.supplied_export_count if deviation is not None else 0
    missing_exports = _missing_calculated_exports(deviation)
    calculated_complete = bool(
        deviation is not None
        and deviation.comparison_performed
        and deviation.matches is True
        and not deviation.blocking_numeric_differences
        and not deviation.open_field_questions
    )
    if deviation is not None and not calculated_complete:
        issues.append(
            ProductionReleaseCorpusIssue(
                code="calculated_core_validation_incomplete",
                severity="blocker",
                message=(
                    "independent calculated core corpus validation is incomplete; "
                    f"{len(missing_exports)} required exports are missing"
                ),
                path=str(resolved_fixture),
            )
        )

    operational_complete = all(item.available for item in evidence)
    has_error = any(issue.severity == "error" for issue in issues)
    if has_error:
        status = "error"
        release_decision = "blocked_invalid_evidence"
    elif not calculated_complete:
        status = "blocked"
        release_decision = "blocked_calculated_core_validation"
    else:
        status = "review_required"
        release_decision = "human_release_review_required"

    return ProductionReleaseCorpusReport(
        repo_root=str(root),
        fixture_path=str(resolved_fixture),
        reference_dir=str(resolved_reference_dir),
        status=status,
        release_decision=release_decision,
        reference_count=coverage.reference_count,
        available_reference_count=coverage.available_reference_count,
        covered_file_count=coverage.covered_file_count,
        covered_rows=coverage.covered_rows,
        covered_periods=coverage.covered_periods,
        coverage_complete=coverage_complete,
        required_calculated_export_count=required_export_count,
        supplied_calculated_export_count=supplied_export_count,
        missing_calculated_export_count=len(missing_exports),
        missing_calculated_exports=missing_exports,
        calculated_comparison_status=(deviation.status if deviation is not None else "not_available"),
        calculated_comparison_performed=(
            deviation.comparison_performed if deviation is not None else False
        ),
        calculated_core_validation_complete=calculated_complete,
        operational_evidence=tuple(evidence),
        operational_evidence_complete=operational_complete,
        issues=tuple(issues),
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m ims.api.production_release_corpus_report",
        description="Erzeugt den read-only PR-69-Abschlussbericht fuer den Produktionskorpus.",
    )
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--fixture", type=Path)
    parser.add_argument("--reference-dir", type=Path)
    args = parser.parse_args(argv)

    result = build_production_release_corpus_report(
        args.repo_root,
        fixture_path=args.fixture,
        reference_dir=args.reference_dir,
    )
    print(json.dumps(result.to_dict(), ensure_ascii=True, sort_keys=True))
    return 2 if result.status == "error" else 0


def _resolve_path(root: Path, value: Path | str | None, default: Path) -> Path:
    path = Path(value) if value is not None else default
    if not path.is_absolute():
        path = root / path
    return path.expanduser().resolve()


def _build_operational_evidence(root: Path) -> list[ProductionReleaseEvidence]:
    return [
        ProductionReleaseEvidence(
            name=name,
            path=str((root / relative_path).resolve()),
            available=(root / relative_path).is_file(),
        )
        for name, relative_path in OPERATIONAL_EVIDENCE_PATHS.items()
    ]


def _operational_issues(
    evidence: Sequence[ProductionReleaseEvidence],
) -> list[ProductionReleaseCorpusIssue]:
    return [
        ProductionReleaseCorpusIssue(
            code="operational_evidence_missing",
            message=f"required technical workbench evidence is missing: {item.name}",
            path=item.path,
        )
        for item in evidence
        if not item.available
    ]


def _missing_calculated_exports(
    deviation: CalculatedLegacyDeviationReport | None,
) -> tuple[str, ...]:
    if deviation is None:
        return ()
    return tuple(
        sorted(
            str(issue.export_identity)
            for issue in deviation.input_issues
            if issue.code == "required_export_missing" and issue.export_identity is not None
        )
    )


if __name__ == "__main__":
    raise SystemExit(main())
