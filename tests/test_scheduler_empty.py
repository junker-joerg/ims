import pytest

from ims.engine.scheduler import Event, Scheduler


def test_scheduler_empty_state_changes_with_planned_events() -> None:
    scheduler = Scheduler()

    assert scheduler.empty() is True
    assert len(scheduler) == 0

    scheduler.plan(Event(0, 0, 0, "subject", 1, "bootstrap"))

    assert scheduler.empty() is False
    assert len(scheduler) == 1

    scheduler.pop()

    assert scheduler.empty() is True
    assert len(scheduler) == 0


def test_scheduler_pop_from_empty_raises_index_error() -> None:
    scheduler = Scheduler()

    with pytest.raises(IndexError, match="empty scheduler"):
        scheduler.pop()
