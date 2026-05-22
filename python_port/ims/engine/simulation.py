from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path

from ims.analysis.aggregates import AggregateSnapshot, collect_basic_aggregates
from ims.engine.context import SimulationContext, ensure_context_rng
from ims.engine.event_builders import (
    build_mixed_bav_events,
    build_progressed_bav_events,
    build_progressed_mixed_bav_events,
    build_sequenced_bav_events,
)
from ims.engine.explicit_period_runner import (
    ExplicitMultiPeriodRunResult,
    ExplicitPeriodRunResult,
    run_explicit_multi_period_from_fixture,
    run_explicit_multi_period_from_mappings,
    run_loaded_explicit_period,
)
from ims.engine.explicit_period_plan import (
    build_explicit_period_fixture_from_plan,
    run_explicit_multi_period_from_plan_fixture,
)
from ims.engine.scheduler import Event, Scheduler
from ims.io.scenario_loader import LoadedScenario, load_scenario, load_scenario_from_mapping
from ims.model.agrsich_export import compute_global_period
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
    bav_update: BAVUpdateResult | None
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
class ScheduledExplicitPeriodResult:
    """
    Ergebnis eines geplanten expliziten VU/VN-Periodenereignisses.
    """

    event: Event
    explicit_period: ExplicitPeriodRunResult


@dataclass(slots=True)
class ScheduledExplicitMultiPeriodResult:
    """
    Ergebnis mehrerer geplanter expliziter VU/VN-Periodenereignisse.
    """

    planned_events: list[Event]
    explicit_multi_period: ExplicitMultiPeriodRunResult


@dataclass(slots=True)
class ControlledLoopResult:
    initial_context: SimulationContext
    planned_events: list[Event]
    dispatched_results: list[DispatchedEventResult]
    max_events: int
    stopped_due_to_limit: bool
    remaining_scheduled_events: int


@dataclass(slots=True)
class _DispatchRunResult:
    dispatched_results: list[DispatchedEventResult]
    stopped_due_to_limit: bool
    remaining_scheduled_events: int


def _build_simulation_step_result(
    *,
    context: SimulationContext,
    bav: BAV,
    insurers: list[Insurer],
    policyholders: list[Policyholder],
    bav_update: BAVUpdateResult,
    aggregate_snapshot: AggregateSnapshot,
) -> SimulationStepResult:
    return SimulationStepResult(
        context=context,
        bav=bav,
        insurers=insurers,
        policyholders=policyholders,
        bav_update=bav_update,
        aggregate_snapshot=aggregate_snapshot,
    )


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



def _load_initialized_scenario(
    path: str | Path,
    *,
    initialize_rng: bool = False,
) -> LoadedScenario:
    loaded = load_scenario(path)
    if initialize_rng:
        ensure_context_rng(loaded.context)
    return loaded



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



def _dispatch_planned_events(
    loaded: LoadedScenario,
    *,
    base_context: SimulationContext,
    planned_events: list[Event],
    max_events: int | None = None,
) -> _DispatchRunResult:
    scheduler = Scheduler()
    for event in planned_events:
        scheduler.plan(event)

    dispatched_results: list[DispatchedEventResult] = []
    while not scheduler.empty() and (
        max_events is None or len(dispatched_results) < max_events
    ):
        event = scheduler.pop()
        event_context = _context_for_event(base_context, event)
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
    return _DispatchRunResult(
        dispatched_results=dispatched_results,
        stopped_due_to_limit=remaining_scheduled_events > 0,
        remaining_scheduled_events=remaining_scheduled_events,
    )



def _build_scheduled_sequence_result(
    *,
    initial_context: SimulationContext,
    planned_events: list[Event],
    dispatch_run: _DispatchRunResult,
) -> ScheduledSequenceResult:
    return ScheduledSequenceResult(
        initial_context=initial_context,
        planned_events=planned_events,
        dispatched_results=dispatch_run.dispatched_results,
    )



