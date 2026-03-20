from ims.engine.context import SimulationContext
from ims.model.bav_service import (
    BAVForeignInfoResult,
    compute_basic_foreign_info,
    initialize_bav_first_run,
    initialize_bav_followup_run,
)
from ims.model.entities import BAV, Insurer, Policyholder


def test_initialize_bav_first_run_sets_foreign_info_to_zero() -> None:
    context = SimulationContext(period=1, run_index=1)
    bav = BAV(entity_id=1)
    bav.service_state.insurer.dp = 9.0
    bav.service_state.policyholder.dg = 8.0

    initialize_bav_first_run(context, bav)

    assert bav.service_state.insurer.dp == 0.0
    assert bav.service_state.insurer.dw == 0.0
    assert bav.service_state.insurer.pm == 0.0
    assert bav.service_state.insurer.wm == 0.0
    assert bav.service_state.insurer.mp == 0.0
    assert bav.service_state.insurer.mw == 0.0
    assert bav.service_state.policyholder.dg == 0.0


def test_initialize_bav_followup_run_sets_foreign_info_to_zero() -> None:
    context = SimulationContext(period=1, run_index=2)
    bav = BAV(entity_id=1)
    bav.service_state.insurer.dp = 7.0
    bav.service_state.policyholder.dg = 6.0

    initialize_bav_followup_run(context, bav)

    assert bav.service_state.insurer.dp == 0.0
    assert bav.service_state.insurer.dw == 0.0
    assert bav.service_state.insurer.pm == 0.0
    assert bav.service_state.insurer.wm == 0.0
    assert bav.service_state.insurer.mp == 0.0
    assert bav.service_state.insurer.mw == 0.0
    assert bav.service_state.policyholder.dg == 0.0


def test_compute_basic_foreign_info_returns_zero_values_for_period_one_or_lower() -> None:
    context = SimulationContext(period=1, run_index=1)
    bav = BAV(entity_id=1)

    result = compute_basic_foreign_info(
        context,
        bav,
        insurers=[Insurer(entity_id=10, premiums_prev=11.0, advertising_prev=5.0, reserves_prev=30.0)],
        policyholders=[Policyholder(entity_id=20, insured_prev=0.8)],
    )

    assert isinstance(result, BAVForeignInfoResult)
    assert result.insurer.dp == 0.0
    assert result.insurer.dw == 0.0
    assert result.insurer.pm == 0.0
    assert result.insurer.wm == 0.0
    assert result.insurer.mp == 0.0
    assert result.insurer.mw == 0.0
    assert result.policyholder.dg == 0.0


def test_compute_basic_foreign_info_computes_expected_small_slice() -> None:
    context = SimulationContext(period=2, run_index=1)
    bav = BAV(entity_id=1)
    insurers = [
        Insurer(entity_id=10, active=True, premiums_prev=10.0, advertising_prev=2.0, reserves_prev=50.0),
        Insurer(entity_id=11, active=True, premiums_prev=20.0, advertising_prev=8.0, reserves_prev=90.0),
        Insurer(entity_id=12, active=False, premiums_prev=100.0, advertising_prev=100.0, reserves_prev=999.0),
    ]
    policyholders = [
        Policyholder(entity_id=20, active=True, insured_prev=0.25, insurer_id=10),
        Policyholder(entity_id=21, active=True, insured_prev=0.75, insurer_id=11),
        Policyholder(entity_id=22, active=False, insured_prev=1.0, insurer_id=12),
    ]

    result = compute_basic_foreign_info(context, bav, insurers, policyholders)

    assert result.insurer.dp == 15.0
    assert result.insurer.dw == 5.0
    assert result.policyholder.dg == 0.5
    assert result.insurer.pm == 10.0
    assert result.insurer.wm == 8.0
    assert result.insurer.mp == 20.0
    assert result.insurer.mw == 8.0
    assert bav.service_state.insurer.dp == 15.0
    assert bav.service_state.policyholder.dg == 0.5


def test_compute_basic_foreign_info_uses_zero_values_for_empty_active_sets() -> None:
    context = SimulationContext(period=3, run_index=1)
    bav = BAV(entity_id=1)

    result = compute_basic_foreign_info(
        context,
        bav,
        insurers=[Insurer(entity_id=10, active=False, premiums_prev=12.0, advertising_prev=4.0, reserves_prev=30.0)],
        policyholders=[Policyholder(entity_id=20, active=False, insured_prev=0.9)],
    )

    assert result.insurer.dp == 0.0
    assert result.insurer.dw == 0.0
    assert result.insurer.pm == 0.0
    assert result.insurer.wm == 0.0
    assert result.insurer.mp == 0.0
    assert result.insurer.mw == 0.0
    assert result.policyholder.dg == 0.0
