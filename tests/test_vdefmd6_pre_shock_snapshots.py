import random

import pytest

from ims.model.vdefmd6_population import build_vdefmd6_population
from ims.model.vdefmd6_pre_shock_snapshots import (
    VDEFMD6_PRE_SHOCK_DRAW_POLICY_ID,
    build_vdefmd6_pre_shock_snapshot_batch,
    build_vdefmd6_shock_snapshot_batch,
)
from ims.model.vn_insurance_rules import (
    VNInsuranceRuleKind,
    VNRandomInsuranceRuleDraws,
    VNSampleSearchInsuranceRuleDraws,
)


def _build(seed: int = 780001):
    return build_vdefmd6_pre_shock_snapshot_batch(
        build_vdefmd6_population(),
        period=2,
        rng=random.Random(seed),
    )


def test_vdefmd6_pre_shock_snapshot_batch_materializes_all_active_vn_inputs() -> None:
    batch = _build()

    assert batch.period == 2
    assert batch.draw_policy_id == VDEFMD6_PRE_SHOCK_DRAW_POLICY_ID
    assert batch.active_insurer_ids == tuple(range(1, 26))
    assert len(batch.insurance_snapshots) == 150
    assert len(batch.damage_snapshots) == 150
    assert [item.policyholder_id for item in batch.insurance_snapshots] == list(
        range(1, 151)
    )
    assert [item.rule_kind for item in batch.insurance_snapshots].count(
        VNInsuranceRuleKind.COMPULSORY
    ) == 15
    assert [item.rule_kind for item in batch.insurance_snapshots].count(
        VNInsuranceRuleKind.RANDOM
    ) == 15
    assert [item.rule_kind for item in batch.insurance_snapshots].count(
        VNInsuranceRuleKind.PREFERENCE
    ) == 30
    assert [item.rule_kind for item in batch.insurance_snapshots].count(
        VNInsuranceRuleKind.SEARCH_HISTORY
    ) == 30
    assert [item.rule_kind for item in batch.insurance_snapshots].count(
        VNInsuranceRuleKind.SAMPLE_SEARCH
    ) == 30
    assert [item.rule_kind for item in batch.insurance_snapshots].count(
        VNInsuranceRuleKind.BEST_INFO
    ) == 30
    assert batch.draw_summary.uniform_values == 990
    assert batch.draw_summary.normal_values == 600
    assert batch.draw_summary.damage_threshold_uniform_values == 300
    assert batch.draw_summary.insurance_uniform_values == 690
    assert batch.runner_started is False
    assert batch.simulation_performed is False
    assert batch.historical_rng_equality_claimed is False


def test_vdefmd6_pre_shock_snapshot_batch_maps_parameters_and_draw_shapes() -> None:
    batch = _build()
    random_snapshot = batch.insurance_snapshots[15]
    sample_snapshot = batch.insurance_snapshots[90]
    damage_snapshot = batch.damage_snapshots[0]

    assert random_snapshot.policyholder_id == 16
    assert random_snapshot.parameters.insurance_thresholds_normal == [0.5, 0.5]
    assert isinstance(random_snapshot.draws, VNRandomInsuranceRuleDraws)
    assert len(random_snapshot.draws.status_draws) == 2
    assert len(random_snapshot.draws.insurer_choice_draws) == 2

    assert sample_snapshot.policyholder_id == 91
    assert sample_snapshot.parameters.sample_sizes_normal == [8, 8]
    assert isinstance(sample_snapshot.draws, VNSampleSearchInsuranceRuleDraws)
    assert [len(item) for item in sample_snapshot.draws.insurer_choice_draws_by_sector] == [
        8,
        8,
    ]
    assert sample_snapshot.information_cost_per_sample == 0.8

    assert damage_snapshot.parameters.damage_intercept_normal == [30.0, 30.0]
    assert damage_snapshot.parameters.damage_factor_normal == [5.0, 5.0]
    assert damage_snapshot.insurance_decisions is None
    assert damage_snapshot.information_cost == 0.0
    assert damage_snapshot.change_shock is False
    assert len(damage_snapshot.damage_thresholds) == 2
    assert len(damage_snapshot.draws.trigger_draws) == 2
    assert len(damage_snapshot.draws.amount_draws) == 2


def test_vdefmd6_pre_shock_snapshot_batch_is_seed_reproducible() -> None:
    first = _build(780123)
    second = _build(780123)
    different = _build(780124)

    assert first == second
    assert first != different


@pytest.mark.parametrize("period", [1, 50])
def test_vdefmd6_pre_shock_snapshot_batch_rejects_out_of_scope_periods(
    period: int,
) -> None:
    with pytest.raises(ValueError, match="between 2 and 49"):
        build_vdefmd6_pre_shock_snapshot_batch(
            build_vdefmd6_population(),
            period=period,
            rng=random.Random(780001),
        )


def test_vdefmd6_pre_shock_snapshot_batch_requires_current_active_state() -> None:
    population = build_vdefmd6_population()
    population.policyholders[0].active = False

    with pytest.raises(ValueError, match="missing active policyholders: 1"):
        build_vdefmd6_pre_shock_snapshot_batch(
            population,
            period=2,
            rng=random.Random(780001),
        )


def test_vdefmd6_shock_snapshot_batch_activates_shock_inputs() -> None:
    population = build_vdefmd6_population()
    for policyholder in population.policyholders:
        policyholder.active = True

    batch = build_vdefmd6_shock_snapshot_batch(
        population,
        period=50,
        rng=random.Random(810002),
    )

    assert batch.change_shock is True
    assert len(batch.insurance_snapshots) == 200
    assert len(batch.damage_snapshots) == 200
    assert all(snapshot.change_shock for snapshot in batch.insurance_snapshots)
    assert all(snapshot.change_shock for snapshot in batch.damage_snapshots)
    sample_search = batch.insurance_snapshots[90]
    assert [len(items) for items in sample_search.draws.insurer_choice_draws_by_sector] == [
        10,
        10,
    ]
    assert batch.draw_summary.uniform_values == 1330
    assert batch.draw_summary.normal_values == 800


@pytest.mark.parametrize("period", [49, 101])
def test_vdefmd6_shock_snapshot_batch_rejects_out_of_scope_periods(
    period: int,
) -> None:
    with pytest.raises(ValueError, match="between 50 and 100"):
        build_vdefmd6_shock_snapshot_batch(
            build_vdefmd6_population(),
            period=period,
            rng=random.Random(810002),
        )
