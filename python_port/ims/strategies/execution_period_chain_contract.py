from __future__ import annotations

from dataclasses import dataclass

from ims.engine.explicit_period_transition_diagnostics import (
    VN_CARRYOVER_INSURER_SOURCE_FIELDS,
    VN_CARRYOVER_POLICYHOLDER_SOURCE_FIELDS,
    VU_CARRYOVER_SOURCE_FIELDS,
)
from ims.strategies.execution_candidate_contract import (
    STRATEGY_EXECUTION_CANDIDATE_VERSION,
)


STRATEGY_EXECUTION_PERIOD_CHAIN_CONTRACT_VERSION = (
    "ims.strategy-execution-period-chain-contract.v1"
)
STRATEGY_EXECUTION_PERIOD_CHAIN_VERSION = (
    "ims.strategy-execution-period-chain.v1"
)


@dataclass(frozen=True, slots=True)
class StrategyExecutionPeriodChainSectionDefinition:
    """Pflichtabschnitt einer spaeteren unveraenderlichen Periodenkette."""

    section_id: str
    fields: tuple[str, ...]
    source: str

    def to_dict(self) -> dict[str, object]:
        return {
            "section_id": self.section_id,
            "fields": list(self.fields),
            "source": self.source,
        }


@dataclass(frozen=True, slots=True)
class StrategyExecutionCarryoverDefinition:
    """Bereits portierte Carryover-Grenze fuer eine Akteursgruppe."""

    carryover_id: str
    actor_scope: str
    implementation_module: str
    implementation_symbol: str
    previous_result_type: str
    source_fields: tuple[str, ...]
    matching_key: str = "entity_id"

    def to_dict(self) -> dict[str, object]:
        return {
            "carryover_id": self.carryover_id,
            "actor_scope": self.actor_scope,
            "implementation_module": self.implementation_module,
            "implementation_symbol": self.implementation_symbol,
            "previous_result_type": self.previous_result_type,
            "source_fields": list(self.source_fields),
            "matching_key": self.matching_key,
        }


STRATEGY_EXECUTION_PERIOD_CHAIN_SECTIONS = (
    StrategyExecutionPeriodChainSectionDefinition(
        section_id="identity",
        fields=("chain_id", "content_digest", "schema_version"),
        source="server_side_pr136_period_chain_builder",
    ),
    StrategyExecutionPeriodChainSectionDefinition(
        section_id="horizon",
        fields=(
            "first_period",
            "last_period",
            "period_count",
            "run_index",
            "max_periods",
        ),
        source="explicit_versioned_chain_input",
    ),
    StrategyExecutionPeriodChainSectionDefinition(
        section_id="period_candidates",
        fields=("candidate_id", "content_digest", "period"),
        source="immutable_pr127_strategy_execution_candidates",
    ),
    StrategyExecutionPeriodChainSectionDefinition(
        section_id="transitions",
        fields=(
            "from_period",
            "to_period",
            "carry_forward_vu_state",
            "carry_forward_vn_state",
        ),
        source="explicit_versioned_chain_input",
    ),
    StrategyExecutionPeriodChainSectionDefinition(
        section_id="provenance",
        fields=(
            "chain_build_schema_version",
            "candidate_resolution_schema_version",
            "candidate_store_source",
            "candidate_count",
            "candidate_digest_reverification_complete",
            "candidate_context_cross_check_complete",
            "actor_identity_cross_check_complete",
        ),
        source="pr135_resolution_and_pr136_period_chain_build",
    ),
    StrategyExecutionPeriodChainSectionDefinition(
        section_id="execution_boundaries",
        fields=(
            "validation_enabled",
            "persistence_enabled",
            "runner_enabled",
            "ui_start_enabled",
        ),
        source="fixed_period_chain_contract",
    ),
)


STRATEGY_EXECUTION_CARRYOVER_DEFINITIONS = (
    StrategyExecutionCarryoverDefinition(
        carryover_id="vu_insurer_state",
        actor_scope="insurer",
        implementation_module="ims.engine.vu_rule_runner",
        implementation_symbol="apply_vu_foreign_info_carryover",
        previous_result_type="VUForeignInfoPeriodRunResult",
        source_fields=VU_CARRYOVER_SOURCE_FIELDS,
    ),
    StrategyExecutionCarryoverDefinition(
        carryover_id="vn_insurer_state",
        actor_scope="insurer",
        implementation_module="ims.engine.vn_rule_runner",
        implementation_symbol="apply_vn_state_carryover",
        previous_result_type="VNSettlementPeriodRunResult",
        source_fields=VN_CARRYOVER_INSURER_SOURCE_FIELDS,
    ),
    StrategyExecutionCarryoverDefinition(
        carryover_id="vn_policyholder_state",
        actor_scope="policyholder",
        implementation_module="ims.engine.vn_rule_runner",
        implementation_symbol="apply_vn_state_carryover",
        previous_result_type="VNSettlementPeriodRunResult",
        source_fields=VN_CARRYOVER_POLICYHOLDER_SOURCE_FIELDS,
    ),
)


