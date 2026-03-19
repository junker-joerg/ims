from __future__ import annotations

from ims.engine.context import SimulationContext
from ims.engine.scheduler import Event
from ims.model.entities import BAV


def _advance_progression_context(
    context: SimulationContext,
    *,
    logtimes_per_period: int,
) -> SimulationContext:
    if context.logtime >= logtimes_per_period - 1:
        return context.advanced(
            period_increment=1,
            logtime_increment=0,
            reset_logtime_to=0,
        )
    return context.advanced(
        period_increment=0,
        logtime_increment=1,
    )


def build_sequenced_bav_events(
    *,
    context: SimulationContext,
    bav: BAV,
    num_events: int,
    use_rng_sample: bool,
) -> list[Event]:
    return [
        Event(
            period=context.period,
            logtime=context.logtime + index,
            priority=0,
            subject_type="bav",
            subject_id=bav.entity_id,
            action="bav_update",
            payload={"use_rng_sample": use_rng_sample, "index": index},
        )
        for index in range(num_events)
    ]



def build_progressed_bav_events(
    *,
    context: SimulationContext,
    bav: BAV,
    num_events: int,
    use_rng_sample: bool,
    logtimes_per_period: int,
) -> list[Event]:
    events: list[Event] = []
    event_context = context

    for index in range(num_events):
        events.append(
            Event(
                period=event_context.period,
                logtime=event_context.logtime,
                priority=0,
                subject_type="bav",
                subject_id=bav.entity_id,
                action="bav_update",
                payload={"use_rng_sample": use_rng_sample, "index": index},
            )
        )

        if index == num_events - 1:
            continue

        event_context = _advance_progression_context(
            event_context,
            logtimes_per_period=logtimes_per_period,
        )

    return events


def build_mixed_bav_events(
    *,
    context: SimulationContext,
    bav: BAV,
    num_pairs: int,
    use_rng_sample: bool,
    start_with_update: bool,
) -> list[Event]:
    events: list[Event] = []

    for index in range(num_pairs):
        base_logtime = context.logtime + (index * 2)
        if start_with_update:
            first_action = "bav_update"
            second_action = "bav_snapshot"
        else:
            first_action = "bav_snapshot"
            second_action = "bav_update"

        events.append(
            Event(
                period=context.period,
                logtime=base_logtime,
                priority=0,
                subject_type="bav",
                subject_id=bav.entity_id,
                action=first_action,
                payload={"use_rng_sample": use_rng_sample, "index": index}
                if first_action == "bav_update"
                else {},
            )
        )
        events.append(
            Event(
                period=context.period,
                logtime=base_logtime + 1,
                priority=0,
                subject_type="bav",
                subject_id=bav.entity_id,
                action=second_action,
                payload={"use_rng_sample": use_rng_sample, "index": index}
                if second_action == "bav_update"
                else {},
            )
        )

    return events


def build_progressed_mixed_bav_events(
    *,
    context: SimulationContext,
    bav: BAV,
    num_pairs: int,
    use_rng_sample: bool,
    logtimes_per_period: int,
    start_with_update: bool,
) -> list[Event]:
    events: list[Event] = []
    event_context = context

    for index in range(num_pairs):
        if start_with_update:
            actions = ("bav_update", "bav_snapshot")
        else:
            actions = ("bav_snapshot", "bav_update")

        for action in actions:
            events.append(
                Event(
                    period=event_context.period,
                    logtime=event_context.logtime,
                    priority=0,
                    subject_type="bav",
                    subject_id=bav.entity_id,
                    action=action,
                    payload={"use_rng_sample": use_rng_sample, "index": index}
                    if action == "bav_update"
                    else {},
                )
            )

            if index == num_pairs - 1 and action == actions[-1]:
                continue

            event_context = _advance_progression_context(
                event_context,
                logtimes_per_period=logtimes_per_period,
            )

    return events
