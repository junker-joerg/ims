"""AP8 read-only projection of the accepted market books, never a new model run.

The runner is the authority. Ratios describe its current membership and financial
rows; an exact accounting bridge is not an isolated causal attribution.
"""
from __future__ import annotations

from collections import defaultdict
from copy import deepcopy
from decimal import Decimal, localcontext
import json

from ims.accounting.management_case import digest
from ims.market.runner import FINANCIAL_FIELDS
from ims.market.transport import wire_payload
from ims.strategies.modern_bridge import ContractError, money

RESULT_VERSION = "ims.market-explorer-result.v1"
MAX_RESULT_BYTES = 40 * 1024 * 1024
BOOK_TERMS = {"opening_equity": 1, "premium_income": 1, "investment_income": 1,
              "insurance_expense": -1, "operating_expense": -1,
              "capital_contribution": 1, "capital_distribution": -1}
ROW_FIELDS = set(FINANCIAL_FIELDS) | {
    "period", "sector_id", "insurer_id", "insurance_group_id", "family_id", "rule",
    "parameters", "active_measures", "information_period", "source_contract", "source_digest",
    "quoted_price", "covered_quantity", "weighted_price", "new_claims_paid", "old_claims_paid",
    "advertising_expense", "active_in_period", "process_and_response_cost", "ap7_new_policies",
    "market_ict_margin_double_deduction",
}


def sums(rows: list[dict]) -> dict[str, str]:
    return {key: money(sum((Decimal(row[key]) for row in rows), Decimal(0))) for key in FINANCIAL_FIELDS}


def share_statistics(rows: list[dict]) -> dict:
    """One sector/period, insurer money summed before shares and HHI are formed."""
    premiums = defaultdict(Decimal)
    active = set()
    for row in rows:
        premiums[row["insurer_id"]] += Decimal(row["premium_income"])
        if row.get("active_in_period", True):
            active.add(row["insurer_id"])
    total = sum(premiums.values(), Decimal(0))
    reason = "negative_premium_basis" if any(p < 0 for p in premiums.values()) else "zero_premium_basis" if total == 0 else None
    squares = sum((p * p for p in premiums.values()), Decimal(0))
    return {"premium_denominator": money(total), "premium_square_sum": format(squares, "f"),
            "hhi": None if reason else money(Decimal(10000) * squares / (total * total)),
            "undefined_reason": reason, "registered_vu_count": len(premiums), "active_vu_count": len(active),
            "shares": [{"insurer_id": aid, "premium_income": money(p),
                        "share_percent": None if reason else money(100 * p / total),
                        "active": aid in active} for aid, p in sorted(premiums.items())]}


def family_statistics(rows: list[dict]) -> dict:
    """Weight by opening assets; do not average unequal individual percentages."""
    total = sums(rows)
    assets = Decimal(total["opening_assets"])
    ratios = [100 * Decimal(row["period_profit"]) / Decimal(row["opening_assets"])
              for row in rows if Decimal(row["opening_assets"]) > 0]
    return {**total, "member_ids": sorted({row["insurer_id"] for row in rows}),
            "weight_field": "opening_assets", "weight_denominator": total["opening_assets"],
            "weighted_profit_percent": money(100 * Decimal(total["period_profit"]) / assets) if assets > 0 else None,
            "individual_min_percent": money(min(ratios)) if ratios else None,
            "individual_max_percent": money(max(ratios)) if ratios else None,
            "valid_individual_count": len(ratios), "individual_count": len(rows)}


def effective_switches(rows: list[dict]) -> list[dict]:
    """P1 is opening stock. Actual decisions alone establish risk/premium ownership."""
    return [deepcopy(row) for row in rows if row["period"] > 1
            and row["previous_insurer_id"] != row["insurer_id"]]


def _check_book(row: dict) -> None:
    value = lambda key: Decimal(row[key])
    profit = value("premium_income") + value("investment_income") - value("insurance_expense") - value("operating_expense")
    closing = sum((sign * value(key) for key, sign in BOOK_TERMS.items()), Decimal(0))
    if profit != value("period_profit") or closing != value("closing_equity"):
        raise ContractError("$.sides.vu_rows", "AP8-Buchungsidentität verletzt; kein Teilergebnis")


