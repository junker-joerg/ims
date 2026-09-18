import copy
from decimal import Decimal, localcontext

import pytest

from ims.accounting.solvency_capital_readiness import build_solvency_capital_readiness
from ims.accounting.solvency_model_balance import build_solvency_model_balance
from ims.accounting.solvency_risk_aggregation import build_solvency_risk_aggregation
from ims.accounting.solvency_risk_modules import build_solvency_risk_modules
from tests.test_solvency_capital_readiness import _input


def _aggregation_input(value: dict) -> dict:
    return value["solvency_risk_aggregation_input"]


def _modules_input(value: dict) -> dict:
    return _aggregation_input(value)["solvency_risk_modules_input"]


def _balance_input(value: dict) -> dict:
    return _modules_input(value)["solvency_scenario_shocks_input"]["solvency_model_balance_input"]


def _case_input(case: str) -> dict:
    value = _input()
    if case == "balance_plus_one":
        _balance_input(value)["adjustments"][0]["asset_delta"] = "11"
    elif case == "life_liability_plus_one":
        _balance_input(value)["adjustments"][2]["liability_delta"] = "-2"
    elif case == "market_stress":
        _modules_input(value)["module_parameters"][0]["stress_rate"] = "0.50"
    elif case == "life_stress":
        _modules_input(value)["module_parameters"][3]["stress_rate"] = "0.25"
    elif case == "health_stress":
        _modules_input(value)["module_parameters"][4]["stress_rate"] = "0.30"
    elif case == "counterparty_stress":
        _aggregation_input(value)["counterparty_cases"][0]["loss_rate"] = "0.6"
    elif case == "operational_stress":
        _aggregation_input(value)["operational_events"][0]["loss_amount"] = "0.4"
    elif case == "larger_buffer":
        _aggregation_input(value)["loss_absorption"]["applied_amount"] = "0.25"
    elif case == "independent_factors":
        loadings = _aggregation_input(value)["aggregation_assumptions"]["factor_loadings"]
        for kind in loadings:
            loadings[kind] = "0"
    elif case == "zero_stress":
        _modules_input(value)["module_parameters"] = []
        _aggregation_input(value)["counterparty_cases"] = []
        _aggregation_input(value)["operational_events"] = []
        _aggregation_input(value)["loss_absorption"]["capacity_amount"] = "0"
        _aggregation_input(value)["loss_absorption"]["applied_amount"] = "0"
        value["management_limits"]["max_net_model_stress_loss"] = "0"
        value["management_limits"]["min_remaining_model_equity_proxy"] = "319"
    elif case == "large_operational_loss":
        _aggregation_input(value)["operational_events"][0]["loss_amount"] = "400"
        value["management_limits"]["max_net_model_stress_loss"] = "500"
    else:
        assert case == "baseline"
    return value


