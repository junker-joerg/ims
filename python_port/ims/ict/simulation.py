"""Deterministic operational queue and model-equity workshop calculation.

No market runner, historical rule, filesystem or hidden random state is used.
Flows are independent declared processes, not a new endogenous market coupling.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP, localcontext

from ims.ict.contract import ContractError, Issue, RESULT_VERSION, digest, failure, validate


def amount(n: Decimal) -> str:
    return format(n.quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP), ".4f")


@dataclass(slots=True)
class Queue:
    original: Decimal
    rework: Decimal = Decimal(0)


def calculate(value: object) -> dict[str, object]:
    try:
        doc = validate(value)
    except ContractError as exc:
        return failure(exc.issues)
    with localcontext() as context:
        context.prec = 64
        return _calculate(doc)


def _calculate(doc: dict) -> dict[str, object]:
    hours = Decimal(doc["period_hours"])
    assets = {a["asset_id"]: a for a in doc["assets"]}
    services = sorted(doc["services"], key=lambda s: s["service_id"])
    insurers = sorted(doc["insurers"], key=lambda s: s["insurer_id"])
    events = sorted(doc["events"], key=lambda e: e["event_id"])
    strategies = sorted(doc["strategies"], key=lambda s: s["strategy_id"])
    dependencies: dict[str, set[str]] = {}

    def closure(key: str) -> set[str]:
        if key not in dependencies:
            dependencies[key] = {key} | set().union(*(closure(d) for d in assets[key]["depends_on"]))
        return dependencies[key]

    for key in assets:
        closure(key)
    service_assets = {s["service_id"]: set().union(*(closure(a) for a in s["asset_ids"])) for s in services}
    owners = {key: sorted({s["insurer_id"] for s in services if key in service_assets[s["service_id"]]}) for key in assets}
    unused = [s for s in strategies if not owners[s["asset_id"]]]
    if unused:
        return failure([Issue("$.strategies", "strategy_owner_missing", "Maßnahmenziel hat keinen verantwortlichen Service/VU")])
    # Each local restart shortens only the remaining affected event. It does not
    # repair a shared provider for other assets or invent a permanent fallback.
    effective_ends: dict[tuple[str, str], Decimal] = {}
    timeline: list[dict[str, object]] = []
    for e in events:
        start = Decimal(e["start_hour"])
        end = start + Decimal(e["duration_hours"])
        targets = [key for key, a in assets.items() if a["provider_id"] == e["target_id"]] if e["kind"] == "provider_outage" else [e["target_id"]]
        for key in sorted(targets):
            local_end = end
            for s in sorted(strategies, key=lambda s: (Decimal(s["start_hour"]), s["strategy_id"])):
                activation = max(start, Decimal(s["start_hour"]))
                if s["asset_id"] == key and s["kind"] == "restart" and activation < min(local_end, Decimal(s["through_hour"])):
                    local_end = activation + (local_end - activation) * (1 - Decimal(s["effectiveness"]))
            effective_ends[e["event_id"], key] = local_end
            timeline.append({"event_id": e["event_id"], "kind": e["kind"], "asset_id": key,
                             "provider_id": assets[key]["provider_id"], "start_hour": str(start),
                             "declared_end_hour": str(end), "effective_end_hour": str(local_end),
                             "start_day": str(start / 24), "declared_duration_days": str(Decimal(e["duration_hours"]) / 24),
                             "affected_insurer_ids": owners[key], "assumption_note": e["assumption_note"]})
    breaks = {Decimal(0), hours * doc["period_count"]}
    for e in events:
        breaks.update((Decimal(e["start_hour"]), Decimal(e["start_hour"]) + Decimal(e["duration_hours"])))
    breaks.update(effective_ends.values())
    for s in strategies:
        breaks.update((Decimal(s["start_hour"]), Decimal(s["through_hour"])))
    queues = {side: {s["service_id"]: Queue(Decimal(s["opening_backlog"])) for s in services} for side in ("baseline", "variant")}
    outputs = {side: {"service_rows": [], "balance_rows": []} for side in queues}
    equity_impact = {i["insurer_id"]: Decimal(0) for i in insurers}
    for period in range(1, doc["period_count"] + 1):
        lo, hi = (period - 1) * hours, period * hours
        points = [lo, *sorted(p for p in breaks if lo < p < hi), hi]
        totals = {side: {s["service_id"]: {"processed_original": Decimal(0), "processed_rework": Decimal(0),
                                        "rework_generated": Decimal(0), "capacity_units": Decimal(0)} for s in services} for side in queues}
        for left, right in zip(points, points[1:]):
            duration = right - left
            mid = (left + right) / 2
            asset_effects: dict[str, tuple[Decimal, Decimal]] = {}

            def effect(key: str) -> tuple[Decimal, Decimal]:
                if key in asset_effects:
                    return asset_effects[key]
                loss, rework = Decimal(0), Decimal(0)
                for e in events:
                    end = effective_ends.get((e["event_id"], key))
                    if end is None or not Decimal(e["start_hour"]) <= mid < end:
                        continue
                    severity = Decimal(1)
                    for s in strategies:
                        if s["asset_id"] == key and s["kind"] == "prevention" and Decimal(s["start_hour"]) <= Decimal(e["start_hour"]) and Decimal(s["start_hour"]) <= mid < Decimal(s["through_hour"]):
                            severity *= 1 - Decimal(s["effectiveness"])
                    loss = max(loss, Decimal(e["capacity_loss_fraction"]) * severity)
                    rework = max(rework, Decimal(e["rework_fraction"]) * severity)
                capacity = 1 - loss
                for dep in assets[key]["depends_on"]:
                    dep_capacity, dep_rework = effect(dep)
                    capacity, rework = min(capacity, dep_capacity), max(rework, dep_rework)
                for s in strategies:
                    if s["asset_id"] == key and s["kind"] == "fallback" and Decimal(s["start_hour"]) <= mid < Decimal(s["through_hour"]):
                        capacity = max(capacity, Decimal(s["effectiveness"]))
                asset_effects[key] = capacity, rework
                return capacity, rework

            for service in services:
                sid = service["service_id"]
                effects = [effect(a) for a in service["asset_ids"]]
                capacity_fraction = min(e[0] for e in effects)
                rework_fraction = max(e[1] for e in effects)
                arrivals = Decimal(service["demand_per_hour"]) * duration
                for side in queues:
                    fraction, rework_rate = (Decimal(1), Decimal(0)) if side == "baseline" else (capacity_fraction, rework_fraction)
                    q, t = queues[side][sid], totals[side][sid]
                    q.original += arrivals
                    generated = arrivals * rework_rate
                    q.rework += generated
                    capacity = Decimal(service["capacity_per_hour"]) * duration * fraction
                    original = min(capacity, q.original)
                    repair = min(capacity - original, q.rework)
                    q.original -= original
                    q.rework -= repair
                    for key, delta in (("processed_original", original), ("processed_rework", repair),
                                       ("rework_generated", generated), ("capacity_units", capacity)):
                        t[key] += delta
        losses = {i["insurer_id"]: Decimal(0) for i in insurers}
        strategy_costs = {i["insurer_id"]: Decimal(0) for i in insurers}
        for s in strategies:
            overlap = max(Decimal(0), min(hi, Decimal(s["through_hour"])) - max(lo, Decimal(s["start_hour"])))
            cost = Decimal(amount(overlap * Decimal(s["cost_per_hour"])))
            affected = owners[s["asset_id"]]
            share = Decimal(amount(cost / len(affected)))
            for index, owner in enumerate(affected):
                strategy_costs[owner] += cost - share * (len(affected) - 1) if index == len(affected) - 1 else share
        for s in services:
            sid, owner = s["service_id"], s["insurer_id"]
            b, v = totals["baseline"][sid], totals["variant"][sid]
            base_q, variant_q = queues["baseline"][sid], queues["variant"][sid]
            margin_delta = (b["processed_original"] - v["processed_original"]) * Decimal(s["unit_margin"])
            backlog_delta = variant_q.original + variant_q.rework - base_q.original
            expense = backlog_delta * Decimal(s["backlog_cost_per_unit_period"]) + v["rework_generated"] * Decimal(s["rework_cost_per_unit"])
            loss = Decimal(amount(margin_delta + expense))
            losses[owner] += loss
            for side in queues:
                q, t = queues[side][sid], totals[side][sid]
                outputs[side]["service_rows"].append({"period": period, "service_id": sid, "insurer_id": owner,
                    "process": s["process"], "arrivals": amount(Decimal(s["demand_per_hour"]) * hours),
                    **{k: amount(n) for k, n in t.items()}, "closing_original_backlog": amount(q.original),
                    "closing_rework_backlog": amount(q.rework), "closing_backlog": amount(q.original + q.rework),
                    "lost_margin": amount(margin_delta if side == "variant" else Decimal(0)),
                    "extra_expense": amount(expense if side == "variant" else Decimal(0)),
                    "operational_impact": amount(loss if side == "variant" else Decimal(0))})
        for i in insurers:
            owner = i["insurer_id"]
            profit, liability = Decimal(i["baseline_profit_per_period"]), Decimal(i["opening_liabilities"])
            loss = losses[owner] + strategy_costs[owner]
            equity_impact[owner] += loss
            for side in queues:
                impact = equity_impact[owner] if side == "variant" else Decimal(0)
                row_loss = loss if side == "variant" else Decimal(0)
                closing_assets = Decimal(i["opening_assets"]) + period * profit - impact
                equity = closing_assets - liability
                outputs[side]["balance_rows"].append({"period": period, "insurer_id": owner,
                    "period_profit": amount(profit - row_loss), "operational_impact": amount(row_loss),
                    "strategy_cost": amount(strategy_costs[owner] if side == "variant" else Decimal(0)),
                    "closing_assets": amount(closing_assets), "closing_liabilities": amount(liability),
                    "model_own_funds_proxy": amount(equity), "cumulative_operational_impact": amount(impact),
                    "loss_limit_met": row_loss <= Decimal(i["max_loss_per_period"]),
                    "equity_floor_met": equity >= Decimal(i["min_equity"])})
    concentration = [{"provider_id": p["provider_id"], "asset_ids": sorted(a for a, d in assets.items() if d["provider_id"] == p["provider_id"]),
                      "insurer_ids": sorted(set().union(*(set(owners[a]) for a, d in assets.items() if d["provider_id"] == p["provider_id"]))),
                      "assumption_note": p["assumption_note"]} for p in sorted(doc["providers"], key=lambda p: p["provider_id"])]
    core = {"schema_version": RESULT_VERSION, "scenario_id": doc["scenario_id"], "variant_id": doc["variant_id"],
            "input_digest": digest(doc), "period_count": doc["period_count"], "period_hours": doc["period_hours"],
            "amount_unit": "model_currency_unit_not_eur", **outputs, "timeline": timeline,
            "provider_concentration": concentration, "source_contract": doc,
            "assumption_note": doc["assumption_note"], "coupling_status": "independent_operational_queues_with_declared_balance_overlay",
            "regulatory_metrics": {key: None for key in ("scr", "mcr", "eligible_own_funds", "scr_coverage_ratio", "mcr_coverage_ratio")}}
    return {**core, "valid": True, "status": "ok", "content_digest": digest(core), "issues": [],
            "writes_performed": False, "runner_invoked": False, "ict_model_calculated": True,
            "historical_full_equality_claim": False, "compliance_decision_enabled": False}
