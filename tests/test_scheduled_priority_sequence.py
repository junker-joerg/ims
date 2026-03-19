from pathlib import Path

import pytest

from ims.engine.simulation import ScheduledSequenceResult, run_two_prioritized_bav_updates


def test_lower_priority_value_is_dispatched_first() -> None:
    scenario_path = Path(__file__).parent / "fixtures" / "minimal_scenario.json"

    result = run_two_prioritized_bav_updates(
        scenario_path,
        initialize_rng=False,
        use_rng_sample=False,
        first_priority=5,
        second_priority=1,
    )

    assert isinstance(result, ScheduledSequenceResult)
    assert len(result.planned_events) == 2
    assert len(result.dispatched_results) == 2

    assert result.planned_events[0].payload["label"] == "first"
    assert result.planned_events[1].payload["label"] == "second"

    assert result.dispatched_results[0].event.priority == 1
    assert result.dispatched_results[0].event.payload["label"] == "second"
    assert result.dispatched_results[1].event.priority == 5
    assert result.dispatched_results[1].event.payload["label"] == "first"


def test_planned_order_can_differ_from_dispatch_order() -> None:
    scenario_path = Path(__file__).parent / "fixtures" / "minimal_scenario.json"

    result = run_two_prioritized_bav_updates(
        scenario_path,
        first_priority=9,
        second_priority=0,
    )

    planned_labels = [event.payload["label"] for event in result.planned_events]
    dispatched_labels = [
        item.event.payload["label"] for item in result.dispatched_results
    ]

    assert planned_labels == ["first", "second"]
    assert dispatched_labels == ["second", "first"]


def test_equal_priority_uses_stable_fifo_order() -> None:
    scenario_path = Path(__file__).parent / "fixtures" / "minimal_scenario.json"

    result = run_two_prioritized_bav_updates(
        scenario_path,
        first_priority=3,
        second_priority=3,
    )

    dispatched_labels = [
        item.event.payload["label"] for item in result.dispatched_results
    ]

    assert dispatched_labels == ["first", "second"]


def test_seeded_priority_sequence_is_deterministic() -> None:
    scenario_path = Path(__file__).parent / "fixtures" / "minimal_scenario.json"

    result_a = run_two_prioritized_bav_updates(
        scenario_path,
        initialize_rng=True,
        use_rng_sample=True,
        first_priority=5,
        second_priority=1,
    )
    result_b = run_two_prioritized_bav_updates(
        scenario_path,
        initialize_rng=True,
        use_rng_sample=True,
        first_priority=5,
        second_priority=1,
    )

    assert result_a.dispatched_results[0].bav_update.sample_token is not None
    assert result_a.dispatched_results[1].bav_update.sample_token is not None

    assert (
        result_a.dispatched_results[0].bav_update.sample_token
        == result_b.dispatched_results[0].bav_update.sample_token
    )
    assert (
        result_a.dispatched_results[1].bav_update.sample_token
        == result_b.dispatched_results[1].bav_update.sample_token
    )


def test_priority_sequence_raises_when_sampling_without_rng() -> None:
    scenario_path = Path(__file__).parent / "fixtures" / "minimal_scenario.json"

    with pytest.raises(
        ValueError,
        match="context.rng is required",
    ):
        run_two_prioritized_bav_updates(
            scenario_path,
            initialize_rng=False,
            use_rng_sample=True,
        )
