from copy import deepcopy
import importlib
import json
from pathlib import Path

from ims.strategies import (
    STRATEGY_ASSIGNMENT_SNAPSHOT_CONTEXT_VALIDATION_VERSION,
    STRATEGY_ASSIGNMENT_SNAPSHOT_CONTEXT_VERSION,
    STRATEGY_SNAPSHOT_CONTEXT_FIELDS,
    STRATEGY_SNAPSHOT_TARGETS,
    strategy_assignment_snapshot_context_contract_payload,
    strategy_snapshot_context_contract_issues,
    validate_strategy_assignment_snapshot_context,
)


FIXTURES = Path(__file__).parent / "fixtures"


def _request_payload() -> dict[str, object]:
    return {
        "draft": json.loads(
            (FIXTURES / "strategy_assignment_draft_v1.json").read_text(
                encoding="utf-8"
            )
        ),
        "context": json.loads(
            (FIXTURES / "strategy_assignment_snapshot_context_v1.json").read_text(
                encoding="utf-8"
            )
        ),
    }


def test_snapshot_context_contract_covers_every_open_translation_field() -> None:
    assert strategy_snapshot_context_contract_issues() == ()

    expected_fields = set().union(
        *(
            set(target.unresolved_snapshot_fields)
            for target in STRATEGY_SNAPSHOT_TARGETS
        )
    )
    definitions = {
        definition.field_name: definition
        for definition in STRATEGY_SNAPSHOT_CONTEXT_FIELDS
    }
    assert set(definitions) == expected_fields
    assert len(definitions) == 18
    assert definitions["random_draws"].fixed_length == 4
    assert definitions["previous_policyholders_sector"].source == "previous_period"
    assert definitions["interest_rate"].nullable is False


def test_snapshot_context_validates_deterministically_without_consuming_values() -> None:
    request = _request_payload()

    first = validate_strategy_assignment_snapshot_context(request)
    second = validate_strategy_assignment_snapshot_context(deepcopy(request))

    assert first.schema_version == (
        STRATEGY_ASSIGNMENT_SNAPSHOT_CONTEXT_VALIDATION_VERSION
    )
    assert first.valid is True
    assert first.draft_valid is True
    assert first.translation_complete is True
    assert first.draft_id == "synthetic-pr108-example"
    assert first.period == 1
    assert first.expected_entry_count == first.validated_entry_count == 3
    assert first.expected_value_count == first.validated_value_count == 23
    assert first.resolved_value_count == 23
    assert first.explicitly_open_value_count == 0
    assert first.to_dict() == second.to_dict()

    result = first.to_dict()
    assert result["all_context_values_supplied"] is True
    assert result["context_values_consumed"] is False
    assert result["snapshot_loader_invocation_performed"] is False
    assert result["snapshot_materialization_ready"] is False
    assert result["snapshots_created"] is False
    assert result["execution_performed"] is False
    assert result["simulation_performed"] is False


def test_nullable_context_value_remains_explicitly_open() -> None:
    request = _request_payload()
    request["context"]["entries"][0]["values"]["random_draws"] = None

    report = validate_strategy_assignment_snapshot_context(request)

    assert report.valid is True
    assert report.validated_value_count == 23
    assert report.resolved_value_count == 22
    assert report.explicitly_open_value_count == 1
    assert report.to_dict()["all_context_values_supplied"] is False
    assert report.to_dict()["snapshot_materialization_ready"] is False


def test_context_requires_exact_draft_entries_and_open_fields() -> None:
    request = _request_payload()
    first_entry = request["context"]["entries"][0]
    del first_entry["values"]["interest_rate"]
    first_entry["values"]["invented_default"] = 0.0
    request["context"]["entries"][1]["strategy_id"] = "vn.vrvn06"
    request["context"]["entries"].pop()

    report = validate_strategy_assignment_snapshot_context(request)
    issue_codes = {issue.code for issue in report.issues}

    assert report.valid is False
    assert report.validated_entry_count == 0
    assert "context_value_missing" in issue_codes
    assert "context_value_unknown" in issue_codes
    assert "strategy_id_mismatch" in issue_codes
    assert "context_entry_missing" in issue_codes
    assert report.to_dict()["snapshots_created"] is False


def test_context_rejects_wrong_period_and_unambiguous_value_shapes() -> None:
    request = _request_payload()
    request["context"]["period"] = 0
    first_values = request["context"]["entries"][0]["values"]
    first_values["random_draws"] = [0.1, 0.2, 0.3]
    first_values["interest_rate"] = "0.02"
    first_values["change_shock"] = 0
    request["context"]["entries"][1]["values"]["active_insurer_ids"] = [0, 2]

    report = validate_strategy_assignment_snapshot_context(request)

    assert report.valid is False
    assert any(issue.code == "positive_integer_required" for issue in report.issues)
    assert sum(
        issue.code == "context_value_shape_invalid" for issue in report.issues
    ) == 4


def test_invalid_draft_never_yields_partially_validated_context() -> None:
    request = _request_payload()
    request["draft"]["assignments"] = []

    report = validate_strategy_assignment_snapshot_context(request)

    assert report.valid is False
    assert report.draft_valid is False
    assert report.translation_complete is False
    assert report.expected_entry_count == 0
    assert report.validated_entry_count == 0
    assert report.expected_value_count == 0
    assert any(issue.code == "draft_assignment_required" for issue in report.issues)


def test_context_validation_does_not_invoke_snapshot_loader(monkeypatch) -> None:
    vu_rules = importlib.import_module("ims.model.vu_rules")

    def reject_snapshot_materialization(mapping: dict[str, object]) -> object:
        raise AssertionError(f"Snapshotloader darf nicht aufgerufen werden: {mapping}")

    monkeypatch.setattr(
        vu_rules,
        "vu_random_uniform_rule_snapshot_from_mapping",
        reject_snapshot_materialization,
    )

    report = validate_strategy_assignment_snapshot_context(_request_payload())

    assert report.valid is True
    assert report.to_dict()["snapshot_loader_invocation_performed"] is False


def test_snapshot_context_contract_exposes_sources_and_closed_boundaries() -> None:
    payload = strategy_assignment_snapshot_context_contract_payload()

    assert payload["schema_version"] == STRATEGY_ASSIGNMENT_SNAPSHOT_CONTEXT_VERSION
    assert payload["validation_schema_version"] == (
        STRATEGY_ASSIGNMENT_SNAPSHOT_CONTEXT_VALIDATION_VERSION
    )
    assert payload["scope"] == "explicit_single_period_snapshot_context"
    assert payload["validation_request_fields"] == ("context", "draft")
    assert payload["contract_issue_count"] == 0
    assert len(payload["field_definitions"]) == 18
    assert set(payload["source_categories"]) == {
        "draw",
        "market_state",
        "period_finance",
        "previous_period",
        "shock",
        "strategy_state",
    }
    assert payload["exact_draft_entry_match_required"] is True
    assert payload["exact_open_field_match_required"] is True
    assert payload["rule_specific_nested_semantics_validated"] is False
    assert all(
        payload[key] is False
        for key in (
            "defaults_applied",
            "context_values_consumed",
            "snapshot_loader_invocation_enabled",
            "persistence_enabled",
            "snapshot_materialization_enabled",
            "execution_enabled",
            "simulation_performed",
            "historical_full_equality_claim",
        )
    )
