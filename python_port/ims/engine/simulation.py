from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ims.analysis.aggregates import AggregateSnapshot, collect_basic_aggregates
from ims.engine.context import SimulationContext, ensure_context_rng
from ims.engine.scheduler import Event, Scheduler
from ims.io.scenario_loader import load_scenario
from ims.model.bav_updates import BAVUpdateResult, update_bav_central_state
from ims.model.entities import BAV, Insurer, Policyholder


@dataclass(slots=True)
class SimulationStepResult:
    """
    Ergebnis eines einzelnen technischen Simulationsschritts.
    """

    context: SimulationContext
    bav: BAV
    insurers: list[Insurer]
    policyholders: list[Policyholder]
    bav_update: BAVUpdateResult
    aggregate_snapshot: AggregateSnapshot


@dataclass(slots=True)
class TwoStepSimulationResult:
    """
    Ergebnis zweier technischer Simulationsschritte mit expliziter
    Fortschreibung von period/logtime.
    """

    initial_context: SimulationContext
    first_step: SimulationStepResult
    second_context: SimulationContext
    second_step: SimulationStepResult


@dataclass(slots=True)
class DispatchedEventResult:
    """
    Ergebnis eines per Dispatcher ausgeführten technischen Events.
    """

    event: Event
    context: SimulationContext
    bav_update: BAVUpdateResult
    aggregate_snapshot: AggregateSnapshot


@dataclass(slots=True)
class ScheduledSequenceResult:
    """
    Ergebnis einer kleinen geplanten Zwei-Event-Sequenz.
    """

    initial_context: SimulationContext
    planned_events: list[Event]
    dispatched_results: list[DispatchedEventResult]


@dataclass(slots=True)
class ControlledLoopResult:
    initial_context: SimulationContext
    planned_events: list[Event]
    dispatched_results: list[DispatchedEventResult]
    max_events: int
    stopped_due_to_limit: bool
    remaining_scheduled_events: int


def _run_loaded_bav_update_step(
    context: SimulationContext,
    bav: BAV,
    insurers: list[Insurer],
    policyholders: list[Policyholder],
    *,
    use_rng_sample: bool,
) -> SimulationStepResult:
    bav_update = update_bav_central_state(
        context=context,
        bav=bav,
        insurers=insurers,
        policyholders=policyholders,
        use_rng_sample=use_rng_sample,
    )
    aggregate_snapshot = collect_basic_aggregates(
        context=context,
        bav=bav,
        insurers=insurers,
        policyholders=policyholders,
    )
    return SimulationStepResult(
        context=context,
        bav=bav,
        insurers=insurers,
        policyholders=policyholders,
        bav_update=bav_update,
        aggregate_snapshot=aggregate_snapshot,
    )


def _context_for_event(
    base_context: SimulationContext,
    event: Event,
) -> SimulationContext:
    """
    Leitet aus einem Basis-Kontext einen expliziten Event-Kontext ab.
    """

    return SimulationContext(
        period=event.period,
        logtime=event.logtime,
        max_periods=base_context.max_periods,
        run_index=base_context.run_index,
        rng_seed=base_context.rng_seed,
        rng=base_context.rng,
    )


