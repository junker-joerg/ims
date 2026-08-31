from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Sequence

from ims.model.agrsich_export import (
    INSURER_HEADER,
    POLICYHOLDER_HEADER,
    ExportTable,
)
from ims.model.legacy_calculated_comparison import (
    CalculatedLegacyComparisonPlan,
    RequiredCalculatedExport,
    build_calculated_legacy_comparison_plan,
)
from ims.model.legacy_calculated_deviation_report import (
    CalculatedLegacyDeviationReport,
    build_calculated_legacy_deviation_report,
)
from ims.model.legacy_export_identity import (
    ExportIdentity,
    build_legacy_export_identity,
    format_legacy_export_identity,
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
    supplied_calculated_period_count: int
    supplied_calculated_exports: tuple[str, ...]
    missing_calculated_export_count: int
    missing_calculated_period_count: int
    missing_calculated_exports: tuple[str, ...]
    calculated_delivery_origin: str
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
            "historical_periods_per_run": 100,
            "calculated_row_count_semantics": (
                "cumulative_result_rows_across_100_period_runs"
            ),
            "coverage_is_fachliche_gleichheit": False,
            "historical_300_500_single_run_claimed": False,
            "historical_rng_reproduction_required": False,
            "coverage_complete": self.coverage_complete,
            "required_calculated_export_count": self.required_calculated_export_count,
            "supplied_calculated_export_count": self.supplied_calculated_export_count,
            "supplied_calculated_period_count": self.supplied_calculated_period_count,
            "supplied_calculated_exports": list(self.supplied_calculated_exports),
            "missing_calculated_export_count": self.missing_calculated_export_count,
            "missing_calculated_period_count": self.missing_calculated_period_count,
            "missing_calculated_exports": list(self.missing_calculated_exports),
            "calculated_delivery_origin": self.calculated_delivery_origin,
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
    calculated_export_tables: Sequence[ExportTable] = (),
    calculation_origin: str = (
        "production_release_corpus_report_no_exports_supplied"
    ),
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
    comparison_plan = None
    if coverage.status != "error":
        try:
            comparison_plan = build_calculated_legacy_comparison_plan(
                resolved_fixture
            )
            deviation = build_calculated_legacy_deviation_report(
                resolved_fixture,
                list(calculated_export_tables),
                calculation_origin=calculation_origin,
            )
        except (OSError, TypeError, ValueError) as exc:
            issues.append(
                ProductionReleaseCorpusIssue(
                    code="calculated_core_report_failed",
                    message=str(exc),
                    path=str(resolved_fixture),
                )
            )

    required_export_count = (
        comparison_plan.required_export_count if comparison_plan is not None else 0
    )
    (
        supplied_exports,
        supplied_period_count,
        missing_exports,
        missing_period_count,
    ) = _calculated_delivery_summary(
        comparison_plan,
        calculated_export_tables,
        deviation,
    )
    supplied_export_count = len(supplied_exports)
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
        supplied_calculated_period_count=supplied_period_count,
        supplied_calculated_exports=supplied_exports,
        missing_calculated_export_count=len(missing_exports),
        missing_calculated_period_count=missing_period_count,
        missing_calculated_exports=missing_exports,
        calculated_delivery_origin=calculation_origin.strip(),
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


def _calculated_delivery_summary(
    plan: CalculatedLegacyComparisonPlan | None,
    tables: Sequence[ExportTable],
    deviation: CalculatedLegacyDeviationReport | None,
) -> tuple[tuple[str, ...], int, tuple[str, ...], int]:
    if plan is None or deviation is None:
        return (), 0, (), 0
    required_by_identity = {
        _required_identity(item): item for item in plan.required_exports
    }
    tables_by_identity: dict[ExportIdentity, list[ExportTable]] = {}
    for table in tables:
        identity = _table_identity(table)
        tables_by_identity.setdefault(identity, []).append(table)
    invalid_labels = {
        issue.export_identity
        for issue in deviation.input_issues
        if issue.code != "required_export_missing"
        and issue.export_identity is not None
    }
    global_input_error = any(
        issue.code != "required_export_missing" and issue.export_identity is None
        for issue in deviation.input_issues
    )
    accepted = {
        identity
        for identity in required_by_identity
        if not global_input_error
        and len(tables_by_identity.get(identity, ())) == 1
        and format_legacy_export_identity(identity) not in invalid_labels
        and _table_matches_delivery_shape(
            tables_by_identity[identity][0],
            required_by_identity[identity],
        )
    }
    supplied_exports = tuple(
        sorted(required_by_identity[identity].filename for identity in accepted)
    )
    supplied_period_count = sum(
        len(required_by_identity[identity].periods) for identity in accepted
    )
    missing_identities = required_by_identity.keys() - accepted
    missing_exports = tuple(
        sorted(format_legacy_export_identity(identity) for identity in missing_identities)
    )
    missing_period_count = sum(
        len(required_by_identity[identity].periods)
        for identity in missing_identities
    )
    return (
        supplied_exports,
        supplied_period_count,
        missing_exports,
        missing_period_count,
    )


def _required_identity(item: RequiredCalculatedExport) -> ExportIdentity:
    return build_legacy_export_identity(
        item.filename,
        item.subject_type,
        item.level,
        item.selector_kind,
        item.selector_value,
    )


def _table_identity(table: ExportTable) -> ExportIdentity:
    return build_legacy_export_identity(
        table.spec.filename,
        table.spec.subject_type,
        table.spec.level,
        table.spec.selector_kind,
        table.spec.selector_value,
    )


def _table_matches_delivery_shape(
    table: ExportTable,
    required: RequiredCalculatedExport,
) -> bool:
    expected_header = (
        INSURER_HEADER
        if required.subject_type == "insurer"
        else POLICYHOLDER_HEADER
    )
    return table.header == expected_header and all(
        len(row.values) == len(expected_header.split()) for row in table.rows
    )


if __name__ == "__main__":
    raise SystemExit(main())
