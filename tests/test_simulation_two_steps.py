import pytest

from ims.engine.simulation import TwoStepSimulationResult, run_two_bav_update_steps


def test_two_step_simulation_advances_logtime_within_same_period() -> None:
    result = run_two_bav_update_steps("tests/fixtures/minimal_scenario.json")

    assert isinstance(result, TwoStepSimulationResult)
    assert result.initial_context.period == 0
    assert result.initial_context.logtime == 0
    assert result.first_step.bav_update.period == 0
    assert result.first_step.bav_update.logtime == 0
    assert result.second_context.period == 0
    assert result.second_context.logtime == 1
    assert result.second_step.bav_update.period == 0
    assert result.second_step.bav_update.logtime == 1


def test_two_step_simulation_can_start_new_period_on_second_step() -> None:
    result = run_two_bav_update_steps(
        "tests/fixtures/minimal_scenario.json",
        second_step_new_period=True,
    )

    assert result.second_context.period == 1
    assert result.second_context.logtime == 0
    assert result.second_step.bav_update.period == 1
    assert result.second_step.bav_update.logtime == 0


def test_two_step_simulation_rng_samples_are_deterministic_for_same_seed() -> None:
    first = run_two_bav_update_steps(
        "tests/fixtures/minimal_scenario.json",
        initialize_rng=True,
        use_rng_sample=True,
    )
    second = run_two_bav_update_steps(
        "tests/fixtures/minimal_scenario.json",
        initialize_rng=True,
        use_rng_sample=True,
    )

    assert first.first_step.bav_update.sample_token == 0.052363598850944326
    assert first.second_step.bav_update.sample_token == 0.08718667752263232
    assert second.first_step.bav_update.sample_token == first.first_step.bav_update.sample_token
    assert second.second_step.bav_update.sample_token == first.second_step.bav_update.sample_token


def test_two_step_simulation_raises_if_sampling_without_rng() -> None:
    with pytest.raises(ValueError, match="context.rng is required"):
        run_two_bav_update_steps(
            "tests/fixtures/minimal_scenario.json",
            initialize_rng=False,
            use_rng_sample=True,
        )
