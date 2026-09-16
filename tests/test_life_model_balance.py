import copy
import json
from decimal import Decimal, localcontext
from pathlib import Path

import pytest

from ims.accounting.life_model_balance import (
    LIFE_BALANCE_RESULT_VERSION,
    build_life_model_balance,
)
from ims.model.life_sector_contract import LIFE_FIELDS, LIFE_SECTOR_CONTRACT_VERSION


FIXTURE = Path(__file__).parent / "fixtures" / "life_model_balance_v1.json"


def _input() -> dict:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def test_two_period_case_credits_opening_liability_then_matures_at_book_value() -> None:
    scenario = _input()
    before = copy.deepcopy(scenario)

    result = build_life_model_balance(scenario).to_dict()

    assert result["schema_version"] == LIFE_BALANCE_RESULT_VERSION
    assert result["life_sector_contract_schema_version"] == LIFE_SECTOR_CONTRACT_VERSION
    assert result["valid"] is True
    assert result["calculated_period_count"] == 2
    assert result["source_kind"] == "explicit_scenario"
    assert result["historical_mapping_status"] == "unresolved"
    assert all(result[key] is False for key in (
        "writes_performed", "runner_invoked", "simulation_performed",
        "statutory_or_solvency_ii_claim", "historical_full_equality_claim",
    ))
    assert scenario == before
    assert result == build_life_model_balance(scenario).to_dict()
    assert json.loads(json.dumps(result)) == result

    first, second = result["rows"]
    assert set(first) == {"period", *(field.field_id for field in LIFE_FIELDS)}
    assert first["guaranteed_rate_per_period"] == second["guaranteed_rate_per_period"] == "0.050000"
    assert (first["guarantee_accretion"], first["closing_guarantee_liability"],
            first["closing_backing_assets"], first["closing_equity"]) == (
        "5.0000", "114.0000", "136.0000", "22.0000"
    )
    assert first["maturities"] == 0
    assert first["liability_release"] == "0.0000"
    assert (second["guarantee_accretion"], second["maturities"],
            second["maturity_benefits_paid"], second["liability_release"]) == (
        "5.7000", 10, "128.7000", "128.7000"
    )
    assert (second["closing_active_policies"], second["closing_remaining_periods"],
            second["closing_guarantee_liability"], second["closing_backing_assets"],
            second["closing_equity"], second["period_profit"]) == (
        0, 0, "0.0000", "22.3000", "22.3000", "0.3000"
    )
    for name in ("active_policies", "remaining_periods", "backing_assets", "guarantee_liability", "equity"):
        assert second[f"opening_{name}"] == first[f"closing_{name}"]
    for row in (first, second):
        assert Decimal(row["opening_backing_assets"]) == (
            Decimal(row["opening_guarantee_liability"]) + Decimal(row["opening_equity"])
        )
        assert Decimal(row["closing_backing_assets"]) == (
            Decimal(row["closing_guarantee_liability"]) + Decimal(row["closing_equity"])
        )
        assert row["deaths"] == row["surrenders"] == 0
        assert row["bonus_accretion"] == row["capital_contribution"] == "0.0000"


def test_prefix_and_explicit_half_even_credit_are_stable() -> None:
    scenario = _input()
    full = build_life_model_balance(scenario).to_dict()
    scenario["periods"] = scenario["periods"][:1]
    assert build_life_model_balance(scenario).to_dict()["rows"] == full["rows"][:1]

    scenario["opening"] = {
        "opening_active_policies": 1,
        "opening_remaining_periods": 2,
        "opening_backing_assets": "0.0001",
        "opening_guarantee_liability": "0.0001",
        "opening_equity": "0",
    }
    scenario["guaranteed_rate_per_period"] = "0.5"
    scenario["periods"][0].update({
        "premiums_collected": "0", "premium_liability_allocation": "0",
        "investment_result": "0", "operating_expense_paid": "0",
    })
    first = build_life_model_balance(scenario).to_dict()["rows"][0]
    assert first["guarantee_accretion"] == "0.0000"
    assert first["closing_guarantee_liability"] == "0.0001"

    scenario["opening"].update({
        "opening_backing_assets": "0.0003",
        "opening_guarantee_liability": "0.0003",
    })
    scenario["periods"][0]["investment_result"] = "0.0002"
    second = build_life_model_balance(scenario).to_dict()["rows"][0]
    assert second["guarantee_accretion"] == "0.0002"
    assert second["closing_guarantee_liability"] == "0.0005"


