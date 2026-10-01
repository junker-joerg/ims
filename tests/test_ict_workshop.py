from copy import deepcopy
from decimal import Decimal

import pytest

from ims.ict.contract import ContractError, validate
from ims.ict.presets import workshop_case
from ims.ict.simulation import calculate


def small_case() -> dict:
    doc = workshop_case()
    doc["period_count"] = 3
    doc["providers"] = doc["providers"][:1]
    doc["assets"] = doc["assets"][:1]
    doc["insurers"] = doc["insurers"][:1]
    doc["services"] = [doc["services"][0]]
    doc["services"][0]["asset_ids"] = ["platform"]
    doc["events"][0].update(start_hour="0", duration_hours="12")
    return doc


def test_outage_queue_recovery_and_exact_balance_without_double_loss() -> None:
    value = small_case()
    before = deepcopy(value)
    result = calculate(value)
    assert value == before
    assert result["valid"]
    rows = result["variant"]["service_rows"]
    # 12 available hours × 12 jobs/h: 144 of 240 arrivals in period 1.
    assert [r["processed_original"] for r in rows] == ["144.0000", "288.0000", "288.0000"]
    assert [r["closing_backlog"] for r in rows] == ["96.0000", "48.0000", "0.0000"]
    # Deferred margins recover, while the explicitly declared holding expense remains.
    assert [r["operational_impact"] for r in rows] == ["193.9200", "-95.0400", "-96.0000"]
    balances = result["variant"]["balance_rows"]
    assert balances[-1]["cumulative_operational_impact"] == "2.8800"
    assert balances[-1]["model_own_funds_proxy"] == "7297.1200"
    for row in balances:
        assert Decimal(row["closing_assets"]) == Decimal(row["closing_liabilities"]) + Decimal(row["model_own_funds_proxy"])
    assert result["runner_invoked"] is result["writes_performed"] is False
    assert all(x is None for x in result["regulatory_metrics"].values())


def test_integrity_creates_rework_without_false_sales_or_implicit_outage() -> None:
    doc = small_case()
    doc["events"][0].update(kind="data_integrity", target_id="platform", capacity_loss_fraction="0", rework_fraction="0.5")
    rows = calculate(doc)["variant"]["service_rows"]
    assert rows[0]["processed_original"] == "240.0000"
    assert rows[0]["rework_generated"] == "60.0000"
    assert rows[0]["processed_rework"] == "48.0000"
    assert rows[0]["closing_rework_backlog"] == "12.0000"
    assert rows[0]["lost_margin"] == "0.0000"
    assert rows[0]["operational_impact"] == "15.2400"
    assert rows[1]["processed_rework"] == "12.0000"
    assert rows[1]["closing_backlog"] == "0.0000"


def test_shared_provider_hits_two_insurers_once_and_local_fallback_is_local() -> None:
    doc = workshop_case()
    doc["period_count"] = 3
    doc["events"][0].update(start_hour="0", duration_hours="24")
    plain = calculate(doc)
    first = plain["variant"]["balance_rows"][:2]
    assert first[0]["operational_impact"] == first[1]["operational_impact"]
    assert plain["provider_concentration"][1]["insurer_ids"] == [1, 2]
    doc["strategies"] = [{"strategy_id": "local-fallback", "kind": "fallback", "asset_id": "portal-1",
                           "start_hour": "0", "through_hour": "24", "effectiveness": "1", "cost_per_hour": "0.25",
                           "assumption_note": "Lokaler deklarierter Fallback für VU 1."}]
    guarded = calculate(doc)["variant"]["balance_rows"][:2]
    assert guarded[0]["operational_impact"] == guarded[0]["strategy_cost"] == "6.0000"
    assert guarded[1]["operational_impact"] == first[1]["operational_impact"]


def test_shared_asset_strategy_cost_is_allocated_once_across_owners() -> None:
    doc = workshop_case()
    doc["period_count"] = 1
    doc["strategies"] = [{"strategy_id": "prevention", "kind": "prevention", "asset_id": "platform", "start_hour": "0",
                           "through_hour": "24", "effectiveness": "0.5", "cost_per_hour": "0.25", "assumption_note": "Geteilte Prävention."}]
    rows = calculate(doc)["variant"]["balance_rows"]
    assert sum(Decimal(r["strategy_cost"]) for r in rows) == Decimal("6")
    assert [r["strategy_cost"] for r in rows] == ["3.0000", "3.0000"]


def test_restart_shortens_remaining_time_at_activation_and_half_open_boundaries() -> None:
    doc = small_case()
    doc["events"][0].update(start_hour="24", duration_hours="24")
    doc["strategies"] = [{"strategy_id": "restart", "kind": "restart", "asset_id": "platform", "start_hour": "36",
                           "through_hour": "48", "effectiveness": "0.5", "cost_per_hour": "0", "assumption_note": "Verbleibende Zeit halbieren."}]
    result = calculate(doc)
    assert result["timeline"][0]["effective_end_hour"] == "42.0"
    assert result["variant"]["service_rows"][0] == result["baseline"]["service_rows"][0]
    assert result["variant"]["service_rows"][1]["capacity_units"] == "72.0000"


def test_prevention_and_overlapping_same_provider_are_not_added_as_two_outages() -> None:
    doc = small_case()
    duplicate = deepcopy(doc["events"][0])
    duplicate["event_id"] = "second-outage"
    doc["events"].append(duplicate)
    without = calculate(doc)
    doc["events"].pop()
    assert calculate(doc)["variant"] == without["variant"]
    doc["strategies"] = [{"strategy_id": "prevent", "kind": "prevention", "asset_id": "platform", "start_hour": "0",
                           "through_hour": "24", "effectiveness": "1", "cost_per_hour": "0", "assumption_note": "Voll wirksame Szenario-Prävention."}]
    result = calculate(doc)
    assert result["variant"] == result["baseline"]


def test_hundred_period_calculation_is_deterministic_and_prefix_preserving() -> None:
    doc = workshop_case()
    full = calculate(doc)
    assert full == calculate(deepcopy(doc))
    short = deepcopy(doc)
    short["period_count"] = 2
    prefix = calculate(short)
    assert prefix["valid"]
    for side in ("baseline", "variant"):
        for key in ("service_rows", "balance_rows"):
            assert prefix[side][key] == [r for r in full[side][key] if r["period"] <= 2]


@pytest.mark.parametrize("mutation", [
    lambda d: d.update(period_hours="0"),
    lambda d: d.update(period_count=True),
    lambda d: d["assets"][0]["depends_on"].append("platform"),
    lambda d: d["assets"][0].update(provider_id="unknown"),
    lambda d: d["services"][0].update(insurer_id=25),
    lambda d: d["services"][0].update(demand_per_hour="NaN"),
    lambda d: d["events"][0].update(capacity_loss_fraction="0.5"),
    lambda d: d["events"][0].update(rework_fraction="1"),
    lambda d: d["events"][0].update(duration_hours="999999999"),
    lambda d: d["services"].append(deepcopy(d["services"][0])),
    lambda d: d.update(guessed_defaults=True),
    lambda d: d["assets"][0].update(depends_on=["unknown"]),
    lambda d: d["services"][0].update(asset_ids=[]),
])
def test_invalid_contract_is_atomic(mutation) -> None:
    doc = small_case()
    mutation(doc)
    with pytest.raises(ContractError):
        validate(doc)
    result = calculate(doc)
    assert not result["valid"] and result["issues"]
    assert result["baseline"] is result["variant"] is result["content_digest"] is None
    assert result["partial_result_returned"] is result["ict_model_calculated"] is False
