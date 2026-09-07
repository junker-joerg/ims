from copy import deepcopy
from dataclasses import replace
import importlib
import json
from pathlib import Path

import pytest

from ims.strategies import (
    STRATEGY_ASSIGNMENT_SNAPSHOT_MATERIALIZATION_CONTRACT_VERSION,
    STRATEGY_SNAPSHOT_NESTED_VALUE_DEFINITIONS,
    VN_SNAPSHOT_MATERIALIZATION_RULES,
    strategy_assignment_snapshot_materialization_contract_payload,
    strategy_snapshot_materialization_contract_issues,
    validate_strategy_assignment_snapshot_context,
)


FIXTURES = Path(__file__).parent / "fixtures"


def _fixture(name: str) -> dict[str, object]:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def test_materialization_contract_covers_all_vn_rules_and_nested_values() -> None:
    assert strategy_snapshot_materialization_contract_issues() == ()

    payload = strategy_assignment_snapshot_materialization_contract_payload()
    rules = {
        definition["strategy_id"]: definition
        for definition in payload["vn_rule_definitions"]
    }

    assert payload["schema_version"] == (
        STRATEGY_ASSIGNMENT_SNAPSHOT_MATERIALIZATION_CONTRACT_VERSION
    )
    assert set(rules) == {f"vn.vrvn{index:02d}" for index in range(1, 7)}
    assert len(payload["nested_value_definitions"]) == 9
    assert payload["contract_issue_count"] == 0
    assert payload["context_validator_uses_nested_contract"] is False
    assert payload["materialization_validation_required"] is True
    assert payload["snapshot_loader_invocation_enabled"] is True
    assert payload["snapshot_materialization_enabled"] is True
    assert payload["partial_results_allowed"] is False
    assert payload["runner_enabled"] is False
    assert payload["simulation_performed"] is False
    assert payload["historical_full_equality_claim"] is False


def test_vn_period_requirements_distinguish_initial_and_later_inputs() -> None:
    payload = strategy_assignment_snapshot_materialization_contract_payload()
    rules = {
        definition["strategy_id"]: definition
        for definition in payload["vn_rule_definitions"]
    }

    assert all(
        rule["period_one_required_fields"] == ("initial_decisions",)
        for rule in rules.values()
    )
    assert rules["vn.vrvn01"]["periods_after_one_required_fields"] == (
        "draws",
        "active_insurer_ids",
    )
    assert rules["vn.vrvn02"]["periods_after_one_required_fields"] == (
        "draws",
        "active_insurer_ids",
        "change_shock",
    )
    assert rules["vn.vrvn03"]["periods_after_one_conditional_fields"] == (
        {
            "field_name": "draws",
            "condition": "required_when_any_sector_has_no_positive_advertising",
        },
    )
    assert rules["vn.vrvn04"]["periods_after_one_conditional_fields"] == (
        {
            "field_name": "draws",
            "condition": "required_when_any_sector_has_no_prior_insured_history",
        },
    )
    assert "draws" in rules["vn.vrvn05"]["periods_after_one_required_fields"]
    assert "draws" in rules["vn.vrvn06"]["periods_after_one_not_consumed_fields"]


def test_documented_nested_samples_are_accepted_by_existing_loaders() -> None:
    fixture = _fixture(
        "strategy_assignment_snapshot_materialization_vn_context_v1.json"
    )
    assert fixture["schema_version"] == (
        STRATEGY_ASSIGNMENT_SNAPSHOT_MATERIALIZATION_CONTRACT_VERSION
    )
    samples = fixture["nested_value_samples"]

    assert set(samples) == {
        definition.schema_id
        for definition in STRATEGY_SNAPSHOT_NESTED_VALUE_DEFINITIONS
    }
    for definition in STRATEGY_SNAPSHOT_NESTED_VALUE_DEFINITIONS:
        module = importlib.import_module(definition.loader_module)
        loader = getattr(module, definition.loader_entrypoint)

        assert loader(deepcopy(samples[definition.schema_id])) is not None


def test_contract_advertises_materializer_without_invoking_snapshot_loader(
    monkeypatch,
) -> None:
    module = importlib.import_module("ims.model.vn_insurance_rules")

    def reject_invocation(value: object) -> object:
        raise AssertionError(f"snapshot loader was invoked with {value!r}")

    monkeypatch.setattr(
        module,
        "vn_insurance_rule_snapshot_from_mapping",
        reject_invocation,
    )

    payload = strategy_assignment_snapshot_materialization_contract_payload()

    assert payload["nested_values_consumed"] is True
    assert payload["snapshot_loader_invocation_enabled"] is True


def test_pr112_validator_remains_generic_until_later_integration() -> None:
    request = {
        "draft": _fixture("strategy_assignment_draft_v1.json"),
        "context": _fixture("strategy_assignment_snapshot_context_v1.json"),
    }
    request["context"]["entries"][1]["values"]["draws"] = {
        "not_a_rule_specific_draw_shape": True
    }

    report = validate_strategy_assignment_snapshot_context(request)

    assert report.valid is True
    with pytest.raises(ValueError, match="requires two draw lists"):
        module = importlib.import_module("ims.model.vn_insurance_rules")
        module.vn_sample_search_insurance_rule_draws_from_mapping(
            request["context"]["entries"][1]["values"]["draws"]
        )


def test_contract_issue_check_rejects_rule_and_loader_drift() -> None:
    wrong_rule = replace(VN_SNAPSHOT_MATERIALIZATION_RULES[0], rule_kind="random")
    wrong_nested = replace(
        STRATEGY_SNAPSHOT_NESTED_VALUE_DEFINITIONS[0],
        loader_entrypoint="missing_loader",
    )

    rule_issues = strategy_snapshot_materialization_contract_issues(
        rules=(wrong_rule, *VN_SNAPSHOT_MATERIALIZATION_RULES[1:])
    )
    loader_issues = strategy_snapshot_materialization_contract_issues(
        nested_values=(
            wrong_nested,
            *STRATEGY_SNAPSHOT_NESTED_VALUE_DEFINITIONS[1:],
        )
    )

    assert "VN-Regelart weicht ab: vn.vrvn01" in rule_issues
    assert "Verschachtelter Loader fehlt: vn.initial-decisions.v1" in loader_issues
