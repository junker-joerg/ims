from pathlib import Path

import pytest

from ims.engine.simulation import ControlledLoopResult, run_progressed_bav_event_loop


SCENARIO_PATH = Path(__file__).parent / "fixtures" / "minimal_scenario.json"


def test_progressed_loop_crosses_period_boundary() -> None:
    result = run_progressed_bav_event_loop(
        SCENARIO_PATH,
        num_events=4,
        max_events=4,
        logtimes_per_period=2,
    )

    planned_points = [(event.period, event.logtime) for event in result.planned_events]
    assert planned_points == [(0, 0), (0, 1), (1, 0), (1, 1)]


def test_progressed_loop_processes_all_events_when_limit_allows() -> None:
    result = run_progressed_bav_event_loop(
        SCENARIO_PATH,
        num_events=4,
        max_events=4,
        logtimes_per_period=2,
    )

    assert isinstance(result, ControlledLoopResult)
    assert len(result.planned_events) == 4
    assert len(result.dispatched_results) == 4
    assert result.stopped_due_to_limit is False
    assert result.remaining_scheduled_events == 0


def test_progressed_loop_stops_at_max_events_across_periods() -> None:
    result = run_progressed_bav_event_loop(
        SCENARIO_PATH,
        num_events=5,
        max_events=3,
        logtimes_per_period=2,
    )

    dispatched_points = [
        (item.event.period, item.event.logtime) for item in result.dispatched_results
    ]

    assert dispatched_points == [(0, 0), (0, 1), (1, 0)]
    assert result.stopped_due_to_limit is True
    assert result.remaining_scheduled_events == 2


def test_progressed_loop_dispatch_order_follows_period_and_logtime() -> None:
    result = run_progressed_bav_event_loop(
        SCENARIO_PATH,
        num_events=6,
        max_events=6,
        logtimes_per_period=2,
    )

    dispatched_points = [
        (item.event.period, item.event.logtime) for item in result.dispatched_results
    ]
    assert dispatched_points == [(0, 0), (0, 1), (1, 0), (1, 1), (2, 0), (2, 1)]


def test_progressed_loop_seeded_rng_sequence_is_deterministic() -> None:
    result_a = run_progressed_bav_event_loop(
        SCENARIO_PATH,
        initialize_rng=True,
        use_rng_sample=True,
        num_events=4,
        max_events=4,
        logtimes_per_period=2,
    )
    result_b = run_progressed_bav_event_loop(
        SCENARIO_PATH,
        initialize_rng=True,
        use_rng_sample=True,
        num_events=4,
        max_events=4,
        logtimes_per_period=2,
    )

    samples_a = [item.bav_update.sample_token for item in result_a.dispatched_results]
    samples_b = [item.bav_update.sample_token for item in result_b.dispatched_results]

    assert samples_a == samples_b


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"num_events": 0, "max_events": 1, "logtimes_per_period": 2}, "num_events must be greater than 0"),
        ({"num_events": 1, "max_events": 0, "logtimes_per_period": 2}, "max_events must be greater than 0"),
        ({"num_events": 1, "max_events": 1, "logtimes_per_period": 0}, "logtimes_per_period must be greater than 0"),
    ],
)
def test_progressed_loop_rejects_invalid_parameters(kwargs: dict[str, int], message: str) -> None:
    with pytest.raises(ValueError, match=message):
        run_progressed_bav_event_loop(SCENARIO_PATH, **kwargs)


def test_progressed_loop_raises_when_sampling_without_rng() -> None:
    with pytest.raises(ValueError, match="context.rng is required"):
        run_progressed_bav_event_loop(
            SCENARIO_PATH,
            initialize_rng=False,
            use_rng_sample=True,
            num_events=4,
            max_events=4,
            logtimes_per_period=2,
        )
