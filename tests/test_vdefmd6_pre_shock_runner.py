import pytest

from ims.engine.vdefmd6_pre_shock_runner import (
    VDEFMD6_PRE_SHOCK_EXECUTION_ORDER,
    VDEFMD6_PRE_SHOCK_STATE_POLICY_ID,
    run_vdefmd6_pre_shock_periods,
)


def _run(seed: int = 20260001):
    return run_vdefmd6_pre_shock_periods(base_seed=seed)


def test_vdefmd6_pre_shock_runner_closes_periods_2_to_49() -> None:
    result = _run()

    assert [item.period for item in result.period_results] == list(range(2, 50))
    assert len(result.vu14_export_table.rows) == 49
    assert [row.values[0] for row in result.vu14_export_table.rows] == list(
        range(1, 50)
    )
    assert result.total_vu_rule_applications == 1200
    assert result.total_vn_insurance_rule_applications == 7200
    assert result.total_vn_damage_settlement_applications == 7200
    assert result.total_uniform_value_count == 47904
    assert result.total_normal_value_count == 29184


def test_vdefmd6_pre_shock_runner_applies_information_costs() -> None:
    result = _run()

    assert all(item.information_cost == 1584.0 for item in result.period_results)
    assert all(
        item.information_cost_policyholder_count == 60
        for item in result.period_results
    )
    assert result.total_information_cost == 76032.0
    assert result.total_information_cost_policyholders == 2880


def test_vdefmd6_pre_shock_runner_uses_explicit_modern_boundaries() -> None:
    result = _run()

    assert result.execution_order == VDEFMD6_PRE_SHOCK_EXECUTION_ORDER
    assert result.state_policy_id == VDEFMD6_PRE_SHOCK_STATE_POLICY_ID
    assert result.legacy_rows_used_as_generation_input is False
    assert result.writes_performed is False
    assert result.scheduler_started is False
    assert result.simulation_performed is False
    assert result.historical_same_slot_order_claimed is False
    assert result.historical_rng_equality_claimed is False
    assert result.historical_full_equality_claimed is False


def test_vdefmd6_pre_shock_runner_is_seed_reproducible() -> None:
    first = _run(20260123)
    second = _run(20260123)
    different = _run(20260124)

    assert first == second
    assert first.vu14_export_table.rows != different.vu14_export_table.rows


@pytest.mark.parametrize("seed", [-1, 1.5])
def test_vdefmd6_pre_shock_runner_rejects_invalid_seed(seed: object) -> None:
    with pytest.raises(ValueError, match="non-negative integer"):
        run_vdefmd6_pre_shock_periods(base_seed=seed)  # type: ignore[arg-type]