def project_result(result: dict) -> dict:
    """Own digest, unchanged underlying result digest; all source rows remain intact."""
    if not result.get("valid"):
        raise ContractError("$", "AP8 benötigt einen gültigen vollständigen Modelllauf")
    with localcontext() as context:
        context.prec = 64
        model = result["source_input"]
        shock = result.get("shock_bundle", {})
        sides = {}
        for side, source in result["sides"].items():
            financial = []
            markets, families = defaultdict(list), defaultdict(list)
            for row in source["vu_rows"]:
                _check_book(row)
                projected = deepcopy({key: value for key, value in row.items() if key in ROW_FIELDS})
                projected.setdefault("active_in_period", True)
                financial.append(projected)
                for sector in (row["sector_id"], "total"):
                    markets[row["period"], sector].append(row)
                    families[row["period"], sector, row["family_id"]].append(row)
            market_rows = []
            for row in source["market_rows"]:
                stats = share_statistics(markets[row["period"], row["sector_id"]])
                market_rows.append({**deepcopy(row), **{k: v for k, v in stats.items() if k != "shares"}})
            family_rows = [{"period": period, "sector_id": sector, "family_id": fid, **family_statistics(rows)}
                           for (period, sector, fid), rows in sorted(families.items())]
            sides[side] = {"financial_rows": financial, "market_rows": market_rows, "family_rows": family_rows,
                           "customer_rows": deepcopy(source["customer_decisions"]),
                           "switch_rows": effective_switches(source["customer_decisions"])}
            names = {"ict_process_rows": "process_rows", "ict_resource_rows": "resource_rows",
                     "ict_job_rows": "job_rows",
                     "ict_dependency_rows": "dependency_rows", "ict_event_rows": "event_rows", "cost_rows": "cost_rows",
                     "life_demand_rows": "life_demand_rows", "life_contract_rows": "life_contract_rows",
                     "switch_process_rows": "switch_process_rows", "terminal_process_rows": "terminal_process_rows"}
            for old, new in names.items():
                sides[side][new] = deepcopy(source.get(old, []))
        core = {"schema_version": RESULT_VERSION, "model_schema_version": result["schema_version"],
                "input_digest": result["input_digest"], "model_result_digest": result["content_digest"],
                "period_count": result["period_count"], "seed": model["seed"],
                "title": shock.get("title", result.get("source_bundle", {}).get("title", model["case_id"])),
                "actors": [{**{key: actor[key] for key in ("insurer_id", "name", "insurance_group_id")},
                            "sectors": list(actor["sectors"])} for actor in model["insurers"]],
                "families": deepcopy(model["families"]), "peer_groups": deepcopy(model["peer_groups"]),
                "comparison_labels": deepcopy(result.get("comparison_labels", {"baseline": "Basis", "variant": "Variante"})),
                "clock": deepcopy(result.get("clock")), "reference": deepcopy(result.get("reference")),
                "schedules": {"events": deepcopy(shock.get("events", [])), "responses": deepcopy(shock.get("responses", {})),
                              "assignments": deepcopy(model["assignments"]), "measures": deepcopy(model["measures"]),
                              "ict": deepcopy(shock.get("ict", {}))},
                "book_terms": BOOK_TERMS.copy(), "scope_notice": shock.get("assumption_note", model["provenance"]["description"]),
                "causal_limit": "Exakte Buchungsidentität; Modellkanal mit belegten Zeilen. Gleichzeitige Mechanismen oder Gruppenwechsel sind nicht isoliert kausal zerlegt. Kurven zeigen Beobachtungen.",
                "sides": sides}
        view = {**core, "valid": True, "issues": [], "content_digest": digest(core),
                "writes_performed": False, "partial_result_returned": False}
        if len(json.dumps(wire_payload(view), ensure_ascii=False, allow_nan=False, separators=(",", ":")).encode("utf-8")) > MAX_RESULT_BYTES:
            raise ContractError("$", "AP8-Ansicht überschreitet 40 MiB; kein Teilergebnis")
        return view
