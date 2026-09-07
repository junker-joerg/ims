from copy import deepcopy
import importlib
import json
from pathlib import Path

from ims.strategies import (
    STRATEGY_ASSIGNMENT_SNAPSHOT_MATERIALIZATION_VALIDATION_VERSION,
    strategy_assignment_snapshot_materialization_validation_contract_payload,
    validate_strategy_assignment_snapshot_materialization_input,
)


FIXTURE = (
    Path(__file__).parent
    / "fixtures"
    / "strategy_assignment_snapshot_materialization_validation_v1.json"
)


def _request() -> dict[str, object]:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def _values(request: dict[str, object], strategy_id: str) -> dict[str, object]:
    for entry in request["context"]["entries"]:
        if entry["strategy_id"] == strategy_id:
            return entry["values"]
    raise AssertionError(f"missing strategy fixture entry: {strategy_id}")


def _issue_codes(report) -> set[str]:
    return {issue.code for issue in report.issues}


def test_complete_later_period_vn_context_is_validated_atomically() -> None:
    request = _request()

    first = validate_strategy_assignment_snapshot_materialization_input(request)
    second = validate_strategy_assignment_snapshot_materialization_input(
        deepcopy(request)
    )

    assert first.schema_version == (
        STRATEGY_ASSIGNMENT_SNAPSHOT_MATERIALIZATION_VALIDATION_VERSION
    )
    assert first.valid is True
    assert first.base_context_valid is True
    assert first.draft_id == "synthetic-pr115-vn-rules"
    assert first.period == 2
    assert first.expected_vn_entry_count == first.validated_vn_entry_count == 6
    assert first.validated_nested_value_count == 7
    assert first.nested_loader_invocation_count == 7
    assert first.to_dict() == second.to_dict()

    result = first.to_dict()
    assert result["materialization_input_valid"] is True
    assert result["context_values_inspected"] is True
    assert result["context_values_consumed"] is False
    assert result["nested_loader_results_retained"] is False
    assert result["snapshot_loader_invocation_performed"] is False
    assert result["snapshot_materialization_ready"] is False
    assert result["snapshots_created"] is False
    assert result["execution_performed"] is False
    assert result["simulation_performed"] is False


def test_period_one_validates_only_two_initial_sector_decisions() -> None:
    request = _request()
    request["context"]["period"] = 1
    initial_decisions = [
        {"sector_index": 0, "insured": True, "insurer_id": 1, "premium": 1.0},
        {"sector_index": 1, "insured": False, "insurer_id": None},
    ]
    for entry in request["context"]["entries"]:
        entry["values"]["initial_decisions"] = deepcopy(initial_decisions)
    _values(request, "vn.vrvn06")["draws"] = {"not_used_in_period_one": True}

    report = validate_strategy_assignment_snapshot_materialization_input(request)

    assert report.valid is True
    assert report.validated_vn_entry_count == 6
    assert report.validated_nested_value_count == 6
    assert report.nested_loader_invocation_count == 6


def test_base_context_failure_short_circuits_all_nested_loaders(monkeypatch) -> None:
    request = _request()
    del _values(request, "vn.vrvn01")["change_shock"]
    module = importlib.import_module("ims.model.vn_insurance_rules")

    def reject_invocation(value: object) -> object:
        raise AssertionError(f"nested loader was invoked with {value!r}")

    monkeypatch.setattr(
        module,
        "vn_compulsory_insurance_rule_draws_from_mapping",
        reject_invocation,
    )

    report = validate_strategy_assignment_snapshot_materialization_input(request)

    assert report.valid is False
    assert report.base_context_valid is False
    assert report.validated_vn_entry_count == 0
    assert report.nested_loader_invocation_count == 0
    assert report.issues[0].stage == "base_context"
    assert "context_value_missing" in _issue_codes(report)


def test_strict_nested_shapes_reject_loader_normalization_shortcuts() -> None:
    request = _request()
    _values(request, "vn.vrvn01")["draws"] = {
        "insurer_choice_draws": [0.5]
    }
    _values(request, "vn.vrvn03")["insurer_inputs"][0][
        "advertising_current_sector"
    ] = [1.0]

    report = validate_strategy_assignment_snapshot_materialization_input(request)

    assert report.valid is False
    assert report.validated_vn_entry_count == 4
    assert _issue_codes(report) == {"two_sector_values_required"}
    assert report.nested_loader_invocation_count == 5


