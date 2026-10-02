"""Reproducible AP5 gate probes; deliberately not a product market runner.

Compare independent hand calculations with existing Vrvn06 and balance kernels.
Capacity admission is the explicit modern proposal in ims_ap5_market_contract.md.
No historical limit or production contract is changed by this script.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from hashlib import sha256
import json
from pathlib import Path
from time import perf_counter

from ims.accounting.model_balance_contract import MODEL_BALANCE_CONTRACT_VERSION
from ims.accounting.non_life_model_balance import (
    MODEL_BALANCE_INPUT_VERSION,
    build_non_life_model_balance,
)
from ims.model.entities import Insurer
from ims.model.sector_taxonomy import SECTOR_TAXONOMY_VERSION
from ims.model.vn_insurance_rules import (
    VNBestInfoInsuranceRuleParameters,
    apply_vn_best_info_insurance_rule,
)
from ims.model.vu_rules import VURandomUniformRuleParameters, apply_vu_random_uniform_rule


@dataclass(frozen=True, slots=True)
class Cohort:
    cohort_id: str
    quantity: int
    loss: int


def choose(offers: dict[int, int], quantity: int, remaining: dict[int, int]) -> int | None:
    eligible = [
        {"insurer_id": insurer_id, "premiums_current_sector": [price, price]}
        for insurer_id, price in offers.items()
        if remaining[insurer_id] >= quantity
    ]
    if not eligible:
        return None
    result = apply_vn_best_info_insurance_rule(
        VNBestInfoInsuranceRuleParameters([1, 1], [1, 1]),
        period=2, market_damage_indicator=0, insurer_inputs=eligible,
    )
    selected = result.decisions[0].insurer_id
    assert selected is not None
    remaining[selected] -= quantity
    return selected


def balance_input(insurer_id: int, *, liability: int = 0, premium: int = 0,
                  incurred: int = 0, paid: int = 0, expense: int = 0) -> dict:
    flow = dict(premium_income="0", investment_income="0", claims_incurred="0",
                claims_paid="0", operating_expense="0", capital_contribution="0",
                capital_distribution="0")
    booked = dict(flow, premium_income=str(premium), claims_incurred=str(incurred),
                  claims_paid=str(paid), operating_expense=str(expense))
    return {
        "schema_version": MODEL_BALANCE_INPUT_VERSION,
        "model_balance_contract_schema_version": MODEL_BALANCE_CONTRACT_VERSION,
        "sector_taxonomy_schema_version": SECTOR_TAXONOMY_VERSION,
        "source_kind": "explicit_scenario", "historical_mapping_status": "unresolved",
        "insurer_id": insurer_id, "sector_id": "motor",
        "opening": {"opening_cash": "100", "opening_claim_liability": str(liability),
                    "opening_equity": str(100 - liability)},
        "periods": [dict(period=1, **flow), dict(period=2, **booked), dict(period=3, **flow)],
    }


def close(value: dict, expected: tuple[int, int, int, int]) -> dict:
    report = build_non_life_model_balance(value)
    assert not report.issues, report.issues
    row = report.rows[1]
    actual = (row.closing_cash, row.closing_claim_liability, row.closing_equity, row.period_profit)
    assert actual == tuple(Decimal(x) for x in expected), (actual, expected)
    assert row.closing_cash == row.closing_claim_liability + row.closing_equity
    following = report.rows[2]
    assert (following.opening_cash, following.opening_claim_liability, following.opening_equity) == actual[:3]
    return row.to_dict()


def hand_cases() -> dict:
    # These expected amounts are the independently worked H1/H2 document values.
    owner = choose({1: 3, 2: 2}, 10, {1: 20, 2: 20})
    assert owner == 2
    h1 = [
        close(balance_input(1, liability=20, paid=5, expense=2), (93, 15, 78, -2)),
        close(balance_input(owner, premium=20, incurred=40, paid=40, expense=1), (79, 0, 79, -21)),
    ]
    assert sum(Decimal(r["closing_cash"]) for r in h1) == 172
    assert sum(Decimal(r["closing_claim_liability"]) for r in h1) == 15
    assert sum(Decimal(r["closing_equity"]) for r in h1) == 157

    offers = {3: 3, 2: 2, 1: 2}  # Deliberately reversed: tie must still select ID 1.
    remaining = {1: 6, 2: 8, 3: 4}
    cohorts = [Cohort("G3", 5, 7), Cohort("G2", 8, 4), Cohort("G1", 6, 9)]
    choices = {}
    booked = {i: {"premium": 0, "loss": 0, "quantity": 0} for i in offers}
    uninsured_quantity = uninsured_loss = 0
    for cohort in sorted(cohorts, key=lambda c: c.cohort_id):
        insurer_id = choose(offers, cohort.quantity, remaining)
        choices[cohort.cohort_id] = insurer_id
        if insurer_id is None:
            uninsured_quantity += cohort.quantity
            uninsured_loss += cohort.loss
        else:
            booked[insurer_id]["premium"] += offers[insurer_id] * cohort.quantity
            booked[insurer_id]["loss"] += cohort.loss
            booked[insurer_id]["quantity"] += cohort.quantity
    assert choices == {"G1": 1, "G2": 2, "G3": None}
    assert (uninsured_quantity, uninsured_loss) == (5, 7)
    expected = {1: (103, 0, 103, 3), 2: (112, 0, 112, 12), 3: (100, 0, 100, 0)}
    h2 = [close(balance_input(i, premium=booked[i]["premium"], incurred=booked[i]["loss"],
                              paid=booked[i]["loss"]), expected[i]) for i in sorted(offers)]
    assert sum(item["quantity"] for item in booked.values()) + uninsured_quantity == 19
    assert sum(item["loss"] for item in booked.values()) + uninsured_loss == 20
    assets = {i: Decimal(r["closing_cash"]) for i, r in zip(sorted(offers), h2)}
    assert sum(assets.values()) == 315
    assert assets[1] + assets[2] == 215
    assert assets[3] == 100
    assert assets[2] + assets[3] == 212
    assert sum(item["premium"] for item in booked.values()) == 28
    return {"H1": {"new_owner": owner, "rows": h1},
            "H2": {"choices": choices, "rows": h2, "uninsured_quantity": 5,
                   "uninsured_loss": 7, "weighted_price": "2.0000"}}


def bound_draw(insurer_id: int, period: int, channel: str) -> float:
    # Proposed seed binding, not a claim of historical myrndf equivalence.
    key = json.dumps(["ap5-gate-probe.v1", 20261002, insurer_id, period, channel],
                     separators=(",", ":")).encode("ascii")
    return (int.from_bytes(sha256(key).digest()[:8], "big") >> 11) / (1 << 53)


def kernel_probe(count: int) -> dict:
    start = perf_counter()
    params = VURandomUniformRuleParameters([6, 6], [2, 2], [6, 6], [2, 2])
    series = []
    for period in range(1, 101):
        offers = []
        for insurer_id in range(1, count + 1):
            draws = [bound_draw(insurer_id, period, channel) for channel in ("motor_price", "property_price", "motor_ad", "property_ad")]
            result = apply_vu_random_uniform_rule(
                Insurer(entity_id=insurer_id, premiums_current_sector=[3, 3],
                        advertising_current_sector=[1, 1]),
                params, period=period, random_draws=draws, interest_rate=0,
            )
            offers.append({"insurer_id": insurer_id,
                           "premiums_current_sector": result.premiums_current_sector,
                           "draws": draws})
        # The legacy selection kernel accepts positive modern IDs, including 41.
        selected = apply_vn_best_info_insurance_rule(
            VNBestInfoInsuranceRuleParameters([1, 1], [1, 1]), period=max(period, 2),
            market_damage_indicator=0,
            insurer_inputs=[{k: v for k, v in offer.items() if k != "draws"} for offer in offers],
        )
        series.append({"period": period, "offers": offers, "selected": selected.chosen_insurer_ids})
    encoded = json.dumps(series, sort_keys=True, separators=(",", ":")).encode("ascii")
    common = [{"period": r["period"], "offers": r["offers"][:40]} for r in series]
    common_bytes = json.dumps(common, sort_keys=True, separators=(",", ":")).encode("ascii")
    return {"vu_count": count, "period_count": 100, "duration_seconds": perf_counter() - start,
            "offer_snapshot_bytes": len(encoded), "snapshot_sha256": sha256(encoded).hexdigest(),
            "first_40_offers_sha256": sha256(common_bytes).hexdigest()}


def run() -> dict:
    started = datetime.now(timezone.utc).isoformat()
    cases = hand_cases()
    probes = [kernel_probe(40), kernel_probe(41)]
    replay = [kernel_probe(40), kernel_probe(41)]
    assert [p["snapshot_sha256"] for p in probes] == [p["snapshot_sha256"] for p in replay]
    assert probes[0]["first_40_offers_sha256"] == probes[1]["first_40_offers_sha256"]
    legacy41 = build_non_life_model_balance(balance_input(41))
    assert "insurer_id_invalid" in {issue.code for issue in legacy41.issues}
    capacities = [8 if 4 <= period <= 5 else 6 for period in range(1, 7)]
    costs = [3 if period == 2 else 0 for period in range(1, 7)]
    assert capacities == [6, 6, 6, 8, 8, 6]
    assert sum(costs) == 3
    return {
        "schema_version": "ims.ap5-contract-probe.v1", "executed_at": started,
        "scope": "gate_preparation_existing_kernels_and_hand_calculations",
        "product_market_runner": False, "contract_accepted": False,
        "cases": cases, "measure_example": {"periods": [1, 2, 3, 4, 5, 6],
                                               "capacities": capacities, "costs": costs},
        "kernel_probes": probes, "replay_equal": True,
        "entrant_preserves_existing_offers_and_draws": True,
        "legacy_41_balance_rejected": True,
        "limits": ["No common 40/41-VU balance calculated", "No API/UI/Excel or installer checked",
                   "Kernel snapshot size is not product API size", "Measure example is a hand schedule, not a product measure engine"],
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = run()
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("AP5 TOR-PROBEN OK: H1/H2, Carryover, 40/41-Angebotskerne, Replay; Produktlauf noch offen")
