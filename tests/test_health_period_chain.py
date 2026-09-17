import copy
import json
from decimal import Decimal
from pathlib import Path
from time import perf_counter

import pytest

from ims.accounting.health_model_balance import build_health_model_balance
from ims.accounting.health_period_chain import (
    HEALTH_PERIOD_CHAIN_HORIZONS,
    HEALTH_PERIOD_CHAIN_RESULT_VERSION,
    run_health_period_chain,
)


FIXTURE = Path(__file__).parent / "fixtures" / "health_period_chain_v1.json"
OLD_FIXTURE = Path(__file__).parent / "fixtures" / "health_model_balance_v1.json"


def _input() -> dict:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def _horizon(count: int) -> dict:
    value = _input()
    value["sources"]["period_count"] = count
    for name in ("new_business", "exits"):
        value["sources"][name]["periods"] = (
            value["sources"][name]["periods"][:count]
            + [{"period": period, "count": 0} for period in range(3, count + 1)]
        )
    for name in ("pricing", "benefits"):
        windows = value["sources"][name]["windows"][:count]
        if count > 2:
            windows.append({
                "start_period": 3, "end_period": count,
                "amount_per_opening_policy": windows[1]["amount_per_opening_policy"],
            })
        value["sources"][name]["windows"] = windows
    value["periods"] = value["periods"][:count] + [
        {
            "period": period,
            "benefits_paid": "9.00",
            "investment_result": "0.00",
            "operating_expense_paid": "0.00",
            "capital_contribution": "0.00",
            "capital_distribution": "0.00",
        }
        for period in range(3, count + 1)
    ]
    return value


def _errors(value: object, *, should_cancel=None) -> set[str]:
    result = run_health_period_chain(value, should_cancel=should_cancel).to_dict()
    assert result["valid"] is False
    assert result["calculated_period_count"] == 0
    assert result["rows"] == []
    return {issue["code"] for issue in result["issues"]}


def test_two_period_stock_and_balance_carryover_are_exact() -> None:
    scenario = _input()
    before = copy.deepcopy(scenario)
    result = run_health_period_chain(scenario).to_dict()

    assert scenario == before
    assert result == run_health_period_chain(scenario).to_dict()
    assert result["schema_version"] == HEALTH_PERIOD_CHAIN_RESULT_VERSION
    assert result["valid"] is True
    assert result["scenario_id"] == "seminar_health_01"
    assert result["variant_id"] == "baseline"
    assert result["calculated_period_count"] == 2
    assert result["writes_performed"] is False
    assert result["app_runner_invoked"] is False
    assert result["health_period_chain_calculated"] is True
    assert result["historical_full_equality_claim"] is False

    first, second = result["rows"]
    assert (first["opening_active_policies"], first["exits"], first["new_business_policies"], first["closing_active_policies"]) == (10, 1, 2, 11)
    assert (second["opening_active_policies"], second["exits"], second["closing_active_policies"]) == (11, 2, 9)
    assert (first["premiums_collected"], first["benefits_incurred"]) == ("30.0000", "18.0000")
    assert (second["premiums_collected"], second["benefits_incurred"]) == ("27.5000", "11.0000")
    assert (first["closing_cash"], first["closing_benefit_liability"], first["closing_equity"]) == ("115.0000", "23.0000", "92.0000")
    assert (second["closing_cash"], second["closing_benefit_liability"], second["closing_equity"]) == ("116.5000", "14.0000", "102.5000")
    for stock in ("active_policies", "cash", "benefit_liability", "equity"):
        assert second[f"opening_{stock}"] == first[f"closing_{stock}"]
    for row in result["rows"]:
        assert Decimal(row["closing_cash"]) == Decimal(row["closing_benefit_liability"]) + Decimal(row["closing_equity"])
        assert row["closing_active_policies"] == row["opening_active_policies"] - row["exits"] + row["new_business_policies"]


def test_closed_two_period_case_matches_pr169_financial_rows() -> None:
    scenario = _input()
    for name in ("new_business", "exits"):
        for entry in scenario["sources"][name]["periods"]:
            entry["count"] = 0
    result = run_health_period_chain(scenario).to_dict()
    old = build_health_model_balance(json.loads(OLD_FIXTURE.read_text(encoding="utf-8"))).to_dict()
    assert result["valid"] is True
    for current, previous in zip(result["rows"], old["rows"], strict=True):
        for field, value in previous.items():
            assert current[field] == value


