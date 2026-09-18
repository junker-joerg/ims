import copy
import json
from decimal import Decimal, localcontext
from pathlib import Path

import pytest

from ims.accounting.four_sector_balance import (
    FOUR_SECTOR_BALANCE_INPUT_VERSION,
    FOUR_SECTOR_BALANCE_RESULT_VERSION,
    SECTOR_IDS,
    build_four_sector_balance,
)
from tests.test_health_period_chain import _horizon as health_horizon


FIXTURES = Path(__file__).parent / "fixtures"
AMOUNTS = (
    "opening_assets", "opening_liabilities", "opening_equity", "period_profit",
    "capital_contribution", "capital_distribution", "closing_assets",
    "closing_liabilities", "closing_equity",
)


def _fixture(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def _input() -> dict:
    motor = _fixture("non_life_model_balance_v1.json")
    property_liability = copy.deepcopy(motor)
    property_liability["sector_id"] = "property_liability"
    return {
        "schema_version": FOUR_SECTOR_BALANCE_INPUT_VERSION,
        "insurer_id": 1,
        "scenario_id": "seminar_health_01",
        "variant_id": "baseline",
        "sectors": {
            "motor": motor,
            "property_liability": property_liability,
            "life": _fixture("life_period_chain_v1.json"),
            "health": _fixture("health_period_chain_v1.json"),
        },
    }


def _hundred() -> dict:
    value = _input()
    for sector_id in ("motor", "property_liability"):
        sector = value["sectors"][sector_id]
        empty = {name: "0" for name in sector["periods"][0] if name != "period"}
        sector["periods"].extend({"period": period, **empty} for period in range(3, 101))
    life = value["sectors"]["life"]
    life["opening"] = {
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
    life["assumptions"]["period_count"] = 100
    life["assumptions"]["investment"] = {
        "mode": "insurer_rule_on_opening_backing_assets",
        "windows": [{"start_period": 1, "end_period": 100, "rate_per_period": "0"}],
    }
    life["assumptions"]["mortality"] = {
        "mode": "explicit_death_policy_ids",
        "periods": [{"period": period, "death_policy_ids": []} for period in range(1, 101)],
    }
    life["periods"] = [{
        "period": period,
        "policy_flows": [{
            "policy_id": "A1", "renewal_premiums_collected": "0",
            "renewal_liability_allocation": "0", "death_benefit_if_death": "0",
            "maturity_benefit_if_due": "100" if period == 100 else "0",
        }],
        "new_business": [], "operating_expense_paid": "0",
        "capital_contribution": "0", "capital_distribution": "0",
    } for period in range(1, 101)]
    value["sectors"]["health"] = health_horizon(100)
    return value


def test_four_sector_totals_and_provenance_are_exact_and_repeatable() -> None:
    value = _input()
    before = copy.deepcopy(value)
    result = build_four_sector_balance(value).to_dict()
    assert value == before
    assert result == build_four_sector_balance(value).to_dict()
    assert result["schema_version"] == FOUR_SECTOR_BALANCE_RESULT_VERSION
    assert result["valid"] is True
    assert result["period_count"] == 2
    assert [item["sector_id"] for item in result["sectors"]] == list(SECTOR_IDS)
    assert len(result["input_digest"]) == len(result["content_digest"]) == 64
    assert result["total_rows"][0] == {
        "period": 1,
        "opening_assets": "450.0000", "opening_liabilities": "200.0000",
        "opening_equity": "250.0000", "period_profit": "32.0000",
        "capital_contribution": "33.0000", "capital_distribution": "5.0000",
        "closing_assets": "453.0000", "closing_liabilities": "143.0000",
        "closing_equity": "310.0000",
    }
    for index, total in enumerate(result["total_rows"]):
        for field in AMOUNTS:
            assert Decimal(total[field]) == sum(
                Decimal(sector["rows"][index][field]) for sector in result["sectors"]
            )
        for prefix in ("opening", "closing"):
            assert Decimal(total[f"{prefix}_assets"]) == (
                Decimal(total[f"{prefix}_liabilities"]) + Decimal(total[f"{prefix}_equity"])
            )
    assert result["total_rows"][1]["opening_assets"] == result["total_rows"][0]["closing_assets"]
    assert result["writes_performed"] is False
    assert result["runner_invoked"] is False
    assert result["statutory_or_solvency_ii_claim"] is False
    assert result["historical_full_equality_claim"] is False


@pytest.mark.parametrize(("mutation", "code"), [
    (lambda value: value["sectors"].pop("health"), "sector_set_invalid"),
    (lambda value: value["sectors"]["life"].update({"insurer_id": 2}), "insurer_mismatch"),
    (lambda value: value["sectors"]["property_liability"].update({"sector_id": "motor"}), "sector_mismatch"),
    (lambda value: value["sectors"]["property_liability"]["periods"].pop(), "period_count_mismatch"),
    (lambda value: value["sectors"]["health"]["sources"].update({"variant_id": "shock"}), "scenario_mismatch"),
    (lambda value: value["sectors"]["health"]["periods"][1].update({"benefits_paid": "999"}), "benefits_exceed_liability"),
    (lambda value: value["sectors"]["motor"]["opening"].update({"opening_cash": "99"}), "opening_identity_invalid"),
])
def test_bad_input_never_returns_partial_allocations(mutation, code: str) -> None:
    value = _input()
    mutation(value)
    result = build_four_sector_balance(value).to_dict()
    assert result["valid"] is False
    assert result["period_count"] == 0
    assert result["input_digest"] is None
    assert result["content_digest"] is None
    assert result["sectors"] == result["total_rows"] == []
    assert code in {item["code"] for item in result["issues"]}


def test_large_horizon_has_exact_prefix_and_stable_precision() -> None:
    value = _hundred()
    with localcontext() as context:
        context.prec = 3
        full = build_four_sector_balance(value).to_dict()
    assert full["valid"] is True, full["issues"]
    assert full["period_count"] == 100
    short = copy.deepcopy(value)
    for sector_id in ("motor", "property_liability", "life", "health"):
        short["sectors"][sector_id]["periods"] = short["sectors"][sector_id]["periods"][:2]
    life = short["sectors"]["life"]
    life["assumptions"]["period_count"] = 2
    life["assumptions"]["mortality"]["periods"] = life["assumptions"]["mortality"]["periods"][:2]
    life["assumptions"]["investment"]["windows"][0]["end_period"] = 2
    health = short["sectors"]["health"]
    health["sources"]["period_count"] = 2
    for name in ("new_business", "exits"):
        health["sources"][name]["periods"] = health["sources"][name]["periods"][:2]
    for name in ("pricing", "benefits"):
        health["sources"][name]["windows"] = health["sources"][name]["windows"][:2]
    prefix = build_four_sector_balance(short).to_dict()
    assert prefix["valid"] is True, prefix["issues"]
    assert full["total_rows"][:2] == prefix["total_rows"]
    assert all(
        full["sectors"][index]["rows"][:2] == prefix["sectors"][index]["rows"]
        for index in range(4)
    )
