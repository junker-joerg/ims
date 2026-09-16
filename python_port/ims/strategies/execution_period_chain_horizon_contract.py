from __future__ import annotations

from dataclasses import dataclass

from ims.strategies.execution_period_chain_bounded_runner_contract import (
    STABLE_PREFIX_PERIOD_EFFECT_FIELDS,
    STABLE_PREFIX_TRANSITION_EFFECT_FIELDS,
)
from ims.strategies.execution_period_chain_contract import (
    STRATEGY_EXECUTION_PERIOD_CHAIN_VERSION,
)


STRATEGY_EXECUTION_PERIOD_CHAIN_HORIZON_CONTRACT_VERSION = (
    "ims.strategy-execution-period-chain-horizon-contract.v2"
)
_MAX_PERIOD_SECONDS = 30
_MAX_PEAK_WORKER_RSS_MIB = 1024
_MAX_CHAIN_PAYLOAD_MIB = 64
_MAX_RESULT_PAYLOAD_MIB = 64
_MIN_FREE_STORAGE_MIB = 256


@dataclass(frozen=True, slots=True)
class StrategyExecutionHorizonDefinition:
    period_count: int
    max_wall_seconds: int

    def to_dict(self) -> dict[str, object]:
        return {
            "period_count": self.period_count,
            "first_local_period": 1,
            "last_local_period": self.period_count,
            "required_candidate_count": self.period_count,
            "required_transition_count": self.period_count - 1,
            "maximum_runner_invocations": self.period_count,
            "maximum_carryover_invocations": 2 * (self.period_count - 1),
            "max_wall_seconds": self.max_wall_seconds,
            "max_period_seconds": _MAX_PERIOD_SECONDS,
            "max_peak_worker_rss_mib": _MAX_PEAK_WORKER_RSS_MIB,
            "max_canonical_chain_payload_mib": _MAX_CHAIN_PAYLOAD_MIB,
            "max_serialized_result_payload_mib": _MAX_RESULT_PAYLOAD_MIB,
            "min_free_storage_before_start_mib": _MIN_FREE_STORAGE_MIB,
            "build_enabled": self.period_count < 100,
            "execution_enabled": self.period_count < 100,
            "persistence_enabled": False,
            "ui_start_enabled": False,
        }


STRATEGY_EXECUTION_HORIZON_DEFINITIONS = (
    StrategyExecutionHorizonDefinition(10, 180),
    StrategyExecutionHorizonDefinition(25, 450),
    StrategyExecutionHorizonDefinition(50, 900),
    StrategyExecutionHorizonDefinition(100, 1800),
)


def strategy_execution_period_chain_horizon_contract_payload() -> dict[str, object]:
    """Beschreibt Folgehorizonte ohne Eingang, I/O oder Ausfuehrung."""

    boundary_flags = {
        "contract_read_only": True,
        "extended_horizon_preflight_enabled": True,
        "extended_horizon_build_enabled": True,
        "extended_horizon_execution_enabled": True,
        "extended_horizon_persistence_enabled": False,
        "extended_horizon_ui_start_enabled": False,
        "writes_performed": False,
        "runner_invocation_performed": False,
        "carryover_invocation_performed": False,
        "execution_performed": False,
        "simulation_performed": False,
        "output_files_enabled": False,
        "historical_rng_equality_claim": False,
        "historical_full_equality_claim": False,
    }
    return {
        "schema_version": STRATEGY_EXECUTION_PERIOD_CHAIN_HORIZON_CONTRACT_VERSION,
        "period_chain_schema_version": STRATEGY_EXECUTION_PERIOD_CHAIN_VERSION,
        "mode": "strategy_execution_period_chain_horizon_contract_read_only",
        "scope": "contiguous_local_single_run_horizons_contract_only",
        "base_model": "Vdefmd6",
        "contract_endpoint": (
            "/api/run-control/strategy-period-chain-horizon-contract"
        ),
        "historical_sources": [
            {"source": "ESS.C:71-75", "meaning": "ascending_local_period_loop"},
            {"source": "IMSDATA.C:14", "meaning": "SIMLAENGE_100_per_run"},
        ],
        "historical_maximum_periods_per_run": 100,
        "released_period_counts": [2, 5, 10, 25, 50],
        "contract_only_period_counts": [100],
        "horizons": [
            definition.to_dict()
            for definition in STRATEGY_EXECUTION_HORIZON_DEFINITIONS
        ],
        "budget_policy": {
            "limits_are_safety_ceilings_not_duration_predictions": True,
            "monotonic_elapsed_clock_required": True,
            "isolation_and_measured_enforcement_required_before_release": True,
            "worker_process_termination_required_for_hard_limit": True,
            "python_thread_cancellation_is_not_sufficient": True,
            "peak_rss_measurement_required": True,
            "canonical_chain_and_result_byte_measurement_required": True,
            "free_storage_preflight_required": True,
            "limit_change_requires_new_contract_version": True,
            "missing_measurement_blocks_release": True,
        },
        "preflight_policy": {
            "complete_contiguous_chain_before_first_runner": True,
            "one_immutable_candidate_per_period": True,
            "one_run_index_and_exact_max_periods": True,
            "all_candidate_and_chain_digests_reverified": True,
            "all_candidate_contexts_and_actor_identities_cross_checked": True,
            "exact_transition_flags_required": True,
            "stored_successful_five_period_baseline_required": True,
            "incomplete_preflight_blocks_first_runner": True,
        },
        "prefix_policy": {
            "baseline": "stored_pr145_five_period_result",
            "baseline_two_period_prefix_verified_required": True,
            "compared_periods": [1, 2, 3, 4, 5],
            "compared_transition_count": 4,
            "included_period_effect_fields": list(STABLE_PREFIX_PERIOD_EFFECT_FIELDS),
            "included_transition_effect_fields": list(
                STABLE_PREFIX_TRANSITION_EFFECT_FIELDS
            ),
            "excluded_horizon_envelope_fields": [
                "chain_id",
                "chain_content_digest",
                "max_periods",
                "period_count",
                "release_identity",
                "result_identity",
            ],
            "comparison_before_period": 6,
            "semantic_equality_required": True,
            "canonical_json_byte_equality_required": True,
            "horizon_envelope_excluded": True,
            "tolerance_allowed": False,
            "first_difference_blocks_remaining_periods": True,
        },
        "abort_policy": {
            "manual_cancellation_at_period_boundary": True,
            "hard_limit_terminates_isolated_worker": True,
            "hard_limit_may_interrupt_current_period": True,
            "stored_candidates_must_remain_unchanged": True,
            "partial_result_returned": False,
            "partial_result_persisted": False,
            "checkpoint_resume_enabled": False,
        },
        "failure_policy": {
            "stop_on_first_error": True,
            "later_periods_after_failure_allowed": False,
            "only_complete_digest_verified_result_persisted_atomically": True,
            "failed_attempt_audit_allowed": True,
            "automatic_retry_enabled": False,
            "new_explicit_release_required_for_retry": True,
            "identical_successful_idempotent_replay_is_read_only": False,
            "persistent_idempotency_requires_later_release": True,
            "same_key_different_request_rejected": False,
        },
        "release_gates": {
            "pr148": [10, 25, 50],
            "pr149": [100],
            "load_and_failure_tests_required_per_horizon": True,
            "no_implicit_release_by_contract": True,
        },
        "next_gate": "PR149",
        "boundary_flags": boundary_flags,
        **boundary_flags,
    }
