from __future__ import annotations

from dataclasses import dataclass

from ims.strategies.execution_period_chain_contract import (
    STRATEGY_EXECUTION_PERIOD_CHAIN_VERSION,
)


STRATEGY_EXECUTION_PERIOD_CHAIN_BOUNDED_RUNNER_CONTRACT_VERSION = (
    "ims.strategy-execution-period-chain-bounded-runner-contract.v1"
)
STRATEGY_EXECUTION_PERIOD_CHAIN_PREFIX_PROJECTION_VERSION = (
    "ims.strategy-execution-period-chain-prefix-projection.v1"
)
BOUNDED_RUNNER_MINIMUM_PERIODS = 2
BOUNDED_RUNNER_MAXIMUM_PERIODS = 5
STABLE_PREFIX_PERIOD_COUNT = 2


@dataclass(frozen=True, slots=True)
class StrategyExecutionBoundedRunnerStepDefinition:
    """Ein verbindlicher Schritt der spaeteren begrenzten Ausfuehrung."""

    step_id: str
    source: str
    before_first_runner: bool

    def to_dict(self) -> dict[str, object]:
        return {
            "step_id": self.step_id,
            "source": self.source,
            "before_first_runner": self.before_first_runner,
        }


STRATEGY_EXECUTION_BOUNDED_RUNNER_STEPS = (
    StrategyExecutionBoundedRunnerStepDefinition(
        step_id="reverify_stored_chain_release",
        source="pr138_period_chain_run_control",
        before_first_runner=True,
    ),
    StrategyExecutionBoundedRunnerStepDefinition(
        step_id="require_contiguous_horizon_2_to_5",
        source="pr133_period_chain_contract",
        before_first_runner=True,
    ),
    StrategyExecutionBoundedRunnerStepDefinition(
        step_id="reresolve_all_candidates_and_reverify_digests",
        source="pr135_period_chain_resolution",
        before_first_runner=True,
    ),
    StrategyExecutionBoundedRunnerStepDefinition(
        step_id="load_and_cross_check_all_isolated_candidate_copies",
        source="pr139_two_period_effect_probe",
        before_first_runner=True,
    ),
    StrategyExecutionBoundedRunnerStepDefinition(
        step_id="run_each_period_once_in_ascending_order",
        source="ims.engine.explicit_period_runner.run_loaded_explicit_period",
        before_first_runner=False,
    ),
    StrategyExecutionBoundedRunnerStepDefinition(
        step_id="apply_exact_stored_transition_flags_before_next_period",
        source="pr139_two_period_effect_probe",
        before_first_runner=False,
    ),
    StrategyExecutionBoundedRunnerStepDefinition(
        step_id="return_complete_ephemeral_result_or_no_result",
        source="pr139_atomic_partial_result_suppression",
        before_first_runner=False,
    ),
)


