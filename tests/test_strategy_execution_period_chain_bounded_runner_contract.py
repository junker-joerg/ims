from ims.strategies import (
    BOUNDED_RUNNER_MAXIMUM_PERIODS,
    BOUNDED_RUNNER_MINIMUM_PERIODS,
    STABLE_PREFIX_PERIOD_COUNT,
    STRATEGY_EXECUTION_BOUNDED_RUNNER_STEPS,
    STRATEGY_EXECUTION_PERIOD_CHAIN_BOUNDED_RUNNER_CONTRACT_VERSION,
    STRATEGY_EXECUTION_PERIOD_CHAIN_PREFIX_PROJECTION_VERSION,
    strategy_execution_period_chain_bounded_runner_contract_payload,
)


def test_bounded_runner_contract_limits_first_extension_to_five_periods() -> None:
    payload = strategy_execution_period_chain_bounded_runner_contract_payload()

    assert payload["schema_version"] == (
        STRATEGY_EXECUTION_PERIOD_CHAIN_BOUNDED_RUNNER_CONTRACT_VERSION
    )
    assert payload["prefix_projection_schema_version"] == (
        STRATEGY_EXECUTION_PERIOD_CHAIN_PREFIX_PROJECTION_VERSION
    )
    assert payload["horizon_policy"] == {
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
    }
    assert payload["current_release_state"] == {
        "released_period_counts": [2, 5],
        "contracted_not_released_period_counts": [3, 4],
        "five_period_target": 5,
        "existing_two_period_endpoint_unchanged": (
            "/api/run-control/strategy-period-chain-effect-probe"
        ),
        "five_period_build_endpoint": (
            "/api/strategies/execution-period-chain-five-period-build"
        ),
            "bounded_execution_endpoint": (
                "/api/run-control/strategy-period-chain-five-period-effect-probe"
            ),
            "persistent_start_endpoint": (
                "/api/run-control/strategy-period-chain-five-period-effect-probe-start"
            ),
            "read_only_result_endpoint_template": (
                "/api/run-control/strategy-period-chain-five-period-effect-probe-result/{chain_id}"
            ),
            "read_only_history_endpoint_template": (
                "/api/run-control/strategy-period-chain-five-period-effect-probe-history/{chain_id}"
            ),
        }
    assert payload["five_period_candidate_validation_enabled"] is True
    assert payload["five_period_chain_build_enabled"] is True
    assert payload["bounded_runner_enabled"] is True
    assert payload["five_period_execution_enabled"] is True
    assert payload["five_period_ui_start_enabled"] is True
    assert payload["prefix_comparison_execution_enabled"] is True
    assert payload["execution_performed"] is False
    assert payload["simulation_performed"] is False
    assert payload["next_gate"] == "PR148"


def test_bounded_runner_contract_orders_full_preparation_before_execution() -> None:
    payload = strategy_execution_period_chain_bounded_runner_contract_payload()
    steps = payload["execution_steps"]

    assert payload["step_count"] == len(STRATEGY_EXECUTION_BOUNDED_RUNNER_STEPS)
    assert [step["step_id"] for step in steps] == [
        "build_and_validate_complete_five_period_chain",
        "load_and_verify_stored_two_period_prefix_baseline",
        "reresolve_all_candidates_and_reverify_digests",
        "load_and_cross_check_all_isolated_candidate_copies",
        "run_each_period_once_in_ascending_order",
        "apply_exact_canonical_transition_flags_before_next_period",
        "compare_exact_two_period_prefix_before_period_3",
        "return_complete_ephemeral_result_or_no_result",
    ]
    assert all(step["before_first_runner"] for step in steps[:4])
    assert not any(step["before_first_runner"] for step in steps[4:])
    assert payload["atomic_failure_policy"] == {
        "validate_complete_chain_before_first_runner": True,
        "stop_after_first_failed_period": True,
        "later_periods_after_failure_allowed": False,
        "partial_result_returned": False,
        "partial_result_persisted": False,
        "retry_implicit": False,
    }


def test_bounded_runner_contract_defines_exact_two_period_prefix_projection() -> None:
    payload = strategy_execution_period_chain_bounded_runner_contract_payload()
    prefix = payload["stable_two_period_prefix_policy"]

    assert prefix["required_period_count"] == STABLE_PREFIX_PERIOD_COUNT
    assert prefix["canonical_json_byte_equality_required"] is True
    assert prefix["semantic_equality_required"] is True
    assert prefix["first_difference_blocks_release"] is True
    assert prefix["tolerance_allowed"] is False
    assert prefix["included_sections"] == [
        "period_effects[period=1]",
        "transition_effects[from_period=1,to_period=2]",
        "period_effects[period=2]",
    ]
    assert prefix["included_period_effect_fields"] == [
        "period",
        "global_period",
        "applications",
        "state_before",
        "state_after",
        "state_changed",
        "changed_insurer_ids",
        "changed_policyholder_ids",
        "in_memory_export",
    ]
    assert prefix["excluded_horizon_envelope_fields"] == [
        "chain_id",
        "chain_content_digest",
        "max_periods",
        "period_count",
        "release_identity",
        "result_identity",
    ]
    assert payload["existing_two_period_effect_probe_enabled"] is True
    assert payload["existing_two_period_effect_probe_changed"] is False


def test_bounded_runner_contract_has_no_write_or_legacy_escape_hatch() -> None:
    payload = strategy_execution_period_chain_bounded_runner_contract_payload()

    assert payload["contract_read_only"] is True
    assert payload["queue_write_enabled"] is False
    assert payload["output_files_enabled"] is False
    assert payload["legacy_comparison_enabled"] is False
    assert payload["writes_performed"] is False
    assert payload["automatic_historical_rule_selection_performed"] is False
    assert payload["historical_rng_equality_claim"] is False
    assert payload["historical_full_equality_claim"] is False