def test_preference_and_search_require_draws_only_for_fallback_paths() -> None:
    request = _request()
    preference = _values(request, "vn.vrvn03")
    for insurer_input in preference["insurer_inputs"]:
        insurer_input["advertising_current_sector"] = [0.0, 0.0]
    search = _values(request, "vn.vrvn04")
    search["history"] = [search["history"][0]]

    report = validate_strategy_assignment_snapshot_materialization_input(request)

    conditional_issues = [
        issue
        for issue in report.issues
        if issue.code == "conditional_context_value_required"
    ]
    assert report.valid is False
    assert len(conditional_issues) == 2
    assert {issue.path for issue in conditional_issues} == {
        "$.context.entries[2].values.draws",
        "$.context.entries[3].values.draws",
    }


def test_search_history_must_precede_context_period() -> None:
    request = _request()
    _values(request, "vn.vrvn04")["history"][0]["period"] = 2

    report = validate_strategy_assignment_snapshot_materialization_input(request)

    assert report.valid is False
    assert "history_period_not_before_context" in _issue_codes(report)
    assert report.validated_vn_entry_count == 5


def test_sample_search_uses_shock_sample_size_for_draw_count() -> None:
    request = _request()
    sample_search = _values(request, "vn.vrvn05")
    sample_search["change_shock"] = True

    report = validate_strategy_assignment_snapshot_materialization_input(request)

    assert report.valid is False
    assert _issue_codes(report) == {"sample_draw_count_insufficient"}
    assert sum(
        issue.code == "sample_draw_count_insufficient" for issue in report.issues
    ) == 2


def test_required_values_ids_probabilities_and_costs_are_semantic() -> None:
    request = _request()
    _values(request, "vn.vrvn01")["active_insurer_ids"] = None
    _values(request, "vn.vrvn02")["active_insurer_ids"] = [1, 1]
    _values(request, "vn.vrvn03")["damage_probabilities"] = [-0.1, 0.2]
    _values(request, "vn.vrvn06")["information_cost_per_insurer"] = -0.01

    report = validate_strategy_assignment_snapshot_materialization_input(request)

    assert report.valid is False
    assert _issue_codes(report) == {
        "required_context_value_open",
        "active_insurer_ids_not_unique",
        "damage_probability_negative",
        "information_cost_negative",
    }
    assert report.validated_vn_entry_count == 2


def test_validation_does_not_invoke_snapshot_loader(monkeypatch) -> None:
    request = _request()
    module = importlib.import_module("ims.model.vn_insurance_rules")

    def reject_invocation(value: object) -> object:
        raise AssertionError(f"snapshot loader was invoked with {value!r}")

    monkeypatch.setattr(
        module,
        "vn_insurance_rule_snapshot_from_mapping",
        reject_invocation,
    )

    report = validate_strategy_assignment_snapshot_materialization_input(request)

    assert report.valid is True
    assert report.to_dict()["snapshot_loader_invocation_performed"] is False
    assert report.to_dict()["snapshots_created"] is False


def test_materialization_validation_contract_keeps_execution_closed() -> None:
    payload = (
        strategy_assignment_snapshot_materialization_validation_contract_payload()
    )

    assert payload["schema_version"] == (
        STRATEGY_ASSIGNMENT_SNAPSHOT_MATERIALIZATION_VALIDATION_VERSION
    )
    assert payload["validated_rule_count"] == 6
    assert payload["validated_nested_schema_count"] == 9
    assert payload["materialization_contract_issue_count"] == 0
    assert payload["partial_acceptance_allowed"] is False
    assert payload["nested_loader_invocation_enabled"] is True
    assert payload["nested_loader_results_retained"] is False
    assert payload["snapshot_loader_invocation_enabled"] is False
    assert payload["snapshot_materialization_enabled"] is False
    assert payload["execution_enabled"] is False
    assert payload["simulation_performed"] is False
    assert payload["historical_full_equality_claim"] is False
