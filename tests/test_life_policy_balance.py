import copy
import json
from decimal import Decimal, localcontext
from pathlib import Path

import pytest

from ims.accounting.life_policy_balance import (
    LIFE_POLICY_RESULT_VERSION,
    build_life_policy_balance,
)


FIXTURE = Path(__file__).parent / "fixtures" / "life_policy_balance_v1.json"


def _input() -> dict:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def _codes(scenario: dict) -> set[str]:
    result = build_life_policy_balance(scenario).to_dict()
    assert result["valid"] is False
    assert result["rows"] == []
    assert result["calculated_period_count"] == 0
    return {issue["code"] for issue in result["issues"]}


def _set(scenario: dict, path: tuple, value: object) -> None:
    target = scenario
    for item in path[:-1]:
        target = target[item]
    target[path[-1]] = value


def test_policy_maturities_reconcile_on_all_three_levels() -> None:
    scenario = _input()
    original = copy.deepcopy(scenario)
    result = build_life_policy_balance(scenario).to_dict()
    assert result["schema_version"] == LIFE_POLICY_RESULT_VERSION
    assert result["mode"] == "fully_enumerated_policies"
    assert result["valid"] is True
    assert result["calculated_period_count"] == 2
    assert result == build_life_policy_balance(scenario).to_dict()
    assert json.loads(json.dumps(result)) == result
    assert scenario == original
    assert all(result[key] is False for key in (
        "writes_performed", "runner_invoked", "simulation_performed",
        "statutory_or_solvency_ii_claim", "historical_full_equality_claim",
    ))

    first, second = result["rows"]
    assert (first["guarantee_accretion"], first["deaths"],
            first["death_liability_release"], first["death_benefits_paid"],
            first["maturities"], first["maturity_liability_release"],
            first["maturity_benefits_paid"]) == (
        "7.0000", 1, "67.0000", "65.0000", 1, "22.0000", "25.0000"
    )
    assert (first["closing_active_policies"], first["closing_backing_assets"],
            first["closing_guarantee_liability"], first["closing_equity"],
            first["period_profit"]) == (2, "104.0000", "54.0000", "50.0000", "0.0000")
    assert [item["policy_id"] for item in first["closing_policies"]] == ["A1", "C1"]
    assert [item["cohort_id"] for item in first["closing_cohorts"]] == ["A", "C"]
    assert first["new_business_cohorts"][0]["cohort_id"] == "C"
    assert first["new_policy_issues"][0]["policy_id"] == "C1"
    assert first["new_policy_issues"][0]["issue_period"] == 1
    assert first["policy_movements"][2]["maturity_benefits_paid"] == "25.0000"
    assert first["cohort_movements"][1]["maturity_liability_release"] == "22.0000"

    assert second["opening_policies"] == first["closing_policies"]
    assert second["opening_cohorts"] == first["closing_cohorts"]
    assert (second["guarantee_accretion"], second["maturity_liability_release"],
            second["maturity_benefits_paid"], second["period_profit"],
            second["closing_backing_assets"], second["closing_equity"]) == (
        "3.9000", "61.9000", "72.0000", "-12.0000", "33.0000", "33.0000"
    )
    assert second["closing_policies"] == second["closing_cohorts"] == []

    for row in result["rows"]:
        assert row["opening_active_policies"] == len(row["opening_policies"])
        assert row["closing_active_policies"] == len(row["closing_policies"])
        assert row["closing_active_policies"] == sum(cohort["active_policies"] for cohort in row["closing_cohorts"])
        assert Decimal(row["closing_guarantee_liability"]) == sum(
            (Decimal(policy["guarantee_liability"]) for policy in row["closing_policies"]), Decimal(0)
        )
        assert Decimal(row["closing_guarantee_liability"]) == sum(
            (Decimal(cohort["guarantee_liability"]) for cohort in row["closing_cohorts"]), Decimal(0)
        )
        assert Decimal(row["closing_backing_assets"]) == (
            Decimal(row["closing_guarantee_liability"]) + Decimal(row["closing_equity"])
        )
        assert Decimal(row["maturity_benefits_paid"]) == sum(
            (Decimal(m["maturity_benefits_paid"]) for m in row["policy_movements"]), Decimal(0)
        )
        assert Decimal(row["maturity_benefits_paid"]) == sum(
            (Decimal(m["maturity_benefits_paid"]) for m in row["cohort_movements"]), Decimal(0)
        )


