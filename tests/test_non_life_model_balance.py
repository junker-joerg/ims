import copy
import json
from pathlib import Path
from decimal import Decimal, localcontext

import pytest

from ims.accounting.model_balance_contract import BALANCE_FIELDS
from ims.accounting.non_life_model_balance import (
    MODEL_BALANCE_RESULT_VERSION,
    build_non_life_model_balance,
)


FIXTURE = Path(__file__).parent / "fixtures" / "non_life_model_balance_v1.json"


def _input() -> dict:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


@pytest.mark.parametrize("sector_id", ["motor", "property_liability"])
def test_two_period_balance_is_exact_and_carries_stocks_by_named_sector(sector_id: str) -> None:
    scenario = _input()
    scenario["sector_id"] = sector_id
    before = copy.deepcopy(scenario)

    result = build_non_life_model_balance(scenario).to_dict()

    assert result["schema_version"] == MODEL_BALANCE_RESULT_VERSION
    assert result["valid"] is True
    assert result["sector_id"] == sector_id
    assert result["calculated_period_count"] == 2
    assert result["source_kind"] == "explicit_scenario"
    assert result["historical_mapping_status"] == "unresolved"
    assert result["writes_performed"] is False
    assert result["runner_invoked"] is False
    assert result["simulation_performed"] is False
    assert result["historical_full_equality_claim"] is False
    assert scenario == before
    assert result == build_non_life_model_balance(scenario).to_dict()
    assert json.loads(json.dumps(result)) == result

    first, second = result["rows"]
    assert set(first) == {"period", *(field.field_id for field in BALANCE_FIELDS)}
    assert (first["period_profit"], first["closing_cash"], first["closing_claim_liability"], first["closing_equity"]) == (
        "11.0000", "117.0000", "33.0000", "84.0000"
    )
    assert (second["period_profit"], second["closing_cash"], second["closing_claim_liability"], second["closing_equity"]) == (
        "3.0000", "116.0000", "29.0000", "87.0000"
    )
    for opening, closing in (
        ("opening_cash", "closing_cash"),
        ("opening_claim_liability", "closing_claim_liability"),
        ("opening_equity", "closing_equity"),
    ):
        assert second[opening] == first[closing]


def test_prefix_and_small_decimal_addition_are_stable() -> None:
    scenario = _input()
    full = build_non_life_model_balance(scenario).to_dict()
    scenario["periods"] = scenario["periods"][:1]
    prefix = build_non_life_model_balance(scenario).to_dict()
    assert prefix["rows"] == full["rows"][:1]

    scenario["opening"] = {
        "opening_cash": "0.1", "opening_claim_liability": "0", "opening_equity": "0.1"
    }
    scenario["periods"][0].update({
        "premium_income": "0.2", "investment_income": "0", "claims_incurred": "0",
        "claims_paid": "0", "operating_expense": "0", "capital_contribution": "0",
        "capital_distribution": "0",
    })
    assert build_non_life_model_balance(scenario).to_dict()["rows"][0]["closing_cash"] == "0.3000"


def test_hundred_periods_preserve_the_two_period_prefix() -> None:
    scenario = _input()
    prefix = build_non_life_model_balance(scenario).to_dict()["rows"]
    empty_flow = {name: "0" for name in (
        "premium_income", "investment_income", "claims_incurred", "claims_paid",
        "operating_expense", "capital_contribution", "capital_distribution",
    )}
    scenario["periods"].extend(
        {"period": period, **empty_flow} for period in range(3, 101)
    )

    result = build_non_life_model_balance(scenario).to_dict()

    assert result["valid"] is True
    assert result["calculated_period_count"] == 100
    assert result["rows"][:2] == prefix
    assert result["rows"][-1]["closing_cash"] == "116.0000"
    for row in result["rows"]:
        assert Decimal(row["opening_cash"]) == (
            Decimal(row["opening_claim_liability"]) + Decimal(row["opening_equity"])
        )
        assert Decimal(row["closing_cash"]) == (
            Decimal(row["closing_claim_liability"]) + Decimal(row["closing_equity"])
        )


def test_large_amounts_do_not_inherit_callers_decimal_precision() -> None:
    scenario = _input()
    scenario["opening"] = {
        "opening_cash": "999999999999.9999",
        "opening_claim_liability": "0",
        "opening_equity": "999999999999.9999",
    }
    scenario["periods"] = [{
        "period": 1,
        "premium_income": "0.0001",
        "investment_income": "0",
        "claims_incurred": "0",
        "claims_paid": "0",
        "operating_expense": "0",
        "capital_contribution": "0",
        "capital_distribution": "0",
    }]

    with localcontext() as context:
        context.prec = 3
        result = build_non_life_model_balance(scenario).to_dict()

    assert result["valid"] is True
    assert result["rows"][0]["closing_cash"] == "1000000000000.0000"
    assert result["rows"][0]["closing_equity"] == "1000000000000.0000"


@pytest.mark.parametrize(
    ("path", "value", "code"),
    [
        (("schema_version",), "ims.insurer-model-balance-input.v0", "contract_value_mismatch"),
        (("source_kind",), "historical_reserve", "contract_value_mismatch"),
        (("historical_mapping_status",), "mapped", "contract_value_mismatch"),
        (("insurer_id",), True, "insurer_id_invalid"),
        (("insurer_id",), 26, "insurer_id_invalid"),
        (("sector_id",), "life", "sector_id_invalid"),
        (("sector_id",), "legacy.damage_1", "sector_id_invalid"),
        (("opening", "opening_equity"), "71.00", "opening_identity_invalid"),
        (("opening", "opening_cash"), "-1", "negative_amount"),
        (("periods", 0, "premium_income"), 20.0, "decimal_string_required"),
        (("periods", 0, "premium_income"), "1e2", "decimal_string_required"),
        (("periods", 0, "premium_income"), "0.00001", "decimal_string_required"),
        (("periods", 0, "premium_income"), "-1", "negative_amount"),
        (("periods", 0, "period"), 2, "period_sequence_invalid"),
        (("periods", 1, "period"), 3, "period_sequence_invalid"),
        (("periods", 1, "claims_paid"), "50.00", "negative_closing_claim_liability"),
        (("periods", 1, "capital_distribution"), "200.00", "negative_closing_cash"),
    ],
)
def test_invalid_input_never_returns_a_partial_balance(path: tuple, value: object, code: str) -> None:
    scenario = _input()
    target = scenario
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = value

    result = build_non_life_model_balance(scenario).to_dict()

    assert result["valid"] is False
    assert result["calculated_period_count"] == 0
    assert result["rows"] == []
    assert code in {issue["code"] for issue in result["issues"]}


def test_unknown_fields_and_unbounded_horizon_are_rejected() -> None:
    scenario = _input()
    scenario["opening"]["legacy_reserve"] = "1000"
    scenario["periods"][0]["advertising_current"] = "5"
    result = build_non_life_model_balance(scenario).to_dict()
    assert result["valid"] is False
    assert [issue["code"] for issue in result["issues"]].count("field_unknown") == 2
    assert result["rows"] == []

    scenario = _input()
    scenario["periods"] = []
    assert "period_count_invalid" in {
        issue["code"] for issue in build_non_life_model_balance(scenario).to_dict()["issues"]
    }
    scenario["periods"] = [{} for _ in range(101)]
    assert "period_count_invalid" in {
        issue["code"] for issue in build_non_life_model_balance(scenario).to_dict()["issues"]
    }
