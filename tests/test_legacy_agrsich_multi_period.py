from pathlib import Path

from ims.model.agrsich_export import (
    INSURER_HEADER,
    POLICYHOLDER_HEADER,
    ExportFileSpec,
    ExportRow,
    ExportTable,
)
from ims.model.legacy_agrsich_multi_period import (
    LegacyTableComparison,
    MultiPeriodLegacyComparison,
    build_multi_period_legacy_comparison,
    compare_insurer_export_table_to_legacy,
    compare_policyholder_export_table_to_legacy,
)
from ims.model.legacy_agrsich_reference import (
    LegacyInsurerTable,
    extract_legacy_row,
    parse_legacy_insurer_dat,
)
from ims.model.legacy_vn_reference import (
    LegacyPolicyholderTable,
    extract_legacy_policyholder_row,
    parse_legacy_policyholder_dat,
)


def _insurer_table_from_legacy_rows(
    legacy_table: LegacyInsurerTable,
    filename: str,
    periods: list[int],
) -> ExportTable:
    rows: list[ExportRow] = []
    for period in periods:
        legacy_row = extract_legacy_row(legacy_table, period)
        assert legacy_row is not None
        rows.append(ExportRow(values=[legacy_row.global_period, *legacy_row.metric_values()]))
    return ExportTable(
        spec=ExportFileSpec(
            filename=filename,
            subject_type="insurer",
            level="I",
            selector_kind="entity",
            selector_value=14,
        ),
        header=INSURER_HEADER,
        rows=rows,
    )


def _policyholder_table_from_legacy_rows(
    legacy_table: LegacyPolicyholderTable,
    filename: str,
    periods: list[int],
) -> ExportTable:
    rows: list[ExportRow] = []
    for period in periods:
        legacy_row = extract_legacy_policyholder_row(legacy_table, period)
        assert legacy_row is not None
        rows.append(ExportRow(values=[legacy_row.global_period, *legacy_row.metric_values()]))
    return ExportTable(
        spec=ExportFileSpec(
            filename=filename,
            subject_type="policyholder",
            level="II",
            selector_kind="rule",
            selector_value=5,
        ),
        header=POLICYHOLDER_HEADER,
        rows=rows,
    )


def test_compare_insurer_export_table_to_legacy_accepts_multiple_periods() -> None:
    legacy_table = parse_legacy_insurer_dat(Path("tests/references/legacy_agrsich/VU14L1.DAT"))
    export_table = _insurer_table_from_legacy_rows(legacy_table, "imsvu014.dat", [1, 2, 3])

    comparison = compare_insurer_export_table_to_legacy(export_table, legacy_table)

    assert isinstance(comparison, LegacyTableComparison)
    assert comparison.matches is True
    assert comparison.filename == "imsvu014.dat"
    assert comparison.subject_type == "insurer"
    assert [row.field_comparisons[1].actual for row in comparison.row_comparisons] == [1, 2, 3]


def test_compare_insurer_export_table_to_legacy_detects_bad_period_row() -> None:
    legacy_table = parse_legacy_insurer_dat(Path("tests/references/legacy_agrsich/VUSK1L4.DAT"))
    export_table = _insurer_table_from_legacy_rows(legacy_table, "imsvusk1.dat", [101, 102, 103])
    export_table.rows[1].values[3] = 999.0

    comparison = compare_insurer_export_table_to_legacy(export_table, legacy_table)

    assert comparison.matches is False
    assert comparison.row_comparisons[0].matches is True
    assert comparison.row_comparisons[1].matches is False
    assert comparison.row_comparisons[2].matches is True


def test_compare_insurer_export_table_to_legacy_rejects_duplicate_periods() -> None:
    legacy_table = parse_legacy_insurer_dat(Path("tests/references/legacy_agrsich/VU14L1.DAT"))
    export_table = _insurer_table_from_legacy_rows(legacy_table, "imsvu014.dat", [1])
    export_table.rows.append(ExportRow(values=list(export_table.rows[0].values)))

    comparison = compare_insurer_export_table_to_legacy(export_table, legacy_table)

    assert comparison.matches is False
    assert comparison.row_comparisons[0].matches is True
    assert comparison.row_comparisons[1].matches is False
    assert comparison.row_comparisons[1].field_comparisons[0].expected == "unique global period"


