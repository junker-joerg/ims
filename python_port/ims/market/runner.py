"""Pure common period market with actor-bound draws and risk-owner accounting."""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from decimal import Decimal, localcontext
from hashlib import sha256
import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ims.market.shock_plan import ShockPlan

from ims.accounting.health_period_chain import run_health_period_chain
from ims.accounting.life_period_chain import run_life_policy_period_chain
from ims.accounting.management_case import digest
from ims.market.contract import NON_LIFE, RESULT_VERSION, SECTORS, selected, validate
from ims.market.transport import wire_payload
from ims.model.entities import Insurer
from ims.model.vn_insurance_rules import VNBestInfoInsuranceRuleParameters, apply_vn_best_info_insurance_rule
from ims.model.vu_rules import VURandomUniformRuleParameters, apply_vu_random_uniform_rule
from ims.strategies.modern_bridge import ContractError, money

FINANCIAL_FIELDS = ("opening_assets", "opening_liabilities", "opening_equity", "closing_assets",
                    "closing_liabilities", "closing_equity", "period_profit", "premium_income",
                    "investment_income", "insurance_expense", "claims_paid", "operating_expense",
                    "measure_cost", "capital_contribution", "capital_distribution")
# Measured complete 41-VU/four-sector/100-period columnar response: 36.24 MB.
# Keep a bounded 48 MiB response budget; larger declared portfolios fail atomically.
MAX_RESULT_BYTES = 48 * 1024 * 1024


@dataclass(slots=True)
class Balance:
    assets: Decimal
    liabilities: Decimal
    equity: Decimal


def actor_draws(seed: int, actor: int, period: int) -> list[float]:
    draws = []
    for channel in ("motor_price", "property_price", "motor_advertising", "property_advertising"):
        key = json.dumps(["ims.market-rng.v1", seed, actor, period, channel], separators=(",", ":")).encode("ascii")
        draws.append((int.from_bytes(sha256(key).digest()[:8], "big") >> 11) / (1 << 53))
    return draws


def profile(doc: dict, side: str, aid: int, sector: str, p: int) -> tuple[dict, dict, list[str], Decimal]:
    family = selected(doc, side, aid, sector, p)
    params = deepcopy(family["parameters"])
    ids, cost = [], Decimal(0)
    for measure in doc["measures"][side]:
        if (measure["insurer_id"], measure["sector_id"]) != (aid, sector):
            continue
        if measure["decision_period"] == p:
            cost += Decimal(measure["cost"])
        start = measure["decision_period"] + measure["lead_periods"]
        if start <= p < start + measure["duration"]:
            params.update(measure["overrides"])
            ids.append(measure["measure_id"])
    return family, params, ids, cost


def aggregate(rows: list[dict], p: int, sector: str) -> dict:
    result = {"period": p, "sector_id": sector, **{field: money(sum((Decimal(row[field]) for row in rows), Decimal(0))) for field in FINANCIAL_FIELDS}}
    if sector == "total":
        # Exposure units differ between sectors; no invented mixed quantity/price.
        result.update(covered_quantity=None, weighted_price=None)
    else:
        quantity = sum((Decimal(row["covered_quantity"]) for row in rows), Decimal(0))
        result.update(covered_quantity=money(quantity), weighted_price=money(Decimal(result["premium_income"]) / quantity) if quantity else None)
    result["active_vu_count"] = len({row["insurer_id"] for row in rows if row.get("active_in_period", True)})
    return result


