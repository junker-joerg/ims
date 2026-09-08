from copy import deepcopy
import importlib
import json
from pathlib import Path

from ims.strategies import (
    STRATEGY_EXECUTION_CANDIDATE_INPUT_VERSION,
    STRATEGY_EXECUTION_CANDIDATE_VALIDATION_VERSION,
    strategy_execution_candidate_validation_contract_payload,
    validate_strategy_execution_candidate_input,
)


FIXTURE = (
    Path(__file__).parent
    / "fixtures"
    / "strategy_execution_candidate_input_v1.json"
)


def _request() -> dict[str, object]:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def _issue_codes(report) -> set[str]:
    return {issue.code for issue in report.issues}


def test_joint_candidate_input_is_validated_atomically_and_deterministically() -> None:
    request = _request()

    first = validate_strategy_execution_candidate_input(request)
    second = validate_strategy_execution_candidate_input(deepcopy(request))

    assert first.schema_version == STRATEGY_EXECUTION_CANDIDATE_VALIDATION_VERSION
    assert first.valid is True
    assert first.request_shape_valid is True
    assert first.vn_context_valid is True
    assert first.vu_input_valid is True
    assert first.vu_state_valid is True
    assert first.scenario_profile_reference_valid is True
    assert first.vn_process_input_valid is True
    assert first.identifiers_consistent is True
    assert first.draft_id == "synthetic-pr125-joint-candidate"
    assert first.period == 2
    assert first.expected_vu_entry_count == first.validated_vu_entry_count == 1
    assert first.expected_vn_entry_count == first.validated_vn_entry_count == 1
    assert (
        first.expected_vn_process_target_count
        == first.validated_vn_process_target_count
        == 1
    )
    assert first.to_dict() == second.to_dict()
    assert first.to_dict()["partial_candidate_returned"] is False
    assert first.to_dict()["scenario_profile_resolved"] is False
    assert first.to_dict()["candidate_created"] is False
    assert first.to_dict()["execution_performed"] is False


def test_candidate_validation_collects_cross_document_and_draw_errors() -> None:
    request = _request()
    request["scenario_profile_reference"]["period"] = 3
    request["vn_process_input"]["draft_id"] = "different-draft"
    request["vn_process_input"]["damage_settlement_snapshots"][0]["draws"][
        "amount_draws"
    ] = [0.25]

    report = validate_strategy_execution_candidate_input(request)

    assert report.valid is False
    assert report.request_shape_valid is True
    assert _issue_codes(report) == {
        "period_mismatch",
        "draft_id_mismatch",
        "two_finite_values_required",
    }
    assert report.validated_vn_process_target_count == 0
    assert report.to_dict()["partial_candidate_returned"] is False
    assert report.to_dict()["candidate_created"] is False


def test_candidate_validation_requires_exact_profile_and_process_coverage() -> None:
    request = _request()
    request["scenario_profile_reference"]["expected_insurer_ids"] = [2]
    request["vn_process_input"]["damage_settlement_snapshots"] = []

    report = validate_strategy_execution_candidate_input(request)

    assert report.valid is False
    assert _issue_codes(report) == {
        "insurer_population_mismatch",
        "vn_process_coverage_mismatch",
    }
    assert report.scenario_profile_reference_valid is False
    assert report.vn_process_input_valid is False


def test_candidate_validation_cross_checks_shared_shock_and_rejects_path_ids() -> None:
    request = _request()
    request["snapshot_context"]["entries"][1]["values"]["change_shock"] = True
    request["vn_process_input"]["damage_settlement_snapshots"][0][
        "change_shock"
    ] = True
    request["scenario_profile_reference"]["profile_id"] = "../free-fixture"

    report = validate_strategy_execution_candidate_input(request)

    assert report.valid is False
    assert _issue_codes(report) == {
        "profile_id_required",
        "shared_change_shock_mismatch",
    }
    assert report.to_dict()["scenario_profile_resolved"] is False
    assert report.to_dict()["candidate_created"] is False


def test_candidate_validation_propagates_vu_state_mismatch() -> None:
    request = _request()
    request["vu_state_provenance"]["period_state"]["interest_rate"] = 0.03

    report = validate_strategy_execution_candidate_input(request)

    assert report.valid is False
    assert report.vu_input_valid is True
    assert report.vu_state_valid is False
    assert _issue_codes(report) == {"period_state_mismatch"}
    assert report.to_dict()["candidate_created"] is False


