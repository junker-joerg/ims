from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from ims.strategies.assignment_draft import STRATEGY_ASSIGNMENT_DRAFT_VERSION
from ims.strategies.assignment_snapshot_context import (
    STRATEGY_ASSIGNMENT_SNAPSHOT_CONTEXT_VALIDATION_VERSION,
    STRATEGY_ASSIGNMENT_SNAPSHOT_CONTEXT_VERSION,
)
from ims.strategies.assignment_snapshot_materialization import (
    STRATEGY_ASSIGNMENT_SNAPSHOT_MATERIALIZATION_VERSION,
)
from ims.strategies.assignment_snapshot_materialization_validation import (
    STRATEGY_ASSIGNMENT_SNAPSHOT_MATERIALIZATION_VALIDATION_VERSION,
)
from ims.strategies.assignment_vu_snapshot_materialization import (
    STRATEGY_ASSIGNMENT_VU_SNAPSHOT_MATERIALIZATION_VERSION,
)
from ims.strategies.assignment_vu_snapshot_materialization_validation import (
    STRATEGY_ASSIGNMENT_VU_SNAPSHOT_MATERIALIZATION_INPUT_VERSION,
    STRATEGY_ASSIGNMENT_VU_SNAPSHOT_MATERIALIZATION_VALIDATION_VERSION,
)
from ims.strategies.assignment_vu_snapshot_state_validation import (
    STRATEGY_ASSIGNMENT_VU_SNAPSHOT_STATE_VALIDATION_VERSION,
    STRATEGY_ASSIGNMENT_VU_SNAPSHOT_STATE_VERSION,
)


STRATEGY_EXECUTION_CANDIDATE_CONTRACT_VERSION = (
    "ims.strategy-execution-candidate-contract.v1"
)
STRATEGY_EXECUTION_CANDIDATE_VERSION = "ims.strategy-execution-candidate.v1"


@dataclass(frozen=True, slots=True)
class StrategyExecutionCandidateSectionDefinition:
    """Pflichtabschnitt des spaeteren unveraenderlichen Kandidaten."""

    section_id: str
    fields: tuple[str, ...]
    source: str
    availability: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class StrategyExecutionCandidateCollectionDefinition:
    """Kanonische LoadedScenario-Sammlung des spaeteren Kandidaten."""

    collection_name: str
    actor_scope: str
    snapshot_role: str
    source: str
    cardinality: str
    alternative_group: str | None = None

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class StrategyExecutionCandidateOpenRequirement:
    """Bewusst noch nicht implementierter Teil des Ausfuehrungsanschlusses."""

    requirement_id: str
    planned_pr: int
    blocks: tuple[str, ...]
    decision: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


STRATEGY_EXECUTION_CANDIDATE_SECTIONS = (
    StrategyExecutionCandidateSectionDefinition(
        section_id="identity",
        fields=("candidate_id", "draft_id", "period", "content_digest"),
        source="server_side_candidate_builder",
        availability="implemented_pr126",
    ),
    StrategyExecutionCandidateSectionDefinition(
        section_id="contract_versions",
        fields=(
            "candidate_schema_version",
            "assignment_draft_schema_version",
            "snapshot_context_schema_version",
            "snapshot_context_validation_schema_version",
            "vn_materialization_schema_version",
            "vn_materialization_validation_schema_version",
            "vu_materialization_input_schema_version",
            "vu_materialization_validation_schema_version",
            "vu_state_schema_version",
            "vu_state_validation_schema_version",
            "vu_materialization_schema_version",
        ),
        source="versioned_source_documents_and_server_contracts",
        availability="described_pr124",
    ),
    StrategyExecutionCandidateSectionDefinition(
        section_id="source_documents",
        fields=(
            "assignment_draft",
            "snapshot_context",
            "vu_materialization_input",
            "vu_state_provenance",
            "vn_process_input",
            "scenario_profile_id",
        ),
        source="original_versioned_documents_not_browser_materialization_reports",
        availability="validated_pr125_built_pr126",
    ),
    StrategyExecutionCandidateSectionDefinition(
        section_id="market_ground_state",
        fields=("simulation_context", "bav", "insurers", "policyholders"),
        source="server_side_known_local_scenario_profile",
        availability="implemented_pr126",
    ),
    StrategyExecutionCandidateSectionDefinition(
        section_id="vu_rule_snapshots",
        fields=("collections",),
        source="server_side_pr121_rematerialization",
        availability="implemented_pr126",
    ),
    StrategyExecutionCandidateSectionDefinition(
        section_id="vn_rule_snapshots",
        fields=("collections",),
        source="server_side_pr116_rematerialization",
        availability="implemented_pr126",
    ),
    StrategyExecutionCandidateSectionDefinition(
        section_id="vn_process_snapshots",
        fields=("collections", "explicit_draw_provenance"),
        source="separate_explicit_vn_process_input",
        availability="validated_pr125_built_pr126",
    ),
    StrategyExecutionCandidateSectionDefinition(
        section_id="execution_boundaries",
        fields=(
            "persistence_enabled",
            "run_control_enabled",
            "runner_enabled",
            "carryover_enabled",
            "output_files_enabled",
            "legacy_comparison_enabled",
        ),
        source="fixed_candidate_contract",
        availability="described_pr124",
    ),
)