def strategy_execution_period_chain_contract_payload() -> dict[str, object]:
    """Beschreibt die spaetere Periodenkette, ohne sie zu bauen oder auszufuehren."""

    boundary_flags = {
        "contract_read_only": True,
        "period_chain_validation_enabled": True,
        "period_chain_candidate_resolution_enabled": True,
        "period_chain_materialization_enabled": True,
        "period_chain_digest_enabled": True,
        "period_chain_persistence_enabled": False,
        "period_chain_runner_enabled": False,
        "carryover_execution_enabled": False,
        "multi_period_execution_enabled": False,
        "ui_start_enabled": False,
        "output_files_enabled": False,
        "legacy_comparison_enabled": False,
        "writes_performed": False,
        "execution_performed": False,
        "simulation_performed": False,
        "automatic_historical_rule_selection_performed": False,
        "historical_rng_equality_claim": False,
        "historical_full_equality_claim": False,
    }
    return {
        "schema_version": STRATEGY_EXECUTION_PERIOD_CHAIN_CONTRACT_VERSION,
        "period_chain_schema_version": STRATEGY_EXECUTION_PERIOD_CHAIN_VERSION,
        "candidate_schema_version": STRATEGY_EXECUTION_CANDIDATE_VERSION,
        "mode": "strategy_execution_period_chain_contract_read_only",
        "base_model": "Vdefmd6",
        "scope": "controlled_contiguous_local_period_chain",
        "contract_endpoint": "/api/strategies/execution-period-chain-contract",
        "validation_contract_endpoint": (
            "/api/strategies/execution-period-chain-validation-contract"
        ),
        "validation_endpoint": (
            "/api/strategies/execution-period-chain-validation"
        ),
        "resolution_contract_endpoint": (
            "/api/strategies/execution-period-chain-resolution-contract"
        ),
        "resolution_endpoint": (
            "/api/strategies/execution-period-chain-resolution"
        ),
        "build_contract_endpoint": (
            "/api/strategies/execution-period-chain-build-contract"
        ),
        "build_endpoint": "/api/strategies/execution-period-chain-build",
        "historical_horizon": {
            "source": "IMSDATA.C:14",
            "constant": "SIMLAENGE",
            "maximum_periods_per_run": 100,
            "local_period_minimum": 1,
            "local_period_maximum": 100,
            "historical_result_rows_above_100_mean_separate_runs": True,
        },
        "period_sequence_policy": {
            "minimum_period_count": 2,
            "maximum_period_count": 100,
            "first_local_period": 1,
            "period_step": 1,
            "strictly_increasing": True,
            "contiguous": True,
            "same_run_index_required": True,
            "same_max_periods_required": True,
            "candidate_period_must_match": True,
            "one_immutable_candidate_per_period": True,
        },
        "candidate_reference_fields": [
            "candidate_id",
            "content_digest",
            "period",
        ],
        "transition_reference_fields": [
            "from_period",
            "to_period",
            "carry_forward_vu_state",
            "carry_forward_vn_state",
        ],
        "previous_period_result_policy": {
            "source": "immediately_previous_in_memory_explicit_period_result",
            "same_chain_required": True,
            "adjacent_period_required": True,
            "successful_result_required": True,
            "stored_pr131_effect_summary_accepted": False,
            "historical_reference_row_accepted": False,
            "synthetic_previous_result_accepted": False,
        },
        "carryover_policy": {
            "default_enabled": False,
            "explicit_opt_in_per_transition_required": True,
            "vu_flag": "carry_forward_vu_state",
            "vn_flag": "carry_forward_vn_state",
            "application_order": ["vu", "vn"],
            "application_order_source": (
                "ims.engine.explicit_period_runner.run_explicit_multi_period_from_mappings"
            ),
            "target": "isolated_copy_of_next_period_candidate",
            "stored_source_candidate_mutation_allowed": False,
            "stored_target_candidate_mutation_allowed": False,
            "same_actor_ids_required_before_execution": True,
            "hidden_fallback_allowed": False,
            "carry_all_fields_allowed": False,
        },
        "section_count": len(STRATEGY_EXECUTION_PERIOD_CHAIN_SECTIONS),
        "sections": [
            definition.to_dict()
            for definition in STRATEGY_EXECUTION_PERIOD_CHAIN_SECTIONS
        ],
        "carryover_definition_count": len(
            STRATEGY_EXECUTION_CARRYOVER_DEFINITIONS
        ),
        "carryover_definitions": [
            definition.to_dict()
            for definition in STRATEGY_EXECUTION_CARRYOVER_DEFINITIONS
        ],
        "provenance_policy": {
            "chain_content_digest_required": True,
            "candidate_digest_reverification_required": True,
            "chain_build_provenance_required": True,
            "execution_provenance_stored_in_chain": False,
            "future_execution_record_references_chain_required": True,
            "source_result_digest_required": True,
            "effective_period_input_digest_required": True,
            "release_identity_per_chain_required": True,
        },
        "stop_policy": {
            "validate_complete_chain_before_first_period": True,
            "stop_after_first_failed_period": True,
            "later_periods_after_failure_allowed": False,
            "partial_chain_success_allowed": False,
            "period_gap_allowed": False,
            "digest_mismatch_allowed": False,
            "missing_actor_allowed": False,
        },
        "next_gate": "PR137",
        "boundary_flags": boundary_flags,
        **boundary_flags,
    }