def test_compare_insurer_export_table_to_legacy_can_require_complete_periods() -> None:
    legacy_table = parse_legacy_insurer_dat(Path("tests/references/legacy_agrsich/VU14L1.DAT"))
    export_table = _insurer_table_from_legacy_rows(legacy_table, "imsvu014.dat", [1])

    comparison = compare_insurer_export_table_to_legacy(
        export_table,
        legacy_table,
        require_complete_legacy_periods=True,
    )

    assert comparison.matches is False
    assert comparison.row_comparisons[0].matches is True
    missing_rows = [row for row in comparison.row_comparisons if not row.matches]
    assert missing_rows
    assert missing_rows[0].field_comparisons[0].actual == "missing export row"
    assert missing_rows[0].field_comparisons[0].expected == 2


def test_compare_policyholder_export_table_to_legacy_accepts_multiple_periods() -> None:
    legacy_table = parse_legacy_policyholder_dat(Path("tests/references/legacy_agrsich/IMSVNR05.DAT"))
    export_table = _policyholder_table_from_legacy_rows(legacy_table, "imsvnr05.dat", [1, 2, 3])

    comparison = compare_policyholder_export_table_to_legacy(export_table, legacy_table)

    assert comparison.matches is True
    assert comparison.filename == "imsvnr05.dat"
    assert comparison.subject_type == "policyholder"
    assert [row.field_comparisons[1].actual for row in comparison.row_comparisons] == [1, 2, 3]


def test_compare_policyholder_export_table_to_legacy_rejects_duplicate_periods() -> None:
    legacy_table = parse_legacy_policyholder_dat(Path("tests/references/legacy_agrsich/IMSVNR05.DAT"))
    export_table = _policyholder_table_from_legacy_rows(legacy_table, "imsvnr05.dat", [1])
    export_table.rows.append(ExportRow(values=list(export_table.rows[0].values)))

    comparison = compare_policyholder_export_table_to_legacy(export_table, legacy_table)

    assert comparison.matches is False
    assert comparison.row_comparisons[0].matches is True
    assert comparison.row_comparisons[1].matches is False
    assert comparison.row_comparisons[1].field_comparisons[0].expected == "unique global period"


def test_compare_policyholder_export_table_to_legacy_can_require_complete_periods() -> None:
    legacy_table = parse_legacy_policyholder_dat(Path("tests/references/legacy_agrsich/IMSVNR05.DAT"))
    export_table = _policyholder_table_from_legacy_rows(legacy_table, "imsvnr05.dat", [1])

    comparison = compare_policyholder_export_table_to_legacy(
        export_table,
        legacy_table,
        require_complete_legacy_periods=True,
    )

    assert comparison.matches is False
    assert comparison.row_comparisons[0].matches is True
    missing_rows = [row for row in comparison.row_comparisons if not row.matches]
    assert missing_rows
    assert missing_rows[0].field_comparisons[0].actual == "missing export row"
    assert missing_rows[0].field_comparisons[0].expected == 2


def test_multi_period_legacy_comparison_combines_vu_and_vn_tables() -> None:
    insurer_legacy = parse_legacy_insurer_dat(Path("tests/references/legacy_agrsich/VUSK1L4.DAT"))
    policyholder_legacy = parse_legacy_policyholder_dat(Path("tests/references/legacy_agrsich/IMSVNSK1.DAT"))
    insurer_export = _insurer_table_from_legacy_rows(insurer_legacy, "imsvusk1.dat", [101, 102])
    policyholder_export = _policyholder_table_from_legacy_rows(policyholder_legacy, "imsvnsk1.dat", [1, 2])

    comparison = build_multi_period_legacy_comparison([
        compare_insurer_export_table_to_legacy(insurer_export, insurer_legacy),
        compare_policyholder_export_table_to_legacy(policyholder_export, policyholder_legacy),
    ])

    assert isinstance(comparison, MultiPeriodLegacyComparison)
    assert comparison.matches is True
    assert [table.filename for table in comparison.table_comparisons] == ["imsvusk1.dat", "imsvnsk1.dat"]


def test_multi_period_legacy_comparison_detects_missing_legacy_period() -> None:
    legacy_table = parse_legacy_policyholder_dat(Path("tests/references/legacy_agrsich/IMSVNSK1.DAT"))
    export_table = _policyholder_table_from_legacy_rows(legacy_table, "imsvnsk1.dat", [1])
    export_table.rows.append(ExportRow(values=[9999, *export_table.rows[0].values[1:]]))

    table_comparison = compare_policyholder_export_table_to_legacy(export_table, legacy_table)
    comparison = build_multi_period_legacy_comparison([table_comparison])

    assert comparison.matches is False
    assert table_comparison.row_comparisons[0].matches is True
    assert table_comparison.row_comparisons[1].matches is False
    assert table_comparison.row_comparisons[1].field_comparisons[0].expected == "missing legacy row"