def test_order_and_prefix_are_stable() -> None:
    scenario = _input()
    full = build_life_policy_balance(scenario).to_dict()
    reordered = copy.deepcopy(scenario)
    for name in ("cohorts", "policies"):
        reordered["opening"][name].reverse()
    for period in reordered["periods"]:
        period["policy_flows"].reverse()
        period["new_business"].reverse()
    assert build_life_policy_balance(reordered).to_dict() == full
    scenario["periods"] = scenario["periods"][:1]
    assert build_life_policy_balance(scenario).to_dict()["rows"] == full["rows"][:1]


def test_credit_rounds_per_policy_and_then_aggregates() -> None:
    scenario = _input()
    scenario["opening"] = {
        "opening_active_policies": 2, "opening_backing_assets": "0.0002",
        "opening_guarantee_liability": "0.0002", "opening_equity": "0",
        "cohorts": [{
            "cohort_id": "A", "issue_period": 0, "issue_term_periods": 2,
            "remaining_periods": 2, "active_policies": 2,
            "guaranteed_rate_per_period": "0.5", "guarantee_liability": "0.0002",
        }],
        "policies": [{
            "policy_id": name, "cohort_id": "A", "issue_term_periods": 2,
            "remaining_periods": 2, "guaranteed_rate_per_period": "0.5",
            "guarantee_liability": "0.0001",
        } for name in ("A1", "A2")],
    }
    scenario["periods"] = [{
        "period": 1, "policy_flows": [{
            "policy_id": name, "renewal_premiums_collected": "0",
            "renewal_liability_allocation": "0", "death": False,
            "death_benefits_paid": "0", "maturity_benefits_paid": "0",
        } for name in ("A1", "A2")],
        "new_business": [], "investment_result": "0", "operating_expense_paid": "0",
        "capital_contribution": "0", "capital_distribution": "0",
    }]
    with localcontext() as context:
        context.prec = 3
        row = build_life_policy_balance(scenario).to_dict()["rows"][0]
    assert row["guarantee_accretion"] == "0.0000"
    assert row["closing_guarantee_liability"] == "0.0002"
    assert row["closing_cohorts"][0]["guarantee_liability"] == "0.0002"


@pytest.mark.parametrize(("path", "value", "code"), [
    (("mode",), "aggregate_cohorts", "contract_value_mismatch"),
    (("opening", "policies", 0, "cohort_id"), "X", "unknown_cohort_id"),
    (("opening", "policies", 0, "remaining_periods"), 1, "policy_issue_terms_mismatch"),
    (("opening", "policies", 1, "policy_id"), "A1", "policy_id_duplicate"),
    (("opening", "policies", 0, "guarantee_liability"), "39", "cohort_policy_liability_mismatch"),
    (("periods", 0, "policy_flows", 0, "policy_id"), "X", "cohort_flows_mismatch"),
    (("periods", 0, "policy_flows", 0, "death_benefits_paid"), "1", "death_benefit_without_death"),
    (("periods", 0, "policy_flows", 2, "maturity_benefits_paid"), "21", "maturity_benefit_below_guarantee"),
    (("periods", 0, "policy_flows", 0, "maturity_benefits_paid"), "1", "maturity_benefit_not_due"),
    (("periods", 0, "policy_flows", 1, "maturity_benefits_paid"), "1", "maturity_benefit_not_due"),
    (("periods", 1, "policy_flows", 0, "maturity_benefits_paid"), "52", "maturity_benefit_below_guarantee"),
    (("periods", 1, "policy_flows", 0, "death"), True, "maturity_benefit_not_due"),
    (("periods", 1, "capital_distribution"), "1000", "negative_closing_assets"),
    (("periods", 0, "new_business", 0, "cohort_id"), "A", "cohort_id_reused"),
    (("periods", 0, "new_business", 0, "new_business_policies"), 2, "new_policy_count_mismatch"),
    (("periods", 0, "new_business", 0, "new_business_premiums_collected"), "11", "new_policy_premium_mismatch"),
    (("periods", 0, "new_business", 0, "new_business_liability_allocation"), "7", "new_policy_allocation_mismatch"),
    (("periods", 0, "new_business", 0, "policies", 0, "policy_id"), "A1", "policy_id_reused"),
])
def test_invalid_inputs_return_no_partial_rows(path: tuple, value: object, code: str) -> None:
    scenario = _input()
    _set(scenario, path, value)
    assert code in _codes(scenario)


