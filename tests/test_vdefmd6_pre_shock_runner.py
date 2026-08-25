import pytest

from ims.engine.vdefmd6_pre_shock_runner import (
    VDEFMD6_100_PERIOD_EXECUTION_ORDER,
    VDEFMD6_100_PERIOD_STATE_POLICY_ID,
    VDEFMD6_PRE_SHOCK_EXECUTION_ORDER,
    VDEFMD6_PRE_SHOCK_STATE_POLICY_ID,
    VDEFMD6_VN_RULE_GROUP_1_FILENAMES,
    VDEFMD6_VN_RULE_GROUP_2_FILENAMES,
    VDEFMD6_VU_AGGREGATE_FILENAMES,
    run_vdefmd6_100_periods,
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


def test_vdefmd6_100_period_runner_closes_shock_boundary() -> None:
    result = run_vdefmd6_100_periods(base_seed=20260001)

    assert len(result.vu14_export_table.rows) == 100
    assert [item.period for item in result.period_results] == list(range(2, 101))
    period_49 = result.period_results[47]
    period_50 = result.period_results[48]
    assert period_49.change_shock is False
    assert period_49.active_policyholder_count == 150
    assert period_50.change_shock is True
    assert period_50.active_policyholder_count == 200
    assert period_50.activated_policyholder_ids == tuple(range(151, 201))
    assert result.period_results[49].activated_policyholder_ids == ()
    assert all(item.change_shock for item in result.period_results[48:])
    assert all(item.active_policyholder_count == 200 for item in result.period_results[48:])


def test_vdefmd6_100_period_runner_counts_controlled_applications() -> None:
    result = run_vdefmd6_100_periods(base_seed=20260001)

    assert result.execution_order == VDEFMD6_100_PERIOD_EXECUTION_ORDER
    assert result.state_policy_id == VDEFMD6_100_PERIOD_STATE_POLICY_ID
    assert result.total_vu_rule_applications == 2475
    assert result.total_vn_insurance_rule_applications == 17400
    assert result.total_vn_damage_settlement_applications == 17400
    assert result.total_uniform_value_count == 116142
    assert result.total_normal_value_count == 70392
    assert result.total_information_cost == 161712.0
    assert result.total_information_cost_policyholders == 5940
    assert result.legacy_rows_used_as_generation_input is False
    assert result.writes_performed is False
    assert result.scheduler_started is False
    assert result.simulation_performed is False
    assert result.historical_full_equality_claimed is False


def test_vdefmd6_100_period_runner_materializes_vu_aggregates() -> None:
    result = run_vdefmd6_100_periods(base_seed=20260001)
    tables = {table.spec.filename: table for table in result.vu_aggregate_export_tables}

    assert tuple(tables) == VDEFMD6_VU_AGGREGATE_FILENAMES
    assert all(len(table.rows) == 100 for table in tables.values())
    assert all(
        [row.values[0] for row in table.rows] == list(range(1, 101))
        for table in tables.values()
    )
    assert tables["imsvusk1.dat"].spec.level == "IV"
    assert tables["imsvusk1.dat"].spec.selector_value == "all"
    assert tables["imsvusk1.dat"].rows[0].values[1:3] == [40.0, 6.8]
    assert [
        tables[f"imsvuvk{class_id}.dat"].spec.selector_value
        for class_id in range(1, 4)
    ] == [1, 2, 3]


def test_vdefmd6_100_period_runner_materializes_first_vn_rule_group() -> None:
    result = run_vdefmd6_100_periods(base_seed=20260001)
    tables = {
        table.spec.filename: table
        for table in result.vn_rule_group_1_export_tables
    }

    assert tuple(tables) == VDEFMD6_VN_RULE_GROUP_1_FILENAMES
    assert all(len(table.rows) == 100 for table in tables.values())
    assert all(
        [row.values[0] for row in table.rows] == list(range(1, 101))
        for table in tables.values()
    )
    assert all(table.spec.level == "II" for table in tables.values())
    assert all(table.spec.selector_kind == "rule" for table in tables.values())
    assert [
        tables[f"imsvnr{rule_id:02d}.dat"].spec.selector_value
        for rule_id in range(1, 4)
    ] == [1, 2, 3]


def test_vdefmd6_100_period_runner_materializes_second_vn_rule_group() -> None:
    result = run_vdefmd6_100_periods(base_seed=20260001)
    tables = {
        table.spec.filename: table
        for table in result.vn_rule_group_2_export_tables
    }

    assert tuple(tables) == VDEFMD6_VN_RULE_GROUP_2_FILENAMES
    assert all(len(table.rows) == 100 for table in tables.values())
    assert all(
        [row.values[0] for row in table.rows] == list(range(1, 101))
        for table in tables.values()
    )
    assert all(table.spec.level == "II" for table in tables.values())
    assert all(table.spec.selector_kind == "rule" for table in tables.values())
    assert [
        tables[f"imsvnr{rule_id:02d}.dat"].spec.selector_value
        for rule_id in range(4, 7)
    ] == [4, 5, 6]
