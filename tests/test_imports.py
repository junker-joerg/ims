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
    from ims.engine.event_builders import (
        build_mixed_bav_events,
        build_progressed_bav_events,
        build_progressed_mixed_bav_events,
        build_sequenced_bav_events,
    )
    from ims.engine.rng import create_rng, rand_int_inclusive, rand_uniform_0_1
    from ims.engine.replay_runner import (
        ReplayPeriodResult,
        ReplayRunResult,
        ReplaySnapshot,
        ReplayWindowTarget,
        run_agrsich_replay_from_fixture,
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
    from ims.engine.vu_rule_runner import (
        VUForeignInfoCarryover,
        VUForeignInfoMultiPeriodRunResult,
        VUForeignInfoPeriodRunResult,
        run_loaded_vu_foreign_info_period,
        run_vu_foreign_info_multi_period_from_fixture,
        run_vu_foreign_info_multi_period_from_mappings,
        run_vu_foreign_info_period_from_fixture,
        run_vu_foreign_info_period_from_mapping,
    )
    from ims.engine.vn_rule_runner import VNSettlementPeriodRunResult, run_vn_settlement_period
    from ims.io.scenario_loader import LoadedScenario, load_scenario, load_scenario_from_mapping
    from ims.model.agrsich_export import (
        ExportFileSpec,
        ExportRow,
        ExportTable,
        build_agrsich_export_tables,
        compute_global_period,
        render_export_header,
        render_export_row,
    )
    from ims.model.agrsich_service import (
        AggregateRecord,
        AgrsichResult,
        collect_basic_agrsich_records,
        collect_extended_agrsich_records,
        refresh_bav_aggregate_state,
    )
    from ims.model.agrsich_writer import (
        ComparisonResult,
        FileComparison,
        compare_export_files_to_reference,
        write_agrsich_export_tables,
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
    from ims.model.legacy_agrsich_multi_period import (
        LegacyTableComparison,
        MultiPeriodLegacyComparison,
        build_multi_period_legacy_comparison,
        compare_insurer_export_table_to_legacy,
        compare_policyholder_export_table_to_legacy,
    )
    from ims.model.legacy_agrsich_reference import (
        LegacyComparison,
        LegacyFieldComparison,
        LegacyInsurerRow,
        LegacyInsurerTable,
        LegacyRowComparison,
        LegacyWindowComparison,
        compare_export_record_to_legacy_row,
        compare_export_file_to_legacy_window,
        extract_legacy_row,
        extract_legacy_window,
        parse_legacy_insurer_dat,
    )
    from ims.model.legacy_vn_reference import (
        LegacyPolicyholderComparison,
        LegacyPolicyholderFieldComparison,
        LegacyPolicyholderRow,
        LegacyPolicyholderTable,
        compare_policyholder_export_record_to_legacy_row,
        extract_legacy_policyholder_row,
        parse_legacy_policyholder_dat,
    )
    from ims.model.legacy_validation_report import (
        LegacyFieldDeviation,
        LegacyFieldDeviationSummary,
        LegacyFileValidationSummary,
        LegacyValidationDeviationRecord,
        LegacyValidationReport,
        LegacyValidationGroupSummary,
        LegacyValidationPeriodSummary,
        build_legacy_file_validation_summary,
        build_legacy_table_validation_summary,
        build_legacy_validation_report,
        build_legacy_validation_report_from_multi_period_comparison,
        build_legacy_validation_report_from_table_comparisons,
        legacy_validation_report_to_dict,
        write_legacy_validation_deviation_index_csv,
        write_legacy_validation_field_summary_csv,
        write_legacy_validation_group_summary_csv,
        write_legacy_validation_period_summary_csv,
        write_legacy_validation_report_csv,
        write_legacy_validation_report_json,
    )
    from ims.model.legacy_validation_run import (
        LegacyValidationArtifact,
        LegacyValidationArtifactManifest,
        LegacyValidationBatchRunManifestCheck,
        LegacyValidationBatchRunManifestCheckBundle,
        LegacyValidationBatchRunManifestCheckBundleArtifactManifest,
        LegacyValidationBatchRunManifestIssue,
        LegacyValidationBatchRunManifestCheckPayloadSummary,
        LegacyValidationBatchRunManifestCheckPayloadSummaryArtifactManifest,
        LegacyValidationBatchRunManifestCheckPayloadSummaryBundle,
        LegacyValidationBatchRunManifestCheckPayloadSummaryBundleArtifactManifest,
        LegacyValidationAcceptanceVerdict,
        LegacyValidationAcceptanceVerdictArtifactManifest,
        LegacyValidationAcceptanceRunResult,
        LegacyValidationAcceptanceRunManifest,
        LegacyValidationBatchRunItem,
        LegacyValidationBatchRunResult,
        LegacyValidationReportPayloadSummary,
        LegacyValidationReportSummaryBundle,
        LegacyValidationReportSummaryBundleArtifactManifest,
        LegacyValidationRunResult,
        LegacyValidationTarget,
        build_legacy_validation_batch_run_manifest_check_payload_summary,
        build_legacy_validation_batch_run_manifest_check_payload_summary_bundle,
        build_legacy_validation_acceptance_verdict,
        build_legacy_validation_acceptance_verdict_from_summary_bundle_manifest,
        build_legacy_validation_report_summary_bundle,
        check_legacy_validation_batch_run_manifest,
        check_legacy_validation_batch_run_manifests,
        check_legacy_validation_batch_run_manifests_from_directory,
        legacy_validation_batch_run_manifest_check_bundle_to_dict,
        legacy_validation_batch_run_manifest_check_payload_summary_bundle_to_dict,
        legacy_validation_batch_run_manifest_check_payload_summary_to_dict,
        legacy_validation_acceptance_verdict_to_dict,
        legacy_validation_batch_run_manifest_check_to_dict,
        legacy_validation_batch_run_result_to_dict,
        legacy_validation_report_payload_summary_to_dict,
        legacy_validation_report_summary_bundle_to_dict,
        load_legacy_validation_batch_run_manifest,
        load_legacy_validation_batch_run_manifest_check_bundle_artifact_manifest,
        load_legacy_validation_batch_run_manifest_check_bundle_payload_from_manifest,
        load_legacy_validation_batch_run_manifest_check_bundle_payloads_from_directory,
        load_legacy_validation_batch_run_manifest_check_payload_summary_artifact_manifest,
        load_legacy_validation_batch_run_manifest_check_payload_summary_from_manifest,
        load_legacy_validation_batch_run_manifest_check_payload_summary_payloads_from_directory,
        load_legacy_validation_batch_run_manifest_check_payload_summary_bundle_artifact_manifest,
        load_legacy_validation_batch_run_manifest_check_payload_summary_bundle_from_manifest,
        load_legacy_validation_acceptance_verdict_artifact_manifest,
        load_legacy_validation_acceptance_verdict_from_manifest,
        load_legacy_validation_acceptance_run_manifest,
        load_legacy_validation_artifact_manifest,
        load_legacy_validation_report_payload_from_manifest,
        load_legacy_validation_report_summary_bundle_artifact_manifest,
        load_legacy_validation_report_summary_bundle_payload_from_manifest,
        run_legacy_validation_batch_from_fixture,
        run_legacy_validation_from_fixture,
        summarize_legacy_validation_batch_run_manifest_check_payload_summaries_from_directory,
        summarize_legacy_validation_batch_run_manifest_check_payloads_from_directory,
        summarize_legacy_validation_report_payload_from_manifest,
        summarize_legacy_validation_report_payloads_from_directory,
        summarize_legacy_validation_report_payloads_from_manifests,
        write_legacy_validation_report_summary_bundle_artifacts,
        write_legacy_validation_report_summary_bundle_artifacts_from_directory,
        write_legacy_validation_report_summary_bundle_artifacts_from_manifests,
        write_legacy_validation_report_summary_bundle_csv,
        write_legacy_validation_report_summary_bundle_json,
        write_legacy_validation_batch_run_manifest,
        write_legacy_validation_batch_run_manifest_check_bundle_artifacts,
        write_legacy_validation_batch_run_manifest_check_bundle_artifacts_from_directory,
        write_legacy_validation_batch_run_manifest_check_bundle_artifacts_from_manifests,
        write_legacy_validation_batch_run_manifest_check_bundle_csv,
        write_legacy_validation_batch_run_manifest_check_bundle_json,
        write_legacy_validation_batch_run_manifest_check_payload_summary_artifacts,
        write_legacy_validation_batch_run_manifest_check_payload_summary_artifacts_from_directory,
        write_legacy_validation_batch_run_manifest_check_payload_summary_csv,
        write_legacy_validation_batch_run_manifest_check_payload_summary_json,
        write_legacy_validation_batch_run_manifest_check_payload_summary_bundle_artifacts,
        write_legacy_validation_batch_run_manifest_check_payload_summary_bundle_artifacts_from_directory,
        write_legacy_validation_batch_run_manifest_check_payload_summary_bundle_csv,
        write_legacy_validation_batch_run_manifest_check_payload_summary_bundle_json,
        write_legacy_validation_acceptance_verdict_artifacts,
        write_legacy_validation_acceptance_verdict_artifacts_from_summary_bundle_manifest,
        write_legacy_validation_acceptance_verdict_csv,
        write_legacy_validation_acceptance_verdict_json,
        write_legacy_validation_acceptance_run_manifest,
        write_legacy_validation_acceptance_run_artifacts_from_summary_directory,
    )
    from ims.model.vn_rules import (
        VNSectorSettlementDecision,
        VNSettlementApplication,
        VNSettlementResult,
        VNSettlementSnapshot,
        apply_vn_settlement_snapshot,
        apply_vn_settlement_snapshots,
        load_vn_settlement_snapshots_from_mapping,
        vn_sector_settlement_decision_from_mapping,
        vn_settlement_snapshot_from_mapping,
    )
    from ims.model.vu_rules import (
        VUExpectedClaimRuleApplication,
        VUExpectedClaimRuleParameters,
        VUExpectedClaimRuleResult,
        VUExpectedClaimRuleSnapshot,
        VUFreeLinearRuleApplication,
        VUFreeLinearRuleParameters,
        VUFreeLinearRuleResult,
        VUFreeLinearRuleSnapshot,
        VUForeignInfoRuleApplication,
        VUForeignInfoRuleKind,
        VUForeignInfoRuleParameters,
        VUForeignInfoRuleResult,
        VUForeignInfoRuleSnapshot,
        VUMarketShareMarkupRuleApplication,
        VUMarketShareMarkupRuleParameters,
        VUMarketShareMarkupRuleResult,
        VUMarketShareMarkupRuleSnapshot,
        VUNetSwitcherMarkupRuleApplication,
        VUNetSwitcherMarkupRuleParameters,
        VUNetSwitcherMarkupRuleResult,
        VUNetSwitcherMarkupRuleSnapshot,
        VURandomNormalRuleApplication,
        VURandomNormalRuleParameters,
        VURandomNormalRuleResult,
        VURandomNormalRuleSnapshot,
        VURandomUniformRuleApplication,
        VURandomUniformRuleParameters,
        VURandomUniformRuleResult,
        VURandomUniformRuleSnapshot,
        VUReserveMarkupRuleApplication,
        VUReserveMarkupRuleParameters,
        VUReserveMarkupRuleResult,
        VUReserveMarkupRuleSnapshot,
        apply_vu_expected_claim_rule,
        apply_vu_expected_claim_rule_snapshots,
        apply_vu_expected_claim_rule_to_insurer,
        apply_vu_free_linear_rule,
        apply_vu_free_linear_rule_snapshots,
        apply_vu_free_linear_rule_to_insurer,
        apply_vu_foreign_info_rule,
        apply_vu_foreign_info_rule_snapshots,
        apply_vu_foreign_info_rule_to_insurer,
        apply_vu_market_share_markup_rule,
        apply_vu_market_share_markup_rule_snapshots,
        apply_vu_market_share_markup_rule_to_insurer,
        apply_vu_net_switcher_markup_rule,
        apply_vu_net_switcher_markup_rule_snapshots,
        apply_vu_net_switcher_markup_rule_to_insurer,
        apply_vu_random_normal_rule,
        apply_vu_random_normal_rule_snapshots,
        apply_vu_random_normal_rule_to_insurer,
        apply_vu_random_uniform_rule,
        apply_vu_random_uniform_rule_snapshots,
        apply_vu_random_uniform_rule_to_insurer,
        apply_vu_reserve_markup_rule,
        apply_vu_reserve_markup_rule_snapshots,
        apply_vu_reserve_markup_rule_to_insurer,
        load_vu_expected_claim_rule_snapshots_from_mapping,
        load_vu_free_linear_rule_snapshots_from_mapping,
        load_vu_foreign_info_rule_snapshots_from_mapping,
        load_vu_market_share_markup_rule_snapshots_from_mapping,
        load_vu_net_switcher_markup_rule_snapshots_from_mapping,
        load_vu_random_normal_rule_snapshots_from_mapping,
        load_vu_random_uniform_rule_snapshots_from_mapping,
        load_vu_reserve_markup_rule_snapshots_from_mapping,
        vu_expected_claim_rule_parameters_from_mapping,
        vu_expected_claim_rule_snapshot_from_mapping,
        vu_free_linear_rule_parameters_from_mapping,
        vu_free_linear_rule_snapshot_from_mapping,
        vu_foreign_info_rule_parameters_from_mapping,
        vu_foreign_info_rule_snapshot_from_mapping,
        vu_market_share_markup_rule_parameters_from_mapping,
        vu_market_share_markup_rule_snapshot_from_mapping,
        vu_net_switcher_markup_rule_parameters_from_mapping,
        vu_net_switcher_markup_rule_snapshot_from_mapping,
        vu_random_normal_rule_parameters_from_mapping,
        vu_random_normal_rule_snapshot_from_mapping,
        vu_random_uniform_rule_parameters_from_mapping,
        vu_random_uniform_rule_snapshot_from_mapping,
        vu_reserve_markup_rule_parameters_from_mapping,
        vu_reserve_markup_rule_snapshot_from_mapping,
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
    assert load_scenario_from_mapping is not None
    assert AggregateSnapshot is not None
    assert collect_basic_aggregates is not None
    assert ExportFileSpec is not None
    assert ExportRow is not None
    assert ExportTable is not None
    assert build_agrsich_export_tables is not None
    assert compute_global_period is not None
    assert render_export_header is not None
    assert render_export_row is not None
    assert AggregateRecord is not None
    assert AgrsichResult is not None
    assert refresh_bav_aggregate_state is not None
    assert collect_basic_agrsich_records is not None
    assert collect_extended_agrsich_records is not None
    assert FileComparison is not None
    assert ComparisonResult is not None
    assert write_agrsich_export_tables is not None
    assert compare_export_files_to_reference is not None
    assert LegacyTableComparison is not None
    assert MultiPeriodLegacyComparison is not None
    assert compare_insurer_export_table_to_legacy is not None
    assert compare_policyholder_export_table_to_legacy is not None
    assert build_multi_period_legacy_comparison is not None
    assert LegacyInsurerRow is not None
    assert LegacyInsurerTable is not None
    assert LegacyFieldComparison is not None
    assert LegacyComparison is not None
    assert LegacyRowComparison is not None
    assert LegacyWindowComparison is not None
    assert parse_legacy_insurer_dat is not None
    assert extract_legacy_row is not None
    assert extract_legacy_window is not None
    assert compare_export_record_to_legacy_row is not None
    assert compare_export_file_to_legacy_window is not None
    assert LegacyPolicyholderRow is not None
    assert LegacyPolicyholderTable is not None
    assert LegacyPolicyholderFieldComparison is not None
    assert LegacyPolicyholderComparison is not None
    assert parse_legacy_policyholder_dat is not None
    assert extract_legacy_policyholder_row is not None
    assert compare_policyholder_export_record_to_legacy_row is not None
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
    assert VUForeignInfoCarryover is not None
    assert VUForeignInfoMultiPeriodRunResult is not None
    assert VUForeignInfoPeriodRunResult is not None
    assert VNSettlementPeriodRunResult is not None
    assert run_loaded_vu_foreign_info_period is not None
    assert run_vu_foreign_info_multi_period_from_fixture is not None
    assert run_vu_foreign_info_multi_period_from_mappings is not None
    assert run_vu_foreign_info_period_from_fixture is not None
    assert run_vu_foreign_info_period_from_mapping is not None
    assert run_vn_settlement_period is not None
    assert insurer.active_prev is True
    assert insurer.rule_id is None
    assert insurer.rule_class is None
    assert insurer.premiums_current == 0.0
    assert insurer.reserves_current == [0.0, 0.0]
    assert insurer.claims_count_current == [0, 0]
    assert insurer.claims_sum_current == [0.0, 0.0]
    assert policyholder.active_prev is True
    assert policyholder.rule_id is None
    assert policyholder.rule_class is None
    assert policyholder.insured_current_sector == []
    assert policyholder.chosen_insurer_current is None
    assert policyholder.chosen_insurer_sector_current == [None, None]
    assert policyholder.paid_premium_current == [0.0, 0.0]
    assert policyholder.self_damage_current == [0.0, 0.0]
    assert policyholder.claim_sum_current == [0.0, 0.0]
    assert policyholder.end_wealth_sector_current == [0.0, 0.0]
    assert policyholder.end_wealth_current == 0.0
    assert rand_uniform_0_1(rng) >= 0.0
    assert rand_int_inclusive(rng, 1, 1) == 1
    assert ReplaySnapshot is not None
    assert ReplayWindowTarget is not None
    assert ReplayPeriodResult is not None
    assert ReplayRunResult is not None
    assert run_agrsich_replay_from_fixture is not None
    assert LegacyFieldDeviation is not None
    assert LegacyFieldDeviationSummary is not None
    assert LegacyFileValidationSummary is not None
    assert LegacyValidationDeviationRecord is not None
    assert LegacyValidationReport is not None
    assert LegacyValidationGroupSummary is not None
    assert LegacyValidationPeriodSummary is not None
    assert build_legacy_file_validation_summary is not None
    assert build_legacy_table_validation_summary is not None
    assert build_legacy_validation_report is not None
    assert build_legacy_validation_report_from_table_comparisons is not None
    assert build_legacy_validation_report_from_multi_period_comparison is not None
    assert legacy_validation_report_to_dict is not None
    assert write_legacy_validation_deviation_index_csv is not None
    assert write_legacy_validation_field_summary_csv is not None
    assert write_legacy_validation_group_summary_csv is not None
    assert write_legacy_validation_period_summary_csv is not None
    assert write_legacy_validation_report_json is not None
    assert write_legacy_validation_report_csv is not None
    assert LegacyValidationArtifact is not None
    assert LegacyValidationArtifactManifest is not None
    assert LegacyValidationBatchRunManifestCheck is not None
    assert LegacyValidationBatchRunManifestCheckBundle is not None
    assert LegacyValidationBatchRunManifestCheckBundleArtifactManifest is not None
    assert LegacyValidationBatchRunManifestIssue is not None
    assert LegacyValidationBatchRunManifestCheckPayloadSummary is not None
    assert LegacyValidationBatchRunManifestCheckPayloadSummaryArtifactManifest is not None
    assert LegacyValidationBatchRunManifestCheckPayloadSummaryBundle is not None
    assert LegacyValidationBatchRunManifestCheckPayloadSummaryBundleArtifactManifest is not None
    assert LegacyValidationAcceptanceVerdict is not None
    assert LegacyValidationAcceptanceVerdictArtifactManifest is not None
    assert LegacyValidationAcceptanceRunResult is not None
    assert LegacyValidationAcceptanceRunManifest is not None
    assert LegacyValidationBatchRunItem is not None
    assert LegacyValidationBatchRunResult is not None
    assert LegacyValidationReportPayloadSummary is not None
    assert LegacyValidationReportSummaryBundle is not None
    assert LegacyValidationReportSummaryBundleArtifactManifest is not None
    assert LegacyValidationRunResult is not None
    assert LegacyValidationTarget is not None
    assert build_legacy_validation_batch_run_manifest_check_payload_summary is not None
    assert build_legacy_validation_batch_run_manifest_check_payload_summary_bundle is not None
    assert build_legacy_validation_acceptance_verdict is not None
    assert build_legacy_validation_acceptance_verdict_from_summary_bundle_manifest is not None
    assert build_legacy_validation_report_summary_bundle is not None
    assert check_legacy_validation_batch_run_manifest is not None
    assert check_legacy_validation_batch_run_manifests is not None
    assert check_legacy_validation_batch_run_manifests_from_directory is not None
    assert legacy_validation_batch_run_manifest_check_bundle_to_dict is not None
    assert legacy_validation_batch_run_manifest_check_payload_summary_bundle_to_dict is not None
    assert legacy_validation_batch_run_manifest_check_payload_summary_to_dict is not None
    assert legacy_validation_acceptance_verdict_to_dict is not None
    assert legacy_validation_batch_run_manifest_check_to_dict is not None
    assert legacy_validation_batch_run_result_to_dict is not None
    assert legacy_validation_report_payload_summary_to_dict is not None
    assert legacy_validation_report_summary_bundle_to_dict is not None
    assert load_legacy_validation_batch_run_manifest is not None
    assert load_legacy_validation_batch_run_manifest_check_bundle_artifact_manifest is not None
    assert load_legacy_validation_batch_run_manifest_check_bundle_payload_from_manifest is not None
    assert load_legacy_validation_batch_run_manifest_check_bundle_payloads_from_directory is not None
    assert load_legacy_validation_batch_run_manifest_check_payload_summary_artifact_manifest is not None
    assert load_legacy_validation_batch_run_manifest_check_payload_summary_from_manifest is not None
    assert load_legacy_validation_batch_run_manifest_check_payload_summary_payloads_from_directory is not None
    assert load_legacy_validation_batch_run_manifest_check_payload_summary_bundle_artifact_manifest is not None
    assert load_legacy_validation_batch_run_manifest_check_payload_summary_bundle_from_manifest is not None
    assert load_legacy_validation_acceptance_verdict_artifact_manifest is not None
    assert load_legacy_validation_acceptance_verdict_from_manifest is not None
    assert load_legacy_validation_acceptance_run_manifest is not None
    assert load_legacy_validation_artifact_manifest is not None
    assert load_legacy_validation_report_payload_from_manifest is not None
    assert load_legacy_validation_report_summary_bundle_artifact_manifest is not None
    assert load_legacy_validation_report_summary_bundle_payload_from_manifest is not None
    assert run_legacy_validation_batch_from_fixture is not None
    assert run_legacy_validation_from_fixture is not None
    assert summarize_legacy_validation_batch_run_manifest_check_payload_summaries_from_directory is not None
    assert summarize_legacy_validation_batch_run_manifest_check_payloads_from_directory is not None
    assert summarize_legacy_validation_report_payload_from_manifest is not None
    assert summarize_legacy_validation_report_payloads_from_directory is not None
    assert summarize_legacy_validation_report_payloads_from_manifests is not None
    assert write_legacy_validation_report_summary_bundle_artifacts is not None
    assert write_legacy_validation_report_summary_bundle_artifacts_from_directory is not None
    assert write_legacy_validation_report_summary_bundle_artifacts_from_manifests is not None
    assert write_legacy_validation_report_summary_bundle_csv is not None
    assert write_legacy_validation_report_summary_bundle_json is not None
    assert write_legacy_validation_batch_run_manifest is not None
    assert write_legacy_validation_batch_run_manifest_check_bundle_artifacts is not None
    assert write_legacy_validation_batch_run_manifest_check_bundle_artifacts_from_directory is not None
    assert write_legacy_validation_batch_run_manifest_check_bundle_artifacts_from_manifests is not None
    assert write_legacy_validation_batch_run_manifest_check_bundle_csv is not None
    assert write_legacy_validation_batch_run_manifest_check_bundle_json is not None
    assert write_legacy_validation_batch_run_manifest_check_payload_summary_artifacts is not None
    assert write_legacy_validation_batch_run_manifest_check_payload_summary_artifacts_from_directory is not None
    assert write_legacy_validation_batch_run_manifest_check_payload_summary_csv is not None
    assert write_legacy_validation_batch_run_manifest_check_payload_summary_json is not None
    assert write_legacy_validation_batch_run_manifest_check_payload_summary_bundle_artifacts is not None
    assert write_legacy_validation_batch_run_manifest_check_payload_summary_bundle_artifacts_from_directory is not None
    assert write_legacy_validation_batch_run_manifest_check_payload_summary_bundle_csv is not None
    assert write_legacy_validation_batch_run_manifest_check_payload_summary_bundle_json is not None
    assert write_legacy_validation_acceptance_verdict_artifacts is not None
    assert write_legacy_validation_acceptance_verdict_artifacts_from_summary_bundle_manifest is not None
    assert write_legacy_validation_acceptance_verdict_csv is not None
    assert write_legacy_validation_acceptance_verdict_json is not None
    assert write_legacy_validation_acceptance_run_manifest is not None
    assert write_legacy_validation_acceptance_run_artifacts_from_summary_directory is not None
    assert VNSectorSettlementDecision is not None
    assert VNSettlementApplication is not None
    assert VNSettlementResult is not None
    assert VNSettlementSnapshot is not None
    assert apply_vn_settlement_snapshot is not None
    assert apply_vn_settlement_snapshots is not None
    assert load_vn_settlement_snapshots_from_mapping is not None
    assert vn_sector_settlement_decision_from_mapping is not None
    assert vn_settlement_snapshot_from_mapping is not None
    assert VUForeignInfoRuleKind is not None
    assert VUForeignInfoRuleParameters is not None
    assert VUForeignInfoRuleResult is not None
    assert VUForeignInfoRuleSnapshot is not None
    assert VUForeignInfoRuleApplication is not None
    assert VUMarketShareMarkupRuleApplication is not None
    assert VUMarketShareMarkupRuleParameters is not None
    assert VUMarketShareMarkupRuleResult is not None
    assert VUMarketShareMarkupRuleSnapshot is not None
    assert VUNetSwitcherMarkupRuleApplication is not None
    assert VUNetSwitcherMarkupRuleParameters is not None
    assert VUNetSwitcherMarkupRuleResult is not None
    assert VUNetSwitcherMarkupRuleSnapshot is not None
    assert VURandomNormalRuleApplication is not None
    assert VURandomNormalRuleParameters is not None
    assert VURandomNormalRuleResult is not None
    assert VURandomNormalRuleSnapshot is not None
    assert VURandomUniformRuleApplication is not None
    assert VURandomUniformRuleParameters is not None
    assert VURandomUniformRuleResult is not None
    assert VURandomUniformRuleSnapshot is not None
    assert VUExpectedClaimRuleApplication is not None
    assert VUExpectedClaimRuleParameters is not None
    assert VUExpectedClaimRuleResult is not None
    assert VUExpectedClaimRuleSnapshot is not None
    assert VUFreeLinearRuleApplication is not None
    assert VUFreeLinearRuleParameters is not None
    assert VUFreeLinearRuleResult is not None
    assert VUFreeLinearRuleSnapshot is not None
    assert VUReserveMarkupRuleApplication is not None
    assert VUReserveMarkupRuleParameters is not None
    assert VUReserveMarkupRuleResult is not None
    assert VUReserveMarkupRuleSnapshot is not None
    assert apply_vu_expected_claim_rule is not None
    assert apply_vu_expected_claim_rule_snapshots is not None
    assert apply_vu_expected_claim_rule_to_insurer is not None
    assert apply_vu_free_linear_rule is not None
    assert apply_vu_free_linear_rule_snapshots is not None
    assert apply_vu_free_linear_rule_to_insurer is not None
    assert apply_vu_foreign_info_rule is not None
    assert apply_vu_foreign_info_rule_snapshots is not None
    assert apply_vu_foreign_info_rule_to_insurer is not None
    assert apply_vu_market_share_markup_rule is not None
    assert apply_vu_market_share_markup_rule_snapshots is not None
    assert apply_vu_market_share_markup_rule_to_insurer is not None
    assert apply_vu_net_switcher_markup_rule is not None
    assert apply_vu_net_switcher_markup_rule_snapshots is not None
    assert apply_vu_net_switcher_markup_rule_to_insurer is not None
    assert apply_vu_random_normal_rule is not None
    assert apply_vu_random_normal_rule_snapshots is not None
    assert apply_vu_random_normal_rule_to_insurer is not None
    assert apply_vu_random_uniform_rule is not None
    assert apply_vu_random_uniform_rule_snapshots is not None
    assert apply_vu_random_uniform_rule_to_insurer is not None
    assert apply_vu_reserve_markup_rule is not None
    assert apply_vu_reserve_markup_rule_snapshots is not None
    assert apply_vu_reserve_markup_rule_to_insurer is not None
    assert load_vu_expected_claim_rule_snapshots_from_mapping is not None
    assert load_vu_free_linear_rule_snapshots_from_mapping is not None
    assert load_vu_foreign_info_rule_snapshots_from_mapping is not None
    assert load_vu_market_share_markup_rule_snapshots_from_mapping is not None
    assert load_vu_net_switcher_markup_rule_snapshots_from_mapping is not None
    assert load_vu_random_normal_rule_snapshots_from_mapping is not None
    assert load_vu_random_uniform_rule_snapshots_from_mapping is not None
    assert load_vu_reserve_markup_rule_snapshots_from_mapping is not None
    assert vu_expected_claim_rule_parameters_from_mapping is not None
    assert vu_expected_claim_rule_snapshot_from_mapping is not None
    assert vu_free_linear_rule_parameters_from_mapping is not None
    assert vu_free_linear_rule_snapshot_from_mapping is not None
    assert vu_foreign_info_rule_parameters_from_mapping is not None
    assert vu_foreign_info_rule_snapshot_from_mapping is not None
    assert vu_market_share_markup_rule_parameters_from_mapping is not None
    assert vu_market_share_markup_rule_snapshot_from_mapping is not None
    assert vu_net_switcher_markup_rule_parameters_from_mapping is not None
    assert vu_net_switcher_markup_rule_snapshot_from_mapping is not None
    assert vu_random_normal_rule_parameters_from_mapping is not None
    assert vu_random_normal_rule_snapshot_from_mapping is not None
    assert vu_random_uniform_rule_parameters_from_mapping is not None
    assert vu_random_uniform_rule_snapshot_from_mapping is not None
    assert vu_reserve_markup_rule_parameters_from_mapping is not None
    assert vu_reserve_markup_rule_snapshot_from_mapping is not None
