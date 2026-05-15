from dataclasses import dataclass
import csv
import json
from pathlib import Path
from typing import Iterable

from ims.model.legacy_agrsich_reference import LegacyWindowComparison


@dataclass(slots=True)
class LegacyFieldDeviation:
    filename: str
    global_period: int | None
    field_name: str
    actual: str | float | int
    expected: str | float | int


@dataclass(slots=True)
class LegacyFileValidationSummary:
    filename: str
    export_path: Path
    legacy_path: Path
    start_period: int
    end_period: int
    matches: bool
    row_count: int
    matched_rows: int
    mismatched_rows: int
    match_rate: float
    periods_with_differences: list[int | None]
    fields_with_differences: list[str]
    field_deviations: list[LegacyFieldDeviation]


@dataclass(slots=True)
class LegacyValidationReport:
    matches: bool
    total_files: int
    total_rows: int
    matched_rows: int
    mismatched_rows: int
    match_rate: float
    file_summaries: list[LegacyFileValidationSummary]


def _match_rate(matched: int, total: int) -> float:
    if total == 0:
        return 0.0
    return matched / total


def _unique_in_order(values: Iterable[int | str | None]) -> list:
    result = []
    seen = set()
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        result.append(value)
    return result


def build_legacy_file_validation_summary(
    comparison: LegacyWindowComparison,
) -> LegacyFileValidationSummary:
    filename = comparison.export_path.name
    row_count = len(comparison.row_comparisons)
    matched_rows = sum(1 for row in comparison.row_comparisons if row.matches)
    field_deviations: list[LegacyFieldDeviation] = []

    for row in comparison.row_comparisons:
        for field in row.field_comparisons:
            if field.matches:
                continue
            field_deviations.append(
                LegacyFieldDeviation(
                    filename=filename,
                    global_period=row.global_period,
                    field_name=field.name,
                    actual=field.actual,
                    expected=field.expected,
                )
            )

    periods_with_differences = _unique_in_order(
        deviation.global_period for deviation in field_deviations
    )
    fields_with_differences = _unique_in_order(
        deviation.field_name for deviation in field_deviations
    )

    return LegacyFileValidationSummary(
        filename=filename,
        export_path=comparison.export_path,
        legacy_path=comparison.legacy_path,
        start_period=comparison.start_period,
        end_period=comparison.end_period,
        matches=comparison.matches,
        row_count=row_count,
        matched_rows=matched_rows,
        mismatched_rows=row_count - matched_rows,
        match_rate=_match_rate(matched_rows, row_count),
        periods_with_differences=periods_with_differences,
        fields_with_differences=fields_with_differences,
        field_deviations=field_deviations,
    )


def build_legacy_validation_report(
    comparisons: Iterable[LegacyWindowComparison],
) -> LegacyValidationReport:
    file_summaries = [
        build_legacy_file_validation_summary(comparison)
        for comparison in comparisons
    ]
    total_rows = sum(summary.row_count for summary in file_summaries)
    matched_rows = sum(summary.matched_rows for summary in file_summaries)

    return LegacyValidationReport(
        matches=bool(file_summaries) and all(summary.matches for summary in file_summaries),
        total_files=len(file_summaries),
        total_rows=total_rows,
        matched_rows=matched_rows,
        mismatched_rows=total_rows - matched_rows,
        match_rate=_match_rate(matched_rows, total_rows),
        file_summaries=file_summaries,
    )


def legacy_validation_report_to_dict(report: LegacyValidationReport) -> dict:
    return {
        "matches": report.matches,
        "total_files": report.total_files,
        "total_rows": report.total_rows,
        "matched_rows": report.matched_rows,
        "mismatched_rows": report.mismatched_rows,
        "match_rate": report.match_rate,
        "files": [
            {
                "filename": summary.filename,
                "export_path": str(summary.export_path),
                "legacy_path": str(summary.legacy_path),
                "start_period": summary.start_period,
                "end_period": summary.end_period,
                "matches": summary.matches,
                "row_count": summary.row_count,
                "matched_rows": summary.matched_rows,
                "mismatched_rows": summary.mismatched_rows,
                "match_rate": summary.match_rate,
                "periods_with_differences": summary.periods_with_differences,
                "fields_with_differences": summary.fields_with_differences,
                "field_deviations": [
                    {
                        "filename": deviation.filename,
                        "global_period": deviation.global_period,
                        "field_name": deviation.field_name,
                        "actual": deviation.actual,
                        "expected": deviation.expected,
                    }
                    for deviation in summary.field_deviations
                ],
            }
            for summary in report.file_summaries
        ],
    }


def write_legacy_validation_report_json(
    report: LegacyValidationReport,
    path: str | Path,
) -> Path:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(legacy_validation_report_to_dict(report), indent=2, sort_keys=True),
        encoding="utf-8",
    )
    return output_path


def write_legacy_validation_report_csv(
    report: LegacyValidationReport,
    path: str | Path,
) -> Path:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "filename",
                "legacy_path",
                "start_period",
                "end_period",
                "matches",
                "row_count",
                "matched_rows",
                "mismatched_rows",
                "match_rate",
                "periods_with_differences",
                "fields_with_differences",
                "field_deviation_count",
            ],
        )
        writer.writeheader()
        for summary in report.file_summaries:
            writer.writerow(
                {
                    "filename": summary.filename,
                    "legacy_path": str(summary.legacy_path),
                    "start_period": summary.start_period,
                    "end_period": summary.end_period,
                    "matches": summary.matches,
                    "row_count": summary.row_count,
                    "matched_rows": summary.matched_rows,
                    "mismatched_rows": summary.mismatched_rows,
                    "match_rate": f"{summary.match_rate:.6f}",
                    "periods_with_differences": ";".join(
                        "" if period is None else str(period)
                        for period in summary.periods_with_differences
                    ),
                    "fields_with_differences": ";".join(summary.fields_with_differences),
                    "field_deviation_count": len(summary.field_deviations),
                }
            )
    return output_path
