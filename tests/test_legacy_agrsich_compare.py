from pathlib import Path
import json

from ims.io.scenario_loader import load_scenario
from ims.model.agrsich_export import build_agrsich_export_tables
from ims.model.agrsich_service import collect_extended_agrsich_records
from ims.model.legacy_agrsich_reference import (
    LegacyComparison,
    LegacyInsurerRow,
    LegacyInsurerTable,
    compare_export_record_to_legacy_row,
    extract_legacy_row,
    parse_legacy_insurer_dat,
)


def _load_export_table(fixture_name: str, expected_filename: str):
    scenario = load_scenario(Path("tests/fixtures") / fixture_name)
    result = collect_extended_agrsich_records(scenario.context, scenario.bav, scenario.insurers, scenario.policyholders)
    tables = build_agrsich_export_tables(scenario.context, result)
    return next(table for table in tables if table.spec.filename == expected_filename)


def test_parse_legacy_insurer_dat_reads_vu14_file() -> None:
    table = parse_legacy_insurer_dat(Path("tests/references/legacy_agrsich/VU14L1.DAT"))

    assert isinstance(table, LegacyInsurerTable)
    assert table.header.split() == ["#t", "Pr1", "Wa1", "Rs1", "Vn1", "Sa1", "Sh1", "Pr2", "Wa2", "Rs2", "Vn2", "Sa2", "Sh2"]
    assert len(table.rows) == 100
    assert table.rows[0].global_period == 1
    assert table.rows[-1].global_period == 100


def test_parse_legacy_insurer_dat_reads_vusk1_file() -> None:
    table = parse_legacy_insurer_dat(Path("tests/references/legacy_agrsich/VUSK1L4.DAT"))

    assert isinstance(table.rows[0], LegacyInsurerRow)
    assert len(table.rows) == 100
    assert table.rows[0].global_period == 101
    assert table.rows[-1].global_period == 200


def test_compare_export_record_to_legacy_row_matches_vu14_alignment() -> None:
    legacy_table = parse_legacy_insurer_dat(Path("tests/references/legacy_agrsich/VU14L1.DAT"))
    legacy_row = extract_legacy_row(legacy_table, 2)
    export_table = _load_export_table("legacy_vu14_alignment.json", "imsvu014.dat")

    assert legacy_row is not None
    comparison = compare_export_record_to_legacy_row(export_table, legacy_row)

    assert isinstance(comparison, LegacyComparison)
    assert comparison.matches is True
    assert all(field.matches is True for field in comparison.field_comparisons)


def test_compare_export_record_to_legacy_row_matches_vusk1_alignment() -> None:
    legacy_table = parse_legacy_insurer_dat(Path("tests/references/legacy_agrsich/VUSK1L4.DAT"))
    legacy_row = extract_legacy_row(legacy_table, 102)
    export_table = _load_export_table("legacy_vusk1_alignment.json", "imsvusk1.dat")

    assert legacy_row is not None
    comparison = compare_export_record_to_legacy_row(export_table, legacy_row)

    assert comparison.matches is True
    assert [field.name for field in comparison.field_comparisons] == [
        "header",
        "global_period",
        "Pr1",
        "Wa1",
        "Rs1",
        "Vn1",
        "Sa1",
        "Sh1",
        "Pr2",
        "Wa2",
        "Rs2",
        "Vn2",
        "Sa2",
        "Sh2",
    ]


def test_compare_export_record_to_legacy_row_detects_difference() -> None:
    legacy_table = parse_legacy_insurer_dat(Path("tests/references/legacy_agrsich/VU14L1.DAT"))
    legacy_row = extract_legacy_row(legacy_table, 2)
    export_table = _load_export_table("legacy_vu14_alignment.json", "imsvu014.dat")
    export_table.rows[0].values[3] = 999.0

    assert legacy_row is not None
    comparison = compare_export_record_to_legacy_row(export_table, legacy_row)

    assert comparison.matches is False
    assert any(field.name == "Rs1" and field.matches is False for field in comparison.field_comparisons)


def test_scenario_loader_duplicates_scalar_reserves_current_for_backward_compatibility(tmp_path: Path) -> None:
    scenario_path = tmp_path / "scalar_reserves.json"
    scenario_path.write_text(json.dumps({
        "context": {"period": 0, "logtime": 0, "max_periods": 12, "run_index": 0, "rng_seed": 1},
        "bav": {"entity_id": 1, "name": "Compat-BAV"},
        "insurers": [{"entity_id": 14, "name": "Compat-VU", "reserves_current": 33.5}],
        "policyholders": []
    }), encoding="utf-8")

    scenario = load_scenario(scenario_path)

    assert scenario.insurers[0].reserves_current == [33.5, 33.5]
