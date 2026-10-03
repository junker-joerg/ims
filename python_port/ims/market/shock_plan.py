"""Period-causal AP7 requests, shared physical processing and market bridge."""
from __future__ import annotations

from collections import defaultdict
from copy import deepcopy
from decimal import Decimal, ROUND_FLOOR

from ims.market.contract import NON_LIFE, SECTORS
from ims.market.runner import quote_offer
from ims.market.shock_life import add_policies
from ims.market.shock_process import CostLedger, Job, ProcessEngine, in_event, window
from ims.model.vn_insurance_rules import VNBestInfoInsuranceRuleParameters, apply_vn_best_info_insurance_rule
from ims.strategies.modern_bridge import ContractError, money


def equal_owners(actors: dict, ids: list[int], preferred_sector: str | None = None) -> list[dict]:
    weights = [Decimal(money(Decimal(1) / len(ids)))] * len(ids)
    weights[-1] = 1 - sum(weights[:-1], Decimal(0))
    return [{"insurer_id": aid, "sector_id": preferred_sector if preferred_sector in actors[aid]["sectors"] else min(actors[aid]["sectors"], key=SECTORS.index),
             "weight": money(weight)} for aid, weight in zip(sorted(ids), weights)]


class ShockPlan:
    """Compute process actions before booking; no future risk values inform choice."""
    def __init__(self, bundle: dict, side: str) -> None:
        self.bundle, self.side = bundle, side
        self.market = bundle["model_input"]
        self.model_side = "variant" if bundle["comparison"] == "no_shock_vs_shock" else side
        self.events = [] if side == "baseline" and bundle["comparison"] == "no_shock_vs_shock" else bundle["events"]
        self.responses = bundle["responses"][self.model_side]
        self.actors = {actor["insurer_id"]: actor for actor in self.market["insurers"]}
        self.activations = {item["insurer_id"]: item for item in bundle["activation"]}
        self.life_offers = {offer["insurer_id"]: offer for offer in bundle["life"]["offers"]}
        self.ledger = CostLedger()
        self.engine = ProcessEngine(bundle, side, self.events, self.responses, self.ledger)
        self.services = {(service["insurer_id"], service["sector_id"], service["kind"]): service["service_id"] for service in bundle["ict"]["services"]}
        self.decisions: dict[tuple, tuple] = {}
        self.issues: list[dict] = []
        self.life_rows: list[dict] = []
        self.switch_rows: list[dict] = []
        self.event_rows: list[dict] = []
        self.pending: list[Job] = []
        self._build()

    def active(self, aid: int, period: int) -> bool:
        if aid not in self.activations:
            return True
        activation = self.activations[aid]
        event = next((event for event in self.events if event["event_id"] == activation["event_id"]), None)
        return event is not None and Decimal((period - 1) * 24) >= Decimal(event["start_hour"])

    def capital(self, aid: int, period: int) -> Decimal:
        if aid not in self.activations or not self.active(aid, period) or self.active(aid, period - 1):
            return Decimal(0)
        return Decimal(self.activations[aid]["capital"])

    def offer(self, aid: int, sector: str, period: int, price: str, advertising: str) -> tuple[str, str]:
        if not self.active(aid, period):
            return "0.0000", "0.0000"
        for response in self.responses:
            start, end = window(response)
            hour = Decimal((period - 1) * 24)
            if response["kind"] == "price" and sector == "motor" and aid in response["insurer_ids"] and start <= hour < end:
                # The accepted price reply is triggered by the declared entry.
                if any(event["kind"] == "entry" and Decimal(event["start_hour"]) <= hour for event in self.events):
                    price = money(response["value"])
        return price, advertising

    def _public_offers(self, sector: str, period: int) -> tuple[dict, dict]:
        offers, capacities = {}, {}
        for aid, actor in sorted(self.actors.items()):
            if sector not in actor["sectors"] or not self.active(aid, period):
                continue
            family, params, measures, cost, draws, price, ad = quote_offer(self.market, self.model_side, aid, sector, period)
            offers[aid] = self.offer(aid, sector, period, price, ad)[0]
            capacities[aid] = Decimal(params.get("capacity", actor["sectors"][sector]["capacity"]))
        return offers, capacities

    def _choice(self, cohort: dict, period: int, eligible: list[int], offers: dict) -> int | None:
        if not eligible:
            return None
        params = VNBestInfoInsuranceRuleParameters([float(cohort["insurance_threshold"])] * 2, [float(cohort["insurance_threshold"])] * 2)
        result = apply_vn_best_info_insurance_rule(params, period=period, market_damage_indicator=float(self.market["damage_indicators"][period - 1]),
            insurer_inputs=[{"insurer_id": aid, "premiums_current_sector": [float(offers[aid])] * 2} for aid in eligible])
        return result.decisions[0].insurer_id

    def _request_switches(self, period: int, owners: dict, outstanding: dict) -> list[Job]:
        jobs = []
        for sector in NON_LIFE:
            offers, capacities = self._public_offers(sector, period)
            cohorts = sorted((cohort for cohort in self.market["customer_groups"] if cohort["sector_id"] == sector), key=lambda cohort: cohort["group_id"])
            if period >= 6:
                for cohort in cohorts:
                    owner = owners[cohort["group_id"]]
                    if owner in capacities:
                        capacities[owner] -= Decimal(cohort["quantity"])
                for job in outstanding.values():
                    if job.sector_id == sector and job.payload["target"] in capacities:
                        capacities[job.payload["target"]] -= Decimal(job.payload["quantity"])
            for cohort in cohorts:
                gid, quantity = cohort["group_id"], Decimal(cohort["quantity"])
                eligible = sorted(aid for aid in offers if capacities[aid] + (quantity if period >= 6 and owners[gid] == aid else 0) >= quantity
                                  and (aid not in self.activations or gid in self.activations[aid]["reachable_group_ids"]))
                if period <= 5:
                    owner = cohort["initial_insurer_id"] if period == 1 else self._choice(cohort, period, eligible, offers)
                    if owner is not None:
                        capacities[owner] -= quantity
                    owners[gid] = owner
                elif gid not in outstanding:
                    target = self._choice(cohort, period, eligible, offers)
                    if target != owners[gid]:
                        process_owner = target if target is not None else owners[gid]
                        sid = self.services.get((process_owner, sector, "underwriting"))
                        if sid is None:
                            raise ContractError("$.ict.services", "Wirksamer Prozess für jeden beantragten Vertragswechsel erforderlich")
                        job = Job(f"P{period:03}_W_{gid}", sid, process_owner, sector, "switch", period,
                                  {"group_id": gid, "previous": owners[gid], "target": target, "quantity": money(quantity)})
                        jobs.append(job)
                        outstanding[gid] = job
                        if target is not None:
                            capacities[target] -= quantity
                self.decisions[(gid, period)] = (owners[gid], eligible)
        return jobs

    def _request_life(self, period: int, outstanding: dict) -> tuple[list[Job], dict]:
        pool = self.bundle["life"]["pool_per_period"] if period >= self.bundle["life"]["start_period"] else 0
        hour, factor = Decimal((period - 1) * 24), Decimal(1)
        for event in self.events:
            if event["kind"] == "life_demand" and in_event(event, hour):
                factor = min(factor, 1 - Decimal(event["intensity"]))
        for response in self.responses:
            start, end = window(response)
            if response["kind"] == "life_attractiveness" and start <= hour < end:
                factor = max(factor, Decimal(response["value"]))
        willing = int((pool * factor).to_integral_value(rounding=ROUND_FLOOR))
        capacities = {aid: offer["admission_per_period"] for aid, offer in self.life_offers.items() if self.active(aid, period)}
        live = defaultdict(int)
        for issue in self.issues:
            if issue["issue_period"] <= period <= issue["maturity_period"]:
                live[issue["insurer_id"]] += 1
        for job in outstanding.values():
            live[job.insurer_id] += 1
        jobs = []
        for index in range(willing):
            eligible = [aid for aid, capacity in capacities.items() if capacity > 0 and live[aid] + len(self.actors[aid]["sectors"]["life"]["source"]["opening"]["policies"]) < 100]
            if not eligible:
                break
            aid = min(eligible, key=lambda key: (Decimal(self.life_offers[key]["premium"]), key))
            sid = self.services[(aid, "life", "underwriting")]
            job = Job(f"P{period:03}_L_{index:02}", sid, aid, "life", "life_application", period)
            capacities[aid] -= 1
            live[aid] += 1
            outstanding[job.job_id] = job
            jobs.append(job)
        return jobs, {"period": period, "pool": pool, "attractiveness": money(factor), "willing": willing,
                      "not_interested": pool - willing, "applications_created": len(jobs), "no_offer_capacity": willing - len(jobs)}

    def _book_declared_costs(self, period: int) -> None:
        for response in self.responses:
            sector = "life" if response["kind"] == "life_attractiveness" else "motor" if response["kind"] == "price" else None
            owners = equal_owners(self.actors, response["insurer_ids"], sector)
            if response["kind"] in ("fallback", "capacity"):
                resource = next(resource for resource in sorted(self.engine.resources.values(), key=lambda item: item["resource_id"]) if resource["asset_id"] == response["asset_id"])
                if {owner["insurer_id"] for owner in resource["owners"]} == set(response["insurer_ids"]):
                    owners = resource["owners"]
            if response["decision_period"] == period:
                self.ledger.allocate("decision_" + response["response_id"], period, Decimal(response["cost"]), owners, "measure", "Beschlossene Vorsorgekosten bleiben auch ohne Schock")
            start, end = window(response)
            hours = max(Decimal(0), min(Decimal(period * 24), end) - max(Decimal((period - 1) * 24), start))
            self.ledger.allocate("upkeep_" + response["response_id"], period, hours * Decimal(response["cost_per_hour"]), owners, "measure", "Tatsächlich aktives Maßnahmenfenster")
        for event in self.events:
            event_period = int(Decimal(event["start_hour"]) // 24) + 1
            if event_period == period:
                owners = equal_owners(self.actors, event["insurer_ids"])
                explanation = "Ereigniskosten einmal mit gleichen Akteursgewichten in der ersten vorhandenen Modellsparte; keine Pfad-Doppelbuchung"
                for resource in sorted(self.engine.resources.values(), key=lambda item: item["resource_id"]):
                    if set(event["asset_ids"]) & set(self.engine.paths(resource["asset_id"])) and {owner["insurer_id"] for owner in resource["owners"]} == set(event["insurer_ids"]):
                        owners = resource["owners"]
                        explanation = "Ereigniskosten genau einmal nach erklärten Ressourcen-Kostenträgern; keine Pfad-Doppelbuchung"
                        break
                self.ledger.allocate("event_" + event["event_id"], period, Decimal(event["cost"]), owners, "operation", explanation)

    def _build(self) -> None:
        owners = {cohort["group_id"]: cohort["initial_insurer_id"] for cohort in self.market["customer_groups"]}
        switches, applications = {}, {}
        for period in range(1, self.market["period_count"] + 1):
            issued = 0
            for job in self.pending:
                if job.kind == "switch":
                    gid = job.payload["group_id"]
                    owners[gid] = job.payload["target"]
                    switches.pop(gid)
                    self.switch_rows.append({"job_id": job.job_id, "period": period, "group_id": gid, "previous_insurer_id": job.payload["previous"],
                                             "insurer_id": job.payload["target"], "request_period": job.created_period, "effective_period": period,
                                             "quantity": job.payload["quantity"], "risk_duplicated": False})
                elif job.kind == "life_application":
                    applications.pop(job.job_id)
                    self.issues.append({"policy_id": "AP7_" + job.job_id, "job_id": job.job_id, "insurer_id": job.insurer_id,
                                        "request_period": job.created_period, "issue_period": period,
                                        "maturity_period": period + self.life_offers[job.insurer_id]["term_periods"],
                                        "premium": self.life_offers[job.insurer_id]["premium"], "allocation": self.life_offers[job.insurer_id]["allocation"]})
                    issued += 1
            arrivals = self._request_switches(period, owners, switches)
            life_jobs, life_row = self._request_life(period, applications)
            arrivals.extend(life_jobs)
            self._book_declared_costs(period)
            active = {aid for aid in self.actors if self.active(aid, period)}
            completed = self.engine.period(period, arrivals, active)
            self.pending = [job for job in completed if job.kind in ("switch", "life_application")]
            life_row.update(issued=issued, waiting_applications=len(applications) - sum(job.kind == "life_application" for job in self.pending),
                            processed_pending_next_period=sum(job.kind == "life_application" for job in self.pending),
                            cumulative_issued=len(self.issues), old_guarantees_preserved_by_shock=True)
            self.life_rows.append(life_row)
            left, right = Decimal((period - 1) * 24), Decimal(period * 24)
            for event in self.events:
                hours = max(Decimal(0), min(right, Decimal(event["start_hour"]) + Decimal(event["duration_hours"])) - max(left, Decimal(event["start_hour"])))
                if hours:
                    self.event_rows.append({"period": period, "event_id": event["event_id"], "kind": event["kind"], "start_hour": event["start_hour"],
                                            "duration_hours": event["duration_hours"], "overlap_hours": money(hours), "intensity": event["intensity"],
                                            "insurer_ids": event["insurer_ids"], "asset_ids": event["asset_ids"], "channels": event["channels"], "assumption_note": event["assumption_note"]})

    def owner(self, group_id: str, period: int) -> tuple:
        return self.decisions[(group_id, period)]

    def extra_expense(self, aid: int, sector: str, period: int) -> Decimal:
        return self.ledger.expenses[(aid, sector, period)]

    def measure_cost(self, aid: int, sector: str, period: int) -> Decimal:
        return self.ledger.measures[(aid, sector, period)]

    def actuarial_source(self, source: dict, aid: int, sector: str) -> dict:
        for row in source["periods"]:
            row["operating_expense_paid"] = money(Decimal(row["operating_expense_paid"]) + self.extra_expense(aid, sector, row["period"]))
        return add_policies(source, self.issues, self.life_offers, aid) if sector == "life" else source

    def decorate(self, row: dict) -> None:
        aid, sector, period = row["insurer_id"], row["sector_id"], row["period"]
        row.update(active_in_period=self.active(aid, period), process_and_response_cost=money(self.extra_expense(aid, sector, period)),
                   market_ict_margin_double_deduction=False, ap7_new_policies=sum(item["insurer_id"] == aid and item["issue_period"] == period for item in self.issues) if sector == "life" else 0)
        if not row["active_in_period"]:
            row["quoted_price"] = None

    def tables(self) -> dict:
        pending = [{"job_id": job.job_id, "service_id": job.service_id, "insurer_id": job.insurer_id, "sector_id": job.sector_id,
                    "kind": job.kind, "created_period": job.created_period, "remaining_work": "0.0000",
                    "status": "processed_pending_next_period", "not_a_permanent_loss": True} for job in self.pending]
        return {"ict_process_rows": self.engine.process_rows, "ict_resource_rows": self.engine.resource_rows,
                "ict_dependency_rows": self.engine.dependency_rows, "ict_event_rows": self.event_rows,
                "ict_job_rows": self.engine.job_rows, "cost_rows": self.ledger.rows, "life_demand_rows": self.life_rows,
                "life_contract_rows": self.issues, "switch_process_rows": self.switch_rows,
                "terminal_process_rows": self.engine.terminal() + pending}
