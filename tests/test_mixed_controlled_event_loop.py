from pathlib import Path

import pytest

from ims.engine.simulation import ControlledLoopResult, run_mixed_controlled_bav_event_loop


SCENARIO_PATH = Path(__file__).parent / "fixtures" / "minimal_scenario.json"


def test_mixed_controlled_loop_with_update_first() -> None:
    result = run_mixed_controlled_bav_event_loop(
        SCENARIO_PATH,
        num_pairs=2,
        max_events=4,
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


def test_mixed_controlled_loop_with_update_first_false() -> None:
    result = run_mixed_controlled_bav_event_loop(
        SCENARIO_PATH,
        num_pairs=2,
        max_events=4,
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


def test_mixed_controlled_loop_stops_at_max_events() -> None:
    result = run_mixed_controlled_bav_event_loop(
        SCENARIO_PATH,
        num_pairs=3,
        max_events=3,
        start_with_update=True,
    )

    assert len(result.planned_events) == 6
    assert len(result.dispatched_results) == 3
    assert result.stopped_due_to_limit is True
    assert result.remaining_scheduled_events == 3


def test_mixed_controlled_loop_rng_samples_are_deterministic_for_updates() -> None:
    result_a = run_mixed_controlled_bav_event_loop(
        SCENARIO_PATH,
        initialize_rng=True,
        use_rng_sample=True,
        num_pairs=2,
        max_events=4,
        start_with_update=True,
    )
    result_b = run_mixed_controlled_bav_event_loop(
        SCENARIO_PATH,
        initialize_rng=True,
        use_rng_sample=True,
        num_pairs=2,
        max_events=4,
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
        ({"num_pairs": 0, "max_events": 1}, "num_pairs must be greater than 0"),
        ({"num_pairs": 1, "max_events": 0}, "max_events must be greater than 0"),
    ],
)
def test_mixed_controlled_loop_rejects_invalid_parameters(
    kwargs: dict[str, int],
    message: str,
) -> None:
    with pytest.raises(ValueError, match=message):
        run_mixed_controlled_bav_event_loop(SCENARIO_PATH, **kwargs)


def test_mixed_controlled_loop_raises_when_sampling_without_rng() -> None:
    with pytest.raises(ValueError, match="context.rng is required"):
        run_mixed_controlled_bav_event_loop(
            SCENARIO_PATH,
            initialize_rng=False,
            use_rng_sample=True,
            num_pairs=2,
            max_events=4,
            start_with_update=True,
        )
