import React, { useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import {
  Activity,
  Archive,
  Boxes,
  Braces,
  CheckCircle2,
  CircleAlert,
  ClipboardCheck,
  CircleDot,
  Database,
  Eye,
  FileText,
  GitBranch,
  ListTree,
  LockKeyhole,
  Pencil,
  Play,
  Plus,
  RefreshCw,
  Search,
  ServerCog,
  ShieldCheck,
  Trash2,
  X
} from "lucide-react";
import "./styles.css";

type StatusItem = {
  label: string;
  value: string;
  tone: "ready" | "quiet" | "warn";
};

type ScenarioMetadata = {
  id: string;
  display_name: string;
  status: string;
  domain_scope: string;
  source: MetadataSource;
  validation: ValidationSummary;
  updated_at: string;
  notes: string;
};

type RunMetadata = {
  id: string;
  display_name: string;
  scenario_id: string;
  status: string;
  source: MetadataSource;
  validation: ValidationSummary;
  period_window: string;
  execution_enabled: boolean;
  updated_at: string;
};

type MetadataSource = {
  kind: string;
  label: string;
  path?: string | null;
};

type ValidationSummary = {
  status: string;
  scope: string;
  claim: string;
};

type MetadataResponse<T> = {
  schema_version: string;
  generated_at: string;
  items: T[];
};

type StrategyActorType = "insurer" | "policyholder";

type StrategyFamily = {
  family_id: string;
  actor_type: StrategyActorType;
  display_name: string;
  description: string;
  taxonomy_only: boolean;
};

type StrategyDefinition = {
  strategy_id: string;
  actor_type: StrategyActorType;
  display_name: string;
  family_id: string;
  historical_action: string;
  historical_rule_id: number;
  historical_rule_class: number | null;
  included_in_vdefmd6: boolean;
  source_file: string;
  source_chapter: string;
  implementation_status: "ported_explicit_core";
  implementation_module: string;
  implementation_entrypoint: string;
  parameter_schema: string | null;
  parameterized: boolean;
  parameter_capabilities: string[];
  test_status: "unit_tested" | "unit_and_regression_tested";
  test_evidence: string[];
  notes: string;
  implementation_variant: string | null;
};

type StrategyCatalog = {
  schema_version: string;
  mode: "strategy_catalog_read_only";
  scope: "read_only_strategy_metadata";
  historical_full_equality_claim: boolean;
  selection_enabled: boolean;
  parameter_editing_enabled: boolean;
  writes_enabled: boolean;
  execution_enabled: boolean;
  simulation_performed: boolean;
  families: StrategyFamily[];
  strategies: StrategyDefinition[];
};

type StrategyWorkbenchView =
  | "catalog"
  | "assignments"
  | "parameters"
  | "draft"
  | "translation"
  | "context"
  | "snapshots"
  | "vu-snapshots"
  | "candidates";

type StrategySectorContract = {
  mode: "legacy_two_position_vector";
  position_count: number;
  position_keys: string[];
  python_indices: number[];
  named_sectors_available: boolean;
  strategy_shared_across_positions: boolean;
  sector_specific_strategy_supported: boolean;
  additional_sectors_supported: boolean;
};

type StrategyAssignmentTarget = {
  actor_type: StrategyActorType;
  entity_type: string;
  entity_id_field: string;
  legacy_rule_id_field: string;
  legacy_rule_class_field: string;
  assignment_scope: "individual_actor";
  assignment_cardinality: "zero_or_one_catalog_strategy_per_actor";
  eligible_strategy_ids: string[];
  group_assignment_supported: boolean;
  scheduled_strategy_switch_supported: boolean;
};

type StrategyParameterField = {
  field_name: string;
  display_name: string;
  python_type: string;
  value_shape: "legacy_two_sector_vector";
  required_by_existing_loader: boolean;
  existing_validation: string;
};

type StrategyParameterSchema = {
  schema_id: string;
  actor_type: StrategyActorType;
  module: string;
  loader_entrypoint: string;
  strategy_ids: string[];
  fields: StrategyParameterField[];
  editing_enabled: boolean;
  defaults_declared: boolean;
  new_domain_bounds_declared: boolean;
};

type StrategySourceProfile = {
  profile_id: string;
  source_model: string;
  actor_type: StrategyActorType;
  target_id_start: number;
  target_id_end: number;
  target_count: number;
  strategy_id: string;
  historical_rule_id: number;
  historical_rule_class: number;
  activation_period: number;
  active_through_run: number;
  logical_time: number;
  parameter_schema: string | null;
  legacy_parameter_value_count: number;
  legacy_parameter_fingerprint: string;
  parameter_values_exposed: boolean;
};

type StrategyAssignmentContract = {
  schema_version: string;
  catalog_schema_version: string;
  mode: "strategy_assignment_contract_read_only";
  scope: "eligibility_parameter_shapes_and_vdefmd6_source_profiles";
  selection_enabled: boolean;
  assignment_editing_enabled: boolean;
  parameter_editing_enabled: boolean;
  group_assignment_enabled: boolean;
  sector_specific_strategy_enabled: boolean;
  scheduled_strategy_switch_enabled: boolean;
  writes_enabled: boolean;
  execution_enabled: boolean;
  simulation_performed: boolean;
  historical_full_equality_claim: boolean;
  sector_contract: StrategySectorContract;
  assignment_targets: StrategyAssignmentTarget[];
  parameter_schemas: StrategyParameterSchema[];
  source_profiles: StrategySourceProfile[];
  source_summary: {
    model: string;
    profile_count: number;
    insurer_count: number;
    policyholder_count: number;
    parameter_values_exposed: boolean;
  };
};

type StrategyAssignmentDraftContract = {
  schema_version: string;
  catalog_schema_version: string;
  assignment_contract_schema_version: string;
  mode: "strategy_assignment_draft_contract_read_only";
  base_model: "Vdefmd6";
  scope: "partial_actor_assignments";
  validation_endpoint: string;
  target_limits: Record<StrategyActorType, { minimum: number; maximum: number }>;
  parameter_value_shape: {
    mode: "legacy_two_position_vector";
    length: number;
    position_keys: string[];
    named_sectors_available: boolean;
  };
  defaults_applied: boolean;
  persistence_enabled: boolean;
  workbench_editing_enabled: boolean;
  snapshot_translation_enabled: boolean;
  execution_enabled: boolean;
  simulation_performed: boolean;
  historical_full_equality_claim: boolean;
};

type StrategyDraftParameterValues = Record<string, [number, number]>;

type StrategyDraftAssignment = {
  actor_type: StrategyActorType;
  target_id: number;
  strategy_id: string;
  activation_period: number;
  active_through_run: number;
  logical_time: number;
  parameter_schema: string | null;
  parameter_values: StrategyDraftParameterValues | null;
};

type StrategyAssignmentDraftDocument = {
  schema_version: string;
  catalog_schema_version: string;
  assignment_contract_schema_version: string;
  base_model: "Vdefmd6";
  scope: "partial_actor_assignments";
  draft_id: string;
  label: string;
  assignments: StrategyDraftAssignment[];
};

type StrategyAssignmentDraftValidationIssue = {
  path: string;
  code: string;
  message: string;
};

type StrategyAssignmentDraftValidationReport = {
  schema_version: string;
  mode: "strategy_assignment_draft_validation";
  status: "ok" | "error";
  valid: boolean;
  assignment_count: number;
  validated_assignment_count: number;
  issue_count: number;
  issues: StrategyAssignmentDraftValidationIssue[];
  writes_performed: boolean;
  snapshots_created: boolean;
  execution_performed: boolean;
  simulation_performed: boolean;
  historical_full_equality_claim: boolean;
};

type StrategySnapshotTarget = {
  strategy_id: string;
  actor_type: StrategyActorType;
  snapshot_module: string;
  snapshot_type: string;
  snapshot_loader: string;
  snapshot_collection: string;
  target_id_field: string;
  rule_kind: string | null;
  provided_snapshot_fields: string[];
  unresolved_snapshot_fields: string[];
};

type StrategySnapshotTranslationContract = {
  schema_version: string;
  draft_schema_version: string;
  mode: "strategy_assignment_snapshot_translation_contract_read_only";
  scope: "validated_draft_to_existing_snapshot_construction_plan";
  translation_endpoint: string;
  strategy_mappings: StrategySnapshotTarget[];
  mapping_issue_count: number;
  partial_snapshot_payloads: boolean;
  typed_parameter_loading_enabled: boolean;
  snapshot_loader_invocation_enabled: boolean;
  defaults_applied: boolean;
  persistence_enabled: boolean;
  snapshot_materialization_enabled: boolean;
  execution_enabled: boolean;
  simulation_performed: boolean;
  historical_full_equality_claim: boolean;
};

type StrategySnapshotTranslationEntry = StrategyDraftAssignment & {
  snapshot_module: string;
  snapshot_type: string;
  snapshot_loader: string;
  snapshot_collection: string;
  snapshot_payload: Record<string, unknown>;
  provided_snapshot_fields: string[];
  unresolved_snapshot_fields: string[];
  snapshot_materialized: boolean;
  execution_ready: boolean;
};

type StrategySnapshotTranslationReport = {
  schema_version: string;
  mode: "strategy_assignment_snapshot_translation";
  status: "ok" | "error";
  draft_valid: boolean;
  translation_complete: boolean;
  draft_id: string | null;
  label: string | null;
  assignment_count: number;
  translated_assignment_count: number;
  issue_count: number;
  issues: StrategyAssignmentDraftValidationIssue[];
  entries: StrategySnapshotTranslationEntry[];
  defaults_applied: boolean;
  snapshot_materialization_ready: boolean;
  writes_performed: boolean;
  snapshots_created: boolean;
  execution_performed: boolean;
  simulation_performed: boolean;
  historical_full_equality_claim: boolean;
};

type StrategySnapshotContextSource =
  | "draw"
  | "period_finance"
  | "shock"
  | "strategy_state"
  | "market_state"
  | "previous_period";

type StrategySnapshotContextValueShape =
  | "array"
  | "boolean"
  | "finite_number"
  | "integer"
  | "number_array"
  | "object"
  | "positive_integer_array";

type StrategySnapshotContextFieldDefinition = {
  field_name: string;
  source: StrategySnapshotContextSource;
  value_shape: StrategySnapshotContextValueShape;
  fixed_length: number | null;
  nullable: boolean;
};

type StrategySnapshotContextContract = {
  schema_version: string;
  validation_schema_version: string;
  draft_schema_version: string;
  translation_schema_version: string;
  mode: "strategy_assignment_snapshot_context_contract_read_only";
  base_model: "Vdefmd6";
  scope: "explicit_single_period_snapshot_context";
  validation_endpoint: string;
  field_definitions: StrategySnapshotContextFieldDefinition[];
  source_categories: StrategySnapshotContextSource[];
  contract_issue_count: number;
  exact_draft_entry_match_required: boolean;
  exact_open_field_match_required: boolean;
  explicit_null_keeps_value_open: boolean;
  defaults_applied: boolean;
  context_values_consumed: boolean;
  snapshot_loader_invocation_enabled: boolean;
  persistence_enabled: boolean;
  snapshot_materialization_enabled: boolean;
  execution_enabled: boolean;
  simulation_performed: boolean;
  historical_full_equality_claim: boolean;
};

type StrategySnapshotContextEditorValue = {
  raw: string;
  explicitlyOpen: boolean;
};

type StrategySnapshotContextEditorEntry = {
  actor_type: StrategyActorType;
  target_id: number;
  strategy_id: string;
  values: Record<string, StrategySnapshotContextEditorValue>;
};

type StrategySnapshotContextDocument = {
  schema_version: string;
  translation_schema_version: string;
  base_model: "Vdefmd6";
  scope: "explicit_single_period_snapshot_context";
  draft_id: string;
  period: number;
  entries: Array<{
    actor_type: StrategyActorType;
    target_id: number;
    strategy_id: string;
    values: Record<string, unknown>;
  }>;
};

type StrategySnapshotContextValidationReport = {
  schema_version: string;
  mode: "strategy_assignment_snapshot_context_validation";
  status: "ok" | "error";
  valid: boolean;
  draft_valid: boolean;
  translation_complete: boolean;
  submitted_schema_version: string | null;
  draft_id: string | null;
  period: number | null;
  expected_entry_count: number;
  validated_entry_count: number;
  expected_value_count: number;
  validated_value_count: number;
  resolved_value_count: number;
  explicitly_open_value_count: number;
  all_context_values_supplied: boolean;
  issue_count: number;
  issues: StrategyAssignmentDraftValidationIssue[];
  defaults_applied: boolean;
  context_values_consumed: boolean;
  snapshot_loader_invocation_performed: boolean;
  snapshot_materialization_ready: boolean;
  writes_performed: boolean;
  snapshots_created: boolean;
  execution_performed: boolean;
  simulation_performed: boolean;
  historical_full_equality_claim: boolean;
};

type StrategySnapshotMaterializationOperationContract = {
  schema_version: string;
  mode: "strategy_assignment_snapshot_materialization_contract";
  scope: "validated_vn_single_period_context_to_typed_snapshots";
  materialization_endpoint: string;
  validated_rule_count: number;
  snapshot_collection: "vn_insurance_rule_snapshots";
  persistence_enabled: boolean;
  execution_enabled: boolean;
  runner_enabled: boolean;
  simulation_performed: boolean;
  historical_full_equality_claim: boolean;
};

type StrategySnapshotMaterializationContract = {
  schema_version: string;
  operation: StrategySnapshotMaterializationOperationContract;
};

type StrategyMaterializedVNSnapshotPayload = {
  policyholder_id: number;
  rule_kind: string;
  parameters: unknown;
  draws: unknown;
  active_insurer_ids: unknown;
  initial_decisions: unknown;
  damage_probabilities: unknown;
  insurer_inputs: unknown;
  history: unknown;
  market_damage_indicator: unknown;
  change_shock: unknown;
  information_cost_per_sample: unknown;
  information_cost_per_insurer: unknown;
};

type StrategyMaterializedVNSnapshot = {
  strategy_id: string;
  snapshot_collection: string;
  snapshot_type: string;
  snapshot: StrategyMaterializedVNSnapshotPayload;
};

type StrategySnapshotMaterializationIssue = StrategyAssignmentDraftValidationIssue & {
  stage: string;
};

type StrategySnapshotMaterializationReport = {
  schema_version: string;
  mode: "strategy_assignment_snapshot_materialization";
  status: "ok" | "error";
  input_valid: boolean;
  materialization_complete: boolean;
  draft_id: string | null;
  period: number | null;
  expected_snapshot_count: number;
  snapshot_count: number;
  snapshot_loader_invocation_count: number;
  nested_loader_invocation_count: number;
  issue_count: number;
  issues: StrategySnapshotMaterializationIssue[];
  snapshots: StrategyMaterializedVNSnapshot[];
  context_values_consumed: boolean;
  nested_loader_results_retained: boolean;
  snapshot_loader_invocation_performed: boolean;
  partial_results_returned: boolean;
  writes_performed: boolean;
  persistence_performed: boolean;
  execution_ready: boolean;
  execution_performed: boolean;
  runner_invoked: boolean;
  simulation_performed: boolean;
  historical_full_equality_claim: boolean;
};

type StrategyVUSnapshotInputContract = {
  input_schema_version: string;
  threshold_source_policy: { policy_id: string };
  draw_source_policy: { policy_id: string };
  fallback_policy: { policy_id: string };
};

type StrategyVUSnapshotStateContract = {
  schema_version: string;
  state_schema_version: string;
  materialization_input_schema_version: string;
  base_model: "Vdefmd6";
  scope: "vu_snapshot_materialization_provenance_state";
  state_value_fields_by_strategy: Record<string, string[]>;
  provenance_definition_count: number;
  draw_values_cross_checked_against_draw_plan: boolean;
};

type StrategyVUSnapshotMaterializationOperationContract = {
  schema_version: string;
  mode: "strategy_assignment_vu_snapshot_materialization_contract";
  scope: "validated_vu_single_period_context_to_typed_snapshots";
  materialization_endpoint: string;
  validated_strategy_count: number;
  snapshot_type_count: number;
  state_provenance_validation_required: boolean;
  persistence_enabled: boolean;
  execution_enabled: boolean;
  runner_enabled: boolean;
  simulation_performed: boolean;
  historical_rng_equality_claim: boolean;
  historical_full_equality_claim: boolean;
};

type StrategyVUSnapshotMaterializationContract = {
  schema_version: string;
  operation: StrategyVUSnapshotMaterializationOperationContract;
};

type StrategyVUStateEditorEntry = {
  insurer_id: number;
  strategy_id: string;
  values: Record<string, string>;
};

type StrategyVUStateEditor = {
  interestRate: string;
  changeShock: string;
  activePolicyholderCount: string;
  entries: StrategyVUStateEditorEntry[];
};

type StrategyMaterializedVUSnapshotPayload = Record<string, unknown> & {
  insurer_id: number;
  rule_kind?: string;
};

type StrategyMaterializedVUSnapshot = {
  strategy_id: string;
  snapshot_collection: string;
  snapshot_type: string;
  snapshot: StrategyMaterializedVUSnapshotPayload;
};

type StrategyVUSnapshotMaterializationReport = {
  schema_version: string;
  mode: "strategy_assignment_vu_snapshot_materialization";
  status: "ok" | "error";
  input_valid: boolean;
  materialization_complete: boolean;
  draft_id: string | null;
  period: number | null;
  expected_snapshot_count: number;
  snapshot_count: number;
  snapshot_loader_invocation_count: number;
  issue_count: number;
  issues: StrategySnapshotMaterializationIssue[];
  snapshots: StrategyMaterializedVUSnapshot[];
  state_provenance_validated: boolean;
  context_values_consumed: boolean;
  state_values_consumed: boolean;
  snapshot_loader_invocation_performed: boolean;
  partial_results_returned: boolean;
  writes_performed: boolean;
  persistence_performed: boolean;
  execution_ready: boolean;
  execution_performed: boolean;
  runner_invoked: boolean;
  simulation_performed: boolean;
  historical_rng_equality_claim: boolean;
  historical_full_equality_claim: boolean;
};

type StrategyExecutionCandidateOverviewEntry = {
  candidate_id: string;
  draft_id: string;
  draft_label: string;
  period: number;
  profile_id: string;
  profile_content_digest: string;
  content_digest: string;
  digest_algorithm: "sha256";
  digest_verified: boolean;
  stored_at: string;
  storage_status: "persisted_immutable";
  source_document_count: number;
  contract_version_count: number;
  insurer_count: number;
  policyholder_count: number;
  vu_snapshot_count: number;
  vn_rule_snapshot_count: number;
  vn_process_snapshot_count: number;
  readiness: {
    candidate_complete: boolean;
    source_documents_present: boolean;
    market_ground_state_present: boolean;
    storage_integrity_verified: boolean;
    run_control_ready: boolean;
    run_control_release_check_available: boolean;
    execution_ready: boolean;
    next_gate: string;
  };
};

type StrategyExecutionCandidateOverview = {
  schema_version: string;
  candidate_schema_version: string;
  mode: "strategy_execution_candidate_overview_read_only";
  status: "ok";
  storage: {
    kind: "memory" | "sqlite";
    configured: boolean;
    path: string | null;
    store_initialized: boolean;
    immutable: boolean;
  };
  candidate_count: number;
  candidates: StrategyExecutionCandidateOverviewEntry[];
  all_candidate_digests_verified: boolean;
  writes_performed: boolean;
  run_control_connected: boolean;
  runner_invocation_performed: boolean;
  execution_performed: boolean;
  simulation_performed: boolean;
  historical_full_equality_claim: boolean;
};

type StrategyDraftEditor = {
  actorType: StrategyActorType;
  targetId: string;
  strategyId: string;
  activationPeriod: string;
  activeThroughRun: string;
  logicalTime: string;
  parameterValues: Record<string, [string, string]>;
};

type MetadataCapabilities = {
  writes: {
    scenario_metadata: CapabilityState;
    run_metadata: CapabilityState;
  };
  simulation_execution: CapabilityState;
};

type HealthStatus = {
  status: string;
  service: string;
  version: string;
  frontend_available: boolean;
};

type VersionInfo = {
  name: string;
  version: string;
  api: string;
};

type MetadataSourceStatus = {
  schema_version: string;
  storage_kind: "memory" | "sqlite";
  configured: boolean;
  injected: boolean;
  path?: string;
  writes_enabled: boolean;
  execution_enabled: boolean;
};

type MetadataConsistency = {
  schema_version: string;
  generated_at: string;
  status: "ok" | "warning";
  scenario_count: number;
  run_count: number;
  runs_with_known_scenario: number;
  runs_with_missing_scenario: string[];
  runs_with_execution_enabled: string[];
  writes_enabled: boolean;
  simulation_enabled: boolean;
  issue_count: number;
};

type RunControlQueueEntry = {
  queue_id: string;
  request: {
    run_id: string;
    scenario_id: string;
    requested_by: string;
    created_at: string;
    metadata_db?: string | null;
    execution_enabled: boolean;
  };
  status: string;
  execution_enabled: boolean;
  execution_performed: boolean;
};

type RunControlQueueOverview = {
  schema_version: string;
  generated_at: string;
  status: "ok" | "warning";
  mode: "run_control_queue_overview";
  source: MetadataSourceStatus;
  queue_count: number;
  entries: RunControlQueueEntry[];
  issues: { code: string; severity: string; message: string }[];
  writes_enabled: boolean;
  execution_enabled: boolean;
  execution_performed: boolean;
};

type RunControlQueueDetail = {
  schema_version: string;
  generated_at: string;
  status: "ok";
  mode: "run_control_queue_detail";
  source: MetadataSourceStatus;
  entry: RunControlQueueEntry;
  writes_enabled: boolean;
  execution_enabled: boolean;
  execution_performed: boolean;
};

type RunControlQueueEnqueueResult = {
  status: "ok";
  mode: "run_control_queue_enqueue";
  schema_version: string;
  db_path: string;
  entry: RunControlQueueEntry;
  entries: RunControlQueueEntry[];
  dry_run: RunControlDryRunResult;
  writes_performed: boolean;
  execution_enabled: boolean;
  execution_performed: boolean;
};

type RunControlNextAction =
  | "run_preflight"
  | "await_execution_release"
  | "await_execution_completion"
  | "inspect_execution_failure"
  | "resolve_blockers"
  | "inspect_persisted_result"
  | "inspect_queue_status";

type RunControlBridgeNextAction =
  | RunControlNextAction
  | "inspect_core_validation_overview"
  | "await_precomputed_execution_summary"
  | "resolve_core_validation_blockers";

type RunControlQueueActionPlan = {
  status: "ok" | "warning" | "error";
  mode: "run_control_queue_action_plan";
  schema_version: string;
  db_path?: string;
  metadata_source: MetadataSourceStatus;
  queue_id?: string;
  queue_count: number;
  actions: {
    queue_id: string;
    run_id: string;
    scenario_id: string;
    queue_status: string;
    next_action: RunControlNextAction;
    next_action_label: string;
    blocked_by: string[];
    execution_allowed: boolean;
    writes_performed: boolean;
    execution_performed: boolean;
  }[];
  issues: {
    code: string;
    severity: string;
    message: string;
    queue_ids: string[];
  }[];
  writes_performed: boolean;
  execution_performed: boolean;
};

type RunControlCoreDiagnosticsBridge = {
  status: "ok" | "warning" | "error";
  mode: "run_control_core_diagnostics_bridge";
  queue_action_plan_mode: string;
  core_validation_mode: string;
  queue_count: number;
  action_count: number;
  period_plan_count: number;
  period_count: number;
  global_periods: number[];
  legacy_reference_count: number;
  execution_summary_available: boolean;
  execution_summary_next_action: string;
  actions: {
    queue_id: string;
    run_id: string;
    scenario_id: string;
    queue_status: string;
    queue_next_action: RunControlNextAction;
    core_validation_status: string;
    bridge_next_action: RunControlBridgeNextAction;
    blocked_by: string[];
    execution_summary_next_action: string;
    execution_allowed: boolean;
    writes_performed: boolean;
    execution_performed: boolean;
  }[];
  issues: {
    source: string;
    code: string;
    severity: string;
    message: string;
    queue_ids: string[];
  }[];
  writes_performed: boolean;
  execution_performed: boolean;
};

type RunControlRequestContract = {
  status: "ok";
  mode: "run_control_request_contract";
  schema_version: string;
  accepted_fields: string[];
  required_fields: string[];
  optional_fields: string[];
  forbidden_fields: string[];
  example_request: {
    run_id: string;
    scenario_id: string;
    metadata_db?: string | null;
    requested_by: string;
    created_at: string;
    execution_enabled: boolean;
  };
  writes_enabled: boolean;
  execution_enabled: boolean;
  execution_performed: boolean;
};

type RunControlDryRunContract = {
  status: "ok" | "warning";
  mode: "run_control_dry_run_contract";
  schema_version: string;
  expected_inputs: string[];
  required_preconditions: string[];
  forbidden_boundaries: string[];
  http_enabled: boolean;
  writes_enabled: boolean;
  execution_enabled: boolean;
  writes_performed: boolean;
  execution_performed: boolean;
};

type RunControlAdapterResultApiContract = {
  status: "ok";
  mode: "run_control_adapter_result_api_contract";
  schema_version: string;
  endpoint: string;
  expected_result_mode: "controlled_execution_adapter";
  expected_validation_mode: "run_control_adapter_result_validation";
  expected_contract_mode: "run_control_adapter_result_contract";
  source_contract_module: string;
  expected_inputs: string[];
  required_preconditions: string[];
  accepted_result_fields: string[];
  accepted_summary_fields: string[];
  forbidden_fields: string[];
  forbidden_boundaries: string[];
  precomputed_result_required: boolean;
  api_accepts_result_payload: boolean;
  api_validates_result_payload: boolean;
  api_starts_adapter: boolean;
  http_enabled: boolean;
  ui_enabled: boolean;
  queue_worker_enabled: boolean;
  writes_performed: boolean;
  execution_performed: boolean;
  simulation_performed: boolean;
  automatic_historical_rule_selection_performed: boolean;
};

type RunControlAdapterStartContract = {
  status: "ok";
  mode: "run_control_adapter_start_contract";
  schema_version: string;
  endpoint: string;
  planned_start_endpoint: string;
  source_adapter_module: string;
  expected_adapter_mode: string;
  expected_summary_mode: string;
  required_request_fields: string[];
  optional_request_fields: string[];
  required_preconditions: string[];
  forbidden_request_fields: string[];
  forbidden_boundaries: string[];
  contract_only: boolean;
  http_enabled: boolean;
  api_accepts_start_payload: boolean;
  api_validates_start_payload: boolean;
  api_starts_adapter: boolean;
  ui_start_enabled: boolean;
  queue_worker_enabled: boolean;
  writes_enabled: boolean;
  execution_enabled: boolean;
  writes_performed: boolean;
  execution_performed: boolean;
  simulation_performed: boolean;
  automatic_historical_rule_selection_performed: boolean;
  historical_full_equality_claimed: boolean;
};

type RunControlExecutionReleaseRequest = {
  schema_version: string;
  queue_id: string;
  run_id: string;
  scenario_id: string;
  release_profile_id: string;
  idempotency_key: string;
  expected_adapter_mode: string;
  explicit_execution_release: true;
  released_by: string;
  released_at: string;
  release_reason: string;
  carry_forward_vu_state: false;
  carry_forward_vn_state: false;
};

type RunControlExecutionReleaseResult = {
  status: "ready" | "blocked" | "error";
  mode: "run_control_execution_release_check";
  request?: RunControlExecutionReleaseRequest;
  issues: string[];
  release_ready: boolean;
  adapter_started: boolean;
  writes_performed: boolean;
  execution_performed: boolean;
  simulation_performed: boolean;
  message?: string;
};

type RunControlAdapterStartResponse = {
  status: "ok" | "error";
  mode: "run_control_adapter_start";
  queue_id?: string;
  queue_status?: string;
  idempotency_key?: string;
  replayed?: boolean;
  record?: RunControlExecutionResultRecord;
  adapter_started: boolean;
  result_persisted: boolean;
  writes_performed: boolean;
  execution_performed: boolean;
  simulation_performed: boolean;
  message?: string;
  issues?: string[];
};

type RunControlExecutionResultRecord = {
  queue_id: string;
  run_id: string;
  scenario_id: string;
  adapter_mode: string;
  fixture_kind: string;
  fixture_path: string;
  summary_mode: string;
  result_status: string;
  persisted_at: string;
  result_payload: Record<string, unknown>;
  summary_payload: Record<string, unknown>;
  validation_payload: Record<string, unknown>;
  adapter_execution_performed: boolean;
  simulation_performed: boolean;
  automatic_historical_rule_selection_performed: boolean;
  historical_full_equality_claimed: boolean;
};

type RunControlExecutionResult = {
  status: "ok" | "error";
  mode: "run_control_execution_result_store_show";
  schema_version: string;
  db_path?: string;
  metadata_source?: MetadataSourceStatus;
  record?: RunControlExecutionResultRecord;
  message?: string;
  issues?: string[];
  writes_performed: boolean;
  execution_performed: boolean;
  adapter_started: boolean;
  simulation_performed: boolean;
  automatic_historical_rule_selection_performed?: boolean;
  historical_full_equality_claimed?: boolean;
};

type RunControlExecutionAttempt = {
  attempt_id: string;
  queue_id: string;
  idempotency_key: string;
  status: "starting" | "failed" | "result_persisted";
  released_by: string;
  released_at: string;
  release_reason: string;
  started_at: string;
  completed_at: string | null;
  failure_message: string | null;
  adapter_started: boolean;
  result_persisted: boolean;
  simulation_performed: boolean;
};

type RunControlExecutionHistory = {
  status: "ok" | "error";
  mode: "run_control_execution_history";
  schema_version: string;
  queue_id: string;
  queue_status: string;
  attempt_count: number;
  attempts: RunControlExecutionAttempt[];
  latest_attempt: RunControlExecutionAttempt | null;
  persisted_result_available: boolean;
  persisted_at: string | null;
  automatic_retry_enabled: boolean;
  queue_worker_enabled: boolean;
  message?: string;
  issues?: string[];
  writes_performed: boolean;
  execution_performed: boolean;
  adapter_started: boolean;
  simulation_performed: boolean;
  historical_full_equality_claimed: boolean;
};

type RunControlDryRunResult = {
  status: "ok" | "error";
  mode: "run_control_dry_run";
  request: RunControlRequestContract["example_request"];
  preflight: RunControlPreflight;
  request_accepted: boolean;
  preflight_passed: boolean;
  scenario_matches_request: boolean;
  dry_run_allowed: boolean;
  issues: string[];
  writes_enabled: boolean;
  execution_enabled: boolean;
  writes_performed: boolean;
  execution_performed: boolean;
};

type RunControlPreflight = {
  status: "ok" | "error";
  mode: "run_control_preflight";
  run_id: string;
  scenario_id: string | null;
  run_found: boolean;
  scenario_found: boolean;
  metadata_source: MetadataSourceStatus;
  execution_enabled: boolean;
  execution_allowed: boolean;
  issues: string[];
  writes_performed: boolean;
  execution_performed: boolean;
};

type CoreValidationOverview = {
  status: "ok" | "warning" | "error";
  mode: "ims_core_validation_overview";
  plan_count: number;
  period_count: number;
  global_periods: number[];
  legacy_reference_count: number;
  legacy_covered_rows: number;
  legacy_covered_periods: number;
  next_validation_actions: string[];
  execution_summary_available: boolean;
  execution_summary_next_action: string;
  execution_summary_contract: {
    mode: "explicit_multi_period_execution_summary_contract";
    summary_mode: "explicit_multi_period_execution_summary";
    required_fields: string[];
    period_axis_fields: string[];
    application_count_fields: string[];
    carryover_fields: string[];
    legacy_fields: string[];
    boundary_fields: string[];
    next_action: string;
    overview_accepts_summary_input: boolean;
    overview_starts_runner: boolean;
    writes_performed: boolean;
    execution_performed: boolean;
  };
  writes_performed: boolean;
  execution_performed: boolean;
};

type CoreValidationCarryoverProbeContract = {
  status: "ok";
  mode: "core_validation_carryover_probe_api_contract";
  endpoint: string;
  expected_probe_mode: "explicit_transition_carryover_probe";
  expected_contract_mode: "explicit_transition_carryover_probe_contract";
  expected_inputs: string[];
  required_preconditions: string[];
  accepted_payload_fields: string[];
  transition_fields: string[];
  carryover_request_fields: string[];
  carried_entity_fields: string[];
  boundary_fields: string[];
  forbidden_boundaries: string[];
  precomputed_probe_required: boolean;
  api_accepts_probe_payload: boolean;
  api_starts_probe: boolean;
  http_enabled: boolean;
  ui_enabled: boolean;
  writes_performed: boolean;
  execution_performed: boolean;
  simulation_performed: boolean;
  automatic_historical_rule_selection_performed: boolean;
};

type CapabilityState = {
  enabled: boolean;
  boundary?: string;
  reason: string;
};

type DetailState = "idle" | "loading" | "ready" | "error";

type ScenarioFilters = {
  query: string;
  status: string;
  source: string;
  scope: string;
};

type RunFilters = {
  query: string;
  status: string;
  scenario: string;
  source: string;
};

type QueueFilters = {
  query: string;
  status: string;
  scenario: string;
};

const statusItems: StatusItem[] = [
  { label: "Backend", value: "bereit", tone: "ready" },
  { label: "Fachlogik", value: "abgegrenzt", tone: "quiet" },
  { label: "Persistenz", value: "vorbereitet", tone: "quiet" }
];

const validationRows = [
  ["Simulationskern", "652 Tests", "gruen"],
  ["Legacy-Fenster", "portierte Pfade", "abgedeckt"],
  ["Historische Vollgleichheit", "nicht behauptet", "offen"]
];

const importShapeRows = [
  ["schema_version", "ims.workbench.metadata.v1"],
  ["scenarios", "Szenario-Metadaten"],
  ["runs", "Run-Metadaten"]
];

const ALL_SCENARIO_FILTERS = "alle";
const ALL_RUN_FILTERS = "alle";
const ALL_QUEUE_FILTERS = "alle";
const STRATEGY_ACTOR_ORDER: StrategyActorType[] = ["insurer", "policyholder"];

const strategyCapabilityLabels: Record<string, string> = {
  two_sector: "zwei Sparten",
  normal_and_change_shock: "Normal- und Schockzweig",
  explicit_uniform_draws: "explizite Gleichverteilung",
  explicit_normal_draws: "explizite Normalverteilung",
  reserve_threshold: "Reserveschwelle",
  net_switcher_threshold: "Wechslerschwelle",
  market_share_threshold: "Marktanteilsschwelle",
  expected_claim: "Erwartungsschaden",
  market_foreign_information: "Marktinformation",
  linear_price_and_advertising: "lineare Praemie und Werbung",
  explicit_insurer_choice_draws: "explizite Versichererwahl",
  explicit_status_and_choice_draws: "expliziter Status und Versichererwahl",
  advertising_preference: "Werbepraeferenz",
  own_premium_history: "eigene Praemienhistorie",
  sample_size: "Stichprobengroesse",
  information_cost: "Informationskosten",
  full_market_information: "vollstaendige Marktinformation"
};

const strategySnapshotFieldLabels: Record<string, string> = {
  insurer_id: "VU-Ziel",
  policyholder_id: "VN-Ziel",
  rule_kind: "Regelvariante",
  parameters: "Strategieparameter",
  random_draws: "Gleichverteilte Ziehungen",
  normal_draws: "Normalverteilte Ziehungen",
  reserve_thresholds: "Reserveschwellen",
  net_switcher_thresholds: "Wechslerschwellen",
  previous_policyholders_sector: "VN-Zahlen der Vorperiode",
  market_share_thresholds: "Marktanteilsschwellen",
  active_policyholder_count: "Anzahl aktiver VN",
  interest_rate: "Zinssatz der Periode",
  change_shock: "Schockstatus der Periode",
  draws: "Regelbezogene Zufallsziehungen",
  active_insurer_ids: "Aktive Versicherer",
  initial_decisions: "Anfangsentscheidungen",
  damage_probabilities: "Schadenwahrscheinlichkeiten",
  insurer_inputs: "VU-Marktwerte",
  history: "Versicherungshistorie",
  market_damage_indicator: "Marktschadenindikator",
  information_cost_per_sample: "Informationskosten je Stichprobe",
  information_cost_per_insurer: "Informationskosten je Versicherer",
  insurance_thresholds_normal: "Versicherungsschwellen im Normalzustand",
  insurance_thresholds_shock: "Versicherungsschwellen im Schockzustand",
  sample_sizes_normal: "Stichprobengroessen im Normalzustand",
  sample_sizes_shock: "Stichprobengroessen im Schockzustand",
  insurer_choice_draws: "Ziehungen fuer die Versichererwahl",
  status_draws: "Ziehungen fuer den Versicherungsstatus",
  fallback_insurer_choice_draws: "Fallback-Ziehungen fuer die Versichererwahl",
  insurer_choice_draws_by_sector: "Ziehungen je historischer Position",
  advertising_current_sector: "Werbung je historischer Position",
  premiums_current_sector: "Praemien je historischer Position",
  period: "Historienperiode",
  sector_index: "Historische Position",
  insured: "Versichert",
  premium: "Praemie"
};

const strategyMaterializedSnapshotGroups = [
  {
    label: "Strategieparameter",
    fields: ["parameters"]
  },
  {
    label: "Ziehungen und Auswahl",
    fields: ["draws", "active_insurer_ids", "initial_decisions"]
  },
  {
    label: "Markt und Historie",
    fields: ["damage_probabilities", "insurer_inputs", "history", "market_damage_indicator"]
  },
  {
    label: "Schock und Kosten",
    fields: ["change_shock", "information_cost_per_sample", "information_cost_per_insurer"]
  }
] as const;

const strategyMaterializedFieldsByRuleKind: Record<string, string[]> = {
  compulsory: ["draws", "active_insurer_ids"],
  random: ["parameters", "draws", "active_insurer_ids", "change_shock"],
  preference: ["parameters", "draws", "damage_probabilities", "insurer_inputs", "change_shock"],
  search_history: [
    "parameters",
    "draws",
    "active_insurer_ids",
    "damage_probabilities",
    "history",
    "change_shock"
  ],
  sample_search: [
    "parameters",
    "draws",
    "insurer_inputs",
    "market_damage_indicator",
    "change_shock",
    "information_cost_per_sample"
  ],
  best_info: [
    "parameters",
    "insurer_inputs",
    "market_damage_indicator",
    "change_shock",
    "information_cost_per_insurer"
  ]
};

const strategyMaterializedVUSnapshotGroups = [
  {
    label: "Strategieparameter",
    fields: ["parameters"]
  },
  {
    label: "Ziehungen",
    fields: ["random_draws", "normal_draws"]
  },
  {
    label: "Schwellen und Markt",
    fields: [
      "reserve_thresholds",
      "net_switcher_thresholds",
      "previous_policyholders_sector",
      "market_share_thresholds",
      "active_policyholder_count"
    ]
  },
  {
    label: "Periode",
    fields: ["interest_rate", "change_shock"]
  }
] as const;

const strategyVUStateFieldLabels: Record<string, string> = {
  aspiration_sector_1: "Anspruchsprofil Sparte 1",
  aspiration_sector_2: "Anspruchsprofil Sparte 2",
  policyholders_t_minus_2: "VU-Bestand aus t-2"
};

const strategySnapshotContextSourceLabels: Record<StrategySnapshotContextSource, string> = {
  draw: "Ziehungen",
  period_finance: "Zins und Periodenkosten",
  shock: "Schockstatus",
  strategy_state: "Strategieschwellen",
  market_state: "Marktwerte",
  previous_period: "Vorperiodenwerte"
};

const strategySnapshotContextSourceDescriptions: Record<StrategySnapshotContextSource, string> = {
  draw: "Explizite Zufallswerte des konkreten Regelaufrufs",
  period_finance: "Finanz- und Informationskosten der gewaehlten Periode",
  shock: "Expliziter Normal- oder Aenderungsschockzweig",
  strategy_state: "Schwellenwerte aus dem belegten Strategiezustand",
  market_state: "Aktive Marktteilnehmer und periodische Marktinformationen",
  previous_period: "Explizit uebernommene Entscheidungen und Historien"
};

export function filterScenarios(scenarios: ScenarioMetadata[], filters: ScenarioFilters): ScenarioMetadata[] {
  const query = filters.query.trim().toLocaleLowerCase();
  return scenarios.filter((scenario) => {
    const matchesQuery =
      !query ||
      scenario.display_name.toLocaleLowerCase().includes(query) ||
      scenario.id.toLocaleLowerCase().includes(query);
    const matchesStatus = filters.status === ALL_SCENARIO_FILTERS || scenario.status === filters.status;
    const matchesSource = filters.source === ALL_SCENARIO_FILTERS || scenario.source.label === filters.source;
    const matchesScope = filters.scope === ALL_SCENARIO_FILTERS || scenario.domain_scope === filters.scope;
    return matchesQuery && matchesStatus && matchesSource && matchesScope;
  });
}

export function filterRuns(runs: RunMetadata[], filters: RunFilters): RunMetadata[] {
  const query = filters.query.trim().toLocaleLowerCase();
  return runs.filter((run) => {
    const matchesQuery =
      !query ||
      run.display_name.toLocaleLowerCase().includes(query) ||
      run.id.toLocaleLowerCase().includes(query);
    const matchesStatus = filters.status === ALL_RUN_FILTERS || run.status === filters.status;
    const matchesScenario = filters.scenario === ALL_RUN_FILTERS || run.scenario_id === filters.scenario;
    const matchesSource = filters.source === ALL_RUN_FILTERS || run.source.label === filters.source;
    return matchesQuery && matchesStatus && matchesScenario && matchesSource;
  });
}

export function filterRunControlQueueEntries(
  entries: RunControlQueueEntry[],
  filters: QueueFilters
): RunControlQueueEntry[] {
  const query = filters.query.trim().toLocaleLowerCase();
  return entries.filter((entry) => {
    const matchesQuery =
      !query ||
      entry.queue_id.toLocaleLowerCase().includes(query) ||
      entry.request.run_id.toLocaleLowerCase().includes(query) ||
      entry.request.requested_by.toLocaleLowerCase().includes(query);
    const matchesStatus = filters.status === ALL_QUEUE_FILTERS || entry.status === filters.status;
    const matchesScenario = filters.scenario === ALL_QUEUE_FILTERS || entry.request.scenario_id === filters.scenario;
    return matchesQuery && matchesStatus && matchesScenario;
  });
}

function uniqueSorted(values: string[]): string[] {
  return Array.from(new Set(values)).sort((left, right) => left.localeCompare(right));
}

function strategyActorLabel(actorType: StrategyActorType): string {
  return actorType === "insurer" ? "Versicherer (VU)" : "Versicherungsnehmer (VN)";
}

function strategyTestStatusLabel(status: StrategyDefinition["test_status"]): string {
  return status === "unit_and_regression_tested" ? "Unit + Regression" : "Unit-getestet";
}

function strategyCapabilityLabel(capability: string): string {
  return strategyCapabilityLabels[capability] ?? capability.replaceAll("_", " ");
}

function strategyValidationLabel(validation: string): string {
  if (validation === "non_negative_integer_coercion") {
    return "nichtnegative ganze Zahlen";
  }
  if (validation === "numeric_coercion_without_domain_bounds") {
    return "numerisch, noch ohne fachliche Wertebereiche";
  }
  return validation.replaceAll("_", " ");
}

function strategyTargetRangeLabel(profile: StrategySourceProfile): string {
  const prefix = profile.actor_type === "insurer" ? "VU" : "VN";
  return profile.target_id_start === profile.target_id_end
    ? `${prefix} ${profile.target_id_start}`
    : `${prefix} ${profile.target_id_start}-${profile.target_id_end}`;
}

function shortStrategyFingerprint(fingerprint: string): string {
  return fingerprint.replace("sha256:", "").slice(0, 10);
}

function shortCandidateDigest(digest: string): string {
  const value = digest.replace("sha256:", "");
  return `${value.slice(0, 12)}...${value.slice(-8)}`;
}

function formatCandidateStoredAt(value: string): string {
  const date = new Date(value);
  if (Number.isNaN(date.valueOf())) {
    return value;
  }
  return new Intl.DateTimeFormat("de-DE", {
    dateStyle: "medium",
    timeStyle: "short"
  }).format(date);
}

function strategySnapshotFieldLabel(fieldName: string): string {
  return strategySnapshotFieldLabels[fieldName] ?? fieldName.replaceAll("_", " ");
}

function strategyMaterializedSnapshotFields(
  snapshot: StrategyMaterializedVNSnapshotPayload,
  period: number | null
): Set<string> {
  if (period === 1) {
    return new Set(["initial_decisions"]);
  }
  return new Set(strategyMaterializedFieldsByRuleKind[snapshot.rule_kind] ?? []);
}

function strategySnapshotScalarLabel(value: unknown): string {
  if (value === null || value === undefined) {
    return "nicht benoetigt oder nicht belegt";
  }
  if (typeof value === "boolean") {
    return value ? "Ja" : "Nein";
  }
  if (typeof value === "number") {
    return new Intl.NumberFormat("de-DE", { maximumFractionDigits: 6 }).format(value);
  }
  return String(value);
}

function StrategySnapshotPreviewValue({ value }: { value: unknown }) {
  if (!Array.isArray(value) && (value === null || typeof value !== "object")) {
    return <span>{strategySnapshotScalarLabel(value)}</span>;
  }
  if (Array.isArray(value)) {
    if (value.length === 0) {
      return <span>keine Eintraege</span>;
    }
    if (value.every((entry) => !Array.isArray(entry) && (entry === null || typeof entry !== "object"))) {
      return <span>{value.map(strategySnapshotScalarLabel).join(" · ")}</span>;
    }
    return (
      <div className="strategy-materialized-records">
        {value.map((entry, index) => (
          <div key={index}>
            <small>{Array.isArray(entry) ? `Position ${index + 1}` : `Eintrag ${index + 1}`}</small>
            <StrategySnapshotPreviewValue value={entry} />
          </div>
        ))}
      </div>
    );
  }
  return (
    <dl className="strategy-materialized-object">
      {Object.entries(value as Record<string, unknown>).map(([fieldName, nestedValue]) => (
        <div key={fieldName}>
          <dt>{strategySnapshotFieldLabel(fieldName)}</dt>
          <dd><StrategySnapshotPreviewValue value={nestedValue} /></dd>
        </div>
      ))}
    </dl>
  );
}

function createEmptyStrategyVUStateEditor(): StrategyVUStateEditor {
  return {
    interestRate: "",
    changeShock: "",
    activePolicyholderCount: "",
    entries: []
  };
}

function parseStrategyVUStateValue(raw: string, kind: "number" | "integer" | "array"): unknown {
  const trimmed = raw.trim();
  if (!trimmed) {
    return null;
  }
  if (kind === "array") {
    try {
      return JSON.parse(trimmed) as unknown;
    } catch {
      return trimmed;
    }
  }
  const parsed = Number(trimmed);
  if (!Number.isFinite(parsed) || (kind === "integer" && !Number.isInteger(parsed))) {
    return trimmed;
  }
  return parsed;
}

function strategySnapshotContextShapeLabel(
  definition: StrategySnapshotContextFieldDefinition
): string {
  if (definition.value_shape === "boolean") {
    return "Ja oder nein";
  }
  if (definition.value_shape === "finite_number") {
    return "Endliche Zahl";
  }
  if (definition.value_shape === "integer") {
    return "Ganze Zahl";
  }
  if (definition.value_shape === "object") {
    return "JSON-Objekt";
  }
  if (definition.value_shape === "positive_integer_array") {
    return "Liste positiver IDs";
  }
  if (definition.value_shape === "number_array" && definition.fixed_length) {
    return `${definition.fixed_length} Zahlen`;
  }
  return "JSON-Liste";
}

function strategySnapshotContextPlaceholder(
  definition: StrategySnapshotContextFieldDefinition
): string {
  if (definition.value_shape === "object") {
    return '{"feld": [0.1, 0.2]}';
  }
  if (definition.value_shape === "positive_integer_array") {
    return "[1, 2, 3]";
  }
  if (definition.value_shape === "number_array") {
    const length = definition.fixed_length ?? 2;
    return `[${Array.from({ length }, (_, index) => (index + 1) / 10).join(", ")}]`;
  }
  if (definition.value_shape === "array") {
    return "[]";
  }
  return "Wert eingeben";
}

function parseStrategySnapshotContextEditorValue(
  editorValue: StrategySnapshotContextEditorValue,
  definition: StrategySnapshotContextFieldDefinition
): unknown {
  if (editorValue.explicitlyOpen) {
    return null;
  }
  const raw = editorValue.raw.trim();
  if (!raw) {
    return undefined;
  }
  if (definition.value_shape === "boolean") {
    return raw === "true" ? true : raw === "false" ? false : raw;
  }
  if (definition.value_shape === "finite_number" || definition.value_shape === "integer") {
    const parsed = Number(raw);
    return Number.isFinite(parsed) ? parsed : raw;
  }
  try {
    return JSON.parse(raw) as unknown;
  } catch {
    return raw;
  }
}

function createEmptyStrategyDraftEditor(actorType: StrategyActorType = "insurer"): StrategyDraftEditor {
  return {
    actorType,
    targetId: "",
    strategyId: "",
    activationPeriod: "",
    activeThroughRun: "",
    logicalTime: "",
    parameterValues: {}
  };
}

function createEmptyStrategyParameterValues(
  schema: StrategyParameterSchema | null
): Record<string, [string, string]> {
  return Object.fromEntries(
    (schema?.fields ?? []).map((field) => [field.field_name, ["", ""]])
  ) as Record<string, [string, string]>;
}

function parsePositiveInteger(value: string): number | null {
  if (!/^\d+$/.test(value.trim())) {
    return null;
  }
  const parsed = Number(value);
  return Number.isSafeInteger(parsed) && parsed > 0 ? parsed : null;
}

function parseStrategyParameterValue(value: string, integerOnly: boolean): number | null {
  if (!value.trim()) {
    return null;
  }
  const parsed = Number(value);
  if (!Number.isFinite(parsed) || (integerOnly && (!Number.isInteger(parsed) || parsed < 0))) {
    return null;
  }
  return parsed;
}

function createUiIdempotencyKey(queueId: string): string {
  const suffix = globalThis.crypto?.randomUUID?.() ?? `${Date.now()}`;
  return `workbench-ui-${queueId}-${suffix}`;
}

function queueActionLabel(entry: RunControlQueueEntry): string {
  if (entry.status === "planned") {
    return "Preflight lokal";
  }
  if (entry.status === "validated") {
    return "Freigabe abwarten";
  }
  if (entry.status === "blocked") {
    return "Blocker klaeren";
  }
  if (entry.status === "result_persisted") {
    return "Ergebnis pruefen";
  }
  if (entry.status === "starting") {
    return "Start laeuft";
  }
  if (entry.status === "failed") {
    return "Fehler pruefen";
  }
  if (entry.execution_enabled || entry.execution_performed) {
    return "Blocker klaeren";
  }
  return "Status pruefen";
}

function yesNoLoading(value: boolean | undefined): string {
  if (value === undefined) {
    return "laedt";
  }
  return value ? "ja" : "nein";
}

function App() {
  const [scenarios, setScenarios] = useState<ScenarioMetadata[]>([]);
  const [runs, setRuns] = useState<RunMetadata[]>([]);
  const [capabilities, setCapabilities] = useState<MetadataCapabilities | null>(null);
  const [metadataSource, setMetadataSource] = useState<MetadataSourceStatus | null>(null);
  const [metadataConsistency, setMetadataConsistency] = useState<MetadataConsistency | null>(null);
  const [strategyCatalog, setStrategyCatalog] = useState<StrategyCatalog | null>(null);
  const [strategyCatalogState, setStrategyCatalogState] = useState<DetailState>("loading");
  const [strategyCatalogError, setStrategyCatalogError] = useState<string | null>(null);
  const [strategyAssignmentContract, setStrategyAssignmentContract] =
    useState<StrategyAssignmentContract | null>(null);
  const [strategyAssignmentState, setStrategyAssignmentState] = useState<DetailState>("loading");
  const [strategyAssignmentError, setStrategyAssignmentError] = useState<string | null>(null);
  const [strategyDraftContract, setStrategyDraftContract] =
    useState<StrategyAssignmentDraftContract | null>(null);
  const [strategyDraftContractState, setStrategyDraftContractState] = useState<DetailState>("loading");
  const [strategyDraftContractError, setStrategyDraftContractError] = useState<string | null>(null);
  const [strategyDraftId, setStrategyDraftId] = useState("");
  const [strategyDraftLabel, setStrategyDraftLabel] = useState("");
  const [strategyDraftAssignments, setStrategyDraftAssignments] = useState<StrategyDraftAssignment[]>([]);
  const [strategyDraftEditor, setStrategyDraftEditor] = useState<StrategyDraftEditor>(
    createEmptyStrategyDraftEditor
  );
  const [strategyDraftEditingIndex, setStrategyDraftEditingIndex] = useState<number | null>(null);
  const [strategyDraftValidation, setStrategyDraftValidation] =
    useState<StrategyAssignmentDraftValidationReport | null>(null);
  const [strategyDraftValidationState, setStrategyDraftValidationState] = useState<DetailState>("idle");
  const [strategyDraftValidationError, setStrategyDraftValidationError] = useState<string | null>(null);
  const [strategySnapshotTranslationContract, setStrategySnapshotTranslationContract] =
    useState<StrategySnapshotTranslationContract | null>(null);
  const [strategySnapshotTranslationContractState, setStrategySnapshotTranslationContractState] =
    useState<DetailState>("loading");
  const [strategySnapshotTranslationContractError, setStrategySnapshotTranslationContractError] =
    useState<string | null>(null);
  const [strategySnapshotTranslation, setStrategySnapshotTranslation] =
    useState<StrategySnapshotTranslationReport | null>(null);
  const [strategySnapshotTranslationState, setStrategySnapshotTranslationState] =
    useState<DetailState>("idle");
  const [strategySnapshotTranslationError, setStrategySnapshotTranslationError] =
    useState<string | null>(null);
  const [strategySnapshotContextContract, setStrategySnapshotContextContract] =
    useState<StrategySnapshotContextContract | null>(null);
  const [strategySnapshotContextContractState, setStrategySnapshotContextContractState] =
    useState<DetailState>("loading");
  const [strategySnapshotContextContractError, setStrategySnapshotContextContractError] =
    useState<string | null>(null);
  const [strategySnapshotContextPeriod, setStrategySnapshotContextPeriod] = useState("");
  const [strategySnapshotContextEntries, setStrategySnapshotContextEntries] =
    useState<StrategySnapshotContextEditorEntry[]>([]);
  const [strategySnapshotContextValidation, setStrategySnapshotContextValidation] =
    useState<StrategySnapshotContextValidationReport | null>(null);
  const [strategySnapshotContextValidationState, setStrategySnapshotContextValidationState] =
    useState<DetailState>("idle");
  const [strategySnapshotContextValidationError, setStrategySnapshotContextValidationError] =
    useState<string | null>(null);
  const [strategySnapshotMaterializationContract, setStrategySnapshotMaterializationContract] =
    useState<StrategySnapshotMaterializationContract | null>(null);
  const [strategySnapshotMaterializationContractState, setStrategySnapshotMaterializationContractState] =
    useState<DetailState>("loading");
  const [strategySnapshotMaterializationContractError, setStrategySnapshotMaterializationContractError] =
    useState<string | null>(null);
  const [strategySnapshotMaterialization, setStrategySnapshotMaterialization] =
    useState<StrategySnapshotMaterializationReport | null>(null);
  const [strategySnapshotMaterializationState, setStrategySnapshotMaterializationState] =
    useState<DetailState>("idle");
  const [strategySnapshotMaterializationError, setStrategySnapshotMaterializationError] =
    useState<string | null>(null);
  const [strategyVUInputContract, setStrategyVUInputContract] =
    useState<StrategyVUSnapshotInputContract | null>(null);
  const [strategyVUStateContract, setStrategyVUStateContract] =
    useState<StrategyVUSnapshotStateContract | null>(null);
  const [strategyVUMaterializationContract, setStrategyVUMaterializationContract] =
    useState<StrategyVUSnapshotMaterializationContract | null>(null);
  const [strategyVUContractsState, setStrategyVUContractsState] =
    useState<DetailState>("loading");
  const [strategyVUContractsError, setStrategyVUContractsError] =
    useState<string | null>(null);
  const [strategyVUStateEditor, setStrategyVUStateEditor] =
    useState<StrategyVUStateEditor>(createEmptyStrategyVUStateEditor);
  const [strategyVUMaterialization, setStrategyVUMaterialization] =
    useState<StrategyVUSnapshotMaterializationReport | null>(null);
  const [strategyVUMaterializationState, setStrategyVUMaterializationState] =
    useState<DetailState>("idle");
  const [strategyVUMaterializationError, setStrategyVUMaterializationError] =
    useState<string | null>(null);
  const [strategyCandidateOverview, setStrategyCandidateOverview] =
    useState<StrategyExecutionCandidateOverview | null>(null);
  const [strategyCandidateOverviewState, setStrategyCandidateOverviewState] =
    useState<DetailState>("loading");
  const [strategyCandidateOverviewError, setStrategyCandidateOverviewError] =
    useState<string | null>(null);
  const [selectedStrategyCandidateId, setSelectedStrategyCandidateId] =
    useState<string | null>(null);
  const [strategyCandidateOverviewRevision, setStrategyCandidateOverviewRevision] =
    useState(0);
  const [strategyWorkbenchView, setStrategyWorkbenchView] = useState<StrategyWorkbenchView>("catalog");
  const [runControlQueue, setRunControlQueue] = useState<RunControlQueueOverview | null>(null);
  const [runControlRequestContract, setRunControlRequestContract] = useState<RunControlRequestContract | null>(null);
  const [runControlDryRunContract, setRunControlDryRunContract] = useState<RunControlDryRunContract | null>(null);
  const [runControlAdapterResultContract, setRunControlAdapterResultContract] =
    useState<RunControlAdapterResultApiContract | null>(null);
  const [runControlAdapterStartContract, setRunControlAdapterStartContract] =
    useState<RunControlAdapterStartContract | null>(null);
  const [executionReleaseActor, setExecutionReleaseActor] = useState("workbench-ui");
  const [executionReleaseReason, setExecutionReleaseReason] = useState("Kontrollierter Workbench-Start");
  const [executionReleaseConfirmed, setExecutionReleaseConfirmed] = useState(false);
  const [executionReleaseRequest, setExecutionReleaseRequest] =
    useState<RunControlExecutionReleaseRequest | null>(null);
  const [executionReleaseResult, setExecutionReleaseResult] =
    useState<RunControlExecutionReleaseResult | null>(null);
  const [executionReleaseState, setExecutionReleaseState] = useState<DetailState>("idle");
  const [executionReleaseError, setExecutionReleaseError] = useState<string | null>(null);
  const [adapterStartResult, setAdapterStartResult] = useState<RunControlAdapterStartResponse | null>(null);
  const [adapterStartState, setAdapterStartState] = useState<DetailState>("idle");
  const [adapterStartError, setAdapterStartError] = useState<string | null>(null);
  const [runControlDryRunResult, setRunControlDryRunResult] = useState<RunControlDryRunResult | null>(null);
  const [runControlDryRunState, setRunControlDryRunState] = useState<DetailState>("idle");
  const [runControlDryRunError, setRunControlDryRunError] = useState<string | null>(null);
  const [runControlQueueEnqueueResult, setRunControlQueueEnqueueResult] = useState<RunControlQueueEnqueueResult | null>(null);
  const [runControlQueueEnqueueState, setRunControlQueueEnqueueState] = useState<DetailState>("idle");
  const [runControlQueueEnqueueError, setRunControlQueueEnqueueError] = useState<string | null>(null);
  const [runControlActionPlan, setRunControlActionPlan] = useState<RunControlQueueActionPlan | null>(null);
  const [runControlActionPlanState, setRunControlActionPlanState] = useState<DetailState>("idle");
  const [runControlActionPlanError, setRunControlActionPlanError] = useState<string | null>(null);
  const [runControlExecutionResult, setRunControlExecutionResult] = useState<RunControlExecutionResult | null>(null);
  const [runControlExecutionResultState, setRunControlExecutionResultState] = useState<DetailState>("idle");
  const [runControlExecutionResultError, setRunControlExecutionResultError] = useState<string | null>(null);
  const [runControlExecutionHistory, setRunControlExecutionHistory] =
    useState<RunControlExecutionHistory | null>(null);
  const [runControlExecutionHistoryState, setRunControlExecutionHistoryState] = useState<DetailState>("idle");
  const [runControlExecutionHistoryError, setRunControlExecutionHistoryError] = useState<string | null>(null);
  const [executionEvidenceRevision, setExecutionEvidenceRevision] = useState(0);
  const [runControlCoreBridge, setRunControlCoreBridge] = useState<RunControlCoreDiagnosticsBridge | null>(null);
  const [coreValidation, setCoreValidation] = useState<CoreValidationOverview | null>(null);
  const [carryoverProbeContract, setCarryoverProbeContract] = useState<CoreValidationCarryoverProbeContract | null>(
    null
  );
  const [selectedQueueId, setSelectedQueueId] = useState<string | null>(null);
  const [queueDetail, setQueueDetail] = useState<RunControlQueueDetail | null>(null);
  const [queueDetailState, setQueueDetailState] = useState<DetailState>("idle");
  const [queueDetailError, setQueueDetailError] = useState<string | null>(null);
  const [runControlPreflight, setRunControlPreflight] = useState<RunControlPreflight | null>(null);
  const [runControlPreflightState, setRunControlPreflightState] = useState<DetailState>("idle");
  const [runControlPreflightError, setRunControlPreflightError] = useState<string | null>(null);
  const [healthStatus, setHealthStatus] = useState<HealthStatus | null>(null);
  const [versionInfo, setVersionInfo] = useState<VersionInfo | null>(null);
  const [selectedScenarioId, setSelectedScenarioId] = useState<string | null>(null);
  const [selectedRunId, setSelectedRunId] = useState<string | null>(null);
  const [scenarioDetail, setScenarioDetail] = useState<ScenarioMetadata | null>(null);
  const [runDetail, setRunDetail] = useState<RunMetadata | null>(null);
  const [detailState, setDetailState] = useState<DetailState>("idle");
  const [detailError, setDetailError] = useState<string | null>(null);
  const [metadataState, setMetadataState] = useState<"loading" | "ready" | "error">("loading");
  const [scenarioQuery, setScenarioQuery] = useState("");
  const [scenarioStatusFilter, setScenarioStatusFilter] = useState(ALL_SCENARIO_FILTERS);
  const [scenarioSourceFilter, setScenarioSourceFilter] = useState(ALL_SCENARIO_FILTERS);
  const [scenarioScopeFilter, setScenarioScopeFilter] = useState(ALL_SCENARIO_FILTERS);
  const [runQuery, setRunQuery] = useState("");
  const [runStatusFilter, setRunStatusFilter] = useState(ALL_RUN_FILTERS);
  const [runScenarioFilter, setRunScenarioFilter] = useState(ALL_RUN_FILTERS);
  const [runSourceFilter, setRunSourceFilter] = useState(ALL_RUN_FILTERS);
  const [queueQuery, setQueueQuery] = useState("");
  const [queueStatusFilter, setQueueStatusFilter] = useState(ALL_QUEUE_FILTERS);
  const [queueScenarioFilter, setQueueScenarioFilter] = useState(ALL_QUEUE_FILTERS);

  useEffect(() => {
    let active = true;

    async function loadExecutionEvidence() {
      if (!selectedQueueId) {
        setRunControlExecutionResult(null);
        setRunControlExecutionResultState("idle");
        setRunControlExecutionResultError(null);
        setRunControlExecutionHistory(null);
        setRunControlExecutionHistoryState("idle");
        setRunControlExecutionHistoryError(null);
        return;
      }
      setRunControlExecutionResultState("loading");
      setRunControlExecutionResultError(null);
      setRunControlExecutionHistoryState("loading");
      setRunControlExecutionHistoryError(null);
      try {
        const [resultResponse, historyResponse] = await Promise.all([
          fetch(`/api/run-control/execution-result/${encodeURIComponent(selectedQueueId)}`),
          fetch(`/api/run-control/execution-history/${encodeURIComponent(selectedQueueId)}`)
        ]);
        const resultPayload = (await resultResponse.json()) as RunControlExecutionResult;
        const historyPayload = (await historyResponse.json()) as RunControlExecutionHistory;
        if (active) {
          if (resultResponse.status === 404) {
            setRunControlExecutionResult(null);
            setRunControlExecutionResultError("kein persistiertes Ergebnis");
            setRunControlExecutionResultState("ready");
          } else if (!resultResponse.ok) {
            setRunControlExecutionResult(null);
            setRunControlExecutionResultError(
              resultPayload.message ?? "Run-Control-Ergebnis nicht erreichbar"
            );
            setRunControlExecutionResultState("error");
          } else {
            setRunControlExecutionResult(resultPayload);
            setRunControlExecutionResultState("ready");
          }
          if (!historyResponse.ok) {
            setRunControlExecutionHistory(null);
            setRunControlExecutionHistoryError(
              historyPayload.message ?? "Run-Control-Verlauf nicht erreichbar"
            );
            setRunControlExecutionHistoryState("error");
          } else {
            setRunControlExecutionHistory(historyPayload);
            setRunControlExecutionHistoryState("ready");
          }
        }
      } catch (error) {
        if (active) {
          setRunControlExecutionResult(null);
          setRunControlExecutionHistory(null);
          setRunControlExecutionResultError(
            error instanceof Error ? error.message : "Run-Control-Ergebnis nicht erreichbar"
          );
          setRunControlExecutionHistoryError(
            error instanceof Error ? error.message : "Run-Control-Verlauf nicht erreichbar"
          );
          setRunControlExecutionResultState("error");
          setRunControlExecutionHistoryState("error");
        }
      }
    }

    loadExecutionEvidence();
    return () => {
      active = false;
    };
  }, [selectedQueueId, executionEvidenceRevision]);

  useEffect(() => {
    setExecutionReleaseConfirmed(false);
    setExecutionReleaseRequest(null);
    setExecutionReleaseResult(null);
    setExecutionReleaseState("idle");
    setExecutionReleaseError(null);
    setAdapterStartResult(null);
    setAdapterStartState("idle");
    setAdapterStartError(null);
  }, [selectedQueueId]);

  useEffect(() => {
    let active = true;

    async function loadMetadata() {
      try {
        const [
          scenarioResponse,
          runResponse,
          capabilityResponse,
          sourceResponse,
          consistencyResponse,
          coreValidationResponse,
          carryoverProbeContractResponse,
          runControlQueueResponse,
          runControlActionPlanResponse,
          runControlCoreBridgeResponse,
          runControlRequestContractResponse,
          runControlDryRunContractResponse,
          runControlAdapterResultContractResponse,
          runControlAdapterStartContractResponse,
          healthResponse,
          versionResponse
        ] = await Promise.all([
          fetch("/api/scenarios"),
          fetch("/api/runs"),
          fetch("/api/metadata/capabilities"),
          fetch("/api/metadata/source"),
          fetch("/api/metadata/consistency"),
          fetch("/api/core-validation/overview"),
          fetch("/api/core-validation/carryover-probe-contract"),
          fetch("/api/run-control/queue"),
          fetch("/api/run-control/queue/action-plan"),
          fetch("/api/run-control/core-diagnostics-bridge"),
          fetch("/api/run-control/request-contract"),
          fetch("/api/run-control/dry-run-contract"),
          fetch("/api/run-control/adapter-result-contract"),
          fetch("/api/run-control/adapter-start-contract"),
          fetch("/api/health"),
          fetch("/api/version")
        ]);
        if (
          !scenarioResponse.ok ||
          !runResponse.ok ||
          !capabilityResponse.ok ||
          !sourceResponse.ok ||
          !consistencyResponse.ok ||
          !coreValidationResponse.ok ||
          !carryoverProbeContractResponse.ok ||
          !runControlQueueResponse.ok ||
          !runControlActionPlanResponse.ok ||
          !runControlCoreBridgeResponse.ok ||
          !runControlRequestContractResponse.ok ||
          !runControlDryRunContractResponse.ok ||
          !runControlAdapterResultContractResponse.ok ||
          !runControlAdapterStartContractResponse.ok ||
          !healthResponse.ok ||
          !versionResponse.ok
        ) {
          throw new Error("metadata request failed");
        }
        const [
          scenarioPayload,
          runPayload,
          capabilityPayload,
          sourcePayload,
          consistencyPayload,
          coreValidationPayload,
          carryoverProbeContractPayload,
          runControlQueuePayload,
          runControlActionPlanPayload,
          runControlCoreBridgePayload,
          runControlRequestContractPayload,
          runControlDryRunContractPayload,
          runControlAdapterResultContractPayload,
          runControlAdapterStartContractPayload,
          healthPayload,
          versionPayload
        ] = await Promise.all([
          scenarioResponse.json() as Promise<MetadataResponse<ScenarioMetadata>>,
          runResponse.json() as Promise<MetadataResponse<RunMetadata>>,
          capabilityResponse.json() as Promise<MetadataCapabilities>,
          sourceResponse.json() as Promise<MetadataSourceStatus>,
          consistencyResponse.json() as Promise<MetadataConsistency>,
          coreValidationResponse.json() as Promise<CoreValidationOverview>,
          carryoverProbeContractResponse.json() as Promise<CoreValidationCarryoverProbeContract>,
          runControlQueueResponse.json() as Promise<RunControlQueueOverview>,
          runControlActionPlanResponse.json() as Promise<RunControlQueueActionPlan>,
          runControlCoreBridgeResponse.json() as Promise<RunControlCoreDiagnosticsBridge>,
          runControlRequestContractResponse.json() as Promise<RunControlRequestContract>,
          runControlDryRunContractResponse.json() as Promise<RunControlDryRunContract>,
          runControlAdapterResultContractResponse.json() as Promise<RunControlAdapterResultApiContract>,
          runControlAdapterStartContractResponse.json() as Promise<RunControlAdapterStartContract>,
          healthResponse.json() as Promise<HealthStatus>,
          versionResponse.json() as Promise<VersionInfo>
        ]);
        if (active) {
          setScenarios(scenarioPayload.items);
          setRuns(runPayload.items);
          setCapabilities(capabilityPayload);
          setMetadataSource(sourcePayload);
          setMetadataConsistency(consistencyPayload);
          setCoreValidation(coreValidationPayload);
          setCarryoverProbeContract(carryoverProbeContractPayload);
          setRunControlQueue(runControlQueuePayload);
          setRunControlActionPlan(runControlActionPlanPayload);
          setRunControlActionPlanState("ready");
          setRunControlCoreBridge(runControlCoreBridgePayload);
          setRunControlRequestContract(runControlRequestContractPayload);
          setRunControlDryRunContract(runControlDryRunContractPayload);
          setRunControlAdapterResultContract(runControlAdapterResultContractPayload);
          setRunControlAdapterStartContract(runControlAdapterStartContractPayload);
          setSelectedQueueId((current) => current ?? runControlQueuePayload.entries[0]?.queue_id ?? null);
          setHealthStatus(healthPayload);
          setVersionInfo(versionPayload);
          setSelectedScenarioId((current) => current ?? scenarioPayload.items[0]?.id ?? null);
          setSelectedRunId((current) => current ?? runPayload.items[0]?.id ?? null);
          setMetadataState("ready");
        }
      } catch {
        if (active) {
          setMetadataState("error");
        }
      }
    }

    loadMetadata();
    return () => {
      active = false;
    };
  }, []);

  useEffect(() => {
    let active = true;

    async function loadStrategyCandidateOverview() {
      setStrategyCandidateOverviewState("loading");
      setStrategyCandidateOverviewError(null);
      try {
        const response = await fetch("/api/strategies/execution-candidates");
        if (!response.ok) {
          throw new Error("Kandidatenablage nicht lesbar");
        }
        const payload = (await response.json()) as StrategyExecutionCandidateOverview;
        if (active) {
          setStrategyCandidateOverview(payload);
          setSelectedStrategyCandidateId((current) => (
            payload.candidates.some((candidate) => candidate.candidate_id === current)
              ? current
              : payload.candidates[0]?.candidate_id ?? null
          ));
          setStrategyCandidateOverviewState("ready");
        }
      } catch (error) {
        if (active) {
          setStrategyCandidateOverview(null);
          setSelectedStrategyCandidateId(null);
          setStrategyCandidateOverviewError(
            error instanceof Error ? error.message : "Kandidatenablage nicht erreichbar"
          );
          setStrategyCandidateOverviewState("error");
        }
      }
    }

    loadStrategyCandidateOverview();
    return () => {
      active = false;
    };
  }, [strategyCandidateOverviewRevision]);

  useEffect(() => {
    let active = true;

    async function loadStrategyCatalog() {
      setStrategyCatalogState("loading");
      setStrategyCatalogError(null);
      try {
        const response = await fetch("/api/strategies/catalog");
        if (!response.ok) {
          throw new Error("Strategiekatalog nicht erreichbar");
        }
        const payload = (await response.json()) as StrategyCatalog;
        if (active) {
          setStrategyCatalog(payload);
          setStrategyCatalogState("ready");
        }
      } catch (error) {
        if (active) {
          setStrategyCatalog(null);
          setStrategyCatalogError(error instanceof Error ? error.message : "Strategiekatalog nicht erreichbar");
          setStrategyCatalogState("error");
        }
      }
    }

    loadStrategyCatalog();
    return () => {
      active = false;
    };
  }, []);

  useEffect(() => {
    let active = true;

    async function loadStrategyAssignmentContract() {
      setStrategyAssignmentState("loading");
      setStrategyAssignmentError(null);
      try {
        const response = await fetch("/api/strategies/assignment-contract");
        if (!response.ok) {
          throw new Error("Strategiezuordnungen nicht erreichbar");
        }
        const payload = (await response.json()) as StrategyAssignmentContract;
        if (active) {
          setStrategyAssignmentContract(payload);
          setStrategyAssignmentState("ready");
        }
      } catch (error) {
        if (active) {
          setStrategyAssignmentContract(null);
          setStrategyAssignmentError(
            error instanceof Error ? error.message : "Strategiezuordnungen nicht erreichbar"
          );
          setStrategyAssignmentState("error");
        }
      }
    }

    loadStrategyAssignmentContract();
    return () => {
      active = false;
    };
  }, []);

  useEffect(() => {
    let active = true;

    async function loadStrategyDraftContract() {
      setStrategyDraftContractState("loading");
      setStrategyDraftContractError(null);
      try {
        const response = await fetch("/api/strategies/assignment-draft-contract");
        if (!response.ok) {
          throw new Error("Strategieentwurfsformat nicht erreichbar");
        }
        const payload = (await response.json()) as StrategyAssignmentDraftContract;
        if (active) {
          setStrategyDraftContract(payload);
          setStrategyDraftContractState("ready");
        }
      } catch (error) {
        if (active) {
          setStrategyDraftContract(null);
          setStrategyDraftContractError(
            error instanceof Error ? error.message : "Strategieentwurfsformat nicht erreichbar"
          );
          setStrategyDraftContractState("error");
        }
      }
    }

    loadStrategyDraftContract();
    return () => {
      active = false;
    };
  }, []);

  useEffect(() => {
    let active = true;

    async function loadStrategySnapshotTranslationContract() {
      setStrategySnapshotTranslationContractState("loading");
      setStrategySnapshotTranslationContractError(null);
      try {
        const response = await fetch(
          "/api/strategies/assignment-snapshot-translation-contract"
        );
        if (!response.ok) {
          throw new Error("Snapshot-Bauplanvertrag nicht erreichbar");
        }
        const payload = (await response.json()) as StrategySnapshotTranslationContract;
        if (active) {
          setStrategySnapshotTranslationContract(payload);
          setStrategySnapshotTranslationContractState("ready");
        }
      } catch (error) {
        if (active) {
          setStrategySnapshotTranslationContract(null);
          setStrategySnapshotTranslationContractError(
            error instanceof Error ? error.message : "Snapshot-Bauplanvertrag nicht erreichbar"
          );
          setStrategySnapshotTranslationContractState("error");
        }
      }
    }

    loadStrategySnapshotTranslationContract();
    return () => {
      active = false;
    };
  }, []);

  useEffect(() => {
    let active = true;

    async function loadStrategySnapshotContextContract() {
      setStrategySnapshotContextContractState("loading");
      setStrategySnapshotContextContractError(null);
      try {
        const response = await fetch(
          "/api/strategies/assignment-snapshot-context-contract"
        );
        if (!response.ok) {
          throw new Error("Snapshot-Kontextvertrag nicht erreichbar");
        }
        const payload = (await response.json()) as StrategySnapshotContextContract;
        if (active) {
          setStrategySnapshotContextContract(payload);
          setStrategySnapshotContextContractState("ready");
        }
      } catch (error) {
        if (active) {
          setStrategySnapshotContextContract(null);
          setStrategySnapshotContextContractError(
            error instanceof Error ? error.message : "Snapshot-Kontextvertrag nicht erreichbar"
          );
          setStrategySnapshotContextContractState("error");
        }
      }
    }

    loadStrategySnapshotContextContract();
    return () => {
      active = false;
    };
  }, []);

  useEffect(() => {
    let active = true;

    async function loadStrategySnapshotMaterializationContract() {
      setStrategySnapshotMaterializationContractState("loading");
      setStrategySnapshotMaterializationContractError(null);
      try {
        const response = await fetch(
          "/api/strategies/assignment-snapshot-materialization-contract"
        );
        if (!response.ok) {
          throw new Error("VN-Snapshotvertrag nicht erreichbar");
        }
        const payload = (await response.json()) as StrategySnapshotMaterializationContract;
        if (active) {
          setStrategySnapshotMaterializationContract(payload);
          setStrategySnapshotMaterializationContractState("ready");
        }
      } catch (error) {
        if (active) {
          setStrategySnapshotMaterializationContract(null);
          setStrategySnapshotMaterializationContractError(
            error instanceof Error ? error.message : "VN-Snapshotvertrag nicht erreichbar"
          );
          setStrategySnapshotMaterializationContractState("error");
        }
      }
    }

    loadStrategySnapshotMaterializationContract();
    return () => {
      active = false;
    };
  }, []);

  useEffect(() => {
    let active = true;

    async function loadStrategyVUContracts() {
      setStrategyVUContractsState("loading");
      setStrategyVUContractsError(null);
      try {
        const [inputResponse, stateResponse, materializationResponse] = await Promise.all([
          fetch("/api/strategies/assignment-vu-snapshot-materialization-validation-contract"),
          fetch("/api/strategies/assignment-vu-snapshot-state-contract"),
          fetch("/api/strategies/assignment-vu-snapshot-materialization-contract")
        ]);
        if (!inputResponse.ok || !stateResponse.ok || !materializationResponse.ok) {
          throw new Error("VU-Snapshotvertraege nicht erreichbar");
        }
        const [input, state, materialization] = await Promise.all([
          inputResponse.json() as Promise<StrategyVUSnapshotInputContract>,
          stateResponse.json() as Promise<StrategyVUSnapshotStateContract>,
          materializationResponse.json() as Promise<StrategyVUSnapshotMaterializationContract>
        ]);
        if (active) {
          setStrategyVUInputContract(input);
          setStrategyVUStateContract(state);
          setStrategyVUMaterializationContract(materialization);
          setStrategyVUContractsState("ready");
        }
      } catch (error) {
        if (active) {
          setStrategyVUInputContract(null);
          setStrategyVUStateContract(null);
          setStrategyVUMaterializationContract(null);
          setStrategyVUContractsError(
            error instanceof Error ? error.message : "VU-Snapshotvertraege nicht erreichbar"
          );
          setStrategyVUContractsState("error");
        }
      }
    }

    loadStrategyVUContracts();
    return () => {
      active = false;
    };
  }, []);

  useEffect(() => {
    let active = true;

    async function loadQueueDetail() {
      if (!selectedQueueId) {
        setQueueDetail(null);
        setQueueDetailState("idle");
        setQueueDetailError(null);
        return;
      }
      setQueueDetailState("loading");
      setQueueDetailError(null);
      try {
        const response = await fetch(`/api/run-control/queue/${encodeURIComponent(selectedQueueId)}`);
        if (response.status === 404) {
          throw new Error("Queue-Eintrag nicht gefunden");
        }
        if (!response.ok) {
          throw new Error("Queue-Detail nicht erreichbar");
        }
        const payload = (await response.json()) as RunControlQueueDetail;
        if (active) {
          setQueueDetail(payload);
          setQueueDetailState("ready");
        }
      } catch (error) {
        if (active) {
          setQueueDetail(null);
          setQueueDetailError(error instanceof Error ? error.message : "Queue-Detail nicht erreichbar");
          setQueueDetailState("error");
        }
      }
    }

    loadQueueDetail();
    return () => {
      active = false;
    };
  }, [selectedQueueId]);

  useEffect(() => {
    let active = true;

    async function loadRunControlPreflight() {
      if (!selectedRunId) {
        setRunControlPreflight(null);
        setRunControlPreflightState("idle");
        setRunControlPreflightError(null);
        return;
      }
      setRunControlPreflightState("loading");
      setRunControlPreflightError(null);
      try {
        const response = await fetch(`/api/run-control/preflight/${encodeURIComponent(selectedRunId)}`);
        if (!response.ok) {
          throw new Error("Run-Control-Preflight nicht erreichbar");
        }
        const payload = (await response.json()) as RunControlPreflight;
        if (active) {
          setRunControlPreflight(payload);
          setRunControlPreflightState("ready");
        }
      } catch (error) {
        if (active) {
          setRunControlPreflight(null);
          setRunControlPreflightError(error instanceof Error ? error.message : "Run-Control-Preflight nicht erreichbar");
          setRunControlPreflightState("error");
        }
      }
    }

    loadRunControlPreflight();
    return () => {
      active = false;
    };
  }, [selectedRunId]);

  useEffect(() => {
    let active = true;

    async function loadDetails() {
      if (!selectedScenarioId || !selectedRunId) {
        return;
      }
      setDetailState("loading");
      setDetailError(null);
      try {
        const [scenarioResponse, runResponse] = await Promise.all([
          fetch(`/api/scenarios/${encodeURIComponent(selectedScenarioId)}`),
          fetch(`/api/runs/${encodeURIComponent(selectedRunId)}`)
        ]);
        if (scenarioResponse.status === 404 || runResponse.status === 404) {
          throw new Error("Metadaten nicht gefunden");
        }
        if (!scenarioResponse.ok || !runResponse.ok) {
          throw new Error("Detaildaten nicht erreichbar");
        }
        const [scenarioPayload, runPayload] = await Promise.all([
          scenarioResponse.json() as Promise<ScenarioMetadata>,
          runResponse.json() as Promise<RunMetadata>
        ]);
        if (active) {
          setScenarioDetail(scenarioPayload);
          setRunDetail(runPayload);
          setDetailState("ready");
        }
      } catch (error) {
        if (active) {
          setScenarioDetail(null);
          setRunDetail(null);
          setDetailError(error instanceof Error ? error.message : "Detaildaten nicht erreichbar");
          setDetailState("error");
        }
      }
    }

    loadDetails();
    return () => {
      active = false;
    };
  }, [selectedScenarioId, selectedRunId]);

  const primaryScenario = scenarios[0];
  const primaryRun = runs[0];
  const writeLabel = capabilities?.writes.scenario_metadata.enabled ? "aktiv" : "gesperrt";
  const executionLabel = capabilities?.simulation_execution.enabled ? "aktiv" : "gesperrt";
  const storageLabel = metadataSource?.storage_kind === "sqlite" ? "SQLite-Datei" : "Memory";
  const storagePath = metadataSource?.path ?? "nicht konfiguriert";
  const strategyCatalogStatusLabel =
    strategyCatalogState === "error"
      ? strategyCatalogError ?? "nicht erreichbar"
      : strategyCatalogState === "ready"
        ? "bereit"
        : "laedt";
  const strategyCatalogBoundaryLabel = !strategyCatalog
    ? "wird geladen"
    : !strategyCatalog.selection_enabled &&
        !strategyCatalog.parameter_editing_enabled &&
        !strategyCatalog.writes_enabled &&
        !strategyCatalog.execution_enabled &&
        !strategyCatalog.simulation_performed
      ? "Nur lesen"
      : "Grenze pruefen";
  const strategyAssignmentStatusLabel =
    strategyAssignmentState === "error"
      ? strategyAssignmentError ?? "nicht erreichbar"
      : strategyAssignmentState === "ready"
        ? "bereit"
        : "laedt";
  const strategyAssignmentBoundaryLabel = !strategyAssignmentContract
    ? "wird geladen"
    : !strategyAssignmentContract.assignment_editing_enabled &&
        !strategyAssignmentContract.parameter_editing_enabled &&
        !strategyAssignmentContract.writes_enabled &&
        !strategyAssignmentContract.execution_enabled &&
        !strategyAssignmentContract.simulation_performed
      ? "Nur lesen"
      : "Grenze pruefen";
  const selectedStrategyCandidate = strategyCandidateOverview?.candidates.find(
    (candidate) => candidate.candidate_id === selectedStrategyCandidateId
  ) ?? null;
  const strategyCandidateStorageLabel = !strategyCandidateOverview
    ? "wird geladen"
    : strategyCandidateOverview.storage.kind !== "sqlite"
      ? "nicht konfiguriert"
      : strategyCandidateOverview.storage.store_initialized
        ? "SQLite bereit"
        : "noch leer";
  const strategyCandidateIntegrityLabel = strategyCandidateOverviewState === "error"
    ? "Pruefung fehlgeschlagen"
    : strategyCandidateOverviewState !== "ready"
      ? "wird geladen"
      : strategyCandidateOverview?.candidate_count === 0
        ? "keine Kandidaten"
        : strategyCandidateOverview?.all_candidate_digests_verified
          ? "Digests geprueft"
          : "Pruefung offen";
  const strategyDefinitionById = new Map(
    (strategyCatalog?.strategies ?? []).map((strategy) => [strategy.strategy_id, strategy])
  );
  const strategyDraftEligibleStrategies = (strategyCatalog?.strategies ?? []).filter(
    (strategy) => strategy.actor_type === strategyDraftEditor.actorType
  );
  const selectedStrategyDraftDefinition = strategyDefinitionById.get(strategyDraftEditor.strategyId) ?? null;
  const selectedStrategyDraftSchema = strategyAssignmentContract?.parameter_schemas.find(
    (schema) => schema.schema_id === selectedStrategyDraftDefinition?.parameter_schema
  ) ?? null;
  const strategyDraftTargetLimit = strategyDraftContract?.target_limits[strategyDraftEditor.actorType] ?? null;
  const strategyDraftTargetId = parsePositiveInteger(strategyDraftEditor.targetId);
  const strategyDraftActivationPeriod = parsePositiveInteger(strategyDraftEditor.activationPeriod);
  const strategyDraftActiveThroughRun = parsePositiveInteger(strategyDraftEditor.activeThroughRun);
  const strategyDraftLogicalTime = parsePositiveInteger(strategyDraftEditor.logicalTime);
  const strategyDraftTargetDuplicate = strategyDraftAssignments.some(
    (assignment, index) =>
      index !== strategyDraftEditingIndex &&
      assignment.actor_type === strategyDraftEditor.actorType &&
      assignment.target_id === strategyDraftTargetId
  );
  const strategyDraftParametersComplete = (selectedStrategyDraftSchema?.fields ?? []).every((field) => {
    const values = strategyDraftEditor.parameterValues[field.field_name];
    const integerOnly = field.python_type === "list[int]";
    return Boolean(
      values &&
      parseStrategyParameterValue(values[0], integerOnly) !== null &&
      parseStrategyParameterValue(values[1], integerOnly) !== null
    );
  });
  const canApplyStrategyDraftAssignment = Boolean(
    strategyDraftTargetId &&
    strategyDraftTargetLimit &&
    strategyDraftTargetId >= strategyDraftTargetLimit.minimum &&
    strategyDraftTargetId <= strategyDraftTargetLimit.maximum &&
    !strategyDraftTargetDuplicate &&
    selectedStrategyDraftDefinition?.actor_type === strategyDraftEditor.actorType &&
    strategyDraftActivationPeriod &&
    strategyDraftActiveThroughRun &&
    strategyDraftActiveThroughRun >= strategyDraftActivationPeriod &&
    strategyDraftLogicalTime &&
    strategyDraftParametersComplete
  );
  const canValidateStrategyDraft = Boolean(
    strategyDraftContract &&
    strategyDraftId.trim() &&
    strategyDraftLabel.trim() &&
    strategyDraftAssignments.length > 0 &&
    strategyDraftValidationState !== "loading"
  );
  const strategyDraftValidationLabel =
    strategyDraftValidationState === "error"
      ? "nicht erreichbar"
      : strategyDraftValidationState === "loading"
        ? "wird geprueft"
        : strategyDraftValidation
          ? strategyDraftValidation.valid
            ? "gueltig"
            : "Fehler gefunden"
          : "noch nicht geprueft";
  const strategySnapshotOpenFieldCount = (strategySnapshotTranslation?.entries ?? []).reduce(
    (total, entry) => total + entry.unresolved_snapshot_fields.length,
    0
  );
  const strategySnapshotTranslationStatusLabel =
    strategySnapshotTranslationState === "error"
      ? "nicht erreichbar"
      : strategySnapshotTranslationState === "loading"
        ? "wird erstellt"
        : strategySnapshotTranslation?.translation_complete
          ? "vollstaendig zugeordnet"
          : "noch keine Vorschau";
  const canTranslateStrategyDraft = Boolean(
    strategySnapshotTranslationContract &&
    strategySnapshotTranslationContractState === "ready" &&
    strategyDraftValidation?.valid &&
    strategySnapshotTranslationState !== "loading"
  );

  const strategySnapshotContextFieldByName = new Map(
    (strategySnapshotContextContract?.field_definitions ?? []).map((definition) => [
      definition.field_name,
      definition
    ])
  );
  const strategySnapshotContextExpectedValueCount = strategySnapshotContextEntries.reduce(
    (total, entry) => total + Object.keys(entry.values).length,
    0
  );
  const strategySnapshotContextEnteredValueCount = strategySnapshotContextEntries.reduce(
    (total, entry) => total + Object.values(entry.values).filter(
      (value) => value.explicitlyOpen || Boolean(value.raw.trim())
    ).length,
    0
  );
  const strategySnapshotContextValidationLabel =
    strategySnapshotContextValidationState === "error"
      ? "nicht erreichbar"
      : strategySnapshotContextValidationState === "loading"
        ? "wird geprueft"
        : strategySnapshotContextValidation
          ? strategySnapshotContextValidation.valid
            ? "formal gueltig"
            : "Fehler gefunden"
          : strategySnapshotContextEntries.length > 0
            ? "noch nicht geprueft"
            : "noch nicht angelegt";
  const strategySnapshotContextPeriodValue = parsePositiveInteger(strategySnapshotContextPeriod);
  const canInitializeStrategySnapshotContext = Boolean(
    strategySnapshotContextContract &&
    strategySnapshotContextContractState === "ready" &&
    strategyDraftValidation?.valid &&
    strategySnapshotTranslation?.translation_complete &&
    strategySnapshotTranslation.entries.length > 0
  );
  const canValidateStrategySnapshotContext = Boolean(
    canInitializeStrategySnapshotContext &&
    strategySnapshotContextPeriodValue &&
    strategySnapshotContextEntries.length === strategySnapshotTranslation?.entries.length &&
    strategySnapshotContextValidationState !== "loading"
  );

  const strategySnapshotMaterializationStatusLabel =
    strategySnapshotMaterializationState === "error"
      ? "nicht erreichbar"
      : strategySnapshotMaterializationState === "loading"
        ? "wird erzeugt"
        : strategySnapshotMaterialization?.materialization_complete
          ? "vollstaendig"
          : strategySnapshotMaterialization?.issue_count
            ? "Eingaben unvollstaendig"
            : "noch keine Vorschau";
  const canMaterializeStrategySnapshots = Boolean(
    strategySnapshotMaterializationContract &&
    strategySnapshotMaterializationContractState === "ready" &&
    strategySnapshotContextValidation?.valid &&
    strategySnapshotMaterializationState !== "loading"
  );
  const strategyVUTranslationEntries = (strategySnapshotTranslation?.entries ?? []).filter(
    (entry) => entry.actor_type === "insurer"
  );
  const strategyVUMaterializationStatusLabel =
    strategyVUMaterializationState === "error"
      ? "nicht erreichbar"
      : strategyVUMaterializationState === "loading"
        ? "wird erzeugt"
        : strategyVUMaterialization?.materialization_complete
          ? "vollstaendig"
          : strategyVUMaterialization?.issue_count
            ? "Herkunft oder Eingabe fehlerhaft"
            : strategyVUStateEditor.entries.length > 0
              ? "Zustandsbeleg offen"
              : "noch keine Vorschau";
  const canInitializeStrategyVUState = Boolean(
    strategyVUContractsState === "ready" &&
    strategyVUStateContract &&
    strategySnapshotContextValidation?.valid &&
    strategyVUTranslationEntries.length > 0
  );
  const canMaterializeStrategyVUSnapshots = Boolean(
    canInitializeStrategyVUState &&
    strategyVUInputContract &&
    strategyVUMaterializationContract &&
    strategyVUStateEditor.entries.length === strategyVUTranslationEntries.length &&
    strategyVUMaterializationState !== "loading"
  );

  const invalidateStrategySnapshotMaterialization = () => {
    setStrategySnapshotMaterialization(null);
    setStrategySnapshotMaterializationState("idle");
    setStrategySnapshotMaterializationError(null);
  };

  const invalidateStrategyVUMaterialization = () => {
    setStrategyVUMaterialization(null);
    setStrategyVUMaterializationState("idle");
    setStrategyVUMaterializationError(null);
  };

  const discardStrategyVUState = () => {
    setStrategyVUStateEditor(createEmptyStrategyVUStateEditor());
    invalidateStrategyVUMaterialization();
  };

  const invalidateStrategySnapshotContextValidation = () => {
    setStrategySnapshotContextValidation(null);
    setStrategySnapshotContextValidationState("idle");
    setStrategySnapshotContextValidationError(null);
    invalidateStrategySnapshotMaterialization();
    discardStrategyVUState();
  };

  const discardStrategySnapshotContext = () => {
    setStrategySnapshotContextPeriod("");
    setStrategySnapshotContextEntries([]);
    invalidateStrategySnapshotContextValidation();
  };

  const invalidateStrategySnapshotTranslation = () => {
    setStrategySnapshotTranslation(null);
    setStrategySnapshotTranslationState("idle");
    setStrategySnapshotTranslationError(null);
    discardStrategySnapshotContext();
  };

  const invalidateStrategyDraftValidation = () => {
    setStrategyDraftValidation(null);
    setStrategyDraftValidationState("idle");
    setStrategyDraftValidationError(null);
    invalidateStrategySnapshotTranslation();
  };

  const selectStrategyDraftActor = (actorType: StrategyActorType) => {
    setStrategyDraftEditor(createEmptyStrategyDraftEditor(actorType));
    setStrategyDraftEditingIndex(null);
  };

  const selectStrategyDraftStrategy = (strategyId: string) => {
    const strategy = strategyDefinitionById.get(strategyId) ?? null;
    const schema = strategyAssignmentContract?.parameter_schemas.find(
      (candidate) => candidate.schema_id === strategy?.parameter_schema
    ) ?? null;
    setStrategyDraftEditor((current) => ({
      ...current,
      strategyId,
      parameterValues: createEmptyStrategyParameterValues(schema)
    }));
  };

  const resetStrategyDraftEditor = () => {
    setStrategyDraftEditor(createEmptyStrategyDraftEditor(strategyDraftEditor.actorType));
    setStrategyDraftEditingIndex(null);
  };

  const buildStrategyDraftAssignment = (): StrategyDraftAssignment | null => {
    if (
      !canApplyStrategyDraftAssignment ||
      strategyDraftTargetId === null ||
      strategyDraftActivationPeriod === null ||
      strategyDraftActiveThroughRun === null ||
      strategyDraftLogicalTime === null ||
      !selectedStrategyDraftDefinition
    ) {
      return null;
    }

    let parameterValues: StrategyDraftParameterValues | null = null;
    if (selectedStrategyDraftSchema) {
      parameterValues = {};
      for (const field of selectedStrategyDraftSchema.fields) {
        const values = strategyDraftEditor.parameterValues[field.field_name];
        const integerOnly = field.python_type === "list[int]";
        const first = values ? parseStrategyParameterValue(values[0], integerOnly) : null;
        const second = values ? parseStrategyParameterValue(values[1], integerOnly) : null;
        if (first === null || second === null) {
          return null;
        }
        parameterValues[field.field_name] = [first, second];
      }
    }

    return {
      actor_type: strategyDraftEditor.actorType,
      target_id: strategyDraftTargetId,
      strategy_id: selectedStrategyDraftDefinition.strategy_id,
      activation_period: strategyDraftActivationPeriod,
      active_through_run: strategyDraftActiveThroughRun,
      logical_time: strategyDraftLogicalTime,
      parameter_schema: selectedStrategyDraftSchema?.schema_id ?? null,
      parameter_values: parameterValues
    };
  };

  const applyStrategyDraftAssignment = () => {
    const assignment = buildStrategyDraftAssignment();
    if (!assignment) {
      return;
    }
    setStrategyDraftAssignments((current) => {
      if (strategyDraftEditingIndex === null) {
        return [...current, assignment];
      }
      return current.map((entry, index) => index === strategyDraftEditingIndex ? assignment : entry);
    });
    resetStrategyDraftEditor();
    invalidateStrategyDraftValidation();
  };

  const editStrategyDraftAssignment = (index: number) => {
    const assignment = strategyDraftAssignments[index];
    if (!assignment) {
      return;
    }
    setStrategyDraftEditor({
      actorType: assignment.actor_type,
      targetId: String(assignment.target_id),
      strategyId: assignment.strategy_id,
      activationPeriod: String(assignment.activation_period),
      activeThroughRun: String(assignment.active_through_run),
      logicalTime: String(assignment.logical_time),
      parameterValues: Object.fromEntries(
        Object.entries(assignment.parameter_values ?? {}).map(([fieldName, values]) => [
          fieldName,
          [String(values[0]), String(values[1])]
        ])
      ) as Record<string, [string, string]>
    });
    setStrategyDraftEditingIndex(index);
  };

  const removeStrategyDraftAssignment = (index: number) => {
    setStrategyDraftAssignments((current) => current.filter((_, candidateIndex) => candidateIndex !== index));
    if (strategyDraftEditingIndex === index) {
      resetStrategyDraftEditor();
    } else if (strategyDraftEditingIndex !== null && strategyDraftEditingIndex > index) {
      setStrategyDraftEditingIndex(strategyDraftEditingIndex - 1);
    }
    invalidateStrategyDraftValidation();
  };

  const buildStrategyDraftDocument = (): StrategyAssignmentDraftDocument | null => {
    if (!strategyDraftContract) {
      return null;
    }
    return {
      schema_version: strategyDraftContract.schema_version,
      catalog_schema_version: strategyDraftContract.catalog_schema_version,
      assignment_contract_schema_version: strategyDraftContract.assignment_contract_schema_version,
      base_model: strategyDraftContract.base_model,
      scope: strategyDraftContract.scope,
      draft_id: strategyDraftId.trim(),
      label: strategyDraftLabel.trim(),
      assignments: strategyDraftAssignments
    };
  };

  const validateStrategyDraft = async () => {
    const draft = buildStrategyDraftDocument();
    if (!draft || !canValidateStrategyDraft) {
      return;
    }
    invalidateStrategySnapshotTranslation();
    setStrategyDraftValidation(null);
    setStrategyDraftValidationState("loading");
    setStrategyDraftValidationError(null);
    try {
      const response = await fetch("/api/strategies/assignment-draft-validation", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(draft)
      });
      if (!response.ok) {
        throw new Error("Strategieentwurf konnte nicht geprueft werden");
      }
      const payload = (await response.json()) as StrategyAssignmentDraftValidationReport;
      setStrategyDraftValidation(payload);
      setStrategyDraftValidationState("ready");
    } catch (error) {
      setStrategyDraftValidation(null);
      setStrategyDraftValidationError(
        error instanceof Error ? error.message : "Strategieentwurf konnte nicht geprueft werden"
      );
      setStrategyDraftValidationState("error");
    }
  };

  const translateStrategyDraft = async () => {
    const draft = buildStrategyDraftDocument();
    const endpoint = strategySnapshotTranslationContract?.translation_endpoint;
    if (!draft || !endpoint || !canTranslateStrategyDraft) {
      return;
    }
    discardStrategySnapshotContext();
    setStrategySnapshotTranslation(null);
    setStrategySnapshotTranslationState("loading");
    setStrategySnapshotTranslationError(null);
    try {
      const response = await fetch(
        endpoint,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(draft)
        }
      );
      if (!response.ok) {
        throw new Error("Snapshot-Bauplaene konnten nicht erstellt werden");
      }
      const payload = (await response.json()) as StrategySnapshotTranslationReport;
      setStrategySnapshotTranslation(payload);
      setStrategySnapshotTranslationState("ready");
    } catch (error) {
      setStrategySnapshotTranslation(null);
      setStrategySnapshotTranslationError(
        error instanceof Error ? error.message : "Snapshot-Bauplaene konnten nicht erstellt werden"
      );
      setStrategySnapshotTranslationState("error");
    }
  };

  const initializeStrategySnapshotContext = () => {
    if (!canInitializeStrategySnapshotContext || !strategySnapshotTranslation) {
      return;
    }
    setStrategySnapshotContextPeriod("");
    setStrategySnapshotContextEntries(
      strategySnapshotTranslation.entries.map((entry) => ({
        actor_type: entry.actor_type,
        target_id: entry.target_id,
        strategy_id: entry.strategy_id,
        values: Object.fromEntries(
          entry.unresolved_snapshot_fields.map((fieldName) => [
            fieldName,
            { raw: "", explicitlyOpen: false }
          ])
        ) as Record<string, StrategySnapshotContextEditorValue>
      }))
    );
    invalidateStrategySnapshotContextValidation();
  };

  const updateStrategySnapshotContextValue = (
    entryIndex: number,
    fieldName: string,
    update: Partial<StrategySnapshotContextEditorValue>
  ) => {
    setStrategySnapshotContextEntries((current) => current.map((entry, index) => {
      if (index !== entryIndex) {
        return entry;
      }
      const previous = entry.values[fieldName] ?? { raw: "", explicitlyOpen: false };
      return {
        ...entry,
        values: {
          ...entry.values,
          [fieldName]: { ...previous, ...update }
        }
      };
    }));
    invalidateStrategySnapshotContextValidation();
  };

  const buildStrategySnapshotContextDocument = (): StrategySnapshotContextDocument | null => {
    if (
      !strategySnapshotContextContract ||
      !strategySnapshotContextPeriodValue ||
      strategySnapshotContextEntries.length === 0
    ) {
      return null;
    }
    return {
      schema_version: strategySnapshotContextContract.schema_version,
      translation_schema_version: strategySnapshotContextContract.translation_schema_version,
      base_model: strategySnapshotContextContract.base_model,
      scope: strategySnapshotContextContract.scope,
      draft_id: strategyDraftId.trim(),
      period: strategySnapshotContextPeriodValue,
      entries: strategySnapshotContextEntries.map((entry) => {
        const values: Record<string, unknown> = {};
        for (const [fieldName, editorValue] of Object.entries(entry.values)) {
          const definition = strategySnapshotContextFieldByName.get(fieldName);
          if (!definition) {
            continue;
          }
          const parsed = parseStrategySnapshotContextEditorValue(editorValue, definition);
          if (parsed !== undefined) {
            values[fieldName] = parsed;
          }
        }
        return {
          actor_type: entry.actor_type,
          target_id: entry.target_id,
          strategy_id: entry.strategy_id,
          values
        };
      })
    };
  };

  const validateStrategySnapshotContext = async () => {
    const draft = buildStrategyDraftDocument();
    const context = buildStrategySnapshotContextDocument();
    const endpoint = strategySnapshotContextContract?.validation_endpoint;
    if (!draft || !context || !endpoint || !canValidateStrategySnapshotContext) {
      return;
    }
    invalidateStrategySnapshotMaterialization();
    invalidateStrategyVUMaterialization();
    setStrategySnapshotContextValidation(null);
    setStrategySnapshotContextValidationState("loading");
    setStrategySnapshotContextValidationError(null);
    try {
      const response = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ draft, context })
      });
      if (!response.ok) {
        throw new Error("Snapshot-Kontext konnte nicht geprueft werden");
      }
      const payload = (await response.json()) as StrategySnapshotContextValidationReport;
      setStrategySnapshotContextValidation(payload);
      setStrategySnapshotContextValidationState("ready");
    } catch (error) {
      setStrategySnapshotContextValidation(null);
      setStrategySnapshotContextValidationError(
        error instanceof Error ? error.message : "Snapshot-Kontext konnte nicht geprueft werden"
      );
      setStrategySnapshotContextValidationState("error");
    }
  };

  const materializeStrategySnapshots = async () => {
    const draft = buildStrategyDraftDocument();
    const context = buildStrategySnapshotContextDocument();
    const endpoint = strategySnapshotMaterializationContract?.operation.materialization_endpoint;
    if (!draft || !context || !endpoint || !canMaterializeStrategySnapshots) {
      return;
    }
    setStrategySnapshotMaterialization(null);
    setStrategySnapshotMaterializationState("loading");
    setStrategySnapshotMaterializationError(null);
    try {
      const response = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ draft, context })
      });
      if (!response.ok) {
        throw new Error("VN-Snapshots konnten nicht erzeugt werden");
      }
      const payload = (await response.json()) as StrategySnapshotMaterializationReport;
      setStrategySnapshotMaterialization(payload);
      setStrategySnapshotMaterializationState("ready");
      if (payload.materialization_complete) {
        setStrategyWorkbenchView("snapshots");
      }
    } catch (error) {
      setStrategySnapshotMaterialization(null);
      setStrategySnapshotMaterializationError(
        error instanceof Error ? error.message : "VN-Snapshots konnten nicht erzeugt werden"
      );
      setStrategySnapshotMaterializationState("error");
    }
  };

  const initializeStrategyVUState = () => {
    if (!canInitializeStrategyVUState || !strategyVUStateContract) {
      return;
    }
    setStrategyVUStateEditor({
      interestRate: "",
      changeShock: "",
      activePolicyholderCount: "",
      entries: strategyVUTranslationEntries.map((entry) => ({
        insurer_id: entry.target_id,
        strategy_id: entry.strategy_id,
        values: Object.fromEntries(
          (strategyVUStateContract.state_value_fields_by_strategy[entry.strategy_id] ?? []).map(
            (fieldName) => [fieldName, ""]
          )
        )
      }))
    });
    invalidateStrategyVUMaterialization();
  };

  const updateStrategyVUPeriodState = (
    fieldName: "interestRate" | "changeShock" | "activePolicyholderCount",
    value: string
  ) => {
    setStrategyVUStateEditor((current) => ({ ...current, [fieldName]: value }));
    invalidateStrategyVUMaterialization();
  };

  const updateStrategyVUEntryState = (
    entryIndex: number,
    fieldName: string,
    value: string
  ) => {
    setStrategyVUStateEditor((current) => ({
      ...current,
      entries: current.entries.map((entry, index) => index === entryIndex
        ? { ...entry, values: { ...entry.values, [fieldName]: value } }
        : entry)
    }));
    invalidateStrategyVUMaterialization();
  };

  const buildStrategyVUMaterializationRequest = (): object | null => {
    const draft = buildStrategyDraftDocument();
    const context = buildStrategySnapshotContextDocument();
    if (
      !draft ||
      !context ||
      !strategyVUInputContract ||
      !strategyVUStateContract ||
      strategyVUStateEditor.entries.length === 0
    ) {
      return null;
    }
    return {
      input: {
        schema_version: strategyVUInputContract.input_schema_version,
        threshold_source_policy: strategyVUInputContract.threshold_source_policy.policy_id,
        draw_source_policy: strategyVUInputContract.draw_source_policy.policy_id,
        fallback_policy: strategyVUInputContract.fallback_policy.policy_id,
        draft,
        context
      },
      state: {
        schema_version: strategyVUStateContract.state_schema_version,
        input_schema_version: strategyVUStateContract.materialization_input_schema_version,
        base_model: strategyVUStateContract.base_model,
        scope: strategyVUStateContract.scope,
        draft_id: draft.draft_id,
        period: context.period,
        period_state: {
          interest_rate: parseStrategyVUStateValue(
            strategyVUStateEditor.interestRate,
            "number"
          ),
          change_shock: strategyVUStateEditor.changeShock === "true"
            ? true
            : strategyVUStateEditor.changeShock === "false"
              ? false
              : null,
          active_policyholder_count: parseStrategyVUStateValue(
            strategyVUStateEditor.activePolicyholderCount,
            "integer"
          )
        },
        entries: strategyVUStateEditor.entries.map((entry) => ({
          insurer_id: entry.insurer_id,
          strategy_id: entry.strategy_id,
          values: Object.fromEntries(
            Object.entries(entry.values).map(([fieldName, value]) => [
              fieldName,
              parseStrategyVUStateValue(value, "array")
            ])
          )
        }))
      }
    };
  };

  const materializeStrategyVUSnapshots = async () => {
    const request = buildStrategyVUMaterializationRequest();
    const endpoint = strategyVUMaterializationContract?.operation.materialization_endpoint;
    if (!request || !endpoint || !canMaterializeStrategyVUSnapshots) {
      return;
    }
    setStrategyVUMaterialization(null);
    setStrategyVUMaterializationState("loading");
    setStrategyVUMaterializationError(null);
    try {
      const response = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(request)
      });
      if (!response.ok) {
        throw new Error("VU-Snapshots konnten nicht erzeugt werden");
      }
      const payload = (await response.json()) as StrategyVUSnapshotMaterializationReport;
      setStrategyVUMaterialization(payload);
      setStrategyVUMaterializationState("ready");
      if (payload.materialization_complete) {
        setStrategyWorkbenchView("vu-snapshots");
      }
    } catch (error) {
      setStrategyVUMaterialization(null);
      setStrategyVUMaterializationError(
        error instanceof Error ? error.message : "VU-Snapshots konnten nicht erzeugt werden"
      );
      setStrategyVUMaterializationState("error");
    }
  };
  const detailStatusLabel = detailState === "error" ? "nicht gefunden" : detailState === "loading" ? "laedt" : "lesend";
  const scenarioNameById = new Map(scenarios.map((scenario) => [scenario.id, scenario.display_name]));
  const scenarioStatusOptions = uniqueSorted(scenarios.map((scenario) => scenario.status));
  const scenarioSourceOptions = uniqueSorted(scenarios.map((scenario) => scenario.source.label));
  const scenarioScopeOptions = uniqueSorted(scenarios.map((scenario) => scenario.domain_scope));
  const runStatusOptions = uniqueSorted(runs.map((run) => run.status));
  const runScenarioOptions = uniqueSorted(runs.map((run) => run.scenario_id));
  const runSourceOptions = uniqueSorted(runs.map((run) => run.source.label));
  const queueEntries = runControlQueue?.entries ?? [];
  const queueStatusOptions = uniqueSorted(queueEntries.map((entry) => entry.status));
  const queueScenarioOptions = uniqueSorted(queueEntries.map((entry) => entry.request.scenario_id));
  const filteredScenarios = filterScenarios(scenarios, {
    query: scenarioQuery,
    status: scenarioStatusFilter,
    source: scenarioSourceFilter,
    scope: scenarioScopeFilter
  });
  const filteredRuns = filterRuns(runs, {
    query: runQuery,
    status: runStatusFilter,
    scenario: runScenarioFilter,
    source: runSourceFilter
  });
  const filteredQueueEntries = filterRunControlQueueEntries(queueEntries, {
    query: queueQuery,
    status: queueStatusFilter,
    scenario: queueScenarioFilter
  });
  const selectedScenario =
    scenarioDetail?.id === selectedScenarioId
      ? scenarioDetail
      : scenarios.find((scenario) => scenario.id === selectedScenarioId) ?? null;
  const selectedRun =
    runDetail?.id === selectedRunId
      ? runDetail
      : runs.find((run) => run.id === selectedRunId) ?? null;
  const selectedScenarioHidden =
    selectedScenarioId !== null && !filteredScenarios.some((scenario) => scenario.id === selectedScenarioId);
  const selectedRunHidden = selectedRunId !== null && !filteredRuns.some((run) => run.id === selectedRunId);
  const filterNotice = selectedScenarioHidden || selectedRunHidden
    ? "Auswahl durch Filter aktuell nicht in den Listen sichtbar"
    : "Auswahl in den Listen sichtbar";
  const selectionRows = [
    ["Szenario", selectedScenario?.display_name ?? "wird geladen"],
    ["Run", selectedRun?.display_name ?? "wird geladen"],
    ["Periodenfenster", selectedRun?.period_window ?? "-"],
    ["Metadatenquelle", storageLabel],
    ["Schreibpfade", capabilities?.writes.scenario_metadata.enabled || capabilities?.writes.run_metadata.enabled ? "aktiv" : "gesperrt"],
    ["Ausfuehrung", capabilities?.simulation_execution.enabled || selectedRun?.execution_enabled ? "aktiv" : "gesperrt"],
    ["Filterzustand", filterNotice]
  ];
  const selectRun = (run: RunMetadata) => {
    setSelectedRunId(run.id);
    setSelectedScenarioId(run.scenario_id);
    setRunControlDryRunResult(null);
    setRunControlDryRunError(null);
    setRunControlDryRunState("idle");
    setRunControlQueueEnqueueResult(null);
    setRunControlQueueEnqueueError(null);
    setRunControlQueueEnqueueState("idle");
  };
  const selectedRunControlRequest = selectedRun
    ? {
        run_id: selectedRun.id,
        scenario_id: selectedRun.scenario_id,
        metadata_db: metadataSource?.path ?? null,
        requested_by: "workbench-ui",
        created_at: "2026-05-27T00:00:00Z",
        execution_enabled: false
      }
    : null;
  const checkRunControlDryRun = async () => {
    if (!selectedRunControlRequest) {
      return;
    }
    setRunControlDryRunState("loading");
    setRunControlDryRunError(null);
    setRunControlQueueEnqueueResult(null);
    setRunControlQueueEnqueueError(null);
    setRunControlQueueEnqueueState("idle");
    try {
      const response = await fetch("/api/run-control/dry-run", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify(selectedRunControlRequest)
      });
      const payload = (await response.json()) as RunControlDryRunResult | { message?: string };
      if (!response.ok) {
        throw new Error("message" in payload && payload.message ? payload.message : "Run-Control-Dry-Run nicht erreichbar");
      }
      setRunControlDryRunResult(payload as RunControlDryRunResult);
      setRunControlDryRunState("ready");
    } catch (error) {
      setRunControlDryRunResult(null);
      setRunControlDryRunError(error instanceof Error ? error.message : "Run-Control-Dry-Run nicht erreichbar");
      setRunControlDryRunState("error");
    }
  };
  const canEnqueueRunControlQueue =
    Boolean(selectedRunControlRequest) &&
    metadataSource?.storage_kind === "sqlite" &&
    Boolean(metadataSource.path) &&
    runControlDryRunResult?.status === "ok" &&
    runControlDryRunResult.request.run_id === selectedRun?.id &&
    runControlDryRunResult.request.scenario_id === selectedRun?.scenario_id;
  const enqueueRunControlQueue = async () => {
    if (!selectedRunControlRequest || !canEnqueueRunControlQueue) {
      return;
    }
    setRunControlQueueEnqueueState("loading");
    setRunControlQueueEnqueueError(null);
    try {
      const response = await fetch("/api/run-control/queue", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify(selectedRunControlRequest)
      });
      const payload = (await response.json()) as RunControlQueueEnqueueResult | { message?: string };
      if (!response.ok) {
        throw new Error("message" in payload && payload.message ? payload.message : "Queue-Vormerkung nicht erreichbar");
      }
      const enqueuePayload = payload as RunControlQueueEnqueueResult;
      setRunControlQueueEnqueueResult(enqueuePayload);
      setRunControlQueueEnqueueState("ready");
      setSelectedQueueId(enqueuePayload.entry.queue_id);
      const overviewResponse = await fetch("/api/run-control/queue");
      if (overviewResponse.ok) {
        setRunControlQueue((await overviewResponse.json()) as RunControlQueueOverview);
      }
      const actionPlanResponse = await fetch("/api/run-control/queue/action-plan");
      if (actionPlanResponse.ok) {
        setRunControlActionPlan((await actionPlanResponse.json()) as RunControlQueueActionPlan);
        setRunControlActionPlanState("ready");
      }
      const coreBridgeResponse = await fetch("/api/run-control/core-diagnostics-bridge");
      if (coreBridgeResponse.ok) {
        setRunControlCoreBridge((await coreBridgeResponse.json()) as RunControlCoreDiagnosticsBridge);
      }
    } catch (error) {
      setRunControlQueueEnqueueResult(null);
      setRunControlQueueEnqueueError(error instanceof Error ? error.message : "Queue-Vormerkung nicht erreichbar");
      setRunControlQueueEnqueueState("error");
    }
  };
  const missingScenarioLabel = metadataConsistency?.runs_with_missing_scenario.length
    ? metadataConsistency.runs_with_missing_scenario.join(", ")
    : "keine";
  const executionEnabledLabel = metadataConsistency?.runs_with_execution_enabled.length
    ? metadataConsistency.runs_with_execution_enabled.join(", ")
    : "keine";
  const consistencyRows = [
    ["Szenarien", String(metadataConsistency?.scenario_count ?? scenarios.length)],
    ["Runs", String(metadataConsistency?.run_count ?? runs.length)],
    ["Run-Bezuege", `${metadataConsistency?.runs_with_known_scenario ?? 0} bekannt`],
    ["Fehlende Bezuege", missingScenarioLabel],
    ["Aktive Ausfuehrung", executionEnabledLabel],
    ["Schreibpfade", metadataConsistency?.writes_enabled ? "aktiv" : "gesperrt"],
    ["Simulation", metadataConsistency?.simulation_enabled ? "aktiv" : "gesperrt"],
    ["Status", metadataConsistency?.status === "warning" ? "Warnung" : "ok"]
  ];
  const coreValidationRows = [
    ["Status", coreValidation?.status ?? "laedt"],
    ["Periodenplaene", String(coreValidation?.plan_count ?? 0)],
    ["Globale Perioden", coreValidation?.global_periods.join(", ") ?? "-"],
    ["Legacy-Referenzen", String(coreValidation?.legacy_reference_count ?? 0)],
    ["Abgedeckte Zeilen", String(coreValidation?.legacy_covered_rows ?? 0)],
    ["Naechste Validierung", coreValidation?.next_validation_actions.join(", ") ?? "-"],
    ["Summary vorhanden", coreValidation?.execution_summary_available ? "ja" : "nein"],
    ["Summary naechster Schritt", coreValidation?.execution_summary_next_action ?? "-"],
    ["Summary-Felder", String(coreValidation?.execution_summary_contract.required_fields.length ?? 0)],
    [
      "Overview startet Runner",
      coreValidation?.execution_summary_contract.overview_starts_runner ? "ja" : "nein"
    ],
    [
      "Schreibpfade",
      coreValidation?.writes_performed || coreValidation?.execution_summary_contract.writes_performed
        ? "aktiv"
        : "gesperrt"
    ],
    [
      "Ausfuehrung",
      coreValidation?.execution_performed || coreValidation?.execution_summary_contract.execution_performed
        ? "aktiv"
        : "gesperrt"
    ]
  ];
  const coreValidationContractRows = [
    ["Modus", coreValidation?.execution_summary_contract.mode ?? "laedt"],
    ["Summary-Modus", coreValidation?.execution_summary_contract.summary_mode ?? "-"],
    ["Periodenachsen", coreValidation?.execution_summary_contract.period_axis_fields.join(", ") ?? "-"],
    ["Anwendungszaehlungen", coreValidation?.execution_summary_contract.application_count_fields.join(", ") ?? "-"],
    ["Carryover", coreValidation?.execution_summary_contract.carryover_fields.join(", ") ?? "-"],
    ["Legacy", coreValidation?.execution_summary_contract.legacy_fields.join(", ") ?? "-"],
    ["Grenzfelder", coreValidation?.execution_summary_contract.boundary_fields.join(", ") ?? "-"],
    ["Naechste Aktion", coreValidation?.execution_summary_contract.next_action ?? "-"]
  ];
  const carryoverProbeRows = [
    ["Status", carryoverProbeContract?.status ?? "laedt"],
    ["Modus", carryoverProbeContract?.mode ?? "laedt"],
    ["Probe-Modus", carryoverProbeContract?.expected_probe_mode ?? "-"],
    ["Endpunkt", carryoverProbeContract?.endpoint ?? "-"],
    ["Vorberechnete Probe", carryoverProbeContract?.precomputed_probe_required ? "erforderlich" : "offen"],
    ["Erwartete Eingaben", carryoverProbeContract?.expected_inputs.join(", ") ?? "-"],
    ["Voraussetzungen", carryoverProbeContract?.required_preconditions.join(", ") ?? "-"]
  ];
  const carryoverProbeBoundaryRows = [
    ["API nimmt Payload an", carryoverProbeContract?.api_accepts_probe_payload ? "ja" : "nein"],
    ["API startet Probe", carryoverProbeContract?.api_starts_probe ? "ja" : "nein"],
    ["UI aktiv", carryoverProbeContract?.ui_enabled ? "ja" : "nein"],
    ["Schreibpfade", carryoverProbeContract?.writes_performed ? "aktiv" : "gesperrt"],
    ["Ausfuehrung", carryoverProbeContract?.execution_performed ? "aktiv" : "gesperrt"],
    ["Simulation", carryoverProbeContract?.simulation_performed ? "aktiv" : "gesperrt"],
    [
      "Historische Regelwahl",
      carryoverProbeContract?.automatic_historical_rule_selection_performed ? "aktiv" : "gesperrt"
    ],
    ["Grenzfelder", carryoverProbeContract?.boundary_fields.join(", ") ?? "-"],
    ["Verbotene Grenzen", carryoverProbeContract?.forbidden_boundaries.join(", ") ?? "-"]
  ];
  const runControlQueueRows = [
    ["Queue-Status", runControlQueue?.status === "warning" ? "Hinweis" : "ok"],
    ["Queue-Eintraege", String(runControlQueue?.queue_count ?? 0)],
    ["Sichtbar", String(filteredQueueEntries.length)],
    ["Hinweise", String(runControlQueue?.issues.length ?? 0)],
    ["Schreibpfade", runControlQueue?.writes_enabled ? "aktiv" : "gesperrt"],
    ["Ausfuehrung", runControlQueue?.execution_enabled || runControlQueue?.execution_performed ? "aktiv" : "gesperrt"]
  ];
  const runControlQueueIssue = runControlQueue?.issues[0]?.message ?? "Queue liest vorhandene lokale Eintraege ohne Ausfuehrung.";
  const runControlIssueRows = runControlQueue?.issues.length
    ? runControlQueue.issues.map((issue) => [issue.severity, issue.code, issue.message])
    : [["info", "run_control_queue_readonly", "Keine Queue-Hinweise fuer die aktuelle Sicht."]];
  const selectedQueueEntry =
    queueDetail?.entry.queue_id === selectedQueueId
      ? queueDetail.entry
      : runControlQueue?.entries.find((entry) => entry.queue_id === selectedQueueId) ?? null;
  const invalidateExecutionRelease = () => {
    setExecutionReleaseRequest(null);
    setExecutionReleaseResult(null);
    setExecutionReleaseState("idle");
    setExecutionReleaseError(null);
    setAdapterStartResult(null);
    setAdapterStartState("idle");
    setAdapterStartError(null);
  };
  const refreshRunControlExecutionState = async (queueId: string) => {
    const [
      overviewResponse,
      detailResponse,
      actionPlanResponse,
      coreBridgeResponse,
      resultResponse,
      historyResponse
    ] =
      await Promise.all([
        fetch("/api/run-control/queue"),
        fetch(`/api/run-control/queue/${encodeURIComponent(queueId)}`),
        fetch("/api/run-control/queue/action-plan"),
        fetch("/api/run-control/core-diagnostics-bridge"),
        fetch(`/api/run-control/execution-result/${encodeURIComponent(queueId)}`),
        fetch(`/api/run-control/execution-history/${encodeURIComponent(queueId)}`)
      ]);
    if (overviewResponse.ok) {
      setRunControlQueue((await overviewResponse.json()) as RunControlQueueOverview);
    }
    if (detailResponse.ok) {
      setQueueDetail((await detailResponse.json()) as RunControlQueueDetail);
      setQueueDetailState("ready");
      setQueueDetailError(null);
    }
    if (actionPlanResponse.ok) {
      setRunControlActionPlan((await actionPlanResponse.json()) as RunControlQueueActionPlan);
      setRunControlActionPlanState("ready");
    }
    if (coreBridgeResponse.ok) {
      setRunControlCoreBridge((await coreBridgeResponse.json()) as RunControlCoreDiagnosticsBridge);
    }
    if (resultResponse.ok) {
      setRunControlExecutionResult((await resultResponse.json()) as RunControlExecutionResult);
      setRunControlExecutionResultState("ready");
      setRunControlExecutionResultError(null);
    } else if (resultResponse.status === 404) {
      setRunControlExecutionResult(null);
      setRunControlExecutionResultState("ready");
      setRunControlExecutionResultError("kein persistiertes Ergebnis");
    }
    if (historyResponse.ok) {
      setRunControlExecutionHistory((await historyResponse.json()) as RunControlExecutionHistory);
      setRunControlExecutionHistoryState("ready");
      setRunControlExecutionHistoryError(null);
    } else {
      const payload = (await historyResponse.json()) as RunControlExecutionHistory;
      setRunControlExecutionHistory(null);
      setRunControlExecutionHistoryState("error");
      setRunControlExecutionHistoryError(payload.message ?? "Run-Control-Verlauf nicht erreichbar");
    }
  };
  const canCheckExecutionRelease =
    selectedQueueEntry?.status === "validated" &&
    executionReleaseConfirmed &&
    Boolean(executionReleaseActor.trim()) &&
    Boolean(executionReleaseReason.trim()) &&
    runControlAdapterStartContract?.api_accepts_start_payload === true &&
    runControlAdapterStartContract.api_validates_start_payload === true &&
    runControlAdapterStartContract.ui_start_enabled === true;
  const checkExecutionRelease = async () => {
    if (!selectedQueueEntry || !runControlAdapterStartContract || !canCheckExecutionRelease) {
      return;
    }
    const request: RunControlExecutionReleaseRequest = {
      schema_version: runControlAdapterStartContract.schema_version,
      queue_id: selectedQueueEntry.queue_id,
      run_id: selectedQueueEntry.request.run_id,
      scenario_id: selectedQueueEntry.request.scenario_id,
      release_profile_id: "vu14-calculated-diagnostic",
      idempotency_key: createUiIdempotencyKey(selectedQueueEntry.queue_id),
      expected_adapter_mode: runControlAdapterStartContract.expected_adapter_mode,
      explicit_execution_release: true,
      released_by: executionReleaseActor.trim(),
      released_at: new Date().toISOString(),
      release_reason: executionReleaseReason.trim(),
      carry_forward_vu_state: false,
      carry_forward_vn_state: false
    };
    setExecutionReleaseRequest(request);
    setExecutionReleaseResult(null);
    setExecutionReleaseState("loading");
    setExecutionReleaseError(null);
    setAdapterStartResult(null);
    setAdapterStartState("idle");
    setAdapterStartError(null);
    try {
      const response = await fetch("/api/run-control/adapter-release-check", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(request)
      });
      const payload = (await response.json()) as RunControlExecutionReleaseResult;
      if (!response.ok && response.status !== 409) {
        throw new Error(payload.message ?? "Ausfuehrungsfreigabe nicht erreichbar");
      }
      setExecutionReleaseResult(payload);
      setExecutionReleaseState("ready");
      setExecutionReleaseError(payload.release_ready ? null : payload.issues.join(", ") || "Freigabe blockiert");
    } catch (error) {
      setExecutionReleaseResult(null);
      setExecutionReleaseError(error instanceof Error ? error.message : "Ausfuehrungsfreigabe nicht erreichbar");
      setExecutionReleaseState("error");
    }
  };
  const canStartAdapter =
    executionReleaseRequest?.queue_id === selectedQueueEntry?.queue_id &&
    executionReleaseResult?.release_ready === true &&
    selectedQueueEntry?.status === "validated" &&
    adapterStartState !== "loading";
  const startReleasedAdapter = async () => {
    if (!executionReleaseRequest || !selectedQueueEntry || !canStartAdapter) {
      return;
    }
    setAdapterStartResult(null);
    setAdapterStartState("loading");
    setAdapterStartError(null);
    try {
      const response = await fetch("/api/run-control/adapter-start", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(executionReleaseRequest)
      });
      const payload = (await response.json()) as RunControlAdapterStartResponse;
      setAdapterStartResult(payload);
      if (!response.ok) {
        setAdapterStartError(payload.message ?? "Adapterstart fehlgeschlagen");
        setAdapterStartState("error");
      } else {
        setAdapterStartState("ready");
      }
      await refreshRunControlExecutionState(selectedQueueEntry.queue_id);
    } catch (error) {
      setAdapterStartResult(null);
      setAdapterStartError(error instanceof Error ? error.message : "Adapterstart nicht erreichbar");
      setAdapterStartState("error");
      await refreshRunControlExecutionState(selectedQueueEntry.queue_id);
    }
  };
  const queueDetailRows = [
    ["Queue-ID", selectedQueueEntry?.queue_id ?? "kein Eintrag"],
    ["Run", selectedQueueEntry?.request.run_id ?? "-"],
    ["Szenario", selectedQueueEntry?.request.scenario_id ?? "-"],
    ["Status", selectedQueueEntry?.status ?? "-"],
    ["Naechster Schritt", selectedQueueEntry ? queueActionLabel(selectedQueueEntry) : "-"],
    ["Angelegt von", selectedQueueEntry?.request.requested_by ?? "-"],
    ["Zeitpunkt", selectedQueueEntry?.request.created_at ?? "-"],
    ["Metadaten-DB", selectedQueueEntry?.request.metadata_db ?? "-"],
    ["Schreibpfade", queueDetail?.writes_enabled ? "aktiv" : "gesperrt"],
    ["Ausfuehrung", selectedQueueEntry?.execution_enabled || selectedQueueEntry?.execution_performed ? "aktiv" : "gesperrt"]
  ];
  const queueDetailStatus =
    queueDetailState === "error" ? queueDetailError ?? "nicht gefunden" : queueDetailState === "loading" ? "laedt" : "lesend";
  const runControlPreflightStatus =
    runControlPreflightState === "error"
      ? runControlPreflightError ?? "nicht erreichbar"
      : runControlPreflightState === "loading"
        ? "laedt"
        : runControlPreflight
          ? "lesend"
          : "laedt";
  const runControlPreflightBoundaryStatus =
    runControlPreflightState === "error"
      ? runControlPreflightError ?? "nicht erreichbar"
      : runControlPreflightState === "loading"
        ? "laedt"
        : runControlPreflight?.status === "error"
          ? "Fehler"
          : runControlPreflight?.issues.length
            ? "Hinweis"
            : runControlPreflight
              ? "ok"
              : "laedt";
  const runControlPreflightIssueLabel = runControlPreflight
    ? runControlPreflight.issues.length
      ? runControlPreflight.issues.join(", ")
      : "keine"
    : runControlPreflightState === "error"
      ? runControlPreflightError ?? "nicht erreichbar"
      : "laedt";
  const runControlPreflightRows = [
    ["Status", runControlPreflight?.status ?? "laedt"],
    ["Run", runControlPreflight?.run_id ?? selectedRunId ?? "-"],
    ["Szenario", runControlPreflight?.scenario_id ?? "-"],
    ["Run gefunden", yesNoLoading(runControlPreflight?.run_found)],
    ["Szenario gefunden", yesNoLoading(runControlPreflight?.scenario_found)],
    ["Hinweise", runControlPreflightIssueLabel],
    ["Schreibpfade", runControlPreflight?.writes_performed ? "aktiv" : "gesperrt"],
    ["Ausfuehrung", runControlPreflight?.execution_allowed || runControlPreflight?.execution_performed ? "aktiv" : "gesperrt"]
  ];
  const runControlRequestRows = [
    ["Modus", runControlRequestContract?.mode ?? "laedt"],
    ["Pflichtfelder", runControlRequestContract?.required_fields.join(", ") ?? "-"],
    ["Optionale Felder", runControlRequestContract?.optional_fields.join(", ") ?? "-"],
    ["Verbotene Felder", runControlRequestContract?.forbidden_fields.join(", ") ?? "-"],
    ["Beispiel run_id", runControlRequestContract?.example_request.run_id ?? "-"],
    ["Beispiel scenario_id", runControlRequestContract?.example_request.scenario_id ?? "-"],
    ["Beispiel metadata_db", runControlRequestContract?.example_request.metadata_db ?? "-"],
    ["Beispiel requested_by", runControlRequestContract?.example_request.requested_by ?? "-"],
    ["Beispiel created_at", runControlRequestContract?.example_request.created_at ?? "-"],
    [
      "Beispiel execution_enabled",
      runControlRequestContract ? String(runControlRequestContract.example_request.execution_enabled) : "-"
    ],
    ["Schreibpfade", runControlRequestContract?.writes_enabled ? "aktiv" : "gesperrt"],
    ["Ausfuehrung", runControlRequestContract?.execution_enabled || runControlRequestContract?.execution_performed ? "aktiv" : "gesperrt"]
  ];
  const runControlDryRunRows = [
    ["Modus", runControlDryRunContract?.mode ?? "laedt"],
    [
      "Status",
      runControlDryRunContract
        ? runControlDryRunContract.http_enabled
          ? "HTTP-Pruefung aktiv"
          : "gesperrt"
        : "laedt"
    ],
    ["Eingaben", runControlDryRunContract?.expected_inputs.join(", ") ?? "-"],
    ["Vorbedingungen", runControlDryRunContract?.required_preconditions.join(", ") ?? "-"],
    ["Gesperrte Grenzen", runControlDryRunContract?.forbidden_boundaries.join(", ") ?? "-"],
    ["HTTP", runControlDryRunContract?.http_enabled ? "aktiv" : "gesperrt"],
    ["Schreibpfade", runControlDryRunContract?.writes_enabled || runControlDryRunContract?.writes_performed ? "aktiv" : "gesperrt"],
    ["Ausfuehrung", runControlDryRunContract?.execution_enabled || runControlDryRunContract?.execution_performed ? "aktiv" : "gesperrt"]
  ];
  const adapterResultContractRows = [
    ["Modus", runControlAdapterResultContract?.mode ?? "laedt"],
    ["Endpunkt", runControlAdapterResultContract?.endpoint ?? "/api/run-control/adapter-result-contract"],
    ["Resultat", runControlAdapterResultContract?.expected_result_mode ?? "-"],
    ["Validation", runControlAdapterResultContract?.expected_validation_mode ?? "-"],
    ["Eingaben", runControlAdapterResultContract?.expected_inputs.join(", ") ?? "-"],
    ["Vorbedingungen", runControlAdapterResultContract?.required_preconditions.join(", ") ?? "-"],
    ["Verbotene Felder", runControlAdapterResultContract?.forbidden_fields.join(", ") ?? "-"],
    ["Gesperrte Grenzen", runControlAdapterResultContract?.forbidden_boundaries.join(", ") ?? "-"],
    [
      "Payload",
      runControlAdapterResultContract?.api_accepts_result_payload ||
      runControlAdapterResultContract?.api_validates_result_payload
        ? "aktiv"
        : "gesperrt"
    ],
    ["Adapterstart", runControlAdapterResultContract?.api_starts_adapter ? "aktiv" : "gesperrt"],
    ["UI", runControlAdapterResultContract?.ui_enabled ? "aktiv" : "gesperrt"],
    [
      "Ausfuehrung",
      runControlAdapterResultContract?.execution_performed || runControlAdapterResultContract?.simulation_performed
        ? "aktiv"
        : "gesperrt"
    ]
  ];
  const runControlDryRunStatus =
    runControlDryRunState === "error"
      ? runControlDryRunError ?? "nicht erreichbar"
      : runControlDryRunState === "loading"
        ? "prueft"
        : runControlDryRunResult
          ? runControlDryRunResult.status === "ok"
            ? "geprueft"
            : "Hinweis"
          : "nicht geprueft";
  const runControlDryRunIssueLabel = runControlDryRunResult
    ? runControlDryRunResult.issues.length
      ? runControlDryRunResult.issues.join(", ")
      : "keine"
    : runControlDryRunState === "error"
      ? runControlDryRunError ?? "nicht erreichbar"
      : "nicht geprueft";
  const runControlDryRunResultRows = [
    ["Status", runControlDryRunStatus],
    ["Run", runControlDryRunResult?.request.run_id ?? selectedRunId ?? "-"],
    ["Szenario", runControlDryRunResult?.request.scenario_id ?? selectedRun?.scenario_id ?? "-"],
    ["Request akzeptiert", yesNoLoading(runControlDryRunResult?.request_accepted)],
    ["Preflight ok", yesNoLoading(runControlDryRunResult?.preflight_passed)],
    ["Szenario passt", yesNoLoading(runControlDryRunResult?.scenario_matches_request)],
    ["Dry-Run erlaubt", runControlDryRunResult?.dry_run_allowed ? "ja" : "nein"],
    ["Hinweise", runControlDryRunIssueLabel],
    ["Schreibpfade", runControlDryRunResult?.writes_enabled || runControlDryRunResult?.writes_performed ? "aktiv" : "gesperrt"],
    ["Ausfuehrung", runControlDryRunResult?.execution_enabled || runControlDryRunResult?.execution_performed ? "aktiv" : "gesperrt"]
  ];
  const runControlQueueEnqueueStatus =
    runControlQueueEnqueueState === "error"
      ? runControlQueueEnqueueError ?? "nicht erreichbar"
      : runControlQueueEnqueueState === "loading"
        ? "merkt vor"
        : runControlQueueEnqueueResult
          ? "vorgemerkt"
          : metadataSource?.storage_kind === "sqlite"
            ? "bereit nach Dry-Run"
            : "SQLite-Quelle fehlt";
  const runControlQueueEnqueueRows = [
    ["Status", runControlQueueEnqueueStatus],
    ["Queue-ID", runControlQueueEnqueueResult?.entry.queue_id ?? selectedRunId ?? "-"],
    ["Statuswert", runControlQueueEnqueueResult?.entry.status ?? "planned"],
    ["Quelle", metadataSource?.storage_kind === "sqlite" ? "SQLite" : "nicht konfiguriert"],
    ["Dry-Run vorher", canEnqueueRunControlQueue || runControlQueueEnqueueResult ? "ok" : "erforderlich"],
    ["Schreibpfad", runControlQueueEnqueueResult?.writes_performed ? "Queue geschrieben" : "nicht geschrieben"],
    ["Ausfuehrung", runControlQueueEnqueueResult?.execution_enabled || runControlQueueEnqueueResult?.execution_performed ? "aktiv" : "gesperrt"]
  ];
  const selectedQueueAction =
    runControlActionPlan?.actions.find((action) => action.queue_id === selectedQueueId) ??
    runControlActionPlan?.actions[0] ??
    null;
  const runControlActionPlanStatus =
    runControlActionPlanState === "error"
      ? runControlActionPlanError ?? "nicht erreichbar"
      : runControlActionPlanState === "loading"
        ? "laedt"
        : runControlActionPlan
          ? runControlActionPlan.status === "ok"
            ? "ok"
            : "Hinweis"
          : "laedt";
  const runControlActionPlanIssueLabel = runControlActionPlan
    ? runControlActionPlan.issues.length
      ? runControlActionPlan.issues.map((issue) => issue.code).join(", ")
      : "keine"
    : runControlActionPlanState === "error"
      ? runControlActionPlanError ?? "nicht erreichbar"
      : "laedt";
  const runControlActionPlanRows = [
    ["Status", runControlActionPlanStatus],
    ["Queue-Eintraege", String(runControlActionPlan?.queue_count ?? 0)],
    ["Ausgewaehlt", selectedQueueAction?.queue_id ?? selectedQueueId ?? "-"],
    ["Naechste Aktion", selectedQueueAction?.next_action ?? "-"],
    ["Aktion", selectedQueueAction?.next_action_label ?? "-"],
    ["Blocker", selectedQueueAction?.blocked_by.length ? selectedQueueAction.blocked_by.join(", ") : "keine"],
    ["Hinweise", runControlActionPlanIssueLabel],
    ["Schreibpfade", runControlActionPlan?.writes_performed ? "aktiv" : "gesperrt"],
    ["Ausfuehrung", selectedQueueAction?.execution_allowed || runControlActionPlan?.execution_performed ? "aktiv" : "gesperrt"]
  ];
  const executionReleaseStatus =
    executionReleaseState === "loading"
      ? "prueft"
      : executionReleaseResult?.release_ready
        ? "freigegeben"
        : executionReleaseError
          ? "blockiert"
          : selectedQueueAction?.next_action === "await_execution_release"
            ? "wartet"
            : selectedQueueAction?.next_action === "inspect_persisted_result"
              ? "erledigt"
              : selectedQueueAction?.blocked_by.length
                ? "blockiert"
                : "nicht bereit";
  const executionStartStatus =
    adapterStartState === "loading"
      ? "startet"
      : adapterStartResult?.result_persisted
        ? "abgeschlossen"
        : adapterStartError
          ? "fehlgeschlagen"
          : selectedQueueEntry?.status === "starting"
            ? "laeuft"
            : selectedQueueEntry?.status === "failed"
              ? "fehlgeschlagen"
              : runControlAdapterStartContract?.ui_start_enabled
                ? "bereit nach Freigabe"
                : "gesperrt";
  const runControlExecutionFlowSteps = [
    ["Preflight", runControlPreflightBoundaryStatus],
    ["Explizite Freigabe", executionReleaseStatus],
    ["Ausfuehren", executionStartStatus]
  ];
  const runControlExecutionFlowRows = [
    ["Startvertrag", runControlAdapterStartContract?.mode ?? "laedt"],
    ["Start-Endpunkt", runControlAdapterStartContract?.planned_start_endpoint ?? "-"],
    ["Payload", runControlAdapterStartContract?.api_accepts_start_payload ? "aktiv" : "gesperrt"],
    ["Payload-Validierung", runControlAdapterStartContract?.api_validates_start_payload ? "aktiv" : "gesperrt"],
    ["Adapterstart", runControlAdapterStartContract?.api_starts_adapter ? "aktiv" : "gesperrt"],
    ["UI-Start", runControlAdapterStartContract?.ui_start_enabled ? "aktiv" : "gesperrt"],
    ["Queue-Worker", runControlAdapterStartContract?.queue_worker_enabled ? "aktiv" : "gesperrt"],
    ["Freigabeprofil", executionReleaseRequest?.release_profile_id ?? "vu14-calculated-diagnostic"],
    ["Freigabe-ID", executionReleaseRequest?.idempotency_key ?? "noch nicht erzeugt"],
    ["Freigabecheck", executionReleaseError ?? executionReleaseResult?.status ?? "offen"],
    ["Startstatus", adapterStartError ?? adapterStartResult?.queue_status ?? selectedQueueEntry?.status ?? "offen"],
    ["Persistenz", selectedQueueEntry?.status === "result_persisted" ? "Ergebnis liegt vor" : "offen"],
    ["Naechster Schritt", selectedQueueAction?.next_action ?? runControlActionPlanStatus]
  ];
  const executionResultRecord = runControlExecutionResult?.record;
  const runControlExecutionResultStatus =
    runControlExecutionResultState === "error"
      ? runControlExecutionResultError ?? "nicht erreichbar"
      : runControlExecutionResultState === "loading"
        ? "laedt"
        : executionResultRecord
          ? "persistiert"
          : runControlExecutionResultError ?? "kein persistiertes Ergebnis";
  const runControlExecutionResultRows = [
    ["Status", runControlExecutionResultStatus],
    ["Queue", executionResultRecord?.queue_id ?? selectedQueueId ?? "-"],
    ["Run", executionResultRecord?.run_id ?? selectedQueueEntry?.request.run_id ?? "-"],
    ["Szenario", executionResultRecord?.scenario_id ?? selectedQueueEntry?.request.scenario_id ?? "-"],
    ["Ergebnis", executionResultRecord?.result_status ?? "-"],
    ["Summary", executionResultRecord?.summary_mode ?? "-"],
    ["Persistiert", executionResultRecord?.persisted_at ?? "-"],
    ["Adaptermodus", executionResultRecord?.adapter_mode ?? "-"],
    [
      "Adapterausfuehrung",
      executionResultRecord?.adapter_execution_performed || runControlExecutionResult?.adapter_started ? "dokumentiert" : "gesperrt"
    ],
    ["Simulation", executionResultRecord?.simulation_performed || runControlExecutionResult?.simulation_performed ? "aktiv" : "gesperrt"],
    [
      "Historische Gleichheit",
      executionResultRecord?.historical_full_equality_claimed ||
      runControlExecutionResult?.historical_full_equality_claimed
        ? "behauptet"
        : "nicht behauptet"
    ],
    ["Schreibpfade", runControlExecutionResult?.writes_performed ? "aktiv" : "gesperrt"],
    ["Ausfuehrung", runControlExecutionResult?.execution_performed ? "aktiv" : "gesperrt"]
  ];
  const latestExecutionAttempt =
    runControlExecutionHistory?.latest_attempt ?? runControlExecutionHistory?.attempts[0] ?? null;
  const runControlExecutionHistoryStatus =
    runControlExecutionHistoryState === "error"
      ? runControlExecutionHistoryError ?? "nicht erreichbar"
      : runControlExecutionHistoryState === "loading"
        ? "laedt"
        : latestExecutionAttempt
          ? latestExecutionAttempt.status
          : "noch kein Startversuch";
  const runControlExecutionHistoryRows = [
    ["Verlauf", runControlExecutionHistoryStatus],
    ["Queue-Status", runControlExecutionHistory?.queue_status ?? selectedQueueEntry?.status ?? "-"],
    ["Versuche", String(runControlExecutionHistory?.attempt_count ?? 0)],
    ["Attempt-ID", latestExecutionAttempt?.attempt_id ?? "-"],
    ["Idempotenz", latestExecutionAttempt?.idempotency_key ?? "-"],
    ["Freigegeben von", latestExecutionAttempt?.released_by ?? "-"],
    ["Freigabezeit", latestExecutionAttempt?.released_at ?? "-"],
    ["Startzeit", latestExecutionAttempt?.started_at ?? "-"],
    ["Abschluss", latestExecutionAttempt?.completed_at ?? "offen"],
    ["Begruendung", latestExecutionAttempt?.release_reason ?? "-"],
    ["Fehler", latestExecutionAttempt?.failure_message ?? "keiner"],
    [
      "Persistiertes Ergebnis",
      runControlExecutionHistory?.persisted_result_available ? "vorhanden" : "nicht vorhanden"
    ],
    [
      "Automatische Wiederholung",
      runControlExecutionHistory?.automatic_retry_enabled ? "aktiv" : "gesperrt"
    ],
    ["Queue-Worker", runControlExecutionHistory?.queue_worker_enabled ? "aktiv" : "gesperrt"]
  ];
  const selectedBridgeAction =
    runControlCoreBridge?.actions.find((action) => action.queue_id === selectedQueueId) ??
    runControlCoreBridge?.actions[0] ??
    null;
  const runControlCoreBridgeIssueLabel = runControlCoreBridge
    ? runControlCoreBridge.issues.length
      ? runControlCoreBridge.issues.map((issue) => issue.code).join(", ")
      : "keine"
    : "laedt";
  const runControlCoreBridgeRows = [
    ["Status", runControlCoreBridge?.status === "warning" ? "Hinweis" : runControlCoreBridge?.status ?? "laedt"],
    ["Queue-Eintraege", String(runControlCoreBridge?.queue_count ?? 0)],
    ["Brueckenaktionen", String(runControlCoreBridge?.action_count ?? 0)],
    ["Ausgewaehlt", selectedBridgeAction?.queue_id ?? selectedQueueId ?? "-"],
    ["Queue-Aktion", selectedBridgeAction?.queue_next_action ?? "-"],
    ["Brueckenaktion", selectedBridgeAction?.bridge_next_action ?? "-"],
    ["Kernstatus", selectedBridgeAction?.core_validation_status ?? runControlCoreBridge?.core_validation_mode ?? "-"],
    ["Periodenplaene", String(runControlCoreBridge?.period_plan_count ?? 0)],
    ["Legacy-Referenzen", String(runControlCoreBridge?.legacy_reference_count ?? 0)],
    ["Summary-Schritt", selectedBridgeAction?.execution_summary_next_action ?? runControlCoreBridge?.execution_summary_next_action ?? "-"],
    ["Blocker", selectedBridgeAction?.blocked_by.length ? selectedBridgeAction.blocked_by.join(", ") : "keine"],
    ["Hinweise", runControlCoreBridgeIssueLabel],
    ["Schreibpfade", selectedBridgeAction?.writes_performed || runControlCoreBridge?.writes_performed ? "aktiv" : "gesperrt"],
    [
      "Ausfuehrung",
      selectedBridgeAction?.execution_allowed ||
      selectedBridgeAction?.execution_performed ||
      runControlCoreBridge?.execution_performed
        ? "aktiv"
        : "gesperrt"
    ]
  ];
  const runControlBoundaryRows = [
    [
      "Queue",
      runControlQueue
        ? `${runControlQueue.queue_count} Eintraege, ${runControlQueue.issues.length} Hinweise`
        : "laedt"
    ],
    ["Preflight", runControlPreflightBoundaryStatus],
    ["Request-Vertrag", runControlRequestContract ? "lesend" : "laedt"],
    ["Dry-Run", runControlDryRunContract?.http_enabled ? runControlDryRunStatus : "gesperrt"],
    ["Adapter-Resultat", runControlAdapterResultContract ? "lesend" : "laedt"],
    ["Queue vormerken", runControlQueueEnqueueStatus],
    ["Aktionsplan", selectedQueueAction?.next_action ?? runControlActionPlanStatus],
    ["Kernbruecke", selectedBridgeAction?.bridge_next_action ?? "laedt"],
    [
      "Schreibpfade",
      runControlQueue?.writes_enabled ||
      runControlRequestContract?.writes_enabled ||
      runControlDryRunContract?.writes_enabled ||
      runControlDryRunContract?.writes_performed ||
      runControlDryRunResult?.writes_enabled ||
      runControlDryRunResult?.writes_performed ||
      runControlAdapterResultContract?.writes_performed ||
      runControlQueueEnqueueResult?.writes_performed ||
      runControlActionPlan?.writes_performed ||
      runControlCoreBridge?.writes_performed ||
      runControlPreflight?.writes_performed
        ? "aktiv"
        : "gesperrt"
    ],
    [
      "Ausfuehrung",
      runControlQueue?.execution_enabled ||
      runControlQueue?.execution_performed ||
      runControlRequestContract?.execution_enabled ||
      runControlRequestContract?.execution_performed ||
      runControlDryRunContract?.execution_enabled ||
      runControlDryRunContract?.execution_performed ||
      runControlDryRunResult?.execution_enabled ||
      runControlDryRunResult?.execution_performed ||
      runControlAdapterResultContract?.api_starts_adapter ||
      runControlAdapterResultContract?.execution_performed ||
      runControlAdapterResultContract?.simulation_performed ||
      runControlQueueEnqueueResult?.execution_enabled ||
      runControlQueueEnqueueResult?.execution_performed ||
      selectedQueueAction?.execution_allowed ||
      runControlActionPlan?.execution_performed ||
      selectedBridgeAction?.execution_allowed ||
      selectedBridgeAction?.execution_performed ||
      runControlCoreBridge?.execution_performed ||
      runControlPreflight?.execution_allowed ||
      runControlPreflight?.execution_performed
        ? "aktiv"
        : "gesperrt"
    ]
  ];
  const diagnosisRows = [
    ["Backend", healthStatus?.status === "ok" ? "bereit" : metadataState === "error" ? "nicht erreichbar" : "laedt"],
    ["Version", versionInfo ? `${versionInfo.name} ${versionInfo.version}` : "laedt"],
    ["Frontend", healthStatus?.frontend_available ? "gebaut" : "nicht gebaut"],
    ["Metadatenquelle", storageLabel],
    ["Schreibpfade", capabilities?.writes.scenario_metadata.enabled || capabilities?.writes.run_metadata.enabled ? "aktiv" : "gesperrt"],
    ["Simulation", capabilities?.simulation_execution.enabled ? "aktiv" : "gesperrt"],
    ["Import", "lokal per CLI"]
  ];

  return (
    <main className="shell">
      <aside className="sidebar" aria-label="Workbench Navigation">
        <div className="brand">
          <div className="brand-mark">IMS</div>
          <div>
            <strong>Workbench</strong>
            <span>lokale Vorschau</span>
          </div>
        </div>
        <nav>
          <a className="active" href="#overview">
            <Activity size={18} aria-hidden="true" /> Dashboard
          </a>
          <a href="#scenarios">
            <FileText size={18} aria-hidden="true" /> Szenarien
          </a>
          <a href="#strategies">
            <ListTree size={18} aria-hidden="true" /> Strategien
          </a>
          <a href="#validation">
            <ShieldCheck size={18} aria-hidden="true" /> Validierung
          </a>
          <a href="#runs">
            <Archive size={18} aria-hidden="true" /> Runs
          </a>
        </nav>
      </aside>

      <section className="content" id="overview">
        <header className="topbar">
          <div>
            <p className="eyebrow">IMS Modernisierung</p>
            <h1>Lokale Simulations-Workbench</h1>
          </div>
          <button className="primary-action" type="button">
            <Play size={18} aria-hidden="true" />
            Neuer Lauf
          </button>
        </header>

        <section className="status-grid" aria-label="Systemstatus">
          {statusItems.map((item) => (
            <article className="status-card" key={item.label}>
              <span className={`status-dot ${item.tone}`} />
              <p>{item.label}</p>
              <strong>{item.value}</strong>
            </article>
          ))}
        </section>

        <section className="work-grid">
          <article className="panel scenario-panel" id="scenarios">
            <div className="panel-heading">
              <FileText size={20} aria-hidden="true" />
              <h2>Szenario-Arbeitsstand</h2>
            </div>
            <div className="scenario-strip">
              <div>
                <span>Referenzfenster</span>
                <strong>{primaryScenario?.domain_scope ?? "wird geladen"}</strong>
              </div>
              <div>
                <span>Schreiben</span>
                <strong>{metadataState === "error" ? "API nicht erreichbar" : writeLabel}</strong>
              </div>
            </div>
            <p className="muted">
              {primaryScenario?.validation.claim ??
                "Diese Ansicht bereitet Bedienflaechen fuer lokale Szenario- und Run-Metadaten vor."}
              {" "}Der Simulationskern bleibt in diesem Schritt unveraendert.
            </p>
            <div className="metadata-list" aria-label="Szenario-Metadaten">
              {scenarios.map((scenario) => (
                <button
                  className={`metadata-row selectable ${scenario.id === selectedScenarioId ? "selected" : ""}`}
                  key={scenario.id}
                  type="button"
                  onClick={() => setSelectedScenarioId(scenario.id)}
                >
                  <span>{scenario.display_name}</span>
                  <strong>{scenario.status}</strong>
                </button>
              ))}
            </div>
          </article>

          <article className="panel" id="runs">
            <div className="panel-heading">
              <Database size={20} aria-hidden="true" />
              <h2>Lokale Ablage</h2>
            </div>
            <div className="meter">
              <span style={{ width: "18%" }} />
            </div>
            <p className="metric">SQLite-Vorbereitung</p>
            <p className="muted">
              {primaryRun
                ? `${primaryRun.display_name}: ${primaryRun.validation.scope}. Schreibpfade bleiben kontrolliert gesperrt.`
                : "Run- und Szenario-Metadaten werden spaeter lokal persistiert."}
            </p>
            <div className="source-status" aria-label="Metadatenquelle">
              <div>
                <span>Ablage</span>
                <strong>{metadataState === "error" ? "nicht erreichbar" : storageLabel}</strong>
              </div>
              <div>
                <span>Pfad</span>
                <strong>{storagePath}</strong>
              </div>
              <div>
                <span>Schreiben</span>
                <strong>{metadataSource?.writes_enabled ? "aktiv" : "gesperrt"}</strong>
              </div>
            </div>
            <div className="metadata-list compact" aria-label="Run-Metadaten">
              {runs.map((run) => (
                <button
                  className={`metadata-row selectable ${run.id === selectedRunId ? "selected" : ""}`}
                  key={run.id}
                  type="button"
                  onClick={() => selectRun(run)}
                >
                  <span>{run.period_window}</span>
                  <strong>{run.status}</strong>
                </button>
              ))}
            </div>
          </article>
        </section>

        <section className="panel detail-panel" aria-label="Metadaten-Details">
          <div className="panel-heading">
            <FileText size={20} aria-hidden="true" />
            <h2>Metadaten-Detail</h2>
          </div>
          <div className="detail-status">
            <span>Quelle</span>
            <strong>{detailStatusLabel}</strong>
          </div>
          {detailState === "error" ? (
            <p className="muted">{detailError}</p>
          ) : (
            <div className="detail-grid">
              <article>
                <span>Szenario</span>
                <strong>{scenarioDetail?.display_name ?? "wird geladen"}</strong>
                <dl>
                  <div>
                    <dt>ID</dt>
                    <dd>{scenarioDetail?.id ?? "-"}</dd>
                  </div>
                  <div>
                    <dt>Umfang</dt>
                    <dd>{scenarioDetail?.domain_scope ?? "-"}</dd>
                  </div>
                  <div>
                    <dt>Validierung</dt>
                    <dd>{scenarioDetail?.validation.scope ?? "-"}</dd>
                  </div>
                </dl>
              </article>
              <article>
                <span>Run</span>
                <strong>{runDetail?.display_name ?? "wird geladen"}</strong>
                <dl>
                  <div>
                    <dt>ID</dt>
                    <dd>{runDetail?.id ?? "-"}</dd>
                  </div>
                  <div>
                    <dt>Fenster</dt>
                    <dd>{runDetail?.period_window ?? "-"}</dd>
                  </div>
                  <div>
                    <dt>Ausfuehrung</dt>
                    <dd>{runDetail?.execution_enabled ? "aktiv" : "gesperrt"}</dd>
                  </div>
                </dl>
              </article>
            </div>
          )}
        </section>

        <section className="panel selection-summary-panel" aria-label="Auswahlzusammenfassung">
          <div className="panel-heading">
            <CircleDot size={20} aria-hidden="true" />
            <h2>Auswahlzusammenfassung</h2>
          </div>
          <div className="selection-summary-grid">
            {selectionRows.map(([label, value]) => (
              <div className="selection-summary-row" key={label}>
                <span>{label}</span>
                <strong>{value}</strong>
              </div>
            ))}
          </div>
        </section>

        <section
          className="panel strategy-catalog-panel"
          id="strategies"
          aria-label="Strategiekatalog"
          data-testid="strategy-catalog"
        >
          <div className="panel-heading strategy-catalog-heading">
            <div>
              <ListTree size={20} aria-hidden="true" />
              <h2>Strategiekatalog</h2>
            </div>
            <span className="readonly-marker">
              <LockKeyhole size={16} aria-hidden="true" />
              {strategyWorkbenchView === "draft"
                ? "Lokal, nicht gespeichert"
                : strategyWorkbenchView === "translation" ||
                    strategyWorkbenchView === "snapshots" ||
                    strategyWorkbenchView === "vu-snapshots"
                  ? "Nur Vorschau"
                  : strategyWorkbenchView === "context"
                    ? "Lokal, nur Pruefung"
                  : "Nur lesen"}
            </span>
          </div>
          <div className="strategy-catalog-summary" aria-label="Strategiekatalog-Status">
            <div>
              <span>Status</span>
              <strong>{strategyCatalogStatusLabel}</strong>
            </div>
            <div>
              <span>Vertrag</span>
              <strong>{strategyCatalog?.schema_version ?? "wird geladen"}</strong>
            </div>
            <div>
              <span>Regeln</span>
              <strong>{strategyCatalog?.strategies.length ?? 0}</strong>
            </div>
            <div>
              <span>Familien</span>
              <strong>{strategyCatalog?.families.length ?? 0}</strong>
            </div>
            <div>
              <span>Bedienmodus</span>
              <strong>{strategyCatalogBoundaryLabel}</strong>
            </div>
            <div>
              <span>Historische Vollgleichheit</span>
              <strong>{strategyCatalog
                ? strategyCatalog.historical_full_equality_claim
                  ? "behauptet"
                  : "nicht behauptet"
                : "wird geladen"}</strong>
            </div>
          </div>

          <div className="strategy-workbench-tabs" role="tablist" aria-label="Strategieansichten">
            <button
              className={strategyWorkbenchView === "catalog" ? "active" : ""}
              type="button"
              role="tab"
              aria-selected={strategyWorkbenchView === "catalog"}
              onClick={() => setStrategyWorkbenchView("catalog")}
            >
              <ListTree size={17} aria-hidden="true" />
              Katalog
            </button>
            <button
              className={strategyWorkbenchView === "assignments" ? "active" : ""}
              type="button"
              role="tab"
              aria-selected={strategyWorkbenchView === "assignments"}
              onClick={() => setStrategyWorkbenchView("assignments")}
            >
              <GitBranch size={17} aria-hidden="true" />
              Zuordnungen
            </button>
            <button
              className={strategyWorkbenchView === "parameters" ? "active" : ""}
              type="button"
              role="tab"
              aria-selected={strategyWorkbenchView === "parameters"}
              onClick={() => setStrategyWorkbenchView("parameters")}
            >
              <Braces size={17} aria-hidden="true" />
              Parameterschemata
            </button>
            <button
              className={strategyWorkbenchView === "draft" ? "active" : ""}
              type="button"
              role="tab"
              aria-selected={strategyWorkbenchView === "draft"}
              onClick={() => setStrategyWorkbenchView("draft")}
            >
              <ClipboardCheck size={17} aria-hidden="true" />
              Entwurf
            </button>
            <button
              className={strategyWorkbenchView === "translation" ? "active" : ""}
              type="button"
              role="tab"
              aria-selected={strategyWorkbenchView === "translation"}
              onClick={() => setStrategyWorkbenchView("translation")}
            >
              <Boxes size={17} aria-hidden="true" />
              Bauplaene
            </button>
            <button
              className={strategyWorkbenchView === "context" ? "active" : ""}
              type="button"
              role="tab"
              aria-selected={strategyWorkbenchView === "context"}
              onClick={() => setStrategyWorkbenchView("context")}
            >
              <Database size={17} aria-hidden="true" />
              Kontext
            </button>
            <button
              className={strategyWorkbenchView === "snapshots" ? "active" : ""}
              type="button"
              role="tab"
              aria-selected={strategyWorkbenchView === "snapshots"}
              onClick={() => setStrategyWorkbenchView("snapshots")}
            >
              <Eye size={17} aria-hidden="true" />
              VN-Snapshots
            </button>
            <button
              className={strategyWorkbenchView === "vu-snapshots" ? "active" : ""}
              type="button"
              role="tab"
              aria-selected={strategyWorkbenchView === "vu-snapshots"}
              onClick={() => setStrategyWorkbenchView("vu-snapshots")}
            >
              <ShieldCheck size={17} aria-hidden="true" />
              VU-Snapshots
            </button>
            <button
              className={strategyWorkbenchView === "candidates" ? "active" : ""}
              type="button"
              role="tab"
              aria-selected={strategyWorkbenchView === "candidates"}
              onClick={() => setStrategyWorkbenchView("candidates")}
            >
              <Archive size={17} aria-hidden="true" />
              Kandidaten
            </button>
          </div>

          {strategyWorkbenchView === "catalog" ? (
            strategyCatalogState === "error" ? (
              <div className="empty-state" role="alert">{strategyCatalogError}</div>
            ) : strategyCatalogState === "loading" ? (
              <div className="empty-state">Strategiekatalog wird geladen</div>
            ) : (
              <div className="strategy-actor-list">
                {STRATEGY_ACTOR_ORDER.map((actorType) => {
                  const actorStrategies = strategyCatalog?.strategies.filter(
                    (strategy) => strategy.actor_type === actorType
                  ) ?? [];
                  const actorFamilies = strategyCatalog?.families.filter(
                    (family) => family.actor_type === actorType
                  ) ?? [];
                  return (
                    <section className="strategy-actor-section" key={actorType}>
                      <div className="strategy-actor-heading">
                        <h3>{strategyActorLabel(actorType)}</h3>
                        <strong>{actorStrategies.length} Regeln</strong>
                      </div>
                      {actorFamilies.map((family) => {
                        const familyStrategies = actorStrategies.filter(
                          (strategy) => strategy.family_id === family.family_id
                        );
                        return (
                          <div className="strategy-family" key={family.family_id}>
                            <div className="strategy-family-heading">
                              <div>
                                <h4>{family.display_name}</h4>
                                <p>{family.description}</p>
                              </div>
                              <strong>{familyStrategies.length}</strong>
                            </div>
                            <div className="strategy-table" role="table" aria-label={family.display_name}>
                              <div className="strategy-table-head" role="row">
                                <span role="columnheader">Regel</span>
                                <span role="columnheader">Herkunft</span>
                                <span role="columnheader">Parameter</span>
                                <span role="columnheader">Teststand</span>
                              </div>
                              {familyStrategies.map((strategy) => (
                                <div className="strategy-table-row" role="row" key={strategy.strategy_id}>
                                  <div role="cell">
                                    <strong>{strategy.display_name}</strong>
                                    <small>{strategy.strategy_id}</small>
                                  </div>
                                  <div role="cell">
                                    <strong>{strategy.historical_action}</strong>
                                    <small>
                                      Kap. {strategy.source_chapter} · {strategy.included_in_vdefmd6
                                        ? `Vdefmd6 Klasse ${strategy.historical_rule_class}`
                                        : "nicht in Vdefmd6"}
                                    </small>
                                  </div>
                                  <div role="cell">
                                    <strong>{strategy.parameterized ? "parametrisierbar" : "feste Regel"}</strong>
                                    <small>
                                      {strategy.parameter_capabilities.map(strategyCapabilityLabel).join(", ")}
                                    </small>
                                  </div>
                                  <div role="cell">
                                    <strong>{strategyTestStatusLabel(strategy.test_status)}</strong>
                                    <small>{strategy.implementation_status === "ported_explicit_core"
                                      ? "expliziter Regelkern"
                                      : strategy.implementation_status}</small>
                                  </div>
                                </div>
                              ))}
                            </div>
                          </div>
                        );
                      })}
                    </section>
                  );
                })}
              </div>
            )
          ) : strategyWorkbenchView === "candidates" ? (
            <div className="strategy-contract-view strategy-candidate-view" data-testid="strategy-candidate-overview">
              <div className="strategy-contract-summary" aria-label="Kandidatenablage-Status">
                <div>
                  <span>Speicher</span>
                  <strong>{strategyCandidateStorageLabel}</strong>
                </div>
                <div>
                  <span>Kandidaten</span>
                  <strong>{strategyCandidateOverview?.candidate_count ?? 0}</strong>
                </div>
                <div>
                  <span>Integritaet</span>
                  <strong>{strategyCandidateIntegrityLabel}</strong>
                </div>
                <div>
                  <span>Ausfuehrung</span>
                  <strong>gesperrt</strong>
                </div>
              </div>

              <div className="strategy-boundary-band">
                <div>
                  <strong>Unveraenderlich gespeichert, noch nicht freigegeben</strong>
                  <span>
                    Diese Ansicht belegt Herkunft und Integritaet. Sie speichert nichts und startet keinen Lauf.
                  </span>
                </div>
                <span className="readonly-marker">
                  <LockKeyhole size={16} aria-hidden="true" />
                  Nur lesen
                </span>
              </div>

              <div className="strategy-candidate-toolbar">
                <div>
                  <strong>Gespeicherte Ausfuehrungskandidaten</strong>
                  <span>Neueste Ablage zuerst, jeder Digest wird serverseitig erneut geprueft.</span>
                </div>
                <button
                  className="secondary-action"
                  type="button"
                  disabled={strategyCandidateOverviewState === "loading"}
                  onClick={() => setStrategyCandidateOverviewRevision((current) => current + 1)}
                >
                  <RefreshCw size={16} aria-hidden="true" />
                  Aktualisieren
                </button>
              </div>

              {strategyCandidateOverviewState === "error" ? (
                <div className="empty-state" role="alert">{strategyCandidateOverviewError}</div>
              ) : strategyCandidateOverviewState === "loading" ? (
                <div className="empty-state">Kandidatenablage wird gelesen</div>
              ) : !strategyCandidateOverview?.storage.configured ? (
                <div className="empty-state">
                  Keine lokale SQLite-Ablage konfiguriert. Die Workbench bleibt vollstaendig read-only.
                </div>
              ) : strategyCandidateOverview.candidate_count === 0 ? (
                <div className="empty-state">
                  Noch keine gespeicherten Kandidaten. Diese Ansicht erzeugt oder speichert keine neuen Eintraege.
                </div>
              ) : (
                <div className="strategy-candidate-layout">
                  <div className="strategy-candidate-list" aria-label="Gespeicherte Kandidaten">
                    {strategyCandidateOverview.candidates.map((candidate) => (
                      <button
                        className={candidate.candidate_id === selectedStrategyCandidateId ? "active" : ""}
                        type="button"
                        aria-pressed={candidate.candidate_id === selectedStrategyCandidateId}
                        key={candidate.candidate_id}
                        onClick={() => setSelectedStrategyCandidateId(candidate.candidate_id)}
                      >
                        <span>
                          <strong>{candidate.draft_label}</strong>
                          <small>Periode {candidate.period} / {formatCandidateStoredAt(candidate.stored_at)}</small>
                        </span>
                        <CheckCircle2 size={17} aria-label="Digest geprueft" />
                      </button>
                    ))}
                  </div>

                  {selectedStrategyCandidate ? (
                    <article className="strategy-candidate-detail" aria-label="Kandidatendetails">
                      <div className="strategy-candidate-heading">
                        <div>
                          <span>Ausfuehrungskandidat</span>
                          <h3>{selectedStrategyCandidate.candidate_id}</h3>
                        </div>
                        <span className="strategy-candidate-verified">
                          <CheckCircle2 size={16} aria-hidden="true" />
                          Digest geprueft
                        </span>
                      </div>

                      <div className="strategy-candidate-readiness" aria-label="Kandidatenreife">
                        <div>
                          <CheckCircle2 size={17} aria-hidden="true" />
                          <span><strong>Eingang</strong><small>vollstaendig</small></span>
                        </div>
                        <div>
                          <CheckCircle2 size={17} aria-hidden="true" />
                          <span><strong>Marktprofil</strong><small>belegt</small></span>
                        </div>
                        <div>
                          <CheckCircle2 size={17} aria-hidden="true" />
                          <span><strong>Speicher</strong><small>intakt</small></span>
                        </div>
                        <div className="locked">
                          <LockKeyhole size={17} aria-hidden="true" />
                          <span>
                            <strong>Run-Control</strong>
                            <small>
                              {selectedStrategyCandidate.readiness.run_control_release_check_available
                                ? "Pruefung bereit"
                                : "gesperrt"}
                            </small>
                          </span>
                        </div>
                      </div>

                      <dl className="strategy-candidate-provenance">
                        <div>
                          <dt>Entwurf</dt>
                          <dd>
                            <strong>{selectedStrategyCandidate.draft_label}</strong>
                            <small>{selectedStrategyCandidate.draft_id}</small>
                          </dd>
                        </div>
                        <div>
                          <dt>Marktprofil</dt>
                          <dd>
                            <strong>{selectedStrategyCandidate.profile_id}</strong>
                            <small title={selectedStrategyCandidate.profile_content_digest}>
                              {shortCandidateDigest(selectedStrategyCandidate.profile_content_digest)}
                            </small>
                          </dd>
                        </div>
                        <div>
                          <dt>Umfang</dt>
                          <dd>
                            <strong>
                              Periode {selectedStrategyCandidate.period}, {selectedStrategyCandidate.insurer_count} VU,
                              {" "}{selectedStrategyCandidate.policyholder_count} VN
                            </strong>
                            <small>
                              {selectedStrategyCandidate.vu_snapshot_count} VU-Snapshots / {selectedStrategyCandidate.vn_rule_snapshot_count} VN-Regeln / {selectedStrategyCandidate.vn_process_snapshot_count} VN-Prozesse
                            </small>
                          </dd>
                        </div>
                        <div>
                          <dt>Herkunft</dt>
                          <dd>
                            <strong>{selectedStrategyCandidate.source_document_count} Quelldokumente</strong>
                            <small>{selectedStrategyCandidate.contract_version_count} versionierte Vertraege</small>
                          </dd>
                        </div>
                        <div>
                          <dt>Speicherstatus</dt>
                          <dd>
                            <strong>unveraenderlich gespeichert</strong>
                            <small>{formatCandidateStoredAt(selectedStrategyCandidate.stored_at)}</small>
                          </dd>
                        </div>
                        <div>
                          <dt>Inhalts-Digest</dt>
                          <dd>
                            <code title={selectedStrategyCandidate.content_digest}>
                              {selectedStrategyCandidate.content_digest}
                            </code>
                          </dd>
                        </div>
                      </dl>

                      <div className="strategy-candidate-lock-note">
                        <LockKeyhole size={18} aria-hidden="true" />
                        <div>
                          <strong>Ausfuehrung bleibt gesperrt</strong>
                          <span>Die Kandidatenfreigabe kann per API geprueft werden. Start und Ausfuehrung bleiben bis {selectedStrategyCandidate.readiness.next_gate} gesperrt.</span>
                        </div>
                      </div>
                    </article>
                  ) : null}
                </div>
              )}
            </div>
          ) : strategyAssignmentState === "error" ? (
            <div className="empty-state" role="alert">{strategyAssignmentError}</div>
          ) : strategyAssignmentState === "loading" ? (
            <div className="empty-state">Strategiezuordnungen werden geladen</div>
          ) : strategyWorkbenchView === "assignments" ? (
            <div className="strategy-contract-view" data-testid="strategy-assignment-profiles">
              <div className="strategy-contract-summary" aria-label="Zuordnungsvertrag-Status">
                <div>
                  <span>Status</span>
                  <strong>{strategyAssignmentStatusLabel}</strong>
                </div>
                <div>
                  <span>Quellmodell</span>
                  <strong>{strategyAssignmentContract?.source_summary.model ?? "-"}</strong>
                </div>
                <div>
                  <span>Quellprofile</span>
                  <strong>{strategyAssignmentContract?.source_summary.profile_count ?? 0}</strong>
                </div>
                <div>
                  <span>Akteure</span>
                  <strong>
                    {strategyAssignmentContract
                      ? `${strategyAssignmentContract.source_summary.insurer_count} VU · ${strategyAssignmentContract.source_summary.policyholder_count} VN`
                      : "-"}
                  </strong>
                </div>
              </div>

              <div className="strategy-boundary-band">
                <div>
                  <strong>{strategyAssignmentContract?.sector_contract.position_count ?? 0} historische Sektorpositionen</strong>
                  <span>
                    Eine Strategie gilt gemeinsam fuer beide Positionen; moderne Spartennamen sind noch nicht zugeordnet.
                  </span>
                </div>
                <span className="readonly-marker">
                  <LockKeyhole size={16} aria-hidden="true" />
                  {strategyAssignmentBoundaryLabel}
                </span>
              </div>

              <div className="strategy-target-list" aria-label="Zulaessige Strategiezuordnungen">
                {(strategyAssignmentContract?.assignment_targets ?? []).map((target) => (
                  <div className="strategy-target-row" key={target.actor_type}>
                    <div>
                      <strong>{strategyActorLabel(target.actor_type)}</strong>
                      <small>Einzelzuordnung je Akteur</small>
                    </div>
                    <div>
                      <strong>{target.eligible_strategy_ids.length} zulaessige Strategien</strong>
                      <small>keine Gruppenbearbeitung</small>
                    </div>
                    <div>
                      <strong>0 oder 1 Strategie</strong>
                      <small>keine geplanten Wechsel</small>
                    </div>
                  </div>
                ))}
              </div>

              {STRATEGY_ACTOR_ORDER.map((actorType) => {
                const profiles = strategyAssignmentContract?.source_profiles.filter(
                  (profile) => profile.actor_type === actorType
                ) ?? [];
                return (
                  <section className="strategy-actor-section" key={actorType}>
                    <div className="strategy-actor-heading">
                      <h3>{strategyActorLabel(actorType)}</h3>
                      <strong>{profiles.length} Quellprofile</strong>
                    </div>
                    <div className="strategy-profile-table" role="table" aria-label={`${strategyActorLabel(actorType)} Quellprofile`}>
                      <div className="strategy-profile-head" role="row">
                        <span role="columnheader">Akteure</span>
                        <span role="columnheader">Historische Strategie</span>
                        <span role="columnheader">Laufbindung</span>
                        <span role="columnheader">Parameterprofil</span>
                      </div>
                      {profiles.map((profile) => {
                        const strategy = strategyDefinitionById.get(profile.strategy_id);
                        return (
                          <div className="strategy-profile-row" role="row" key={profile.profile_id}>
                            <div role="cell">
                              <strong>{strategyTargetRangeLabel(profile)}</strong>
                              <small>
                                {profile.target_count} {profile.target_count === 1 ? "Akteur" : "Akteure"} · {profile.profile_id}
                              </small>
                            </div>
                            <div role="cell">
                              <strong>{strategy?.display_name ?? profile.strategy_id}</strong>
                              <small>Regel {profile.historical_rule_id} · Klasse {profile.historical_rule_class}</small>
                            </div>
                            <div role="cell">
                              <strong>ab Periode {profile.activation_period}</strong>
                              <small>Laufhorizont {profile.active_through_run} · Logtime {profile.logical_time}</small>
                            </div>
                            <div role="cell">
                              <strong>{profile.parameter_schema ? "Strategieschema vorhanden" : "kein Strategieschema"}</strong>
                              <small>
                                {profile.parameter_schema ? `${profile.parameter_schema} · ` : ""}
                                {profile.parameter_values_exposed
                                  ? `${profile.legacy_parameter_value_count} Quellwerte sichtbar`
                                  : `${profile.legacy_parameter_value_count} Quellwerte geschuetzt · Profil ${shortStrategyFingerprint(profile.legacy_parameter_fingerprint)}`}
                              </small>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </section>
                );
              })}
            </div>
          ) : strategyWorkbenchView === "parameters" ? (
            <div className="strategy-contract-view" data-testid="strategy-parameter-schemas">
              <div className="strategy-contract-summary" aria-label="Parameterschema-Status">
                <div>
                  <span>Vertrag</span>
                  <strong>{strategyAssignmentContract?.schema_version ?? "-"}</strong>
                </div>
                <div>
                  <span>Schemata</span>
                  <strong>{strategyAssignmentContract?.parameter_schemas.length ?? 0}</strong>
                </div>
                <div>
                  <span>Feldform</span>
                  <strong>2 historische Positionen</strong>
                </div>
                <div>
                  <span>Parameterwerte</span>
                  <strong>
                    {strategyAssignmentContract?.source_summary.parameter_values_exposed ? "sichtbar" : "nicht offengelegt"}
                  </strong>
                </div>
              </div>

              <div className="strategy-boundary-band">
                <div>
                  <strong>Vorhandene Loaderformen, keine neuen Fachgrenzen</strong>
                  <span>
                    Die Ansicht zeigt Feldnamen und bestehende technische Pruefungen, aber keine konkreten Werte oder Defaults.
                  </span>
                </div>
                <span className="readonly-marker">
                  <LockKeyhole size={16} aria-hidden="true" />
                  {strategyAssignmentBoundaryLabel}
                </span>
              </div>

              {STRATEGY_ACTOR_ORDER.map((actorType) => {
                const schemas = strategyAssignmentContract?.parameter_schemas.filter(
                  (schema) => schema.actor_type === actorType
                ) ?? [];
                return (
                  <section className="strategy-actor-section" key={actorType}>
                    <div className="strategy-actor-heading">
                      <h3>{strategyActorLabel(actorType)}</h3>
                      <strong>{schemas.length} Schemata</strong>
                    </div>
                    <div className="strategy-schema-list">
                      {schemas.map((schema, index) => (
                        <details className="strategy-schema" key={schema.schema_id} open={index === 0}>
                          <summary>
                            <div>
                              <strong>{schema.schema_id}</strong>
                              <small>
                                {schema.strategy_ids.map((strategyId) =>
                                  strategyDefinitionById.get(strategyId)?.display_name ?? strategyId
                                ).join(", ")}
                              </small>
                            </div>
                            <span>{schema.fields.length} Felder</span>
                          </summary>
                          <div className="strategy-schema-source">
                            <span>{schema.module}</span>
                            <strong>{schema.loader_entrypoint}</strong>
                          </div>
                          <div className="strategy-schema-fields" role="table" aria-label={`${schema.schema_id} Felder`}>
                            <div className="strategy-schema-field-head" role="row">
                              <span role="columnheader">Feld</span>
                              <span role="columnheader">Form</span>
                              <span role="columnheader">Bestehende Pruefung</span>
                            </div>
                            {schema.fields.map((field) => (
                              <div className="strategy-schema-field-row" role="row" key={field.field_name}>
                                <div role="cell">
                                  <strong>{field.display_name}</strong>
                                  <small>{field.field_name}</small>
                                </div>
                                <div role="cell">
                                  <strong>{field.python_type}</strong>
                                  <small>2 historische Positionen</small>
                                </div>
                                <div role="cell">
                                  <strong>{strategyValidationLabel(field.existing_validation)}</strong>
                                  <small>{field.required_by_existing_loader ? "Pflichtfeld im Loader" : "optional"}</small>
                                </div>
                              </div>
                            ))}
                          </div>
                        </details>
                      ))}
                    </div>
                  </section>
                );
              })}

              <div className="strategy-unparameterized-note">
                <strong>Vrvn01: Pflichtversicherung</strong>
                <span>
                  Kein eigenes Strategieschema. Explizite Versichererwahl-Ziehungen bleiben Laufeingaben und werden hier nicht als Parameter dargestellt.
                </span>
              </div>
            </div>
          ) : strategyWorkbenchView === "snapshots" ? (
            strategySnapshotMaterializationContractState === "error" ? (
              <div className="empty-state" role="alert">
                {strategySnapshotMaterializationContractError}
              </div>
            ) : strategySnapshotMaterializationContractState === "loading" ? (
              <div className="empty-state">VN-Snapshotvertrag wird geladen</div>
            ) : (
              <div
                className="strategy-contract-view strategy-materialized-view"
                data-testid="strategy-snapshot-materialization-preview"
              >
                <div className="strategy-contract-summary" aria-label="VN-Snapshot-Vorschau-Status">
                  <div>
                    <span>Materialisierung</span>
                    <strong>{strategySnapshotMaterializationContract?.operation.schema_version ?? "-"}</strong>
                  </div>
                  <div>
                    <span>Periode</span>
                    <strong>{strategySnapshotMaterialization?.period ?? "noch offen"}</strong>
                  </div>
                  <div>
                    <span>VN-Snapshots</span>
                    <strong>
                      {strategySnapshotMaterialization
                        ? `${strategySnapshotMaterialization.snapshot_count} / ${strategySnapshotMaterialization.expected_snapshot_count}`
                        : "noch keine"}
                    </strong>
                  </div>
                  <div>
                    <span>Status</span>
                    <strong>{strategySnapshotMaterializationStatusLabel}</strong>
                  </div>
                </div>

                <div className="strategy-boundary-band">
                  <div>
                    <strong>Typisierte Eingabevorschau fuer eine VN-Regelperiode</strong>
                    <span>
                      Die Ansicht zeigt nur vollstaendig erzeugte In-Memory-Snapshots. Sie speichert nichts und fuehrt keine Regel aus.
                    </span>
                  </div>
                  <span className="readonly-marker">
                    <LockKeyhole size={16} aria-hidden="true" />
                    Vorschau ohne Ausfuehrung
                  </span>
                </div>

                {!strategySnapshotMaterialization?.materialization_complete ? (
                  <div className="strategy-snapshot-prerequisite">
                    <Database size={20} aria-hidden="true" />
                    <div>
                      <strong>Zuerst einen gueltigen Kontext in VN-Snapshots ueberfuehren</strong>
                      <span>Die Vorschau entsteht im Kontext-Tab nach der serverseitigen Pruefung.</span>
                    </div>
                    <button
                      className="secondary-action"
                      type="button"
                      onClick={() => setStrategyWorkbenchView("context")}
                    >
                      <Database size={17} aria-hidden="true" />
                      Zum Kontext
                    </button>
                  </div>
                ) : (
                  <>
                    <div className="strategy-materialized-list-heading">
                      <div>
                        <strong>{strategySnapshotMaterialization.snapshot_count} VN-Snapshots vollstaendig erzeugt</strong>
                        <span>
                          {strategySnapshotMaterialization.snapshot_loader_invocation_count} Snapshot-Loader und {strategySnapshotMaterialization.nested_loader_invocation_count} verschachtelte Loader wurden aufgerufen.
                        </span>
                      </div>
                      <span>Entwurf {strategySnapshotMaterialization.draft_id}</span>
                    </div>
                    <div className="strategy-materialized-list" aria-label="Materialisierte VN-Snapshots">
                      {strategySnapshotMaterialization.snapshots.map((entry, index) => {
                        const strategy = strategyDefinitionById.get(entry.strategy_id);
                        const visibleFields = strategyMaterializedSnapshotFields(
                          entry.snapshot,
                          strategySnapshotMaterialization.period
                        );
                        return (
                          <details
                            className="strategy-materialized-entry"
                            open={index === 0}
                            key={`${entry.strategy_id}-${entry.snapshot.policyholder_id}`}
                          >
                            <summary>
                              <div>
                                <strong>
                                  VN {entry.snapshot.policyholder_id} · {strategy?.display_name ?? entry.strategy_id}
                                </strong>
                                <span>{entry.strategy_id} · {entry.snapshot.rule_kind}</span>
                              </div>
                              <span>typisiert</span>
                            </summary>
                            <div className="strategy-materialized-entry-body">
                              <div className="strategy-materialized-meta">
                                <span>Snapshottyp <strong>{entry.snapshot_type}</strong></span>
                                <span>Sammlung <strong>{entry.snapshot_collection}</strong></span>
                              </div>
                              {strategyMaterializedSnapshotGroups.map((group) => {
                                const fields = group.fields.filter((fieldName) => visibleFields.has(fieldName));
                                if (fields.length === 0) {
                                  return null;
                                }
                                return (
                                  <section className="strategy-materialized-group" key={group.label}>
                                    <h3>{group.label}</h3>
                                    <div className="strategy-materialized-fields">
                                      {fields.map((fieldName) => (
                                        <div key={fieldName}>
                                          <div>
                                            <strong>{strategySnapshotFieldLabel(fieldName)}</strong>
                                            <small>{fieldName}</small>
                                          </div>
                                          <div className="strategy-materialized-value">
                                            <StrategySnapshotPreviewValue
                                              value={entry.snapshot[fieldName as keyof StrategyMaterializedVNSnapshotPayload]}
                                            />
                                          </div>
                                        </div>
                                      ))}
                                    </div>
                                  </section>
                                );
                              })}
                            </div>
                          </details>
                        );
                      })}
                    </div>
                    <div className="strategy-context-report-boundaries strategy-materialized-boundaries">
                      <span>Teilresultate: {strategySnapshotMaterialization.partial_results_returned ? "ja" : "nein"}</span>
                      <span>Speicherung: {strategySnapshotMaterialization.persistence_performed ? "ja" : "nein"}</span>
                      <span>Ausfuehrungsbereit: {strategySnapshotMaterialization.execution_ready ? "ja" : "nein"}</span>
                      <span>Runner: {strategySnapshotMaterialization.runner_invoked ? "ja" : "nein"}</span>
                      <span>Ausfuehrung: {strategySnapshotMaterialization.execution_performed ? "ja" : "nein"}</span>
                      <span>Simulation: {strategySnapshotMaterialization.simulation_performed ? "ja" : "nein"}</span>
                    </div>
                  </>
                )}
              </div>
            )
          ) : strategyWorkbenchView === "vu-snapshots" ? (
            strategyVUContractsState === "error" ? (
              <div className="empty-state" role="alert">{strategyVUContractsError}</div>
            ) : strategyVUContractsState === "loading" ? (
              <div className="empty-state">VU-Snapshotvertraege werden geladen</div>
            ) : (
              <div
                className="strategy-contract-view strategy-materialized-view"
                data-testid="strategy-vu-snapshot-materialization-preview"
              >
                <div className="strategy-contract-summary" aria-label="VU-Snapshot-Vorschau-Status">
                  <div>
                    <span>Materialisierung</span>
                    <strong>{strategyVUMaterializationContract?.operation.schema_version ?? "-"}</strong>
                  </div>
                  <div>
                    <span>Periode</span>
                    <strong>
                      {strategyVUMaterialization?.period ??
                        strategySnapshotContextPeriodValue ??
                        "noch offen"}
                    </strong>
                  </div>
                  <div>
                    <span>VU-Snapshots</span>
                    <strong>
                      {strategyVUMaterialization
                        ? `${strategyVUMaterialization.snapshot_count} / ${
                            strategyVUMaterialization.expected_snapshot_count
                          }`
                        : `0 / ${strategyVUTranslationEntries.length}`}
                    </strong>
                  </div>
                  <div>
                    <span>Status</span>
                    <strong>{strategyVUMaterializationStatusLabel}</strong>
                  </div>
                </div>

                <div className="strategy-boundary-band">
                  <div>
                    <strong>Typisierte Eingabevorschau fuer eine VU-Regelperiode</strong>
                    <span>
                      Der getrennte Zustandsbeleg wird nur gegen den Kontext geprueft.
                      Snapshotwerte stammen weiterhin aus dem Kontext.
                    </span>
                  </div>
                  <span className="readonly-marker">
                    <LockKeyhole size={16} aria-hidden="true" />
                    Vorschau ohne Ausfuehrung
                  </span>
                </div>

                {!strategySnapshotContextValidation?.valid ? (
                  <div className="strategy-snapshot-prerequisite">
                    <Database size={20} aria-hidden="true" />
                    <div>
                      <strong>Zuerst Entwurf, Bauplaene und Kontext gueltig pruefen</strong>
                      <span>Die VU-Vorschau bleibt an denselben lokalen Einperiodenkontext gebunden.</span>
                    </div>
                    <button
                      className="secondary-action"
                      type="button"
                      onClick={() => setStrategyWorkbenchView("context")}
                    >
                      <Database size={17} aria-hidden="true" />
                      Zum Kontext
                    </button>
                  </div>
                ) : strategyVUTranslationEntries.length === 0 ? (
                  <div className="strategy-snapshot-prerequisite">
                    <ShieldCheck size={20} aria-hidden="true" />
                    <div>
                      <strong>Der gepruefte Entwurf enthaelt keinen Versicherer</strong>
                      <span>VU-Snapshots entstehen nur fuer VU-Strategiezuordnungen.</span>
                    </div>
                  </div>
                ) : (
                  <>
                    <section className="strategy-context-action" aria-label="VU-Zustandsbeleg anlegen">
                      <div>
                        <strong>Getrennten VU-Zustandsbeleg erfassen</strong>
                        <span>
                          Der Beleg bestaetigt Zins, Schock, Marktbestand und
                          regelabhaengige VU-Zustaende, ohne sie als Snapshotquelle zu verwenden.
                        </span>
                      </div>
                      {strategyVUStateEditor.entries.length === 0 ? (
                        <button
                          className="primary-action"
                          type="button"
                          disabled={!canInitializeStrategyVUState}
                          onClick={initializeStrategyVUState}
                        >
                          <Plus size={17} aria-hidden="true" />
                          Zustandsbeleg anlegen
                        </button>
                      ) : (
                        <button
                          className="secondary-action"
                          type="button"
                          onClick={discardStrategyVUState}
                        >
                          <X size={17} aria-hidden="true" />
                          Zustandsbeleg verwerfen
                        </button>
                      )}
                    </section>

                    {strategyVUStateEditor.entries.length === 0 ? (
                      <div className="strategy-snapshot-prerequisite ready">
                        <ShieldCheck size={20} aria-hidden="true" />
                        <div>
                          <strong>{strategyVUTranslationEntries.length} VU-Bauplaene sind bereit</strong>
                          <span>Der Herkunftsbeleg wird erst nach der ausdruecklichen Aktion lokal angelegt.</span>
                        </div>
                      </div>
                    ) : (
                      <>
                        <section className="strategy-vu-period-state" aria-label="Gemeinsamer VU-Periodenzustand">
                          <div className="strategy-vu-state-heading">
                            <strong>Gemeinsamer Periodenzustand</strong>
                            <span>Diese Werte muessen mit jedem betroffenen Kontextwert identisch sein.</span>
                          </div>
                          <div className="strategy-vu-period-state-fields">
                            <label>
                              <span>Zinssatz</span>
                              <input
                                aria-label="Zinssatz im VU-Zustandsbeleg"
                                type="number"
                                step="any"
                                value={strategyVUStateEditor.interestRate}
                                onChange={(event) => updateStrategyVUPeriodState(
                                  "interestRate",
                                  event.target.value
                                )}
                                placeholder="z. B. 0,02"
                              />
                            </label>
                            <label>
                              <span>Schockstatus</span>
                              <select
                                aria-label="Schockstatus im VU-Zustandsbeleg"
                                value={strategyVUStateEditor.changeShock}
                                onChange={(event) => updateStrategyVUPeriodState(
                                  "changeShock",
                                  event.target.value
                                )}
                              >
                                <option value="">Bitte waehlen</option>
                                <option value="false">Normalzustand</option>
                                <option value="true">Aenderungsschock</option>
                              </select>
                            </label>
                            <label>
                              <span>Aktive VN</span>
                              <input
                                aria-label="Aktive VN im VU-Zustandsbeleg"
                                type="number"
                                min="0"
                                step="1"
                                value={strategyVUStateEditor.activePolicyholderCount}
                                onChange={(event) => updateStrategyVUPeriodState(
                                  "activePolicyholderCount",
                                  event.target.value
                                )}
                                placeholder="Anzahl"
                              />
                            </label>
                          </div>
                        </section>

                        <div className="strategy-context-list" aria-label="VU-Zustandseintraege">
                          {strategyVUStateEditor.entries.map((entry, entryIndex) => {
                            const strategy = strategyDefinitionById.get(entry.strategy_id);
                            const fields = Object.keys(entry.values);
                            return (
                              <details
                                className="strategy-context-entry"
                                open={fields.length > 0}
                                key={`${entry.strategy_id}-${entry.insurer_id}`}
                              >
                                <summary>
                                  <div>
                                    <strong>
                                      VU {entry.insurer_id} · {strategy?.display_name ?? entry.strategy_id}
                                    </strong>
                                    <span>{entry.strategy_id}</span>
                                  </div>
                                  <span className="open">
                                    {fields.length === 0 ? "kein Zusatzwert" : `${fields.length} Herkunftswerte`}
                                  </span>
                                </summary>
                                <div className="strategy-context-entry-body">
                                  {fields.length === 0 ? (
                                    <div className="strategy-vu-empty-state-values">
                                      Fuer diese Regel genuegt der gemeinsame Periodenzustand.
                                    </div>
                                  ) : fields.map((fieldName) => (
                                    <div className="strategy-context-field" key={fieldName}>
                                      <div className="strategy-context-field-name">
                                        <strong>{strategyVUStateFieldLabels[fieldName] ?? fieldName}</strong>
                                        <small>{fieldName}</small>
                                        <span>Getrennter Herkunftsbeleg</span>
                                      </div>
                                      <div className="strategy-context-field-control">
                                        <textarea
                                          aria-label={`${
                                            strategyVUStateFieldLabels[fieldName] ?? fieldName
                                          } fuer VU ${entry.insurer_id}`}
                                          rows={2}
                                          value={entry.values[fieldName]}
                                          onChange={(event) => updateStrategyVUEntryState(
                                            entryIndex,
                                            fieldName,
                                            event.target.value
                                          )}
                                          placeholder={fieldName === "policyholders_t_minus_2"
                                            ? "[0, 0]"
                                            : "[0, 0, 0]"}
                                          spellCheck={false}
                                        />
                                      </div>
                                      <span className="strategy-context-required">Pflichtwert</span>
                                    </div>
                                  ))}
                                </div>
                              </details>
                            );
                          })}
                        </div>

                        <section
                          className="strategy-context-action strategy-materialization-action"
                          aria-label="VU-Snapshot-Vorschau erzeugen"
                        >
                          <div>
                            <strong>VU-Snapshots atomar im Speicher erzeugen</strong>
                            <span>
                              PR121 prueft zuerst den gesamten Herkunftsbeleg und zeigt keine Teilresultate.
                            </span>
                          </div>
                          <button
                            className="primary-action"
                            type="button"
                            disabled={!canMaterializeStrategyVUSnapshots}
                            onClick={materializeStrategyVUSnapshots}
                          >
                            <Eye size={17} aria-hidden="true" />
                            {strategyVUMaterializationState === "loading"
                              ? "Snapshots werden erzeugt"
                              : "VU-Snapshots anzeigen"}
                          </button>
                        </section>

                        {strategyVUMaterializationError ? (
                          <div className="empty-state" role="alert">
                            {strategyVUMaterializationError}
                          </div>
                        ) : strategyVUMaterialization && !strategyVUMaterialization.materialization_complete ? (
                          <div className="strategy-draft-report invalid strategy-materialization-errors" role="alert">
                            <div className="strategy-draft-report-summary">
                              <CircleAlert size={20} aria-hidden="true" />
                              <div>
                                <strong>VU-Snapshots noch nicht erzeugt</strong>
                                <span>
                                  Eingabe oder Herkunft meldet {strategyVUMaterialization.issue_count} Fehler.
                                </span>
                              </div>
                            </div>
                            <div className="strategy-draft-issues">
                              {strategyVUMaterialization.issues.map((issue) => (
                                <div key={`${issue.stage}-${issue.path}-${issue.code}`}>
                                  <strong>{issue.path}</strong>
                                  <span>{issue.message}</span>
                                </div>
                              ))}
                            </div>
                          </div>
                        ) : null}

                        {strategyVUMaterialization?.materialization_complete ? (
                          <>
                            <div className="strategy-vu-provenance-band">
                              <span>
                                Herkunftsabgleich
                                <strong>
                                  {strategyVUMaterialization.state_provenance_validated
                                    ? "vollstaendig"
                                    : "offen"}
                                </strong>
                              </span>
                              <span>
                                Kontextwerte
                                <strong>
                                  {strategyVUMaterialization.context_values_consumed
                                    ? "verwendet"
                                    : "nicht verwendet"}
                                </strong>
                              </span>
                              <span>
                                Zustandswerte
                                <strong>
                                  {strategyVUMaterialization.state_values_consumed
                                    ? "verwendet"
                                    : "nur geprueft"}
                                </strong>
                              </span>
                              <span>
                                Ziehungsherkunft
                                <strong>
                                  {strategyVUStateContract?.draw_values_cross_checked_against_draw_plan
                                    ? "abgeglichen"
                                    : "nicht abgeglichen"}
                                </strong>
                              </span>
                            </div>
                            <div className="strategy-materialized-list-heading">
                              <div>
                                <strong>
                                  {strategyVUMaterialization.snapshot_count} VU-Snapshots vollstaendig erzeugt
                                </strong>
                                <span>
                                  {strategyVUMaterialization.snapshot_loader_invocation_count}
                                  {" vorhandene Snapshot-Loader wurden atomar aufgerufen."}
                                </span>
                              </div>
                              <span>Entwurf {strategyVUMaterialization.draft_id}</span>
                            </div>
                            <div className="strategy-materialized-list" aria-label="Materialisierte VU-Snapshots">
                              {strategyVUMaterialization.snapshots.map((entry, index) => {
                                const strategy = strategyDefinitionById.get(entry.strategy_id);
                                return (
                                  <details
                                    className="strategy-materialized-entry"
                                    open={index === 0}
                                    key={`${entry.strategy_id}-${entry.snapshot.insurer_id}`}
                                  >
                                    <summary>
                                      <div>
                                        <strong>
                                          VU {entry.snapshot.insurer_id} ·{" "}
                                          {strategy?.display_name ?? entry.strategy_id}
                                        </strong>
                                        <span>
                                          {entry.strategy_id}
                                          {entry.snapshot.rule_kind ? ` · ${entry.snapshot.rule_kind}` : ""}
                                        </span>
                                      </div>
                                      <span>typisiert</span>
                                    </summary>
                                    <div className="strategy-materialized-entry-body">
                                      <div className="strategy-materialized-meta">
                                        <span>Snapshottyp <strong>{entry.snapshot_type}</strong></span>
                                        <span>Sammlung <strong>{entry.snapshot_collection}</strong></span>
                                      </div>
                                      {strategyMaterializedVUSnapshotGroups.map((group) => {
                                        const fields = group.fields.filter((fieldName) => (
                                          Object.prototype.hasOwnProperty.call(entry.snapshot, fieldName)
                                        ));
                                        if (fields.length === 0) {
                                          return null;
                                        }
                                        return (
                                          <section className="strategy-materialized-group" key={group.label}>
                                            <h3>{group.label}</h3>
                                            <div className="strategy-materialized-fields">
                                              {fields.map((fieldName) => (
                                                <div key={fieldName}>
                                                  <div>
                                                    <strong>{strategySnapshotFieldLabel(fieldName)}</strong>
                                                    <small>{fieldName}</small>
                                                  </div>
                                                  <div className="strategy-materialized-value">
                                                    <StrategySnapshotPreviewValue
                                                      value={entry.snapshot[fieldName]}
                                                    />
                                                  </div>
                                                </div>
                                              ))}
                                            </div>
                                          </section>
                                        );
                                      })}
                                    </div>
                                  </details>
                                );
                              })}
                            </div>
                            <div className="strategy-context-report-boundaries strategy-materialized-boundaries">
                              <span>
                                Teilresultate:{" "}
                                {strategyVUMaterialization.partial_results_returned ? "ja" : "nein"}
                              </span>
                              <span>
                                Speicherung:{" "}
                                {strategyVUMaterialization.persistence_performed ? "ja" : "nein"}
                              </span>
                              <span>
                                Ausfuehrungsbereit:{" "}
                                {strategyVUMaterialization.execution_ready ? "ja" : "nein"}
                              </span>
                              <span>Runner: {strategyVUMaterialization.runner_invoked ? "ja" : "nein"}</span>
                              <span>Ausfuehrung: {strategyVUMaterialization.execution_performed ? "ja" : "nein"}</span>
                              <span>Simulation: {strategyVUMaterialization.simulation_performed ? "ja" : "nein"}</span>
                            </div>
                          </>
                        ) : null}
                      </>
                    )}
                  </>
                )}
              </div>
            )
          ) : strategyWorkbenchView === "context" ? (
            strategySnapshotContextContractState === "error" ? (
              <div className="empty-state" role="alert">{strategySnapshotContextContractError}</div>
            ) : strategySnapshotContextContractState === "loading" ? (
              <div className="empty-state">Snapshot-Kontextvertrag wird geladen</div>
            ) : (
              <div
                className="strategy-contract-view strategy-context-view"
                data-testid="strategy-snapshot-context-editor"
              >
                <div className="strategy-contract-summary" aria-label="Snapshot-Kontext-Status">
                  <div>
                    <span>Kontextvertrag</span>
                    <strong>{strategySnapshotContextContract?.schema_version ?? "-"}</strong>
                  </div>
                  <div>
                    <span>Periode</span>
                    <strong>{strategySnapshotContextPeriodValue ?? "noch offen"}</strong>
                  </div>
                  <div>
                    <span>Erfasste Werte</span>
                    <strong>
                      {strategySnapshotContextEnteredValueCount} / {strategySnapshotContextExpectedValueCount || strategySnapshotOpenFieldCount}
                    </strong>
                  </div>
                  <div>
                    <span>Pruefstatus</span>
                    <strong>{strategySnapshotContextValidationLabel}</strong>
                  </div>
                </div>

                <div className="strategy-boundary-band">
                  <div>
                    <strong>Einperiodenkontext im aktuellen Browserfenster</strong>
                    <span>
                      Die allgemeine Pruefung verwendet keine Werte. Erst die ausdrueckliche Vorschau erzeugt VN-Snapshots im Speicher.
                    </span>
                  </div>
                  <span className="readonly-marker">
                    <LockKeyhole size={16} aria-hidden="true" />
                    Nicht gespeichert
                  </span>
                </div>

                <section className="strategy-context-action" aria-label="Snapshot-Kontext anlegen">
                  <div>
                    <strong>Kontext aus den offenen Bauplanfeldern anlegen</strong>
                    <span>Jeder Eintrag bleibt leer, bis ein Wert eingegeben oder bewusst als offen markiert wird.</span>
                  </div>
                  {strategySnapshotContextEntries.length === 0 ? (
                    <button
                      className="primary-action"
                      type="button"
                      disabled={!canInitializeStrategySnapshotContext}
                      onClick={initializeStrategySnapshotContext}
                    >
                      <Plus size={17} aria-hidden="true" />
                      Kontext anlegen
                    </button>
                  ) : (
                    <button
                      className="secondary-action"
                      type="button"
                      onClick={discardStrategySnapshotContext}
                    >
                      <X size={17} aria-hidden="true" />
                      Kontext verwerfen
                    </button>
                  )}
                </section>

                {!strategyDraftValidation?.valid ? (
                  <div className="strategy-snapshot-prerequisite">
                    <ClipboardCheck size={20} aria-hidden="true" />
                    <div>
                      <strong>Zuerst den Entwurf erfolgreich pruefen</strong>
                      <span>Der Kontext bleibt atomar an den gueltigen Strategieentwurf gebunden.</span>
                    </div>
                  </div>
                ) : !strategySnapshotTranslation?.translation_complete ? (
                  <div className="strategy-snapshot-prerequisite">
                    <Boxes size={20} aria-hidden="true" />
                    <div>
                      <strong>Zuerst die Snapshot-Bauplaene anzeigen</strong>
                      <span>Die offene Feldmenge wird unveraendert aus der Bauplanvorschau uebernommen.</span>
                    </div>
                  </div>
                ) : strategySnapshotContextEntries.length === 0 ? (
                  <div className="strategy-snapshot-prerequisite ready">
                    <Database size={20} aria-hidden="true" />
                    <div>
                      <strong>{strategySnapshotTranslation.entries.length} Bauplaene sind bereit</strong>
                      <span>Der Kontext wird erst nach der ausdruecklichen Aktion lokal angelegt.</span>
                    </div>
                  </div>
                ) : (
                  <>
                    <section className="strategy-context-period" aria-label="Kontextperiode">
                      <label>
                        <span>Periode</span>
                        <input
                          aria-label="Periode des Snapshot-Kontexts"
                          type="number"
                          min="1"
                          step="1"
                          value={strategySnapshotContextPeriod}
                          onChange={(event) => {
                            setStrategySnapshotContextPeriod(event.target.value);
                            invalidateStrategySnapshotContextValidation();
                          }}
                          placeholder="z. B. 1"
                        />
                      </label>
                      <div>
                        <strong>Genau eine positive IMS-Periode</strong>
                        <span>
                          Aktivierungsperiode, Laufgrenze und Logtime werden nicht als Kontextperiode umgedeutet.
                        </span>
                      </div>
                      <span className={strategySnapshotContextPeriodValue ? "valid" : "open"}>
                        {strategySnapshotContextPeriodValue ? "gesetzt" : "erforderlich"}
                      </span>
                    </section>

                    <div className="strategy-context-list" aria-label="Kontexteintraege">
                      {strategySnapshotContextEntries.map((entry, entryIndex) => {
                        const actorLabel = entry.actor_type === "insurer" ? "VU" : "VN";
                        const strategy = strategyDefinitionById.get(entry.strategy_id);
                        const entryValueCount = Object.values(entry.values).filter(
                          (value) => value.explicitlyOpen || Boolean(value.raw.trim())
                        ).length;
                        const entryPath = `$.context.entries[${entryIndex}]`;
                        const entryIssueCount = strategySnapshotContextValidation?.issues.filter(
                          (issue) => issue.path.startsWith(entryPath)
                        ).length ?? 0;
                        return (
                          <details
                            className="strategy-context-entry"
                            key={`${entry.actor_type}-${entry.target_id}`}
                          >
                            <summary>
                              <div>
                                <strong>
                                  {actorLabel} {entry.target_id} · {strategy?.display_name ?? entry.strategy_id}
                                </strong>
                                <span>{entry.strategy_id}</span>
                              </div>
                              <span className={entryIssueCount > 0 ? "invalid" : "open"}>
                                {entryValueCount} / {Object.keys(entry.values).length} Werte
                              </span>
                            </summary>
                            <div className="strategy-context-entry-body">
                              {(strategySnapshotContextContract?.source_categories ?? []).map((source) => {
                                const fieldNames = Object.keys(entry.values).filter(
                                  (fieldName) => strategySnapshotContextFieldByName.get(fieldName)?.source === source
                                );
                                if (fieldNames.length === 0) {
                                  return null;
                                }
                                return (
                                  <section className="strategy-context-source" key={source}>
                                    <div className="strategy-context-source-heading">
                                      <div>
                                        <strong>{strategySnapshotContextSourceLabels[source]}</strong>
                                        <span>{strategySnapshotContextSourceDescriptions[source]}</span>
                                      </div>
                                      <small>{fieldNames.length} Felder</small>
                                    </div>
                                    {fieldNames.map((fieldName) => {
                                      const definition = strategySnapshotContextFieldByName.get(fieldName);
                                      const editorValue = entry.values[fieldName];
                                      if (!definition || !editorValue) {
                                        return null;
                                      }
                                      const fieldPath = `${entryPath}.values.${fieldName}`;
                                      const fieldIssues = strategySnapshotContextValidation?.issues.filter(
                                        (issue) => issue.path === fieldPath
                                      ) ?? [];
                                      const inputLabel = `${strategySnapshotFieldLabel(fieldName)} fuer ${actorLabel} ${entry.target_id}`;
                                      return (
                                        <div
                                          className={`strategy-context-field ${fieldIssues.length > 0 ? "invalid" : ""}`}
                                          key={fieldName}
                                        >
                                          <div className="strategy-context-field-name">
                                            <strong>{strategySnapshotFieldLabel(fieldName)}</strong>
                                            <small>{fieldName}</small>
                                            <span>{strategySnapshotContextShapeLabel(definition)}</span>
                                          </div>
                                          <div className="strategy-context-field-control">
                                            {definition.value_shape === "boolean" ? (
                                              <select
                                                aria-label={inputLabel}
                                                disabled={editorValue.explicitlyOpen}
                                                value={editorValue.raw}
                                                onChange={(event) => updateStrategySnapshotContextValue(
                                                  entryIndex,
                                                  fieldName,
                                                  { raw: event.target.value }
                                                )}
                                              >
                                                <option value="">Bitte waehlen</option>
                                                <option value="false">Nein</option>
                                                <option value="true">Ja</option>
                                              </select>
                                            ) : definition.value_shape === "finite_number" ||
                                                definition.value_shape === "integer" ? (
                                              <input
                                                aria-label={inputLabel}
                                                type="number"
                                                step={definition.value_shape === "integer" ? "1" : "any"}
                                                disabled={editorValue.explicitlyOpen}
                                                value={editorValue.raw}
                                                onChange={(event) => updateStrategySnapshotContextValue(
                                                  entryIndex,
                                                  fieldName,
                                                  { raw: event.target.value }
                                                )}
                                                placeholder={strategySnapshotContextPlaceholder(definition)}
                                              />
                                            ) : (
                                              <textarea
                                                aria-label={inputLabel}
                                                rows={definition.value_shape === "object" ? 3 : 2}
                                                disabled={editorValue.explicitlyOpen}
                                                value={editorValue.raw}
                                                onChange={(event) => updateStrategySnapshotContextValue(
                                                  entryIndex,
                                                  fieldName,
                                                  { raw: event.target.value }
                                                )}
                                                placeholder={strategySnapshotContextPlaceholder(definition)}
                                                spellCheck={false}
                                              />
                                            )}
                                            {fieldIssues.map((issue) => (
                                              <span className="strategy-context-field-error" key={issue.code}>
                                                {issue.message}
                                              </span>
                                            ))}
                                          </div>
                                          {definition.nullable ? (
                                            <label className="strategy-context-null-toggle">
                                              <input
                                                type="checkbox"
                                                checked={editorValue.explicitlyOpen}
                                                onChange={(event) => updateStrategySnapshotContextValue(
                                                  entryIndex,
                                                  fieldName,
                                                  { explicitlyOpen: event.target.checked }
                                                )}
                                              />
                                              <span>Bewusst offen</span>
                                              <small><code>null</code> bleibt unaufgeloest</small>
                                            </label>
                                          ) : (
                                            <span className="strategy-context-required">Pflichtwert</span>
                                          )}
                                        </div>
                                      );
                                    })}
                                  </section>
                                );
                              })}
                            </div>
                          </details>
                        );
                      })}
                    </div>

                    <section className="strategy-draft-validation strategy-context-validation" aria-label="Kontext pruefen">
                      <div className="strategy-draft-validation-action">
                        <div>
                          <strong>Serverseitige Kontextpruefung</strong>
                          <span>Prueft Periode, Zielbindung, Feldmenge und eindeutige Wertformen atomar.</span>
                        </div>
                        <button
                          className="primary-action"
                          type="button"
                          disabled={!canValidateStrategySnapshotContext}
                          onClick={validateStrategySnapshotContext}
                        >
                          <ClipboardCheck size={17} aria-hidden="true" />
                          {strategySnapshotContextValidationState === "loading"
                            ? "Pruefung laeuft"
                            : "Kontext pruefen"}
                        </button>
                      </div>
                      {strategySnapshotContextValidationError ? (
                        <div className="empty-state" role="alert">
                          {strategySnapshotContextValidationError}
                        </div>
                      ) : strategySnapshotContextValidation ? (
                        <div className={`strategy-draft-report ${strategySnapshotContextValidation.valid ? "valid" : "invalid"}`}>
                          <div className="strategy-draft-report-summary">
                            {strategySnapshotContextValidation.valid ? (
                              <CheckCircle2 size={20} aria-hidden="true" />
                            ) : (
                              <CircleAlert size={20} aria-hidden="true" />
                            )}
                            <div>
                              <strong>
                                {strategySnapshotContextValidation.valid
                                  ? "Kontext ist formal gueltig"
                                  : "Kontext enthaelt Fehler"}
                              </strong>
                              <span>
                                {strategySnapshotContextValidation.resolved_value_count} von {strategySnapshotContextValidation.expected_value_count} Werten gesetzt
                                {strategySnapshotContextValidation.explicitly_open_value_count > 0
                                  ? `, ${strategySnapshotContextValidation.explicitly_open_value_count} bewusst offen`
                                  : ""}
                              </span>
                            </div>
                          </div>
                          {strategySnapshotContextValidation.issues.length > 0 ? (
                            <div className="strategy-draft-issues">
                              {strategySnapshotContextValidation.issues.map((issue) => (
                                <div key={`${issue.path}-${issue.code}`}>
                                  <strong>{issue.path}</strong>
                                  <span>{issue.message}</span>
                                </div>
                              ))}
                            </div>
                          ) : null}
                          <div className="strategy-context-report-boundaries">
                            <span>Defaults: {strategySnapshotContextValidation.defaults_applied ? "ja" : "nein"}</span>
                            <span>Werte verwendet: {strategySnapshotContextValidation.context_values_consumed ? "ja" : "nein"}</span>
                            <span>Loader: {strategySnapshotContextValidation.snapshot_loader_invocation_performed ? "ja" : "nein"}</span>
                            <span>Snapshots: {strategySnapshotContextValidation.snapshots_created ? "ja" : "nein"}</span>
                            <span>Ausfuehrung: {strategySnapshotContextValidation.execution_performed ? "ja" : "nein"}</span>
                            <span>Simulation: {strategySnapshotContextValidation.simulation_performed ? "ja" : "nein"}</span>
                          </div>
                        </div>
                      ) : null}
                    </section>

                    {strategySnapshotContextValidation?.valid ? (
                      <section
                        className="strategy-context-action strategy-materialization-action"
                        aria-label="VN-Snapshot-Vorschau erzeugen"
                      >
                        <div>
                          <strong>VN-Snapshots im Speicher erzeugen</strong>
                          <span>
                            Prueft die strengeren VN-Wertformen und zeigt nur bei vollstaendigem Erfolg eine Vorschau.
                          </span>
                        </div>
                        <button
                          className="primary-action"
                          type="button"
                          disabled={!canMaterializeStrategySnapshots}
                          onClick={materializeStrategySnapshots}
                        >
                          <Eye size={17} aria-hidden="true" />
                          {strategySnapshotMaterializationState === "loading"
                            ? "Snapshots werden erzeugt"
                            : "VN-Snapshots anzeigen"}
                        </button>
                      </section>
                    ) : null}
                    {strategySnapshotMaterializationError ? (
                      <div className="empty-state" role="alert">
                        {strategySnapshotMaterializationError}
                      </div>
                    ) : strategySnapshotMaterialization && !strategySnapshotMaterialization.materialization_complete ? (
                      <div className="strategy-draft-report invalid strategy-materialization-errors" role="alert">
                        <div className="strategy-draft-report-summary">
                          <CircleAlert size={20} aria-hidden="true" />
                          <div>
                            <strong>VN-Snapshots noch nicht erzeugt</strong>
                            <span>Die strengere Materialisierungspruefung meldet {strategySnapshotMaterialization.issue_count} Fehler.</span>
                          </div>
                        </div>
                        <div className="strategy-draft-issues">
                          {strategySnapshotMaterialization.issues.map((issue) => (
                            <div key={`${issue.stage}-${issue.path}-${issue.code}`}>
                              <strong>{issue.path}</strong>
                              <span>{issue.message}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    ) : null}
                  </>
                )}
              </div>
            )
          ) : strategyWorkbenchView === "translation" ? (
            strategySnapshotTranslationContractState === "error" ? (
              <div className="empty-state" role="alert">{strategySnapshotTranslationContractError}</div>
            ) : strategySnapshotTranslationContractState === "loading" ? (
              <div className="empty-state">Snapshot-Bauplanvertrag wird geladen</div>
            ) : (
              <div
                className="strategy-contract-view strategy-snapshot-view"
                data-testid="strategy-snapshot-translation-preview"
              >
                <div className="strategy-contract-summary" aria-label="Snapshot-Bauplan-Status">
                  <div>
                    <span>Uebersetzungsvertrag</span>
                    <strong>{strategySnapshotTranslationContract?.schema_version ?? "-"}</strong>
                  </div>
                  <div>
                    <span>Regel-Mappings</span>
                    <strong>{strategySnapshotTranslationContract?.strategy_mappings.length ?? 0}</strong>
                  </div>
                  <div>
                    <span>Bauplaene</span>
                    <strong>{strategySnapshotTranslation?.translated_assignment_count ?? 0}</strong>
                  </div>
                  <div>
                    <span>Offene Werte</span>
                    <strong>{strategySnapshotOpenFieldCount}</strong>
                  </div>
                </div>

                <div className="strategy-boundary-band">
                  <div>
                    <strong>Strukturelle Vorschau, noch nicht ausfuehrbar</strong>
                    <span>
                      Unbekannte Laufzeitwerte bleiben offen. Es werden keine Defaults eingesetzt und keine Snapshots erzeugt.
                    </span>
                  </div>
                  <span className="readonly-marker">
                    <LockKeyhole size={16} aria-hidden="true" />
                    Keine Materialisierung
                  </span>
                </div>

                <section className="strategy-snapshot-action" aria-label="Snapshot-Bauplaene anzeigen">
                  <div>
                    <strong>Geprueften Entwurf uebersetzen</strong>
                    <span>
                      Die Vorschau ordnet den lokalen Entwurf vorhandenen Regel-Snapshottypen zu.
                    </span>
                  </div>
                  <button
                    className="primary-action"
                    type="button"
                    disabled={!canTranslateStrategyDraft}
                    onClick={translateStrategyDraft}
                  >
                    <Eye size={17} aria-hidden="true" />
                    {strategySnapshotTranslationState === "loading"
                      ? "Bauplaene werden erstellt"
                      : "Bauplaene anzeigen"}
                  </button>
                </section>

                {!strategyDraftValidation?.valid ? (
                  <div className="strategy-snapshot-prerequisite">
                    <ClipboardCheck size={20} aria-hidden="true" />
                    <div>
                      <strong>Zuerst den Entwurf erfolgreich pruefen</strong>
                      <span>Die Vorschau verwendet nur einen unveraenderten, gueltigen Entwurf aus dem Tab Entwurf.</span>
                    </div>
                  </div>
                ) : strategySnapshotTranslationError ? (
                  <div className="empty-state" role="alert">{strategySnapshotTranslationError}</div>
                ) : strategySnapshotTranslationState === "loading" ? (
                  <div className="empty-state">Snapshot-Bauplaene werden erstellt</div>
                ) : strategySnapshotTranslation ? (
                  strategySnapshotTranslation.translation_complete ? (
                    <div className="strategy-snapshot-list" aria-label="Snapshot-Bauplanvorschau">
                      <div className="strategy-snapshot-list-heading">
                        <div>
                          <h3>{strategySnapshotTranslation.label}</h3>
                          <span>{strategySnapshotTranslation.draft_id}</span>
                        </div>
                        <strong>{strategySnapshotTranslationStatusLabel}</strong>
                      </div>
                      {strategySnapshotTranslation.entries.map((entry) => {
                        const strategy = strategyDefinitionById.get(entry.strategy_id);
                        const actorLabel = entry.actor_type === "insurer" ? "VU" : "VN";
                        return (
                          <article
                            className="strategy-snapshot-row"
                            key={`${entry.actor_type}-${entry.target_id}`}
                          >
                            <div className="strategy-snapshot-row-heading">
                              <div>
                                <strong>{actorLabel} {entry.target_id} · {strategy?.display_name ?? entry.strategy_id}</strong>
                                <span>{entry.strategy_id}</span>
                              </div>
                              <span className="strategy-snapshot-open-marker">
                                <CircleAlert size={16} aria-hidden="true" />
                                Kontext offen
                              </span>
                            </div>

                            <div className="strategy-snapshot-meta">
                              <div>
                                <span>Snapshottyp</span>
                                <strong>{entry.snapshot_type}</strong>
                              </div>
                              <div>
                                <span>Zeitbindung</span>
                                <strong>ab Periode {entry.activation_period}, bis Lauf {entry.active_through_run}</strong>
                                <small>Logtime {entry.logical_time}</small>
                              </div>
                              <div>
                                <span>Zielcontainer</span>
                                <strong>{entry.snapshot_collection}</strong>
                              </div>
                            </div>

                            <div className="strategy-snapshot-fields">
                              <section aria-label={`Vorbereitete Werte fuer ${actorLabel} ${entry.target_id}`}>
                                <div className="strategy-snapshot-field-heading prepared">
                                  <CheckCircle2 size={17} aria-hidden="true" />
                                  <strong>Aus dem Entwurf vorbereitet</strong>
                                </div>
                                <ul>
                                  {entry.provided_snapshot_fields.map((fieldName) => (
                                    <li key={fieldName}>
                                      <span>{strategySnapshotFieldLabel(fieldName)}</span>
                                      <small>{fieldName}</small>
                                    </li>
                                  ))}
                                </ul>
                              </section>
                              <section aria-label={`Offene Laufzeitwerte fuer ${actorLabel} ${entry.target_id}`}>
                                <div className="strategy-snapshot-field-heading open">
                                  <CircleAlert size={17} aria-hidden="true" />
                                  <strong>Vor Materialisierung erforderlich</strong>
                                </div>
                                <ul>
                                  {entry.unresolved_snapshot_fields.map((fieldName) => (
                                    <li key={fieldName}>
                                      <span>{strategySnapshotFieldLabel(fieldName)}</span>
                                      <small>{fieldName}</small>
                                    </li>
                                  ))}
                                </ul>
                              </section>
                            </div>
                          </article>
                        );
                      })}
                      <div className="strategy-draft-report-boundaries">
                        <span>Defaults: {strategySnapshotTranslation.defaults_applied ? "ja" : "nein"}</span>
                        <span>Snapshots: {strategySnapshotTranslation.snapshots_created ? "ja" : "nein"}</span>
                        <span>Ausfuehrung: {strategySnapshotTranslation.execution_performed ? "ja" : "nein"}</span>
                        <span>Simulation: {strategySnapshotTranslation.simulation_performed ? "ja" : "nein"}</span>
                      </div>
                    </div>
                  ) : (
                    <div className="strategy-draft-report invalid">
                      <div className="strategy-draft-report-summary">
                        <CircleAlert size={20} aria-hidden="true" />
                        <div>
                          <strong>Bauplaene konnten nicht vollstaendig zugeordnet werden</strong>
                          <span>{strategySnapshotTranslation.issue_count} Vertragsfehler</span>
                        </div>
                      </div>
                      <div className="strategy-draft-issues">
                        {strategySnapshotTranslation.issues.map((issue) => (
                          <div key={`${issue.path}-${issue.code}`}>
                            <strong>{issue.path}</strong>
                            <span>{issue.message}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )
                ) : (
                  <div className="strategy-snapshot-prerequisite ready">
                    <Boxes size={20} aria-hidden="true" />
                    <div>
                      <strong>Entwurf ist bereit fuer die Vorschau</strong>
                      <span>Bauplaene werden erst nach dem ausdruecklichen Anzeigen berechnet.</span>
                    </div>
                  </div>
                )}
              </div>
            )
          ) : strategyDraftContractState === "error" ? (
            <div className="empty-state" role="alert">{strategyDraftContractError}</div>
          ) : strategyDraftContractState === "loading" ? (
            <div className="empty-state">Strategieentwurfsformat wird geladen</div>
          ) : (
            <div className="strategy-contract-view strategy-draft-view" data-testid="strategy-assignment-draft-editor">
              <div className="strategy-contract-summary" aria-label="Strategieentwurf-Status">
                <div>
                  <span>Entwurfsformat</span>
                  <strong>{strategyDraftContract?.schema_version ?? "-"}</strong>
                </div>
                <div>
                  <span>Basismodell</span>
                  <strong>{strategyDraftContract?.base_model ?? "-"}</strong>
                </div>
                <div>
                  <span>Zuordnungen</span>
                  <strong>{strategyDraftAssignments.length}</strong>
                </div>
                <div>
                  <span>Pruefstatus</span>
                  <strong>{strategyDraftValidationLabel}</strong>
                </div>
              </div>

              <div className="strategy-boundary-band">
                <div>
                  <strong>Lokaler Entwurf im aktuellen Browserfenster</strong>
                  <span>
                    Die Pruefung speichert nichts und erzeugt weder Regel-Snapshots noch einen Simulationslauf.
                  </span>
                </div>
                <span className="readonly-marker">
                  <LockKeyhole size={16} aria-hidden="true" />
                  Nicht gespeichert
                </span>
              </div>

              <div className="strategy-draft-metadata" aria-label="Entwurfskopf">
                <label>
                  <span>Entwurfs-ID</span>
                  <input
                    type="text"
                    value={strategyDraftId}
                    onChange={(event) => {
                      setStrategyDraftId(event.target.value);
                      invalidateStrategyDraftValidation();
                    }}
                    placeholder="z. B. marktvergleich-01"
                  />
                </label>
                <label>
                  <span>Bezeichnung</span>
                  <input
                    type="text"
                    value={strategyDraftLabel}
                    onChange={(event) => {
                      setStrategyDraftLabel(event.target.value);
                      invalidateStrategyDraftValidation();
                    }}
                    placeholder="Bezeichnung des Entwurfs"
                  />
                </label>
              </div>

              <section className="strategy-draft-editor" aria-label="Strategiezuordnung erfassen">
                <div className="strategy-draft-section-heading">
                  <div>
                    <h3>{strategyDraftEditingIndex === null ? "Zuordnung erfassen" : "Zuordnung bearbeiten"}</h3>
                    <span>Ein Akteur, eine Strategie und die vorhandenen technischen Zeitangaben.</span>
                  </div>
                  {strategyDraftEditingIndex !== null ? <strong>Eintrag {strategyDraftEditingIndex + 1}</strong> : null}
                </div>

                <div className="strategy-draft-actor" role="group" aria-label="Akteurstyp">
                  {STRATEGY_ACTOR_ORDER.map((actorType) => (
                    <button
                      className={strategyDraftEditor.actorType === actorType ? "active" : ""}
                      type="button"
                      aria-pressed={strategyDraftEditor.actorType === actorType}
                      onClick={() => selectStrategyDraftActor(actorType)}
                      key={actorType}
                    >
                      {strategyActorLabel(actorType)}
                    </button>
                  ))}
                </div>

                <div className="strategy-draft-fields">
                  <label>
                    <span>Ziel-ID</span>
                    <input
                      aria-label="Ziel-ID"
                      type="number"
                      min={strategyDraftTargetLimit?.minimum ?? 1}
                      max={strategyDraftTargetLimit?.maximum}
                      step="1"
                      value={strategyDraftEditor.targetId}
                      onChange={(event) => setStrategyDraftEditor((current) => ({
                        ...current,
                        targetId: event.target.value
                      }))}
                      placeholder={strategyDraftTargetLimit
                        ? `${strategyDraftTargetLimit.minimum}-${strategyDraftTargetLimit.maximum}`
                        : "ID"}
                    />
                    <small>
                      {strategyDraftTargetDuplicate
                        ? "Dieser Akteur ist bereits zugeordnet."
                        : strategyDraftTargetLimit
                          ? `Zulaessig: ${strategyDraftTargetLimit.minimum}-${strategyDraftTargetLimit.maximum}`
                          : "Zielgrenze wird geladen"}
                    </small>
                  </label>
                  <label className="strategy-draft-strategy-field">
                    <span>Strategie</span>
                    <select
                      aria-label="Strategie"
                      value={strategyDraftEditor.strategyId}
                      onChange={(event) => selectStrategyDraftStrategy(event.target.value)}
                    >
                      <option value="">Strategie waehlen</option>
                      {strategyDraftEligibleStrategies.map((strategy) => (
                        <option value={strategy.strategy_id} key={strategy.strategy_id}>
                          {strategy.display_name}
                        </option>
                      ))}
                    </select>
                    <small>{selectedStrategyDraftDefinition?.strategy_id ?? "Noch keine Strategie ausgewaehlt"}</small>
                  </label>
                  <label>
                    <span>Aktiv ab Periode</span>
                    <input
                      type="number"
                      min="1"
                      step="1"
                      value={strategyDraftEditor.activationPeriod}
                      onChange={(event) => setStrategyDraftEditor((current) => ({
                        ...current,
                        activationPeriod: event.target.value
                      }))}
                      placeholder="Periode"
                    />
                  </label>
                  <label>
                    <span>Aktiv bis Lauf</span>
                    <input
                      type="number"
                      min="1"
                      step="1"
                      value={strategyDraftEditor.activeThroughRun}
                      onChange={(event) => setStrategyDraftEditor((current) => ({
                        ...current,
                        activeThroughRun: event.target.value
                      }))}
                      placeholder="Laufgrenze"
                    />
                  </label>
                  <label>
                    <span>Logische Zeit</span>
                    <input
                      type="number"
                      min="1"
                      step="1"
                      value={strategyDraftEditor.logicalTime}
                      onChange={(event) => setStrategyDraftEditor((current) => ({
                        ...current,
                        logicalTime: event.target.value
                      }))}
                      placeholder="Zeitpunkt"
                    />
                  </label>
                </div>

                {selectedStrategyDraftDefinition ? (
                  selectedStrategyDraftSchema ? (
                    <div className="strategy-draft-parameters" aria-label="Strategieparameter">
                      <div className="strategy-draft-parameter-head">
                        <div>
                          <strong>Strategieparameter</strong>
                          <small>{selectedStrategyDraftSchema.schema_id}</small>
                        </div>
                        <span>Historische Position 1</span>
                        <span>Historische Position 2</span>
                      </div>
                      {selectedStrategyDraftSchema.fields.map((field) => {
                        const values = strategyDraftEditor.parameterValues[field.field_name] ?? ["", ""];
                        return (
                          <div className="strategy-draft-parameter-row" key={field.field_name}>
                            <div>
                              <strong>{field.display_name}</strong>
                              <small>{field.field_name}</small>
                            </div>
                            {[0, 1].map((position) => (
                              <label key={position}>
                                <span>Position {position + 1}</span>
                                <input
                                  aria-label={`${field.display_name}, Position ${position + 1}`}
                                  type="number"
                                  min={field.python_type === "list[int]" ? "0" : undefined}
                                  step={field.python_type === "list[int]" ? "1" : "any"}
                                  value={values[position]}
                                  onChange={(event) => setStrategyDraftEditor((current) => {
                                    const currentValues = current.parameterValues[field.field_name] ?? ["", ""];
                                    const nextValues = position === 0
                                      ? [event.target.value, currentValues[1]]
                                      : [currentValues[0], event.target.value];
                                    return {
                                      ...current,
                                      parameterValues: {
                                        ...current.parameterValues,
                                        [field.field_name]: nextValues as [string, string]
                                      }
                                    };
                                  })}
                                />
                              </label>
                            ))}
                          </div>
                        );
                      })}
                    </div>
                  ) : (
                    <div className="strategy-draft-no-parameters">
                      <strong>Keine Strategieparameter</strong>
                      <span>Diese Regel besitzt im vorhandenen Vertrag keinen Parameterblock.</span>
                    </div>
                  )
                ) : null}

                <div className="strategy-draft-editor-actions">
                  <button className="secondary-action" type="button" onClick={resetStrategyDraftEditor}>
                    <X size={17} aria-hidden="true" />
                    {strategyDraftEditingIndex === null ? "Eingaben leeren" : "Bearbeitung abbrechen"}
                  </button>
                  <button
                    className="primary-action"
                    type="button"
                    disabled={!canApplyStrategyDraftAssignment}
                    onClick={applyStrategyDraftAssignment}
                  >
                    <Plus size={17} aria-hidden="true" />
                    {strategyDraftEditingIndex === null ? "Zuordnung uebernehmen" : "Aenderung uebernehmen"}
                  </button>
                </div>
              </section>

              <section className="strategy-draft-assignments" aria-label="Erfasste Zuordnungen">
                <div className="strategy-draft-section-heading">
                  <div>
                    <h3>Erfasste Zuordnungen</h3>
                    <span>Nur im aktuellen Browserzustand.</span>
                  </div>
                  <strong>{strategyDraftAssignments.length}</strong>
                </div>
                {strategyDraftAssignments.length === 0 ? (
                  <div className="empty-state">Noch keine Zuordnung erfasst</div>
                ) : (
                  <div className="strategy-draft-table" role="table" aria-label="Strategieentwurf-Zuordnungen">
                    <div className="strategy-draft-table-head" role="row">
                      <span role="columnheader">Akteur</span>
                      <span role="columnheader">Strategie</span>
                      <span role="columnheader">Zeit</span>
                      <span role="columnheader">Parameter</span>
                      <span role="columnheader">Aktionen</span>
                    </div>
                    {strategyDraftAssignments.map((assignment, index) => (
                      <div className="strategy-draft-table-row" role="row" key={`${assignment.actor_type}-${assignment.target_id}`}>
                        <div role="cell">
                          <strong>{assignment.actor_type === "insurer" ? "VU" : "VN"} {assignment.target_id}</strong>
                          <small>{strategyActorLabel(assignment.actor_type)}</small>
                        </div>
                        <div role="cell">
                          <strong>{strategyDefinitionById.get(assignment.strategy_id)?.display_name ?? assignment.strategy_id}</strong>
                          <small>{assignment.strategy_id}</small>
                        </div>
                        <div role="cell">
                          <strong>Periode {assignment.activation_period}</strong>
                          <small>bis Lauf {assignment.active_through_run} · Logtime {assignment.logical_time}</small>
                        </div>
                        <div role="cell">
                          <strong>{assignment.parameter_schema ? `${Object.keys(assignment.parameter_values ?? {}).length} Felder` : "ohne Parameter"}</strong>
                          <small>{assignment.parameter_schema ?? "kein Schema"}</small>
                        </div>
                        <div className="strategy-draft-row-actions" role="cell">
                          <button
                            type="button"
                            title="Zuordnung bearbeiten"
                            aria-label={`Zuordnung ${index + 1} bearbeiten`}
                            onClick={() => editStrategyDraftAssignment(index)}
                          >
                            <Pencil size={16} aria-hidden="true" />
                          </button>
                          <button
                            type="button"
                            title="Zuordnung entfernen"
                            aria-label={`Zuordnung ${index + 1} entfernen`}
                            onClick={() => removeStrategyDraftAssignment(index)}
                          >
                            <Trash2 size={16} aria-hidden="true" />
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </section>

              <section className="strategy-draft-validation" aria-label="Entwurf pruefen">
                <div className="strategy-draft-validation-action">
                  <div>
                    <strong>Serverseitige Vertragspruefung</strong>
                    <span>Prueft Struktur, Zielgrenzen und vorhandene Parameterloader.</span>
                  </div>
                  <button
                    className="primary-action"
                    type="button"
                    disabled={!canValidateStrategyDraft}
                    onClick={validateStrategyDraft}
                  >
                    <ClipboardCheck size={17} aria-hidden="true" />
                    {strategyDraftValidationState === "loading" ? "Pruefung laeuft" : "Entwurf pruefen"}
                  </button>
                </div>
                {strategyDraftValidationError ? (
                  <div className="empty-state" role="alert">{strategyDraftValidationError}</div>
                ) : strategyDraftValidation ? (
                  <div className={`strategy-draft-report ${strategyDraftValidation.valid ? "valid" : "invalid"}`}>
                    <div className="strategy-draft-report-summary">
                      <CheckCircle2 size={20} aria-hidden="true" />
                      <div>
                        <strong>{strategyDraftValidation.valid ? "Entwurf ist gueltig" : "Entwurf enthaelt Fehler"}</strong>
                        <span>
                          {strategyDraftValidation.validated_assignment_count} von {strategyDraftValidation.assignment_count} Zuordnungen geprueft
                        </span>
                      </div>
                    </div>
                    {strategyDraftValidation.issues.length > 0 ? (
                      <div className="strategy-draft-issues">
                        {strategyDraftValidation.issues.map((issue) => (
                          <div key={`${issue.path}-${issue.code}`}>
                            <strong>{issue.path}</strong>
                            <span>{issue.message}</span>
                          </div>
                        ))}
                      </div>
                    ) : null}
                    <div className="strategy-draft-report-boundaries">
                      <span>Speichern: {strategyDraftValidation.writes_performed ? "ja" : "nein"}</span>
                      <span>Snapshots: {strategyDraftValidation.snapshots_created ? "ja" : "nein"}</span>
                      <span>Ausfuehrung: {strategyDraftValidation.execution_performed ? "ja" : "nein"}</span>
                      <span>Simulation: {strategyDraftValidation.simulation_performed ? "ja" : "nein"}</span>
                    </div>
                  </div>
                ) : null}
              </section>
            </div>
          )}
        </section>

        <section className="panel scenario-overview-panel" aria-label="Szenario-Uebersicht">
          <div className="panel-heading">
            <FileText size={20} aria-hidden="true" />
            <h2>Szenario-Uebersicht</h2>
          </div>
          <div className="scenario-filterbar" aria-label="Szenariofilter">
            <label className="scenario-search">
              <Search size={17} aria-hidden="true" />
              <span>Suche</span>
              <input
                aria-label="Szenariosuche"
                onChange={(event) => setScenarioQuery(event.target.value)}
                placeholder="Name oder ID"
                type="search"
                value={scenarioQuery}
              />
            </label>
            <label>
              <span>Status</span>
              <select
                aria-label="Szenario-Statusfilter"
                onChange={(event) => setScenarioStatusFilter(event.target.value)}
                value={scenarioStatusFilter}
              >
                <option value={ALL_SCENARIO_FILTERS}>alle</option>
                {scenarioStatusOptions.map((status) => (
                  <option key={status} value={status}>
                    {status}
                  </option>
                ))}
              </select>
            </label>
            <label>
              <span>Quelle</span>
              <select
                aria-label="Szenario-Quellenfilter"
                onChange={(event) => setScenarioSourceFilter(event.target.value)}
                value={scenarioSourceFilter}
              >
                <option value={ALL_SCENARIO_FILTERS}>alle</option>
                {scenarioSourceOptions.map((source) => (
                  <option key={source} value={source}>
                    {source}
                  </option>
                ))}
              </select>
            </label>
            <label>
              <span>Umfang</span>
              <select
                aria-label="Szenario-Scopefilter"
                onChange={(event) => setScenarioScopeFilter(event.target.value)}
                value={scenarioScopeFilter}
              >
                <option value={ALL_SCENARIO_FILTERS}>alle</option>
                {scenarioScopeOptions.map((scope) => (
                  <option key={scope} value={scope}>
                    {scope}
                  </option>
                ))}
              </select>
            </label>
          </div>
          <p className="scenario-filter-count">
            {filteredScenarios.length} von {scenarios.length} Szenarien sichtbar
          </p>
          <div className="scenario-overview-table">
            <div className="scenario-overview-head" aria-hidden="true">
              <span>Szenario</span>
              <span>Umfang</span>
              <span>Quelle</span>
              <span>Validierung</span>
              <span>Aktualisiert</span>
              <span>Ausfuehrung</span>
            </div>
            {filteredScenarios.map((scenario) => (
              <button
                className={`scenario-overview-row ${scenario.id === selectedScenarioId ? "selected" : ""}`}
                key={scenario.id}
                type="button"
                onClick={() => setSelectedScenarioId(scenario.id)}
              >
                <span>
                  <strong>{scenario.display_name}</strong>
                  <small>{scenario.status}</small>
                </span>
                <span>{scenario.domain_scope}</span>
                <span>{scenario.source.label}</span>
                <span>{scenario.validation.scope}</span>
                <span>{scenario.updated_at}</span>
                <span>{executionLabel}</span>
              </button>
            ))}
          </div>
          {filteredScenarios.length === 0 ? (
            <div className="empty-state">Keine Szenarien fuer diesen Filter.</div>
          ) : null}
        </section>

        <section className="panel run-overview-panel" aria-label="Run-Uebersicht">
          <div className="panel-heading">
            <Archive size={20} aria-hidden="true" />
            <h2>Run-Uebersicht</h2>
          </div>
          <div className="run-filterbar" aria-label="Runfilter">
            <label className="run-search">
              <Search size={17} aria-hidden="true" />
              <span>Suche</span>
              <input
                aria-label="Runsuche"
                onChange={(event) => setRunQuery(event.target.value)}
                placeholder="Name oder ID"
                type="search"
                value={runQuery}
              />
            </label>
            <label>
              <span>Status</span>
              <select
                aria-label="Run-Statusfilter"
                onChange={(event) => setRunStatusFilter(event.target.value)}
                value={runStatusFilter}
              >
                <option value={ALL_RUN_FILTERS}>alle</option>
                {runStatusOptions.map((status) => (
                  <option key={status} value={status}>
                    {status}
                  </option>
                ))}
              </select>
            </label>
            <label>
              <span>Szenario</span>
              <select
                aria-label="Run-Szenariofilter"
                onChange={(event) => setRunScenarioFilter(event.target.value)}
                value={runScenarioFilter}
              >
                <option value={ALL_RUN_FILTERS}>alle</option>
                {runScenarioOptions.map((scenarioId) => (
                  <option key={scenarioId} value={scenarioId}>
                    {scenarioNameById.get(scenarioId) ?? scenarioId}
                  </option>
                ))}
              </select>
            </label>
            <label>
              <span>Quelle</span>
              <select
                aria-label="Run-Quellenfilter"
                onChange={(event) => setRunSourceFilter(event.target.value)}
                value={runSourceFilter}
              >
                <option value={ALL_RUN_FILTERS}>alle</option>
                {runSourceOptions.map((source) => (
                  <option key={source} value={source}>
                    {source}
                  </option>
                ))}
              </select>
            </label>
          </div>
          <p className="run-filter-count">
            {filteredRuns.length} von {runs.length} Runs sichtbar
          </p>
          <div className="run-overview-table">
            <div className="run-overview-head" aria-hidden="true">
              <span>Run</span>
              <span>Szenario</span>
              <span>Fenster</span>
              <span>Quelle</span>
              <span>Ausfuehrung</span>
            </div>
            {filteredRuns.map((run) => (
              <button
                className={`run-overview-row ${run.id === selectedRunId ? "selected" : ""}`}
                key={run.id}
                type="button"
                onClick={() => selectRun(run)}
              >
                <span>
                  <strong>{run.display_name}</strong>
                  <small>{run.status}</small>
                </span>
                <span>{scenarioNameById.get(run.scenario_id) ?? run.scenario_id}</span>
                <span>{run.period_window}</span>
                <span>{run.source.label}</span>
                <span>{run.execution_enabled ? "aktiv" : "gesperrt"}</span>
              </button>
            ))}
          </div>
          {filteredRuns.length === 0 ? (
            <div className="empty-state">Keine Runs fuer diesen Filter.</div>
          ) : null}
        </section>

        <section className="panel core-validation-panel" aria-label="Kernvalidierungsueberblick">
          <div className="panel-heading">
            <GitBranch size={20} aria-hidden="true" />
            <h2>Kernvalidierungsueberblick</h2>
          </div>
          <div className="core-validation-summary">
            {coreValidationRows.map(([label, value]) => (
              <div className="core-validation-summary-row" key={label}>
                <span>{label}</span>
                <strong>{value}</strong>
              </div>
            ))}
          </div>
          <div className="core-validation-contract" aria-label="Execution-Summary-Vertrag">
            {coreValidationContractRows.map(([label, value]) => (
              <div className="core-validation-contract-row" key={label}>
                <span>{label}</span>
                <strong>{value}</strong>
              </div>
            ))}
          </div>
        </section>

        <section
          className="panel carryover-probe-panel"
          aria-label="Carryover-Probe-Vertrag"
          data-testid="carryover-probe-contract"
        >
          <div className="panel-heading">
            <GitBranch size={20} aria-hidden="true" />
            <h2>Carryover-Probe-Vertrag</h2>
          </div>
          <div className="core-validation-summary">
            {carryoverProbeRows.map(([label, value]) => (
              <div className="core-validation-summary-row" key={label}>
                <span>{label}</span>
                <strong>{value}</strong>
              </div>
            ))}
          </div>
          <div className="core-validation-contract" aria-label="Carryover-Probe-Grenzen">
            {carryoverProbeBoundaryRows.map(([label, value]) => (
              <div className="core-validation-contract-row" key={label}>
                <span>{label}</span>
                <strong>{value}</strong>
              </div>
            ))}
          </div>
        </section>

        <section
          className="panel adapter-result-contract-panel"
          aria-label="Adapter-Resultat-Vertrag"
          data-testid="adapter-result-contract"
        >
          <div className="panel-heading">
            <Braces size={20} aria-hidden="true" />
            <h2>Adapter-Resultat-Vertrag</h2>
          </div>
          <div className="adapter-result-contract-grid" aria-label="Adapter-Resultat-Grenzen">
            {adapterResultContractRows.map(([label, value]) => (
              <div className="adapter-result-contract-row" key={label}>
                <span>{label}</span>
                <strong>{value}</strong>
              </div>
            ))}
          </div>
        </section>

        <section className="panel run-control-boundary-panel" aria-label="Run-Control-Statusband">
          <div className="panel-heading">
            <ShieldCheck size={20} aria-hidden="true" />
            <h2>Run-Control-Statusband</h2>
          </div>
          <div className="run-control-boundary-grid">
            {runControlBoundaryRows.map(([label, value]) => (
              <div className="run-control-boundary-row" key={label}>
                <span>{label}</span>
                <strong>{value}</strong>
              </div>
            ))}
          </div>
        </section>

        <section className="panel run-control-panel" aria-label="Run-Control-Uebersicht">
          <div className="panel-heading">
            <ServerCog size={20} aria-hidden="true" />
            <h2>Run-Control-Uebersicht</h2>
          </div>
          <div className="run-control-summary">
            {runControlQueueRows.map(([label, value]) => (
              <div className="run-control-summary-row" key={label}>
                <span>{label}</span>
                <strong>{value}</strong>
              </div>
            ))}
          </div>
          <p className="run-control-note">{runControlQueueIssue}</p>
          <div className="run-control-filterbar" aria-label="Run-Control-Queuefilter">
            <label className="run-control-search">
              <Search size={17} aria-hidden="true" />
              <span>Suche</span>
              <input
                aria-label="Run-Control-Queuesuche"
                onChange={(event) => setQueueQuery(event.target.value)}
                placeholder="Queue, Run oder Person"
                type="search"
                value={queueQuery}
              />
            </label>
            <label>
              <span>Status</span>
              <select
                aria-label="Run-Control-Statusfilter"
                onChange={(event) => setQueueStatusFilter(event.target.value)}
                value={queueStatusFilter}
              >
                <option value={ALL_QUEUE_FILTERS}>alle</option>
                {queueStatusOptions.map((status) => (
                  <option key={status} value={status}>
                    {status}
                  </option>
                ))}
              </select>
            </label>
            <label>
              <span>Szenario</span>
              <select
                aria-label="Run-Control-Szenariofilter"
                onChange={(event) => setQueueScenarioFilter(event.target.value)}
                value={queueScenarioFilter}
              >
                <option value={ALL_QUEUE_FILTERS}>alle</option>
                {queueScenarioOptions.map((scenarioId) => (
                  <option key={scenarioId} value={scenarioId}>
                    {scenarioNameById.get(scenarioId) ?? scenarioId}
                  </option>
                ))}
              </select>
            </label>
          </div>
          <p className="run-control-filter-count">
            {filteredQueueEntries.length} von {queueEntries.length} Queue-Eintraegen sichtbar
          </p>
          <div className="run-control-table">
            <div className="run-control-head" aria-hidden="true">
              <span>Queue</span>
              <span>Run</span>
              <span>Szenario</span>
              <span>Status</span>
              <span>Naechster Schritt</span>
              <span>Ausfuehrung</span>
            </div>
            {filteredQueueEntries.map((entry) => (
              <button
                className={`run-control-row ${entry.queue_id === selectedQueueId ? "selected" : ""}`}
                key={entry.queue_id}
                type="button"
                onClick={() => setSelectedQueueId(entry.queue_id)}
              >
                <span>
                  <strong>{entry.queue_id}</strong>
                  <small>{entry.request.requested_by}</small>
                </span>
                <span>{entry.request.run_id}</span>
                <span>{entry.request.scenario_id}</span>
                <span>{entry.status}</span>
                <span>{queueActionLabel(entry)}</span>
                <span>{entry.execution_enabled || entry.execution_performed ? "aktiv" : "gesperrt"}</span>
              </button>
            ))}
          </div>
          {queueEntries.length === 0 ? (
            <div className="empty-state">Keine Run-Control-Queue-Eintraege fuer diese Metadatenquelle.</div>
          ) : null}
          {queueEntries.length > 0 && filteredQueueEntries.length === 0 ? (
            <div className="empty-state">Keine Queue-Eintraege fuer diesen Filter.</div>
          ) : null}
          <div className="run-control-detail" aria-label="Run-Control-Queue-Detail">
            <div className="detail-status">
              <span>Queue-Detail</span>
              <strong>{queueDetailStatus}</strong>
            </div>
            <div className="run-control-detail-grid">
              {queueDetailRows.map(([label, value]) => (
                <div className="run-control-detail-row" key={label}>
                  <span>{label}</span>
                  <strong>{value}</strong>
                </div>
              ))}
            </div>
          </div>
          <div className="run-control-issues" aria-label="Run-Control-Queue-Hinweise">
            {runControlIssueRows.map(([severity, code, message]) => (
              <div className="run-control-issue-row" key={code}>
                <span>{severity}</span>
                <strong>{code}</strong>
                <small>{message}</small>
              </div>
            ))}
          </div>
        </section>

        <section className="panel import-panel" aria-label="Importvorschau">
          <div className="panel-heading">
            <Braces size={20} aria-hidden="true" />
            <h2>Importvorschau</h2>
          </div>
          <div className="import-grid">
            <article>
              <span>JSON-Struktur</span>
              <div className="shape-list">
                {importShapeRows.map(([field, meaning]) => (
                  <div className="shape-row" key={field}>
                    <code>{field}</code>
                    <strong>{meaning}</strong>
                  </div>
                ))}
              </div>
            </article>
            <article>
              <span>Grenzen</span>
              <ul className="boundary-list">
                <li>Import aktuell nur ueber Python-Adapter</li>
                <li>Preview lokal per CLI ohne Schreiben</li>
                <li>Snapshot lokal per CLI ohne Browser-Export</li>
                <li>Export lokal per CLI nur mit explizitem Zielpfad</li>
                <li>Roundtrip lokal per CLI ohne Schreiben</li>
                <li>Dry-Run lokal per CLI ohne Import</li>
                <li>Importbericht lokal per CLI nach explizitem Schreiben</li>
                <li>Startdiagnose lokal per CLI ohne Serverstart</li>
                <li>Startplan lokal per CLI nur beschreibend</li>
                <li>Readiness lokal per CLI ohne Serverstart</li>
                <li>v1-Readiness als lokaler Abschluss-Smoke</li>
                <li>CLI-Uebersicht lokal per CLI ohne Seiteneffekte</li>
                <li>Schreibvertrag lokal per CLI nur beschreibend</li>
                <li>Schreibvertragspruefung lokal per CLI ohne Import</li>
                <li>Run-Control-Vertrag lokal per CLI ohne Ausfuehrung</li>
                <li>Run-Control-Preflight lokal per CLI ohne Ausfuehrung</li>
                <li>Run-Control-Request-Vertrag per API nur lesend</li>
                <li>Run-Control-Dry-Run per API pruefend ohne Ausfuehrung</li>
                <li><code>execution_enabled</code> bleibt <code>false</code></li>
                <li>Browser schreibt keine Metadaten</li>
              </ul>
            </article>
          </div>
        </section>

        <section
          className="panel run-control-dry-run-panel"
          aria-label="Run-Control-Dry-Run-Vertrag"
          data-testid="run-control-demo-dry-run-panel"
        >
          <div className="panel-heading">
            <CircleDot size={20} aria-hidden="true" />
            <h2>Run-Control-Dry-Run-Vertrag</h2>
          </div>
          <div className="run-control-dry-run-actions">
            <button
              className="secondary-action"
              data-testid="run-control-demo-dry-run-button"
              disabled={!selectedRun || runControlDryRunState === "loading"}
              type="button"
              onClick={checkRunControlDryRun}
            >
              <ShieldCheck size={17} aria-hidden="true" />
              Dry-Run pruefen
            </button>
            <button
              className="secondary-action"
              data-testid="run-control-demo-queue-button"
              disabled={!canEnqueueRunControlQueue || runControlQueueEnqueueState === "loading"}
              type="button"
              onClick={enqueueRunControlQueue}
            >
              <Database size={17} aria-hidden="true" />
              Queue vormerken
            </button>
          </div>
          <div className="run-control-dry-run-grid">
            {runControlDryRunRows.map(([label, value]) => (
              <div className="run-control-dry-run-row" key={label}>
                <span>{label}</span>
                <strong>{value}</strong>
              </div>
            ))}
          </div>
          <div
            className="run-control-dry-run-result-grid"
            aria-label="Run-Control-Dry-Run-Ergebnis"
            data-testid="run-control-demo-dry-run-result"
          >
            {runControlDryRunResultRows.map(([label, value]) => (
              <div className="run-control-dry-run-result-row" key={label}>
                <span>{label}</span>
                <strong>{value}</strong>
              </div>
            ))}
          </div>
          <div
            className="run-control-queue-enqueue-grid"
            aria-label="Run-Control-Queue-Vormerkung"
            data-testid="run-control-demo-queue-result"
          >
            {runControlQueueEnqueueRows.map(([label, value]) => (
              <div className="run-control-queue-enqueue-row" key={label}>
                <span>{label}</span>
                <strong>{value}</strong>
              </div>
            ))}
          </div>
        </section>

        <section
          className="panel run-control-action-plan-panel"
          aria-label="Run-Control-Aktionsplan"
          data-testid="run-control-demo-action-plan"
        >
          <div className="panel-heading">
            <GitBranch size={20} aria-hidden="true" />
            <h2>Run-Control-Aktionsplan</h2>
          </div>
          <div className="run-control-action-plan-grid">
            {runControlActionPlanRows.map(([label, value]) => (
              <div className="run-control-action-plan-row" key={label}>
                <span>{label}</span>
                <strong>{value}</strong>
              </div>
            ))}
          </div>
        </section>

        <section
          className="panel run-control-execution-flow-panel"
          aria-label="Run-Control-Ausfuehrungsflow"
          data-testid="run-control-execution-flow"
        >
          <div className="panel-heading">
            <Play size={20} aria-hidden="true" />
            <h2>Run-Control-Ausfuehrungsflow</h2>
          </div>
          <div className="run-control-execution-flow-steps" aria-label="Preflight -> explizite Freigabe -> Ausfuehren">
            {runControlExecutionFlowSteps.map(([label, value]) => (
              <div className="run-control-execution-flow-step" key={label}>
                <span>{label}</span>
                <strong>{value}</strong>
              </div>
            ))}
          </div>
          <div className="run-control-execution-release" data-testid="run-control-execution-release">
            <div className="run-control-execution-release-fields">
              <label>
                <span>Freigegeben von</span>
                <input
                  type="text"
                  value={executionReleaseActor}
                  onChange={(event) => {
                    setExecutionReleaseActor(event.target.value);
                    invalidateExecutionRelease();
                  }}
                />
              </label>
              <label>
                <span>Begruendung</span>
                <input
                  type="text"
                  value={executionReleaseReason}
                  onChange={(event) => {
                    setExecutionReleaseReason(event.target.value);
                    invalidateExecutionRelease();
                  }}
                />
              </label>
            </div>
            <div className="run-control-execution-release-actions">
              <label className="run-control-execution-confirmation">
                <input
                  type="checkbox"
                  checked={executionReleaseConfirmed}
                  onChange={(event) => {
                    setExecutionReleaseConfirmed(event.target.checked);
                    invalidateExecutionRelease();
                  }}
                />
                <span>Ausfuehrung explizit freigeben</span>
              </label>
              <button
                className="secondary-action"
                data-testid="run-control-release-check-button"
                disabled={!canCheckExecutionRelease || executionReleaseState === "loading"}
                type="button"
                onClick={checkExecutionRelease}
              >
                <ShieldCheck size={17} aria-hidden="true" />
                Freigabe pruefen
              </button>
              <button
                className="primary-action"
                data-testid="run-control-adapter-start-button"
                disabled={!canStartAdapter}
                type="button"
                onClick={startReleasedAdapter}
              >
                <Play size={17} aria-hidden="true" />
                Adapter starten
              </button>
            </div>
          </div>
          <div className="run-control-execution-flow-grid" aria-label="Run-Control-Startvertrag-Grenzen">
            {runControlExecutionFlowRows.map(([label, value]) => (
              <div className="run-control-execution-flow-row" key={label}>
                <span>{label}</span>
                <strong>{value}</strong>
              </div>
            ))}
          </div>
        </section>

        <section
          className="panel run-control-execution-result-panel"
          aria-label="Run-Control-Ergebnisanzeige"
          data-testid="run-control-execution-result"
        >
          <div className="panel-heading">
            <Database size={20} aria-hidden="true" />
            <h2>Run-Control-Ergebnisanzeige</h2>
            <button
              className="secondary-action run-control-execution-result-refresh"
              data-testid="run-control-execution-result-refresh"
              disabled={
                !selectedQueueId ||
                runControlExecutionResultState === "loading" ||
                runControlExecutionHistoryState === "loading"
              }
              type="button"
              onClick={() => setExecutionEvidenceRevision((revision) => revision + 1)}
            >
              <RefreshCw size={17} aria-hidden="true" />
              Ergebnis neu laden
            </button>
          </div>
          <div className="run-control-execution-result-grid" aria-label="Persistiertes Run-Control-Ergebnis">
            {runControlExecutionResultRows.map(([label, value]) => (
              <div className="run-control-execution-result-row" key={label}>
                <span>{label}</span>
                <strong>{value}</strong>
              </div>
            ))}
          </div>
          <div
            className="run-control-execution-result-grid run-control-execution-history-grid"
            aria-label="Run-Control-Ausfuehrungsverlauf"
            data-testid="run-control-execution-history"
          >
            {runControlExecutionHistoryRows.map(([label, value]) => (
              <div className="run-control-execution-result-row" key={label}>
                <span>{label}</span>
                <strong>{value}</strong>
              </div>
            ))}
          </div>
        </section>

        <section
          className="panel run-control-core-bridge-panel"
          aria-label="Run-Control-Kernblick-Bruecke"
          data-testid="run-control-core-bridge"
        >
          <div className="panel-heading">
            <GitBranch size={20} aria-hidden="true" />
            <h2>Run-Control-Kernblick-Bruecke</h2>
          </div>
          <div className="run-control-core-bridge-grid">
            {runControlCoreBridgeRows.map(([label, value]) => (
              <div className="run-control-core-bridge-row" key={label}>
                <span>{label}</span>
                <strong>{value}</strong>
              </div>
            ))}
          </div>
        </section>

        <section className="panel run-control-preflight-panel" aria-label="Run-Control-Preflight">
          <div className="panel-heading">
            <ShieldCheck size={20} aria-hidden="true" />
            <h2>Run-Control-Preflight</h2>
          </div>
          <div className="detail-status">
            <span>Quelle</span>
            <strong>{runControlPreflightStatus}</strong>
          </div>
          <div className="run-control-preflight-grid">
            {runControlPreflightRows.map(([label, value]) => (
              <div className="run-control-preflight-row" key={label}>
                <span>{label}</span>
                <strong>{value}</strong>
              </div>
            ))}
          </div>
        </section>

        <section className="panel run-control-request-panel" aria-label="Run-Control-Request-Vertrag">
          <div className="panel-heading">
            <FileText size={20} aria-hidden="true" />
            <h2>Run-Control-Request-Vertrag</h2>
          </div>
          <div className="run-control-request-grid">
            {runControlRequestRows.map(([label, value]) => (
              <div className="run-control-request-row" key={label}>
                <span>{label}</span>
                <strong>{value}</strong>
              </div>
            ))}
          </div>
        </section>

        <section className="panel diagnosis-panel" aria-label="Betriebsdiagnose">
          <div className="panel-heading">
            <ServerCog size={20} aria-hidden="true" />
            <h2>Betriebsdiagnose</h2>
          </div>
          <div className="diagnosis-grid">
            {diagnosisRows.map(([label, value]) => (
              <div className="diagnosis-row" key={label}>
                <span>{label}</span>
                <strong>{value}</strong>
              </div>
            ))}
          </div>
        </section>

        <section className="panel consistency-panel" aria-label="Metadaten-Konsistenz">
          <div className="panel-heading">
            <ShieldCheck size={20} aria-hidden="true" />
            <h2>Metadaten-Konsistenz</h2>
          </div>
          <div className="consistency-summary">
            <span className={`status-dot ${metadataConsistency?.status === "warning" ? "warn" : "ready"}`} />
            <strong>{metadataConsistency?.issue_count ?? 0} offene Hinweise</strong>
          </div>
          <div className="consistency-grid">
            {consistencyRows.map(([label, value]) => (
              <div className="consistency-row" key={label}>
                <span>{label}</span>
                <strong>{value}</strong>
              </div>
            ))}
          </div>
        </section>

        <section className="panel validation-panel" id="validation">
          <div className="panel-heading">
            <GitBranch size={20} aria-hidden="true" />
            <h2>Validierungsstatus</h2>
          </div>
          <div className="validation-table">
            {validationRows.map(([area, scope, state]) => (
              <div className="validation-row" key={area}>
                <span>{area}</span>
                <span>{scope}</span>
                <strong>
                  {state === "gruen" ? (
                    <CheckCircle2 size={17} aria-hidden="true" />
                  ) : (
                    <CircleDot size={17} aria-hidden="true" />
                  )}
                  {state}
                </strong>
              </div>
            ))}
          </div>
        </section>
      </section>
    </main>
  );
}

createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