def _build_sequenced_bav_events(
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


def dispatch_event(
    event: Event,
    *,
    context: SimulationContext,
    bav: BAV,
    insurers: list[Insurer],
    policyholders: list[Policyholder],
) -> DispatchedEventResult:
    """
    Führt genau eine kleine unterstützte Event-Art aus.

    Unterstützt in diesem PR nur:
    - action == "bav_update"
    """

    if event.action != "bav_update":
        raise ValueError(f"unsupported event action: {event.action}")

    bav_update = update_bav_central_state(
        context=context,
        bav=bav,
        insurers=insurers,
        policyholders=policyholders,
        use_rng_sample=bool(event.payload.get("use_rng_sample", False))
        if isinstance(event.payload, dict)
        else False,
    )

    aggregate_snapshot = collect_basic_aggregates(
        context=context,
        bav=bav,
        insurers=insurers,
        policyholders=policyholders,
    )

    return DispatchedEventResult(
        event=event,
        context=context,
        bav_update=bav_update,
        aggregate_snapshot=aggregate_snapshot,
    )


def run_single_bav_update_step(
    path: str | Path,
    *,
    initialize_rng: bool = False,
    use_rng_sample: bool = False,
) -> SimulationStepResult:
    """
    Führt genau einen minimalen technischen Update-Schritt aus.
    """

    loaded = load_scenario(path)

    context = loaded.context
    if initialize_rng:
        ensure_context_rng(context)
        loaded.context = context

    bav_update = update_bav_central_state(
        context=context,
        bav=loaded.bav,
        insurers=loaded.insurers,
        policyholders=loaded.policyholders,
        use_rng_sample=use_rng_sample,
    )

    aggregate_snapshot = collect_basic_aggregates(
        context=context,
        bav=loaded.bav,
        insurers=loaded.insurers,
        policyholders=loaded.policyholders,
    )

    return SimulationStepResult(
        context=context,
        bav=loaded.bav,
        insurers=loaded.insurers,
        policyholders=loaded.policyholders,
        bav_update=bav_update,
        aggregate_snapshot=aggregate_snapshot,
    )


def run_two_bav_update_steps(
    path: str | Path,
    *,
    initialize_rng: bool = False,
    use_rng_sample: bool = False,
    second_step_new_period: bool = False,
) -> TwoStepSimulationResult:
    """
    Führt genau zwei technische Update-Schritte mit expliziter
    Fortschreibung von period/logtime aus.
    """

    loaded = load_scenario(path)

    initial_context = loaded.context
    if initialize_rng:
        ensure_context_rng(initial_context)
        loaded.context = initial_context

    first_update = update_bav_central_state(
        context=initial_context,
        bav=loaded.bav,
        insurers=loaded.insurers,
        policyholders=loaded.policyholders,
        use_rng_sample=use_rng_sample,
    )
    first_aggregate = collect_basic_aggregates(
        context=initial_context,
        bav=loaded.bav,
        insurers=loaded.insurers,
        policyholders=loaded.policyholders,
    )
    first_step = SimulationStepResult(
        context=initial_context,
        bav=loaded.bav,
        insurers=loaded.insurers,
        policyholders=loaded.policyholders,
        bav_update=first_update,
        aggregate_snapshot=first_aggregate,
    )

    if second_step_new_period:
        second_context = initial_context.advanced(
            period_increment=1,
            logtime_increment=0,
            reset_logtime_to=0,
        )
    else:
        second_context = initial_context.advanced(
            period_increment=0,
            logtime_increment=1,
        )

    loaded.context = second_context

    second_update = update_bav_central_state(
        context=second_context,
        bav=loaded.bav,
        insurers=loaded.insurers,
        policyholders=loaded.policyholders,
        use_rng_sample=use_rng_sample,
    )
    second_aggregate = collect_basic_aggregates(
        context=second_context,
        bav=loaded.bav,
        insurers=loaded.insurers,
        policyholders=loaded.policyholders,
    )
    second_step = SimulationStepResult(
        context=second_context,
        bav=loaded.bav,
        insurers=loaded.insurers,
        policyholders=loaded.policyholders,
        bav_update=second_update,
        aggregate_snapshot=second_aggregate,
    )

    return TwoStepSimulationResult(
        initial_context=initial_context,
        first_step=first_step,
        second_context=second_context,
        second_step=second_step,
    )


def run_scheduled_bav_update(
    path: str | Path,
    *,
    initialize_rng: bool = False,
    use_rng_sample: bool = False,
) -> DispatchedEventResult:
    """
    Plant genau ein technisches BAV-Update-Event, poppt es aus dem
    Scheduler und führt es über den kleinen Dispatcher aus.
    """

    loaded = load_scenario(path)

    context = loaded.context
    if initialize_rng:
        ensure_context_rng(context)
        loaded.context = context

    scheduler = Scheduler()
    event = Event(
        period=context.period,
        logtime=context.logtime,
        priority=0,
        subject_type="bav",
        subject_id=loaded.bav.entity_id,
        action="bav_update",
        payload={"use_rng_sample": use_rng_sample},
    )

    scheduler.plan(event)
    scheduled_event = scheduler.pop()

    return dispatch_event(
        scheduled_event,
        context=context,
        bav=loaded.bav,
        insurers=loaded.insurers,
        policyholders=loaded.policyholders,
    )


def run_two_scheduled_bav_updates(
    path: str | Path,
    *,
    initialize_rng: bool = False,
    use_rng_sample: bool = False,
    second_step_new_period: bool = False,
) -> ScheduledSequenceResult:
    """
    Plant genau zwei technische `bav_update`-Events, entnimmt sie in
    Scheduler-Reihenfolge und führt sie nacheinander per Dispatcher aus.
    """

    loaded = load_scenario(path)

    initial_context = loaded.context
    if initialize_rng:
        ensure_context_rng(initial_context)
        loaded.context = initial_context

    first_event = Event(
        period=initial_context.period,
        logtime=initial_context.logtime,
        priority=0,
        subject_type="bav",
        subject_id=loaded.bav.entity_id,
        action="bav_update",
        payload={"use_rng_sample": use_rng_sample},
    )

    if second_step_new_period:
        second_event = Event(
            period=initial_context.period + 1,
            logtime=0,
            priority=0,
            subject_type="bav",
            subject_id=loaded.bav.entity_id,
            action="bav_update",
            payload={"use_rng_sample": use_rng_sample},
        )
    else:
        second_event = Event(
            period=initial_context.period,
            logtime=initial_context.logtime + 1,
            priority=0,
            subject_type="bav",
            subject_id=loaded.bav.entity_id,
            action="bav_update",
            payload={"use_rng_sample": use_rng_sample},
        )

    scheduler = Scheduler()
    scheduler.plan(first_event)
    scheduler.plan(second_event)

    dispatched_results: list[DispatchedEventResult] = []

    while not scheduler.empty():
        event = scheduler.pop()
        event_context = _context_for_event(initial_context, event)
        loaded.context = event_context

        dispatched = dispatch_event(
            event,
            context=event_context,
            bav=loaded.bav,
            insurers=loaded.insurers,
            policyholders=loaded.policyholders,
        )
        dispatched_results.append(dispatched)

    return ScheduledSequenceResult(
        initial_context=initial_context,
        planned_events=[first_event, second_event],
        dispatched_results=dispatched_results,
    )


def run_two_prioritized_bav_updates(
    path: str | Path,
    *,
    initialize_rng: bool = False,
    use_rng_sample: bool = False,
    first_priority: int = 1,
    second_priority: int = 0,
) -> ScheduledSequenceResult:
    """
    Plant genau zwei technische `bav_update`-Events mit gleichem
    period/logtime, aber unterschiedlicher priority.

    Ziel dieses Slices ist allein die explizite Prüfung, dass die
    Scheduler-Reihenfolge bei gleichem Zeitpunkt über `priority`
    bestimmt wird.
    """

    loaded = load_scenario(path)

    initial_context = loaded.context
    if initialize_rng:
        ensure_context_rng(initial_context)
        loaded.context = initial_context

    first_event = Event(
        period=initial_context.period,
        logtime=initial_context.logtime,
        priority=first_priority,
        subject_type="bav",
        subject_id=loaded.bav.entity_id,
        action="bav_update",
        payload={
            "use_rng_sample": use_rng_sample,
            "label": "first",
        },
    )
    second_event = Event(
        period=initial_context.period,
        logtime=initial_context.logtime,
        priority=second_priority,
        subject_type="bav",
        subject_id=loaded.bav.entity_id,
        action="bav_update",
        payload={
            "use_rng_sample": use_rng_sample,
            "label": "second",
        },
    )

    scheduler = Scheduler()
    scheduler.plan(first_event)
    scheduler.plan(second_event)

    dispatched_results: list[DispatchedEventResult] = []

    while not scheduler.empty():
        event = scheduler.pop()
        event_context = _context_for_event(initial_context, event)
        loaded.context = event_context

        dispatched = dispatch_event(
            event,
            context=event_context,
            bav=loaded.bav,
            insurers=loaded.insurers,
            policyholders=loaded.policyholders,
        )
        dispatched_results.append(dispatched)

    return ScheduledSequenceResult(
        initial_context=initial_context,
        planned_events=[first_event, second_event],
        dispatched_results=dispatched_results,
    )


def run_controlled_bav_event_loop(
    path: str | Path,
    *,
    initialize_rng: bool = False,
    use_rng_sample: bool = False,
    num_events: int = 3,
    max_events: int = 3,
) -> ControlledLoopResult:
    if num_events <= 0:
        raise ValueError("num_events must be greater than 0")
    if max_events <= 0:
        raise ValueError("max_events must be greater than 0")

    loaded = load_scenario(path)
    initial_context = loaded.context
    if initialize_rng:
        ensure_context_rng(initial_context)
        loaded.context = initial_context

    planned_events = _build_sequenced_bav_events(
        context=initial_context,
        bav=loaded.bav,
        num_events=num_events,
        use_rng_sample=use_rng_sample,
    )

    scheduler = Scheduler()
    for event in planned_events:
        scheduler.plan(event)

    dispatched_results: list[DispatchedEventResult] = []
    while not scheduler.empty() and len(dispatched_results) < max_events:
        event = scheduler.pop()
        event_context = _context_for_event(initial_context, event)
        loaded.context = event_context
        dispatched_results.append(
            dispatch_event(
                event,
                context=event_context,
                bav=loaded.bav,
                insurers=loaded.insurers,
                policyholders=loaded.policyholders,
            )
        )

    remaining_scheduled_events = len(scheduler)
    return ControlledLoopResult(
        initial_context=initial_context,
        planned_events=planned_events,
        dispatched_results=dispatched_results,
        max_events=max_events,
        stopped_due_to_limit=remaining_scheduled_events > 0,
        remaining_scheduled_events=remaining_scheduled_events,
    )
