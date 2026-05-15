from dataclasses import dataclass
import csv
import json
from pathlib import Path
from typing import Iterable

from ims.model.legacy_agrsich_multi_period import LegacyTableComparison, MultiPeriodLegacyComparison
from ims.model.legacy_agrsich_reference import LegacyWindowComparison


@dataclass(slots=True)
class LegacyFieldDeviation:
    filename: str
    global_period: int | None
    field_name: str
    actual: str | float | int
    expected: str | float | int


@dataclass(slots=True)
class LegacyFieldDeviationSummary:
    filename: str
    field_name: str
    deviation_count: int
    periods_with_differences: list[int | None]
    numeric_deviation_count: int
    max_abs_delta: float | None


@dataclass(slots=True)
class LegacyValidationGroupSummary:
    subject_type: str
    level: str
    file_count: int
    row_count: int
    matched_rows: int
    mismatched_rows: int
    match_rate: float
    matches: bool
    filenames: list[str]
    fields_with_differences: list[str]


@dataclass(slots=True)
class LegacyValidationPeriodSummary:
    global_period: int | None
    file_count: int
    row_count: int
    matched_rows: int
    mismatched_rows: int
    match_rate: float
    matches: bool
    filenames: list[str]
    fields_with_differences: list[str]


@dataclass(slots=True)
class LegacyValidationDeviationRecord:
    filename: str
    subject_type: str
    level: str
    selector_kind: str
    selector_value: int | str | None
    global_period: int | None
    field_name: str
    actual: str | float | int
    expected: str | float | int


@dataclass(slots=True)
class LegacyFileValidationSummary:
    filename: str
    subject_type: str
    level: str
    selector_kind: str
    selector_value: int | str | None
    export_path: Path
    legacy_path: Path | None
    start_period: int
    end_period: int
    matches: bool
    row_count: int
    matched_rows: int
    mismatched_rows: int
    match_rate: float
    compared_periods: list[int | None]
    periods_with_differences: list[int | None]
    fields_with_differences: list[str]
    field_deviations: list[LegacyFieldDeviation]
    field_summaries: list[LegacyFieldDeviationSummary]


@dataclass(slots=True)
class LegacyValidationReport:
    matches: bool
    total_files: int
    total_rows: int
    matched_rows: int
    mismatched_rows: int
    match_rate: float
    file_summaries: list[LegacyFileValidationSummary]
    field_summaries: list[LegacyFieldDeviationSummary]
    group_summaries: list[LegacyValidationGroupSummary]
    period_summaries: list[LegacyValidationPeriodSummary]
    deviation_index: list[LegacyValidationDeviationRecord]


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


def _numeric_delta(deviation: LegacyFieldDeviation) -> float | None:
    if isinstance(deviation.actual, bool) or isinstance(deviation.expected, bool):
        return None
    if not isinstance(deviation.actual, int | float) or not isinstance(deviation.expected, int | float):
        return None
    return abs(float(deviation.actual) - float(deviation.expected))


def _build_field_deviation_summaries(
    deviations: Iterable[LegacyFieldDeviation],
) -> list[LegacyFieldDeviationSummary]:
    grouped: dict[tuple[str, str], list[LegacyFieldDeviation]] = {}
    ordered_keys: list[tuple[str, str]] = []
    for deviation in deviations:
        key = (deviation.filename, deviation.field_name)
        if key not in grouped:
            grouped[key] = []
            ordered_keys.append(key)
        grouped[key].append(deviation)

    summaries: list[LegacyFieldDeviationSummary] = []
    for filename, field_name in ordered_keys:
        items = grouped[(filename, field_name)]
        deltas = [
            delta
            for delta in (_numeric_delta(deviation) for deviation in items)
            if delta is not None
        ]
        summaries.append(
            LegacyFieldDeviationSummary(
                filename=filename,
                field_name=field_name,
                deviation_count=len(items),
                periods_with_differences=_unique_in_order(
                    deviation.global_period for deviation in items
                ),
                numeric_deviation_count=len(deltas),
                max_abs_delta=max(deltas) if deltas else None,
            )
        )
    return summaries