_VU_COLLECTIONS = (
    "vu_foreign_info_rule_snapshots",
    "vu_random_uniform_rule_snapshots",
    "vu_random_normal_rule_snapshots",
    "vu_reserve_markup_rule_snapshots",
    "vu_net_switcher_markup_rule_snapshots",
    "vu_expected_claim_rule_snapshots",
    "vu_market_share_markup_rule_snapshots",
    "vu_free_linear_rule_snapshots",
)

STRATEGY_EXECUTION_CANDIDATE_COLLECTIONS = (
    *(
        StrategyExecutionCandidateCollectionDefinition(
            collection_name=collection_name,
            actor_scope="insurer",
            snapshot_role="vu_strategy_rule",
            source="pr121_server_side_rematerialization",
            cardinality="exactly_one_target_snapshot_per_assigned_insurer",
        )
        for collection_name in _VU_COLLECTIONS
    ),
    StrategyExecutionCandidateCollectionDefinition(
        collection_name="vn_insurance_rule_snapshots",
        actor_scope="policyholder",
        snapshot_role="vn_strategy_rule",
        source="pr116_server_side_rematerialization",
        cardinality="exactly_one_target_snapshot_per_assigned_policyholder",
    ),
    StrategyExecutionCandidateCollectionDefinition(
        collection_name="vn_damage_settlement_snapshots",
        actor_scope="policyholder",
        snapshot_role="vn_damage_and_settlement",
        source="separate_explicit_vn_process_input",
        cardinality="disjoint_with_vn_settlement_snapshots",
        alternative_group="vn_process",
    ),
    StrategyExecutionCandidateCollectionDefinition(
        collection_name="vn_settlement_snapshots",
        actor_scope="policyholder",
        snapshot_role="vn_settlement_only",
        source="separate_explicit_vn_process_input",
        cardinality="disjoint_with_vn_damage_settlement_snapshots",
        alternative_group="vn_process",
    ),
)


STRATEGY_EXECUTION_CANDIDATE_OPEN_REQUIREMENTS = (
    StrategyExecutionCandidateOpenRequirement(
        requirement_id="single_period_effect_probe",
        planned_pr=130,
        blocks=("runner_execution",),
        decision="run_only_on_an_isolated_copy_without_files_carryover_or_legacy_compare",
    ),
)


