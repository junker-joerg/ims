import copy
import json
from decimal import Decimal, localcontext
from pathlib import Path

import pytest

from ims.accounting.life_closed_cohort_balance import (
    LIFE_CLOSED_COHORT_RESULT_VERSION,
    build_life_closed_cohort_balance,
)
from ims.accounting.life_model_balance import build_life_model_balance
from ims.model.life_sector_v3_contract import LIFE_SECTOR_V3_CONTRACT_VERSION


FIXTURE = Path(__file__).parent / "fixtures" / "life_closed_cohort_v1.json"
V2_FIXTURE = Path(__file__).parent / "fixtures" / "life_model_balance_v1.json"


def _input() -> dict:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def _issue_codes(result: dict) -> set[str]:
    assert result["valid"] is False
    assert result["rows"] == []
    assert result["calculated_period_count"] == 0
    return {item["code"] for item in result["issues"]}


def test_deaths_and_capital_are_separate_from_release_and_profit() -> None:
    scenario = _input()
    before = copy.deepcopy(scenario)
    result = build_life_closed_cohort_balance(scenario).to_dict()

    assert result["schema_version"] == LIFE_CLOSED_COHORT_RESULT_VERSION
    assert result["life_sector_contract_schema_version"] == LIFE_SECTOR_V3_CONTRACT_VERSION
    assert result["valid"] is True
    assert result["calculated_period_count"] == 3
    assert result == build_life_closed_cohort_balance(scenario).to_dict()
    assert json.loads(json.dumps(result)) == result
    assert scenario == before
    assert all(result[key] is False for key in (
        "writes_performed", "runner_invoked", "simulation_performed",
        "statutory_or_solvency_ii_claim", "historical_full_equality_claim",
    ))
    prefix = copy.deepcopy(scenario)
    prefix["periods"] = prefix["periods"][:2]
    assert build_life_closed_cohort_balance(prefix).to_dict()["rows"] == result["rows"][:2]

    first, second, third = result["rows"]
    assert (first["deaths"], first["death_benefits_paid"],
            first["death_liability_release"], first["maturities"]) == (
        2, "30.0000", "22.8000", 0
    )
    assert (first["guarantee_accretion"], first["closing_active_policies"],
            first["closing_guarantee_liability"], first["closing_backing_assets"],
            first["closing_equity"], first["period_profit"]) == (
        "5.0000", 8, "91.2000", "131.0000", "39.8000", "-5.2000"
    )
    assert (second["deaths"], second["death_liability_release"],
            second["capital_distribution"], second["closing_active_policies"],
            second["closing_guarantee_liability"], second["closing_backing_assets"],
            second["closing_equity"], second["period_profit"]) == (
        1, "13.0950", "5.0000", 7, "91.6650", "129.0000", "37.3350", "2.5350"
    )
    assert (third["deaths"], third["maturities"],
            third["maturity_liability_release"], third["maturity_benefits_paid"],
            third["closing_backing_assets"], third["closing_equity"]) == (
        0, 7, "105.2482", "105.2482", "38.7518", "38.7518"
    )
    for row in result["rows"]:
        assert Decimal(row["closing_backing_assets"]) == (
            Decimal(row["closing_guarantee_liability"]) + Decimal(row["closing_equity"])
        )
        assert Decimal(row["liability_release"]) == (
            Decimal(row["death_liability_release"]) + Decimal(row["maturity_liability_release"])
        )
        assert row["opening_active_policies"] - row["deaths"] - row["maturities"] == row["closing_active_policies"]
    for previous, following in zip(result["rows"], result["rows"][1:]):
        for name in ("active_policies", "remaining_periods", "backing_assets", "guarantee_liability", "equity"):
            assert following[f"opening_{name}"] == previous[f"closing_{name}"]


