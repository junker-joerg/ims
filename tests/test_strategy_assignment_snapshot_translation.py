from copy import deepcopy
from dataclasses import fields
import importlib
import json
from pathlib import Path

from ims.model.vn_insurance_rules import (
    VNInsuranceRuleSnapshot,
    VNSampleSearchInsuranceRuleParameters,
)
from ims.model.vu_rules import VURandomUniformRuleParameters
from ims.strategies import (
    STRATEGY_ASSIGNMENT_SNAPSHOT_TRANSLATION_VERSION,
    STRATEGY_DEFINITIONS,
    STRATEGY_PARAMETER_SCHEMAS,
    STRATEGY_SNAPSHOT_TARGETS,
    StrategyActorType,
    strategy_assignment_snapshot_translation_contract_payload,
    strategy_snapshot_translation_issues,
    translate_strategy_assignment_draft,
)


FIXTURE = Path(__file__).parent / "fixtures" / "strategy_assignment_draft_v1.json"


def _fixture_payload() -> dict[str, object]:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def _all_strategy_payload() -> dict[str, object]:
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
    return payload


def test_snapshot_translation_contract_covers_existing_snapshot_types() -> None:
    assert strategy_snapshot_translation_issues() == ()
    assert len(STRATEGY_SNAPSHOT_TARGETS) == len(STRATEGY_DEFINITIONS) == 16

    target_by_id = {
        target.strategy_id: target for target in STRATEGY_SNAPSHOT_TARGETS
    }
    assert target_by_id["vu.vrvu07"].rule_kind == "dumping"
    assert target_by_id["vu.vrvu08"].rule_kind == "average"
    assert target_by_id["vu.vrvu09"].rule_kind == "attack"
    assert target_by_id["vn.vrvn06"].rule_kind == "best_info"
    assert target_by_id["vn.vrvn06"].snapshot_type == VNInsuranceRuleSnapshot.__name__


def test_valid_draft_translates_deterministically_to_typed_construction_plans() -> None:
    payload = _fixture_payload()

    first = translate_strategy_assignment_draft(payload)
    second = translate_strategy_assignment_draft(deepcopy(payload))

    assert first.schema_version == STRATEGY_ASSIGNMENT_SNAPSHOT_TRANSLATION_VERSION
    assert first.draft_valid is True
    assert first.translation_complete is True
    assert first.assignment_count == 3
    assert len(first.entries) == 3
    assert first.to_dict() == second.to_dict()

    vu_entry, sample_entry, compulsory_entry = first.entries
    assert isinstance(vu_entry.parameters, VURandomUniformRuleParameters)
    assert vu_entry.target.snapshot_type == "VURandomUniformRuleSnapshot"
    assert vu_entry.snapshot_payload() == {
        "insurer_id": 1,
        "parameters": payload["assignments"][0]["parameter_values"],
    }
    assert "random_draws" in vu_entry.target.unresolved_snapshot_fields
    assert isinstance(sample_entry.parameters, VNSampleSearchInsuranceRuleParameters)
    assert sample_entry.snapshot_payload()["rule_kind"] == "sample_search"
    assert compulsory_entry.parameters is None
    assert compulsory_entry.snapshot_payload()["parameters"] is None

    result = first.to_dict()
    assert result["defaults_applied"] is False
    assert result["snapshot_materialization_ready"] is False
    assert result["snapshots_created"] is False
    assert result["execution_performed"] is False
    assert result["simulation_performed"] is False


def test_every_catalog_strategy_maps_all_snapshot_fields_without_materializing() -> None:
    report = translate_strategy_assignment_draft(_all_strategy_payload())

    assert report.translation_complete is True
    assert len(report.entries) == 16
    for entry in report.entries:
        module = importlib.import_module(entry.target.snapshot_module)
        snapshot_type = getattr(module, entry.target.snapshot_type)
        snapshot_fields = {field.name for field in fields(snapshot_type)}
        provided_fields = set(entry.target.provided_snapshot_fields)
        unresolved_fields = set(entry.target.unresolved_snapshot_fields)
        assert provided_fields.isdisjoint(unresolved_fields)
        assert provided_fields | unresolved_fields == snapshot_fields
        assert set(entry.snapshot_payload()) == provided_fields
        assert entry.to_dict()["snapshot_materialized"] is False
        assert entry.to_dict()["execution_ready"] is False


def test_translation_does_not_invoke_snapshot_loaders_or_apply_implicit_defaults(
    monkeypatch,
) -> None:
    vu_rules = importlib.import_module("ims.model.vu_rules")

    def reject_snapshot_materialization(mapping: dict[str, object]) -> object:
        raise AssertionError(f"Snapshotloader darf nicht aufgerufen werden: {mapping}")

    monkeypatch.setattr(
        vu_rules,
        "vu_random_uniform_rule_snapshot_from_mapping",
        reject_snapshot_materialization,
    )
    entry = translate_strategy_assignment_draft(_fixture_payload()).entries[0]

    assert set(entry.snapshot_payload()) == {"insurer_id", "parameters"}
    assert set(entry.target.unresolved_snapshot_fields) == {
        "random_draws",
        "interest_rate",
        "change_shock",
    }


def test_translation_keeps_unknown_markup_context_explicitly_unresolved() -> None:
    payload = _all_strategy_payload()
    report = translate_strategy_assignment_draft(payload)
    entries = {entry.assignment.strategy_id: entry for entry in report.entries}

    assert entries["vu.vrvu03"].target.unresolved_snapshot_fields == (
        "reserve_thresholds",
        "interest_rate",
        "change_shock",
    )
    assert entries["vu.vrvu04"].target.unresolved_snapshot_fields == (
        "net_switcher_thresholds",
        "previous_policyholders_sector",
        "interest_rate",
        "change_shock",
    )
    assert entries["vu.vrvu05"].target.unresolved_snapshot_fields == (
        "market_share_thresholds",
        "active_policyholder_count",
        "interest_rate",
        "change_shock",
    )


def test_invalid_draft_is_not_partially_translated() -> None:
    payload = _fixture_payload()
    payload["assignments"] = []

    report = translate_strategy_assignment_draft(payload)

    assert report.draft_valid is False
    assert report.translation_complete is False
    assert report.assignment_count == 0
    assert report.entries == ()
    assert report.issues[0].code == "assignment_required"
    assert report.to_dict()["status"] == "error"


def test_translation_contract_exposes_mapping_and_closed_boundaries() -> None:
    payload = strategy_assignment_snapshot_translation_contract_payload()

    assert payload["schema_version"] == STRATEGY_ASSIGNMENT_SNAPSHOT_TRANSLATION_VERSION
    assert payload["draft_schema_version"] == "ims.strategy-assignment-draft.v1"
    assert payload["scope"] == (
        "validated_draft_to_existing_snapshot_construction_plan"
    )
    assert payload["mapping_issue_count"] == 0
    assert len(payload["strategy_mappings"]) == 16
    assert payload["partial_snapshot_payloads"] is True
    assert payload["typed_parameter_loading_enabled"] is True
    assert all(
        payload[key] is False
        for key in (
            "snapshot_loader_invocation_enabled",
            "defaults_applied",
            "persistence_enabled",
            "snapshot_materialization_enabled",
            "execution_enabled",
            "simulation_performed",
            "historical_full_equality_claim",
        )
    )
