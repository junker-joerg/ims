import copy
import json
from pathlib import Path

import pytest

from ims.accounting.life_period_chain import (
    LIFE_PERIOD_CHAIN_RESULT_VERSION,
    run_life_policy_period_chain,
)
from ims.accounting.life_policy_balance import build_life_policy_balance


FIXTURE = Path(__file__).parent / "fixtures" / "life_period_chain_v1.json"
POLICY_FIXTURE = Path(__file__).parent / "fixtures" / "life_policy_balance_v1.json"


def _input() -> dict:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def _codes(scenario: dict, **kwargs) -> set[str]:
    result = run_life_policy_period_chain(scenario, **kwargs).to_dict()
    assert result["valid"] is False
    assert result["rows"] == []
    assert result["resolved_sources"] == []
    assert result["calculated_period_count"] == 0
    assert result["policy_periods"] == 0
    return {item["code"] for item in result["issues"]}


def _curve_case() -> dict:
    scenario = _input()
    scenario["opening"] = {
        "opening_active_policies": 2, "opening_backing_assets": "30",
        "opening_guarantee_liability": "20", "opening_equity": "10",
        "cohorts": [{
            "cohort_id": "A", "issue_period": 0, "issue_term_periods": 2,
            "remaining_periods": 2, "active_policies": 2,
            "guaranteed_rate_per_period": "0", "guarantee_liability": "20",
        }],
        "policies": [{
            "policy_id": name, "cohort_id": "A", "issue_term_periods": 2,
            "remaining_periods": 2, "guaranteed_rate_per_period": "0",
            "guarantee_liability": "10",
        } for name in ("A1", "A2")],
    }
    scenario["assumptions"]["investment"] = {
        "mode": "insurer_rule_on_opening_backing_assets",
        "windows": [{"start_period": 1, "end_period": 2, "rate_per_period": "0.1"}],
    }
    scenario["assumptions"]["mortality"] = {
        "mode": "exogenous_deterministic_rate_curve",
        "windows": [{"start_period": 1, "end_period": 2, "rate_per_period": "0.5"}],
    }
    scenario["periods"] = [{
        "period": period,
        "policy_flows": [{
            "policy_id": name, "renewal_premiums_collected": "0",
            "renewal_liability_allocation": "0", "death_benefit_if_death": "10",
            "maturity_benefit_if_due": "10" if period == 2 else "0",
        } for name in (("A1", "A2") if period == 1 else ("A2",))],
        "new_business": [], "operating_expense_paid": "0",
        "capital_contribution": "0", "capital_distribution": "0",
    } for period in (1, 2)]
    return scenario


def test_explicit_chain_preserves_pr163_values_and_is_json_stable() -> None:
    scenario = _input()
    before = copy.deepcopy(scenario)
    result = run_life_policy_period_chain(scenario).to_dict()
    previous = build_life_policy_balance(json.loads(POLICY_FIXTURE.read_text(encoding="utf-8"))).to_dict()
    assert result["schema_version"] == LIFE_PERIOD_CHAIN_RESULT_VERSION
    assert result["valid"] is True
    assert result["calculated_period_count"] == 2
    assert result["rows"] == previous["rows"]
    assert result["policy_periods"] == 5
    assert [source["investment_result"] for source in result["resolved_sources"]] == ["5.0000", "2.0000"]
    assert [source["death_policy_ids"] for source in result["resolved_sources"]] == [["A2"], []]
    assert result["rows"][1]["opening_policies"] == result["rows"][0]["closing_policies"]
    assert result["rows"][1]["opening_backing_assets"] == result["rows"][0]["closing_backing_assets"]
    assert result == run_life_policy_period_chain(scenario).to_dict()
    assert json.loads(json.dumps(result)) == result
    assert scenario == before
    assert all(result[key] is False for key in (
        "writes_performed", "app_runner_invoked", "historical_simulation_performed",
        "statutory_or_solvency_ii_claim", "historical_full_equality_claim",
    ))
    assert result["life_period_chain_calculated"] is True


