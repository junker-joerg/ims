from ims.engine.scheduler import Event, Scheduler


def test_scheduler_orders_by_period_logtime_and_priority() -> None:
    scheduler = Scheduler()

    scheduler.plan(Event(1, 2, 1, "subject", 1, "late-priority"))
    scheduler.plan(Event(0, 5, 9, "subject", 2, "earliest-period"))
    scheduler.plan(Event(1, 1, 5, "subject", 3, "earliest-logtime"))
    scheduler.plan(Event(1, 2, 0, "subject", 4, "higher-priority"))

    popped = [scheduler.pop().action for _ in range(len(scheduler))]

    assert popped == [
        "earliest-period",
        "earliest-logtime",
        "higher-priority",
        "late-priority",
    ]


def test_scheduler_is_stable_for_identical_sort_keys() -> None:
    scheduler = Scheduler()

    scheduler.plan(Event(1, 1, 1, "subject", 1, "first"))
    scheduler.plan(Event(1, 1, 1, "subject", 2, "second"))
    scheduler.plan(Event(1, 1, 1, "subject", 3, "third"))

    popped = [scheduler.pop().action for _ in range(len(scheduler))]

    assert popped == ["first", "second", "third"]