def test_missing_flow_and_undeclared_field_rejected() -> None:
    scenario = _input()
    scenario["periods"][1]["policy_flows"].pop()
    assert "cohort_flows_mismatch" in _codes(scenario)

    scenario = _input()
    scenario["periods"][0]["new_business"][0]["policies"][0]["payout_formula"] = "unknown"
    assert "field_unknown" in _codes(scenario)


def test_policy_limit_is_on_active_policies_not_total_ever_issued() -> None:
    scenario = _input()
    template = scenario["opening"]["policies"][0]
    scenario["opening"]["cohorts"][0]["active_policies"] = 100
    scenario["opening"]["cohorts"][0]["guarantee_liability"] = "100"
    scenario["opening"]["cohorts"].pop()
    scenario["opening"]["opening_active_policies"] = 100
    scenario["opening"]["opening_guarantee_liability"] = "100"
    scenario["opening"]["opening_backing_assets"] = "130"
    scenario["opening"]["policies"] = [
        {**template, "policy_id": f"A{number}", "guarantee_liability": "1"}
        for number in range(100)
    ]
    scenario["periods"] = [scenario["periods"][0]]
    scenario["periods"][0]["policy_flows"] = [{
        "policy_id": f"A{number}", "renewal_premiums_collected": "0",
        "renewal_liability_allocation": "0", "death": False,
        "death_benefits_paid": "0", "maturity_benefits_paid": "0",
    } for number in range(100)]
    scenario["periods"][0]["investment_result"] = "0"
    scenario["periods"][0]["operating_expense_paid"] = "0"
    scenario["periods"][0]["capital_contribution"] = "0"
    scenario["periods"][0]["new_business"] = []
    assert build_life_policy_balance(scenario).to_dict()["rows"][0]["closing_active_policies"] == 100
    scenario["periods"][0]["new_business"] = _input()["periods"][0]["new_business"]
    assert "policy_limit_exceeded" in _codes(scenario)


def test_policy_id_cannot_be_reissued_after_maturity() -> None:
    scenario = _input()
    scenario["periods"][1]["new_business"] = [{
        **scenario["periods"][0]["new_business"][0],
        "cohort_id": "D",
        "policies": [{
            **scenario["periods"][0]["new_business"][0]["policies"][0],
            "policy_id": "B1",
        }],
    }]
    assert "policy_id_reused" in _codes(scenario)


def test_one_policy_100_periods_and_stable_prefix() -> None:
    scenario = _input()
    scenario["opening"] = {
        "opening_active_policies": 1, "opening_backing_assets": "120",
        "opening_guarantee_liability": "100", "opening_equity": "20",
        "cohorts": [{
            "cohort_id": "A", "issue_period": 0, "issue_term_periods": 100,
            "remaining_periods": 100, "active_policies": 1,
            "guaranteed_rate_per_period": "0", "guarantee_liability": "100",
        }],
        "policies": [{
            "policy_id": "A1", "cohort_id": "A", "issue_term_periods": 100,
            "remaining_periods": 100, "guaranteed_rate_per_period": "0",
            "guarantee_liability": "100",
        }],
    }
    scenario["periods"] = [{
        "period": number,
        "policy_flows": [{
            "policy_id": "A1", "renewal_premiums_collected": "0",
            "renewal_liability_allocation": "0", "death": False,
            "death_benefits_paid": "0",
            "maturity_benefits_paid": "105" if number == 100 else "0",
        }],
        "new_business": [], "investment_result": "0", "operating_expense_paid": "0",
        "capital_contribution": "0", "capital_distribution": "0",
    } for number in range(1, 101)]
    full = build_life_policy_balance(scenario).to_dict()
    assert full["valid"] is True
    assert full["calculated_period_count"] == 100
    assert full["rows"][-1]["maturity_liability_release"] == "100.0000"
    assert full["rows"][-1]["maturity_benefits_paid"] == "105.0000"
    assert full["rows"][-1]["closing_equity"] == "15.0000"
    scenario["periods"] = scenario["periods"][:2]
    assert build_life_policy_balance(scenario).to_dict()["rows"] == full["rows"][:2]