def test_all_approved_horizons_have_the_exact_100_period_prefix() -> None:
    started = perf_counter()
    full = run_health_period_chain(_horizon(100)).to_dict()
    assert full["valid"] is True
    assert len(full["rows"]) == 100
    assert len(json.dumps(full["rows"], sort_keys=True).encode("utf-8")) < 1_000_000
    for count in sorted(HEALTH_PERIOD_CHAIN_HORIZONS):
        short = run_health_period_chain(_horizon(count)).to_dict()
        assert short["valid"] is True
        assert short["rows"] == full["rows"][:count]
    assert perf_counter() - started < 10


@pytest.mark.parametrize(
    ("path", "value", "code"),
    [
        (("schema_version",), "ims.health-period-chain-input.v0", "contract_value_mismatch"),
        (("insurer_id",), True, "insurer_id_invalid"),
        (("sources", "schema_version"), "ims.health-period-sources-input.v0", "contract_value_mismatch"),
        (("sources", "insurer_id"), 2, "source_insurer_mismatch"),
        (("sources", "period_count"), 3, "period_coverage_invalid"),
        (("opening", "opening_active_policies"), 9, "source_opening_mismatch"),
        (("opening", "opening_cash"), "99", "opening_identity_invalid"),
        (("periods", 1, "period"), 3, "period_sequence_invalid"),
        (("periods", 1, "benefits_paid"), "100", "benefits_exceed_liability"),
        (("periods", 1, "investment_result"), "-200", "negative_closing_cash"),
        (("sources", "benefits", "actor_type"), "insurer", "actor_mismatch"),
        (("sources", "pricing", "windows", 1, "start_period"), 1, "window_overlap"),
    ],
)
def test_invalid_input_is_atomic(path: tuple, value: object, code: str) -> None:
    scenario = _input()
    target = scenario
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = value
    assert code in _errors(scenario)


def test_unknown_missing_horizon_and_late_error_return_no_rows() -> None:
    scenario = _input()
    scenario["periods"][0]["unknown"] = "0"
    del scenario["periods"][1]["benefits_paid"]
    assert {"field_unknown", "field_missing"} <= _errors(scenario)

    assert "horizon_invalid" in _errors(_horizon(3))

    mismatched = _input()
    mismatched["sources"] = _horizon(1)["sources"]
    assert "source_horizon_mismatch" in _errors(mismatched)

    long_case = _horizon(100)
    long_case["periods"][99]["benefits_paid"] = "999999"
    assert "benefits_exceed_liability" in _errors(long_case)

    overflowing = _input()
    overflowing["opening"]["opening_cash"] = "999999999999.9999"
    overflowing["opening"]["opening_equity"] = "999999999979.9999"
    assert "balance_amount_overflow" in _errors(overflowing)


def test_cancellation_after_some_work_returns_no_partial_rows() -> None:
    calls = 0

    def cancel() -> bool:
        nonlocal calls
        calls += 1
        return calls == 3

    assert "run_cancelled" in _errors(_horizon(100), should_cancel=cancel)
    assert calls == 3


def test_zero_opening_can_gain_business_next_period_without_current_flow() -> None:
    scenario = _input()
    scenario["opening"] = {
        "opening_active_policies": 0,
        "opening_cash": "100",
        "opening_benefit_liability": "20",
        "opening_equity": "80",
    }
    scenario["sources"]["opening_active_policies"] = 0
    scenario["sources"]["exits"]["periods"] = [
        {"period": 1, "count": 0}, {"period": 2, "count": 0},
    ]
    scenario["periods"][0]["benefits_paid"] = "0"
    scenario["periods"][1]["benefits_paid"] = "0"
    result = run_health_period_chain(scenario).to_dict()
    assert result["valid"] is True
    assert result["rows"][0]["premiums_collected"] == "0.0000"
    assert result["rows"][0]["benefits_incurred"] == "0.0000"
    assert result["rows"][1]["premiums_collected"] == "5.0000"
