from dataclasses import dataclass, field
import argparse
import json
from pathlib import Path
from typing import Any

from ims.model.legacy_validation_report import (
    LegacyFieldDeviationSummary,
    LegacyFileValidationSummary,
    LegacyValidationPeriodSummary,
)
from ims.model.legacy_validation_run import (
    LegacyValidationRunResult,
    run_legacy_validation_from_fixture,
)


LEGACY_VALIDATION_DEFAULT_TOLERANCE = 0.05


@dataclass(slots=True)
class LegacyValidationOverviewIssue:
    code: str
    message: str
    severity: str = "error"

    def to_dict(self) -> dict[str, str]:
        return {
            "code": self.code,
            "severity": self.severity,
            "message": self.message,
        }


@dataclass(slots=True)
class LegacyValidationToleranceSummary:
    export_filename: str
    subject_type: str
    tolerance: float
    source: str = "legacy_compare_default"

    def to_dict(self) -> dict[str, Any]:
        return {
            "export_filename": self.export_filename,
            "subject_type": self.subject_type,
            "tolerance": self.tolerance,
            "source": self.source,
        }


@dataclass(slots=True)
class LegacyValidationTableOverview:
    filename: str
    subject_type: str
    level: str
    selector_kind: str
    selector_value: int | str | None
    start_period: int
    end_period: int
    row_count: int
    matched_rows: int
    mismatched_rows: int
    match_rate: float
    matches: bool
    fields_with_differences: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "filename": self.filename,
            "subject_type": self.subject_type,
            "level": self.level,
            "selector_kind": self.selector_kind,
            "selector_value": self.selector_value,
            "start_period": self.start_period,
            "end_period": self.end_period,
            "row_count": self.row_count,
            "matched_rows": self.matched_rows,
            "mismatched_rows": self.mismatched_rows,
            "match_rate": self.match_rate,
            "matches": self.matches,
            "fields_with_differences": list(self.fields_with_differences),
        }


@dataclass(slots=True)
class LegacyValidationPeriodOverview:
    global_period: int | None
    file_count: int
    row_count: int
    matched_rows: int
    mismatched_rows: int
    match_rate: float
    matches: bool
    filenames: list[str]
    fields_with_differences: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "global_period": self.global_period,
            "file_count": self.file_count,
            "row_count": self.row_count,
            "matched_rows": self.matched_rows,
            "mismatched_rows": self.mismatched_rows,
            "match_rate": self.match_rate,
            "matches": self.matches,
            "filenames": list(self.filenames),
            "fields_with_differences": list(self.fields_with_differences),
        }


@dataclass(slots=True)
class LegacyValidationFieldOverview:
    filename: str
    field_name: str
    deviation_count: int
    periods_with_differences: list[int | None]
    numeric_deviation_count: int
    max_abs_delta: float | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "filename": self.filename,
            "field_name": self.field_name,
            "deviation_count": self.deviation_count,
            "periods_with_differences": list(self.periods_with_differences),
            "numeric_deviation_count": self.numeric_deviation_count,
            "max_abs_delta": self.max_abs_delta,
        }


@dataclass(slots=True)
class LegacyValidationCoverageOverview:
    filename: str
    legacy_path: str
    legacy_source: str
    is_legacy_reference: bool
    subject_type: str
    level: str
    selector_kind: str
    selector_value: int | str | None
    start_period: int
    end_period: int
    period_count: int
    row_count: int
    matches: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "filename": self.filename,
            "legacy_path": self.legacy_path,
            "legacy_source": self.legacy_source,
            "is_legacy_reference": self.is_legacy_reference,
            "subject_type": self.subject_type,
            "level": self.level,
            "selector_kind": self.selector_kind,
            "selector_value": self.selector_value,
            "start_period": self.start_period,
            "end_period": self.end_period,
            "period_count": self.period_count,
            "row_count": self.row_count,
            "matches": self.matches,
        }


@dataclass(slots=True)
class LegacyValidationOverviewResult:
    status: str
    mode: str
    fixture_path: str
    reference_count: int = 0
    table_count: int = 0
    period_count: int = 0
    field_summary_count: int = 0
    deviation_count: int = 0
    matches: bool = False
    total_rows: int = 0
    matched_rows: int = 0
    mismatched_rows: int = 0
    match_rate: float = 0.0
    periods: list[LegacyValidationPeriodOverview] = field(default_factory=list)
    tables: list[LegacyValidationTableOverview] = field(default_factory=list)
    coverage: list[LegacyValidationCoverageOverview] = field(default_factory=list)
    field_summaries: list[LegacyValidationFieldOverview] = field(default_factory=list)
    tolerances: list[LegacyValidationToleranceSummary] = field(default_factory=list)
    issues: list[LegacyValidationOverviewIssue] = field(default_factory=list)
    writes_performed: bool = False
    execution_performed: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "mode": self.mode,
            "fixture_path": self.fixture_path,
            "reference_count": self.reference_count,
            "table_count": self.table_count,
            "period_count": self.period_count,
            "field_summary_count": self.field_summary_count,
            "deviation_count": self.deviation_count,
            "matches": self.matches,
            "total_rows": self.total_rows,
            "matched_rows": self.matched_rows,
            "mismatched_rows": self.mismatched_rows,
            "match_rate": self.match_rate,
            "periods": [period.to_dict() for period in self.periods],
            "tables": [table.to_dict() for table in self.tables],
            "coverage": [entry.to_dict() for entry in self.coverage],
            "field_summaries": [summary.to_dict() for summary in self.field_summaries],
            "tolerances": [tolerance.to_dict() for tolerance in self.tolerances],
            "issues": [issue.to_dict() for issue in self.issues],
            "writes_performed": self.writes_performed,
            "execution_performed": self.execution_performed,
        }