@pytest.mark.parametrize(
    ("case", "own_funds", "gross", "net", "remaining", "limits_met"),
    [
        ("baseline", "319.0000", "1.7750", "1.6000", "317.4000", True),
        ("balance_plus_one", "320.0000", "1.7750", "1.6000", "318.4000", True),
        ("life_liability_plus_one", "318.0000", "1.7750", "1.6000", "316.4000", True),
        ("market_stress", "319.0000", "2.0250", "1.8500", "317.1500", True),
        ("life_stress", "319.0000", "1.9000", "1.7250", "317.2750", True),
        ("health_stress", "319.0000", "1.9750", "1.8000", "317.2000", True),
        ("counterparty_stress", "319.0000", "1.9750", "1.8000", "317.2000", True),
        ("operational_stress", "319.0000", "1.9750", "1.8000", "317.2000", True),
        ("larger_buffer", "319.0000", "1.7750", "1.5250", "317.4750", True),
        ("independent_factors", "319.0000", "0.8821", "0.7071", "318.2929", True),
        ("zero_stress", "319.0000", "0.0000", "0.0000", "319.0000", True),
        ("large_operational_loss", "319.0000", "401.5750", "401.4000", "-82.4000", False),
    ],
)
def test_fixed_cases_close_balance_stress_and_management_chain(
    case: str, own_funds: str, gross: str, net: str, remaining: str, limits_met: bool,
) -> None:
    value = _case_input(case)
    original = copy.deepcopy(value)
    with localcontext() as context:
        context.prec = 3
        balance = build_solvency_model_balance(_balance_input(value)).to_dict()
        modules = build_solvency_risk_modules(_modules_input(value)).to_dict()
        aggregation = build_solvency_risk_aggregation(_aggregation_input(value)).to_dict()
        readiness = build_solvency_capital_readiness(value).to_dict()
    assert value == original
    for report in (balance, modules, aggregation, readiness):
        assert report["valid"] is True, report["issues"]
        assert report["writes_performed"] is False
        assert report["runner_invoked"] is False
        assert report["historical_full_equality_claim"] is False
    assert readiness == build_solvency_capital_readiness(value).to_dict()

    total = balance["total_row"]
    assert total["model_own_funds_proxy"] == own_funds
    for row in (*balance["sector_rows"], total):
        assert Decimal(row["model_own_funds_proxy"]) == (
            Decimal(row["adjusted_model_assets"]) - Decimal(row["adjusted_model_liabilities"])
        )
        assert Decimal(row["model_own_funds_proxy"]) == (
            Decimal(row["closing_equity"]) + Decimal(row["proxy_change_vs_equity"])
        )
    for field in ("closing_assets", "closing_liabilities", "closing_equity", "asset_delta",
                  "liability_delta", "adjusted_model_assets", "adjusted_model_liabilities",
                  "model_own_funds_proxy", "proxy_change_vs_equity"):
        assert Decimal(total[field]) == sum(Decimal(row[field]) for row in balance["sector_rows"])

    totals = aggregation["totals"]
    assert totals["gross_model_stress_loss"] == gross
    assert totals["net_model_stress_loss"] == net
    losses = [Decimal(row["model_loss_amount"]) for row in aggregation["component_rows"]]
    assert len(losses) == 6
    assert Decimal(totals["unadjusted_sum_of_components"]) == sum(losses)
    assert Decimal(totals["scenario_diversification_proxy"]) == sum(losses) - Decimal(gross)
    assert max(losses) <= Decimal(gross) <= sum(losses)
    assert Decimal(totals["model_buffer_applied"]) <= Decimal(totals["model_buffer_capacity"])
    assert Decimal(net) == Decimal(gross) - Decimal(totals["model_buffer_applied"])
    assert Decimal(net) >= 0

    management = readiness["management_evaluation"]
    assert management["model_own_funds_proxy"] == own_funds
    assert management["net_model_stress_loss"] == net
    assert management["remaining_model_equity_proxy"] == remaining
    assert Decimal(remaining) == Decimal(own_funds) - Decimal(net)
    assert management["loss_limit_met"] is (
        Decimal(net) <= Decimal(management["max_net_model_stress_loss"])
    )
    assert management["equity_floor_met"] is (
        Decimal(remaining) >= Decimal(management["min_remaining_model_equity_proxy"])
    )
    assert management["both_limits_met"] is limits_met
    assert management["decision_kind"] == "workshop_only_not_compliance"

    assert modules["source_model_balance_content_digest"] == balance["content_digest"]
    assert aggregation["source_module_content_digest"] == modules["content_digest"]
    assert aggregation["source_model_balance_content_digest"] == balance["content_digest"]
    assert readiness["source_risk_aggregation_content_digest"] == aggregation["content_digest"]
    assert readiness["source_model_balance_content_digest"] == balance["content_digest"]
    assert readiness["regulatory_metrics"] == {
        "status": "blocked_missing_regulatory_basis",
        "eligible_own_funds": None, "scr": None, "mcr": None,
        "scr_coverage_ratio": None, "mcr_coverage_ratio": None,
    }
    assert readiness["compliance_decision_enabled"] is False


