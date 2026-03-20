from pathlib import Path

from ims.engine.simulation import (
    run_controlled_bav_event_loop,
    run_progressed_mixed_controlled_bav_event_loop,
    run_single_bav_update_step,
    run_two_scheduled_bav_updates,
)


def test_run_single_bav_update_step_keeps_consistent_result_fields(minimal_scenario_path: Path) -> None:
    result = run_single_bav_update_step(minimal_scenario_path)

    assert result.context.period == 0
    assert result.context.logtime == 0
    assert result.bav.entity_id == 100
    assert len(result.insurers) == 1
    assert len(result.policyholders) == 1
    assert result.bav_update.period == 0
    assert result.aggregate_snapshot.period == 0


def test_run_controlled_bav_event_loop_keeps_result_metadata(minimal_scenario_path: Path) -> None:
    result = run_controlled_bav_event_loop(
        minimal_scenario_path,
        num_events=5,
        max_events=3,
    )

    assert result.max_events == 3
    assert result.stopped_due_to_limit is True
    assert result.remaining_scheduled_events == 2
    assert len(result.dispatched_results) == 3


def test_run_two_scheduled_bav_updates_keeps_two_dispatched_results_in_order(minimal_scenario_path: Path) -> None:
    result = run_two_scheduled_bav_updates(minimal_scenario_path)

    assert len(result.dispatched_results) == 2
    assert [
        (item.event.period, item.event.logtime, item.event.action)
        for item in result.dispatched_results
    ] == [
        (0, 0, "bav_update"),
        (0, 1, "bav_update"),
    ]


def test_run_progressed_mixed_controlled_bav_event_loop_keeps_sequence_metadata(minimal_scenario_path: Path) -> None:
    result = run_progressed_mixed_controlled_bav_event_loop(
        minimal_scenario_path,
        num_pairs=3,
        max_events=6,
        logtimes_per_period=2,
        start_with_update=True,
    )

    assert result.max_events == 6
    assert result.stopped_due_to_limit is False
    assert result.remaining_scheduled_events == 0
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
