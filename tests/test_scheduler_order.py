"""Tests for the initial scheduler scaffold."""

from python_port.scheduler import SchedulerPlan, SchedulerStep


def test_scheduler_plan_preserves_step_insertion_order() -> None:
    plan = SchedulerPlan()

    plan.add_step(SchedulerStep("load-context"))
    plan.add_step(SchedulerStep("load-entities"))
    plan.add_step(SchedulerStep("build-schedule"))

    assert plan.ordered_names() == [
        "load-context",
        "load-entities",
        "build-schedule",
    ]


def test_scheduler_plan_extend_preserves_batch_order() -> None:
    plan = SchedulerPlan([SchedulerStep("bootstrap")])

    plan.extend(
        [
            SchedulerStep("prepare-context"),
            SchedulerStep("prepare-entities"),
            SchedulerStep("prepare-scheduler"),
        ]
    )

    assert plan.ordered_names() == [
        "bootstrap",
        "prepare-context",
        "prepare-entities",
        "prepare-scheduler",
    ]
