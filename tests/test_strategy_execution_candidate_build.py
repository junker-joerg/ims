from copy import deepcopy
from dataclasses import replace
from hashlib import sha256
import importlib
import json
from pathlib import Path

from ims.io.scenario_loader import LoadedScenario, ScenarioValidationError
from ims.strategies import (
    DEFAULT_STRATEGY_EXECUTION_SCENARIO_PROFILE_ID,
    STRATEGY_EXECUTION_CANDIDATE_BUILD_VERSION,
    STRATEGY_EXECUTION_CANDIDATE_VERSION,
    StrategyExecutionScenarioProfileDefinition,
    VUAssignmentSnapshotMaterializationIssue,
    build_default_strategy_execution_scenario_profiles,
    build_strategy_execution_candidate,
    strategy_execution_candidate_build_contract_payload,
)


ROOT = Path(__file__).resolve().parents[1]
FIXTURE_ROOT = ROOT / "tests" / "fixtures"
INPUT_FIXTURE = FIXTURE_ROOT / "strategy_execution_candidate_input_v1.json"
PROFILE_ROOT = ROOT / "python_port" / "ims" / "strategies" / "profiles"
PROFILE_FIXTURE = PROFILE_ROOT / "strategy_execution_candidate_profile_v1.json"


def _request() -> dict[str, object]:
    return json.loads(INPUT_FIXTURE.read_text(encoding="utf-8"))


def _profiles() -> dict[str, StrategyExecutionScenarioProfileDefinition]:
    return build_default_strategy_execution_scenario_profiles()


def _build(value: object):
    return build_strategy_execution_candidate(
        value,
        profiles=_profiles(),
        trusted_profile_root=PROFILE_ROOT,
    )


