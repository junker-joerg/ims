from pathlib import Path

from ims.engine.context import SimulationContext
from ims.model.agrsich_service import (
    AggregateRecord,
    AgrsichResult,
    collect_basic_agrsich_records,
    refresh_bav_aggregate_state,
)
from ims.model.entities import BAV, Insurer, Policyholder


def _build_agrsich_sample() -> tuple[SimulationContext, BAV, list[Insurer], list[Policyholder]]:
    context = SimulationContext(period=3, logtime=0, max_periods=12, run_index=1, rng_seed=123)
    bav = BAV(entity_id=100, name="Basis-BAV")
    insurers = [
        Insurer(
            entity_id=200,
            active=True,
            rule_id=1,
            rule_class=10,
            premiums_current=10.0,
            advertising_current=2.0,
            reserves_current=50.0,
            policyholders_current=100.0,
        ),
        Insurer(
            entity_id=201,
            active=True,
            rule_id=1,
            rule_class=10,
            premiums_current=20.0,
            advertising_current=6.0,
            reserves_current=70.0,
            policyholders_current=120.0,
        ),
        Insurer(
            entity_id=202,
            active=True,
            rule_id=2,
            rule_class=20,
            premiums_current=40.0,
            advertising_current=10.0,
            reserves_current=90.0,
            policyholders_current=80.0,
        ),
        Insurer(
            entity_id=203,
            active=False,
            rule_id=2,
            rule_class=20,
            premiums_current=999.0,
            advertising_current=999.0,
            reserves_current=999.0,
            policyholders_current=999.0,
        ),
    ]
    policyholders = [
        Policyholder(
            entity_id=300,
            active=True,
            rule_id=5,
            rule_class=50,
            insured_current=0.2,
            chosen_insurer_current=200,
        ),
        Policyholder(
            entity_id=301,
            active=True,
            rule_id=5,
            rule_class=50,
            insured_current=0.6,
            chosen_insurer_current=201,
        ),
        Policyholder(
            entity_id=302,
            active=True,
            rule_id=6,
            rule_class=60,
            insured_current=0.8,
            chosen_insurer_current=201,
        ),
        Policyholder(
            entity_id=303,
            active=False,
            rule_id=6,
            rule_class=60,
            insured_current=1.0,
            chosen_insurer_current=202,
        ),
    ]
    return context, bav, insurers, policyholders


def test_refresh_bav_aggregate_state_writes_ids_and_counts() -> None:
    context, bav, insurers, policyholders = _build_agrsich_sample()

    refresh_bav_aggregate_state(bav, insurers, policyholders, period=context.period)

    aggregate_state = bav.service_state.aggregate_state
    assert aggregate_state.active_insurer_ids_current == [200, 201, 202]
    assert aggregate_state.active_policyholder_ids_current == [300, 301, 302]
    assert aggregate_state.insurer_rule_counts == {1: 2, 2: 1}
    assert aggregate_state.insurer_rule_class_counts == {10: 2, 20: 1}
    assert aggregate_state.policyholder_rule_counts == {5: 2, 6: 1}
    assert aggregate_state.policyholder_rule_class_counts == {50: 2, 60: 1}
    assert aggregate_state.last_agrsich_period == 3


def test_collect_basic_agrsich_records_generates_stage_i_to_iv_records() -> None:
    context, bav, insurers, policyholders = _build_agrsich_sample()

    result = collect_basic_agrsich_records(context, bav, insurers, policyholders)

    assert isinstance(result, AgrsichResult)
    assert all(isinstance(record, AggregateRecord) for record in result.insurer_records)
    assert all(isinstance(record, AggregateRecord) for record in result.policyholder_records)
    assert {record.aggregate_level for record in result.insurer_records} == {"I", "II", "III", "IV"}
    assert {record.aggregate_level for record in result.policyholder_records} == {"I", "II", "III", "IV"}


def test_collect_basic_agrsich_records_insurer_stage_ii_to_iv_use_means() -> None:
    context, bav, insurers, policyholders = _build_agrsich_sample()

    result = collect_basic_agrsich_records(context, bav, insurers, policyholders)
    insurer_records = {(record.aggregate_level, record.aggregate_key): record for record in result.insurer_records}

    stage_ii_rule_1 = insurer_records[("II", 1)]
    assert stage_ii_rule_1.metrics["premium_1"] == 15.0
    assert stage_ii_rule_1.metrics["advertising_1"] == 4.0
    assert stage_ii_rule_1.metrics["reserves"] == 60.0
    assert stage_ii_rule_1.metrics["policyholders_1"] == 110.0

    stage_iii_class_10 = insurer_records[("III", 10)]
    assert stage_iii_class_10.metrics["premium_2"] == 15.0
    assert stage_iii_class_10.metrics["advertising_2"] == 4.0

    stage_iv_all = insurer_records[("IV", "all")]
    assert stage_iv_all.metrics["premium_1"] == 70.0 / 3.0
    assert stage_iv_all.metrics["advertising_1"] == 6.0
    assert stage_iv_all.metrics["reserves"] == 70.0
    assert stage_iv_all.metrics["policyholders_2"] == 100.0


def test_collect_basic_agrsich_records_policyholder_uses_mean_and_mode_with_tiebreak() -> None:
    context, bav, insurers, policyholders = _build_agrsich_sample()
    policyholders[0].chosen_insurer_current = 200
    policyholders[1].chosen_insurer_current = 201

    result = collect_basic_agrsich_records(context, bav, insurers, policyholders)
    policyholder_records = {(record.aggregate_level, record.aggregate_key): record for record in result.policyholder_records}

    stage_ii_rule_5 = policyholder_records[("II", 5)]
    assert stage_ii_rule_5.metrics["coverage_1"] == 0.4
    assert stage_ii_rule_5.metrics["coverage_2"] == 0.4
    assert stage_ii_rule_5.metrics["chosen_insurer_1"] == 200
    assert stage_ii_rule_5.metrics["chosen_insurer_2"] == 200

    stage_iv_all = policyholder_records[("IV", "all")]
    assert stage_iv_all.metrics["coverage_1"] == (0.2 + 0.6 + 0.8) / 3.0
    assert stage_iv_all.metrics["chosen_insurer_1"] == 201


def test_collect_basic_agrsich_records_updates_bav_aggregate_state() -> None:
    context, bav, insurers, policyholders = _build_agrsich_sample()

    collect_basic_agrsich_records(context, bav, insurers, policyholders)

    aggregate_state = bav.service_state.aggregate_state
    assert aggregate_state.active_insurer_ids_current == [200, 201, 202]
    assert aggregate_state.policyholder_rule_counts == {5: 2, 6: 1}
    assert aggregate_state.last_agrsich_period == 3


def test_scenario_loader_reads_current_aggregate_fields(minimal_scenario_path: Path) -> None:
    from ims.io.scenario_loader import load_scenario

    scenario = load_scenario(minimal_scenario_path)

    assert scenario.insurers[0].rule_id == 7
    assert scenario.insurers[0].premiums_current == 12.0
    assert scenario.insurers[0].policyholders_current == 1.0
    assert scenario.policyholders[0].rule_id == 17
    assert scenario.policyholders[0].insured_current == 0.5
    assert scenario.policyholders[0].chosen_insurer_current == 200
