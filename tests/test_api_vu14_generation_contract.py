import json
from pathlib import Path

from ims.api.vu14_generation_contract import (
    build_vu14_generation_contract_report,
    main,
)


REPO_ROOT = Path(__file__).resolve().parent.parent
CONTRACT_PATH = REPO_ROOT / "tests" / "fixtures" / "vu14_100_period_generation_contract.json"
PLAN_DOC = REPO_ROOT / "docs" / "plans" / "vu14_generation_contract_plan.md"
MIGRATION_DOC = REPO_ROOT / "docs" / "migration" / "vu14_100_period_generation_contract.md"


def _contract_data() -> dict:
    return json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))


def test_vu14_generation_contract_prepares_exact_100_period_target() -> None:
    report = build_vu14_generation_contract_report(REPO_ROOT)
    payload = report.to_dict()

    assert payload["status"] == "prepared"
    assert payload["contract_version"] == "pr72-v1"
    assert payload["target"] == {
        "subject_type": "insurer",
        "level": "I",
        "selector_kind": "entity",
        "selector_value": 14,
        "export_filename": "imsvu014.dat",
        "legacy_reference": "VU14L1.DAT",
        "period_start": 1,
        "period_end": 100,
        "period_count": 100,
    }
    assert payload["required_period_count"] == 100
    assert payload["contract_ready"] is True
    assert payload["issues"] == []


def test_vu14_generation_contract_requires_provenance_for_every_input_group() -> None:
    report = build_vu14_generation_contract_report(REPO_ROOT)
    payload = report.to_dict()

    assert payload["input_requirement_count"] == 6
    assert payload["currently_evidenced_input_requirement_count"] == 4
    assert [item["code"] for item in payload["input_requirements"]] == [
        "complete_population_origin",
        "initial_state_origin",
        "vu14_rule_schedule_origin",
        "rng_stream_origin",
        "state_transition_origin",
        "policyholder_claim_origin",
    ]
    assert all(item["origin_required"] is True for item in payload["input_requirements"])
    assert [
        item["code"] for item in payload["input_requirements"] if item["currently_evidenced"]
    ] == [
        "complete_population_origin",
        "initial_state_origin",
        "vu14_rule_schedule_origin",
        "state_transition_origin",
    ]
    assert payload["source_evidence_count"] == 10
    assert payload["source_binding"]["status"] == "source_bound"
    assert payload["source_binding"]["independent_period_one_ready"] is True
    assert payload["population_builder"]["status"] == "population_built"
    assert payload["population_builder"]["population_ready"] is True
    assert payload["population_builder"]["summary"]["insurer_count"] == 25
    assert payload["population_builder"]["summary"]["policyholder_count"] == 200


def test_vu14_generation_contract_rejects_existing_output_echo_as_generation_input() -> None:
    report = build_vu14_generation_contract_report(REPO_ROOT)
    payload = report.to_dict()
    existing = payload["existing_slice"]

    assert existing["periods"] == [1, 2, 3, 4]
    assert existing["direct_output_update_fields"] == [
        "premiums_current",
        "advertising_current",
        "reserves_current",
        "policyholders_current",
        "claims_count_current",
        "claims_sum_current",
    ]
    assert existing["output_projection_connected"] is True
    assert existing["independent_state_evolution"] is False
    assert existing["acceptable_as_generation_input"] is False
    assert payload["forbidden_input_kinds"] == [
        "legacy_export_rows",
        "calculated_export_echo",
        "period_by_period_output_state_updates",
    ]


def test_vu14_generation_contract_keeps_generation_and_release_blocked() -> None:
    payload = build_vu14_generation_contract_report(REPO_ROOT).to_dict()

    assert payload["generation_blocker_codes"] == [
        "rng_stream_origin_missing",
        "policyholder_claim_origin_missing",
        "independent_periods_2_100_missing",
        "independent_100_period_export_missing",
    ]
    assert payload["generation_ready"] is False
    assert payload["independent_full_window_ready"] is False
    assert payload["production_release_approved"] is False
    assert payload["writes_performed"] is False
    assert payload["execution_performed"] is False
    assert payload["runner_started"] is False
    assert payload["simulation_performed"] is False
    assert payload["automatic_historical_rule_selection_performed"] is False
    assert payload["historical_full_equality_claimed"] is False


def test_vu14_generation_contract_detects_period_contract_drift(tmp_path: Path) -> None:
    contract = _contract_data()
    contract["target"]["period_end"] = 99
    contract["target"]["period_count"] = 99
    path = tmp_path / "bad_period_contract.json"
    path.write_text(json.dumps(contract), encoding="utf-8")

    report = build_vu14_generation_contract_report(REPO_ROOT, contract_path=path)

    assert report.status == "error"
    assert "target_period_contract_mismatch" in {issue.code for issue in report.issues}


def test_vu14_generation_contract_serializes_malformed_target(tmp_path: Path) -> None:
    contract = _contract_data()
    contract["target"] = {"export_filename": "wrong.dat"}
    path = tmp_path / "bad_target_contract.json"
    path.write_text(json.dumps(contract), encoding="utf-8")

    payload = build_vu14_generation_contract_report(
        REPO_ROOT,
        contract_path=path,
    ).to_dict()

    assert payload["status"] == "error"
    assert payload["target"]["export_filename"] == "imsvu014.dat"
    assert payload["required_period_count"] == 100
    assert "target_period_contract_mismatch" in {
        issue["code"] for issue in payload["issues"]
    }


def test_vu14_generation_contract_detects_missing_input_origin_boundary(tmp_path: Path) -> None:
    contract = _contract_data()
    contract["input_requirements"][2]["origin_required"] = False
    path = tmp_path / "bad_origin_contract.json"
    path.write_text(json.dumps(contract), encoding="utf-8")

    report = build_vu14_generation_contract_report(REPO_ROOT, contract_path=path)

    assert report.status == "error"
    assert "input_origin_requirement_missing" in {issue.code for issue in report.issues}


def test_vu14_generation_contract_cli_is_read_only(capsys) -> None:
    exit_code = main(["--repo-root", str(REPO_ROOT)])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["status"] == "prepared"
    assert payload["contract_ready"] is True
    assert payload["generation_ready"] is False
    assert payload["execution_performed"] is False
    assert payload["simulation_performed"] is False


def test_vu14_generation_contract_documents_origin_and_remaining_plan() -> None:
    plan = PLAN_DOC.read_text(encoding="utf-8")
    migration = MIGRATION_DOC.read_text(encoding="utf-8")

    assert "IMSDATA.C:94-103" in plan
    assert "IMS.E:1045-1063" in plan
    assert "IMS.E:402-446" in plan
    assert "periodengenauem Output-Echo" in plan
    assert "contract_ready = true" in migration
    assert "generation_ready = false" in migration
    assert "acceptable_as_generation_input = false" in migration
    assert "mindestens acht reviewbare Schritte" in migration
    assert "Eine fachliche Freigabe" in migration
    assert "weder aus PR 72" in migration
