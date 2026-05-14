from dataclasses import dataclass

from ims.engine.context import SimulationContext
from ims.model.agrsich_export import ExportTable
from ims.model.agrsich_export import build_agrsich_export_tables
from ims.model.agrsich_service import collect_extended_agrsich_records
from ims.model.entities import BAV, Insurer, Policyholder
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
class AgrsichPeriodState:
    context: SimulationContext
    bav: BAV
    insurers: list[Insurer]
    policyholders: list[Policyholder]


@dataclass(slots=True)
class LegacyTableComparison:
    filename: str
    subject_type: str
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


def _table_key(table: ExportTable) -> tuple[str, str, str, str, int | str | None]:
    return (
        table.spec.filename,
        table.spec.subject_type,
        table.spec.level,
        table.spec.selector_kind,
        table.spec.selector_value,
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


def build_multi_period_agrsich_export_tables(period_states: list[AgrsichPeriodState]) -> list[ExportTable]:
    tables_by_key: dict[tuple[str, str, str, str, int | str | None], ExportTable] = {}
    table_order: list[tuple[str, str, str, str, int | str | None]] = []

    for period_state in period_states:
        result = collect_extended_agrsich_records(
            period_state.context,
            period_state.bav,
            period_state.insurers,
            period_state.policyholders,
        )
        single_period_tables = build_agrsich_export_tables(period_state.context, result)
        for table in single_period_tables:
            key = _table_key(table)
            if key not in tables_by_key:
                tables_by_key[key] = ExportTable(spec=table.spec, header=table.header, rows=[])
                table_order.append(key)
            tables_by_key[key].rows.extend(table.rows)

    return [tables_by_key[key] for key in table_order]


def compare_insurer_export_table_to_legacy(
    export_table: ExportTable,
    legacy_table: LegacyInsurerTable,
    *,
    tolerance: float = 0.05,
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

    return LegacyTableComparison(
        filename=export_table.spec.filename,
        subject_type="insurer",
        matches=bool(row_comparisons) and all(comparison.matches for comparison in row_comparisons),
        row_comparisons=row_comparisons,
    )


def compare_policyholder_export_table_to_legacy(
    export_table: ExportTable,
    legacy_table: LegacyPolicyholderTable,
    *,
    tolerance: float = 0.05,
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

    return LegacyTableComparison(
        filename=export_table.spec.filename,
        subject_type="policyholder",
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