def actuarial(doc: dict, side: str, actor: dict, sector: str, cache: dict, bridge: ShockPlan | None = None) -> list[dict]:
    """Isolate existing per-VU actuarial contract at local ID 1; retain modern ID."""
    aid, n = actor["insurer_id"], doc["period_count"]
    source = deepcopy(actor["sectors"][sector]["source"])
    if sector == "life":
        source["assumptions"]["investment"] = {"mode": "insurer_rule_on_opening_backing_assets", "windows": [
            {"start_period": p, "end_period": p, "rate_per_period": profile(doc, side, aid, sector, p)[1]["rate_per_period"]} for p in range(1, n + 1)]}
        for p, row in enumerate(source["periods"], 1):
            if row.get("new_business"):
                raise ContractError("$.insurers", "AP5-Leben führt geschlossene Bestände, keine neue VN-Nachfrage")
            row["operating_expense_paid"] = money(Decimal(row["operating_expense_paid"]) + profile(doc, side, aid, sector, p)[3])
        stock = ("backing_assets", "guarantee_liability")
    else:
        health = source["sources"]
        health["pricing"]["windows"] = []
        for p, row in enumerate(source["periods"], 1):
            params, cost = profile(doc, side, aid, sector, p)[1::2]
            health["pricing"]["windows"].append({"start_period": p, "end_period": p, "amount_per_opening_policy": params["price_per_policy"]})
            for channel in ("new_business", "exits"):
                health[channel]["periods"][p - 1]["count"] = params[channel]
            row["operating_expense_paid"] = money(Decimal(row["operating_expense_paid"]) + cost)
        stock = ("cash", "benefit_liability")
    key = (sector, digest(source))
    if bridge is not None:
        source = bridge.actuarial_source(source, aid, sector)
        key = (sector, digest(source))
    if key not in cache:
        cache[key] = run_life_policy_period_chain(source) if sector == "life" else run_health_period_chain(source)
    report = cache[key]
    if report.issues:
        issue = report.issues[0]
        raise ContractError(f"$.VU{aid}.{sector}" + issue.path.removeprefix("$"), issue.message)
    rows = []
    for raw in report.to_dict()["rows"]:
        p = raw["period"]
        family, params, measures, cost = profile(doc, side, aid, sector, p)
        premium, investment, profit, expense = (Decimal(raw[k]) for k in ("premiums_collected", "investment_result", "period_profit", "operating_expense_paid"))
        paid = Decimal(raw["benefits_paid"]) if sector == "health" else Decimal(raw["death_benefits_paid"]) + Decimal(raw["maturity_benefits_paid"])
        quantity = Decimal(raw["opening_active_policies"])
        row = {"period": p, "insurer_id": aid, "insurance_group_id": actor["insurance_group_id"], "sector_id": sector,
               "family_id": family["family_id"], "rule": family["rule"], "parameters": params, "active_measures": measures,
               "information_period": p - 1, "source_contract": source["schema_version"],
               "source_digest": digest({"period_source": source["periods"][p - 1], "parameters": params}), "local_calculation_id": 1,
               "premium_income": money(premium), "investment_income": money(investment), "insurance_expense": money(premium + investment - expense - profit),
               "claims_paid": money(paid), "operating_expense": money(expense), "measure_cost": money(cost), "period_profit": money(profit),
               "covered_quantity": money(quantity), "quoted_price": params.get("price_per_policy"), "weighted_price": money(premium / quantity) if quantity else None,
               "capital_contribution": raw["capital_contribution"], "capital_distribution": raw["capital_distribution"]}
        for when in ("opening", "closing"):
            row.update({when + "_assets": raw[when + "_" + stock[0]], when + "_liabilities": raw[when + "_" + stock[1]], when + "_equity": raw[when + "_equity"]})
        if bridge is not None:
            row["measure_cost"] = money(cost + bridge.measure_cost(aid, sector, p))
            bridge.decorate(row)
        rows.append(row)
    return rows


def quote_offer(doc: dict, side: str, aid: int, sector: str, p: int) -> tuple:
    """The unchanged AP5 public quote and actor-bound draw contract."""
    family, params, measures, cost = profile(doc, side, aid, sector, p)
    draws = actor_draws(doc["seed"], aid, p)
    if family["rule"] == "vu.vrvu01":
        pf, af = float(params["premium_factor"]), float(params["advertising_factor"])
        calculated = apply_vu_random_uniform_rule(Insurer(aid, premiums_current_sector=[pf * .5] * 2, advertising_current_sector=[af * .5] * 2),
            VURandomUniformRuleParameters([pf] * 2, [af] * 2, [pf] * 2, [af] * 2), period=p, random_draws=draws, interest_rate=0)
        index = NON_LIFE.index(sector)
        price, ad = money(calculated.premiums_current_sector[index]), money(calculated.advertising_current_sector[index])
    else:
        price, ad = money(params["price"]), money(params["advertising"])
    return family, params, measures, cost, draws, price, ad


