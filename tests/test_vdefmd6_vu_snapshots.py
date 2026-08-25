import random

import pytest

from ims.model.vdefmd6_population import build_vdefmd6_population
from ims.model.vdefmd6_vu_snapshots import (
    VDEFMD6_VU_DRAW_POLICY_ID,
    build_vdefmd6_shock_vu_snapshot_batch,
    build_vdefmd6_vu_snapshot_batch,
)
from ims.model.vu_rules import VUForeignInfoRuleKind


def _build(seed: int = 790001):
    return build_vdefmd6_vu_snapshot_batch(
        build_vdefmd6_population(),
        period=2,
        rng=random.Random(seed),
    )


def test_vdefmd6_vu_snapshot_batch_materializes_all_25_insurers() -> None:
    batch = _build()

    assert batch.period == 2
    assert batch.draw_policy_id == VDEFMD6_VU_DRAW_POLICY_ID
    assert batch.snapshot_count == 25
    assert len(batch.random_uniform_snapshots) == 2
    assert len(batch.random_normal_snapshots) == 2
    assert len(batch.reserve_markup_snapshots) == 3
    assert len(batch.net_switcher_markup_snapshots) == 3
    assert len(batch.market_share_markup_snapshots) == 3
    assert len(batch.expected_claim_snapshots) == 3
    assert len(batch.foreign_info_snapshots) == 9
    assert [item.rule_kind for item in batch.foreign_info_snapshots] == [
        VUForeignInfoRuleKind.DUMPING,
        VUForeignInfoRuleKind.DUMPING,
        VUForeignInfoRuleKind.DUMPING,
        VUForeignInfoRuleKind.AVERAGE,
        VUForeignInfoRuleKind.AVERAGE,
        VUForeignInfoRuleKind.AVERAGE,
        VUForeignInfoRuleKind.ATTACK,
        VUForeignInfoRuleKind.ATTACK,
        VUForeignInfoRuleKind.ATTACK,
    ]
    assert batch.uniform_value_count == 8
    assert batch.normal_value_count == 8
    assert batch.runner_started is False
    assert batch.simulation_performed is False
    assert batch.historical_rng_equality_claimed is False


def test_vdefmd6_vu_snapshot_batch_maps_parameters_and_aspirations() -> None:
    batch = _build()
    random_uniform = batch.random_uniform_snapshots[0]
    random_normal = batch.random_normal_snapshots[0]
    reserve = batch.reserve_markup_snapshots[0]
    net_switcher = batch.net_switcher_markup_snapshots[0]
    market_share = batch.market_share_markup_snapshots[0]
    expected_claim = batch.expected_claim_snapshots[0]
    foreign_info = batch.foreign_info_snapshots[0]

    assert random_uniform.insurer_id == 1
    assert random_uniform.parameters.premium_factor_normal == [60.0, 50.0]
    assert random_uniform.parameters.advertising_factor_normal == [20.0, 20.0]
    assert len(random_uniform.random_draws) == 4

    assert random_normal.insurer_id == 3
    assert random_normal.parameters.premium_intercept_normal == [30.0, 30.0]
    assert random_normal.parameters.premium_factor_normal == [5.0, 5.0]
    assert random_normal.parameters.advertising_intercept_normal == [10.0, 10.0]
    assert random_normal.parameters.advertising_factor_normal == [0.0, 0.0]

    assert reserve.insurer_id == 5
    assert reserve.reserve_thresholds == [0.0, 0.0]
    assert reserve.parameters.premium_below_normal == [1.03, 1.04]
    assert reserve.parameters.premium_above_normal == [0.97, 0.97]

    assert net_switcher.insurer_id == 8
    assert net_switcher.net_switcher_thresholds == [2.0, 0.0]
    assert net_switcher.previous_policyholders_sector == [0.0, 0.0]

    assert market_share.insurer_id == 11
    assert market_share.market_share_thresholds == [0.04, 0.04]
    assert market_share.active_policyholder_count == 150

    assert expected_claim.insurer_id == 14
    assert expected_claim.parameters.premium_below_normal == [1.02, 1.02]
    assert expected_claim.parameters.advertising_above_normal == [1.03, 1.03]

    assert foreign_info.insurer_id == 17
    assert foreign_info.rule_kind is VUForeignInfoRuleKind.DUMPING
    assert foreign_info.parameters.premium_intercept_normal == [1.07, 1.07]
    assert foreign_info.parameters.premium_factor_normal == [1.07, 1.07]
    assert foreign_info.interest_rate == 0.02
    assert foreign_info.change_shock is False


