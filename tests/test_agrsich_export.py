from pathlib import Path

from ims.engine.context import SimulationContext
from ims.model.agrsich_export import (
    INSURER_HEADER,
    POLICYHOLDER_HEADER,
    ExportFileSpec,
    ExportRow,
    ExportTable,
    build_agrsich_export_tables,
    compute_global_period,
)
from ims.model.agrsich_service import collect_extended_agrsich_records
from ims.model.entities import BAV, Insurer, Policyholder


def _build_export_sample() -> tuple[SimulationContext, BAV, list[Insurer], list[Policyholder]]:
    context = SimulationContext(period=2, logtime=0, max_periods=12, run_index=2, rng_seed=123)
    bav = BAV(entity_id=100, name="Basis-BAV")
    insurers = [
        Insurer(entity_id=200, active=True, rule_id=1, rule_class=10, premiums_current=10.0, advertising_current=2.0, reserves_current=50.0, policyholders_current=100.0, claims_count_current=[1, 3], claims_sum_current=[5.0, 15.0]),
        Insurer(entity_id=201, active=True, rule_id=1, rule_class=10, premiums_current=20.0, advertising_current=6.0, reserves_current=70.0, policyholders_current=120.0, claims_count_current=[3, 5], claims_sum_current=[9.0, 21.0]),
        Insurer(entity_id=202, active=True, rule_id=2, rule_class=20, premiums_current=40.0, advertising_current=10.0, reserves_current=90.0, policyholders_current=80.0, claims_count_current=[5, 7], claims_sum_current=[13.0, 25.0]),
        Insurer(entity_id=203, active=False, rule_id=2, rule_class=20, premiums_current=999.0, advertising_current=999.0, reserves_current=999.0, policyholders_current=999.0, claims_count_current=[9, 9], claims_sum_current=[99.0, 99.0]),
    ]
    policyholders = [
        Policyholder(entity_id=300, active=True, rule_id=5, rule_class=50, insured_current=0.2, chosen_insurer_current=200, paid_premium_current=[1.0, 2.0], self_damage_current=[0.1, 0.2], claim_sum_current=[0.3, 0.4], end_wealth_current=10.0),
        Policyholder(entity_id=301, active=True, rule_id=5, rule_class=50, insured_current=0.6, chosen_insurer_current=201, paid_premium_current=[3.0, 4.0], self_damage_current=[0.5, 0.6], claim_sum_current=[0.7, 0.8], end_wealth_current=20.0),
        Policyholder(entity_id=302, active=True, rule_id=6, rule_class=60, insured_current=0.8, chosen_insurer_current=201, paid_premium_current=[5.0, 6.0], self_damage_current=[0.9, 1.0], claim_sum_current=[1.1, 1.2], end_wealth_current=30.0),
        Policyholder(entity_id=303, active=False, rule_id=6, rule_class=60, insured_current=9.9, chosen_insurer_current=202, paid_premium_current=[9.0, 9.0], self_damage_current=[9.0, 9.0], claim_sum_current=[9.0, 9.0], end_wealth_current=99.0),
    ]
    return context, bav, insurers, policyholders


def test_compute_global_period_continues_across_runs() -> None:
    assert compute_global_period(SimulationContext(period=2, max_periods=12, run_index=2)) == 26
    assert compute_global_period(SimulationContext(period=3, max_periods=0, run_index=5)) == 3


def test_build_agrsich_export_tables_produces_tables_and_stable_headers() -> None:
    context, bav, insurers, policyholders = _build_export_sample()
    result = collect_extended_agrsich_records(context, bav, insurers, policyholders)

    tables = build_agrsich_export_tables(context, result)

    assert tables
    assert all(isinstance(table, ExportTable) for table in tables)
    assert all(isinstance(table.spec, ExportFileSpec) for table in tables)
    assert all(isinstance(table.rows[0], ExportRow) for table in tables)
    assert any(table.header == INSURER_HEADER for table in tables)
    assert any(table.header == POLICYHOLDER_HEADER for table in tables)


def test_build_agrsich_export_tables_uses_historical_filename_patterns() -> None:
    context, bav, insurers, policyholders = _build_export_sample()
    result = collect_extended_agrsich_records(context, bav, insurers, policyholders)
    tables = build_agrsich_export_tables(context, result)
    filenames = {table.spec.filename for table in tables}

    assert "imsvu200.dat" in filenames
    assert "imsvn300.dat" in filenames
    assert "imsvur01.dat" in filenames
    assert "imsvnr05.dat" in filenames
    assert "imsvuvk10.dat" in filenames
    assert "imsvnvk50.dat" in filenames
    assert "imsvusk1.dat" in filenames
    assert "imsvnsk1.dat" in filenames


def test_export_tables_contain_expected_stage_ii_to_iv_values() -> None:
    context, bav, insurers, policyholders = _build_export_sample()
    result = collect_extended_agrsich_records(context, bav, insurers, policyholders)
    tables = build_agrsich_export_tables(context, result)
    by_filename = {table.spec.filename: table for table in tables}

    insurer_rule_table = by_filename["imsvur01.dat"]
    assert insurer_rule_table.header == INSURER_HEADER
    assert insurer_rule_table.rows[0].values == [26, 15.0, 4.0, 60.0, 110.0, 2.0, 7.0, 15.0, 4.0, 60.0, 110.0, 4.0, 18.0]

    insurer_all_table = by_filename["imsvusk1.dat"]
    assert insurer_all_table.rows[0].values == [26, 70.0 / 3.0, 6.0, 70.0, 100.0, 3.0, 9.0, 70.0 / 3.0, 6.0, 70.0, 100.0, 5.0, 61.0 / 3.0]

    policyholder_rule_table = by_filename["imsvnr05.dat"]
    assert policyholder_rule_table.header == POLICYHOLDER_HEADER
    assert policyholder_rule_table.rows[0].values == [26, 2.0, 0.3, 0.4, 200, 0.5, 3.0, 0.4, 0.4, 200, 0.6000000000000001, 15.0]

    policyholder_all_table = by_filename["imsvnsk1.dat"]
    assert policyholder_all_table.rows[0].values == [26, 3.0, 0.5, (0.2 + 0.6 + 0.8) / 3.0, 201, 0.7000000000000001, 4.0, 0.6, (0.2 + 0.6 + 0.8) / 3.0, 201, 0.8000000000000002, 20.0]


def test_scenario_loader_reads_extended_export_metrics(minimal_scenario_path: Path) -> None:
    from ims.io.scenario_loader import load_scenario

    scenario = load_scenario(minimal_scenario_path)

    assert scenario.insurers[0].claims_count_current == [1, 2]
    assert scenario.insurers[0].claims_sum_current == [5.0, 7.5]
    assert scenario.policyholders[0].paid_premium_current == [1.5, 2.5]
    assert scenario.policyholders[0].self_damage_current == [0.2, 0.4]
    assert scenario.policyholders[0].claim_sum_current == [0.3, 0.7]
    assert scenario.policyholders[0].end_wealth_current == 10.0