def _status_from_report(result: LegacyValidationRunResult) -> str:
    return "ok" if result.report.matches else "warning"


def _table_overview(summary: LegacyFileValidationSummary) -> LegacyValidationTableOverview:
    return LegacyValidationTableOverview(
        filename=summary.filename,
        subject_type=summary.subject_type,
        level=summary.level,
        selector_kind=summary.selector_kind,
        selector_value=summary.selector_value,
        start_period=summary.start_period,
        end_period=summary.end_period,
        row_count=summary.row_count,
        matched_rows=summary.matched_rows,
        mismatched_rows=summary.mismatched_rows,
        match_rate=summary.match_rate,
        matches=summary.matches,
        fields_with_differences=list(summary.fields_with_differences),
    )


def _period_overview(summary: LegacyValidationPeriodSummary) -> LegacyValidationPeriodOverview:
    return LegacyValidationPeriodOverview(
        global_period=summary.global_period,
        file_count=summary.file_count,
        row_count=summary.row_count,
        matched_rows=summary.matched_rows,
        mismatched_rows=summary.mismatched_rows,
        match_rate=summary.match_rate,
        matches=summary.matches,
        filenames=list(summary.filenames),
        fields_with_differences=list(summary.fields_with_differences),
    )


def _field_overview(summary: LegacyFieldDeviationSummary) -> LegacyValidationFieldOverview:
    return LegacyValidationFieldOverview(
        filename=summary.filename,
        field_name=summary.field_name,
        deviation_count=summary.deviation_count,
        periods_with_differences=list(summary.periods_with_differences),
        numeric_deviation_count=summary.numeric_deviation_count,
        max_abs_delta=summary.max_abs_delta,
    )


def _legacy_source(path: Path) -> tuple[str, bool]:
    normalized_parts = tuple(part.lower() for part in path.parts)
    if "legacy_agrsich" in normalized_parts:
        return "legacy_agrsich", True
    return "unknown", False


def _coverage_overview(result: LegacyValidationRunResult) -> list[LegacyValidationCoverageOverview]:
    summaries_by_filename = {summary.filename: summary for summary in result.report.file_summaries}
    coverage: list[LegacyValidationCoverageOverview] = []
    for target in result.targets:
        summary = summaries_by_filename[target.export_filename]
        legacy_source, is_legacy_reference = _legacy_source(target.legacy_path)
        coverage.append(
            LegacyValidationCoverageOverview(
                filename=target.export_filename,
                legacy_path=str(target.legacy_path),
                legacy_source=legacy_source,
                is_legacy_reference=is_legacy_reference,
                subject_type=target.subject_type,
                level=target.level,
                selector_kind=target.selector_kind,
                selector_value=target.selector_value,
                start_period=summary.start_period,
                end_period=summary.end_period,
                period_count=len(target.periods),
                row_count=summary.row_count,
                matches=summary.matches,
            )
        )
    return coverage


def build_legacy_validation_overview(path: str | Path) -> LegacyValidationOverviewResult:
    fixture_path = Path(path).expanduser().resolve()
    try:
        result = run_legacy_validation_from_fixture(fixture_path)
        report = result.report
        tolerances = [
            LegacyValidationToleranceSummary(
                export_filename=target.export_filename,
                subject_type=target.subject_type,
                tolerance=LEGACY_VALIDATION_DEFAULT_TOLERANCE,
            )
            for target in result.targets
        ]
        return LegacyValidationOverviewResult(
            status=_status_from_report(result),
            mode="legacy_agrsich_validation_overview",
            fixture_path=str(fixture_path),
            reference_count=len(result.targets),
            table_count=report.total_files,
            period_count=len(report.period_summaries),
            field_summary_count=len(report.field_summaries),
            deviation_count=len(report.deviation_index),
            matches=report.matches,
            total_rows=report.total_rows,
            matched_rows=report.matched_rows,
            mismatched_rows=report.mismatched_rows,
            match_rate=report.match_rate,
            periods=[_period_overview(summary) for summary in report.period_summaries],
            tables=[_table_overview(summary) for summary in report.file_summaries],
            coverage=_coverage_overview(result),
            field_summaries=[_field_overview(summary) for summary in report.field_summaries],
            tolerances=tolerances,
        )
    except Exception as exc:
        return LegacyValidationOverviewResult(
            status="error",
            mode="legacy_agrsich_validation_overview",
            fixture_path=str(fixture_path),
            issues=[
                LegacyValidationOverviewIssue(
                    code="legacy_validation_overview_failed",
                    message=str(exc),
                )
            ],
        )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Summarize an existing Legacy-Agrsich validation fixture without writing artifacts.",
    )
    parser.add_argument("fixture_path", help="Path to a legacy validation fixture JSON file.")
    args = parser.parse_args(argv)

    result = build_legacy_validation_overview(args.fixture_path)
    print(json.dumps(result.to_dict(), indent=2, sort_keys=True))
    return 2 if result.status == "error" else 0


if __name__ == "__main__":
    raise SystemExit(main())
