"""Ordering tests for the generic IMS scheduler scaffold."""

from ims.engine.scheduler import Scheduler


def test_scheduler_orders_by_period_logtime_priority_and_insertion() -> None:
    scheduler = Scheduler()

    scheduler.plan(period=1, logtime=5, priority=1, name="late-priority")
    scheduler.plan(period=0, logtime=9, priority=9, name="earliest-period")
    scheduler.plan(period=1, logtime=2, priority=5, name="earliest-logtime")
    scheduler.plan(period=1, logtime=5, priority=0, name="higher-priority")
    scheduler.plan(period=1, logtime=5, priority=0, name="same-priority-first")
    scheduler.plan(period=1, logtime=5, priority=0, name="same-priority-second")

    popped_names = []
    while not scheduler.empty():
        popped_names.append(scheduler.pop().name)

    assert popped_names == [
        "earliest-period",
        "earliest-logtime",
        "higher-priority",
        "same-priority-first",
        "same-priority-second",
        "late-priority",
    ]
