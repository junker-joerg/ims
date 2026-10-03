"""Regression values for the AP7 proposal; no new production semantics."""
from __future__ import annotations

from decimal import Decimal
import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("ap7_probes", ROOT / "scripts/planning/probe_ap7_contract.py")
probes = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(probes)


@pytest.fixture(scope="module")
def report():
    return probes.probe_contract()


def test_life_old_payments_remain_when_new_policy_is_removed(report):
    life = report["existing_life_core"]
    with_new, closed = life["with_declared_new_business"], life["without_new_business"]
    assert [row["death_benefits_paid"] for row in closed] == ["65.0000", "0.0000"]
    assert [row["maturity_benefits_paid"] for row in closed] == ["25.0000", "60.0000"]
    assert [(row["closing_backing_assets"], row["closing_guarantee_liability"], row["closing_equity"])
            for row in closed] == [("94.0000", "46.0000", "48.0000"), ("35.0000", "0.0000", "35.0000")]
    assert with_new[1]["closing_equity"] == "33.0000"
    assert life["input_unchanged"]


def test_existing_entry_financing_and_registered_count_are_distinguished(report):
    entry = report["existing_market_entry_probe"]
    before, after = entry["entrant_P20_P21"]
    assert before["premium_income"] == "0.0000" and before["closing_equity"] == "0.0000"
    assert Decimal(after["capital_contribution"]) + Decimal(after["premium_income"]) - Decimal(after["claims_paid"]) == Decimal("1002")
    assert after["closing_assets"] == after["closing_equity"] == "1002.0000"
    assert entry["old_AP5_active_count_P20"] == 3
    assert entry["variant_decision_P21"]["premium_income"] == "5.0000"
    assert entry["variant_decision_P21"]["risk_loss"] == "8.0000"
    assert entry["input_unchanged"]


def test_declared_capacity_fallback_does_not_claim_independent_path(report):
    old = report["existing_ict_core"]
    assert old["without_fallback_processed"] == "0.0000"
    assert old["declared_fallback_processed"] == "240.0000"
    assert old["fallback_still_has_original_platform_dependency"]
    hand = report["independent_proposed_hand_arithmetic"]
    assert hand["independent_fallback_available"] and not hand["dependent_fallback_available"]
    assert hand["outage_hours_P21_P22"] == [24, 12]


def test_hand_queue_keeps_unissued_and_processed_pending_visible(report):
    hand = report["independent_proposed_hand_arithmetic"]
    for side in (hand["queue_baseline"], hand["queue_shock"]):
        for row in side["rows"]:
            assert row["cumulative_issued"] + row["pending_next_period"] + row["closing_queue"] == row["period"] * 2
    assert (hand["queue_shock"]["issued"], hand["queue_shock"]["pending_next_period"], hand["queue_shock"]["queue"]) == (7, 3, 2)
    assert sum(Decimal(row["premium"]) for row in hand["queue_baseline"]["rows"]) - sum(
        Decimal(row["premium"]) for row in hand["queue_shock"]["rows"]) == Decimal("9")
    assert sum(Decimal(cost) for cost in hand["cost_allocations"]) == Decimal("6")
    assert hand["attractiveness_pool_4_counts"] == [4, 1, 2]


def test_probe_preserves_sources_and_cannot_overwrite_them(report):
    assert report["source_hashes"] == probes.source_hashes(ROOT)
    assert report["status"] == "passed"
    assert report["new_model_contract_authorized"] is False
    assert report["historical_full_equality_claim"] is False
    for source in (*probes.SOURCES, "scripts/planning/probe_ap7_contract.py"):
        with pytest.raises(SystemExit) as error:
            probes.main(["--out", str(ROOT / source)])
        assert error.value.code == 2