def test_vdefmd6_vu_snapshot_batch_exposes_bav_previous_period_inputs() -> None:
    inputs = _build().bav_previous_period_inputs

    assert inputs.period == 2
    assert inputs.active_insurer_ids_t_minus_1 == tuple(range(1, 26))
    assert inputs.active_policyholder_ids_t_minus_1 == tuple(range(1, 151))
    assert len(inputs.insurer_states) == 25
    assert len(inputs.policyholder_states) == 150
    assert inputs.interest_rate == 0.02
    assert inputs.information_cost_per_lookup == 0.8
    assert inputs.insurer_states[0].premiums_t_minus_1 == (40.0, 40.0)
    assert inputs.insurer_states[0].advertising_t_minus_1 == (0.0, 0.0)
    assert inputs.insurer_states[0].reserves_t_minus_1 == (0.0, 0.0)
    assert inputs.insurer_states[0].policyholders_t_minus_1 == (0.0, 0.0)
    assert inputs.insurer_states[0].policyholders_t_minus_2 == (0.0, 0.0)
    assert inputs.policyholder_states[0].insured_t_minus_1 == (0.0, 0.0)


def test_vdefmd6_vu_snapshot_batch_keeps_information_cost_application_open() -> None:
    boundary = _build().information_cost_boundary

    assert boundary.historical_rules == (5, 6)
    assert boundary.historical_wealth_subtraction_evidenced is True
    assert boundary.python_rule_result_exposes_cost is True
    assert boundary.python_settlement_snapshot_accepts_cost is False
    assert boundary.application_ready is False


def test_vdefmd6_vu_snapshot_batch_is_seed_reproducible() -> None:
    assert _build(790123) == _build(790123)
    assert _build(790123) != _build(790124)


@pytest.mark.parametrize("period", [1, 50])
def test_vdefmd6_vu_snapshot_batch_rejects_out_of_scope_periods(period: int) -> None:
    with pytest.raises(ValueError, match="between 2 and 49"):
        build_vdefmd6_vu_snapshot_batch(
            build_vdefmd6_population(),
            period=period,
            rng=random.Random(790001),
        )


def test_vdefmd6_vu_snapshot_batch_requires_current_active_insurer_state() -> None:
    population = build_vdefmd6_population()
    population.insurers[0].active = False

    with pytest.raises(ValueError, match="missing active insurers: 1"):
        build_vdefmd6_vu_snapshot_batch(
            population,
            period=2,
            rng=random.Random(790001),
        )


def test_vdefmd6_shock_vu_snapshot_batch_selects_period_50_parameters() -> None:
    population = build_vdefmd6_population()
    for policyholder in population.policyholders:
        policyholder.active = True

    batch = build_vdefmd6_shock_vu_snapshot_batch(
        population,
        period=50,
        rng=random.Random(810001),
    )

    assert batch.snapshot_count == 25
    assert batch.bav_previous_period_inputs.active_policyholder_ids_t_minus_1 == tuple(
        range(1, 201)
    )
    assert batch.random_uniform_snapshots[0].change_shock is True
    assert batch.random_normal_snapshots[0].change_shock is True
    assert batch.expected_claim_snapshots[0].change_shock is True
    assert batch.foreign_info_snapshots[-1].change_shock is True
    assert batch.market_share_markup_snapshots[0].active_policyholder_count == 200


@pytest.mark.parametrize("period", [49, 101])
def test_vdefmd6_shock_vu_snapshot_batch_rejects_out_of_scope_periods(
    period: int,
) -> None:
    with pytest.raises(ValueError, match="between 50 and 100"):
        build_vdefmd6_shock_vu_snapshot_batch(
            build_vdefmd6_population(),
            period=period,
            rng=random.Random(810001),
        )