def _canonical_digest(value: object) -> str:
    encoded = json.dumps(
        value,
        ensure_ascii=True,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")
    return f"sha256:{sha256(encoded).hexdigest()}"


def test_builds_canonical_loaded_scenario_and_stable_digest() -> None:
    request = _request()
    unchanged = deepcopy(request)

    first = _build(request)
    second = _build(request)

    assert first.build_complete is True
    assert first.input_valid is True
    assert first.profile_resolved is True
    assert first.vu_materialization_complete is True
    assert first.vn_materialization_complete is True
    assert first.canonical_scenario_loaded is True
    assert first.vu_snapshot_count == 1
    assert first.vn_snapshot_count == 1
    assert first.vn_process_snapshot_count == 1
    assert first.rematerialization_snapshot_loader_invocation_count == 2
    assert first.issues == ()
    assert first.candidate is not None
    assert isinstance(first.candidate.loaded_scenario, LoadedScenario)
    assert first.candidate.loaded_scenario.context.period == 2
    assert [item.entity_id for item in first.candidate.loaded_scenario.insurers] == [1]
    assert [item.entity_id for item in first.candidate.loaded_scenario.policyholders] == [1]
    assert len(first.candidate.loaded_scenario.vn_insurance_rule_snapshots) == 1
    assert len(first.candidate.loaded_scenario.vn_damage_settlement_snapshots) == 1
    assert first.candidate.loaded_scenario.vn_settlement_snapshots == []
    assert first.to_dict() == second.to_dict()
    assert request == unchanged

    payload = first.candidate.to_dict()
    identity = payload["identity"]
    basis = {
        "candidate_schema_version": payload["schema_version"],
        "draft_id": identity["draft_id"],
        "period": identity["period"],
        **{
            key: value
            for key, value in payload.items()
            if key not in {"schema_version", "mode", "identity"}
        },
    }
    assert payload["schema_version"] == STRATEGY_EXECUTION_CANDIDATE_VERSION
    assert identity["content_digest"] == _canonical_digest(basis)
    digest_hex = identity["content_digest"].removeprefix("sha256:")
    assert identity["candidate_id"] == f"strategy-candidate-{digest_hex[:24]}"


def test_canonicalizes_assignment_and_context_collection_order() -> None:
    original = _request()
    reordered = deepcopy(original)
    reordered["assignment_draft"]["assignments"].reverse()
    reordered["snapshot_context"]["entries"].reverse()

    original_report = _build(original)
    reordered_report = _build(reordered)

    assert original_report.build_complete is True
    assert reordered_report.build_complete is True
    assert original_report.candidate is not None
    assert reordered_report.candidate is not None
    assert (
        original_report.candidate.content_digest
        == reordered_report.candidate.content_digest
    )


def test_invalid_input_stops_before_profile_and_materializers(monkeypatch) -> None:
    module = importlib.import_module(
        "ims.strategies.execution_candidate_build"
    )

    def reject_invocation(*args: object, **kwargs: object) -> object:
        raise AssertionError(f"operation invoked with {args!r} {kwargs!r}")

    monkeypatch.setattr(module, "_resolve_profile", reject_invocation)
    monkeypatch.setattr(
        module,
        "materialize_strategy_assignment_vu_snapshots",
        reject_invocation,
    )
    monkeypatch.setattr(
        module,
        "materialize_strategy_assignment_snapshots",
        reject_invocation,
    )
    request = _request()
    request["vn_process_input"]["period"] = 3

    report = _build(request)

    assert report.build_complete is False
    assert report.input_valid is False
    assert report.profile_resolved is False
    assert report.rematerialization_attempted is False
    assert report.rematerialization_snapshot_loader_invocation_count == 0
    assert report.candidate is None
    assert report.to_dict()["partial_candidate_returned"] is False


def test_unknown_profile_stops_before_materializers(monkeypatch) -> None:
    module = importlib.import_module(
        "ims.strategies.execution_candidate_build"
    )

    def reject_invocation(*args: object, **kwargs: object) -> object:
        raise AssertionError(f"materializer invoked with {args!r} {kwargs!r}")

    monkeypatch.setattr(
        module,
        "materialize_strategy_assignment_vu_snapshots",
        reject_invocation,
    )
    monkeypatch.setattr(
        module,
        "materialize_strategy_assignment_snapshots",
        reject_invocation,
    )
    request = _request()
    request["scenario_profile_reference"]["profile_id"] = "unknown-profile"

    report = _build(request)

    assert report.input_valid is True
    assert report.profile_resolved is False
    assert report.candidate is None
    assert [issue.code for issue in report.issues] == [
        "unknown_scenario_profile"
    ]


def test_profile_population_mismatch_returns_no_candidate(tmp_path) -> None:
    profile = json.loads(PROFILE_FIXTURE.read_text(encoding="utf-8"))
    profile["insurers"][0]["entity_id"] = 2
    profile["policyholders"][0]["insurer_id"] = 2
    profile["policyholders"][0]["chosen_insurer_current"] = 2
    profile["policyholders"][0]["chosen_insurer_sector_current"] = [2, None]
    profile_path = tmp_path / "profile.json"
    profile_path.write_text(json.dumps(profile), encoding="utf-8")
    profiles = {
        DEFAULT_STRATEGY_EXECUTION_SCENARIO_PROFILE_ID: (
            StrategyExecutionScenarioProfileDefinition(
                profile_id=DEFAULT_STRATEGY_EXECUTION_SCENARIO_PROFILE_ID,
                path=profile_path,
            )
        )
    }

    report = build_strategy_execution_candidate(
        _request(),
        profiles=profiles,
        trusted_profile_root=tmp_path,
    )

    assert report.build_complete is False
    assert report.profile_resolved is False
    assert report.rematerialization_attempted is False
    assert report.candidate is None
    assert [issue.code for issue in report.issues] == [
        "scenario_profile_insurer_population_mismatch"
    ]


def test_final_scenario_loader_failure_returns_no_partial_candidate(
    monkeypatch,
) -> None:
    module = importlib.import_module(
        "ims.strategies.execution_candidate_build"
    )
    original = module.load_scenario_from_mapping
    invocation_count = 0

    def fail_second_load(value: dict[str, object]) -> LoadedScenario:
        nonlocal invocation_count
        invocation_count += 1
        if invocation_count == 2:
            raise ScenarioValidationError("synthetic final load failure")
        return original(value)

    monkeypatch.setattr(module, "load_scenario_from_mapping", fail_second_load)

    report = _build(_request())

    assert invocation_count == 2
    assert report.input_valid is True
    assert report.profile_resolved is True
    assert report.vu_materialization_complete is True
    assert report.vn_materialization_complete is True
    assert report.canonical_scenario_loaded is False
    assert report.candidate is None
    assert report.to_dict()["digest_calculation_performed"] is False
    assert report.to_dict()["partial_candidate_returned"] is False
    assert [issue.code for issue in report.issues] == [
        "canonical_scenario_loader_rejected"
    ]


def test_materialization_failure_discards_joint_candidate(monkeypatch) -> None:
    module = importlib.import_module(
        "ims.strategies.execution_candidate_build"
    )
    original = module.materialize_strategy_assignment_vu_snapshots

    def fail_after_validation(value: object):
        report = original(value)
        return replace(
            report,
            snapshots=(),
            issues=(
                VUAssignmentSnapshotMaterializationIssue(
                    stage="snapshot_loader",
                    path="$.input.context.entries[0]",
                    code="snapshot_loader_rejected",
                    message="synthetic materialization failure",
                ),
            ),
        )

    monkeypatch.setattr(
        module,
        "materialize_strategy_assignment_vu_snapshots",
        fail_after_validation,
    )

    report = _build(_request())

    assert report.profile_resolved is True
    assert report.rematerialization_attempted is True
    assert report.vu_materialization_complete is False
    assert report.vn_materialization_complete is True
    assert report.candidate is None
    assert report.to_dict()["snapshots_created"] is False
    assert report.to_dict()["digest_calculation_performed"] is False
    assert report.to_dict()["partial_candidate_returned"] is False
    assert [issue.code for issue in report.issues] == [
        "snapshot_loader_rejected"
    ]


def test_candidate_build_does_not_invoke_runner(monkeypatch) -> None:
    runner = importlib.import_module("ims.engine.explicit_period_runner")

    def reject_execution(*args: object, **kwargs: object) -> object:
        raise AssertionError(f"runner invoked with {args!r} {kwargs!r}")

    monkeypatch.setattr(runner, "run_loaded_explicit_period", reject_execution)

    report = _build(_request())

    assert report.build_complete is True
    payload = report.to_dict()
    assert payload["candidate_persisted"] is False
    assert payload["writes_performed"] is False
    assert payload["run_control_connected"] is False
    assert payload["runner_invocation_performed"] is False
    assert payload["execution_performed"] is False
    assert payload["simulation_performed"] is False
    json.dumps(payload, allow_nan=False, sort_keys=True)


def test_candidate_build_contract_opens_only_pr126_capabilities() -> None:
    payload = strategy_execution_candidate_build_contract_payload()

    assert payload["schema_version"] == STRATEGY_EXECUTION_CANDIDATE_BUILD_VERSION
    assert payload["known_profile_ids"] == [
        DEFAULT_STRATEGY_EXECUTION_SCENARIO_PROFILE_ID
    ]
    assert payload["profile_source_policy"] == "server_registry_only"
    assert payload["free_profile_paths_accepted"] is False
    assert payload["server_side_rematerialization_enabled"] is True
    assert payload["canonical_loaded_scenario_enabled"] is True
    assert payload["digest_calculation_enabled"] is True
    assert payload["candidate_creation_enabled"] is True
    assert payload["candidate_persistence_enabled"] is False
    assert payload["run_control_enabled"] is False
    assert payload["runner_enabled"] is False
    assert payload["simulation_performed"] is False
