import json
from pathlib import Path

from ims.api.vdefmd6_vn_input_draw_report import (
    build_vdefmd6_vn_input_draw_report,
    main,
)


REPO_ROOT = Path(__file__).resolve().parent.parent
CONTRACT_PATH = REPO_ROOT / "tests" / "fixtures" / "vdefmd6_vn_input_draw_contract.json"
PLAN_DOC = REPO_ROOT / "docs" / "plans" / "vdefmd6_vn_input_draw_plan.md"
MIGRATION_DOC = REPO_ROOT / "docs" / "migration" / "vdefmd6_vn_input_draw_contract.md"


def _contract() -> dict:
    return json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))


def test_vdefmd6_vn_input_draw_report_maps_all_pre_shock_rules() -> None:
    payload = build_vdefmd6_vn_input_draw_report(REPO_ROOT).to_dict()

    assert payload["status"] == "input_draw_path_mapped"
    assert payload["contract_version"] == "pr77-v1"
    assert payload["source_anchor_count"] == 20
    assert payload["summary"] == {
        "period_start": 1,
        "period_end": 49,
        "policyholder_count": 200,
        "pre_shock_active_policyholder_count": 150,
        "deferred_policyholder_count": 50,
        "mapped_rule_count": 6,
        "pre_shock_rule_counts": {
            "1": 15,
            "2": 15,
            "3": 30,
            "4": 30,
            "5": 30,
            "6": 30,
        },
        "historical_damage_normal_calls_per_active_policyholder": 4,
        "historical_uniform_draws_per_normal_call": 12,
        "historical_minimum_damage_uniform_draws_per_active_policyholder": 48,
        "historical_minimum_damage_uniform_draws_per_pre_shock_period": 7200,
    }
    assert [item["rule_kind"] for item in payload["rule_mappings"]] == [
        "compulsory",
        "random",
        "preference",
        "search_history",
        "sample_search",
        "best_info",
    ]
    assert payload["mapping_ready"] is True
    assert payload["issues"] == []


def test_vdefmd6_vn_input_draw_report_keeps_generation_and_rng_claims_closed() -> None:
    payload = build_vdefmd6_vn_input_draw_report(REPO_ROOT).to_dict()

    assert payload["draw_order"]["within_sector_normal_call_order"] == "unspecified_by_c_expression"
    assert payload["draw_order"]["historical_draw_order_fully_bound"] is False
    assert payload["runner_bridge"]["matches_historical_random_consumption_order"] is False
    assert payload["policyholder_claim_path_mapped"] is True
    assert payload["settlement_write_path_mapped"] is True
    assert payload["policyholder_claim_origin_evidenced_for_generation"] is False
    assert payload["settlement_state_origin_evidenced_for_generation"] is False
    assert payload["independent_periods_2_49_ready"] is False
    assert payload["generation_ready"] is False
    assert payload["runner_started"] is False
    assert payload["rng_draws_performed"] is False
    assert payload["simulation_performed"] is False
    assert payload["historical_full_equality_claimed"] is False


def test_vdefmd6_vn_input_draw_report_rejects_historical_order_claim_drift(tmp_path: Path) -> None:
    contract = _contract()
    contract["draw_order"]["historical_draw_order_fully_bound"] = True
    path = tmp_path / "bad_draw_order.json"
    path.write_text(json.dumps(contract), encoding="utf-8")

    report = build_vdefmd6_vn_input_draw_report(REPO_ROOT, contract_path=path)

    assert report.mapping_ready is False
    assert "draw_order_mismatch" in {issue.code for issue in report.issues}


def test_vdefmd6_vn_input_draw_report_rejects_source_anchor_drift(tmp_path: Path) -> None:
    contract = _contract()
    contract["source_anchors"][0]["needle"] = "missing Vrvn01 rule"
    path = tmp_path / "bad_source_anchor.json"
    path.write_text(json.dumps(contract), encoding="utf-8")

    report = build_vdefmd6_vn_input_draw_report(REPO_ROOT, contract_path=path)

    assert report.mapping_ready is False
    assert "source_anchor_missing" in {issue.code for issue in report.issues}


def test_vdefmd6_vn_input_draw_cli_and_docs_keep_pr78_boundary(capsys) -> None:
    exit_code = main(["--repo-root", str(REPO_ROOT)])
    payload = json.loads(capsys.readouterr().out)
    plan = PLAN_DOC.read_text(encoding="utf-8")
    migration = MIGRATION_DOC.read_text(encoding="utf-8")

    assert exit_code == 0
    assert payload["mapping_ready"] is True
    assert payload["execution_performed"] is False
    assert "PR 78" in plan
    assert "acht" in plan
    assert "nicht festgelegt" in migration
    assert "keine historische Vollgleichheitsbehauptung" in migration
