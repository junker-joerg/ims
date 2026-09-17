import copy
import json
from decimal import Decimal, localcontext
from pathlib import Path

import pytest

from ims.accounting.life_closed_cohort_balance import build_life_closed_cohort_balance
from ims.accounting.life_cohort_balance import (
    LIFE_COHORT_RESULT_VERSION,
    build_life_cohort_balance,
)
from ims.model.life_sector_v3_contract import LIFE_SECTOR_V3_CONTRACT_VERSION


FIXTURE = Path(__file__).parent / "fixtures" / "life_cohort_balance_v1.json"
CLOSED_FIXTURE = Path(__file__).parent / "fixtures" / "life_closed_cohort_v1.json"


def _input() -> dict:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def _codes(result: dict) -> set[str]:
    assert result["valid"] is False
    assert result["rows"] == []
    assert result["calculated_period_count"] == 0
    return {item["code"] for item in result["issues"]}


def test_new_cohorts_credit_only_after_issue_and_reconcile() -> None:
    scenario = _input()
    before = copy.deepcopy(scenario)
    result = build_life_cohort_balance(scenario).to_dict()

    assert result["schema_version"] == LIFE_COHORT_RESULT_VERSION
    assert result["life_sector_contract_schema_version"] == LIFE_SECTOR_V3_CONTRACT_VERSION
    assert result["valid"] is True
    assert result["calculated_period_count"] == 3
    assert result == build_life_cohort_balance(scenario).to_dict()
    assert json.loads(json.dumps(result)) == result
    assert scenario == before
    assert all(result[key] is False for key in (
        "writes_performed", "runner_invoked", "simulation_performed",
        "statutory_or_solvency_ii_claim", "historical_full_equality_claim",
    ))

    first, second, third = result["rows"]
    assert (first["guarantee_accretion"], first["deaths"],
            first["death_liability_release"], first["new_business_policies"],
            first["premiums_collected"], first["premium_liability_allocation"]) == (
        "9.0000", 2, "22.8000", 3, "29.0000", "25.0000"
    )
    assert (first["closing_active_policies"], first["closing_guarantee_liability"],
            first["closing_backing_assets"], first["closing_equity"],
            first["period_profit"]) == (15, "151.2000", "192.0000", "40.8000", "-9.2000")
    assert [cohort["cohort_id"] for cohort in first["closing_cohorts"]] == ["A", "B", "C"]
    assert first["closing_cohorts"][2] == {
        "cohort_id": "C", "issue_period": 1, "issue_term_periods": 2,
        "remaining_periods": 2, "active_policies": 3,
        "guaranteed_rate_per_period": "0.200000", "guarantee_liability": "12.0000",
    }
    assert [item["cohort_id"] for item in first["cohort_movements"]] == ["A", "B"]

    assert (second["guarantee_accretion"], second["deaths"],
            second["death_liability_release"], second["maturities"],
            second["maturity_liability_release"], second["new_business_policies"]) == (
        "11.7600", 2, "27.2950", 10, "134.2650", 2
    )
    assert (second["closing_active_policies"], second["closing_guarantee_liability"],
            second["closing_backing_assets"], second["closing_equity"],
            second["period_profit"]) == (5, "24.4000", "56.7350", "32.3350", "-3.4650")
    assert [cohort["cohort_id"] for cohort in second["closing_cohorts"]] == ["C", "D"]
    assert second["closing_cohorts"][1]["issue_period"] == 2
    assert second["closing_cohorts"][1]["guarantee_liability"] == "8.0000"
    assert [item["cohort_id"] for item in second["cohort_movements"]] == ["A", "B", "C"]
    assert second["cohort_movements"][2]["guarantee_accretion"] == "2.4000"

    assert (third["guarantee_accretion"], third["maturities"],
            third["maturity_benefits_paid"], third["closing_active_policies"],
            third["closing_guarantee_liability"], third["closing_backing_assets"],
            third["period_profit"]) == (
        "5.6800", 5, "33.0800", 0, "0.0000", "28.6550", "-3.6800"
    )
    assert third["cohort_movements"][1]["cohort_id"] == "D"
    assert third["cohort_movements"][1]["guarantee_accretion"] == "2.4000"
    assert third["closing_cohorts"] == []

    for row in result["rows"]:
        assert row["opening_active_policies"] == sum(item["active_policies"] for item in row["opening_cohorts"])
        assert row["closing_active_policies"] == sum(item["active_policies"] for item in row["closing_cohorts"])
        assert Decimal(row["opening_guarantee_liability"]) == sum(
            (Decimal(item["guarantee_liability"]) for item in row["opening_cohorts"]), Decimal(0)
        )
        assert Decimal(row["closing_guarantee_liability"]) == sum(
            (Decimal(item["guarantee_liability"]) for item in row["closing_cohorts"]), Decimal(0)
        )
        assert Decimal(row["closing_backing_assets"]) == (
            Decimal(row["closing_guarantee_liability"]) + Decimal(row["closing_equity"])
        )
        assert row["closing_active_policies"] == (
            row["opening_active_policies"] - row["deaths"] - row["maturities"]
            + row["new_business_policies"]
        )
    for previous, following in zip(result["rows"], result["rows"][1:]):
        assert following["opening_cohorts"] == previous["closing_cohorts"]
        for name in ("active_policies", "backing_assets", "guarantee_liability", "equity"):
            assert following[f"opening_{name}"] == previous[f"closing_{name}"]


