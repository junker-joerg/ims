"""AP7 physical graph, shared FIFO work budgets and explicit cost ledger."""
from __future__ import annotations

from collections import Counter, defaultdict, deque
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any

from ims.market.shock_contract import MAX_JOBS
from ims.strategies.modern_bridge import ContractError, money


def window(response: dict) -> tuple[Decimal, Decimal]:
    start = Decimal((response["decision_period"] + response["lead_periods"] - 1) * 24)
    return start, start + Decimal(response["duration_periods"] * 24)


def in_event(event: dict, hour: Decimal) -> bool:
    return Decimal(event["start_hour"]) <= hour < Decimal(event["start_hour"]) + Decimal(event["duration_hours"])


@dataclass(slots=True)
class Job:
    job_id: str
    service_id: str
    insurer_id: int
    sector_id: str
    kind: str
    created_period: int
    payload: dict = field(default_factory=dict)
    remaining_work: Decimal = Decimal(1)
    completed_hour: Decimal | None = None


class CostLedger:
    """One economic cost ID, distributed once; equity effect belongs to market."""
    def __init__(self) -> None:
        self.rows: list[dict] = []
        self.expenses: dict[tuple, Decimal] = defaultdict(Decimal)
        self.measures: dict[tuple, Decimal] = defaultdict(Decimal)
        self.seen: set[tuple] = set()

    def allocate(self, cost_id: str, period: int, amount: Decimal, owners: list[dict], kind: str, explanation: str) -> None:
        key = (cost_id, period)
        if key in self.seen:
            raise ContractError("$.costs", "Doppelte wirtschaftliche Kosten-ID")
        self.seen.add(key)
        total = Decimal(money(amount))
        if not total:
            return
        owners = sorted(owners, key=lambda owner: (owner["insurer_id"], owner["sector_id"]))
        weight_sum = sum((Decimal(owner["weight"]) for owner in owners), Decimal(0))
        if weight_sum != 1:
            raise ContractError("$.costs", "Explizite Gewichtssumme 1 erforderlich")
        remainder = total
        for index, owner in enumerate(owners):
            share = remainder if index == len(owners) - 1 else min(remainder, Decimal(money(total * Decimal(owner["weight"]))))
            remainder -= share
            target = (owner["insurer_id"], owner["sector_id"], period)
            self.expenses[target] += share
            if kind == "measure":
                self.measures[target] += share
            self.rows.append({"cost_id": cost_id, "period": period, "insurer_id": owner["insurer_id"],
                              "sector_id": owner["sector_id"], "kind": kind, "weight": owner["weight"],
                              "total_cost": money(total), "amount": money(share), "explanation": explanation})
        assert remainder == 0


