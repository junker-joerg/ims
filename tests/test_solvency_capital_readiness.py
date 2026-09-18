import copy
from decimal import Decimal, localcontext
from types import SimpleNamespace

import pytest

from ims.accounting.solvency_capital_readiness import (
    SOLVENCY_CAPITAL_READINESS_INPUT_VERSION,
    SOLVENCY_CAPITAL_READINESS_RESULT_VERSION,
    build_solvency_capital_readiness,
    solvency_capital_readiness_contract_payload,
)
from ims.accounting.solvency_model_balance import build_solvency_model_balance
from ims.accounting.solvency_risk_aggregation import build_solvency_risk_aggregation
from tests.test_solvency_risk_aggregation import _input as aggregation_input


def _input() -> dict:
    return {
        "schema_version": SOLVENCY_CAPITAL_READINESS_INPUT_VERSION,
        "solvency_risk_aggregation_input": aggregation_input(),
        "management_limits": {
            "source_kind": "management_workshop_declared_not_regulatory",
            "assumption_note": "Seminargrenzen ohne Aufsichtsanspruch",
            "max_net_model_stress_loss": "2",
            "min_remaining_model_equity_proxy": "300",
        },
    }


def _balance_input(value: dict) -> dict:
    return (
        value["solvency_risk_aggregation_input"]
        ["solvency_risk_modules_input"]
        ["solvency_scenario_shocks_input"]
        ["solvency_model_balance_input"]
    )


def test_management_values_are_source_bound_but_regulatory_metrics_blocked() -> None:
    value = _input()
    before = copy.deepcopy(value)
    with localcontext() as context:
        context.prec = 3
        result = build_solvency_capital_readiness(value).to_dict()
    assert value == before
    assert result == build_solvency_capital_readiness(value).to_dict()
    assert result["valid"] is True, result["issues"]
    assert result["schema_version"] == SOLVENCY_CAPITAL_READINESS_RESULT_VERSION
    aggregation = build_solvency_risk_aggregation(value["solvency_risk_aggregation_input"]).to_dict()
    balance = build_solvency_model_balance(_balance_input(value)).to_dict()
    assert result["source_risk_aggregation_content_digest"] == aggregation["content_digest"]
    assert result["source_model_balance_content_digest"] == balance["content_digest"]
    assert len(result["input_digest"]) == len(result["content_digest"]) == 64
    assert result["checkpoint"] == balance["checkpoint"]
    assert result["amount_unit"] == "model_currency_unit_not_eur"
    assert result["review_applicability_window"] == "before_2027_review"
    assert result["management_evaluation"] == {
        "source_kind": "management_workshop_declared_not_regulatory",
        "assumption_note": "Seminargrenzen ohne Aufsichtsanspruch",
        "model_own_funds_proxy": "319.0000",
        "net_model_stress_loss": "1.6000",
        "remaining_model_equity_proxy": "317.4000",
        "max_net_model_stress_loss": "2.0000",
        "min_remaining_model_equity_proxy": "300.0000",
        "loss_limit_met": True,
        "equity_floor_met": True,
        "both_limits_met": True,
        "decision_kind": "workshop_only_not_compliance",
    }
    assert result["regulatory_metrics"] == {
        "status": "blocked_missing_regulatory_basis",
        "eligible_own_funds": None,
        "scr": None,
        "mcr": None,
        "scr_coverage_ratio": None,
        "mcr_coverage_ratio": None,
    }
    assert {row["requirement_code"] for row in result["readiness_rows"]} == {
        "reporting_date_and_legal_basis_unverified",
        "valuation_and_technical_provisions_missing",
        "eligible_own_funds_missing",
        "scr_calibration_and_formula_missing",
        "regulatory_loss_absorption_missing",
        "mcr_inputs_and_floor_missing",
        "model_currency_to_eur_missing",
    }
    assert all(row["status"] == "not_evidenced" for row in result["readiness_rows"])
    for flag in (
        "writes_performed", "runner_invoked", "statutory_balance_claim",
        "regulatory_own_funds_claim", "scr_or_mcr_calculated",
        "compliance_decision_enabled", "historical_full_equality_claim",
    ):
        assert result[flag] is False


@pytest.mark.parametrize(("max_loss", "min_equity", "loss_ok", "equity_ok"), [
    ("1.6", "317.4", True, True),
    ("1.5999", "317.4", False, True),
    ("1.6", "317.4001", True, False),
    ("0", "400", False, False),
])
def test_management_limits_are_inclusive_and_independent(
    max_loss: str, min_equity: str, loss_ok: bool, equity_ok: bool,
) -> None:
    value = _input()
    value["management_limits"]["max_net_model_stress_loss"] = max_loss
    value["management_limits"]["min_remaining_model_equity_proxy"] = min_equity
    result = build_solvency_capital_readiness(value).to_dict()
    assert result["valid"] is True
    management = result["management_evaluation"]
    assert management["loss_limit_met"] is loss_ok
    assert management["equity_floor_met"] is equity_ok
    assert management["both_limits_met"] is (loss_ok and equity_ok)
    assert result["regulatory_metrics"]["scr"] is None
    assert result["compliance_decision_enabled"] is False