def test_candidate_validation_rejects_duplicate_vn_process_target() -> None:
    request = _request()
    duplicate = deepcopy(
        request["vn_process_input"]["damage_settlement_snapshots"][0]
    )
    request["vn_process_input"]["damage_settlement_snapshots"].append(duplicate)

    report = validate_strategy_execution_candidate_input(request)

    assert report.valid is False
    assert _issue_codes(report) == {"duplicate_process_target"}
    assert report.validated_vn_process_target_count == 1
    assert report.to_dict()["partial_candidate_returned"] is False


def test_candidate_validation_rejects_settlement_only_and_unknown_fields() -> None:
    settlement_only = _request()
    settlement_only["vn_process_input"]["damage_settlement_snapshots"] = []
    settlement_only["vn_process_input"]["settlement_snapshots"] = [
        {"policyholder_id": 1}
    ]
    unknown_field = _request()
    unknown_field["free_fixture_path"] = "outside-the-server-profile"

    settlement_report = validate_strategy_execution_candidate_input(
        settlement_only
    )
    unknown_report = validate_strategy_execution_candidate_input(unknown_field)

    assert settlement_report.valid is False
    assert _issue_codes(settlement_report) == {
        "settlement_only_not_supported",
        "vn_process_coverage_mismatch",
    }
    assert unknown_report.request_shape_valid is False
    assert _issue_codes(unknown_report) == {"field_unknown"}
    assert unknown_report.to_dict()["candidate_created"] is False


def test_candidate_validation_does_not_invoke_snapshot_or_scenario_loaders(
    monkeypatch,
) -> None:
    vn_insurance_rules = importlib.import_module("ims.model.vn_insurance_rules")
    vu_rules = importlib.import_module("ims.model.vu_rules")
    vn_rules = importlib.import_module("ims.model.vn_rules")
    scenario_loader = importlib.import_module("ims.io.scenario_loader")
    runner = importlib.import_module("ims.engine.explicit_period_runner")

    def fail_if_called(*args, **kwargs):
        raise AssertionError(f"operation invoked with {args!r} and {kwargs!r}")

    monkeypatch.setattr(
        vn_insurance_rules,
        "vn_insurance_rule_snapshot_from_mapping",
        fail_if_called,
    )
    monkeypatch.setattr(
        vu_rules,
        "vu_random_uniform_rule_snapshot_from_mapping",
        fail_if_called,
    )
    monkeypatch.setattr(
        vn_rules,
        "vn_damage_settlement_snapshot_from_mapping",
        fail_if_called,
    )
    monkeypatch.setattr(scenario_loader, "load_scenario_from_mapping", fail_if_called)
    monkeypatch.setattr(runner, "run_loaded_explicit_period", fail_if_called)

    report = validate_strategy_execution_candidate_input(_request())

    assert report.valid is True
    assert report.to_dict()["snapshot_loader_invocation_performed"] is False
    assert report.to_dict()["scenario_profile_resolved"] is False
    assert report.to_dict()["runner_invocation_performed"] is False


def test_candidate_validation_contract_exposes_atomic_closed_boundary() -> None:
    payload = strategy_execution_candidate_validation_contract_payload()

    assert payload["schema_version"] == (
        STRATEGY_EXECUTION_CANDIDATE_VALIDATION_VERSION
    )
    assert payload["input_schema_version"] == (
        STRATEGY_EXECUTION_CANDIDATE_INPUT_VERSION
    )
    assert payload["single_shared_draft_required"] is True
    assert payload["single_shared_context_required"] is True
    assert payload["exact_profile_population_reference_required"] is True
    assert payload["complete_vn_process_target_coverage_required"] is True
    assert payload["explicit_vn_damage_draws_required"] is True
    assert payload["settlement_only_snapshots_allowed"] is False
    assert payload["partial_acceptance_allowed"] is False
    assert payload["snapshot_loader_invocation_enabled"] is False
    assert payload["scenario_profile_resolution_enabled"] is False
    assert payload["candidate_creation_enabled"] is False
    assert payload["runner_enabled"] is False
    assert payload["simulation_performed"] is False
