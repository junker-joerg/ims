from ims.engine.context import SimulationContext
from ims.engine.event_builders import (
    build_mixed_bav_events,
    build_progressed_bav_events,
    build_progressed_mixed_bav_events,
    build_sequenced_bav_events,
)
from ims.model.entities import BAV


CONTEXT = SimulationContext(period=0, logtime=0, max_periods=12, run_index=1, rng_seed=123)
BAV_ENTITY = BAV(entity_id=100)


def test_build_sequenced_bav_events() -> None:
    events = build_sequenced_bav_events(
        context=CONTEXT,
        bav=BAV_ENTITY,
        num_events=3,
        use_rng_sample=True,
    )

    assert len(events) == 3
    assert [(event.period, event.logtime, event.action) for event in events] == [
        (0, 0, "bav_update"),
        (0, 1, "bav_update"),
        (0, 2, "bav_update"),
    ]
    assert [event.payload for event in events] == [
        {"use_rng_sample": True, "index": 0},
        {"use_rng_sample": True, "index": 1},
        {"use_rng_sample": True, "index": 2},
    ]


def test_build_progressed_bav_events() -> None:
    events = build_progressed_bav_events(
        context=CONTEXT,
        bav=BAV_ENTITY,
        num_events=4,
        use_rng_sample=False,
        logtimes_per_period=2,
    )

    assert len(events) == 4
    assert [(event.period, event.logtime, event.action) for event in events] == [
        (0, 0, "bav_update"),
        (0, 1, "bav_update"),
        (1, 0, "bav_update"),
        (1, 1, "bav_update"),
    ]
    assert [event.payload for event in events] == [
        {"use_rng_sample": False, "index": 0},
        {"use_rng_sample": False, "index": 1},
        {"use_rng_sample": False, "index": 2},
        {"use_rng_sample": False, "index": 3},
    ]


def test_build_mixed_bav_events() -> None:
    events = build_mixed_bav_events(
        context=CONTEXT,
        bav=BAV_ENTITY,
        num_pairs=2,
        use_rng_sample=True,
        start_with_update=False,
    )

    assert len(events) == 4
    assert [(event.period, event.logtime, event.action) for event in events] == [
        (0, 0, "bav_snapshot"),
        (0, 1, "bav_update"),
        (0, 2, "bav_snapshot"),
        (0, 3, "bav_update"),
    ]
    assert [event.payload for event in events] == [
        {},
        {"use_rng_sample": True, "index": 0},
        {},
        {"use_rng_sample": True, "index": 1},
    ]


def test_build_progressed_mixed_bav_events() -> None:
    events = build_progressed_mixed_bav_events(
        context=CONTEXT,
        bav=BAV_ENTITY,
        num_pairs=3,
        use_rng_sample=False,
        logtimes_per_period=2,
        start_with_update=True,
    )

    assert len(events) == 6
    assert [(event.period, event.logtime, event.action) for event in events] == [
        (0, 0, "bav_update"),
        (0, 1, "bav_snapshot"),
        (1, 0, "bav_update"),
        (1, 1, "bav_snapshot"),
        (2, 0, "bav_update"),
        (2, 1, "bav_snapshot"),
    ]
    assert [event.payload for event in events] == [
        {"use_rng_sample": False, "index": 0},
        {},
        {"use_rng_sample": False, "index": 1},
        {},
        {"use_rng_sample": False, "index": 2},
        {},
    ]
