import importlib

from ims.engine.explicit_period_transition_diagnostics import (
    VN_CARRYOVER_INSURER_SOURCE_FIELDS,
    VN_CARRYOVER_POLICYHOLDER_SOURCE_FIELDS,
    VU_CARRYOVER_SOURCE_FIELDS,
)
from ims.strategies import (
    STRATEGY_EXECUTION_CARRYOVER_DEFINITIONS,
    STRATEGY_EXECUTION_PERIOD_CHAIN_CONTRACT_VERSION,
    STRATEGY_EXECUTION_PERIOD_CHAIN_SECTIONS,
    STRATEGY_EXECUTION_PERIOD_CHAIN_VERSION,
    strategy_execution_period_chain_contract_payload,
)


def test_period_chain_contract_versions_horizon_and_contiguous_sequence() -> None:
    payload = strategy_execution_period_chain_contract_payload()

    assert payload["schema_version"] == (
        STRATEGY_EXECUTION_PERIOD_CHAIN_CONTRACT_VERSION
    )
    assert payload["period_chain_schema_version"] == (
        STRATEGY_EXECUTION_PERIOD_CHAIN_VERSION
    )
    assert payload["mode"] == "strategy_execution_period_chain_contract_read_only"
    assert payload["scope"] == "controlled_contiguous_local_period_chain"
    assert payload["historical_horizon"] == {
        "source": "IMSDATA.C:14",
        "constant": "SIMLAENGE",
        "maximum_periods_per_run": 100,
        "local_period_minimum": 1,
        "local_period_maximum": 100,
        "historical_result_rows_above_100_mean_separate_runs": True,
    }
    assert payload["period_sequence_policy"] == {
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
    }
    assert payload["section_count"] == 6
    assert len(STRATEGY_EXECUTION_PERIOD_CHAIN_SECTIONS) == 6


def test_period_chain_contract_reuses_only_existing_carryover_boundaries() -> None:
    payload = strategy_execution_period_chain_contract_payload()
    definitions = {
        item["carryover_id"]: item for item in payload["carryover_definitions"]
    }

    assert payload["carryover_definition_count"] == 3
    assert len(STRATEGY_EXECUTION_CARRYOVER_DEFINITIONS) == 3
    assert definitions["vu_insurer_state"]["source_fields"] == list(
        VU_CARRYOVER_SOURCE_FIELDS
    )
    assert definitions["vn_insurer_state"]["source_fields"] == list(
        VN_CARRYOVER_INSURER_SOURCE_FIELDS
    )
    assert definitions["vn_policyholder_state"]["source_fields"] == list(
        VN_CARRYOVER_POLICYHOLDER_SOURCE_FIELDS
    )
    assert definitions["vu_insurer_state"]["implementation_symbol"] == (
        "apply_vu_foreign_info_carryover"
    )
    assert definitions["vn_policyholder_state"]["implementation_symbol"] == (
        "apply_vn_state_carryover"
    )
    assert payload["carryover_policy"]["default_enabled"] is False
    assert payload["carryover_policy"]["application_order"] == ["vu", "vn"]
    assert payload["carryover_policy"]["carry_all_fields_allowed"] is False
    assert payload["carryover_policy"]["hidden_fallback_allowed"] is False


def test_period_chain_contract_requires_real_previous_result_and_stops_atomically() -> None:
    payload = strategy_execution_period_chain_contract_payload()

    previous = payload["previous_period_result_policy"]
    assert previous["source"] == (
        "immediately_previous_in_memory_explicit_period_result"
    )
    assert previous["successful_result_required"] is True
    assert previous["stored_pr131_effect_summary_accepted"] is False
    assert previous["historical_reference_row_accepted"] is False
    assert previous["synthetic_previous_result_accepted"] is False
    assert payload["stop_policy"]["validate_complete_chain_before_first_period"] is True
    assert payload["stop_policy"]["stop_after_first_failed_period"] is True
    assert payload["stop_policy"]["partial_chain_success_allowed"] is False
    assert payload["provenance_policy"]["source_result_digest_required"] is True
    assert payload["provenance_policy"]["effective_period_input_digest_required"] is True
    assert payload["provenance_policy"]["execution_provenance_stored_in_chain"] is False
    assert payload["provenance_policy"][
        "future_execution_record_references_chain_required"
    ] is True


def test_period_chain_contract_keeps_all_execution_boundaries_closed(
    monkeypatch,
) -> None:
    vu_runner = importlib.import_module("ims.engine.vu_rule_runner")
    vn_runner = importlib.import_module("ims.engine.vn_rule_runner")
    period_runner = importlib.import_module("ims.engine.explicit_period_runner")

    def fail_if_called(*args, **kwargs):
        raise AssertionError(f"operation invoked with {args!r} and {kwargs!r}")

    monkeypatch.setattr(vu_runner, "apply_vu_foreign_info_carryover", fail_if_called)
    monkeypatch.setattr(vn_runner, "apply_vn_state_carryover", fail_if_called)
    monkeypatch.setattr(period_runner, "run_loaded_explicit_period", fail_if_called)

    payload = strategy_execution_period_chain_contract_payload()

    assert payload["contract_read_only"] is True
    assert payload["period_chain_validation_enabled"] is True
    assert payload["period_chain_candidate_resolution_enabled"] is True
    assert payload["period_chain_materialization_enabled"] is True
    assert payload["period_chain_digest_enabled"] is True
    assert payload["period_chain_persistence_enabled"] is False
    assert payload["period_chain_runner_enabled"] is False
    assert payload["carryover_execution_enabled"] is False
    assert payload["multi_period_execution_enabled"] is False
    assert payload["ui_start_enabled"] is False
    assert payload["output_files_enabled"] is False
    assert payload["legacy_comparison_enabled"] is False
    assert payload["writes_performed"] is False
    assert payload["execution_performed"] is False
    assert payload["simulation_performed"] is False
    assert payload["automatic_historical_rule_selection_performed"] is False
    assert payload["historical_rng_equality_claim"] is False
    assert payload["historical_full_equality_claim"] is False
    assert payload["next_gate"] == "PR137"
