from pathlib import Path

import pytest

from ims.engine.simulation import ScheduledSequenceResult, run_two_scheduled_bav_updates


def test_two_scheduled_events_run_in_logtime_order_within_same_period(minimal_scenario_path: Path) -> None:
    result = run_two_scheduled_bav_updates(minimal_scenario_path)

    assert isinstance(result, ScheduledSequenceResult)
    assert len(result.planned_events) == 2
    assert len(result.dispatched_results) == 2
    assert result.planned_events[0].period == 0
    assert result.planned_events[0].logtime == 0
    assert result.planned_events[1].period == 0
    assert result.planned_events[1].logtime == 1
    assert result.dispatched_results[0].event.logtime == 0
    assert result.dispatched_results[1].event.logtime == 1


def test_two_scheduled_events_can_cross_period_boundary(minimal_scenario_path: Path) -> None:
    result = run_two_scheduled_bav_updates(
        minimal_scenario_path,
        second_step_new_period=True,
    )

    assert result.planned_events[0].period == 0
    assert result.planned_events[0].logtime == 0
    assert result.planned_events[1].period == 1
    assert result.planned_events[1].logtime == 0
    assert result.dispatched_results[1].context.period == 1
    assert result.dispatched_results[1].context.logtime == 0


def test_two_scheduled_events_rng_samples_are_deterministic(minimal_scenario_path: Path) -> None:
    first = run_two_scheduled_bav_updates(
        minimal_scenario_path,
        initialize_rng=True,
        use_rng_sample=True,
    )
    second = run_two_scheduled_bav_updates(
        minimal_scenario_path,
        initialize_rng=True,
        use_rng_sample=True,
    )

    assert first.dispatched_results[0].bav_update.sample_token == 0.052363598850944326
    assert first.dispatched_results[1].bav_update.sample_token == 0.08718667752263232
    assert second.dispatched_results[0].bav_update.sample_token == first.dispatched_results[0].bav_update.sample_token
    assert second.dispatched_results[1].bav_update.sample_token == first.dispatched_results[1].bav_update.sample_token


def test_two_scheduled_events_raise_when_sampling_without_rng(minimal_scenario_path: Path) -> None:
    with pytest.raises(ValueError, match="context.rng is required"):
        run_two_scheduled_bav_updates(
            minimal_scenario_path,
            initialize_rng=False,
            use_rng_sample=True,
        )