def test_negative_remaining_model_equity_is_not_clamped() -> None:
    value = _input()
    value["solvency_risk_aggregation_input"]["operational_events"][0]["loss_amount"] = "400"
    value["management_limits"]["max_net_model_stress_loss"] = "500"
    result = build_solvency_capital_readiness(value).to_dict()
    assert result["valid"] is True, result["issues"]
    management = result["management_evaluation"]
    assert management["loss_limit_met"] is True
    assert management["equity_floor_met"] is False
    assert Decimal(management["remaining_model_equity_proxy"]) < 0
    assert (
        Decimal(management["model_own_funds_proxy"])
        - Decimal(management["net_model_stress_loss"])
        == Decimal(management["remaining_model_equity_proxy"])
    )
    assert result["regulatory_metrics"]["status"] == "blocked_missing_regulatory_basis"


@pytest.mark.parametrize(("reference_date", "window", "revision_blocked"), [
    ("2027-01-29", "before_2027_review", False),
    ("2027-01-30", "from_2027_review_unverified", True),
    ("2027-02-01", "from_2027_review_unverified", True),
])
def test_review_window_never_opens_regulatory_gate(
    reference_date: str, window: str, revision_blocked: bool,
) -> None:
    value = _input()
    _balance_input(value)["checkpoint"]["reference_date"] = reference_date
    result = build_solvency_capital_readiness(value).to_dict()
    assert result["valid"] is True, result["issues"]
    assert result["review_applicability_window"] == window
    codes = {row["requirement_code"] for row in result["readiness_rows"]}
    assert ("review_2027_applicability_unverified" in codes) is revision_blocked
    assert result["regulatory_metrics"]["scr_coverage_ratio"] is None


@pytest.mark.parametrize(("mutation", "code"), [
    (lambda v: v.update({"schema_version": "wrong"}), "contract_value_mismatch"),
    (lambda v: v.update({"scr": "1"}), "field_unknown"),
    (lambda v: v["management_limits"].pop("max_net_model_stress_loss"), "field_missing"),
    (lambda v: v["management_limits"].update({"source_kind": "regulatory"}), "source_kind_invalid"),
    (lambda v: v["management_limits"].update({"assumption_note": " "}), "note_invalid"),
    (lambda v: v["management_limits"].update({"max_net_model_stress_loss": -1}), "amount_format_invalid"),
    (lambda v: v["management_limits"].update({"max_net_model_stress_loss": "1e2"}), "amount_format_invalid"),
    (lambda v: v["management_limits"].update({"min_remaining_model_equity_proxy": "-1"}), "amount_format_invalid"),
    (lambda v: v["management_limits"].update({"min_remaining_model_equity_proxy": "1.00001"}), "amount_format_invalid"),
    (
        lambda v: v["solvency_risk_aggregation_input"]["loss_absorption"].update({"applied_amount": "9"}),
        "buffer_capacity_exceeded",
    ),
    (lambda v: _balance_input(v)["checkpoint"].update({"reference_date": "bad"}), "date_invalid"),
])
def test_invalid_input_is_atomic(mutation, code: str) -> None:
    value = _input()
    mutation(value)
    result = build_solvency_capital_readiness(value).to_dict()
    assert result["valid"] is False
    assert result["management_evaluation"] is None
    assert result["readiness_rows"] == []
    assert result["source_risk_aggregation_content_digest"] is None
    assert result["source_model_balance_content_digest"] is None
    assert result["content_digest"] is None
    assert result["regulatory_metrics"]["scr"] is None
    assert code in {issue["code"] for issue in result["issues"]}


def test_recalculated_balance_digest_must_match_aggregation(monkeypatch) -> None:
    import ims.accounting.solvency_capital_readiness as readiness

    value = _input()
    balance = build_solvency_model_balance(_balance_input(value)).to_dict()
    balance["content_digest"] = "0" * 64
    monkeypatch.setattr(readiness, "build_solvency_model_balance", lambda _: SimpleNamespace(to_dict=lambda: balance))
    result = build_solvency_capital_readiness(value).to_dict()
    assert result["valid"] is False
    assert result["management_evaluation"] is None
    assert {issue["code"] for issue in result["issues"]} == {"source_digest_mismatch"}


def test_contract_discloses_blocked_capital_fields_and_sources() -> None:
    contract = solvency_capital_readiness_contract_payload()
    assert contract["review_start_date"] == "2027-01-30"
    assert contract["reference_date_is_regulatory_reporting_date"] is False
    assert contract["blocked_regulatory_metrics"] == [
        "eligible_own_funds", "scr", "mcr", "scr_coverage_ratio", "mcr_coverage_ratio",
    ]
    assert contract["legal_sources"]["scr_calibration"].endswith("article-2188_en")
    assert contract["scr_or_mcr_calculated"] is False
    assert contract["compliance_decision_enabled"] is False
