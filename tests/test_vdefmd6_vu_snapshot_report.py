import json
from pathlib import Path

from ims.api.vdefmd6_vu_snapshot_report import (
    build_vdefmd6_vu_snapshot_report,
    main,
)


REPO_ROOT = Path(__file__).resolve().parent.parent
CONTRACT_PATH = REPO_ROOT / "tests" / "fixtures" / "vdefmd6_vu_snapshot_contract.json"
PLAN_DOC = REPO_ROOT / "docs" / "plans" / "vdefmd6_vu_snapshot_plan.md"
MIGRATION_DOC = REPO_ROOT / "docs" / "migration" / "vdefmd6_vu_snapshot_contract.md"


def _contract() -> dict:
    return json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))


def test_vdefmd6_vu_snapshot_report_freezes_all_vu_families() -> None:
    payload = build_vdefmd6_vu_snapshot_report(REPO_ROOT).to_dict()

    assert payload["status"] == "snapshot_materialization_ready"
    assert payload["contract_version"] == "pr79-v1"
    assert payload["source_anchor_count"] == 16
    assert payload["summary"]["snapshot_count"] == 25
    assert payload["summary"]["active_policyholder_input_count"] == 150
    assert payload["summary"]["uniform_value_count"] == 8
    assert payload["summary"]["normal_value_count"] == 8
    assert payload["snapshot_materialization_ready"] is True
    assert payload["issues"] == []


def test_vdefmd6_vu_snapshot_report_keeps_application_claims_closed() -> None:
    payload = build_vdefmd6_vu_snapshot_report(REPO_ROOT).to_dict()

    assert payload["bav_previous_period_inputs_ready"] is True
    assert payload["information_cost_origin_evidenced"] is True
    assert payload["information_cost_application_ready"] is False
    assert payload["bav_service_executed"] is False
    assert payload["runner_started"] is False
    assert payload["simulation_performed"] is False
    assert payload["independent_periods_2_49_ready"] is False
    assert payload["generation_ready"] is False
    assert payload["historical_full_equality_claimed"] is False


def test_vdefmd6_vu_snapshot_report_rejects_cost_boundary_drift(tmp_path: Path) -> None:
    contract = _contract()
    contract["expected"]["python_settlement_snapshot_accepts_cost"] = True
    path = tmp_path / "bad_cost_boundary.json"
    path.write_text(json.dumps(contract), encoding="utf-8")

    report = build_vdefmd6_vu_snapshot_report(REPO_ROOT, contract_path=path)

    assert report.snapshot_materialization_ready is False
    assert "expected_mismatch" in {issue.code for issue in report.issues}


def test_vdefmd6_vu_snapshot_report_rejects_source_anchor_drift(tmp_path: Path) -> None:
    contract = _contract()
    contract["source_anchors"][0]["needle"] = "missing Vrvu01 source"
    path = tmp_path / "bad_anchor.json"
    path.write_text(json.dumps(contract), encoding="utf-8")

    report = build_vdefmd6_vu_snapshot_report(REPO_ROOT, contract_path=path)

    assert report.snapshot_materialization_ready is False
    assert "source_anchor_missing" in {issue.code for issue in report.issues}


def test_vdefmd6_vu_snapshot_report_cli(capsys) -> None:
    exit_code = main(["--repo-root", str(REPO_ROOT)])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["status"] == "snapshot_materialization_ready"
    assert payload["runner_started"] is False


def test_vdefmd6_vu_snapshot_docs_keep_pr80_boundary() -> None:
    plan = PLAN_DOC.read_text(encoding="utf-8")
    migration = MIGRATION_DOC.read_text(encoding="utf-8")

    assert "Nach PR 79 bleiben mindestens sieben" in plan
    assert "PR 80" in plan
    assert "information_cost_application_ready = false" in migration
    assert "keine historische Vollgleichheitsbehauptung" in migration