def test_capital_movements_change_assets_and_equity_but_not_profit() -> None:
    with_capital = _input()
    without_capital = copy.deepcopy(with_capital)
    without_capital["periods"][0]["capital_contribution"] = "0"
    with_capital["periods"] = with_capital["periods"][:1]
    without_capital["periods"] = without_capital["periods"][:1]
    funded = build_life_closed_cohort_balance(with_capital).to_dict()["rows"][0]
    unfunded = build_life_closed_cohort_balance(without_capital).to_dict()["rows"][0]

    assert funded["period_profit"] == unfunded["period_profit"] == "-5.2000"
    assert funded["closing_guarantee_liability"] == unfunded["closing_guarantee_liability"]
    assert Decimal(funded["closing_backing_assets"]) - Decimal(unfunded["closing_backing_assets"]) == 25
    assert Decimal(funded["closing_equity"]) - Decimal(unfunded["closing_equity"]) == 25

    with_distribution = _input()
    without_distribution = copy.deepcopy(with_distribution)
    without_distribution["periods"][1]["capital_distribution"] = "0"
    distributed = build_life_closed_cohort_balance(with_distribution).to_dict()["rows"][1]
    retained = build_life_closed_cohort_balance(without_distribution).to_dict()["rows"][1]
    assert distributed["period_profit"] == retained["period_profit"]
    assert distributed["closing_guarantee_liability"] == retained["closing_guarantee_liability"]
    assert Decimal(retained["closing_backing_assets"]) - Decimal(distributed["closing_backing_assets"]) == 5
    assert Decimal(retained["closing_equity"]) - Decimal(distributed["closing_equity"]) == 5


def test_zero_death_and_zero_capital_preserve_pr159_rows_and_prefix() -> None:
    old = json.loads(V2_FIXTURE.read_text(encoding="utf-8"))
    scenario = _input()
    scenario["opening"] = old["opening"]
    scenario["guaranteed_rate_per_period"] = old["guaranteed_rate_per_period"]
    scenario["periods"] = [
        {
            "period": row["period"],
            "renewal_premiums_collected": row["premiums_collected"],
            "renewal_liability_allocation": row["premium_liability_allocation"],
            "investment_result": row["investment_result"],
            "deaths": 0,
            "death_benefits_paid": "0",
            "operating_expense_paid": row["operating_expense_paid"],
            "capital_contribution": "0",
            "capital_distribution": "0",
        }
        for row in old["periods"]
    ]
    full = build_life_closed_cohort_balance(scenario).to_dict()
    old_rows = build_life_model_balance(old).to_dict()["rows"]
    assert full["valid"] is True
    for new, previous in zip(full["rows"], old_rows):
        assert {key: new[key] for key in previous} == previous
        assert new["death_liability_release"] == "0.0000"
    scenario["periods"] = scenario["periods"][:1]
    assert build_life_closed_cohort_balance(scenario).to_dict()["rows"] == full["rows"][:1]


def test_death_precedes_maturity_and_full_exit_releases_everything() -> None:
    scenario = _input()
    scenario["opening"]["opening_remaining_periods"] = 1
    scenario["periods"] = [scenario["periods"][0]]
    row = build_life_closed_cohort_balance(scenario).to_dict()["rows"][0]
    assert (row["deaths"], row["maturities"], row["death_liability_release"],
            row["maturity_liability_release"], row["closing_guarantee_liability"]) == (
        2, 8, "22.8000", "91.2000", "0.0000"
    )

    scenario["opening"]["opening_remaining_periods"] = 2
    scenario["periods"][0]["deaths"] = 10
    scenario["periods"][0]["death_benefits_paid"] = "114"
    row = build_life_closed_cohort_balance(scenario).to_dict()["rows"][0]
    assert row["maturities"] == 0
    assert row["death_liability_release"] == "114.0000"
    assert row["closing_active_policies"] == 0
    assert row["closing_remaining_periods"] == 0
    assert row["closing_guarantee_liability"] == "0.0000"
    scenario["periods"].append({**scenario["periods"][0], "period": 2, "deaths": 0, "death_benefits_paid": "0"})
    assert "cohort_extinguished" in _issue_codes(build_life_closed_cohort_balance(scenario).to_dict())


def test_half_even_death_release_and_callers_decimal_precision() -> None:
    scenario = _input()
    scenario["opening"] = {
        "opening_active_policies": 2,
        "opening_remaining_periods": 2,
        "opening_backing_assets": "0.0001",
        "opening_guarantee_liability": "0.0001",
        "opening_equity": "0",
    }
    scenario["guaranteed_rate_per_period"] = "0"
    scenario["periods"] = [{
        "period": 1,
        "renewal_premiums_collected": "0",
        "renewal_liability_allocation": "0",
        "investment_result": "0",
        "deaths": 1,
        "death_benefits_paid": "0",
        "operating_expense_paid": "0",
        "capital_contribution": "0",
        "capital_distribution": "0",
    }]
    with localcontext() as context:
        context.prec = 3
        row = build_life_closed_cohort_balance(scenario).to_dict()["rows"][0]
    assert row["death_liability_release"] == "0.0000"
    assert row["closing_guarantee_liability"] == "0.0001"

    scenario["opening"].update({
        "opening_backing_assets": "999999999999.9999",
        "opening_guarantee_liability": "0",
        "opening_equity": "999999999999.9999",
    })
    row = build_life_closed_cohort_balance(scenario).to_dict()["rows"][0]
    assert row["death_liability_release"] == "0.0000"
    assert row["closing_backing_assets"] == "999999999999.9999"


