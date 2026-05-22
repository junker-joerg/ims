from pathlib import Path

import pytest

from ims.engine.simulation import (
    ScheduledExplicitPeriodResult,
    run_scheduled_explicit_vu_vn_period_from_mapping,
)


def _free_linear_parameters() -> dict[str, list[float]]:
    return {
        "premium_intercept_normal": [0.0, 0.0],
        "premium_factor_normal": [2.0, 2.0],
        "advertising_intercept_normal": [0.0, 0.0],
        "advertising_factor_normal": [1.0, 1.0],
        "premium_intercept_shock": [0.0, 0.0],
        "premium_factor_shock": [1.0, 1.0],
        "advertising_intercept_shock": [0.0, 0.0],
        "advertising_factor_shock": [1.0, 1.0],
    }


def _damage_parameters() -> dict[str, list[float]]:
    return {
        "damage_intercept_normal": [5.0, 7.0],
        "damage_factor_normal": [2.0, 3.0],
        "damage_intercept_shock": [50.0, 70.0],
        "damage_factor_shock": [20.0, 30.0],
    }


def _scenario() -> dict:
    return {
        "context": {"period": 2, "logtime": 4, "max_periods": 12, "run_index": 0, "rng_seed": 1002},
        "bav": {"entity_id": 1, "name": "BAV"},
        "insurers": [
            {
                "entity_id": 11,
                "name": "VU-11",
                "rule_id": 1,
                "rule_class": 1,
                "premiums_current_sector": [4.0, 6.0],
                "advertising_current_sector": [1.0, 1.0],
                "reserves_current": [40.0, 60.0],
                "policyholders_current_sector": [1.0, 2.0],
                "claims_count_current": [0, 0],
                "claims_sum_current": [0.0, 0.0],
            }
        ],
        "policyholders": [
            {
                "entity_id": 21,
                "name": "VN-21",
                "rule_id": 5,
                "rule_class": 1,
            }
        ],
        "vu_free_linear_rule_snapshots": [
            {
                "insurer_id": 11,
                "interest_rate": 0.0,
                "parameters": _free_linear_parameters(),
            }
        ],
        "vn_insurance_rule_snapshots": [
            {
                "policyholder_id": 21,
                "rule_kind": "compulsory",
                "active_insurer_ids": [11],
                "draws": {"insurer_choice_draws": [0.0, 0.0]},
            }
        ],
        "vn_damage_settlement_snapshots": [
            {
                "policyholder_id": 21,
                "previous_wealth": 100.0,
                "damage_thresholds": [0.8, 0.2],
                "parameters": _damage_parameters(),
                "draws": {
                    "trigger_draws": [0.1, 0.5],
                    "amount_draws": [2.0, 3.0],
                },
            }
        ],
    }


def _non_empty_lines(path: Path) -> list[str]:
    return [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def test_scheduled_explicit_vu_vn_period_runs_combined_rule_path(tmp_path: Path) -> None:
    result = run_scheduled_explicit_vu_vn_period_from_mapping(_scenario(), output_dir=tmp_path)

    assert isinstance(result, ScheduledExplicitPeriodResult)
    assert result.event.action == "explicit_vu_vn_period"
    assert result.event.period == 2
    assert result.event.logtime == 4
    assert result.explicit_period.period == 2
    assert result.explicit_period.global_period == 2
    assert len(result.explicit_period.vu_result.free_linear_applications) == 1
    assert len(result.explicit_period.vn_result.insurance_rule_applications) == 1
    assert result.explicit_period.vn_result.total_damage_settlement_applications == 1

    insurer = result.explicit_period.vn_result.insurers[0]
    policyholder = result.explicit_period.vn_result.policyholders[0]
    assert insurer.reserves_current == pytest.approx([39.0, 72.0])
    assert insurer.policyholders_current_sector == pytest.approx([2.0, 3.0])
    assert policyholder.paid_premium_current == pytest.approx([8.0, 12.0])
    assert policyholder.end_wealth_current == pytest.approx(71.0)

    lines = _non_empty_lines(tmp_path / "imsvu011.dat")
    assert lines[1].split() == [
        "2",
        "8.0",
        "1.0",
        "39.0",
        "2.0",
        "1",
        "9.0",
        "12.0",
        "1.0",
        "72.0",
        "3.0",
        "0",
        "0.0",
    ]


def test_scheduled_explicit_vu_vn_period_preserves_priority() -> None:
    result = run_scheduled_explicit_vu_vn_period_from_mapping(_scenario(), priority=7)

    assert result.event.priority == 7
    assert result.explicit_period.vn_result.policyholders[0].end_wealth_current == pytest.approx(71.0)
