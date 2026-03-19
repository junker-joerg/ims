import pytest

from ims.engine.simulation import SimulationStepResult, run_single_bav_update_step


def test_run_single_bav_update_step_without_rng() -> None:
    result = run_single_bav_update_step("tests/fixtures/minimal_scenario.json")

    assert isinstance(result, SimulationStepResult)
    assert result.context.rng is None
    assert result.bav_update.period == 0
    assert result.bav_update.logtime == 0
    assert result.bav_update.active_insurer_count == 1
    assert result.bav_update.active_policyholder_count == 1
    assert result.bav_update.sample_token is None
    assert result.aggregate_snapshot.assigned_policyholders == 1


def test_run_single_bav_update_step_with_rng_sample_is_deterministic() -> None:
    first = run_single_bav_update_step(
        "tests/fixtures/minimal_scenario.json",
        initialize_rng=True,
        use_rng_sample=True,
    )
    second = run_single_bav_update_step(
        "tests/fixtures/minimal_scenario.json",
        initialize_rng=True,
        use_rng_sample=True,
    )

    assert first.context.rng is not None
    assert first.bav_update.sample_token == 0.052363598850944326
    assert second.bav_update.sample_token == first.bav_update.sample_token


def test_run_single_bav_update_step_raises_when_sampling_without_rng() -> None:
    with pytest.raises(ValueError, match="context.rng is required"):
        run_single_bav_update_step(
            "tests/fixtures/minimal_scenario.json",
            initialize_rng=False,
            use_rng_sample=True,
        )