def test_curve_sources_use_verified_carryover_and_death_before_maturity() -> None:
    result = run_life_policy_period_chain(_curve_case()).to_dict()
    assert result["valid"] is True
    first, second = result["rows"]
    assert (first["investment_result"], first["death_benefits_paid"],
            first["closing_backing_assets"], first["closing_guarantee_liability"],
            first["closing_equity"]) == ("3.0000", "10.0000", "23.0000", "10.0000", "13.0000")
    assert (second["investment_result"], second["death_benefits_paid"],
            second["maturity_benefits_paid"], second["closing_backing_assets"],
            second["closing_equity"]) == ("2.3000", "10.0000", "0.0000", "15.3000", "15.3000")
    assert [source["death_policy_ids"] for source in result["resolved_sources"]] == [["A1"], ["A2"]]
    assert [source["opening_backing_assets"] for source in result["resolved_sources"]] == ["30.0000", "23.0000"]
    assert second["opening_policies"] == first["closing_policies"]
    assert second["closing_policies"] == []


def test_input_order_and_horizon_extension_preserve_prefix() -> None:
    scenario = _input()
    full = run_life_policy_period_chain(scenario).to_dict()
    reordered = copy.deepcopy(scenario)
    reordered["opening"]["cohorts"].reverse()
    reordered["opening"]["policies"].reverse()
    for period in reordered["periods"]:
        period["policy_flows"].reverse()
        period["new_business"].reverse()
    assert run_life_policy_period_chain(reordered).to_dict() == full

    prefix = copy.deepcopy(scenario)
    prefix["periods"] = prefix["periods"][:1]
    prefix["assumptions"]["period_count"] = 1
    for source in ("investment", "mortality"):
        prefix["assumptions"][source]["periods"] = prefix["assumptions"][source]["periods"][:1]
    shortened = run_life_policy_period_chain(prefix).to_dict()
    assert shortened["valid"] is True
    assert shortened["rows"] == full["rows"][:1]
    assert shortened["resolved_sources"] == full["resolved_sources"][:1]


def test_one_policy_can_carry_through_100_periods() -> None:
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
    scenario["assumptions"]["period_count"] = 100
    scenario["assumptions"]["investment"] = {
        "mode": "insurer_rule_on_opening_backing_assets",
        "windows": [{"start_period": 1, "end_period": 100, "rate_per_period": "0"}],
    }
    scenario["assumptions"]["mortality"] = {
        "mode": "explicit_death_policy_ids",
        "periods": [{"period": period, "death_policy_ids": []} for period in range(1, 101)],
    }
    scenario["periods"] = [{
        "period": period,
        "policy_flows": [{
            "policy_id": "A1", "renewal_premiums_collected": "0",
            "renewal_liability_allocation": "0", "death_benefit_if_death": "0",
            "maturity_benefit_if_due": "100" if period == 100 else "0",
        }],
        "new_business": [], "operating_expense_paid": "0",
        "capital_contribution": "0", "capital_distribution": "0",
    } for period in range(1, 101)]
    full = run_life_policy_period_chain(scenario).to_dict()
    assert full["valid"] is True
    assert full["calculated_period_count"] == 100
    assert full["policy_periods"] == 100
    assert full["rows"][-1]["closing_active_policies"] == 0
    assert full["rows"][-1]["closing_backing_assets"] == "20.0000"
    assert full["rows"][-1]["closing_equity"] == "20.0000"
    prefix = copy.deepcopy(scenario)
    prefix["periods"] = prefix["periods"][:2]
    prefix["assumptions"]["period_count"] = 2
    prefix["assumptions"]["investment"]["windows"][0]["end_period"] = 2
    prefix["assumptions"]["mortality"]["periods"] = prefix["assumptions"]["mortality"]["periods"][:2]
    short = run_life_policy_period_chain(prefix).to_dict()
    assert short["rows"] == full["rows"][:2]
    assert short["resolved_sources"] == full["resolved_sources"][:2]


