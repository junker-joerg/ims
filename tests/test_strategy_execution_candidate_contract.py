from dataclasses import fields
import importlib

from ims.io.scenario_loader import LoadedScenario
from ims.strategies import (
    STRATEGY_EXECUTION_CANDIDATE_COLLECTIONS,
    STRATEGY_EXECUTION_CANDIDATE_CONTRACT_VERSION,
    STRATEGY_EXECUTION_CANDIDATE_OPEN_REQUIREMENTS,
    STRATEGY_EXECUTION_CANDIDATE_SECTIONS,
    STRATEGY_EXECUTION_CANDIDATE_VERSION,
    VU_SNAPSHOT_MATERIALIZATION_TARGETS,
    strategy_execution_candidate_contract_payload,
)


def test_candidate_contract_versions_required_sections_and_sources() -> None:
    payload = strategy_execution_candidate_contract_payload()

    assert payload["schema_version"] == (
        STRATEGY_EXECUTION_CANDIDATE_CONTRACT_VERSION
    )
    assert payload["candidate_schema_version"] == (
        STRATEGY_EXECUTION_CANDIDATE_VERSION
    )
    assert payload["mode"] == "strategy_execution_candidate_contract_read_only"
    assert payload["scope"] == "single_period_joint_vu_vn_candidate"
    assert payload["required_section_count"] == 8
    assert {section["section_id"] for section in payload["required_sections"]} == {
        "identity",
        "contract_versions",
        "source_documents",
        "market_ground_state",
        "vu_rule_snapshots",
        "vn_rule_snapshots",
        "vn_process_snapshots",
        "execution_boundaries",
    }
    assert len(STRATEGY_EXECUTION_CANDIDATE_SECTIONS) == 8
    assert payload["authoritative_source_policy"] == {
        "original_versioned_documents_required": True,
        "server_side_rematerialization_required": True,
        "known_local_scenario_profile_required": True,
        "explicit_draws_required": True,
        "browser_materialization_reports_accepted": False,
        "free_fixture_paths_accepted": False,
        "free_output_paths_accepted": False,
    }


def test_candidate_contract_covers_loaded_scenario_snapshot_collections() -> None:
    payload = strategy_execution_candidate_contract_payload()
    collection_names = {
        definition["collection_name"] for definition in payload["collections"]
    }
    loaded_scenario_fields = {definition.name for definition in fields(LoadedScenario)}
    vu_target_collections = {
        target.snapshot_collection for target in VU_SNAPSHOT_MATERIALIZATION_TARGETS
    }

    assert payload["vu_collection_count"] == 8
    assert payload["vn_rule_collection_count"] == 1
    assert payload["vn_process_collection_count"] == 2
    assert payload["collection_count"] == 11
    assert len(STRATEGY_EXECUTION_CANDIDATE_COLLECTIONS) == 11
    assert vu_target_collections == {
        name for name in collection_names if name.startswith("vu_")
    }
    assert collection_names <= loaded_scenario_fields
    assert {
        "vn_insurance_rule_snapshots",
        "vn_damage_settlement_snapshots",
        "vn_settlement_snapshots",
    } <= collection_names
    process_collections = [
        definition
        for definition in payload["collections"]
        if definition["alternative_group"] == "vn_process"
    ]
    assert len(process_collections) == 2


def test_candidate_contract_marks_builder_complete_and_keeps_execution_open() -> None:
    payload = strategy_execution_candidate_contract_payload()

    assert payload["open_requirement_count"] == 3
    assert len(STRATEGY_EXECUTION_CANDIDATE_OPEN_REQUIREMENTS) == 3
    assert {item["planned_pr"] for item in payload["open_requirements"]} == {
        127,
        129,
        130,
    }
    assert payload["execution_anchor"] == {
        "module": "ims.engine.explicit_period_runner",
        "symbol": "run_loaded_explicit_period",
        "status": "planned_only",
    }
    assert payload["candidate_input_validation_enabled"] is True
    assert payload["scenario_profile_resolution_enabled"] is True
    assert payload["server_side_rematerialization_enabled"] is True
    assert payload["digest_calculation_enabled"] is True
    assert payload["candidate_creation_enabled"] is True
    assert payload["snapshot_loader_invocation_enabled"] is True
    assert payload["candidate_persistence_enabled"] is False
    assert payload["run_control_enabled"] is False
    assert payload["runner_enabled"] is False
    assert payload["execution_enabled"] is False
    assert payload["simulation_performed"] is False
    assert payload["historical_rng_equality_claim"] is False
    assert payload["historical_full_equality_claim"] is False
    assert payload["writes_performed"] is False


def test_candidate_contract_describes_but_does_not_invoke_builder_or_runner(
    monkeypatch,
) -> None:
    vn_materialization = importlib.import_module(
        "ims.strategies.assignment_snapshot_materialization"
    )
    vu_materialization = importlib.import_module(
        "ims.strategies.assignment_vu_snapshot_materialization"
    )
    runner = importlib.import_module("ims.engine.explicit_period_runner")

    def fail_if_called(*args, **kwargs):
        raise AssertionError(f"operation invoked with {args!r} and {kwargs!r}")

    monkeypatch.setattr(
        vn_materialization,
        "materialize_strategy_assignment_snapshots",
        fail_if_called,
    )
    monkeypatch.setattr(
        vu_materialization,
        "materialize_strategy_assignment_vu_snapshots",
        fail_if_called,
    )
    monkeypatch.setattr(runner, "run_loaded_explicit_period", fail_if_called)

    payload = strategy_execution_candidate_contract_payload()

    assert payload["snapshot_loader_invocation_enabled"] is True
    assert payload["writes_performed"] is False
