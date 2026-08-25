import json
from pathlib import Path

from ims.api.vdefmd6_100_period_run_report import (
    build_vdefmd6_100_period_run_report,
    main,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = (
    REPO_ROOT / "tests" / "fixtures" / "vdefmd6_100_period_run_contract.json"
)
PLAN_PATH = REPO_ROOT / "docs" / "plans" / "vdefmd6_shock_run_plan.md"
MIGRATION_PATH = (
    REPO_ROOT / "docs" / "migration" / "vdefmd6_100_period_run_contract.md"
)


def test_vdefmd6_100_period_report_classifies_shock_path() -> None:
    payload = build_vdefmd6_100_period_run_report(REPO_ROOT).to_dict()

    assert payload["status"] == "100_period_path_classified"
    assert payload["contract_version"] == "pr81-v1"
    assert payload["source_anchor_count"] == 12
    assert payload["summary"]["generated_period_count"] == 100
    assert payload["summary"]["matched_field_count"] == 488
    assert payload["summary"]["full_row_match_periods"] == [1]
    assert payload["shock_boundary"]["shock_period"] == 50
    assert payload["shock_boundary"]["activated_policyholder_ids"] == list(
        range(151, 201)
    )
    assert payload["shock_boundary_ready"] is True
    assert payload["generation_ready"] is True
    assert payload["production_release_approved"] is False
    assert payload["simulation_performed"] is False
    assert payload["historical_full_equality_claimed"] is False
    assert payload["issues"] == []


def test_vdefmd6_100_period_report_rejects_contract_drift(tmp_path: Path) -> None:
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    contract["shock_boundary"]["shock_period"] = 51
    path = tmp_path / "contract.json"
    path.write_text(json.dumps(contract), encoding="utf-8")

    payload = build_vdefmd6_100_period_run_report(
        REPO_ROOT,
        contract_path=path,
    ).to_dict()

    assert payload["status"] == "error"
    assert "shock_boundary_mismatch" in {
        item["code"] for item in payload["issues"]
    }


def test_vdefmd6_100_period_report_rejects_missing_reference(
    tmp_path: Path,
) -> None:
    payload = build_vdefmd6_100_period_run_report(
        REPO_ROOT,
        reference_path=tmp_path / "missing.dat",
    ).to_dict()

    assert payload["status"] == "error"
    assert "reference_comparison_failed" in {
        item["code"] for item in payload["issues"]
    }


def test_vdefmd6_100_period_report_cli(capsys) -> None:
    exit_code = main(["--repo-root", str(REPO_ROOT)])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["status"] == "100_period_path_classified"
    assert payload["writes_performed"] is False


def test_vdefmd6_100_period_docs_keep_historical_boundaries() -> None:
    plan = PLAN_PATH.read_text(encoding="utf-8")
    migration = MIGRATION_PATH.read_text(encoding="utf-8")

    assert "Nach PR 81 bleiben mindestens fuenf" in plan
    assert "PR 82" in plan
    assert "488/1400" in migration
    assert "generation_ready = true" in migration
    assert "keine historische Gleichheitsaussage" in migration
