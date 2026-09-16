import pytest

from ims.strategies import (
    STRATEGY_EXECUTION_HORIZON_DEFINITIONS,
    STRATEGY_EXECUTION_PERIOD_CHAIN_HORIZON_CONTRACT_VERSION,
    strategy_execution_period_chain_horizon_contract_payload,
)
from ims.strategies.execution_period_chain_bounded_runner_contract import (
    STABLE_PREFIX_PERIOD_EFFECT_FIELDS,
    STABLE_PREFIX_TRANSITION_EFFECT_FIELDS,
)


@pytest.mark.parametrize(
    ("periods", "seconds"),
    [(10, 180), (25, 450), (50, 900), (100, 1800)],
)
def test_horizon_limits_are_explicit_and_all_four_are_ephemerally_released(
    periods: int,
    seconds: int,
) -> None:
    payload = strategy_execution_period_chain_horizon_contract_payload()
    horizon = next(
        item for item in payload["horizons"] if item["period_count"] == periods
    )

    assert horizon["first_local_period"] == 1
    assert horizon["last_local_period"] == periods
    assert horizon["required_candidate_count"] == periods
    assert horizon["required_transition_count"] == periods - 1
    assert horizon["maximum_runner_invocations"] == periods
    assert horizon["maximum_carryover_invocations"] == 2 * (periods - 1)
    assert horizon["max_wall_seconds"] == seconds
    assert horizon["max_period_seconds"] == 30
    assert horizon["max_peak_worker_rss_mib"] == 1024
    assert horizon["max_canonical_chain_payload_mib"] == 64
    assert horizon["max_serialized_result_payload_mib"] == 64
    assert horizon["min_free_storage_before_start_mib"] == 256
    assert horizon["build_enabled"] is True
    assert horizon["execution_enabled"] is True
    assert horizon["persistence_enabled"] is False
    assert horizon["ui_start_enabled"] is False


def test_horizon_contract_fails_closed_and_preserves_five_period_path() -> None:
    payload = strategy_execution_period_chain_horizon_contract_payload()

    assert payload["schema_version"] == (
        STRATEGY_EXECUTION_PERIOD_CHAIN_HORIZON_CONTRACT_VERSION
    )
    assert [
        definition.period_count for definition in STRATEGY_EXECUTION_HORIZON_DEFINITIONS
    ] == [10, 25, 50, 100]
    assert payload["released_period_counts"] == [2, 5, 10, 25, 50, 100]
    assert payload["contract_only_period_counts"] == []
    assert len(payload["horizons"]) == 4
    assert payload["historical_maximum_periods_per_run"] == 100
    assert payload["budget_policy"]["missing_measurement_blocks_release"] is True
    assert (
        payload["budget_policy"][
            "isolation_and_measured_enforcement_required_before_release"
        ]
        is True
    )
    assert (
        payload["budget_policy"]["python_thread_cancellation_is_not_sufficient"] is True
    )
    assert (
        payload["preflight_policy"]["incomplete_preflight_blocks_first_runner"] is True
    )
    assert payload["prefix_policy"]["baseline"] == "stored_pr145_five_period_result"
    assert payload["prefix_policy"]["compared_periods"] == [1, 2, 3, 4, 5]
    assert payload["prefix_policy"]["compared_transition_count"] == 4
    assert payload["prefix_policy"]["included_period_effect_fields"] == list(
        STABLE_PREFIX_PERIOD_EFFECT_FIELDS
    )
    assert payload["prefix_policy"]["included_transition_effect_fields"] == list(
        STABLE_PREFIX_TRANSITION_EFFECT_FIELDS
    )
    assert payload["prefix_policy"]["excluded_horizon_envelope_fields"] == [
        "chain_id",
        "chain_content_digest",
        "max_periods",
        "period_count",
        "release_identity",
        "result_identity",
    ]
    assert payload["prefix_policy"]["comparison_before_period"] == 6
    assert payload["prefix_policy"]["canonical_json_byte_equality_required"] is True
    assert payload["prefix_policy"]["tolerance_allowed"] is False
    assert payload["abort_policy"]["partial_result_persisted"] is False
    assert payload["abort_policy"]["checkpoint_resume_enabled"] is False
    assert payload["failure_policy"]["automatic_retry_enabled"] is False
    assert (
        payload["failure_policy"]["identical_successful_idempotent_replay_is_read_only"]
        is False
    )
    assert (
        payload["failure_policy"]["persistent_idempotency_requires_later_release"]
        is True
    )
    assert payload["release_gates"]["pr148"] == [10, 25, 50]
    assert payload["release_gates"]["pr149"] == [100]
    assert payload["release_gates"]["no_implicit_release_by_contract"] is True
    assert payload["contract_read_only"] is True
    assert all(
        payload[flag] is True
        for flag in (
            "extended_horizon_preflight_enabled",
            "extended_horizon_build_enabled",
            "extended_horizon_execution_enabled",
        )
    )
    assert all(
        payload[flag] is False
        for flag in (
            "extended_horizon_persistence_enabled",
            "extended_horizon_ui_start_enabled",
            "writes_performed",
            "runner_invocation_performed",
            "carryover_invocation_performed",
            "execution_performed",
            "simulation_performed",
            "output_files_enabled",
            "historical_rng_equality_claim",
            "historical_full_equality_claim",
        )
    )
    assert payload["next_gate"] == "PR150"


def test_contract_payload_is_fresh_and_cannot_mutate_future_calls() -> None:
    first = strategy_execution_period_chain_horizon_contract_payload()
    first["horizons"][0]["period_count"] = 101
    first["prefix_policy"]["compared_periods"].append(6)

    second = strategy_execution_period_chain_horizon_contract_payload()
    assert second["contract_only_period_counts"] == []
    assert second["horizons"][0]["period_count"] == 10
    assert second["prefix_policy"]["compared_periods"] == [1, 2, 3, 4, 5]