def _build_group_summaries(
    file_summaries: Iterable[LegacyFileValidationSummary],
) -> list[LegacyValidationGroupSummary]:
    grouped: dict[tuple[str, str], list[LegacyFileValidationSummary]] = {}
    ordered_keys: list[tuple[str, str]] = []
    for summary in file_summaries:
        key = (summary.subject_type, summary.level)
        if key not in grouped:
            grouped[key] = []
            ordered_keys.append(key)
        grouped[key].append(summary)

    group_summaries: list[LegacyValidationGroupSummary] = []
    for subject_type, level in ordered_keys:
        items = grouped[(subject_type, level)]
        row_count = sum(item.row_count for item in items)
        matched_rows = sum(item.matched_rows for item in items)
        group_summaries.append(
            LegacyValidationGroupSummary(
                subject_type=subject_type,
                level=level,
                file_count=len(items),
                row_count=row_count,
                matched_rows=matched_rows,
                mismatched_rows=row_count - matched_rows,
                match_rate=_match_rate(matched_rows, row_count),
                matches=all(item.matches for item in items),
                filenames=[item.filename for item in items],
                fields_with_differences=_unique_in_order(
                    field_name
                    for item in items
                    for field_name in item.fields_with_differences
                ),
            )
        )
    return group_summaries


def _build_period_summaries(
    file_summaries: Iterable[LegacyFileValidationSummary],
) -> list[LegacyValidationPeriodSummary]:
    grouped: dict[int | None, list[LegacyFileValidationSummary]] = {}
    ordered_periods: list[int | None] = []
    for summary in file_summaries:
        for period in summary.compared_periods:
            if period not in grouped:
                grouped[period] = []
                ordered_periods.append(period)
            grouped[period].append(summary)

    period_summaries: list[LegacyValidationPeriodSummary] = []
    for period in ordered_periods:
        items = grouped[period]
        mismatched_rows = sum(
            1
            for item in items
            if period in item.periods_with_differences
        )
        row_count = len(items)
        matched_rows = row_count - mismatched_rows
        period_summaries.append(
            LegacyValidationPeriodSummary(
                global_period=period,
                file_count=len(_unique_in_order(item.filename for item in items)),
                row_count=row_count,
                matched_rows=matched_rows,
                mismatched_rows=mismatched_rows,
                match_rate=_match_rate(matched_rows, row_count),
                matches=mismatched_rows == 0,
                filenames=_unique_in_order(item.filename for item in items),
                fields_with_differences=_unique_in_order(
                    deviation.field_name
                    for item in items
                    for deviation in item.field_deviations
                    if deviation.global_period == period
                ),
            )
        )
    return period_summaries


def _build_deviation_index(
    file_summaries: Iterable[LegacyFileValidationSummary],
) -> list[LegacyValidationDeviationRecord]:
    return [
        LegacyValidationDeviationRecord(
            filename=summary.filename,
            subject_type=summary.subject_type,
            level=summary.level,
            selector_kind=summary.selector_kind,
            selector_value=summary.selector_value,
            global_period=deviation.global_period,
            field_name=deviation.field_name,
            actual=deviation.actual,
            expected=deviation.expected,
        )
        for summary in file_summaries
        for deviation in summary.field_deviations
    ]


