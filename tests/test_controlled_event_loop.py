from pathlib import Path

import pytest

from ims.engine.simulation import ControlledLoopResult, run_controlled_bav_event_loop


def test_controlled_loop_processes_all_three_events(minimal_scenario_path: Path) -> None:
    result = run_controlled_bav_event_loop(minimal_scenario_path, num_events=3, max_events=3)

    assert isinstance(result, ControlledLoopResult)
    assert len(result.planned_events) == 3
    assert len(result.dispatched_results) == 3
    assert result.stopped_due_to_limit is False
    assert result.remaining_scheduled_events == 0


def test_controlled_loop_stops_at_max_events_limit(minimal_scenario_path: Path) -> None:
    result = run_controlled_bav_event_loop(minimal_scenario_path, num_events=5, max_events=3)

    assert len(result.planned_events) == 5
    assert len(result.dispatched_results) == 3
    assert result.stopped_due_to_limit is True
    assert result.remaining_scheduled_events == 2


def test_controlled_loop_dispatch_order_follows_logtime_order(minimal_scenario_path: Path) -> None:
    result = run_controlled_bav_event_loop(minimal_scenario_path, num_events=4, max_events=4)

    dispatched_logtimes = [item.event.logtime for item in result.dispatched_results]
    assert dispatched_logtimes == [0, 1, 2, 3]


def test_controlled_loop_seeded_rng_sequence_is_deterministic(minimal_scenario_path: Path) -> None:
    result_a = run_controlled_bav_event_loop(
        minimal_scenario_path,
        initialize_rng=True,
        use_rng_sample=True,
        num_events=3,
        max_events=3,
    )
    result_b = run_controlled_bav_event_loop(
        minimal_scenario_path,
        initialize_rng=True,
        use_rng_sample=True,
        num_events=3,
        max_events=3,
    )

    samples_a = [item.bav_update.sample_token for item in result_a.dispatched_results]
    samples_b = [item.bav_update.sample_token for item in result_b.dispatched_results]

    assert samples_a == samples_b


def test_controlled_loop_rejects_invalid_num_events(minimal_scenario_path: Path) -> None:
    with pytest.raises(ValueError, match="num_events must be greater than 0"):
        run_controlled_bav_event_loop(minimal_scenario_path, num_events=0, max_events=1)


def test_controlled_loop_rejects_invalid_max_events(minimal_scenario_path: Path) -> None:
    with pytest.raises(ValueError, match="max_events must be greater than 0"):
        run_controlled_bav_event_loop(minimal_scenario_path, num_events=1, max_events=0)


def test_controlled_loop_raises_when_sampling_without_rng(minimal_scenario_path: Path) -> None:
    with pytest.raises(ValueError, match="context.rng is required"):
        run_controlled_bav_event_loop(
            minimal_scenario_path,
            initialize_rng=False,
            use_rng_sample=True,
            num_events=3,
            max_events=3,
        )