def strategy_execution_period_chain_bounded_runner_contract_payload() -> dict[
    str, object
]:
    """Beschreibt den begrenzten Runner, ohne eine Periode auszufuehren."""

    boundary_flags = {
        "contract_read_only": True,
        "bounded_runner_enabled": False,
        "five_period_candidate_validation_enabled": False,
        "five_period_chain_build_enabled": False,
        "five_period_execution_enabled": False,
        "five_period_result_persistence_enabled": False,
        "five_period_ui_start_enabled": False,
        "existing_two_period_effect_probe_enabled": True,
        "existing_two_period_effect_probe_changed": False,
        "prefix_projection_defined": True,
        "prefix_comparison_execution_enabled": False,
        "queue_write_enabled": False,
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
        "schema_version": (
            STRATEGY_EXECUTION_PERIOD_CHAIN_BOUNDED_RUNNER_CONTRACT_VERSION
        ),
        "period_chain_schema_version": STRATEGY_EXECUTION_PERIOD_CHAIN_VERSION,
        "prefix_projection_schema_version": (
            STRATEGY_EXECUTION_PERIOD_CHAIN_PREFIX_PROJECTION_VERSION
        ),
        "mode": "strategy_execution_period_chain_bounded_runner_contract_read_only",
        "scope": "controlled_contiguous_local_period_chain_2_to_5_contract_only",
        "base_model": "Vdefmd6",
        "contract_endpoint": (
            "/api/run-control/strategy-period-chain-bounded-runner-contract"
        ),
        "historical_sources": [
            {
                "source": "ESS.C:73-75",
                "meaning": "period_loop_calls_logical_time_execution",
            },
            {
                "source": "IMSDATA.C:14",
                "meaning": "SIMLAENGE_limits_historical_run_to_100_periods",
            },
        ],
        "horizon_policy": {
            "minimum_period_count": BOUNDED_RUNNER_MINIMUM_PERIODS,
            "maximum_period_count": BOUNDED_RUNNER_MAXIMUM_PERIODS,
            "first_local_period": 1,
            "period_step": 1,
            "strictly_increasing": True,
            "contiguous": True,
            "same_run_index_required": True,
            "same_max_periods_required": True,
            "one_immutable_candidate_per_period": True,
            "candidate_period_must_match": True,
            "larger_horizon_rejected_before_first_runner": True,
        },
        "current_release_state": {
            "released_period_counts": [2],
            "contracted_not_released_period_counts": [3, 4, 5],
            "five_period_target": 5,
            "existing_two_period_endpoint_unchanged": (
                "/api/run-control/strategy-period-chain-effect-probe"
            ),
            "bounded_execution_endpoint": None,
        },
        "step_count": len(STRATEGY_EXECUTION_BOUNDED_RUNNER_STEPS),
        "execution_steps": [
            definition.to_dict()
            for definition in STRATEGY_EXECUTION_BOUNDED_RUNNER_STEPS
        ],
        "transition_policy": {
            "stored_flags_authoritative": True,
            "vu_flag": "carry_forward_vu_state",
            "vn_flag": "carry_forward_vn_state",
            "application_order": ["vu", "vn"],
            "target": "isolated_copy_of_next_period_candidate",
            "hidden_fallback_allowed": False,
            "stored_candidate_mutation_allowed": False,
        },
        "stable_two_period_prefix_policy": {
            "required_period_count": STABLE_PREFIX_PERIOD_COUNT,
            "baseline": "stored_pr140_two_period_effect_probe_result",
            "comparison_target": "first_two_periods_of_future_bounded_result",
            "projection_schema_version": (
                STRATEGY_EXECUTION_PERIOD_CHAIN_PREFIX_PROJECTION_VERSION
            ),
            "canonical_json_byte_equality_required": True,
            "semantic_equality_required": True,
            "included_sections": [
                "period_effects[period=1]",
                "transition_effects[from_period=1,to_period=2]",
                "period_effects[period=2]",
            ],
            "included_period_effect_fields": [
                "period",
                "global_period",
                "applications",
                "state_before",
                "state_after",
                "state_changed",
                "changed_insurer_ids",
                "changed_policyholder_ids",
                "in_memory_export",
            ],
            "included_transition_effect_fields": [
                "from_period",
                "to_period",
                "from_global_period",
                "to_global_period",
                "vu_carryover_requested",
                "vn_carryover_requested",
                "vu_carryover_executed",
                "vn_carryover_executed",
                "carried_insurer_ids",
                "carried_policyholder_ids",
                "state_before",
                "state_after",
                "state_changed",
            ],
            "excluded_horizon_envelope_fields": [
                "chain_id",
                "chain_content_digest",
                "max_periods",
                "period_count",
                "release_identity",
                "result_identity",
            ],
            "first_difference_blocks_release": True,
            "tolerance_allowed": False,
        },
        "atomic_failure_policy": {
            "validate_complete_chain_before_first_runner": True,
            "stop_after_first_failed_period": True,
            "later_periods_after_failure_allowed": False,
            "partial_result_returned": False,
            "partial_result_persisted": False,
            "retry_implicit": False,
        },
        "next_gate": "PR143",
        "boundary_flags": boundary_flags,
        **boundary_flags,
    }
