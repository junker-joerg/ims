import json
from pathlib import Path

import pytest

from ims.api.vu14_pre_shock_projection_report import (
    build_vu14_pre_shock_projection_report,
    main,
)
from ims.model.vu14_pre_shock_projection import (
    VU14PreShockProjection,
    build_vu14_pre_shock_projection,
)
from ims.model.vu_rules import vu_expected_claim_rule_parameters_from_mapping


REPO_ROOT = Path(__file__).resolve().parent.parent
CONTRACT_PATH = (
    REPO_ROOT / "tests" / "fixtures" / "vu14_pre_shock_projection_contract.json"
)
BINDING_PATH = REPO_ROOT / "tests" / "fixtures" / "vu14_vdefmd6_source_binding.json"
MODEL_PATH = REPO_ROOT / "python_port" / "ims" / "model" / "vu14_pre_shock_projection.py"
PLAN_DOC = REPO_ROOT / "docs" / "plans" / "vu14_pre_shock_projection_plan.md"


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _projection() -> VU14PreShockProjection:
    binding = _json(BINDING_PATH)
    return build_vu14_pre_shock_projection(
        vu_expected_claim_rule_parameters_from_mapping(binding["vu14"]["parameters"]),
        interest_rate=binding["bav"]["interest_rate"],
    )


def test_vu14_projection_generates_pre_shock_periods_without_legacy_input() -> None:
    projection = _projection()

    assert [item.period for item in projection.periods] == list(range(1, 50))
    assert all(item.export_table.spec.filename == "imsvu014.dat" for item in projection.periods)
    assert all(item.expected_claim_values == (0.0, 0.0) for item in projection.periods)
    assert projection.legacy_rows_used_as_input is False
    assert projection.policyholder_claim_inputs_bound is False
    assert projection.settlement_state_inputs_bound is False
    assert projection.rng_draws_performed is False
    assert projection.scheduler_started is False
    assert projection.simulation_performed is False
    assert "legacy_agrsich" not in MODEL_PATH.read_text(encoding="utf-8")


def test_vu14_projection_preserves_independent_rule_state_progression() -> None:
    projection = _projection()
    rows = {
        item.period: item.export_table.rows[0].values for item in projection.periods
    }

    assert rows[1][1:13] == [
        40.0, 10.0, 0.0, 0.0, 0, 0.0,
        40.0, 10.0, 0.0, 0.0, 0, 0.0,
    ]
    assert rows[2][1] == pytest.approx(39.2)
    assert rows[2][2] == pytest.approx(10.3)
    assert rows[16][1] == pytest.approx(29.542764105816158)
    assert rows[17][1] == pytest.approx(28.951908823699835)


def test_vu14_projection_report_classifies_prefix_and_first_divergence() -> None:
    payload = build_vu14_pre_shock_projection_report(REPO_ROOT).to_dict()
    summary = payload["summary"]

    assert payload["status"] == "projection_classified"
    assert payload["contract_version"] == "pr76-v1"
    assert payload["source_anchor_count"] == 10
    assert payload["rule_projection_ready"] is True
    assert summary["generated_period_count"] == 49
    assert summary["followup_period_count"] == 48
    assert summary["compared_field_count"] == 686
    assert summary["matched_field_count"] == 188
    assert summary["full_row_match_periods"] == [1]
    assert summary["rule_output_match_periods"] == list(range(1, 17))
    assert summary["first_rule_output_divergence_period"] == 17
    assert summary["field_match_counts"] == {
        "header": 49,
        "global_period": 49,
        "Pr1": 16,
        "Wa1": 16,
        "Rs1": 1,
        "Vn1": 7,
        "Sa1": 7,
        "Sh1": 7,
        "Pr2": 16,
        "Wa2": 16,
        "Rs2": 1,
        "Vn2": 1,
        "Sa2": 1,
        "Sh2": 1,
    }
    assert payload["issues"] == []


def test_vu14_projection_report_keeps_full_state_and_execution_blocked() -> None:
    payload = build_vu14_pre_shock_projection_report(REPO_ROOT).to_dict()

    assert payload["blocker_codes"] == [
        "policyholder_claim_origin_missing",
        "settlement_state_origin_missing",
        "historical_rng_draw_order_missing",
    ]
    assert payload["projection_generated_before_legacy_read"] is True
    assert payload["legacy_rows_used_as_generation_input"] is False
    assert payload["downstream_incidental_matches_are_evidence"] is False
    assert payload["independent_periods_2_49_ready"] is False
    assert payload["full_state_projection_ready"] is False
    assert payload["generation_ready"] is False
    assert payload["writes_performed"] is False
    assert payload["execution_performed"] is False
    assert payload["scheduler_started"] is False
    assert payload["rng_draws_performed"] is False
    assert payload["simulation_performed"] is False
    assert payload["historical_full_equality_claimed"] is False


def test_vu14_projection_report_rejects_summary_drift(tmp_path: Path) -> None:
    contract = _json(CONTRACT_PATH)
    contract["expected"]["first_rule_output_divergence_period"] = 18
    path = tmp_path / "bad_projection_contract.json"
    path.write_text(json.dumps(contract), encoding="utf-8")

    report = build_vu14_pre_shock_projection_report(
        REPO_ROOT,
        contract_path=path,
    )

    assert report.rule_projection_ready is False
    assert "projection_summary_mismatch" in {issue.code for issue in report.issues}


def test_vu14_projection_report_rejects_execution_boundary_drift(
    tmp_path: Path,
) -> None:
    contract = _json(CONTRACT_PATH)
    contract["boundaries"]["simulation_performed"] = True
    path = tmp_path / "bad_projection_boundary.json"
    path.write_text(json.dumps(contract), encoding="utf-8")

    report = build_vu14_pre_shock_projection_report(
        REPO_ROOT,
        contract_path=path,
    )

    assert report.rule_projection_ready is False
    assert "execution_boundary_mismatch" in {issue.code for issue in report.issues}


def test_vu14_projection_report_rejects_source_anchor_drift(tmp_path: Path) -> None:
    contract = _json(CONTRACT_PATH)
    contract["source_anchors"][0]["needle"] = "missing VU14 rule"
    path = tmp_path / "bad_projection_anchor.json"
    path.write_text(json.dumps(contract), encoding="utf-8")

    report = build_vu14_pre_shock_projection_report(
        REPO_ROOT,
        contract_path=path,
    )

    assert report.rule_projection_ready is False
    assert "source_anchor_missing" in {issue.code for issue in report.issues}


def test_vu14_projection_cli_and_plan_document_conservative_boundary(capsys) -> None:
    exit_code = main(["--repo-root", str(REPO_ROOT)])
    payload = json.loads(capsys.readouterr().out)
    plan = PLAN_DOC.read_text(encoding="utf-8")

    assert exit_code == 0
    assert payload["rule_projection_ready"] is True
    assert payload["simulation_performed"] is False
    assert "Periode 17" in plan
    assert "keine historische Vollgleichheitsbehauptung" in plan
    assert "PR 77" in plan and "PR 78" in plan