def side_result(doc: dict, side: str, actuarial_cache: dict | None = None, bridge: ShockPlan | None = None) -> dict:
    actors = sorted(doc["insurers"], key=lambda a: a["insurer_id"])
    if actuarial_cache is None:
        actuarial_cache = {}
    balances, closed, sources = {}, {}, []
    for actor in actors:
        aid = actor["insurer_id"]
        for sector, source in actor["sectors"].items():
            if sector in NON_LIFE:
                balances[(aid, sector)] = Balance(*(Decimal(source["opening"][key]) for key in ("assets", "liabilities", "equity")))
            else:
                closed[(aid, sector)] = actuarial(doc, side, actor, sector, actuarial_cache, bridge)
                sources.append({"insurer_id": aid, "sector_id": sector, "input_digest": digest(source["source"]), "adapter": "isolated_existing_actuarial_contract_id_1"})
    rows, decisions, market, families, peers, insurance_groups, snapshots = [], [], [], [], [], [], []
    owners = {c["group_id"]: c["initial_insurer_id"] for c in doc["customer_groups"]}
    for p in range(1, doc["period_count"] + 1):
        current = []
        for sector in NON_LIFE:
            offers, capacities, flows = {}, {}, {}
            for actor in actors:
                aid = actor["insurer_id"]
                if sector not in actor["sectors"]:
                    continue
                source = actor["sectors"][sector]
                family, params, measures, cost, draws, price, ad = quote_offer(doc, side, aid, sector, p)
                if bridge is not None:
                    price, ad = bridge.offer(aid, sector, p, price, ad)
                offers[aid] = price
                capacities[aid] = Decimal(params.get("capacity", source["capacity"]))
                flows[aid] = {"premium": Decimal(0), "loss": Decimal(0), "paid": Decimal(0), "quantity": Decimal(0),
                              "family": family, "params": params, "measures": measures, "cost": cost, "advertising": Decimal(ad), "draws": draws}
            for cohort in sorted(doc["customer_groups"], key=lambda c: c["group_id"]):
                if cohort["sector_id"] != sector:
                    continue
                quantity = Decimal(cohort["quantity"])
                previous_owner = owners[cohort["group_id"]]
                eligible = sorted(aid for aid in offers if capacities[aid] >= quantity)
                if bridge is not None:
                    owner, eligible = bridge.owner(cohort["group_id"], p)
                elif p == 1:
                    owner = cohort["initial_insurer_id"]
                    if owner is not None and owner not in eligible:
                        raise ContractError("$.customer_groups", "Anfangsvertrag überschreitet aktive Kapazität")
                elif eligible:
                    choice = apply_vn_best_info_insurance_rule(VNBestInfoInsuranceRuleParameters([float(cohort["insurance_threshold"])] * 2, [float(cohort["insurance_threshold"])] * 2),
                        period=p, market_damage_indicator=float(doc["damage_indicators"][p - 1]),
                        insurer_inputs=[{"insurer_id": aid, "premiums_current_sector": [float(offers[aid])] * 2} for aid in eligible])
                    owner = choice.decisions[0].insurer_id
                else:
                    owner = None
                risk = cohort["risk_periods"][p - 1]
                loss = Decimal(risk["loss"])
                premium = Decimal(money(quantity * Decimal(offers[owner]))) if owner is not None else Decimal(0)
                paid = Decimal(money(loss * Decimal(risk["paid_share"]))) if owner is not None else Decimal(0)
                if owner is not None:
                    capacities[owner] -= quantity
                    for key, val in (("premium", premium), ("loss", loss), ("paid", paid), ("quantity", quantity)):
                        flows[owner][key] += val
                owners[cohort["group_id"]] = owner
                decisions.append({"period": p, "sector_id": sector, "group_id": cohort["group_id"], "previous_insurer_id": previous_owner,
                                  "insurer_id": owner, "quantity": money(quantity), "insured": owner is not None,
                                  "premium_income": money(premium), "risk_loss": money(loss), "new_claims_paid": money(paid),
                                  "uninsured_loss": money(loss if owner is None else 0), "eligible_insurer_ids": eligible,
                                  "rule": "declared_initial_contract" if p == 1 else "vn.vrvn06_with_capacity_admission",
                                  "information_period": p, "information_scope": "current_public_offers_before_risk_booking"})
            for actor in actors:
                aid = actor["insurer_id"]
                if aid not in flows:
                    continue
                source = actor["sectors"][sector]
                flow, stock = flows[aid], balances[(aid, sector)]
                base = {key: Decimal(value) for key, value in source["periods"][p - 1].items() if key != "period"}
                extra = Decimal(0)
                if bridge is not None:
                    extra = bridge.extra_expense(aid, sector, p)
                    base["capital_contribution"] += bridge.capital(aid, p)
                if base["old_claims_paid"] > stock.liabilities:
                    raise ContractError(f"$.VU{aid}.{sector}.period{p}", "Altzahlung übersteigt die beim Träger verbliebene Anfangsverbindlichkeit")
                expense = base["operating_expense"] + flow["advertising"] + flow["cost"] + extra
                paid = flow["paid"] + base["old_claims_paid"]
                profit = flow["premium"] + base["investment_income"] - flow["loss"] - expense
                closing = Balance(stock.assets + flow["premium"] + base["investment_income"] + base["capital_contribution"] - paid - expense - base["capital_distribution"],
                                  stock.liabilities + flow["loss"] - paid,
                                  stock.equity + profit + base["capital_contribution"] - base["capital_distribution"])
                if closing.assets < 0 or closing.liabilities < 0 or closing.assets != closing.liabilities + closing.equity:
                    raise ContractError(f"$.VU{aid}.{sector}.period{p}", "Ungültiger Cash-/Reservebestand oder Bilanzidentität; kein Teilergebnis")
                row = {"period": p, "sector_id": sector, "insurer_id": aid, "insurance_group_id": actor["insurance_group_id"],
                       "family_id": flow["family"]["family_id"], "rule": flow["family"]["rule"], "parameters": flow["params"],
                       "active_measures": flow["measures"], "information_period": p - 1, "draws": flow["draws"],
                       "source_contract": "ims.modern-market.v1", "quoted_price": offers[aid], "covered_quantity": money(flow["quantity"]),
                       "weighted_price": money(flow["premium"] / flow["quantity"]) if flow["quantity"] else None,
                       "premium_income": money(flow["premium"]), "investment_income": money(base["investment_income"]), "insurance_expense": money(flow["loss"]),
                       "claims_paid": money(paid), "new_claims_paid": money(flow["paid"]), "old_claims_paid": money(base["old_claims_paid"]),
                       "operating_expense": money(expense), "advertising_expense": money(flow["advertising"]), "measure_cost": money(flow["cost"] + (bridge.measure_cost(aid, sector, p) if bridge else Decimal(0))),
                       "period_profit": money(profit), "capital_contribution": money(base["capital_contribution"]), "capital_distribution": money(base["capital_distribution"])}
                for when, values in (("opening", stock), ("closing", closing)):
                    row.update({when + "_" + key: money(getattr(values, key)) for key in ("assets", "liabilities", "equity")})
                if bridge is not None:
                    bridge.decorate(row)
                current.append(row)
                balances[(aid, sector)] = closing
        for (aid, sector), series in closed.items():
            current.append(series[p - 1])
        current.sort(key=lambda r: (r["insurer_id"], SECTORS.index(r["sector_id"])))
        rows.extend(current)
        for sector in (*SECTORS, "total"):
            subset = [r for r in current if sector == "total" or r["sector_id"] == sector]
            market.append(aggregate(subset, p, sector))
            for family in doc["families"]:
                families.append({"family_id": family["family_id"], **aggregate([r for r in subset if r["family_id"] == family["family_id"]], p, sector)})
            for peer in doc["peer_groups"]:
                peers.append({"group_id": peer["group_id"], **aggregate([r for r in subset if r["insurer_id"] in peer["insurer_ids"]], p, sector)})
            for gid in sorted({a["insurance_group_id"] for a in actors}):
                insurance_groups.append({"group_id": gid, **aggregate([r for r in subset if r["insurance_group_id"] == gid], p, sector)})
        now = next(r for r in market if r["period"] == p and r["sector_id"] == "total")
        snapshots.append({"period": p, "available_to_vu_decisions_in_period": p + 1,
                          "market": {key: now[key] for key in ("closing_assets", "closing_liabilities", "closing_equity", "period_profit")}})
    return {"vu_rows": rows, "market_rows": market, "family_rows": families, "peer_rows": peers,
            "insurance_group_rows": insurance_groups, "customer_decisions": decisions, "information_snapshots": snapshots, "actuarial_sources": sources}


