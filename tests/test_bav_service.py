from pathlib import Path

from ims.engine.context import SimulationContext
from ims.model.bav_service import (
    BAVForeignInfoResult,
    compute_extended_foreign_info,
    initialize_bav_first_run,
    initialize_bav_followup_run,
    refresh_bav_activity_state,
)
from ims.model.entities import BAV, Insurer, Policyholder


def test_initialize_bav_first_run_sets_foreign_info_to_zero() -> None:
    context = SimulationContext(period=1, run_index=1)
    bav = BAV(entity_id=1)
    bav.service_state.insurer.dp = 9.0
    bav.service_state.policyholder.dg = 8.0
    bav.service_state.computation_meta.foreign_info_available = True

    initialize_bav_first_run(context, bav)

    assert bav.service_state.insurer.dp == 0.0
    assert bav.service_state.insurer.dw == 0.0
    assert bav.service_state.insurer.pm == 0.0
    assert bav.service_state.insurer.wm == 0.0
    assert bav.service_state.insurer.mp == 0.0
    assert bav.service_state.insurer.mw == 0.0
    assert bav.service_state.policyholder.dg == 0.0
    assert bav.service_state.computation_meta.foreign_info_available is False


def test_initialize_bav_followup_run_sets_foreign_info_to_zero() -> None:
    context = SimulationContext(period=1, run_index=2)
    bav = BAV(entity_id=1)
    bav.service_state.insurer.dp = 7.0
    bav.service_state.policyholder.dg = 6.0
    bav.service_state.computation_meta.leader_insurer_id = 999

    initialize_bav_followup_run(context, bav)

    assert bav.service_state.insurer.dp == 0.0
    assert bav.service_state.insurer.dw == 0.0
    assert bav.service_state.insurer.pm == 0.0
    assert bav.service_state.insurer.wm == 0.0
    assert bav.service_state.insurer.mp == 0.0
    assert bav.service_state.insurer.mw == 0.0
    assert bav.service_state.policyholder.dg == 0.0
    assert bav.service_state.computation_meta.leader_insurer_id is None


def test_refresh_bav_activity_state_writes_prev_and_current_ids_and_counts() -> None:
    bav = BAV(entity_id=1)
    insurers = [
        Insurer(entity_id=10, active=True, active_prev=False),
        Insurer(entity_id=11, active=False, active_prev=True),
        Insurer(entity_id=12, active=True, active_prev=True),
    ]
    policyholders = [
        Policyholder(entity_id=20, active=False, active_prev=True),
        Policyholder(entity_id=21, active=True, active_prev=False),
        Policyholder(entity_id=22, active=True, active_prev=True),
    ]

    refresh_bav_activity_state(bav, insurers, policyholders)

    activity = bav.service_state.activity_state
    assert activity.active_insurer_ids_prev == [11, 12]
    assert activity.active_policyholder_ids_prev == [20, 22]
    assert activity.active_insurer_ids_current == [10, 12]
    assert activity.active_policyholder_ids_current == [21, 22]
    assert activity.active_insurer_count_prev == 2
    assert activity.active_policyholder_count_prev == 2
    assert activity.active_insurer_count_current == 2
    assert activity.active_policyholder_count_current == 2


def test_compute_extended_foreign_info_returns_zero_values_for_period_one_or_lower() -> None:
    context = SimulationContext(period=1, run_index=1)
    bav = BAV(entity_id=1)
    insurers = [Insurer(entity_id=10, active=True, active_prev=True, premiums_prev=11.0, advertising_prev=5.0, reserves_prev=30.0)]
    policyholders = [Policyholder(entity_id=20, active=False, active_prev=True, insured_prev=0.8)]

    result = compute_extended_foreign_info(context, bav, insurers, policyholders)

    assert isinstance(result, BAVForeignInfoResult)
    assert result.insurer.dp == 0.0
    assert result.insurer.dw == 0.0
    assert result.insurer.pm == 0.0
    assert result.insurer.wm == 0.0
    assert result.insurer.mp == 0.0
    assert result.insurer.mw == 0.0
    assert result.policyholder.dg == 0.0
    assert bav.service_state.activity_state.active_insurer_ids_prev == [10]
    assert bav.service_state.activity_state.active_policyholder_ids_prev == [20]
    assert bav.service_state.activity_state.active_insurer_ids_current == [10]
    assert bav.service_state.activity_state.active_policyholder_ids_current == []
    assert bav.service_state.computation_meta.foreign_info_available is False
    assert bav.service_state.computation_meta.used_previous_period_values is False
    assert bav.service_state.computation_meta.leader_insurer_id is None


