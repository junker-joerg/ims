"""Observe existing AP7-related cores and check independent hand arithmetic.

These probes neither implement nor authorize the proposed production contract.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from decimal import Decimal, ROUND_FLOOR
import hashlib
import json
from pathlib import Path
from time import perf_counter
from typing import Any

from ims.accounting.life_period_chain import run_life_policy_period_chain
from ims.ict.presets import workshop_case as ict_case
from ims.ict.simulation import calculate as ict_calculate
from ims.market.presets import assignment, family, portfolio, workshop_case as market_case
from ims.market.runner import calculate as market_calculate

ROOT = Path(__file__).resolve().parents[2]
SOURCES = (
    "IMS.E", "IMSDATA.C", "ESS.C", "python_port/ims/market/runner.py",
    "python_port/ims/ict/simulation.py", "python_port/ims/accounting/life_period_chain.py",
    "tests/fixtures/life_period_chain_v1.json",
)


def observe_life(root: Path) -> dict[str, Any]:
    source = "tests/fixtures/life_period_chain_v1.json"
    life = json.loads((root / source).read_text(encoding="utf-8"))
    before = deepcopy(life)
    with_new = run_life_policy_period_chain(life).to_dict()
    closed = deepcopy(life)
    closed["periods"][0]["new_business"] = []
    closed["periods"][1]["policy_flows"] = [
        row for row in closed["periods"][1]["policy_flows"] if row["policy_id"] != "C1"
    ]
    closed_before = deepcopy(closed)
    without_new = run_life_policy_period_chain(closed).to_dict()
    assert life == before and closed == closed_before
    assert with_new["valid"] and without_new["valid"]
    assert [row["death_benefits_paid"] for row in with_new["rows"]] == [
        row["death_benefits_paid"] for row in without_new["rows"]
    ]
    assert with_new["rows"][0]["maturity_benefits_paid"] == "25.0000"
    assert without_new["rows"][0]["maturity_benefits_paid"] == "25.0000"
    keys = (
        "period", "premiums_collected", "death_benefits_paid", "maturity_benefits_paid",
        "closing_backing_assets", "closing_guarantee_liability", "closing_equity",
    )
    for result in (with_new, without_new):
        for row in result["rows"]:
            assert Decimal(row["closing_backing_assets"]) == (
                Decimal(row["closing_guarantee_liability"]) + Decimal(row["closing_equity"])
            )
    return {
        "source": source,
        "with_declared_new_business": [{key: row[key] for key in keys} for row in with_new["rows"]],
        "without_new_business": [{key: row[key] for key in keys} for row in without_new["rows"]],
        "old_death_and_first_maturity_preserved": True,
        "input_unchanged": True,
    }


def observe_ict() -> dict[str, Any]:
    case = ict_case()
    case["period_count"] = 1
    case["services"] = [case["services"][0]]
    case["insurers"] = [case["insurers"][0]]
    case["services"][0]["unit_margin"] = "0"
    case["events"][0].update(start_hour="0", duration_hours="24")
    before = deepcopy(case)
    plain = ict_calculate(case)
    guarded = deepcopy(case)
    guarded["strategies"] = [{
        "strategy_id": "declared-fallback", "kind": "fallback", "asset_id": "portal-1",
        "start_hour": "0", "through_hour": "24", "effectiveness": "1", "cost_per_hour": "0.25",
        "assumption_note": "Bestehender AP3-Kapazitätsparameter, kein neuer unabhängiger Ersatzpfad.",
    }]
    guarded_before = deepcopy(guarded)
    fallback = ict_calculate(guarded)
    assert case == before and guarded == guarded_before
    assert plain["valid"] and fallback["valid"]
    assert plain["variant"]["service_rows"][0]["processed_original"] == "0.0000"
    assert fallback["variant"]["service_rows"][0]["processed_original"] == "240.0000"
    return {
        "source": "ims.ict.presets.workshop_case", "without_fallback_processed": "0.0000",
        "declared_fallback_processed": "240.0000",
        "fallback_kind": "declared_capacity_not_verified_independence",
        "fallback_still_has_original_platform_dependency": True, "input_unchanged": True,
    }


def observe_entry() -> dict[str, Any]:
    case = market_case("switch", 25)
    case["insurers"].append({
        "insurer_id": 3, "insurance_group_id": "Fiktiver_Eintritt", "name": "Fiktiver Anbieter 3",
        "sectors": {"motor": portfolio(25, assets="0", capacity="0")},
    })
    case["insurers"][-1]["sectors"]["motor"]["periods"][20]["capital_contribution"] = "1000"
    case["families"].append(family("Fiktiver_Preis", "motor", "offer.fixed", {"price": "1", "advertising": "0"}))
    for side in ("baseline", "variant"):
        case["assignments"][side].append(assignment(3, "motor", "Fiktiver_Preis", end=25))
        case["measures"][side].append({
            "measure_id": "Eintritt", "insurer_id": 3, "sector_id": "motor",
            "decision_period": 21, "lead_periods": 0, "duration": 5, "cost": "0",
            "overrides": {"capacity": "10"},
        })
    case["measures"]["variant"].append({
        "measure_id": "Preisantwort", "insurer_id": 1, "sector_id": "motor",
        "decision_period": 21, "lead_periods": 0, "duration": 5, "cost": "0",
        "overrides": {"price": "0.5"},
    })
    case["customer_groups"][0]["risk_periods"][20].update(loss="8", paid_share="1")
    before = deepcopy(case)
    result = market_calculate(case)
    assert case == before and result["valid"], result["issues"]
    entrant = [row for row in result["sides"]["baseline"]["vu_rows"]
               if row["insurer_id"] == 3 and row["period"] in (20, 21)]
    assert entrant[0]["closing_assets"] == "0.0000" and entrant[0]["premium_income"] == "0.0000"
    assert entrant[1]["capital_contribution"] == "1000.0000"
    assert entrant[1]["premium_income"] == "10.0000"
    assert entrant[1]["claims_paid"] == "8.0000" and entrant[1]["closing_assets"] == "1002.0000"
    decisions = [row for row in result["sides"]["baseline"]["customer_decisions"] if row["period"] in (20, 21)]
    assert [row["insurer_id"] for row in decisions] == [2, 3]
    reply = next(row for row in result["sides"]["variant"]["customer_decisions"] if row["period"] == 21)
    assert reply["insurer_id"] == 1 and reply["premium_income"] == "5.0000" and reply["risk_loss"] == "8.0000"
    registered = next(row["active_vu_count"] for row in result["sides"]["baseline"]["market_rows"]
                      if row["period"] == 20 and row["sector_id"] == "total")
    assert registered == 3
    return {
        "period_count": 25, "registered_actors": 3, "entrant_P20_P21": entrant,
        "baseline_decision_P20_P21": decisions, "variant_decision_P21": reply,
        "old_AP5_active_count_P20": registered, "input_unchanged": True,
        "limit": "AP5 counts registered sector rows as active; a new AP7 activation status remains to implement.",
    }


def hand_queue(outage: bool) -> dict[str, Any]:
    """Independent six-hour FIFO arithmetic; one hour per tiny hand period."""
    queue: list[str] = []
    pending: list[str] = []
    issued: list[str] = []
    rows = []
    for period in range(1, 7):
        due, pending = pending, []
        issued.extend(due)
        queue.extend([f"P{period}-A", f"P{period}-B"])
        capacity = 0 if outage and period in (3, 4) else 3
        completed, queue = queue[:capacity], queue[capacity:]
        pending.extend(completed)
        rows.append({
            "period": period, "arrivals": 2, "completed": len(completed), "issued": len(due),
            "closing_queue": len(queue), "pending_next_period": len(pending),
            "cumulative_issued": len(issued), "premium": str(Decimal(len(due)) * 3),
            "new_liability": str(Decimal(len(due)) * 2),
        })
        assert len(issued) + len(pending) + len(queue) == period * 2
    return {"rows": rows, "issued": len(issued), "pending_next_period": len(pending), "queue": len(queue)}


def hand_arithmetic() -> dict[str, Any]:
    baseline, shock = hand_queue(False), hand_queue(True)
    assert (baseline["issued"], baseline["pending_next_period"], baseline["queue"]) == (10, 2, 0)
    assert (shock["issued"], shock["pending_next_period"], shock["queue"]) == (7, 3, 2)
    weights = [Decimal("0.3333"), Decimal("0.3333"), Decimal("0.3334")]
    costs = [(6 * weight).quantize(Decimal("0.0001")) for weight in weights]
    assert sum(weights) == 1 and sum(costs) == 6
    graph = {"US-IAM": [], "Q-independent": [], "Q-dependent": ["US-IAM"]}
    def available(key: str) -> bool:
        return key != "US-IAM" and all(available(dependency) for dependency in graph[key])
    assert available("Q-independent") and not available("Q-dependent")
    counts = [int((Decimal(4) * Decimal(a)).to_integral_value(rounding=ROUND_FLOOR)) for a in ("1", ".25", ".5")]
    assert counts == [4, 1, 2]
    # Default 24-hour clock: [480,516) spans all of P21 and half of P22.
    outage_hours = [max(0, min(end, 516) - max(start, 480)) for start, end in ((480, 504), (504, 528))]
    assert outage_hours == [24, 12]
    return {
        "attractiveness_pool_4_counts": counts, "queue_baseline": baseline, "queue_shock": shock,
        "premium_difference_at_horizon": "9",
        "difference_kind": "deferred_issuance_with_terminal_pending_items_not_permanent_loss",
        "no_second_ict_margin_deduction": True, "shared_cost": "6", "weights": [str(w) for w in weights],
        "cost_allocations": [str(cost) for cost in costs],
        "independent_fallback_available": available("Q-independent"),
        "dependent_fallback_available": available("Q-dependent"),
        "outage_hours_P21_P22": outage_hours, "half_open_end_hour": 516,
        "six_hour_hand_clock_note": "Tiny one-hour hand periods; proposed full-demo default is 24 hours per model period.",
    }


def source_hashes(root: Path) -> dict[str, str]:
    return {name: hashlib.sha256((root / name).read_bytes()).hexdigest() for name in SOURCES}


def probe_contract(root: Path = ROOT) -> dict[str, Any]:
    started = perf_counter()
    before = source_hashes(root)
    result = {
        "schema_version": "ims.ap7-contract-probes.v1", "status": "passed",
        "kind": "existing_core_observations_and_independent_hand_arithmetic_not_production_implementation",
        "new_model_contract_authorized": False, "historical_full_equality_claim": False,
        "existing_life_core": observe_life(root), "existing_ict_core": observe_ict(),
        "existing_market_entry_probe": observe_entry(), "independent_proposed_hand_arithmetic": hand_arithmetic(),
        "source_hashes": before,
    }
    assert before == source_hashes(root)
    result["seconds"] = perf_counter() - started
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=ROOT / ".tmp-pr-ap7/contract-probes.json")
    args = parser.parse_args(argv)
    protected = {(ROOT / name).resolve() for name in SOURCES} | {Path(__file__).resolve()}
    if args.out.resolve() in protected:
        parser.error("Ausgabe darf keine Eingangsquelle oder Prüferdatei überschreiben")
    report = probe_contract()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "seconds": report["seconds"],
                      "new_model_contract_authorized": False, "out": str(args.out)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
