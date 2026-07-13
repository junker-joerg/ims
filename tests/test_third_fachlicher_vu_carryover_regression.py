import pytest

from ims.engine.vu_rule_runner import run_vu_foreign_info_multi_period_from_mappings


def _parameters() -> dict[str, list[float]]:
    return {
        "premium_intercept_normal": [1.0, 2.0],
        "premium_factor_normal": [0.5, 0.25],
        "advertising_intercept_normal": [3.0, 4.0],
        "advertising_factor_normal": [0.1, 0.2],
        "premium_intercept_shock": [10.0, 20.0],
        "premium_factor_shock": [1.0, 2.0],
        "advertising_intercept_shock": [30.0, 40.0],
        "advertising_factor_shock": [3.0, 4.0],
    }


def _net_switcher_markup_parameters() -> dict[str, list[float]]:
    return {
        "premium_below_normal": [1.1, 1.2],
        "premium_above_normal": [0.9, 0.8],
        "advertising_below_normal": [1.3, 1.4],
        "advertising_above_normal": [0.7, 0.6],
        "premium_below_shock": [2.1, 2.2],
        "premium_above_shock": [1.9, 1.8],
        "advertising_below_shock": [2.3, 2.4],
        "advertising_above_shock": [1.7, 1.6],
    }


def _scenario_for_period(period: int) -> dict:
    return {
        "context": {"period": period, "logtime": period + 10, "max_periods": 12, "run_index": 1},
        "bav": {"entity_id": 1, "name": "BAV"},
        "insurers": [
            {
                "entity_id": 10,
                "name": "VU-10",
                "active": True,
                "active_prev": True,
                "premiums_prev_sector": [100.0, 200.0],
                "advertising_prev_sector": [10.0, 20.0],
                "reserves_prev_sector": [1000.0, 100.0],
                "reserves_current": [50.0, 60.0],
                "policyholders_prev": 20.0,
                "policyholders_prev_sector": [20.0, 75.0],
                "policyholders_current": 30.0,
                "policyholders_current_sector": [30.0, 80.0],
                "claims_count_current": [2, 4],
                "claims_sum_current": [250.0, 600.0],
            }
        ],
        "policyholders": [],
        "vu_foreign_info_rule_snapshots": [
            {
                "insurer_id": 10,
                "rule_kind": "average",
                "interest_rate": 0.05,
                "parameters": _parameters(),
            }
        ],
    }


def test_third_fachlicher_vu_carryover_fixture_regression() -> None:
    result = run_vu_foreign_info_multi_period_from_mappings(
        [_scenario_for_period(2), _scenario_for_period(3)],
        carry_forward_insurer_state=True,
    )

    assert result.processed_local_periods == [2, 3]
    assert result.processed_global_periods == [14, 15]
    assert len(result.carryovers) == 1
    carryover = result.carryovers[0]
    assert carryover.from_period == 2
    assert carryover.to_period == 3
    assert carryover.from_global_period == 14
    assert carryover.to_global_period == 15
    assert carryover.insurer_ids == [10]

    second = result.period_results[1]
    assert second.foreign_info.insurer.dp == [51.0, 52.0]
    assert second.foreign_info.insurer.dw == [4.0, 8.0]
    assert second.foreign_info.insurer.mp == [51.0, 52.0]
    insurer = second.insurers[0]
    assert insurer.premiums_current_sector == [26.5, 15.0]
    assert insurer.advertising_current_sector == [3.4, 5.6]
    assert insurer.reserves_current == pytest.approx([55.125, 66.15])
    assert insurer.policyholders_current_sector == [30.0, 80.0]
    assert insurer.policyholders_prev_sector == [30.0, 80.0]


def test_third_fachlicher_vu_carryover_advances_vrvu04_basis() -> None:
    first = _scenario_for_period(2)
    second = _scenario_for_period(3)
    second["vu_foreign_info_rule_snapshots"] = []
    second["vu_net_switcher_markup_rule_snapshots"] = [
        {
            "insurer_id": 10,
            "net_switcher_thresholds": [5.0, 10.0],
            "parameters": _net_switcher_markup_parameters(),
        }
    ]

    result = run_vu_foreign_info_multi_period_from_mappings(
        [first, second],
        carry_forward_insurer_state=True,
    )

    second_result = result.period_results[1]
    application = second_result.net_switcher_markup_applications[0]
    assert result.carryovers[0].insurer_ids == [10]
    assert second_result.foreign_info.insurer.dp == [51.0, 52.0]
    assert second_result.insurers[0].policyholders_prev_sector == [30.0, 80.0]
    assert application.result.net_switcher_values == pytest.approx([0.0, 0.0])