def test_input_order_and_prefix_do_not_change_results() -> None:
    scenario = _input()
    full = build_life_cohort_balance(scenario).to_dict()
    reordered = copy.deepcopy(scenario)
    reordered["opening"]["cohorts"].reverse()
    for period in reordered["periods"]:
        period["cohort_flows"].reverse()
        period["new_business"].reverse()
    assert build_life_cohort_balance(reordered).to_dict() == full

    scenario["periods"] = scenario["periods"][:2]
    assert build_life_cohort_balance(scenario).to_dict()["rows"] == full["rows"][:2]


def test_one_cohort_without_new_business_preserves_pr161_totals() -> None:
    old = json.loads(CLOSED_FIXTURE.read_text(encoding="utf-8"))
    scenario = _input()
    scenario["opening"] = {
        "opening_active_policies": old["opening"]["opening_active_policies"],
        "opening_backing_assets": old["opening"]["opening_backing_assets"],
        "opening_guarantee_liability": old["opening"]["opening_guarantee_liability"],
        "opening_equity": old["opening"]["opening_equity"],
        "cohorts": [{
            "cohort_id": "base", "issue_period": 0,
            "issue_term_periods": old["opening"]["opening_remaining_periods"],
            "remaining_periods": old["opening"]["opening_remaining_periods"],
            "active_policies": old["opening"]["opening_active_policies"],
            "guaranteed_rate_per_period": old["guaranteed_rate_per_period"],
            "guarantee_liability": old["opening"]["opening_guarantee_liability"],
        }],
    }
    scenario["periods"] = [{
        "period": item["period"],
        "cohort_flows": [{
            "cohort_id": "base",
            "renewal_premiums_collected": item["renewal_premiums_collected"],
            "renewal_liability_allocation": item["renewal_liability_allocation"],
            "deaths": item["deaths"],
            "death_benefits_paid": item["death_benefits_paid"],
        }],
        "new_business": [],
        "investment_result": item["investment_result"],
        "operating_expense_paid": item["operating_expense_paid"],
        "capital_contribution": item["capital_contribution"],
        "capital_distribution": item["capital_distribution"],
    } for item in old["periods"]]
    new_result = build_life_cohort_balance(scenario).to_dict()
    old_result = build_life_closed_cohort_balance(old).to_dict()
    assert new_result["valid"] is True
    for new, previous in zip(new_result["rows"], old_result["rows"]):
        shared = new.keys() & previous.keys()
        assert {key: new[key] for key in shared} == {key: previous[key] for key in shared}
        assert new["new_business_policies"] == 0
        assert new["new_business_cohorts"] == []


