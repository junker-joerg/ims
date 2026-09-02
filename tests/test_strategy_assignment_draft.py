from copy import deepcopy
import json
from pathlib import Path

import pytest

from ims.strategies import (
    STRATEGY_ASSIGNMENT_DRAFT_VALIDATION_VERSION,
    STRATEGY_ASSIGNMENT_DRAFT_VERSION,
    STRATEGY_DEFINITIONS,
    STRATEGY_PARAMETER_SCHEMAS,
    StrategyActorType,
    load_strategy_assignment_draft,
    strategy_assignment_draft_contract_payload,
    validate_strategy_assignment_draft,
)


FIXTURE = Path(__file__).parent / "fixtures" / "strategy_assignment_draft_v1.json"


def _fixture_payload() -> dict[str, object]:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def _issue_codes(payload: dict[str, object]) -> set[str]:
    report = validate_strategy_assignment_draft(payload)
    return {issue.code for issue in report.issues}


def test_synthetic_assignment_draft_validates_and_loads_without_execution() -> None:
    payload = _fixture_payload()

    report = validate_strategy_assignment_draft(payload)
    draft = load_strategy_assignment_draft(payload)

    assert report.schema_version == STRATEGY_ASSIGNMENT_DRAFT_VALIDATION_VERSION
    assert report.valid is True
    assert report.assignment_count == 3
    assert report.validated_assignment_count == 3
    assert report.issues == ()
    assert draft.schema_version == STRATEGY_ASSIGNMENT_DRAFT_VERSION
    assert draft.to_dict() == payload
    assert draft.assignments[0].parameter_values is not None
    assert draft.assignments[1].parameter_values is not None
    assert draft.assignments[2].parameter_schema is None
    assert draft.assignments[2].parameter_values is None


def test_draft_contract_exposes_versions_targets_and_closed_boundaries() -> None:
    payload = strategy_assignment_draft_contract_payload()

    assert payload["schema_version"] == STRATEGY_ASSIGNMENT_DRAFT_VERSION
    assert payload["catalog_schema_version"] == "ims.strategy-catalog.v1"
    assert payload["assignment_contract_schema_version"] == (
        "ims.strategy-assignment-contract.v1"
    )
    assert payload["base_model"] == "Vdefmd6"
    assert payload["scope"] == "partial_actor_assignments"
    assert payload["target_limits"] == {
        "insurer": {"minimum": 1, "maximum": 25},
        "policyholder": {"minimum": 1, "maximum": 200},
    }
    assert payload["parameter_value_shape"]["length"] == 2
    assert payload["parameterless_strategy_ids"] == ("vn.vrvn01",)
    assert all(
        payload[key] is False
        for key in (
            "unknown_fields_allowed",
            "defaults_applied",
            "persistence_enabled",
            "workbench_editing_enabled",
            "snapshot_translation_enabled",
            "execution_enabled",
            "simulation_performed",
            "historical_full_equality_claim",
        )
    )


def test_draft_validates_every_catalog_strategy_against_its_existing_loader() -> None:
    payload = _fixture_payload()
    schema_by_id = {
        schema.schema_id: schema for schema in STRATEGY_PARAMETER_SCHEMAS
    }
    actor_counts = {
        StrategyActorType.INSURER: 0,
        StrategyActorType.POLICYHOLDER: 0,
    }
    assignments: list[dict[str, object]] = []
    for strategy in STRATEGY_DEFINITIONS:
        actor_counts[strategy.actor_type] += 1
        schema = (
            schema_by_id[strategy.parameter_schema]
            if strategy.parameter_schema is not None
            else None
        )
        assignments.append(
            {
                "actor_type": strategy.actor_type,
                "target_id": actor_counts[strategy.actor_type],
                "strategy_id": strategy.strategy_id,
                "activation_period": 1,
                "active_through_run": 100,
                "logical_time": 1,
                "parameter_schema": strategy.parameter_schema,
                "parameter_values": (
                    None
                    if schema is None
                    else {
                        field.field_name: [0, 0]
                        for field in schema.fields
                    }
                ),
            }
        )
    payload["assignments"] = assignments

    report = validate_strategy_assignment_draft(payload)

    assert report.valid is True
    assert report.assignment_count == 16
    assert report.validated_assignment_count == 16
    assert report.issues == ()


def test_draft_rejects_version_drift_and_unknown_document_fields() -> None:
    payload = _fixture_payload()
    payload["schema_version"] = "ims.strategy-assignment-draft.v2"
    payload["future_option"] = True

    assert _issue_codes(payload) == {
        "contract_value_mismatch",
        "draft_field_unknown",
    }


def test_draft_rejects_duplicate_out_of_range_and_actor_mismatch() -> None:
    payload = _fixture_payload()
    assignments = payload["assignments"]
    assert isinstance(assignments, list)
    assignments.append(deepcopy(assignments[0]))
    first = assignments[0]
    assert isinstance(first, dict)
    first["target_id"] = 26
    first["actor_type"] = "policyholder"
    first["target_id"] = 201

    codes = _issue_codes(payload)

    assert "target_out_of_vdefmd6_range" in codes
    assert "strategy_actor_mismatch" in codes
    assert "duplicate_actor_assignment" not in codes

    duplicate_payload = _fixture_payload()
    duplicate_assignments = duplicate_payload["assignments"]
    assert isinstance(duplicate_assignments, list)
    duplicate_assignments.append(deepcopy(duplicate_assignments[0]))
    assert "duplicate_actor_assignment" in _issue_codes(duplicate_payload)


def test_draft_rejects_parameter_schema_fields_and_vector_drift() -> None:
    payload = _fixture_payload()
    assignments = payload["assignments"]
    assert isinstance(assignments, list)
    vu = assignments[0]
    assert isinstance(vu, dict)
    vu["parameter_schema"] = "VUForeignInfoRuleParameters"
    values = vu["parameter_values"]
    assert isinstance(values, dict)
    values.pop("premium_factor_normal")
    values["unsupported"] = [1.0, 1.0]
    values["advertising_factor_normal"] = [1.0]

    codes = _issue_codes(payload)

    assert "parameter_schema_mismatch" in codes
    assert "parameter_field_missing" in codes
    assert "parameter_field_unknown" in codes
    assert "legacy_two_position_vector_required" in codes


def test_draft_rejects_invalid_sample_sizes_and_parameterless_values() -> None:
    payload = _fixture_payload()
    assignments = payload["assignments"]
    assert isinstance(assignments, list)
    sample = assignments[1]
    compulsory = assignments[2]
    assert isinstance(sample, dict)
    assert isinstance(compulsory, dict)
    sample_values = sample["parameter_values"]
    assert isinstance(sample_values, dict)
    sample_values["sample_sizes_normal"] = [-1, 2.5]
    compulsory["parameter_values"] = {}

    codes = _issue_codes(payload)

    assert "existing_parameter_bound_failed" in codes
    assert "integer_required" in codes
    assert "parameter_values_not_supported" in codes


def test_draft_rejects_empty_assignment_list_and_loader_reports_paths() -> None:
    payload = _fixture_payload()
    payload["assignments"] = []

    report = validate_strategy_assignment_draft(payload)

    assert report.valid is False
    assert report.assignment_count == 0
    assert report.validated_assignment_count == 0
    assert report.issues[0].path == "$.assignments"
    assert report.issues[0].code == "assignment_required"
    with pytest.raises(ValueError, match=r"\$\.assignments"):
        load_strategy_assignment_draft(payload)
