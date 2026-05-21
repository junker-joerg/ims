from dataclasses import dataclass

from ims.model.agrsich_export import ExportTable
from ims.model.legacy_agrsich_reference import (
    LegacyComparison,
    LegacyFieldComparison,
    LegacyInsurerTable,
    compare_export_record_to_legacy_row,
    extract_legacy_row,
)
from ims.model.legacy_vn_reference import (
    LegacyPolicyholderComparison,
    LegacyPolicyholderFieldComparison,
    LegacyPolicyholderTable,
    compare_policyholder_export_record_to_legacy_row,
    extract_legacy_policyholder_row,
)


@dataclass(slots=True)
class LegacyTableComparison:
    filename: str
    subject_type: str
    level: str
    selector_kind: str
    selector_value: int | str | None
    matches: bool
    row_comparisons: list[LegacyComparison | LegacyPolicyholderComparison]


@dataclass(slots=True)
class MultiPeriodLegacyComparison:
    matches: bool
    table_comparisons: list[LegacyTableComparison]


def _single_row_table(table: ExportTable, row_index: int) -> ExportTable:
    return ExportTable(
        spec=table.spec,
        header=table.header,
        rows=[table.rows[row_index]],
    )


def _missing_insurer_row_comparison(global_period: int) -> LegacyComparison:
    return LegacyComparison(
        matches=False,
        field_comparisons=[
            LegacyFieldComparison(
                name="global_period",
                actual=global_period,
                expected="missing legacy row",
                matches=False,
            )
        ],
    )


def _missing_policyholder_row_comparison(global_period: int) -> LegacyPolicyholderComparison:
    return LegacyPolicyholderComparison(
        matches=False,
        field_comparisons=[
            LegacyPolicyholderFieldComparison(
                name="global_period",
                actual=global_period,
                expected="missing legacy row",
                matches=False,
            )
        ],
    )


def _missing_insurer_export_row_comparison(global_period: int) -> LegacyComparison:
    return LegacyComparison(
        matches=False,
        field_comparisons=[
            LegacyFieldComparison(
                name="global_period",
                actual="missing export row",
                expected=global_period,
                matches=False,
            )
        ],
    )


def _missing_policyholder_export_row_comparison(global_period: int) -> LegacyPolicyholderComparison:
    return LegacyPolicyholderComparison(
        matches=False,
        field_comparisons=[
            LegacyPolicyholderFieldComparison(
                name="global_period",
                actual="missing export row",
                expected=global_period,
                matches=False,
            )
        ],
    )


def _duplicate_insurer_row_comparison(global_period: int) -> LegacyComparison:
    return LegacyComparison(
        matches=False,
        field_comparisons=[
            LegacyFieldComparison(
                name="global_period",
                actual=global_period,
                expected="unique global period",
                matches=False,
            )
        ],
    )


def _duplicate_policyholder_row_comparison(global_period: int) -> LegacyPolicyholderComparison:
    return LegacyPolicyholderComparison(
        matches=False,
        field_comparisons=[
            LegacyPolicyholderFieldComparison(
                name="global_period",
                actual=global_period,
                expected="unique global period",
                matches=False,
            )
        ],
    )


def compare_insurer_export_table_to_legacy(
    export_table: ExportTable,
    legacy_table: LegacyInsurerTable,
    *,
    tolerance: float = 0.05,
    require_complete_legacy_periods: bool = False,
) -> LegacyTableComparison:
    row_comparisons: list[LegacyComparison | LegacyPolicyholderComparison] = []
    seen_global_periods: set[int] = set()
    for index, row in enumerate(export_table.rows):
        global_period = int(row.values[0])
        if global_period in seen_global_periods:
            row_comparisons.append(_duplicate_insurer_row_comparison(global_period))
            continue
        seen_global_periods.add(global_period)

        legacy_row = extract_legacy_row(legacy_table, global_period)
        if legacy_row is None:
            row_comparisons.append(_missing_insurer_row_comparison(global_period))
            continue
        row_comparisons.append(
            compare_export_record_to_legacy_row(
                _single_row_table(export_table, index),
                legacy_row,
                tolerance=tolerance,
            )
        )

    if require_complete_legacy_periods:
        for row in legacy_table.rows:
            if row.global_period not in seen_global_periods:
                row_comparisons.append(_missing_insurer_export_row_comparison(row.global_period))

    return LegacyTableComparison(
        filename=export_table.spec.filename,
        subject_type="insurer",
        level=export_table.spec.level,
        selector_kind=export_table.spec.selector_kind,
        selector_value=export_table.spec.selector_value,
        matches=bool(row_comparisons) and all(comparison.matches for comparison in row_comparisons),
        row_comparisons=row_comparisons,
    )


def compare_policyholder_export_table_to_legacy(
    export_table: ExportTable,
    legacy_table: LegacyPolicyholderTable,
    *,
    tolerance: float = 0.05,
    require_complete_legacy_periods: bool = False,
) -> LegacyTableComparison:
    row_comparisons: list[LegacyComparison | LegacyPolicyholderComparison] = []
    seen_global_periods: set[int] = set()
    for index, row in enumerate(export_table.rows):
        global_period = int(row.values[0])
        if global_period in seen_global_periods:
            row_comparisons.append(_duplicate_policyholder_row_comparison(global_period))
            continue
        seen_global_periods.add(global_period)

        legacy_row = extract_legacy_policyholder_row(legacy_table, global_period)
        if legacy_row is None:
            row_comparisons.append(_missing_policyholder_row_comparison(global_period))
            continue
        row_comparisons.append(
            compare_policyholder_export_record_to_legacy_row(
                _single_row_table(export_table, index),
                legacy_row,
                tolerance=tolerance,
            )
        )

    if require_complete_legacy_periods:
        for row in legacy_table.rows:
            if row.global_period not in seen_global_periods:
                row_comparisons.append(_missing_policyholder_export_row_comparison(row.global_period))

    return LegacyTableComparison(
        filename=export_table.spec.filename,
        subject_type="policyholder",
        level=export_table.spec.level,
        selector_kind=export_table.spec.selector_kind,
        selector_value=export_table.spec.selector_value,
        matches=bool(row_comparisons) and all(comparison.matches for comparison in row_comparisons),
        row_comparisons=row_comparisons,
    )


def build_multi_period_legacy_comparison(
    table_comparisons: list[LegacyTableComparison],
) -> MultiPeriodLegacyComparison:
    return MultiPeriodLegacyComparison(
        matches=bool(table_comparisons) and all(comparison.matches for comparison in table_comparisons),
        table_comparisons=table_comparisons,
    )
