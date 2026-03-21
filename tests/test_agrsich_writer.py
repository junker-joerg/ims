from pathlib import Path

from ims.engine.context import SimulationContext
from ims.model.agrsich_export import build_agrsich_export_tables
from ims.model.agrsich_service import collect_extended_agrsich_records
from ims.model.agrsich_writer import (
    ComparisonResult,
    FileComparison,
    compare_export_files_to_reference,
    write_agrsich_export_tables,
)
from ims.model.entities import BAV, Insurer, Policyholder


REFERENCE_FILENAMES = [
    "imsvur02.dat",
    "imsvnr11.dat",
    "imsvusk1.dat",
    "imsvnsk1.dat",
]


def _build_reference_sample() -> tuple[SimulationContext, BAV, list[Insurer], list[Policyholder]]:
    context = SimulationContext(period=2, logtime=0, max_periods=12, run_index=1, rng_seed=123)
    bav = BAV(entity_id=100, name="Basis-BAV")
    insurers = [
        Insurer(entity_id=200, active=True, rule_id=2, rule_class=1, premiums_current=10.0, advertising_current=2.0, reserves_current=50.0, policyholders_current=100.0, claims_count_current=[1, 2], claims_sum_current=[5.0, 10.0]),
        Insurer(entity_id=201, active=True, rule_id=2, rule_class=1, premiums_current=20.0, advertising_current=4.0, reserves_current=70.0, policyholders_current=120.0, claims_count_current=[3, 4], claims_sum_current=[7.0, 12.0]),
        Insurer(entity_id=202, active=True, rule_id=3, rule_class=2, premiums_current=30.0, advertising_current=6.0, reserves_current=90.0, policyholders_current=140.0, claims_count_current=[5, 6], claims_sum_current=[9.0, 14.0]),
    ]
    policyholders = [
        Policyholder(entity_id=300, active=True, rule_id=11, rule_class=5, insured_current=0.2, chosen_insurer_current=200, paid_premium_current=[1.0, 2.0], self_damage_current=[0.1, 0.2], claim_sum_current=[0.3, 0.4], end_wealth_current=10.0),
        Policyholder(entity_id=301, active=True, rule_id=11, rule_class=5, insured_current=0.6, chosen_insurer_current=201, paid_premium_current=[3.0, 4.0], self_damage_current=[0.5, 0.6], claim_sum_current=[0.7, 0.8], end_wealth_current=20.0),
        Policyholder(entity_id=302, active=True, rule_id=12, rule_class=6, insured_current=0.8, chosen_insurer_current=201, paid_premium_current=[5.0, 6.0], self_damage_current=[0.9, 1.0], claim_sum_current=[1.1, 1.2], end_wealth_current=30.0),
    ]
    return context, bav, insurers, policyholders


def _build_reference_tables():
    context, bav, insurers, policyholders = _build_reference_sample()
    result = collect_extended_agrsich_records(context, bav, insurers, policyholders)
    tables = build_agrsich_export_tables(context, result)
    selected = [table for table in tables if table.spec.filename in REFERENCE_FILENAMES]
    return context, selected


def test_write_agrsich_export_tables_writes_files(tmp_path: Path) -> None:
    _, tables = _build_reference_tables()

    written = write_agrsich_export_tables(tmp_path, tables)

    assert sorted(path.name for path in written) == sorted(REFERENCE_FILENAMES)
    for filename in REFERENCE_FILENAMES:
        assert (tmp_path / filename).exists()


def test_write_agrsich_export_tables_writes_header_only_once_and_appends_rows(tmp_path: Path) -> None:
    _, tables = _build_reference_tables()

    write_agrsich_export_tables(tmp_path, tables, append=True)
    write_agrsich_export_tables(tmp_path, tables, append=True)

    file_text = (tmp_path / "imsvur02.dat").read_text(encoding="utf-8")
    assert file_text.count("#t Pr1 Wa1 Rs1 Vn1 Sa1 Sh1 Pr2 Wa2 Rs2 Vn2 Sa2 Sh2") == 1
    assert len(file_text.strip().splitlines()) == 3


def test_compare_export_files_to_reference_matches_curated_reference(tmp_path: Path) -> None:
    _, tables = _build_reference_tables()
    reference_dir = Path("tests/references/agrsich")

    write_agrsich_export_tables(tmp_path, tables)
    result = compare_export_files_to_reference(tmp_path, reference_dir, filenames=REFERENCE_FILENAMES)

    assert isinstance(result, ComparisonResult)
    assert result.all_match is True
    assert all(isinstance(comparison, FileComparison) for comparison in result.comparisons)
    assert all(comparison.matches is True for comparison in result.comparisons)


def test_compare_export_files_to_reference_detects_difference(tmp_path: Path) -> None:
    _, tables = _build_reference_tables()
    reference_dir = Path("tests/references/agrsich")

    write_agrsich_export_tables(tmp_path, tables)
    (tmp_path / "imsvur02.dat").write_text("broken\n", encoding="utf-8")

    result = compare_export_files_to_reference(tmp_path, reference_dir, filenames=["imsvur02.dat"])

    assert result.all_match is False
    assert result.comparisons[0].filename == "imsvur02.dat"
    assert result.comparisons[0].matches is False
    assert result.comparisons[0].actual_text == "broken\n"
    assert result.comparisons[0].reference_text.startswith("#t Pr1 Wa1")


def test_compare_export_files_to_reference_detects_missing_reference(tmp_path: Path) -> None:
    _, tables = _build_reference_tables()
    missing_reference_dir = tmp_path / "missing_refs"
    write_agrsich_export_tables(tmp_path, tables)

    result = compare_export_files_to_reference(tmp_path, missing_reference_dir, filenames=["imsvur02.dat"])

    assert result.all_match is False
    assert result.comparisons[0].matches is False
    assert result.comparisons[0].reference_text == ""
