from copy import deepcopy
from decimal import Decimal

import pytest

from ims.strategies.modern_bridge import calculate
from ims.strategies.modern_presets import workshop_case


@pytest.mark.parametrize("case", ["price", "inflation", "capital"])
def test_full_reproducible_modern_case_has_actual_common_prefix_and_balanced_carryover(case):
    source = workshop_case(case)
    before = deepcopy(source)
    result = calculate(source)
    assert result["valid"], result["issues"]
    assert result == calculate(source) and source == before
    for side in ("baseline", "variant"):
        rows = result["sides"][side]["total_rows"]
        for horizon in (2, 5):
            prefix = calculate(workshop_case(case, horizon))
            assert prefix["valid"]
            assert rows[:horizon] == prefix["sides"][side]["total_rows"]
        for index, row in enumerate(rows):
            assert Decimal(row["closing_assets"]) == Decimal(row["closing_liabilities"]) + Decimal(row["closing_equity"])
            if index: assert row["opening_equity"] == rows[index - 1]["closing_equity"]
    assert result["sides"]["baseline"]["total_rows"][:5] == result["sides"]["variant"]["total_rows"][:5]
    assert result["regulatory_metrics"] == {"scr": None, "mcr": None, "coverage_ratio": None}
    assert result["historical_runner_invoked"] is False


def test_price_choice_exposure_and_hundred_balance_are_hand_calculable():
    result = calculate(workshop_case())
    assert result["valid"]
    traces = result["decision_traces"]
    base = next(row for row in traces["baseline"] if row["period"] == 6 and row["sector_id"] == "motor")
    changed = next(row for row in traces["variant"] if row["period"] == 6 and row["sector_id"] == "motor")
    assert base["quoted_price"] == "3.0000" and base["covered_exposure"] == "100.0000" and base["premium_income"] == "300.0000"
    assert changed["quoted_price"] == "3.6000" and changed["covered_exposure"] == "0.0000" and changed["premium_income"] == "0.0000"
    assert changed["advertising_expense"] == "2.0000"
    assert all(group["chosen_insurer_id"] == 2 for group in changed["group_decisions"])
    assert base["model_balance"]["period_profit"] == "245.0000"
    assert changed["model_balance"]["period_profit"] == "-57.0000"
    assert result["sides"]["baseline"]["total_rows"][-1]["closing_equity"] == "116015.7633"
    assert result["sides"]["variant"]["total_rows"][-1]["closing_equity"] == "87325.7633"
    assert Decimal("116015.7633") - Decimal("87325.7633") == Decimal(302) * 95
    assets = Decimal("10000")
    for period in range(1, 101):
        assets += (assets * Decimal("0.0005")).quantize(Decimal("0.0001")) + 200 - (1000 if period == 100 else 0)
    life = next(sector for sector in result["sides"]["baseline"]["sectors"] if sector["sector_id"] == "life")
    assert life["rows"][-1]["closing_assets"] == str(assets)


def test_inclusive_one_period_window_and_group_threshold_are_local():
    source = workshop_case("price", 10)
    changed = next(item for item in source["strategies"]["variant"] if item["period_from"] == 6)
    changed["period_through"] = 6
    vn = next(item for item in source["strategies"]["variant"] if item["target_id"] == "motor_A")
    vn["period_through"] = 6
    source["strategies"]["variant"].append({**deepcopy(vn), "period_from": 7, "period_through": 7, "parameters": {"insurance_threshold": "0.05", "insurance_threshold_shock": "0.05"}})
    result = calculate(source)
    assert result["valid"]
    rows = [row for row in result["decision_traces"]["variant"] if row["sector_id"] == "motor"]
    assert rows[5]["premium_income"] == "0.0000"
    assert rows[6]["quoted_price"] == "3.0000" and rows[6]["premium_income"] == "150.0000"
    assert rows[7]["premium_income"] == "300.0000"


def test_health_exit_decision_preserves_existing_opening_stock_billing():
    source = workshop_case("price", 10)
    old = next(item for item in source["strategies"]["variant"] if item["strategy_id"] == "health.declared_exits")
    old["period_through"] = 5
    source["strategies"]["variant"].append({**deepcopy(old), "period_from": 6, "period_through": 10, "parameters": {"count": 2}})
    result = calculate(source)
    assert result["valid"]
    rows = [entry["generated_period_source"] for entry in result["decision_traces"]["variant"] if entry["sector_id"] == "health"]
    assert rows[5]["opening_policies"] == 100 and rows[5]["exits"] == 2 and rows[5]["premium_income"] == "300.0000"
    assert rows[6]["opening_policies"] == 99 and rows[6]["premium_income"] == "297.0000"


@pytest.mark.parametrize("kind", ["late_draw", "nan", "group", "overlap", "unmapped", "prefix", "health_exit", "life_gap", "unknown", "id_type"])
def test_invalid_late_modern_sources_are_atomic(kind):
    source = workshop_case()
    if kind == "late_draw": source["market_periods"][-1]["draws"]["VU1"] = ["0.5"]
    if kind == "nan": source["market_periods"][-1]["damage_indicator"] = "NaN"
    if kind == "group": source["policyholder_groups"][-1]["initial_insurer_id"] = 9
    if kind == "overlap": source["strategies"]["variant"].append(deepcopy(source["strategies"]["variant"][0]))
    if kind == "unmapped": source["strategies"]["variant"][0]["strategy_id"] = "vu.vrvu07"
    if kind == "prefix": source["strategies"]["variant"][0]["parameters"]["premium_factor"] = "5"
    if kind == "health_exit": source["strategies"]["variant"][-2] = {"actor_type": "policyholder", "target_id": "health_A", "sector_id": "health", "strategy_id": "health.declared_exits", "period_from": 1, "period_through": 100, "parameters": {"count": 1000}}
    if kind == "life_gap": next(item for item in source["strategies"]["variant"] if item["sector_id"] == "life")["period_through"] = 99
    if kind == "unknown": source["population"] = "historical"
    if kind == "id_type": source["strategies"]["variant"][0]["target_id"] = []
    result = calculate(source)
    assert not result["valid"] and result["content_digest"] is None
    assert result["sides"] == result["generated_sources"] == result["decision_traces"] == {}
    assert result["partial_result_returned"] is False and result["writes_performed"] is False
