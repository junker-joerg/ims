import json
from pathlib import Path

from ims.api.vdefmd6_vn_rule_group_1_run_report import (
    DEFAULT_REFERENCE_PATHS,
    build_vdefmd6_vn_rule_group_1_run_report,
    main,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = (
    REPO_ROOT
    / "tests"
    / "fixtures"
    / "vdefmd6_vn_rule_group_1_run_contract.json"
)
PLAN_PATH = REPO_ROOT / "docs" / "plans" / "vdefmd6_vn_rule_group_1_run_plan.md"
MIGRATION_PATH = (
    REPO_ROOT
    / "docs"
    / "migration"
    / "vdefmd6_vn_rule_group_1_run_contract.md"
)


def test_vdefmd6_vn_rule_group_1_report_classifies_three_targets() -> None:
    payload = build_vdefmd6_vn_rule_group_1_run_report(REPO_ROOT).to_dict()
    targets = {
        item["export_filename"]: item for item in payload["target_summaries"]
    }

    assert payload["status"] == "vn_rule_group_1_path_classified"
    assert payload["contract_version"] == "pr83-v1"
    assert payload["rule_target_count"] == 3
    assert payload["source_anchor_count"] == 14
    assert targets["imsvnr01.dat"]["reference_filename"] == "IMSVNR01.DAT"
    assert targets["imsvnr01.dat"]["matched_field_count"] == 316
    assert targets["imsvnr02.dat"]["matched_field_count"] == 241
    assert targets["imsvnr03.dat"]["matched_field_count"] == 389
    assert all(
        item["first_full_state_divergence_period"] == 1
        for item in targets.values()
    )
    assert payload["historical_vn_rule_accumulator_compatibility_applied"] is False
    assert payload["historical_full_equality_claimed"] is False
    assert payload["production_release_approved"] is False
    assert payload["issues"] == []


def test_vdefmd6_vn_rule_group_1_report_rejects_contract_drift(
    tmp_path: Path,
) -> None:
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    contract["expected_targets"][0]["matched_field_count"] = 1300
    path = tmp_path / "contract.json"
    path.write_text(json.dumps(contract), encoding="utf-8")

    payload = build_vdefmd6_vn_rule_group_1_run_report(
        REPO_ROOT,
        contract_path=path,
    ).to_dict()

    assert payload["status"] == "error"
    assert "expected_targets_mismatch" in {
        item["code"] for item in payload["issues"]
    }


def test_vdefmd6_vn_rule_group_1_report_rejects_missing_reference(
    tmp_path: Path,
) -> None:
    references = dict(DEFAULT_REFERENCE_PATHS)
    references["imsvnr02.dat"] = tmp_path / "missing.dat"

    payload = build_vdefmd6_vn_rule_group_1_run_report(
        REPO_ROOT,
        reference_paths=references,
    ).to_dict()

    assert payload["status"] == "error"
    assert "reference_comparison_failed" in {
        item["code"] for item in payload["issues"]
    }


def test_vdefmd6_vn_rule_group_1_report_rejects_wrong_reference_target_set(
    tmp_path: Path,
) -> None:
    payload = build_vdefmd6_vn_rule_group_1_run_report(
        REPO_ROOT,
        reference_paths={"unexpected.dat": tmp_path / "missing.dat"},
    ).to_dict()

    assert payload["status"] == "error"
    assert "reference_target_set_mismatch" in {
        item["code"] for item in payload["issues"]
    }


def test_vdefmd6_vn_rule_group_1_report_cli(capsys) -> None:
    exit_code = main(["--repo-root", str(REPO_ROOT)])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["status"] == "vn_rule_group_1_path_classified"
    assert payload["writes_performed"] is False
    assert payload["simulation_performed"] is False


def test_vdefmd6_vn_rule_group_1_docs_keep_historical_boundaries() -> None:
    plan = PLAN_PATH.read_text(encoding="utf-8")
    migration = MIGRATION_PATH.read_text(encoding="utf-8")

    assert "IMSVNR01.DAT" in plan
    assert "nicht geleert" in plan
    assert "keine historische Vollgleichheitsbehauptung" in plan
    assert "316/1300" in migration
    assert "946 von 3.900" in migration
    assert "Nach PR 83 bleiben drei" in migration