class ProcessEngine:
    def __init__(self, bundle: dict, side: str, events: list[dict], responses: list[dict], ledger: CostLedger) -> None:
        self.bundle, self.side, self.events, self.responses, self.ledger = bundle, side, events, responses, ledger
        self.assets = {asset["asset_id"]: asset for asset in bundle["ict"]["assets"]}
        self.resources = {resource["resource_id"]: resource for resource in bundle["ict"]["resources"]}
        self.services = {service["service_id"]: service for service in bundle["ict"]["services"]}
        self.queues = {rid: deque() for rid in self.resources}
        self.job_count = 0
        self.process_rows: list[dict] = []
        self.resource_rows: list[dict] = []
        self.dependency_rows: list[dict] = []
        self.job_rows: list[dict] = []
        self._state_cache: dict[tuple, tuple] = {}
        self._path_cache: dict[str, list[str]] = {}

    def paths(self, key: str) -> list[str]:
        if key not in self._path_cache:
            result, pending = set(), [key]
            while pending:
                current = pending.pop()
                if current not in result:
                    result.add(current)
                    pending.extend(self.assets[current]["depends_on"])
            self._path_cache[key] = sorted(result)
        return self._path_cache[key]

    def state(self, key: str, hour: Decimal) -> tuple[Decimal, set[str]]:
        if (key, hour) in self._state_cache:
            return self._state_cache[(key, hour)]
        factor, causes = Decimal(1), set()
        for event in self.events:
            if "capacity" in event["channels"] and key in event["asset_ids"] and in_event(event, hour):
                factor = min(factor, 1 - Decimal(event["intensity"]))
                if Decimal(event["intensity"]) > 0:
                    causes.add(event["event_id"])
        for dependency in self.assets[key]["depends_on"]:
            other, inherited = self.state(dependency, hour)
            factor = min(factor, other)
            causes.update(inherited)
        self._state_cache[(key, hour)] = (factor, causes)
        return factor, causes

    def capacity(self, resource: dict, hour: Decimal) -> tuple[Decimal, list[str], list[dict]]:
        primary, causes = self.state(resource["asset_id"], hour)
        factor = primary
        staff_multiplier = Decimal(1)
        substitutes = []
        for response in self.responses:
            start, end = window(response)
            if response["asset_id"] != resource["asset_id"] or not start <= hour < end:
                continue
            if response["kind"] == "capacity":
                staff_multiplier = Decimal(response["value"])
            elif response["kind"] == "fallback":
                path = self.paths(response["replacement_asset_id"])
                available, fallback_causes = self.state(response["replacement_asset_id"], hour)
                unknown = any(self.assets[key]["control"] == "unknown" for key in path)
                if unknown:
                    available = Decimal(0)
                effective = available * Decimal(response["value"])
                factor = max(factor, effective)
                substitutes.append({"response_id": response["response_id"], "path": path,
                                    "available": money(available), "effective_factor": money(effective),
                                    "causes": sorted(fallback_causes), "unknown_control": unknown})
        # Capacity is the staff budget on either available path. Its position
        # in the JSON response list must not change the fallback's effect.
        return factor * staff_multiplier, sorted(causes), substitutes

    def period(self, period: int, arrivals: list[Job], active: set[int]) -> list[Job]:
        start, end = Decimal((period - 1) * 24), Decimal(period * 24)
        if period >= 6:
            for service in self.services.values():
                if service["kind"] != "underwriting" and service["insurer_id"] in active:
                    arrivals.extend(Job(f"P{period:03}_{service['service_id']}_{i:02}", service["service_id"],
                                        service["insurer_id"], service["sector_id"], service["kind"], period)
                                    for i in range(service["arrivals_per_period"]))
        self.job_count += len(arrivals)
        if self.job_count > MAX_JOBS:
            raise ContractError("$.ict", "40.000 Vorgänge überschritten; kein Teilergebnis")
        opening = Counter(job.service_id for queue in self.queues.values() for job in queue)
        count_arrivals: dict[str, int] = defaultdict(int)
        for job in sorted(arrivals, key=lambda job: job.job_id):
            service = self.services[job.service_id]
            self.queues[service["resource_id"]].append(job)
            count_arrivals[job.service_id] += 1
        edges = {start, end}
        for event in self.events:
            for edge in (Decimal(event["start_hour"]), Decimal(event["start_hour"]) + Decimal(event["duration_hours"])):
                if start < edge < end:
                    edges.add(edge)
        for response in self.responses:
            for edge in window(response):
                if start < edge < end:
                    edges.add(edge)
        edges = sorted(edges)
        completed: list[Job] = []
        capacity_work: dict[str, Decimal] = defaultdict(Decimal)
        actual_work: dict[str, Decimal] = defaultdict(Decimal)
        lost_hours: dict[str, Decimal] = defaultdict(Decimal)
        asset_hours: dict[str, Decimal] = defaultdict(Decimal)
        asset_causes: dict[str, set] = defaultdict(set)
        fallback_details: dict[str, list] = defaultdict(list)
        capacity_segments: dict[str, list] = defaultdict(list)
        holding: dict[tuple, Decimal] = defaultdict(Decimal)
        for left, right in zip(edges, edges[1:]):
            duration = right - left
            for key in self.assets:
                factor, causes = self.state(key, left)
                asset_hours[key] += duration * (1 - factor)
                asset_causes[key].update(causes)
            for rid, resource in self.resources.items():
                factor, causes, replacements = self.capacity(resource, left)
                rate = Decimal(resource["capacity_per_hour"]) * factor
                capacity_segments[rid].append({"from_hour": money(left), "through_hour": money(right),
                    "effective_factor": money(factor), "capacity_per_hour": money(rate), "causing_event_ids": causes,
                    "active_response_ids": [response["response_id"] for response in self.responses
                        if response["asset_id"] == resource["asset_id"] and window(response)[0] <= left < window(response)[1]],
                    "replacements": replacements})
                budget = rate * duration
                capacity_work[rid] += budget
                lost_hours[rid] += duration * max(Decimal(0), 1 - min(Decimal(1), factor))
                if replacements:
                    fallback_details[rid].append({"from_hour": money(left), "through_hour": money(right),
                                                  "primary_causes": causes, "effective_factor": money(factor), "replacements": replacements})
                queue, cursor = self.queues[rid], left
                initial_jobs = list(queue)
                # A partially completed unit retains its progress over event edges.
                while queue and rate and cursor < right:
                    job = queue[0]
                    required_time = job.remaining_work / rate
                    available_time = right - cursor
                    used = min(required_time, available_time)
                    work = rate * used
                    actual_work[rid] += work
                    job.remaining_work = Decimal(0) if required_time <= available_time else job.remaining_work - work
                    cursor += used
                    if job.remaining_work == 0:
                        queue.popleft()
                        job.completed_hour = cursor
                        completed.append(job)
                        self.job_rows.append({"job_id": job.job_id, "service_id": job.service_id, "insurer_id": job.insurer_id,
                                              "sector_id": job.sector_id, "kind": job.kind, "created_period": job.created_period,
                                              "completed_period": period, "completed_hour": money(cursor),
                                              "contract_effective_period": period + 1 if job.kind in ("life_application", "switch") else None,
                                              "insurance_payment_delayed": False})
                for waiting in initial_jobs:
                    holding[(waiting.insurer_id, waiting.sector_id)] += (waiting.completed_hour if waiting.completed_hour is not None else right) - left
        for (aid, sector), hours in sorted(holding.items()):
            self.ledger.allocate(f"holding_VU{aid}_{sector}", period, hours * Decimal(self.bundle["ict"]["holding_cost_per_job_hour"]),
                                 [{"insurer_id": aid, "sector_id": sector, "weight": "1"}], "operation", "Tatsächliche Vorgangsstunden bis Bearbeitung; kein zweiter Margenverlust")
        for rid, resource in self.resources.items():
            self.ledger.allocate("resource_" + rid, period, Decimal(resource["cost_per_hour"]) * 24,
                                 resource["owners"], "operation", "Deklarierter Ressourcenaufwand auch ohne Schock")
            self.resource_rows.append({"period": period, "resource_id": rid, "asset_id": resource["asset_id"],
                                       "capacity_work": money(capacity_work[rid]), "processed_work": money(actual_work[rid]),
                                       "lost_equivalent_hours": money(lost_hours[rid]), "closing_queue": len(self.queues[rid]),
                                       "fallback_segments": fallback_details[rid], "capacity_segments": capacity_segments[rid], "shared_budget": True})
        done_counts = Counter(job.service_id for job in completed)
        closing_counts = Counter(job.service_id for queue in self.queues.values() for job in queue)
        for sid, service in self.services.items():
            done, closing = done_counts[sid], closing_counts[sid]
            assert opening[sid] + count_arrivals[sid] == done + closing
            self.process_rows.append({"period": period, "service_id": sid, "insurer_id": service["insurer_id"],
                                      "sector_id": service["sector_id"], "kind": service["kind"], "resource_id": service["resource_id"],
                                      "opening_queue": opening[sid], "arrivals": count_arrivals[sid], "completed": done,
                                      "closing_queue": closing, "insurance_payments_delayed": False, "rework": 0})
        for key, asset in self.assets.items():
            self.dependency_rows.append({"period": period, "asset_id": key, "label": asset["label"], "control": asset["control"],
                                         "depends_on": asset["depends_on"], "transitive_path": self.paths(key),
                                         "lost_equivalent_hours": money(asset_hours[key]), "causing_event_ids": sorted(asset_causes[key])})
        return completed

    def terminal(self) -> list[dict]:
        return [{"job_id": job.job_id, "service_id": job.service_id, "insurer_id": job.insurer_id, "sector_id": job.sector_id,
                 "kind": job.kind, "created_period": job.created_period, "remaining_work": money(job.remaining_work),
                 "status": "waiting", "not_a_permanent_loss": True} for queue in self.queues.values() for job in queue]