def test_empty_opening_can_issue_then_mature_one_period_term() -> None:
    scenario = _input()
    scenario["opening"] = {
        "opening_active_policies": 0,
        "opening_backing_assets": "20",
        "opening_guarantee_liability": "0",
        "opening_equity": "20",
        "cohorts": [],
    }
    scenario["periods"] = [
        {
            "period": 1, "cohort_flows": [],
            "new_business": [{
                "cohort_id": "X", "issue_term_periods": 1,
                "guaranteed_rate_per_period": "0.5", "new_business_policies": 1,
                "new_business_premiums_collected": "10",
                "new_business_liability_allocation": "9",
            }],
            "investment_result": "0", "operating_expense_paid": "0",
            "capital_contribution": "0", "capital_distribution": "0",
        },
        {
            "period": 2,
            "cohort_flows": [{
                "cohort_id": "X", "renewal_premiums_collected": "0",
                "renewal_liability_allocation": "0", "deaths": 0,
                "death_benefits_paid": "0",
            }],
            "new_business": [], "investment_result": "0",
            "operating_expense_paid": "0", "capital_contribution": "0",
            "capital_distribution": "0",
        },
    ]
    first, second = build_life_cohort_balance(scenario).to_dict()["rows"]
    assert (first["guarantee_accretion"], first["maturities"],
            first["closing_guarantee_liability"]) == ("0.0000", 0, "9.0000")
    assert (second["guarantee_accretion"], second["maturities"],
            second["maturity_benefits_paid"], second["closing_equity"]) == (
        "4.5000", 1, "13.5000", "16.5000"
    )

    scenario["periods"].extend([
        {
            "period": 3, "cohort_flows": [], "new_business": [],
            "investment_result": "0", "operating_expense_paid": "0",
            "capital_contribution": "0", "capital_distribution": "0",
        },
        {
            "period": 4, "cohort_flows": [],
            "new_business": [{
                "cohort_id": "Y", "issue_term_periods": 2,
                "guaranteed_rate_per_period": "0", "new_business_policies": 1,
                "new_business_premiums_collected": "1",
                "new_business_liability_allocation": "1",
            }],
            "investment_result": "0", "operating_expense_paid": "0",
            "capital_contribution": "0", "capital_distribution": "0",
        },
    ])
    _, _, gap, restart = build_life_cohort_balance(scenario).to_dict()["rows"]
    assert gap["opening_cohorts"] == gap["closing_cohorts"] == []
    assert gap["closing_backing_assets"] == "16.5000"
    assert restart["closing_active_policies"] == 1
    assert restart["closing_cohorts"][0]["issue_period"] == 4


def test_half_even_credit_is_per_cohort_not_on_aggregate() -> None:
    scenario = _input()
    scenario["opening"] = {
        "opening_active_policies": 2,
        "opening_backing_assets": "0.0002",
        "opening_guarantee_liability": "0.0002",
        "opening_equity": "0",
        "cohorts": [{
            "cohort_id": name, "issue_period": 0, "issue_term_periods": 2,
            "remaining_periods": 2, "active_policies": 1,
            "guaranteed_rate_per_period": "0.5", "guarantee_liability": "0.0001",
        } for name in ("A", "B")],
    }
    scenario["periods"] = [{
        "period": 1,
        "cohort_flows": [{
            "cohort_id": name, "renewal_premiums_collected": "0",
            "renewal_liability_allocation": "0", "deaths": 0,
            "death_benefits_paid": "0",
        } for name in ("A", "B")],
        "new_business": [], "investment_result": "0",
        "operating_expense_paid": "0", "capital_contribution": "0",
        "capital_distribution": "0",
    }]
    with localcontext() as context:
        context.prec = 3
        row = build_life_cohort_balance(scenario).to_dict()["rows"][0]
    assert row["guarantee_accretion"] == "0.0000"
    assert row["closing_guarantee_liability"] == "0.0002"


def test_new_cohort_can_run_to_period_100_with_stable_prefix() -> None:
    scenario = _input()
    scenario["opening"] = {
        "opening_active_policies": 1,
        "opening_backing_assets": "120",
        "opening_guarantee_liability": "100",
        "opening_equity": "20",
        "cohorts": [{
            "cohort_id": "old", "issue_period": 0,
            "issue_term_periods": 1, "remaining_periods": 1,
            "active_policies": 1, "guaranteed_rate_per_period": "0",
            "guarantee_liability": "100",
        }],
    }
    first = {
        "period": 1,
        "cohort_flows": [{
            "cohort_id": "old", "renewal_premiums_collected": "0",
            "renewal_liability_allocation": "0", "deaths": 0,
            "death_benefits_paid": "0",
        }],
        "new_business": [{
            "cohort_id": "new", "issue_term_periods": 99,
            "guaranteed_rate_per_period": "0", "new_business_policies": 1,
            "new_business_premiums_collected": "5",
            "new_business_liability_allocation": "5",
        }],
        "investment_result": "0", "operating_expense_paid": "0",
        "capital_contribution": "0", "capital_distribution": "0",
    }
    later = [{
        "period": number,
        "cohort_flows": [{
            "cohort_id": "new", "renewal_premiums_collected": "0",
            "renewal_liability_allocation": "0", "deaths": 0,
            "death_benefits_paid": "0",
        }],
        "new_business": [], "investment_result": "0",
        "operating_expense_paid": "0", "capital_contribution": "0",
        "capital_distribution": "0",
    } for number in range(2, 101)]
    scenario["periods"] = [first, *later]
    prefix = copy.deepcopy(scenario)
    prefix["periods"] = prefix["periods"][:2]
    full = build_life_cohort_balance(scenario).to_dict()
    assert full["valid"] is True
    assert full["calculated_period_count"] == 100
    assert full["rows"][:2] == build_life_cohort_balance(prefix).to_dict()["rows"]
    assert full["rows"][0]["maturity_benefits_paid"] == "100.0000"
    assert full["rows"][0]["closing_guarantee_liability"] == "5.0000"
    assert full["rows"][1]["maturities"] == 0
    assert full["rows"][-1]["maturity_benefits_paid"] == "5.0000"
    assert full["rows"][-1]["closing_active_policies"] == 0
    assert full["rows"][-1]["closing_equity"] == "20.0000"