def build_legacy_file_validation_summary(
    comparison: LegacyWindowComparison,
) -> LegacyFileValidationSummary:
    filename = comparison.export_path.name
    row_count = len(comparison.row_comparisons)
    matched_rows = sum(1 for row in comparison.row_comparisons if row.matches)
    compared_periods = [row.global_period for row in comparison.row_comparisons]
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
    field_summaries = _build_field_deviation_summaries(field_deviations)

    return LegacyFileValidationSummary(
        filename=filename,
        subject_type="insurer",
        level="",
        selector_kind="",
        selector_value=None,
        export_path=comparison.export_path,
        legacy_path=comparison.legacy_path,
        start_period=comparison.start_period,
        end_period=comparison.end_period,
        matches=comparison.matches,
        row_count=row_count,
        matched_rows=matched_rows,
        mismatched_rows=row_count - matched_rows,
        match_rate=_match_rate(matched_rows, row_count),
        compared_periods=compared_periods,
        periods_with_differences=periods_with_differences,
        fields_with_differences=fields_with_differences,
        field_deviations=field_deviations,
        field_summaries=field_summaries,
    )


def build_legacy_table_validation_summary(
    comparison: LegacyTableComparison,
) -> LegacyFileValidationSummary:
    row_count = len(comparison.row_comparisons)
    matched_rows = sum(1 for row in comparison.row_comparisons if row.matches)
    global_periods: list[int | None] = []
    field_deviations: list[LegacyFieldDeviation] = []

    for row in comparison.row_comparisons:
        global_period = _global_period_from_row_comparison(row)
        global_periods.append(global_period)
        for field in row.field_comparisons:
            if field.matches:
                continue
            field_deviations.append(
                LegacyFieldDeviation(
                    filename=comparison.filename,
                    global_period=global_period,
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
    field_summaries = _build_field_deviation_summaries(field_deviations)
    numeric_periods = [period for period in global_periods if period is not None]

    return LegacyFileValidationSummary(
        filename=comparison.filename,
        subject_type=comparison.subject_type,
        level=comparison.level,
        selector_kind=comparison.selector_kind,
        selector_value=comparison.selector_value,
        export_path=Path(comparison.filename),
        legacy_path=None,
        start_period=min(numeric_periods) if numeric_periods else 0,
        end_period=max(numeric_periods) if numeric_periods else 0,
        matches=comparison.matches,
        row_count=row_count,
        matched_rows=matched_rows,
        mismatched_rows=row_count - matched_rows,
        match_rate=_match_rate(matched_rows, row_count),
        compared_periods=global_periods,
        periods_with_differences=periods_with_differences,
        fields_with_differences=fields_with_differences,
        field_deviations=field_deviations,
        field_summaries=field_summaries,
    )


def _global_period_from_row_comparison(row_comparison) -> int | None:
    global_period = getattr(row_comparison, "global_period", None)
    if global_period is not None:
        return int(global_period)

    for field in row_comparison.field_comparisons:
        if field.name != "global_period":
            continue
        try:
            return int(field.actual)
        except (TypeError, ValueError):
            try:
                return int(field.expected)
            except (TypeError, ValueError):
                return None
    return None


def build_legacy_validation_report(
    comparisons: Iterable[LegacyWindowComparison],
) -> LegacyValidationReport:
    file_summaries = [
        build_legacy_file_validation_summary(comparison)
        for comparison in comparisons
    ]
    return _build_report_from_summaries(file_summaries)


def build_legacy_validation_report_from_table_comparisons(
    comparisons: Iterable[LegacyTableComparison],
) -> LegacyValidationReport:
    file_summaries = [
        build_legacy_table_validation_summary(comparison)
        for comparison in comparisons
    ]
    return _build_report_from_summaries(file_summaries)


def build_legacy_validation_report_from_multi_period_comparison(
    comparison: MultiPeriodLegacyComparison,
) -> LegacyValidationReport:
    return build_legacy_validation_report_from_table_comparisons(comparison.table_comparisons)


def _build_report_from_summaries(
    file_summaries: list[LegacyFileValidationSummary],
) -> LegacyValidationReport:
    total_rows = sum(summary.row_count for summary in file_summaries)
    matched_rows = sum(summary.matched_rows for summary in file_summaries)
    group_summaries = _build_group_summaries(file_summaries)
    period_summaries = _build_period_summaries(file_summaries)
    deviation_index = _build_deviation_index(file_summaries)

    return LegacyValidationReport(
        matches=bool(file_summaries) and all(summary.matches for summary in file_summaries),
        total_files=len(file_summaries),
        total_rows=total_rows,
        matched_rows=matched_rows,
        mismatched_rows=total_rows - matched_rows,
        match_rate=_match_rate(matched_rows, total_rows),
        file_summaries=file_summaries,
        field_summaries=[
            field_summary
            for summary in file_summaries
            for field_summary in summary.field_summaries
        ],
        group_summaries=group_summaries,
        period_summaries=period_summaries,
        deviation_index=deviation_index,
    )


def _field_summary_to_dict(summary: LegacyFieldDeviationSummary) -> dict:
    return {
        "filename": summary.filename,
        "field_name": summary.field_name,
        "deviation_count": summary.deviation_count,
        "periods_with_differences": summary.periods_with_differences,
        "numeric_deviation_count": summary.numeric_deviation_count,
        "max_abs_delta": summary.max_abs_delta,
    }


def _group_summary_to_dict(summary: LegacyValidationGroupSummary) -> dict:
    return {
        "subject_type": summary.subject_type,
        "level": summary.level,
        "file_count": summary.file_count,
        "row_count": summary.row_count,
        "matched_rows": summary.matched_rows,
        "mismatched_rows": summary.mismatched_rows,
        "match_rate": summary.match_rate,
        "matches": summary.matches,
        "filenames": summary.filenames,
        "fields_with_differences": summary.fields_with_differences,
    }


def _period_summary_to_dict(summary: LegacyValidationPeriodSummary) -> dict:
    return {
        "global_period": summary.global_period,
        "file_count": summary.file_count,
        "row_count": summary.row_count,
        "matched_rows": summary.matched_rows,
        "mismatched_rows": summary.mismatched_rows,
        "match_rate": summary.match_rate,
        "matches": summary.matches,
        "filenames": summary.filenames,
        "fields_with_differences": summary.fields_with_differences,
    }


def _deviation_record_to_dict(record: LegacyValidationDeviationRecord) -> dict:
    return {
        "filename": record.filename,
        "subject_type": record.subject_type,
        "level": record.level,
        "selector_kind": record.selector_kind,
        "selector_value": record.selector_value,
        "global_period": record.global_period,
        "field_name": record.field_name,
        "actual": record.actual,
        "expected": record.expected,
    }


def legacy_validation_report_to_dict(report: LegacyValidationReport) -> dict:
    return {
        "matches": report.matches,
        "total_files": report.total_files,
        "total_rows": report.total_rows,
        "matched_rows": report.matched_rows,
        "mismatched_rows": report.mismatched_rows,
        "match_rate": report.match_rate,
        "field_summaries": [
            _field_summary_to_dict(summary)
            for summary in report.field_summaries
        ],
        "group_summaries": [
            _group_summary_to_dict(summary)
            for summary in report.group_summaries
        ],
        "period_summaries": [
            _period_summary_to_dict(summary)
            for summary in report.period_summaries
        ],
        "deviation_index": [
            _deviation_record_to_dict(record)
            for record in report.deviation_index
        ],
        "files": [
            {
                "filename": summary.filename,
                "subject_type": summary.subject_type,
                "level": summary.level,
                "selector_kind": summary.selector_kind,
                "selector_value": summary.selector_value,
                "export_path": str(summary.export_path),
                "legacy_path": None if summary.legacy_path is None else str(summary.legacy_path),
                "start_period": summary.start_period,
                "end_period": summary.end_period,
                "matches": summary.matches,
                "row_count": summary.row_count,
                "matched_rows": summary.matched_rows,
                "mismatched_rows": summary.mismatched_rows,
                "match_rate": summary.match_rate,
                "compared_periods": summary.compared_periods,
                "periods_with_differences": summary.periods_with_differences,
                "fields_with_differences": summary.fields_with_differences,
                "field_summaries": [
                    _field_summary_to_dict(field_summary)
                    for field_summary in summary.field_summaries
                ],
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
                "subject_type",
                "level",
                "selector_kind",
                "selector_value",
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
                "field_summary_count",
            ],
        )
        writer.writeheader()
        for summary in report.file_summaries:
            writer.writerow(
                {
                    "filename": summary.filename,
                    "subject_type": summary.subject_type,
                    "level": summary.level,
                    "selector_kind": summary.selector_kind,
                    "selector_value": "" if summary.selector_value is None else summary.selector_value,
                    "legacy_path": "" if summary.legacy_path is None else str(summary.legacy_path),
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
                    "field_summary_count": len(summary.field_summaries),
                }
            )
    return output_path


def write_legacy_validation_field_summary_csv(
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
                "field_name",
                "deviation_count",
                "numeric_deviation_count",
                "max_abs_delta",
                "periods_with_differences",
            ],
        )
        writer.writeheader()
        for summary in report.field_summaries:
            writer.writerow(
                {
                    "filename": summary.filename,
                    "field_name": summary.field_name,
                    "deviation_count": summary.deviation_count,
                    "numeric_deviation_count": summary.numeric_deviation_count,
                    "max_abs_delta": "" if summary.max_abs_delta is None else f"{summary.max_abs_delta:.6f}",
                    "periods_with_differences": ";".join(
                        "" if period is None else str(period)
                        for period in summary.periods_with_differences
                    ),
                }
            )
    return output_path


def write_legacy_validation_group_summary_csv(
    report: LegacyValidationReport,
    path: str | Path,
) -> Path:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "subject_type",
                "level",
                "file_count",
                "row_count",
                "matched_rows",
                "mismatched_rows",
                "match_rate",
                "matches",
                "filenames",
                "fields_with_differences",
            ],
        )
        writer.writeheader()
        for summary in report.group_summaries:
            writer.writerow(
                {
                    "subject_type": summary.subject_type,
                    "level": summary.level,
                    "file_count": summary.file_count,
                    "row_count": summary.row_count,
                    "matched_rows": summary.matched_rows,
                    "mismatched_rows": summary.mismatched_rows,
                    "match_rate": f"{summary.match_rate:.6f}",
                    "matches": summary.matches,
                    "filenames": ";".join(summary.filenames),
                    "fields_with_differences": ";".join(summary.fields_with_differences),
                }
            )
    return output_path


