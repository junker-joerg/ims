from copy import deepcopy
import importlib
import json
from pathlib import Path

from ims.strategies import (
    STRATEGY_EXECUTION_PERIOD_CHAIN_INPUT_VERSION,
    STRATEGY_EXECUTION_PERIOD_CHAIN_VALIDATION_VERSION,
    strategy_execution_candidate_id_from_digest,
    strategy_execution_period_chain_validation_contract_payload,
    validate_strategy_execution_period_chain_input,
)


FIXTURE = (
    Path(__file__).parent
    / "fixtures"
    / "strategy_execution_period_chain_input_v1.json"
)


def _request() -> dict[str, object]:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def _issue_codes(report) -> set[str]:
    return {issue.code for issue in report.issues}


def test_period_chain_input_is_validated_atomically_and_deterministically() -> None:
    request = _request()

    first = validate_strategy_execution_period_chain_input(request)
    second = validate_strategy_execution_period_chain_input(deepcopy(request))

    assert first.schema_version == STRATEGY_EXECUTION_PERIOD_CHAIN_VALIDATION_VERSION
    assert first.valid is True
    assert first.request_shape_valid is True
    assert first.horizon_valid is True
    assert first.candidate_references_valid is True
    assert first.transitions_valid is True
    assert first.identifiers_consistent is True
    assert first.run_index == 0
    assert first.max_periods == 2
    assert first.first_period == 1
    assert first.last_period == 2
    assert first.expected_candidate_count == first.validated_candidate_count == 2
    assert first.expected_transition_count == first.validated_transition_count == 1
    assert first.vu_carryover_transition_count == 1
    assert first.vn_carryover_transition_count == 1
    assert first.to_dict() == second.to_dict()
    assert first.to_dict()["partial_chain_returned"] is False
    assert first.to_dict()["candidate_storage_resolved"] is False
    assert first.to_dict()["period_chain_created"] is False
    assert first.to_dict()["execution_performed"] is False


def test_period_chain_validation_accepts_complete_100_period_horizon() -> None:
    request = _request()
    request["max_periods"] = 100
    request["period_candidates"] = []
    for period in range(1, 101):
        digest = f"sha256:{period:02x}{'0' * 62}"
        request["period_candidates"].append(
            {
                "candidate_id": strategy_execution_candidate_id_from_digest(
                    digest
                ),
                "content_digest": digest,
                "period": period,
            }
        )
    request["transitions"] = [
        {
            "from_period": period,
            "to_period": period + 1,
            "carry_forward_vu_state": True,
            "carry_forward_vn_state": True,
        }
        for period in range(1, 100)
    ]

    report = validate_strategy_execution_period_chain_input(request)

    assert report.valid is True
    assert report.first_period == 1
    assert report.last_period == 100
    assert report.validated_candidate_count == 100
    assert report.validated_transition_count == 99


def test_period_chain_validation_rejects_incomplete_and_unordered_horizon() -> None:
    request = _request()
    request["max_periods"] = 3
    request["period_candidates"][0]["period"] = 2
    request["period_candidates"][1]["period"] = 1

    report = validate_strategy_execution_period_chain_input(request)

    assert report.valid is False
    assert report.horizon_valid is False
    assert _issue_codes(report) == {
        "candidate_count_mismatch",
        "period_sequence_mismatch",
        "transition_count_mismatch",
    }
    assert report.to_dict()["partial_chain_returned"] is False


def test_period_chain_validation_rejects_bad_identity_and_duplicate_digest() -> None:
    request = _request()
    request["period_candidates"][1]["candidate_id"] = (
        request["period_candidates"][0]["candidate_id"]
    )
    request["period_candidates"][1]["content_digest"] = (
        request["period_candidates"][0]["content_digest"]
    )

    report = validate_strategy_execution_period_chain_input(request)

    assert report.valid is False
    assert report.identifiers_consistent is False
    assert _issue_codes(report) == {
        "duplicate_candidate_id",
        "duplicate_content_digest",
    }
    assert report.validated_candidate_count == 1
    assert report.to_dict()["candidate_content_digest_reverified"] is False


def test_period_chain_validation_rejects_non_adjacent_and_implicit_carryover() -> None:
    request = _request()
    transition = request["transitions"][0]
    transition["to_period"] = 3
    transition["carry_forward_vn_state"] = 1

    report = validate_strategy_execution_period_chain_input(request)

    assert report.valid is False
    assert report.transitions_valid is False
    assert _issue_codes(report) == {
        "boolean_required",
        "non_adjacent_transition",
        "transition_sequence_mismatch",
    }
    assert report.vn_carryover_transition_count == 0
    assert report.to_dict()["carryover_invocation_performed"] is False


def test_period_chain_validation_rejects_horizon_above_100_and_unknown_path() -> None:
    request = _request()
    request["max_periods"] = 101
    request["output_dir"] = "outside"

    report = validate_strategy_execution_period_chain_input(request)

    assert report.valid is False
    assert report.request_shape_valid is False
    assert report.horizon_valid is False
    assert _issue_codes(report) == {"field_unknown", "integer_range_required"}
    assert report.to_dict()["writes_performed"] is False


def test_period_chain_validation_does_not_resolve_build_carry_or_run(
    monkeypatch,
) -> None:
    store = importlib.import_module("ims.api.strategy_execution_candidate_store")
    builder = importlib.import_module("ims.strategies.execution_candidate_build")
    vu_runner = importlib.import_module("ims.engine.vu_rule_runner")
    vn_runner = importlib.import_module("ims.engine.vn_rule_runner")
    period_runner = importlib.import_module("ims.engine.explicit_period_runner")

    def fail_if_called(*args, **kwargs):
        raise AssertionError(f"operation invoked with {args!r} and {kwargs!r}")

    monkeypatch.setattr(store, "get_strategy_execution_candidate", fail_if_called)
    monkeypatch.setattr(builder, "build_strategy_execution_candidate", fail_if_called)
    monkeypatch.setattr(vu_runner, "apply_vu_foreign_info_carryover", fail_if_called)
    monkeypatch.setattr(vn_runner, "apply_vn_state_carryover", fail_if_called)
    monkeypatch.setattr(period_runner, "run_loaded_explicit_period", fail_if_called)

    report = validate_strategy_execution_period_chain_input(_request())

    assert report.valid is True
    assert report.to_dict()["candidate_storage_resolved"] is False
    assert report.to_dict()["candidate_context_cross_checked"] is False
    assert report.to_dict()["carryover_invocation_performed"] is False
    assert report.to_dict()["runner_invocation_performed"] is False


def test_period_chain_validation_contract_exposes_atomic_closed_boundary() -> None:
    payload = strategy_execution_period_chain_validation_contract_payload()

    assert payload["schema_version"] == (
        STRATEGY_EXECUTION_PERIOD_CHAIN_VALIDATION_VERSION
    )
    assert payload["input_schema_version"] == (
        STRATEGY_EXECUTION_PERIOD_CHAIN_INPUT_VERSION
    )
    assert payload["minimum_period_count"] == 2
    assert payload["maximum_period_count"] == 100
    assert payload["complete_horizon_required"] is True
    assert payload["explicit_carryover_flags_required"] is True
    assert payload["partial_acceptance_allowed"] is False
    assert payload["candidate_storage_resolution_enabled"] is False
    assert payload["candidate_context_cross_check_enabled"] is False
    assert payload["period_chain_creation_enabled"] is False
    assert payload["carryover_invocation_enabled"] is False
    assert payload["runner_enabled"] is False
    assert payload["simulation_performed"] is False
    assert payload["next_gate"] == "PR139"
