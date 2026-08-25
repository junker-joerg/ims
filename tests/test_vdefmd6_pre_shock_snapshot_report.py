import json
from pathlib import Path

from ims.api.vdefmd6_pre_shock_snapshot_report import (
    build_vdefmd6_pre_shock_snapshot_report,
    main,
)


REPO_ROOT = Path(__file__).resolve().parent.parent
CONTRACT_PATH = (
    REPO_ROOT / "tests" / "fixtures" / "vdefmd6_pre_shock_snapshot_contract.json"
)


def _contract() -> dict:
    return json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))


def test_vdefmd6_pre_shock_snapshot_report_freezes_materialized_scope() -> None:
    payload = build_vdefmd6_pre_shock_snapshot_report(REPO_ROOT).to_dict()

    assert payload["status"] == "snapshot_materialization_ready"
    assert payload["contract_version"] == "pr78-v1"
    assert payload["source_anchor_count"] == 12
    assert payload["summary"]["insurance_snapshot_count"] == 150
    assert payload["summary"]["damage_snapshot_count"] == 150
    assert payload["summary"]["uniform_value_count"] == 990
    assert payload["summary"]["normal_value_count"] == 600
    assert payload["snapshot_materialization_ready"] is True
    assert payload["issues"] == []


def test_vdefmd6_pre_shock_snapshot_report_keeps_execution_claims_closed() -> None:
    payload = build_vdefmd6_pre_shock_snapshot_report(REPO_ROOT).to_dict()

    assert payload["snapshot_materialization_performed"] is True
    assert payload["rng_draws_performed"] is True
    assert payload["runner_started"] is False
    assert payload["simulation_performed"] is False
    assert payload["independent_periods_2_49_ready"] is False
    assert payload["full_state_projection_ready"] is False
    assert payload["generation_ready"] is False
    assert payload["historical_rng_equality_claimed"] is False
    assert payload["historical_full_equality_claimed"] is False


def test_vdefmd6_pre_shock_snapshot_report_rejects_draw_policy_drift(
    tmp_path: Path,
) -> None:
    contract = _contract()
    contract["draw_order"] = list(reversed(contract["draw_order"]))
    path = tmp_path / "bad_draw_order.json"
    path.write_text(json.dumps(contract), encoding="utf-8")

    report = build_vdefmd6_pre_shock_snapshot_report(REPO_ROOT, contract_path=path)

    assert report.snapshot_materialization_ready is False
    assert "draw_order_mismatch" in {issue.code for issue in report.issues}


def test_vdefmd6_pre_shock_snapshot_report_rejects_source_anchor_drift(
    tmp_path: Path,
) -> None:
    contract = _contract()
    contract["source_anchors"][0]["needle"] = "missing Myinitvn source"
    path = tmp_path / "bad_anchor.json"
    path.write_text(json.dumps(contract), encoding="utf-8")

    report = build_vdefmd6_pre_shock_snapshot_report(REPO_ROOT, contract_path=path)

    assert report.snapshot_materialization_ready is False
    assert "source_anchor_missing" in {issue.code for issue in report.issues}


def test_vdefmd6_pre_shock_snapshot_report_cli(capsys) -> None:
    exit_code = main(["--repo-root", str(REPO_ROOT)])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["status"] == "snapshot_materialization_ready"
    assert payload["runner_started"] is False