def _build_controlled_loop_result(
    *,
    initial_context: SimulationContext,
    planned_events: list[Event],
    max_events: int,
    dispatch_run: _DispatchRunResult,
) -> ControlledLoopResult:
    return ControlledLoopResult(
        initial_context=initial_context,
        planned_events=planned_events,
        dispatched_results=dispatch_run.dispatched_results,
        max_events=max_events,
        stopped_due_to_limit=dispatch_run.stopped_due_to_limit,
        remaining_scheduled_events=dispatch_run.remaining_scheduled_events,
    )



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
    - action == "bav_snapshot"
    """

    if event.action == "bav_update":
        bav_update = update_bav_central_state(
            context=context,
            bav=bav,
            insurers=insurers,
            policyholders=policyholders,
            use_rng_sample=bool(event.payload.get("use_rng_sample", False))
            if isinstance(event.payload, dict)
            else False,
        )
    elif event.action == "bav_snapshot":
        bav_update = None
    else:
        raise ValueError(f"unsupported event action: {event.action}")

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

    loaded = _load_initialized_scenario(path, initialize_rng=initialize_rng)

    bav_update = update_bav_central_state(
        context=loaded.context,
        bav=loaded.bav,
        insurers=loaded.insurers,
        policyholders=loaded.policyholders,
        use_rng_sample=use_rng_sample,
    )

    aggregate_snapshot = collect_basic_aggregates(
        context=loaded.context,
        bav=loaded.bav,
        insurers=loaded.insurers,
        policyholders=loaded.policyholders,
    )

    return _build_simulation_step_result(
        context=loaded.context,
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

    loaded = _load_initialized_scenario(path, initialize_rng=initialize_rng)

    initial_context = loaded.context
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
    first_step = _build_simulation_step_result(
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
    second_step = _build_simulation_step_result(
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

    loaded = _load_initialized_scenario(path, initialize_rng=initialize_rng)

    event = Event(
        period=loaded.context.period,
        logtime=loaded.context.logtime,
        priority=0,
        subject_type="bav",
        subject_id=loaded.bav.entity_id,
        action="bav_update",
        payload={"use_rng_sample": use_rng_sample},
    )

    dispatch_run = _dispatch_planned_events(
        loaded,
        base_context=loaded.context,
        planned_events=[event],
    )
    return dispatch_run.dispatched_results[0]


def run_scheduled_explicit_vu_vn_period_from_mapping(
    data: dict,
    *,
    output_dir: str | Path | None = None,
    priority: int = 0,
) -> ScheduledExplicitPeriodResult:
    """
    Plant genau einen expliziten VU/VN-Periodenschritt und fuehrt ihn aus.

    Dieser Baustein ist bewusst nur ein kontrollierter Anschluss des bereits
    portierten expliziten Periodenrunners an den technischen Scheduler. Er
    ersetzt keine historische PlanVU-/PlanVN-Ablaufsteuerung.
    """

    loaded = load_scenario_from_mapping(data)
    event = Event(
        period=loaded.context.period,
        logtime=loaded.context.logtime,
        priority=priority,
        subject_type="scenario",
        subject_id="explicit-vu-vn",
        action="explicit_vu_vn_period",
        payload={},
    )
    scheduler = Scheduler()
    scheduler.plan(event)
    planned_event = scheduler.pop()
    if planned_event.action != "explicit_vu_vn_period":
        raise ValueError(f"unsupported explicit period event action: {planned_event.action}")
    return ScheduledExplicitPeriodResult(
        event=planned_event,
        explicit_period=run_loaded_explicit_period(loaded, output_dir=output_dir),
    )


def _planned_explicit_vu_vn_period_events(period_scenarios: list[dict]) -> list[Event]:
    scheduler = Scheduler()
    for index, period_scenario in enumerate(period_scenarios):
        loaded = load_scenario_from_mapping(period_scenario)
        scheduler.plan(
            Event(
                period=compute_global_period(loaded.context),
                logtime=loaded.context.logtime,
                priority=index,
                subject_type="scenario",
                subject_id=f"explicit-vu-vn-{index}",
                action="explicit_vu_vn_period",
                payload={
                    "input_index": index,
                    "context_period": loaded.context.period,
                    "run_index": loaded.context.run_index,
                },
            )
        )

    planned_events: list[Event] = []
    while not scheduler.empty():
        event = scheduler.pop()
        if event.action != "explicit_vu_vn_period":
            raise ValueError(f"unsupported explicit period event action: {event.action}")
        planned_events.append(event)
    return planned_events


def run_scheduled_explicit_vu_vn_periods_from_mappings(
    period_scenarios: list[dict],
    *,
    output_dir: str | Path | None = None,
    carry_forward_vu_state: bool = False,
    carry_forward_vn_state: bool = False,
) -> ScheduledExplicitMultiPeriodResult:
    """
    Plant mehrere explizite VU/VN-Periodenschritte und fuehrt den validierten
    Mehrperiodenrunner aus.
    """

    if not isinstance(period_scenarios, list):
        raise ValueError("scheduled explicit VU/VN run requires a list of period scenarios")

    planned_events = _planned_explicit_vu_vn_period_events(period_scenarios)
    return ScheduledExplicitMultiPeriodResult(
        planned_events=planned_events,
        explicit_multi_period=run_explicit_multi_period_from_mappings(
            period_scenarios,
            output_dir=output_dir,
            carry_forward_vu_state=carry_forward_vu_state,
            carry_forward_vn_state=carry_forward_vn_state,
        ),
    )


def _period_scenarios_from_scheduled_fixture_payload(payload: object) -> list[dict]:
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        period_scenarios = payload.get("periods")
        if isinstance(period_scenarios, list):
            return period_scenarios
    raise ValueError("scheduled explicit VU/VN fixture requires a list or object field: periods")


def run_scheduled_explicit_vu_vn_periods_from_fixture(
    path: str | Path,
    *,
    output_dir: str | Path | None = None,
    carry_forward_vu_state: bool = False,
    carry_forward_vn_state: bool = False,
) -> ScheduledExplicitMultiPeriodResult:
    """
    Laedt ein explizites VU/VN-Mehrperioden-Fixture, plant die Periodenereignisse
    und fuehrt den validierten Fixture-Runner aus.
    """

    fixture_path = Path(path)
    with fixture_path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)

    period_scenarios = _period_scenarios_from_scheduled_fixture_payload(payload)
    planned_events = _planned_explicit_vu_vn_period_events(period_scenarios)
    return ScheduledExplicitMultiPeriodResult(
        planned_events=planned_events,
        explicit_multi_period=run_explicit_multi_period_from_fixture(
            fixture_path,
            output_dir=output_dir,
            carry_forward_vu_state=carry_forward_vu_state,
            carry_forward_vn_state=carry_forward_vn_state,
        ),
    )


def run_scheduled_explicit_vu_vn_periods_from_plan_fixture(
    path: str | Path,
    *,
    output_dir: str | Path | None = None,
) -> ScheduledExplicitMultiPeriodResult:
    """
    Laedt ein explizites VU/VN-Periodenplan-Fixture, plant die erzeugten
    Periodenereignisse und fuehrt den validierten Plan-Runner aus.
    """

    plan_path = Path(path)
    with plan_path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)

    fixture = build_explicit_period_fixture_from_plan(payload)
    planned_events = _planned_explicit_vu_vn_period_events(fixture["periods"])
    return ScheduledExplicitMultiPeriodResult(
        planned_events=planned_events,
        explicit_multi_period=run_explicit_multi_period_from_plan_fixture(
            plan_path,
            output_dir=output_dir,
        ),
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

    loaded = _load_initialized_scenario(path, initialize_rng=initialize_rng)

    initial_context = loaded.context
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

    planned_events = [first_event, second_event]
    dispatch_run = _dispatch_planned_events(
        loaded,
        base_context=initial_context,
        planned_events=planned_events,
    )
    return _build_scheduled_sequence_result(
        initial_context=initial_context,
        planned_events=planned_events,
        dispatch_run=dispatch_run,
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

    loaded = _load_initialized_scenario(path, initialize_rng=initialize_rng)

    initial_context = loaded.context
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

    planned_events = [first_event, second_event]
    dispatch_run = _dispatch_planned_events(
        loaded,
        base_context=initial_context,
        planned_events=planned_events,
    )
    return _build_scheduled_sequence_result(
        initial_context=initial_context,
        planned_events=planned_events,
        dispatch_run=dispatch_run,
    )



def run_mixed_bav_event_sequence(
    path: str | Path,
    *,
    initialize_rng: bool = False,
    use_rng_sample: bool = False,
    update_first: bool = True,
) -> ScheduledSequenceResult:
    loaded = _load_initialized_scenario(path, initialize_rng=initialize_rng)

    initial_context = loaded.context
    if update_first:
        first_event = Event(
            period=initial_context.period,
            logtime=initial_context.logtime,
            priority=0,
            subject_type="bav",
            subject_id=loaded.bav.entity_id,
            action="bav_update",
            payload={"use_rng_sample": use_rng_sample},
        )
        second_event = Event(
            period=initial_context.period,
            logtime=initial_context.logtime + 1,
            priority=0,
            subject_type="bav",
            subject_id=loaded.bav.entity_id,
            action="bav_snapshot",
            payload={},
        )
    else:
        first_event = Event(
            period=initial_context.period,
            logtime=initial_context.logtime,
            priority=0,
            subject_type="bav",
            subject_id=loaded.bav.entity_id,
            action="bav_snapshot",
            payload={},
        )
        second_event = Event(
            period=initial_context.period,
            logtime=initial_context.logtime + 1,
            priority=0,
            subject_type="bav",
            subject_id=loaded.bav.entity_id,
            action="bav_update",
            payload={"use_rng_sample": use_rng_sample},
        )

    planned_events = [first_event, second_event]
    dispatch_run = _dispatch_planned_events(
        loaded,
        base_context=initial_context,
        planned_events=planned_events,
    )
    return _build_scheduled_sequence_result(
        initial_context=initial_context,
        planned_events=planned_events,
        dispatch_run=dispatch_run,
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

    loaded = _load_initialized_scenario(path, initialize_rng=initialize_rng)

    planned_events = build_sequenced_bav_events(
        context=loaded.context,
        bav=loaded.bav,
        num_events=num_events,
        use_rng_sample=use_rng_sample,
    )

    dispatch_run = _dispatch_planned_events(
        loaded,
        base_context=loaded.context,
        planned_events=planned_events,
        max_events=max_events,
    )
    return _build_controlled_loop_result(
        initial_context=loaded.context,
        planned_events=planned_events,
        max_events=max_events,
        dispatch_run=dispatch_run,
    )



def run_mixed_controlled_bav_event_loop(
    path: str | Path,
    *,
    initialize_rng: bool = False,
    use_rng_sample: bool = False,
    num_pairs: int = 2,
    max_events: int = 4,
    start_with_update: bool = True,
) -> ControlledLoopResult:
    if num_pairs <= 0:
        raise ValueError("num_pairs must be greater than 0")
    if max_events <= 0:
        raise ValueError("max_events must be greater than 0")

    loaded = _load_initialized_scenario(path, initialize_rng=initialize_rng)

    planned_events = build_mixed_bav_events(
        context=loaded.context,
        bav=loaded.bav,
        num_pairs=num_pairs,
        use_rng_sample=use_rng_sample,
        start_with_update=start_with_update,
    )

    dispatch_run = _dispatch_planned_events(
        loaded,
        base_context=loaded.context,
        planned_events=planned_events,
        max_events=max_events,
    )
    return _build_controlled_loop_result(
        initial_context=loaded.context,
        planned_events=planned_events,
        max_events=max_events,
        dispatch_run=dispatch_run,
    )



def run_progressed_mixed_controlled_bav_event_loop(
    path: str | Path,
    *,
    initialize_rng: bool = False,
    use_rng_sample: bool = False,
    num_pairs: int = 3,
    max_events: int = 6,
    logtimes_per_period: int = 2,
    start_with_update: bool = True,
) -> ControlledLoopResult:
    if num_pairs <= 0:
        raise ValueError("num_pairs must be greater than 0")
    if max_events <= 0:
        raise ValueError("max_events must be greater than 0")
    if logtimes_per_period <= 0:
        raise ValueError("logtimes_per_period must be greater than 0")

    loaded = _load_initialized_scenario(path, initialize_rng=initialize_rng)

    planned_events = build_progressed_mixed_bav_events(
        context=loaded.context,
        bav=loaded.bav,
        num_pairs=num_pairs,
        use_rng_sample=use_rng_sample,
        logtimes_per_period=logtimes_per_period,
        start_with_update=start_with_update,
    )

    dispatch_run = _dispatch_planned_events(
        loaded,
        base_context=loaded.context,
        planned_events=planned_events,
        max_events=max_events,
    )
    return _build_controlled_loop_result(
        initial_context=loaded.context,
        planned_events=planned_events,
        max_events=max_events,
        dispatch_run=dispatch_run,
    )



def run_progressed_bav_event_loop(
    path: str | Path,
    *,
    initialize_rng: bool = False,
    use_rng_sample: bool = False,
    num_events: int = 4,
    max_events: int = 4,
    logtimes_per_period: int = 2,
) -> ControlledLoopResult:
    if num_events <= 0:
        raise ValueError("num_events must be greater than 0")
    if max_events <= 0:
        raise ValueError("max_events must be greater than 0")
    if logtimes_per_period <= 0:
        raise ValueError("logtimes_per_period must be greater than 0")

    loaded = _load_initialized_scenario(path, initialize_rng=initialize_rng)

    planned_events = build_progressed_bav_events(
        context=loaded.context,
        bav=loaded.bav,
        num_events=num_events,
        use_rng_sample=use_rng_sample,
        logtimes_per_period=logtimes_per_period,
    )

    dispatch_run = _dispatch_planned_events(
        loaded,
        base_context=loaded.context,
        planned_events=planned_events,
        max_events=max_events,
    )
    return _build_controlled_loop_result(
        initial_context=loaded.context,
        planned_events=planned_events,
        max_events=max_events,
        dispatch_run=dispatch_run,
    )
