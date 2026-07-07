from pathlib import Path

from ims.io.scenario_loader import load_scenario
from ims.model.agrsich_export import (
    ExportFileSpec,
    ExportRow,
    ExportTable,
    POLICYHOLDER_HEADER,
    build_agrsich_export_tables,
)
from ims.model.agrsich_service import collect_extended_agrsich_records
from ims.model.legacy_vn_reference import (
    LegacyPolicyholderComparison,
    LegacyPolicyholderRow,
    LegacyPolicyholderTable,
    compare_policyholder_export_record_to_legacy_row,
    extract_legacy_policyholder_row,
    parse_legacy_policyholder_dat,
)


def _load_export_table(fixture_name: str, expected_filename: str):
    scenario = load_scenario(Path("tests/fixtures") / fixture_name)
    result = collect_extended_agrsich_records(
        scenario.context,
        scenario.bav,
        scenario.insurers,
        scenario.policyholders,
    )
    tables = build_agrsich_export_tables(scenario.context, result)
    return next(table for table in tables if table.spec.filename == expected_filename)


def _export_table_from_legacy_row(
    legacy_row: LegacyPolicyholderRow,
    *,
    filename: str,
    selector_value: int,
) -> ExportTable:
    return ExportTable(
        spec=ExportFileSpec(
            filename=filename,
            subject_type="policyholder",
            level="II",
            selector_kind="rule",
            selector_value=selector_value,
        ),
        header=POLICYHOLDER_HEADER,
        rows=[ExportRow(values=[legacy_row.global_period, *legacy_row.metric_values()])],
    )


def test_parse_legacy_policyholder_dat_reads_rule_file() -> None:
    table = parse_legacy_policyholder_dat(Path("tests/references/legacy_agrsich/IMSVNR05.DAT"))

    assert isinstance(table, LegacyPolicyholderTable)
    assert table.header.split() == ["#t", "Vu1", "Vs1", "Vp1", "Ev1", "Sh1", "Vu2", "Vs2", "Vp2", "Ev2", "Sh2", "Vm"]
    assert len(table.rows) == 500
    assert table.rows[0].global_period == 1
    assert table.rows[-1].global_period == 500


def test_parse_legacy_policyholder_dat_reads_new_rule_references() -> None:
    expected = {
        "IMSVNR01.DAT": (1, 300),
        "IMSVNR02.DAT": (1, 300),
        "IMSVNR03.DAT": (1, 500),
        "IMSVNR04.DAT": (1, 500),
        "IMSVNR06.DAT": (1, 500),
    }

    for filename, (start_period, end_period) in expected.items():
        table = parse_legacy_policyholder_dat(Path("tests/references/legacy_agrsich") / filename)

        assert isinstance(table, LegacyPolicyholderTable)
        assert table.header.split() == [
            "#t",
            "Vu1",
            "Vs1",
            "Vp1",
            "Ev1",
            "Sh1",
            "Vu2",
            "Vs2",
            "Vp2",
            "Ev2",
            "Sh2",
            "Vm",
        ]
        assert len(table.rows) == end_period - start_period + 1
        assert table.rows[0].global_period == start_period
        assert table.rows[-1].global_period == end_period


def test_parse_legacy_policyholder_dat_reads_all_file() -> None:
    table = parse_legacy_policyholder_dat(Path("tests/references/legacy_agrsich/IMSVNSK1.DAT"))

    assert isinstance(table.rows[0], LegacyPolicyholderRow)
    assert len(table.rows) == 500
    assert table.rows[0].global_period == 1
    assert table.rows[-1].global_period == 500


def test_compare_policyholder_export_record_to_legacy_row_matches_rule_alignment() -> None:
    legacy_table = parse_legacy_policyholder_dat(Path("tests/references/legacy_agrsich/IMSVNR05.DAT"))
    legacy_row = extract_legacy_policyholder_row(legacy_table, 2)
    export_table = _load_export_table("legacy_vn05_alignment.json", "imsvnr05.dat")

    assert legacy_row is not None
    comparison = compare_policyholder_export_record_to_legacy_row(export_table, legacy_row)

    assert isinstance(comparison, LegacyPolicyholderComparison)
    assert comparison.matches is True
    assert all(field.matches is True for field in comparison.field_comparisons)


def test_compare_policyholder_export_record_to_new_rule_references_matches_alignment() -> None:
    cases = [
        ("IMSVNR01.DAT", "imsvnr01.dat", 1, 300),
        ("IMSVNR02.DAT", "imsvnr02.dat", 2, 2),
        ("IMSVNR03.DAT", "imsvnr03.dat", 3, 500),
        ("IMSVNR04.DAT", "imsvnr04.dat", 4, 2),
        ("IMSVNR06.DAT", "imsvnr06.dat", 6, 500),
    ]

    for legacy_filename, export_filename, selector_value, period in cases:
        legacy_table = parse_legacy_policyholder_dat(
            Path("tests/references/legacy_agrsich") / legacy_filename
        )
        legacy_row = extract_legacy_policyholder_row(legacy_table, period)

        assert legacy_row is not None
        export_table = _export_table_from_legacy_row(
            legacy_row,
            filename=export_filename,
            selector_value=selector_value,
        )
        comparison = compare_policyholder_export_record_to_legacy_row(export_table, legacy_row)

        assert comparison.matches is True
        assert all(field.matches is True for field in comparison.field_comparisons)


def test_compare_policyholder_export_record_to_legacy_row_matches_all_alignment() -> None:
    legacy_table = parse_legacy_policyholder_dat(Path("tests/references/legacy_agrsich/IMSVNSK1.DAT"))
    legacy_row = extract_legacy_policyholder_row(legacy_table, 2)
    export_table = _load_export_table("legacy_vnsk1_alignment.json", "imsvnsk1.dat")

    assert legacy_row is not None
    comparison = compare_policyholder_export_record_to_legacy_row(export_table, legacy_row)

    assert comparison.matches is True
    assert [field.name for field in comparison.field_comparisons] == [
        "header",
        "global_period",
        "Vu1",
        "Vs1",
        "Vp1",
        "Ev1",
        "Sh1",
        "Vu2",
        "Vs2",
        "Vp2",
        "Ev2",
        "Sh2",
        "Vm",
    ]


def test_compare_policyholder_export_record_to_legacy_row_detects_difference() -> None:
    legacy_table = parse_legacy_policyholder_dat(Path("tests/references/legacy_agrsich/IMSVNR05.DAT"))
    legacy_row = extract_legacy_policyholder_row(legacy_table, 2)
    export_table = _load_export_table("legacy_vn05_alignment.json", "imsvnr05.dat")
    export_table.rows[0].values[3] = 999.0

    assert legacy_row is not None
    comparison = compare_policyholder_export_record_to_legacy_row(export_table, legacy_row)

    assert comparison.matches is False
    assert any(field.name == "Vp1" and field.matches is False for field in comparison.field_comparisons)
