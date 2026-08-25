import json
from pathlib import Path

from ims.api.vdefmd6_vu_aggregate_run_report import (
    DEFAULT_REFERENCE_PATHS,
    build_vdefmd6_vu_aggregate_run_report,
    main,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = (
    REPO_ROOT / "tests" / "fixtures" / "vdefmd6_vu_aggregate_run_contract.json"
)
PLAN_PATH = REPO_ROOT / "docs" / "plans" / "vdefmd6_vu_aggregate_run_plan.md"
MIGRATION_PATH = (
    REPO_ROOT / "docs" / "migration" / "vdefmd6_vu_aggregate_run_contract.md"
)


def test_vdefmd6_vu_aggregate_report_classifies_four_targets() -> None:
    payload = build_vdefmd6_vu_aggregate_run_report(REPO_ROOT).to_dict()
    targets = {
        item["export_filename"]: item for item in payload["target_summaries"]
    }

    assert payload["status"] == "vu_aggregate_path_classified"
    assert payload["contract_version"] == "pr82-v1"
    assert payload["aggregate_target_count"] == 4
    assert payload["source_anchor_count"] == 12
    assert targets["imsvusk1.dat"]["reference_filename"] == "VUSK1L5.DAT"
    assert targets["imsvusk1.dat"]["matched_field_count"] == 232
    assert targets["imsvuvk1.dat"]["matched_field_count"] == 229
    assert targets["imsvuvk2.dat"]["first_full_state_divergence_period"] == 1
    assert targets["imsvuvk3.dat"]["matched_field_count"] == 215
    assert payload["historical_vu_class_accumulator_compatibility_applied"] is False
    assert payload["historical_full_equality_claimed"] is False
    assert payload["production_release_approved"] is False
    assert payload["issues"] == []


def test_vdefmd6_vu_aggregate_report_rejects_contract_drift(tmp_path: Path) -> None:
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    contract["expected_targets"][0]["matched_field_count"] = 1400
    path = tmp_path / "contract.json"
    path.write_text(json.dumps(contract), encoding="utf-8")

    payload = build_vdefmd6_vu_aggregate_run_report(
        REPO_ROOT,
        contract_path=path,
    ).to_dict()

    assert payload["status"] == "error"
    assert "expected_targets_mismatch" in {
        item["code"] for item in payload["issues"]
    }


def test_vdefmd6_vu_aggregate_report_rejects_missing_reference(
    tmp_path: Path,
) -> None:
    references = dict(DEFAULT_REFERENCE_PATHS)
    references["imsvuvk2.dat"] = tmp_path / "missing.dat"

    payload = build_vdefmd6_vu_aggregate_run_report(
        REPO_ROOT,
        reference_paths=references,
    ).to_dict()

    assert payload["status"] == "error"
    assert "reference_comparison_failed" in {
        item["code"] for item in payload["issues"]
    }


def test_vdefmd6_vu_aggregate_report_rejects_wrong_reference_target_set(
    tmp_path: Path,
) -> None:
    payload = build_vdefmd6_vu_aggregate_run_report(
        REPO_ROOT,
        reference_paths={"unexpected.dat": tmp_path / "missing.dat"},
    ).to_dict()

    assert payload["status"] == "error"
    assert "reference_target_set_mismatch" in {
        item["code"] for item in payload["issues"]
    }


def test_vdefmd6_vu_aggregate_report_cli(capsys) -> None:
    exit_code = main(["--repo-root", str(REPO_ROOT)])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["status"] == "vu_aggregate_path_classified"
    assert payload["writes_performed"] is False
    assert payload["simulation_performed"] is False


def test_vdefmd6_vu_aggregate_docs_keep_historical_boundaries() -> None:
    plan = PLAN_PATH.read_text(encoding="utf-8")
    migration = MIGRATION_PATH.read_text(encoding="utf-8")

    assert "VUSK1L5.DAT" in plan
    assert "Zeitfenster desselben" in plan
    assert "nicht zurueckgesetzt" in plan
    assert "keine historische Vollgleichheitsbehauptung" in plan
    assert "232/1400" in migration
    assert "229/1400" in migration
    assert "Nach PR 82 bleiben vier" in migration
