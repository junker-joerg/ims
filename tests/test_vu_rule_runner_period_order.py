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


def _scenario_for_period(period: int, *, snapshot_insurer_id: int = 10) -> dict:
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
            }
        ],
        "policyholders": [],
        "vu_foreign_info_rule_snapshots": [
            {
                "insurer_id": snapshot_insurer_id,
                "rule_kind": "average",
                "parameters": _parameters(),
            }
        ],
    }


def test_vu_rule_multi_period_runner_validates_period_order_before_rule_application() -> None:
    with pytest.raises(ValueError, match="increasing periods"):
        run_vu_foreign_info_multi_period_from_mappings(
            [
                _scenario_for_period(3, snapshot_insurer_id=99),
                _scenario_for_period(2),
            ]
        )
