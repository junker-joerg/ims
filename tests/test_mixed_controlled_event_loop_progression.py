from pathlib import Path

import pytest

from ims.engine.simulation import (
    ControlledLoopResult,
    run_progressed_mixed_controlled_bav_event_loop,
)


def test_progressed_mixed_loop_crosses_period_boundary(minimal_scenario_path: Path) -> None:
    result = run_progressed_mixed_controlled_bav_event_loop(
        minimal_scenario_path,
        num_pairs=3,
        max_events=6,
        logtimes_per_period=2,
        start_with_update=True,
    )

    assert [(event.period, event.logtime) for event in result.planned_events] == [
        (0, 0),
        (0, 1),
        (1, 0),
        (1, 1),
        (2, 0),
        (2, 1),
    ]


def test_progressed_mixed_loop_with_start_with_update_true(minimal_scenario_path: Path) -> None:
    result = run_progressed_mixed_controlled_bav_event_loop(
        minimal_scenario_path,
        num_pairs=2,
        max_events=4,
        logtimes_per_period=2,
        start_with_update=True,
    )

    assert isinstance(result, ControlledLoopResult)
    assert [event.action for event in result.planned_events] == [
        "bav_update",
        "bav_snapshot",
        "bav_update",
        "bav_snapshot",
    ]
    assert [item.bav_update is not None for item in result.dispatched_results] == [
        True,
        False,
        True,
        False,
    ]


def test_progressed_mixed_loop_with_start_with_update_false(minimal_scenario_path: Path) -> None:
    result = run_progressed_mixed_controlled_bav_event_loop(
        minimal_scenario_path,
        num_pairs=2,
        max_events=4,
        logtimes_per_period=2,
        start_with_update=False,
    )

    assert [event.action for event in result.planned_events] == [
        "bav_snapshot",
        "bav_update",
        "bav_snapshot",
        "bav_update",
    ]
    assert [item.bav_update is not None for item in result.dispatched_results] == [
        False,
        True,
        False,
        True,
    ]


def test_progressed_mixed_loop_stops_at_max_events_across_periods(minimal_scenario_path: Path) -> None:
    result = run_progressed_mixed_controlled_bav_event_loop(
        minimal_scenario_path,
        num_pairs=3,
        max_events=5,
        logtimes_per_period=2,
        start_with_update=True,
    )

    assert len(result.planned_events) == 6
    assert len(result.dispatched_results) == 5
    assert result.stopped_due_to_limit is True
    assert result.remaining_scheduled_events == 1
    assert [
        (item.event.period, item.event.logtime) for item in result.dispatched_results
    ] == [(0, 0), (0, 1), (1, 0), (1, 1), (2, 0)]


def test_progressed_mixed_loop_rng_samples_are_deterministic_for_updates(minimal_scenario_path: Path) -> None:
    result_a = run_progressed_mixed_controlled_bav_event_loop(
        minimal_scenario_path,
        initialize_rng=True,
        use_rng_sample=True,
        num_pairs=3,
        max_events=6,
        logtimes_per_period=2,
        start_with_update=True,
    )
    result_b = run_progressed_mixed_controlled_bav_event_loop(
        minimal_scenario_path,
        initialize_rng=True,
        use_rng_sample=True,
        num_pairs=3,
        max_events=6,
        logtimes_per_period=2,
        start_with_update=True,
    )

    samples_a = [
        item.bav_update.sample_token
        for item in result_a.dispatched_results
        if item.bav_update is not None
    ]
    samples_b = [
        item.bav_update.sample_token
        for item in result_b.dispatched_results
        if item.bav_update is not None
    ]

    assert samples_a == samples_b


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"num_pairs": 0, "max_events": 1, "logtimes_per_period": 2}, "num_pairs must be greater than 0"),
        ({"num_pairs": 1, "max_events": 0, "logtimes_per_period": 2}, "max_events must be greater than 0"),
        ({"num_pairs": 1, "max_events": 1, "logtimes_per_period": 0}, "logtimes_per_period must be greater than 0"),
    ],
)
def test_progressed_mixed_loop_rejects_invalid_parameters(
    minimal_scenario_path: Path,
    kwargs: dict[str, int],
    message: str,
) -> None:
    with pytest.raises(ValueError, match=message):
        run_progressed_mixed_controlled_bav_event_loop(minimal_scenario_path, **kwargs)


def test_progressed_mixed_loop_raises_when_sampling_without_rng(minimal_scenario_path: Path) -> None:
    with pytest.raises(ValueError, match="context.rng is required"):
        run_progressed_mixed_controlled_bav_event_loop(
            minimal_scenario_path,
            initialize_rng=False,
            use_rng_sample=True,
            num_pairs=3,
            max_events=6,
            logtimes_per_period=2,
            start_with_update=True,
        )