def write_legacy_validation_period_summary_csv(
    report: LegacyValidationReport,
    path: str | Path,
) -> Path:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "global_period",
                "file_count",
                "row_count",
                "matched_rows",
                "mismatched_rows",
                "match_rate",
                "matches",
                "filenames",
                "fields_with_differences",
            ],
        )
        writer.writeheader()
        for summary in report.period_summaries:
            writer.writerow(
                {
                    "global_period": "" if summary.global_period is None else summary.global_period,
                    "file_count": summary.file_count,
                    "row_count": summary.row_count,
                    "matched_rows": summary.matched_rows,
                    "mismatched_rows": summary.mismatched_rows,
                    "match_rate": f"{summary.match_rate:.6f}",
                    "matches": summary.matches,
                    "filenames": ";".join(summary.filenames),
                    "fields_with_differences": ";".join(summary.fields_with_differences),
                }
            )
    return output_path


def write_legacy_validation_deviation_index_csv(
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
                "subject_type",
                "level",
                "selector_kind",
                "selector_value",
                "global_period",
                "field_name",
                "actual",
                "expected",
            ],
        )
        writer.writeheader()
        for record in report.deviation_index:
            writer.writerow(
                {
                    "filename": record.filename,
                    "subject_type": record.subject_type,
                    "level": record.level,
                    "selector_kind": record.selector_kind,
                    "selector_value": "" if record.selector_value is None else record.selector_value,
                    "global_period": "" if record.global_period is None else record.global_period,
                    "field_name": record.field_name,
                    "actual": record.actual,
                    "expected": record.expected,
                }
            )
    return output_path
