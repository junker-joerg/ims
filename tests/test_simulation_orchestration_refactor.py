from pathlib import Path

from ims.engine.simulation import (
    run_controlled_bav_event_loop,
    run_progressed_mixed_controlled_bav_event_loop,
    run_scheduled_bav_update,
)


SCENARIO_PATH = Path(__file__).parent / "fixtures" / "minimal_scenario.json"


def test_run_scheduled_bav_update_still_dispatches_single_event() -> None:
    result = run_scheduled_bav_update(SCENARIO_PATH)

    assert result.event.action == "bav_update"
    assert result.event.period == 0
    assert result.event.logtime == 0
    assert result.bav_update is not None


def test_run_controlled_bav_event_loop_keeps_limit_behavior() -> None:
    result = run_controlled_bav_event_loop(
        SCENARIO_PATH,
        num_events=5,
        max_events=3,
    )

    assert len(result.planned_events) == 5
    assert len(result.dispatched_results) == 3
    assert result.stopped_due_to_limit is True
    assert result.remaining_scheduled_events == 2


def test_run_progressed_mixed_controlled_bav_event_loop_keeps_ordering() -> None:
    result = run_progressed_mixed_controlled_bav_event_loop(
        SCENARIO_PATH,
        num_pairs=3,
        max_events=6,
        logtimes_per_period=2,
        start_with_update=True,
    )

    assert [
        (item.event.period, item.event.logtime, item.event.action)
        for item in result.dispatched_results
    ] == [
        (0, 0, "bav_update"),
        (0, 1, "bav_snapshot"),
        (1, 0, "bav_update"),
        (1, 1, "bav_snapshot"),
        (2, 0, "bav_update"),
        (2, 1, "bav_snapshot"),
    ]


def test_refactored_orchestration_keeps_rng_determinism() -> None:
    result_a = run_progressed_mixed_controlled_bav_event_loop(
        SCENARIO_PATH,
        initialize_rng=True,
        use_rng_sample=True,
        num_pairs=3,
        max_events=6,
        logtimes_per_period=2,
        start_with_update=True,
    )
    result_b = run_progressed_mixed_controlled_bav_event_loop(
        SCENARIO_PATH,
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