@pytest.mark.parametrize(("path", "value", "code"), [
    (("schema_version",), "ims.life-cohort-balance-input.v0", "contract_value_mismatch"),
    (("opening", "cohorts", 1, "issue_period"), 0, "cohort_vintage_invalid"),
    (("opening", "cohorts", 1, "cohort_id"), "A", "cohort_id_duplicate"),
    (("opening", "opening_guarantee_liability"), "139", "opening_cohort_liability_mismatch"),
    (("periods", 0, "new_business", 0, "cohort_id"), "A", "cohort_id_reused"),
    (("periods", 0, "new_business", 0, "issue_term_periods"), 0, "count_invalid"),
    (("periods", 0, "new_business", 0, "guaranteed_rate_per_period"), "1.1", "rate_invalid"),
    (("periods", 0, "new_business", 0, "new_business_policies"), True, "count_invalid"),
    (("periods", 0, "new_business", 0, "new_business_liability_allocation"), "16", "premium_allocation_exceeds_collected"),
    (("periods", 0, "cohort_flows", 1, "death_benefits_paid"), "1", "death_benefit_without_death"),
    (("periods", 1, "cohort_flows", 2, "deaths"), 4, "deaths_exceed_opening"),
    (("periods", 2, "capital_distribution"), "1000", "negative_closing_assets"),
    (("periods", 2, "cohort_flows", 0, "cohort_id"), "A", "cohort_flows_mismatch"),
])
def test_invalid_cases_return_no_partial_rows(path: tuple, value: object, code: str) -> None:
    scenario = _input()
    target = scenario
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = value
    assert code in _codes(build_life_cohort_balance(scenario).to_dict())


def test_missing_extra_duplicate_and_reused_ids_are_rejected() -> None:
    scenario = _input()
    scenario["periods"][0]["cohort_flows"].pop()
    assert "cohort_flows_mismatch" in _codes(build_life_cohort_balance(scenario).to_dict())

    scenario = _input()
    scenario["periods"][0]["cohort_flows"].append({
        **scenario["periods"][0]["cohort_flows"][0], "cohort_id": "C",
    })
    assert "cohort_flows_mismatch" in _codes(build_life_cohort_balance(scenario).to_dict())

    scenario = _input()
    scenario["periods"][0]["new_business"].append(copy.deepcopy(scenario["periods"][0]["new_business"][0]))
    assert "cohort_id_duplicate" in _codes(build_life_cohort_balance(scenario).to_dict())

    scenario = _input()
    scenario["periods"][2]["new_business"] = [{
        **scenario["periods"][0]["new_business"][0], "cohort_id": "A",
    }]
    assert "cohort_id_reused" in _codes(build_life_cohort_balance(scenario).to_dict())

    scenario = _input()
    scenario["periods"][0]["new_business"][0]["deaths"] = 0
    assert "field_unknown" in _codes(build_life_cohort_balance(scenario).to_dict())

    scenario = _input()
    template = scenario["periods"][0]["new_business"][0]
    scenario["periods"][0]["new_business"].extend(
        {**template, "cohort_id": f"N{number}"} for number in range(99)
    )
    assert "cohort_limit_exceeded" in _codes(build_life_cohort_balance(scenario).to_dict())