@pytest.mark.parametrize(
    ("case", "risk_kind", "expected"),
    [
        ("market_stress", "asset_market_value", "0.5000"),
        ("life_stress", "life_obligation", "0.2500"),
        ("health_stress", "health_benefit_obligation", "0.3000"),
        ("counterparty_stress", "counterparty_model_loss", "0.6000"),
        ("operational_stress", "operational_model_loss", "0.4000"),
    ],
)
def test_increased_declared_stress_changes_only_its_component(
    case: str, risk_kind: str, expected: str,
) -> None:
    baseline = build_solvency_risk_aggregation(_aggregation_input(_case_input("baseline"))).to_dict()
    changed = build_solvency_risk_aggregation(_aggregation_input(_case_input(case))).to_dict()
    before = {row["risk_kind"]: row["model_loss_amount"] for row in baseline["component_rows"]}
    after = {row["risk_kind"]: row["model_loss_amount"] for row in changed["component_rows"]}
    assert after[risk_kind] == expected
    assert {key: amount for key, amount in after.items() if key != risk_kind} == {
        key: amount for key, amount in before.items() if key != risk_kind
    }
    assert Decimal(changed["totals"]["net_model_stress_loss"]) > Decimal(
        baseline["totals"]["net_model_stress_loss"]
    )
    assert changed["source_model_balance_content_digest"] == baseline["source_model_balance_content_digest"]


def test_inclusive_management_limits_have_independent_boundary_failures() -> None:
    value = _case_input("baseline")
    value["management_limits"]["max_net_model_stress_loss"] = "1.6"
    value["management_limits"]["min_remaining_model_equity_proxy"] = "317.4"
    equal = build_solvency_capital_readiness(value).to_dict()["management_evaluation"]
    assert (equal["loss_limit_met"], equal["equity_floor_met"], equal["both_limits_met"]) == (
        True, True, True,
    )
    value["management_limits"]["max_net_model_stress_loss"] = "1.5999"
    loss_fail = build_solvency_capital_readiness(value).to_dict()["management_evaluation"]
    assert (loss_fail["loss_limit_met"], loss_fail["equity_floor_met"], loss_fail["both_limits_met"]) == (
        False, True, False,
    )
    value["management_limits"]["max_net_model_stress_loss"] = "1.6"
    value["management_limits"]["min_remaining_model_equity_proxy"] = "317.4001"
    equity_fail = build_solvency_capital_readiness(value).to_dict()["management_evaluation"]
    assert (equity_fail["loss_limit_met"], equity_fail["equity_floor_met"], equity_fail["both_limits_met"]) == (
        True, False, False,
    )


@pytest.mark.parametrize("error", ["double_stress", "buffer_over_gross"])
def test_invalid_chain_never_returns_partial_capital_values(error: str) -> None:
    value = _case_input("baseline")
    if error == "double_stress":
        _aggregation_input(value)["counterparty_cases"][0]["exposure_id"] = "motor_assets"
        expected_code = "exposure_stressed_twice"
    else:
        _aggregation_input(value)["loss_absorption"]["capacity_amount"] = "2"
        _aggregation_input(value)["loss_absorption"]["applied_amount"] = "2"
        expected_code = "buffer_gross_exceeded"
    report = build_solvency_capital_readiness(value).to_dict()
    assert report["valid"] is False
    assert report["management_evaluation"] is None
    assert report["readiness_rows"] == []
    assert report["content_digest"] is None
    assert report["source_model_balance_content_digest"] is None
    assert report["source_risk_aggregation_content_digest"] is None
    assert expected_code in {issue["code"] for issue in report["issues"]}
    assert all(value is None for key, value in report["regulatory_metrics"].items() if key != "status")
