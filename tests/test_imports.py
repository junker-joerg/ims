def test_package_imports() -> None:
    import ims
    import ims.model
    import ims.engine
    import ims.io
    import ims.analysis

    assert ims is not None
    assert ims.model is not None
    assert ims.engine is not None
    assert ims.io is not None
    assert ims.analysis is not None


def test_core_placeholders_import() -> None:
    from ims.engine.context import SimulationContext
    from ims.engine.scheduler import Event, Scheduler
    from ims.model.entities import BaseEntity
    from ims.analysis.aggregates import AggregateSnapshot, collect_basic_aggregates
    from ims.engine.context import SimulationContext
    from ims.engine.rng import create_rng, rand_int_inclusive, rand_uniform_0_1
    from ims.engine.scheduler import Event, Scheduler
    from ims.engine.simulation import (
        ControlledLoopResult,
        DispatchedEventResult,
        ScheduledSequenceResult,
        SimulationStepResult,
        TwoStepSimulationResult,
        dispatch_event,
        run_controlled_bav_event_loop,
        run_mixed_bav_event_sequence,
        run_progressed_bav_event_loop,
        run_scheduled_bav_update,
        run_single_bav_update_step,
        run_two_bav_update_steps,
        run_two_prioritized_bav_updates,
        run_two_scheduled_bav_updates,
    )
    from ims.io.scenario_loader import LoadedScenario, load_scenario
    from ims.model.bav_updates import BAVUpdateResult, update_bav_central_state
    from ims.engine.context import SimulationContext, ensure_context_rng
    from ims.analysis.aggregates import AggregateSnapshot, collect_basic_aggregates
    from ims.engine.rng import create_rng, rand_int_inclusive, rand_uniform_0_1
    from ims.engine.scheduler import Event, Scheduler
    from ims.engine.simulation import (
        SimulationStepResult,
        TwoStepSimulationResult,
        run_single_bav_update_step,
        run_two_bav_update_steps,
    )
    from ims.io.scenario_loader import LoadedScenario, load_scenario
    from ims.model.bav_updates import BAVUpdateResult, update_bav_central_state
    from ims.engine.simulation import SimulationStepResult, run_single_bav_update_step
    from ims.io.scenario_loader import LoadedScenario, load_scenario
    from ims.model.bav_updates import BAVUpdateResult, update_bav_central_state
    from ims.engine.context import SimulationContext
    from ims.analysis.aggregates import AggregateSnapshot, collect_basic_aggregates
    from ims.engine.scheduler import Event, Scheduler
    from ims.io.scenario_loader import LoadedScenario, load_scenario
    from ims.model.entities import BAV, BaseEntity, Insurer, Policyholder

    ctx = SimulationContext()
    scheduler = Scheduler()
    entity = BaseEntity(entity_id=1)
    event = Event(0, 0, 0, "entity", 1, "noop")

    assert ctx.period == 0
    assert ctx.max_periods == 0
    assert scheduler.empty() is True
    assert entity.entity_id == 1
    assert event.action == "noop"
    bav = BAV(entity_id=1)
    insurer = Insurer(entity_id=101)
    policyholder = Policyholder(entity_id=201)
    rng = create_rng(1995)

    event = Event(
        period=0,
        logtime=0,
        priority=0,
        subject_type="test",
        subject_id=1,
        action="noop",
    )

    scheduler.plan(event)

    assert ctx.period == 0
    assert scheduler.empty() is False
    assert entity.entity_id == 1
    assert bav.entity_id == 1
    assert insurer.entity_id == 101
    assert policyholder.entity_id == 201
    assert LoadedScenario is not None
    assert load_scenario is not None
    assert AggregateSnapshot is not None
    assert collect_basic_aggregates is not None
    assert BAVUpdateResult is not None
    assert update_bav_central_state is not None
    assert SimulationStepResult is not None
    assert TwoStepSimulationResult is not None
    assert ControlledLoopResult is not None
    assert DispatchedEventResult is not None
    assert ScheduledSequenceResult is not None
    assert dispatch_event is not None
    assert run_controlled_bav_event_loop is not None
    assert run_mixed_bav_event_sequence is not None
    assert run_progressed_bav_event_loop is not None
    assert DispatchedEventResult is not None
    assert ScheduledSequenceResult is not None
    assert dispatch_event is not None
    assert run_scheduled_bav_update is not None
    assert run_single_bav_update_step is not None
    assert run_two_bav_update_steps is not None
    assert run_two_scheduled_bav_updates is not None
    assert run_two_prioritized_bav_updates is not None
    assert rand_uniform_0_1(rng) >= 0.0
    assert rand_int_inclusive(rng, 1, 1) == 1
    event = Event(0, 0, 0, "entity", 1, "noop")
    rng = create_rng(123)
    scenario = load_scenario("tests/fixtures/minimal_scenario.json")
    simulation_result = run_single_bav_update_step("tests/fixtures/minimal_scenario.json")
    two_step_result = run_two_bav_update_steps("tests/fixtures/minimal_scenario.json")
    scenario = load_scenario("tests/fixtures/minimal_scenario.json")
    snapshot = collect_basic_aggregates(
        scenario.context,
        scenario.bav,
        scenario.insurers,
        scenario.policyholders,
    )

    assert ctx.period == 0
    assert ensure_context_rng(SimulationContext(rng_seed=123)) is not None
    assert SimulationContext(period=0, logtime=0).advanced(logtime_increment=1).logtime == 1
    assert scheduler.empty() is True
    assert entity.entity_id == 1
    assert event.action == "noop"
    assert 0.0 <= rand_uniform_0_1(rng) < 1.0
    assert 1 <= rand_int_inclusive(create_rng(123), 1, 3) <= 3
    update_result = update_bav_central_state(
        scenario.context,
        scenario.bav,
        scenario.insurers,
        scenario.policyholders,
    )

    assert scheduler.empty() is True
    assert entity.entity_id == 1
    assert event.action == "noop"
    assert BAV is not None
    assert Insurer is not None
    assert Policyholder is not None
    assert isinstance(scenario, LoadedScenario)
    assert isinstance(snapshot, AggregateSnapshot)
    assert snapshot.assigned_policyholders == 1
    assert isinstance(update_result, BAVUpdateResult)
    assert update_result.active_policyholder_count == 1
    assert isinstance(simulation_result, SimulationStepResult)
    assert simulation_result.aggregate_snapshot.assigned_policyholders == 1
    assert isinstance(two_step_result, TwoStepSimulationResult)
    assert two_step_result.second_step.aggregate_snapshot.assigned_policyholders == 1
"""Import smoke tests for the IMS Python scaffold."""

import importlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "python_port"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

MODULES = [
    "ims",
    "ims.model",
    "ims.model.entities",
    "ims.engine",
    "ims.engine.context",
    "ims.engine.scheduler",
    "ims.io",
    "ims.analysis",
]


def test_scaffold_modules_are_importable() -> None:
    for module_name in MODULES:
        assert importlib.import_module(module_name) is not None