def calculate(value: object) -> dict:
    try:
        with localcontext() as context:
            context.prec = 64
            doc = validate(value)
            actuarial_cache = {}
            sides = {side: side_result(doc, side, actuarial_cache) for side in ("baseline", "variant")}
            for key in ("vu_rows", "customer_decisions"):
                first = [[r for r in sides[side][key] if r["period"] <= 5] for side in ("baseline", "variant")]
                if first[0] != first[1]:
                    raise ContractError("$.measures", "Gemeinsamer tatsächlicher Anfang 1–5 erforderlich, einschließlich Kosten")
            core = {"schema_version": RESULT_VERSION, "source_input": deepcopy(doc), "input_digest": digest(doc),
                    "period_count": doc["period_count"], "sides": sides,
                    "limits": ["synthetic_or_declared_model_market", "no_new_life_demand", "no_market_ict_coupling", "no_cross_sector_funding", "no_dynamic_insolvency", "no_regulatory_capital"],
                    "historical_full_equality_claim": False, "regulatory_metrics": {"scr": None, "mcr": None, "coverage_ratio": None}}
            result = {**core, "valid": True, "issues": [], "content_digest": digest(core), "writes_performed": False, "partial_result_returned": False}
            response_bytes = len(json.dumps(wire_payload(result), ensure_ascii=False, separators=(",", ":")).encode("utf-8"))
            if response_bytes > MAX_RESULT_BYTES:
                raise ContractError("$", f"Vollständiges Marktergebnis ({response_bytes} Bytes) überschreitet {MAX_RESULT_BYTES // 1024**2} MiB; kein Teilergebnis")
            return result
    except (ContractError, ValueError, TypeError, KeyError, StopIteration, ArithmeticError, RecursionError) as exc:
        return {"schema_version": RESULT_VERSION, "valid": False, "issues": [{"path": getattr(exc, "path", "$"), "code": "market_contract_invalid", "message": str(exc) or "Unvollständiger Marktvertrag"}],
                "sides": {}, "content_digest": None, "writes_performed": False, "partial_result_returned": False}
