from copy import deepcopy
from decimal import Decimal

import pytest

from ims.accounting.management_case import calculate, declare_sources, source_contract, workshop_case


@pytest.mark.parametrize("case", ["inflation", "price", "capital"])
def test_declared_hundred_case_exact_balances_prefixes_and_effects(case):
    source = workshop_case(case, 100, 1)
    before = deepcopy(source)
    full = calculate(source)
    short = calculate(workshop_case(case, 2, 1))
    assert full["valid"] and short["valid"]
    assert full == calculate(source) and source == before
    assert full["sides"]["baseline"]["total_rows"][-1]["closing_equity"] == "87500.0000"
    for side in ("baseline", "variant"):
        result = full["sides"][side]
        assert result["total_rows"][:2] == short["sides"][side]["total_rows"]
        for period, row in enumerate(result["total_rows"]):
            assert Decimal(row["closing_assets"]) == Decimal(row["closing_liabilities"]) + Decimal(row["closing_equity"])
            assert Decimal(row["closing_equity"]) == sum(Decimal(sector["rows"][period]["closing_equity"]) for sector in result["sectors"])
            if period: assert row["opening_equity"] == result["total_rows"][period - 1]["closing_equity"]
    assert full["sides"]["baseline"]["total_rows"][:5] == full["sides"]["variant"]["total_rows"][:5]
    assert full["sides"]["baseline"]["total_rows"][5]["period_profit"] != full["sides"]["variant"]["total_rows"][5]["period_profit"]
    assert full["regulatory_metrics"]["scr"] is None


@pytest.mark.parametrize("kind", ["stale_digest", "late_balance", "vu", "scenario", "variant", "horizon", "unexplained"])
def test_common_sources_are_atomic_and_never_silently_relabelled(kind):
    source = workshop_case("inflation", 100, 1)
    envelope = source["sides"]["variant"]
    part = envelope["four_sector_input"]
    if kind == "stale_digest": part["sectors"]["motor"]["periods"][-1]["premium_income"] = "999"
    if kind == "late_balance":
        part["sectors"]["health"]["periods"][-1]["benefits_paid"] = "999999"
        envelope["source_contract"] = source_contract(part, envelope["source_contract"]["economic_assumption"])
    if kind == "vu": part["insurer_id"] = 2
    if kind == "scenario": part["scenario_id"] = "other"
    if kind == "variant": part["variant_id"] = "baseline"
    if kind == "horizon": part["sectors"]["motor"]["periods"].pop()
    if kind == "unexplained": envelope["source_contract"]["economic_assumption"] = ""
    result = calculate(source)
    assert not result["valid"] and result["content_digest"] is None
    assert result["sides"] == {} and result["partial_result_returned"] is False


def test_edit_requires_explicit_source_redeclaration_and_preserves_ids():
    source = workshop_case("price", 2, 1)
    source["sides"]["variant"]["four_sector_input"]["sectors"]["motor"]["periods"][0]["premium_income"] = "250"
    assert not calculate(source)["valid"]
    assert not declare_sources({"source_input": source, "explicit_common_source_declaration": False})["valid"]
    rebound = declare_sources({"source_input": source, "explicit_common_source_declaration": True})
    assert rebound["valid"] and calculate(rebound["source_input"])["valid"]
    assert rebound["source_input"]["sides"]["variant"]["four_sector_input"] == source["sides"]["variant"]["four_sector_input"]