def test_hundred_periods_and_prefix_are_stable() -> None:
    scenario = _input()
    scenario["opening"]["opening_remaining_periods"] = 100
    scenario["guaranteed_rate_per_period"] = "0"
    scenario["periods"] = [{
        "period": period,
        "renewal_premiums_collected": "0",
        "renewal_liability_allocation": "0",
        "investment_result": "0",
        "deaths": 0,
        "death_benefits_paid": "0",
        "operating_expense_paid": "0",
        "capital_contribution": "0",
        "capital_distribution": "0",
    } for period in range(1, 101)]
    prefix = copy.deepcopy(scenario)
    prefix["periods"] = prefix["periods"][:2]
    full = build_life_closed_cohort_balance(scenario).to_dict()
    assert full["valid"] is True
    assert full["rows"][:2] == build_life_closed_cohort_balance(prefix).to_dict()["rows"]
    assert full["rows"][-1]["maturities"] == 10
    assert full["rows"][-1]["closing_active_policies"] == 0


@pytest.mark.parametrize(("path", "value", "code"), [
    (("schema_version",), "ims.life-closed-cohort-input.v0", "contract_value_mismatch"),
    (("life_sector_contract_schema_version",), "ims.life-sector-contract.v2", "contract_value_mismatch"),
    (("insurer_id",), True, "insurer_id_invalid"),
    (("opening", "opening_active_policies"), 0, "count_invalid"),
    (("opening", "opening_equity"), "19", "opening_identity_invalid"),
    (("guaranteed_rate_per_period",), 0.05, "rate_invalid"),
    (("periods", 0, "deaths"), True, "death_count_invalid"),
    (("periods", 0, "deaths"), 11, "deaths_exceed_opening"),
    (("periods", 0, "deaths"), -1, "death_count_invalid"),
    (("periods", 0, "death_benefits_paid"), -1, "decimal_string_required"),
    (("periods", 0, "death_benefits_paid"), "-1", "negative_amount"),
    (("periods", 0, "renewal_liability_allocation"), "11", "premium_allocation_exceeds_collected"),
    (("periods", 0, "capital_contribution"), 1, "decimal_string_required"),
    (("periods", 0, "capital_distribution"), "-1", "negative_amount"),
    (("periods", 0, "period"), 2, "period_sequence_invalid"),
    (("periods", 2, "capital_distribution"), "100", "negative_closing_assets"),
])
def test_invalid_inputs_never_return_partial_rows(path: tuple, value: object, code: str) -> None:
    scenario = _input()
    target = scenario
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = value
    assert code in _issue_codes(build_life_closed_cohort_balance(scenario).to_dict())


def test_missing_fields_phantom_benefit_and_extra_term_are_rejected() -> None:
    scenario = _input()
    del scenario["periods"][1]["capital_contribution"]
    assert "field_missing" in _issue_codes(build_life_closed_cohort_balance(scenario).to_dict())

    scenario = _input()
    scenario["periods"][2]["death_benefits_paid"] = "1"
    assert "death_benefit_without_death" in _issue_codes(build_life_closed_cohort_balance(scenario).to_dict())

    scenario = _input()
    scenario["opening"]["opening_remaining_periods"] = 2
    assert "periods_exceed_remaining_term" in _issue_codes(build_life_closed_cohort_balance(scenario).to_dict())

    scenario = _input()
    scenario["periods"][1]["deaths"] = 9
    assert "deaths_exceed_opening" in _issue_codes(build_life_closed_cohort_balance(scenario).to_dict())

    scenario = _input()
    scenario["periods"][0]["new_business_policies"] = 1
    assert "field_unknown" in _issue_codes(build_life_closed_cohort_balance(scenario).to_dict())
