import json
from pathlib import Path

from ims.api.vdefmd6_pre_shock_run_report import (
    build_vdefmd6_pre_shock_run_report,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = REPO_ROOT / "tests" / "fixtures" / "vdefmd6_pre_shock_run_contract.json"
PLAN_PATH = REPO_ROOT / "docs" / "plans" / "vdefmd6_pre_shock_run_plan.md"
MIGRATION_PATH = (
    REPO_ROOT / "docs" / "migration" / "vdefmd6_pre_shock_run_contract.md"
)


def test_vdefmd6_pre_shock_run_report_classifies_vu14_deviations() -> None:
    payload = build_vdefmd6_pre_shock_run_report(REPO_ROOT).to_dict()

    assert payload["status"] == "pre_shock_path_classified"
    assert payload["contract_version"] == "pr80-v1"
    assert payload["source_anchor_count"] == 15
    assert payload["information_cost_application_ready"] is True
    assert payload["independent_periods_2_49_ready"] is True
    assert payload["full_state_projection_ready"] is True
    assert payload["generation_ready"] is False
    assert payload["summary"]["matched_field_count"] == 236
    assert payload["summary"]["full_row_match_periods"] == [1]
    assert payload["summary"]["first_full_state_divergence_period"] == 2
    assert payload["summary"]["first_rule_output_divergence_period"] == 10
    assert payload["historical_full_equality_claimed"] is False
    assert payload["simulation_performed"] is False
    assert payload["issues"] == []


def test_vdefmd6_pre_shock_run_report_rejects_contract_drift(tmp_path: Path) -> None:
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    contract["expected"]["total_information_cost"] = 0.0
    path = tmp_path / "contract.json"
    path.write_text(json.dumps(contract), encoding="utf-8")

    payload = build_vdefmd6_pre_shock_run_report(
        REPO_ROOT,
        contract_path=path,
    ).to_dict()

    assert payload["status"] == "error"
    assert "expected_mismatch" in {item["code"] for item in payload["issues"]}


def test_vdefmd6_pre_shock_run_report_rejects_missing_reference(
    tmp_path: Path,
) -> None:
    payload = build_vdefmd6_pre_shock_run_report(
        REPO_ROOT,
        reference_path=tmp_path / "missing.dat",
    ).to_dict()

    assert payload["status"] == "error"
    assert "reference_comparison_failed" in {
        item["code"] for item in payload["issues"]
    }


def test_vdefmd6_pre_shock_run_docs_keep_historical_boundaries() -> None:
    plan = PLAN_PATH.read_text(encoding="utf-8")
    migration = MIGRATION_PATH.read_text(encoding="utf-8")

    assert "Nach PR 80 bleiben mindestens sechs" in plan
    assert "PR 81" in plan
    assert "236/686" in plan
    assert "information_cost_application_ready = true" in migration
    assert "generation_ready = false" in migration
    assert "keine Vollsimulation" in migration
    assert "keine historische Gleichheitsaussage" in migration