def strategy_execution_candidate_contract_payload() -> dict[str, Any]:
    """Beschreibt den Kandidatenvertrag und seine geschlossenen Ausfuehrungsgrenzen."""

    boundary_flags = {
        "browser_materialization_report_authoritative": False,
        "candidate_input_validation_enabled": True,
        "scenario_profile_resolution_enabled": True,
        "server_side_rematerialization_enabled": True,
        "digest_calculation_enabled": True,
        "candidate_creation_enabled": True,
        "candidate_persistence_enabled": True,
        "explicit_storage_release_required": True,
        "immutable_candidate_storage_enabled": True,
        "candidate_digest_reverification_enabled": True,
        "candidate_overview_enabled": True,
        "candidate_workbench_read_only_enabled": True,
        "run_control_enabled": True,
        "run_control_candidate_resolution_enabled": True,
        "run_control_release_check_enabled": True,
        "run_control_queue_enabled": False,
        "run_control_preflight_enabled": False,
        "adapter_start_allowed": False,
        "snapshot_loader_invocation_enabled": True,
        "runner_enabled": False,
        "execution_enabled": False,
        "carryover_enabled": False,
        "output_files_enabled": False,
        "legacy_comparison_enabled": False,
        "writes_performed": False,
        "simulation_performed": False,
        "historical_rng_equality_claim": False,
        "historical_full_equality_claim": False,
    }
    return {
        "schema_version": STRATEGY_EXECUTION_CANDIDATE_CONTRACT_VERSION,
        "candidate_schema_version": STRATEGY_EXECUTION_CANDIDATE_VERSION,
        "mode": "strategy_execution_candidate_contract_read_only",
        "base_model": "Vdefmd6",
        "scope": "single_period_joint_vu_vn_candidate",
        "contract_endpoint": "/api/strategies/execution-candidate-contract",
        "candidate_validation_contract_endpoint": (
            "/api/strategies/execution-candidate-validation-contract"
        ),
        "candidate_validation_endpoint": (
            "/api/strategies/execution-candidate-validation"
        ),
        "candidate_build_contract_endpoint": (
            "/api/strategies/execution-candidate-build-contract"
        ),
        "candidate_build_endpoint": (
            "/api/strategies/execution-candidate-build"
        ),
        "candidate_store_contract_endpoint": (
            "/api/strategies/execution-candidate-store-contract"
        ),
        "candidate_store_endpoint": (
            "/api/strategies/execution-candidate-store"
        ),
        "candidate_read_endpoint_template": (
            "/api/strategies/execution-candidates/{candidate_id}"
        ),
        "candidate_overview_endpoint": (
            "/api/strategies/execution-candidates"
        ),
        "candidate_run_control_contract_endpoint": (
            "/api/run-control/strategy-candidate-contract"
        ),
        "candidate_run_control_release_check_endpoint": (
            "/api/run-control/strategy-candidate-release-check"
        ),
        "execution_anchor": {
            "module": "ims.engine.explicit_period_runner",
            "symbol": "run_loaded_explicit_period",
            "status": "planned_only",
        },
        "authoritative_source_policy": {
            "original_versioned_documents_required": True,
            "server_side_rematerialization_required": True,
            "known_local_scenario_profile_required": True,
            "explicit_draws_required": True,
            "browser_materialization_reports_accepted": False,
            "free_fixture_paths_accepted": False,
            "free_output_paths_accepted": False,
            "browser_candidate_payloads_accepted": False,
        },
        "upstream_contract_versions": {
            "assignment_draft": STRATEGY_ASSIGNMENT_DRAFT_VERSION,
            "snapshot_context": STRATEGY_ASSIGNMENT_SNAPSHOT_CONTEXT_VERSION,
            "snapshot_context_validation": (
                STRATEGY_ASSIGNMENT_SNAPSHOT_CONTEXT_VALIDATION_VERSION
            ),
            "vn_materialization": STRATEGY_ASSIGNMENT_SNAPSHOT_MATERIALIZATION_VERSION,
            "vn_materialization_validation": (
                STRATEGY_ASSIGNMENT_SNAPSHOT_MATERIALIZATION_VALIDATION_VERSION
            ),
            "vu_materialization_input": (
                STRATEGY_ASSIGNMENT_VU_SNAPSHOT_MATERIALIZATION_INPUT_VERSION
            ),
            "vu_materialization_validation": (
                STRATEGY_ASSIGNMENT_VU_SNAPSHOT_MATERIALIZATION_VALIDATION_VERSION
            ),
            "vu_state": STRATEGY_ASSIGNMENT_VU_SNAPSHOT_STATE_VERSION,
            "vu_state_validation": (
                STRATEGY_ASSIGNMENT_VU_SNAPSHOT_STATE_VALIDATION_VERSION
            ),
            "vu_materialization": (
                STRATEGY_ASSIGNMENT_VU_SNAPSHOT_MATERIALIZATION_VERSION
            ),
        },
        "required_section_count": len(STRATEGY_EXECUTION_CANDIDATE_SECTIONS),
        "required_sections": [
            definition.to_dict()
            for definition in STRATEGY_EXECUTION_CANDIDATE_SECTIONS
        ],
        "vu_collection_count": len(_VU_COLLECTIONS),
        "vn_rule_collection_count": 1,
        "vn_process_collection_count": 2,
        "collection_count": len(STRATEGY_EXECUTION_CANDIDATE_COLLECTIONS),
        "collections": [
            definition.to_dict()
            for definition in STRATEGY_EXECUTION_CANDIDATE_COLLECTIONS
        ],
        "open_requirement_count": len(
            STRATEGY_EXECUTION_CANDIDATE_OPEN_REQUIREMENTS
        ),
        "open_requirements": [
            requirement.to_dict()
            for requirement in STRATEGY_EXECUTION_CANDIDATE_OPEN_REQUIREMENTS
        ],
        "boundary_flags": boundary_flags,
        **boundary_flags,
    }
