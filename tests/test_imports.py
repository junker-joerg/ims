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
    from ims.analysis.aggregates import AggregateSnapshot, collect_basic_aggregates
    from ims.engine.context import SimulationContext
    from ims.engine.rng import create_rng, rand_int_inclusive, rand_uniform_0_1
    from ims.engine.event_builders import (
        build_mixed_bav_events,
        build_progressed_bav_events,
        build_progressed_mixed_bav_events,
        build_sequenced_bav_events,
    )
    from ims.engine.scheduler import Event, Scheduler
    from ims.engine.simulation import (
        ControlledLoopResult,
        DispatchedEventResult,
        ScheduledSequenceResult,
        SimulationStepResult,
        TwoStepSimulationResult,
        _build_simulation_step_result,
        _dispatch_planned_events,
        _load_initialized_scenario,
        dispatch_event,
        run_controlled_bav_event_loop,
        run_mixed_bav_event_sequence,
        run_mixed_controlled_bav_event_loop,
        run_progressed_bav_event_loop,
        run_progressed_mixed_controlled_bav_event_loop,
        run_scheduled_bav_update,
        run_single_bav_update_step,
        run_two_bav_update_steps,
        run_two_prioritized_bav_updates,
        run_two_scheduled_bav_updates,
    )
    from ims.io.scenario_loader import LoadedScenario, load_scenario
    from ims.model.agrsich_export import (
        ExportFileSpec,
        ExportRow,
        ExportTable,
        build_agrsich_export_tables,
        compute_global_period,
    )
    from ims.model.agrsich_service import (
        AggregateRecord,
        AgrsichResult,
        collect_basic_agrsich_records,
        collect_extended_agrsich_records,
        refresh_bav_aggregate_state,
    )
    from ims.model.bav_service import (
        BAVForeignInfoResult,
        compute_basic_foreign_info,
        compute_extended_foreign_info,
        initialize_bav_first_run,
        initialize_bav_followup_run,
        refresh_bav_activity_state,
    )
    from ims.model.bav_updates import BAVUpdateResult, update_bav_central_state
    from ims.model.entities import (
        BAV,
        BAVActivityState,
        BAVAggregateState,
        BAVForeignInfoInsurer,
        BAVForeignInfoPolicyholder,
        BAVServiceComputationMeta,
        BAVServiceState,
        BaseEntity,
        Insurer,
        Policyholder,
    )

    ctx = SimulationContext()
    scheduler = Scheduler()
    entity = BaseEntity(entity_id=1)
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
    assert build_sequenced_bav_events is not None
    assert build_progressed_bav_events is not None
    assert build_mixed_bav_events is not None
    assert build_progressed_mixed_bav_events is not None
    assert scheduler.empty() is False
    assert entity.entity_id == 1
    assert bav.entity_id == 1
    assert insurer.entity_id == 101
    assert policyholder.entity_id == 201
    assert isinstance(bav.service_state, BAVServiceState)
    assert isinstance(bav.service_state.insurer, BAVForeignInfoInsurer)
    assert isinstance(bav.service_state.policyholder, BAVForeignInfoPolicyholder)
    assert isinstance(bav.service_state.activity_state, BAVActivityState)
    assert isinstance(bav.service_state.aggregate_state, BAVAggregateState)
    assert isinstance(bav.service_state.computation_meta, BAVServiceComputationMeta)
    assert LoadedScenario is not None
    assert load_scenario is not None
    assert AggregateSnapshot is not None
    assert collect_basic_aggregates is not None
    assert ExportFileSpec is not None
    assert ExportRow is not None
    assert ExportTable is not None
    assert build_agrsich_export_tables is not None
    assert compute_global_period is not None
    assert AggregateRecord is not None
    assert AgrsichResult is not None
    assert refresh_bav_aggregate_state is not None
    assert collect_basic_agrsich_records is not None
    assert collect_extended_agrsich_records is not None
    assert BAVForeignInfoResult is not None
    assert compute_basic_foreign_info is not None
    assert compute_extended_foreign_info is not None
    assert refresh_bav_activity_state is not None
    assert initialize_bav_first_run is not None
    assert initialize_bav_followup_run is not None
    assert BAVUpdateResult is not None
    assert update_bav_central_state is not None
    assert SimulationStepResult is not None
    assert TwoStepSimulationResult is not None
    assert _build_simulation_step_result is not None
    assert _dispatch_planned_events is not None
    assert _load_initialized_scenario is not None
    assert ControlledLoopResult is not None
    assert DispatchedEventResult is not None
    assert ScheduledSequenceResult is not None
    assert dispatch_event is not None
    assert run_controlled_bav_event_loop is not None
    assert run_mixed_bav_event_sequence is not None
    assert run_mixed_controlled_bav_event_loop is not None
    assert run_progressed_bav_event_loop is not None
    assert run_progressed_mixed_controlled_bav_event_loop is not None
    assert run_scheduled_bav_update is not None
    assert run_single_bav_update_step is not None
    assert run_two_bav_update_steps is not None
    assert run_two_scheduled_bav_updates is not None
    assert run_two_prioritized_bav_updates is not None
    assert insurer.active_prev is True
    assert insurer.rule_id is None
    assert insurer.rule_class is None
    assert insurer.premiums_current == 0.0
    assert insurer.claims_count_current == [0, 0]
    assert insurer.claims_sum_current == [0.0, 0.0]
    assert policyholder.active_prev is True
    assert policyholder.rule_id is None
    assert policyholder.rule_class is None
    assert policyholder.chosen_insurer_current is None
    assert policyholder.paid_premium_current == [0.0, 0.0]
    assert policyholder.self_damage_current == [0.0, 0.0]
    assert policyholder.claim_sum_current == [0.0, 0.0]
    assert policyholder.end_wealth_current == 0.0
    assert rand_uniform_0_1(rng) >= 0.0
    assert rand_int_inclusive(rng, 1, 1) == 1