def test_compute_extended_foreign_info_uses_only_previous_period_activity() -> None:
    context = SimulationContext(period=2, run_index=1)
    bav = BAV(entity_id=1)
    insurers = [
        Insurer(entity_id=200, active=False, active_prev=True, premiums_prev=12.0, advertising_prev=4.0, reserves_prev=50.0, rule_class=1),
        Insurer(entity_id=201, active=True, active_prev=True, premiums_prev=18.0, advertising_prev=6.0, reserves_prev=80.0, rule_class=2),
        Insurer(entity_id=202, active=True, active_prev=False, premiums_prev=99.0, advertising_prev=99.0, reserves_prev=10.0, rule_class=3),
    ]
    policyholders = [
        Policyholder(entity_id=300, active=False, active_prev=True, insured_prev=0.25, insurer_id=200, rule_class=10),
        Policyholder(entity_id=301, active=True, active_prev=True, insured_prev=0.75, insurer_id=201, rule_class=11),
        Policyholder(entity_id=302, active=True, active_prev=False, insured_prev=1.0, insurer_id=202, rule_class=12),
    ]

    result = compute_extended_foreign_info(context, bav, insurers, policyholders)

    assert result.insurer.dp == 15.0
    assert result.insurer.dw == 5.0
    assert result.policyholder.dg == 0.5
    assert result.insurer.pm == 12.0
    assert result.insurer.wm == 6.0
    assert result.insurer.mp == 18.0
    assert result.insurer.mw == 6.0


def test_compute_extended_foreign_info_persists_activity_and_market_leader_meta() -> None:
    context = SimulationContext(period=2, run_index=1)
    bav = BAV(entity_id=1)
    insurers = [
        Insurer(entity_id=200, active=False, active_prev=True, premiums_prev=12.0, advertising_prev=4.0, reserves_prev=50.0),
        Insurer(entity_id=201, active=True, active_prev=True, premiums_prev=18.0, advertising_prev=6.0, reserves_prev=80.0),
        Insurer(entity_id=202, active=True, active_prev=False, premiums_prev=99.0, advertising_prev=99.0, reserves_prev=10.0),
    ]
    policyholders = [
        Policyholder(entity_id=300, active=False, active_prev=True, insured_prev=0.25, insurer_id=200),
        Policyholder(entity_id=301, active=True, active_prev=True, insured_prev=0.75, insurer_id=201),
        Policyholder(entity_id=302, active=True, active_prev=False, insured_prev=1.0, insurer_id=202),
    ]

    compute_extended_foreign_info(context, bav, insurers, policyholders)

    activity = bav.service_state.activity_state
    meta = bav.service_state.computation_meta

    assert activity.active_insurer_ids_prev == [200, 201]
    assert activity.active_policyholder_ids_prev == [300, 301]
    assert activity.active_insurer_ids_current == [201, 202]
    assert activity.active_policyholder_ids_current == [301, 302]
    assert activity.active_insurer_count_prev == 2
    assert activity.active_policyholder_count_prev == 2
    assert activity.active_insurer_count_current == 2
    assert activity.active_policyholder_count_current == 2
    assert meta.foreign_info_available is True
    assert meta.used_previous_period_values is True
    assert meta.leader_insurer_id == 201


def test_compute_extended_foreign_info_uses_zero_values_for_empty_previous_active_sets() -> None:
    context = SimulationContext(period=3, run_index=1)
    bav = BAV(entity_id=1)

    result = compute_extended_foreign_info(
        context,
        bav,
        insurers=[Insurer(entity_id=10, active=True, active_prev=False, premiums_prev=12.0, advertising_prev=4.0, reserves_prev=30.0)],
        policyholders=[Policyholder(entity_id=20, active=True, active_prev=False, insured_prev=0.9)],
    )

    assert result.insurer.dp == 0.0
    assert result.insurer.dw == 0.0
    assert result.insurer.pm == 0.0
    assert result.insurer.wm == 0.0
    assert result.insurer.mp == 0.0
    assert result.insurer.mw == 0.0
    assert result.policyholder.dg == 0.0
    assert bav.service_state.computation_meta.foreign_info_available is True
    assert bav.service_state.computation_meta.used_previous_period_values is True
    assert bav.service_state.computation_meta.leader_insurer_id is None
    assert bav.service_state.activity_state.active_insurer_ids_current == [10]
    assert bav.service_state.activity_state.active_policyholder_ids_current == [20]


def test_scenario_loader_reads_optional_previous_activity_and_rule_class(minimal_scenario_path: Path) -> None:
    from ims.io.scenario_loader import load_scenario

    scenario = load_scenario(minimal_scenario_path)

    assert scenario.insurers[0].active_prev is True
    assert scenario.insurers[0].rule_class == 1
    assert scenario.policyholders[0].active_prev is True
    assert scenario.policyholders[0].rule_class == 10
