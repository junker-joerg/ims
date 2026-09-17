import copy
import json
from decimal import Decimal, localcontext
from pathlib import Path

import pytest

from ims.accounting.health_model_balance import (
    HEALTH_BALANCE_RESULT_VERSION,
    build_health_model_balance,
)
from ims.model.health_sector_contract import HEALTH_FIELDS, HEALTH_SECTOR_CONTRACT_VERSION


FIXTURE = Path(__file__).parent / "fixtures" / "health_model_balance_v1.json"


def _input() -> dict:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def test_two_period_closed_health_balance_is_exact_and_keeps_prefix() -> None:
    scenario = _input()
    before = copy.deepcopy(scenario)
    result = build_health_model_balance(scenario).to_dict()

    assert result["schema_version"] == HEALTH_BALANCE_RESULT_VERSION
    assert result["health_sector_contract_schema_version"] == HEALTH_SECTOR_CONTRACT_VERSION
    assert result["valid"] is True
    assert result["calculated_period_count"] == 2
    assert result["sector_id"] == "health"
    assert result["source_kind"] == "explicit_scenario"
    assert result["historical_mapping_status"] == "unresolved"
    assert scenario == before
    assert result == json.loads(json.dumps(result)) == build_health_model_balance(scenario).to_dict()
    for key in (
        "writes_performed", "runner_invoked", "simulation_performed",
        "statutory_or_solvency_ii_claim", "historical_full_equality_claim",
    ):
        assert result[key] is False

    first, second = result["rows"]
    assert set(first) == {"period", *(field.field_id for field in HEALTH_FIELDS)}
    assert (
        first["period_profit"], first["closing_cash"],
        first["closing_benefit_liability"], first["closing_equity"],
    ) == ("10.0000", "115.0000", "23.0000", "92.0000")
    assert (
        second["period_profit"], second["closing_cash"],
        second["closing_benefit_liability"], second["closing_equity"],
    ) == ("11.0000", "114.0000", "13.0000", "101.0000")
    for name in ("active_policies", "cash", "benefit_liability", "equity"):
        assert second[f"opening_{name}"] == first[f"closing_{name}"]
    assert first["closing_active_policies"] == second["closing_active_policies"] == 10

    scenario["periods"] = scenario["periods"][:1]
    assert build_health_model_balance(scenario).to_dict()["rows"] == result["rows"][:1]


def test_no_active_policies_can_pay_an_old_benefit_but_not_create_new_flow() -> None:
    scenario = _input()
    scenario["opening"]["opening_active_policies"] = 0
    scenario["periods"] = [dict(scenario["periods"][0])]
    scenario["periods"][0].update({
        "premiums_collected": "0", "benefits_incurred": "0",
        "benefits_paid": "5", "investment_result": "0",
        "operating_expense_paid": "0", "capital_contribution": "0",
        "capital_distribution": "0",
    })
    result = build_health_model_balance(scenario).to_dict()
    assert result["valid"] is True
    assert result["rows"][0]["closing_benefit_liability"] == "15.0000"
    assert result["rows"][0]["closing_active_policies"] == 0

    scenario["periods"][0]["benefits_incurred"] = "1"
    invalid = build_health_model_balance(scenario).to_dict()
    assert invalid["rows"] == []
    assert "flow_without_active_policies" in {issue["code"] for issue in invalid["issues"]}


def test_exact_decimal_addition_is_independent_of_callers_precision() -> None:
    scenario = _input()
    scenario["opening"] = {
        "opening_active_policies": 1,
        "opening_cash": "999999999999.9999",
        "opening_benefit_liability": "0",
        "opening_equity": "999999999999.9999",
    }
    scenario["periods"] = [dict(scenario["periods"][0])]
    scenario["periods"][0].update({
        "premiums_collected": "0.0001", "benefits_incurred": "0",
        "benefits_paid": "0", "investment_result": "0",
        "operating_expense_paid": "0", "capital_contribution": "0",
        "capital_distribution": "0",
    })
    with localcontext() as context:
        context.prec = 3
        result = build_health_model_balance(scenario).to_dict()
    assert result["valid"] is True
    assert result["rows"][0]["closing_cash"] == "1000000000000.0000"
    assert result["rows"][0]["closing_equity"] == "1000000000000.0000"
    assert Decimal(result["rows"][0]["closing_cash"]) == Decimal(
        result["rows"][0]["closing_benefit_liability"]
    ) + Decimal(result["rows"][0]["closing_equity"])


@pytest.mark.parametrize(
    ("path", "value", "code"),
    [
        (("schema_version",), "ims.health-model-balance-input.v0", "contract_value_mismatch"),
        (("health_sector_contract_schema_version",), "ims.health-sector-contract.v1", "contract_value_mismatch"),
        (("source_kind",), "legacy", "contract_value_mismatch"),
        (("historical_mapping_status",), "mapped", "contract_value_mismatch"),
        (("sector_id",), "property_liability", "contract_value_mismatch"),
        (("insurer_id",), True, "insurer_id_invalid"),
        (("insurer_id",), 26, "insurer_id_invalid"),
        (("opening", "opening_active_policies"), True, "count_invalid"),
        (("opening", "opening_cash"), "99.00", "opening_identity_invalid"),
        (("opening", "opening_cash"), "-1", "negative_amount"),
        (("periods", 0, "premiums_collected"), 10.0, "decimal_string_required"),
        (("periods", 0, "premiums_collected"), "1e2", "decimal_string_required"),
        (("periods", 0, "premiums_collected"), "0.00001", "decimal_string_required"),
        (("periods", 0, "benefits_incurred"), "-1", "negative_amount"),
        (("periods", 0, "period"), 2, "period_sequence_invalid"),
        (("periods", 1, "period"), 3, "period_sequence_invalid"),
        (("periods", 1, "benefits_paid"), "50", "benefits_exceed_liability"),
        (("periods", 1, "capital_distribution"), "200", "negative_closing_cash"),
    ],
)
def test_invalid_input_never_returns_partial_rows(path: tuple, value: object, code: str) -> None:
    scenario = _input()
    target = scenario
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = value
    result = build_health_model_balance(scenario).to_dict()
    assert result["valid"] is False
    assert result["calculated_period_count"] == 0
    assert result["rows"] == []
    assert code in {issue["code"] for issue in result["issues"]}


def test_unknown_missing_and_unbounded_periods_are_rejected() -> None:
    scenario = _input()
    scenario["opening"]["ageing_reserve"] = "10"
    scenario["periods"][0]["legacy_claim"] = "1"
    del scenario["periods"][1]["benefits_paid"]
    result = build_health_model_balance(scenario).to_dict()
    assert result["valid"] is False
    assert result["rows"] == []
    assert [issue["code"] for issue in result["issues"]].count("field_unknown") == 2
    assert "field_missing" in {issue["code"] for issue in result["issues"]}

    scenario = _input()
    scenario["periods"] = []
    assert "period_count_invalid" in {
        issue["code"] for issue in build_health_model_balance(scenario).to_dict()["issues"]
    }
    scenario["periods"] = [{"period": period} for period in range(1, 4)]
    assert "period_count_invalid" in {
        issue["code"] for issue in build_health_model_balance(scenario).to_dict()["issues"]
    }
