import pytest

from ims.engine.vu_rule_runner import run_vu_foreign_info_multi_period_from_mappings


def _random_uniform_parameters() -> dict[str, list[float]]:
    return {
        "premium_factor_normal": [10.0, 20.0],
        "advertising_factor_normal": [30.0, 40.0],
        "premium_factor_shock": [50.0, 60.0],
        "advertising_factor_shock": [70.0, 80.0],
    }


def _scenario_for_period(period: int, *, rng_seed: int, random_draws: list[float]) -> dict:
    return {
        "context": {
            "period": period,
            "logtime": period + 10,
            "max_periods": 12,
            "run_index": 1,
            "rng_seed": rng_seed,
        },
        "bav": {"entity_id": 1, "name": "BAV"},
        "insurers": [
            {
                "entity_id": 10,
                "name": "VU-10",
                "active": True,
                "active_prev": True,
                "premiums_prev_sector": [100.0, 200.0],
                "premiums_current_sector": [100.0, 200.0],
                "advertising_prev_sector": [10.0, 20.0],
                "advertising_current_sector": [10.0, 20.0],
                "reserves_prev_sector": [50.0, 60.0],
                "reserves_current": [50.0, 60.0],
                "policyholders_prev_sector": [20.0, 75.0],
                "policyholders_current_sector": [30.0, 80.0],
            }
        ],
        "policyholders": [],
        "vu_random_uniform_rule_snapshots": [
            {
                "insurer_id": 10,
                "random_draws": random_draws,
                "interest_rate": 0.05,
                "parameters": _random_uniform_parameters(),
            }
        ],
    }


def _period_scenarios() -> list[dict]:
    return [
        _scenario_for_period(
            2,
            rng_seed=111,
            random_draws=[0.1, 0.2, 0.3, 0.4],
        ),
        _scenario_for_period(
            3,
            rng_seed=999,
            random_draws=[0.5, 0.25, 0.75, 0.125],
        ),
    ]


def test_tenth_fachlicher_vu_random_draws_and_carryover_regression() -> None:
    result = run_vu_foreign_info_multi_period_from_mappings(
        _period_scenarios(),
        carry_forward_insurer_state=True,
    )

    assert result.processed_local_periods == [2, 3]
    assert result.processed_global_periods == [14, 15]
    assert result.total_rule_applications == 2
    assert len(result.carryovers) == 1
    carryover = result.carryovers[0]
    assert carryover.from_global_period == 14
    assert carryover.to_global_period == 15
    assert carryover.insurer_ids == [10]

    first_application = result.period_results[0].random_uniform_applications[0]
    assert first_application.result.random_draws == [0.1, 0.2, 0.3, 0.4]
    assert first_application.result.premiums_current_sector == pytest.approx([1.0, 4.0])
    assert first_application.result.advertising_current_sector == pytest.approx([9.0, 16.0])
    assert first_application.result.reserves_current == pytest.approx([52.5, 63.0])

    second = result.period_results[1]
    second_application = second.random_uniform_applications[0]
    assert second_application.result.random_draws == [0.5, 0.25, 0.75, 0.125]
    assert second.insurers[0].premiums_prev_sector == pytest.approx([1.0, 4.0])
    assert second.insurers[0].advertising_prev_sector == pytest.approx([9.0, 16.0])
    assert second.insurers[0].reserves_prev_sector == pytest.approx([52.5, 63.0])
    assert second_application.result.premiums_current_sector == pytest.approx([5.0, 5.0])
    assert second_application.result.advertising_current_sector == pytest.approx([22.5, 5.0])
    assert second_application.result.reserves_current == pytest.approx([55.125, 66.15])


def test_tenth_fachlicher_vu_random_state_is_not_carried_without_opt_in() -> None:
    result = run_vu_foreign_info_multi_period_from_mappings(_period_scenarios())

    assert result.carryovers == []
    second = result.period_results[1]
    second_application = second.random_uniform_applications[0]
    assert second.insurers[0].premiums_prev_sector == [100.0, 200.0]
    assert second.insurers[0].advertising_prev_sector == [10.0, 20.0]
    assert second.insurers[0].reserves_prev_sector == [50.0, 60.0]
    assert second_application.result.random_draws == [0.5, 0.25, 0.75, 0.125]
    assert second_application.result.reserves_current == pytest.approx([52.5, 63.0])
