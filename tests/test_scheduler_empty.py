"""Empty-state tests for the generic IMS scheduler scaffold."""

from ims.engine.scheduler import Scheduler


def test_scheduler_reports_empty_before_and_after_event_lifecycle() -> None:
    scheduler = Scheduler()

    assert scheduler.empty() is True

    scheduler.plan(period=0, logtime=0, priority=0, name="bootstrap")
    assert scheduler.empty() is False

    scheduler.pop()
    assert scheduler.empty() is True
