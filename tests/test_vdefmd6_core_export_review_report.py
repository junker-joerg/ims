import json
from pathlib import Path

from ims.api.vdefmd6_core_export_review_report import (
    CORE_EXPORT_FILENAMES,
    build_vdefmd6_core_export_review_report,
    main,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = (
    REPO_ROOT
    / "tests"
    / "fixtures"
    / "vdefmd6_core_export_run_contract.json"
)
WINDOW_BUNDLE_PATH = (
    REPO_ROOT
    / "tests"
    / "fixtures"
    / "vdefmd6_core_export_window_bundle.json"
)
PLAN_PATH = REPO_ROOT / "docs" / "plans" / "vdefmd6_core_export_review_plan.md"
MIGRATION_PATH = (
    REPO_ROOT
    / "docs"
    / "migration"
    / "vdefmd6_core_export_review.md"
)


def test_vdefmd6_core_export_review_classifies_all_fifteen_targets() -> None:
    payload = build_vdefmd6_core_export_review_report(REPO_ROOT).to_dict()
    summary = payload["summary"]

    assert payload["status"] == "review_ready"
    assert payload["contract_version"] == "pr86-v1"
    assert payload["controlled_export_count"] == 15
    assert payload["source_anchor_count"] == 13
    assert tuple(
        item["export_filename"] for item in payload["target_summaries"]
    ) == CORE_EXPORT_FILENAMES
    assert summary["compared_row_count"] == 1500
    assert summary["full_row_match_count"] == 3
    assert summary["compared_field_count"] == 20000
    assert summary["matched_field_count"] == 4492
    assert summary["matched_structural_field_count"] == 3000
    assert summary["matched_fach_field_count"] == 1492
    assert summary["exact_field_match_count"] == 3839
    assert summary["tolerated_numeric_difference_count"] == 653
    assert summary["blocking_numeric_difference_count"] == 14752
    assert summary["open_field_question_count"] == 756
    assert payload["review_recommendation"] == "keep_blocked"
    assert payload["planned_minimum_series_complete"] is True
    assert payload["full_legacy_corpus_window_complete"] is False
    assert payload["historical_full_equality_claimed"] is False
    assert payload["production_release_approved"] is False
    assert payload["issues"] == []


def test_vdefmd6_core_export_review_keeps_level_iv_time_window_identity() -> None:
    bundle = json.loads(WINDOW_BUNDLE_PATH.read_text(encoding="utf-8"))
    targets = {item["export_filename"]: item for item in bundle["targets"]}

    assert targets["imsvusk1.dat"]["legacy_path"].endswith("VUSK1L5.DAT")
    assert targets["imsvusk1.dat"]["level"] == "IV"
    assert targets["imsvusk1.dat"]["selector_value"] == "SK1"
    assert targets["imsvusk1.dat"]["periods"] == list(range(1, 101))
    assert targets["imsvnsk1.dat"]["level"] == "IV"
    assert targets["imsvnsk1.dat"]["selector_value"] == "SK1"


def test_vdefmd6_core_export_review_rejects_contract_drift(tmp_path: Path) -> None:
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    contract["expected_summary"]["matched_field_count"] = 20000
    path = tmp_path / "contract.json"
    path.write_text(json.dumps(contract), encoding="utf-8")

    payload = build_vdefmd6_core_export_review_report(
        REPO_ROOT,
        contract_path=path,
    ).to_dict()

    assert payload["status"] == "error"
    assert "expected_summary_mismatch" in {
        item["code"] for item in payload["issues"]
    }


def test_vdefmd6_core_export_review_rejects_missing_window_bundle(
    tmp_path: Path,
) -> None:
    payload = build_vdefmd6_core_export_review_report(
        REPO_ROOT,
        window_bundle_path=tmp_path / "missing.json",
    ).to_dict()

    assert payload["status"] == "error"
    assert "joint_deviation_failed" in {
        item["code"] for item in payload["issues"]
    }
    assert payload["joint_deviation_comparison_ready"] is False


def test_vdefmd6_core_export_review_rejects_incomplete_target_set(
    tmp_path: Path,
) -> None:
    bundle = json.loads(WINDOW_BUNDLE_PATH.read_text(encoding="utf-8"))
    bundle["targets"] = bundle["targets"][:-1]
    path = tmp_path / "window.json"
    path.write_text(json.dumps(bundle), encoding="utf-8")

    payload = build_vdefmd6_core_export_review_report(
        REPO_ROOT,
        window_bundle_path=path,
    ).to_dict()

    assert payload["status"] == "error"
    assert "joint_deviation_blocked" in {
        item["code"] for item in payload["issues"]
    }


def test_vdefmd6_core_export_review_cli(capsys) -> None:
    exit_code = main(["--repo-root", str(REPO_ROOT)])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["status"] == "review_ready"
    assert payload["simulation_performed"] is False
    assert payload["production_release_approved"] is False


def test_vdefmd6_core_export_review_docs_keep_release_boundaries() -> None:
    plan = PLAN_PATH.read_text(encoding="utf-8")
    migration = MIGRATION_PATH.read_text(encoding="utf-8")

    assert "keine Gleichsetzung von 1.500 kontrollierten Zielzeilen" in plan
    assert "keinen weiteren vorab nummerierten Pflicht-PR" in plan
    assert "4.492/20.000" in migration
    assert "1.492/17.000" in migration
    assert "14.752" in migration
    assert "`keep_blocked`" in migration
    assert "keine historische Vollgleichheitsbehauptung" in migration