def test_full_100_by_100_policy_period_budget() -> None:
    scenario = _input()
    scenario["opening"] = {
        "opening_active_policies": 100, "opening_backing_assets": "200",
        "opening_guarantee_liability": "100", "opening_equity": "100",
        "cohorts": [{
            "cohort_id": "A", "issue_period": 0, "issue_term_periods": 100,
            "remaining_periods": 100, "active_policies": 100,
            "guaranteed_rate_per_period": "0", "guarantee_liability": "100",
        }],
        "policies": [{
            "policy_id": f"A{number:03}", "cohort_id": "A",
            "issue_term_periods": 100, "remaining_periods": 100,
            "guaranteed_rate_per_period": "0", "guarantee_liability": "1",
        } for number in range(100)],
    }
    scenario["assumptions"]["period_count"] = 100
    scenario["assumptions"]["investment"] = {
        "mode": "explicit_scenario",
        "periods": [{"period": period, "investment_result": "0"} for period in range(1, 101)],
    }
    scenario["assumptions"]["mortality"] = {
        "mode": "explicit_death_policy_ids",
        "periods": [{"period": period, "death_policy_ids": []} for period in range(1, 101)],
    }
    scenario["periods"] = [{
        "period": period,
        "policy_flows": [{
            "policy_id": f"A{number:03}", "renewal_premiums_collected": "0",
            "renewal_liability_allocation": "0", "death_benefit_if_death": "0",
            "maturity_benefit_if_due": "1" if period == 100 else "0",
        } for number in range(100)],
        "new_business": [], "operating_expense_paid": "0",
        "capital_contribution": "0", "capital_distribution": "0",
    } for period in range(1, 101)]
    result = run_life_policy_period_chain(scenario).to_dict()
    assert result["valid"] is True
    assert result["calculated_period_count"] == 100
    assert result["policy_periods"] == 10_000
    assert result["rows"][-1]["maturity_benefits_paid"] == "100.0000"
    assert result["rows"][-1]["closing_backing_assets"] == "100.0000"
    assert result["rows"][-1]["closing_active_policies"] == 0


@pytest.mark.parametrize(("mutate", "code"), [
    (lambda case: case["assumptions"].update({"insurer_id": 2}), "assumption_insurer_mismatch"),
    (lambda case: case["assumptions"].update({"period_count": 1}), "assumption_horizon_mismatch"),
    (lambda case: case["periods"][0].update({"investment_result": "5"}), "field_unknown"),
    (lambda case: case["periods"][0]["policy_flows"][0].update({"death": False}), "field_unknown"),
    (lambda case: case["assumptions"]["mortality"].update({"windows": []}), "field_unknown"),
    (lambda case: case["periods"][0]["new_business"][0]["policies"].extend(
        [copy.deepcopy(case["periods"][0]["new_business"][0]["policies"][0]) for _ in range(100)]
    ), "policy_list_invalid"),
    (lambda case: case["periods"][1]["policy_flows"].pop(), "policy_flows_mismatch"),
    (lambda case: case["periods"][1]["policy_flows"][0].update({"maturity_benefit_if_due": "50"}), "maturity_benefit_below_guarantee"),
    (lambda case: case["periods"][1]["policy_flows"][0].update({"death_benefit_if_death": "-1"}), "negative_amount"),
    (lambda case: case["assumptions"]["investment"]["periods"][1].update({"investment_result": "-1000"}), "negative_closing_assets"),
    (lambda case: case["assumptions"]["mortality"]["periods"][1].update({"death_policy_ids": ["A2"]}), "death_policy_not_active"),
    (lambda case: case["opening"].update({"opening_backing_assets": "149"}), "opening_identity_invalid"),
])
def test_invalid_or_late_inputs_return_no_partial_result(mutate, code: str) -> None:
    scenario = _input()
    mutate(scenario)
    assert code in _codes(scenario)


def test_cancel_between_periods_returns_no_partial_result() -> None:
    calls = 0

    def cancel() -> bool:
        nonlocal calls
        calls += 1
        return calls == 2

    assert "run_cancelled" in _codes(_input(), should_cancel=cancel)
    assert calls == 2