def test_large_amounts_ignore_callers_decimal_precision() -> None:
    scenario = _input()
    scenario["opening"].update({
        "opening_backing_assets": "999999999999.9999",
        "opening_guarantee_liability": "0",
        "opening_equity": "999999999999.9999",
    })
    scenario["periods"] = [scenario["periods"][0]]
    with localcontext() as context:
        context.prec = 3
        result = build_life_model_balance(scenario).to_dict()
    assert result["valid"] is True
    assert result["rows"][0]["closing_backing_assets"] == "1000000000015.9999"


def test_hundred_periods_close_the_cohort_without_changing_prefix() -> None:
    scenario = _input()
    scenario["opening"]["opening_remaining_periods"] = 100
    scenario["guaranteed_rate_per_period"] = "0"
    scenario["periods"] = [{
        "period": period,
        "premiums_collected": "0",
        "premium_liability_allocation": "0",
        "investment_result": "0",
        "operating_expense_paid": "0",
    } for period in range(1, 101)]
    prefix_scenario = copy.deepcopy(scenario)
    prefix_scenario["periods"] = prefix_scenario["periods"][:2]

    full = build_life_model_balance(scenario).to_dict()
    prefix = build_life_model_balance(prefix_scenario).to_dict()

    assert full["valid"] is True
    assert full["calculated_period_count"] == 100
    assert full["rows"][:2] == prefix["rows"]
    assert full["rows"][-1]["maturity_benefits_paid"] == "100.0000"
    assert full["rows"][-1]["closing_active_policies"] == 0
    assert full["rows"][-1]["closing_equity"] == "20.0000"


@pytest.mark.parametrize(("path", "value", "code"), [
    (("schema_version",), "ims.life-model-balance-input.v0", "contract_value_mismatch"),
    (("life_sector_contract_schema_version",), "ims.life-sector-contract.v1", "contract_value_mismatch"),
    (("source_kind",), "legacy", "contract_value_mismatch"),
    (("sector_id",), "motor", "contract_value_mismatch"),
    (("insurer_id",), True, "insurer_id_invalid"),
    (("insurer_id",), 26, "insurer_id_invalid"),
    (("opening", "opening_active_policies"), 0, "count_invalid"),
    (("opening", "opening_remaining_periods"), 101, "count_invalid"),
    (("opening", "opening_equity"), "19", "opening_identity_invalid"),
    (("opening", "opening_backing_assets"), "-1", "negative_amount"),
    (("guaranteed_rate_per_period",), 0.05, "rate_invalid"),
    (("guaranteed_rate_per_period",), "1.000001", "rate_invalid"),
    (("periods", 0, "premiums_collected"), "1e2", "decimal_string_required"),
    (("periods", 0, "premiums_collected"), "0.00001", "decimal_string_required"),
    (("periods", 0, "premium_liability_allocation"), "11", "premium_allocation_exceeds_collected"),
    (("periods", 0, "period"), 2, "period_sequence_invalid"),
    (("periods", 1, "investment_result"), "-1000", "negative_closing_assets"),
])
def test_invalid_input_never_returns_partial_rows(path: tuple, value: object, code: str) -> None:
    scenario = _input()
    target = scenario
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = value
    result = build_life_model_balance(scenario).to_dict()
    assert result["valid"] is False
    assert result["rows"] == []
    assert result["calculated_period_count"] == 0
    assert code in {item["code"] for item in result["issues"]}


def test_extra_period_and_undeclared_strategies_are_rejected() -> None:
    scenario = _input()
    scenario["opening"]["opening_remaining_periods"] = 1
    assert "periods_exceed_remaining_term" in {
        issue["code"] for issue in build_life_model_balance(scenario).to_dict()["issues"]
    }

    scenario = _input()
    scenario["periods"][0]["bonus_accretion"] = "1"
    scenario["periods"][0]["surrenders"] = 1
    assert {issue["code"] for issue in build_life_model_balance(scenario).to_dict()["issues"]} == {"field_unknown"}
