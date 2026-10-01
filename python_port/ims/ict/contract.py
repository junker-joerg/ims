"""Bounded, explicit service/asset/provider and event/time workshop contract."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import asdict, dataclass
from decimal import Decimal

INPUT_VERSION = "ims.ict-workshop-input.v1"
RESULT_VERSION = "ims.ict-workshop-result.v1"
PROCESSES = ("sales", "underwriting", "claims", "service")
EVENT_KINDS = ("outage", "capacity_loss", "data_integrity", "provider_outage")
STRATEGY_KINDS = ("prevention", "restart", "fallback")
FIELDS = {
    "root": {"schema_version", "scenario_id", "variant_id", "source_kind", "assumption_note",
             "period_hours", "period_count", "providers", "assets", "services", "insurers", "events", "strategies"},
    "providers": {"provider_id", "assumption_note"},
    "assets": {"asset_id", "provider_id", "depends_on", "assumption_note"},
    "services": {"service_id", "insurer_id", "process", "asset_ids", "demand_per_hour", "capacity_per_hour",
                 "unit_margin", "backlog_cost_per_unit_period", "rework_cost_per_unit", "opening_backlog", "assumption_note"},
    "insurers": {"insurer_id", "opening_assets", "opening_liabilities", "baseline_profit_per_period",
                 "max_loss_per_period", "min_equity", "assumption_note"},
    "events": {"event_id", "kind", "target_id", "start_hour", "duration_hours", "capacity_loss_fraction",
               "rework_fraction", "assumption_note"},
    "strategies": {"strategy_id", "kind", "asset_id", "start_hour", "through_hour", "effectiveness",
                   "cost_per_hour", "assumption_note"},
}
ID_FIELDS = {"providers": "provider_id", "assets": "asset_id", "services": "service_id",
             "insurers": "insurer_id", "events": "event_id", "strategies": "strategy_id"}
LIMITS = {"providers": 20, "assets": 40, "services": 40, "insurers": 25, "events": 20, "strategies": 20}
_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}\Z")
_AMOUNT = re.compile(r"(?:0|[1-9][0-9]{0,11})(?:\.[0-9]{1,4})?\Z")


@dataclass(frozen=True, slots=True)
class Issue:
    path: str
    code: str
    message: str


class ContractError(ValueError):
    def __init__(self, issues: list[Issue]):
        self.issues = tuple(issues)
        super().__init__(issues[0].message)


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def failure(issues: tuple[Issue, ...] | list[Issue]) -> dict[str, object]:
    return {"schema_version": RESULT_VERSION, "valid": False, "status": "error", "content_digest": None,
            "issues": [asdict(i) for i in issues], "baseline": None, "variant": None,
            "partial_result_returned": False, "writes_performed": False, "runner_invoked": False,
            "ict_model_calculated": False, "compliance_decision_enabled": False}


def contract_payload() -> dict[str, object]:
    return {"input_schema_version": INPUT_VERSION, "result_schema_version": RESULT_VERSION,
            "source_kind": "declared_workshop_not_historical_or_regulatory", "max_periods": 100,
            "limits": LIMITS, "processes": PROCESSES, "event_kinds": EVENT_KINDS, "strategy_kinds": STRATEGY_KINDS,
            "time_interval": "half_open_hours_start_inclusive_end_exclusive",
            "day_hours": "24", "period_hours": "explicit_required_not_inferred_from_ESS",
            "amount_unit": "model_currency_unit_not_eur", "writes_enabled": False,
            "historical_runner_enabled": False, "compliance_decision_enabled": False,
            "calculation_endpoint": "/api/ict/calculate", "validation_endpoint": "/api/ict/validate",
            "fields": {k: sorted(v) for k, v in FIELDS.items()}}


def validate(value: object) -> dict:
    """Validate the whole bounded document before any result is produced."""
    issues: list[Issue] = []

    def issue(path: str, code: str, message: str) -> None:
        issues.append(Issue(path, code, message))

    def exact(obj: object, kind: str, path: str) -> bool:
        if type(obj) is not dict:
            issue(path, "object_required", "Objekt erforderlich")
            return False
        for key in sorted(FIELDS[kind] - obj.keys()):
            issue(f"{path}.{key}", "field_missing", "Pflichtfeld fehlt")
        for key in obj.keys() - FIELDS[kind]:
            issue(path, "field_unknown", f"Unbekanntes Feld: {key}")
        return True

    def text(item: object, path: str, identifier: bool = False) -> None:
        valid = type(item) is str and item == item.strip() and item.isprintable()
        valid = valid and (bool(_ID.fullmatch(item)) if identifier else 1 <= len(item) <= 400)
        if not valid:
            issue(path, "text_invalid", "Benannter druckbarer Text erforderlich")

    def number(item: object, path: str, maximum: Decimal = Decimal("999999999999"), positive: bool = False) -> Decimal:
        if type(item) is not str or not _AMOUNT.fullmatch(item):
            issue(path, "decimal_string_required", "Nichtnegativer Dezimaltext mit höchstens vier Nachkommastellen erforderlich")
            return Decimal(0)
        n = Decimal(item)
        if n > maximum or (positive and n == 0):
            issue(path, "number_out_of_range", "Zahl außerhalb des zulässigen Bereichs")
        return n

    if not exact(value, "root", "$"):
        raise ContractError(issues)
    if value.get("schema_version") != INPUT_VERSION:
        issue("$.schema_version", "version_mismatch", "Unbekannter ICT-Vertrag")
    if value.get("source_kind") != "declared_workshop_not_historical_or_regulatory":
        issue("$.source_kind", "source_kind_invalid", "Ausdrückliche Workshop-Quelle erforderlich")
    for field in ("scenario_id", "variant_id"):
        text(value.get(field), f"$.{field}", True)
    text(value.get("assumption_note"), "$.assumption_note")
    hours = number(value.get("period_hours"), "$.period_hours", Decimal(8760), True)
    count = value.get("period_count")
    if type(count) is not int or not 1 <= count <= 100:
        issue("$.period_count", "period_count_invalid", "1 bis 100 vollständige Perioden erforderlich")
    registries: dict[str, dict] = {}
    for kind, limit in LIMITS.items():
        rows = value.get(kind)
        minimum = 0 if kind in ("events", "strategies") else 1
        if type(rows) is not list or not minimum <= len(rows) <= limit:
            issue(f"$.{kind}", "row_limit_invalid", f"{minimum} bis {limit} Einträge erforderlich")
            rows = []
        registry: dict = {}
        registries[kind] = registry
        for index, row in enumerate(rows):
            path = f"$.{kind}[{index}]"
            if not exact(row, kind, path):
                continue
            key = row.get(ID_FIELDS[kind])
            if kind == "insurers":
                if type(key) is not int or not 1 <= key <= 25:
                    issue(path + ".insurer_id", "insurer_invalid", "VU-ID 1 bis 25 erforderlich")
            else:
                text(key, path + "." + ID_FIELDS[kind], True)
            text(row.get("assumption_note"), path + ".assumption_note")
            if type(key) not in (str, int):
                continue
            if key in registry:
                issue(path, "id_duplicate", "ID mehrfach vergeben")
            registry[key] = row
    # Stop before reference traversal if structural fields are malformed.
    if issues:
        raise ContractError(issues)
    assets, providers = registries["assets"], registries["providers"]
    insurers = registries["insurers"]
    for index, row in enumerate(value["assets"]):
        path = f"$.assets[{index}]"
        if type(row["provider_id"]) is not str or row["provider_id"] not in providers:
            issue(path + ".provider_id", "provider_unknown", "Anbieter nicht deklariert")
        deps = row["depends_on"]
        if type(deps) is not list or len(deps) > 40 or any(type(x) is not str for x in deps):
            issue(path + ".depends_on", "dependencies_invalid", "Liste benannter Abhängigkeiten erforderlich")
        elif len(set(deps)) != len(deps) or any(x not in assets for x in deps):
            issue(path + ".depends_on", "dependency_unknown_or_duplicate", "Abhängigkeit unbekannt oder doppelt")
    for index, row in enumerate(value["services"]):
        path = f"$.services[{index}]"
        if type(row["insurer_id"]) is not int or row["insurer_id"] not in insurers:
            issue(path + ".insurer_id", "insurer_unknown", "Service-Verantwortlicher nicht deklariert")
        if row["process"] not in PROCESSES:
            issue(path + ".process", "process_unknown", "Unbekannter Geschäftsprozess")
        ids = row["asset_ids"]
        if type(ids) is not list or not 1 <= len(ids) <= 40 or any(type(x) is not str for x in ids):
            issue(path + ".asset_ids", "assets_invalid", "Mindestens eine benannte ICT-Abhängigkeit erforderlich")
        elif len(set(ids)) != len(ids) or any(x not in assets for x in ids):
            issue(path + ".asset_ids", "asset_unknown_or_duplicate", "ICT-Abhängigkeit unbekannt oder doppelt")
        for field in ("demand_per_hour", "capacity_per_hour", "unit_margin", "backlog_cost_per_unit_period", "rework_cost_per_unit"):
            number(row[field], path + "." + field, Decimal(1000))
        number(row["opening_backlog"], path + ".opening_backlog", Decimal(1000000))
    for index, row in enumerate(value["insurers"]):
        path = f"$.insurers[{index}]"
        for field in ("opening_assets", "opening_liabilities", "baseline_profit_per_period", "max_loss_per_period", "min_equity"):
            number(row[field], path + "." + field)
    horizon_hours = hours * 100  # permits a stable shorter prefix with future events still declared
    for index, row in enumerate(value["events"]):
        path = f"$.events[{index}]"
        kind = row["kind"]
        if type(kind) is not str or kind not in EVENT_KINDS:
            issue(path + ".kind", "event_kind_unknown", "Unbekannter Ereignistyp")
        targets = providers if kind == "provider_outage" else assets
        if type(row["target_id"]) is not str or row["target_id"] not in targets:
            issue(path + ".target_id", "target_unknown", "Ereignisziel nicht deklariert")
        start = number(row["start_hour"], path + ".start_hour", horizon_hours)
        duration = number(row["duration_hours"], path + ".duration_hours", horizon_hours, True)
        loss = number(row["capacity_loss_fraction"], path + ".capacity_loss_fraction", Decimal(1))
        rework = number(row["rework_fraction"], path + ".rework_fraction", Decimal(1))
        if start + duration > horizon_hours:
            issue(path, "time_out_of_range", "Ereignis überschreitet den begrenzten Zeitvertrag")
        if kind == "data_integrity" and (loss != 0 or rework == 0):
            issue(path, "integrity_semantics_invalid", "Datenintegrität erfordert Nacharbeit ohne impliziten Kapazitätsausfall")
        if kind != "data_integrity" and rework != 0:
            issue(path, "rework_not_declared_integrity", "Nacharbeit benötigt einen getrennten Datenintegritätsfall")
        if kind in ("outage", "provider_outage") and loss != 1:
            issue(path, "outage_semantics_invalid", "Vollausfall benötigt Verlustanteil 1")
        if kind == "capacity_loss" and not 0 < loss < 1:
            issue(path, "capacity_semantics_invalid", "Teilkapazität benötigt Verlustanteil zwischen 0 und 1")
    for index, row in enumerate(value["strategies"]):
        path = f"$.strategies[{index}]"
        if type(row["kind"]) is not str or row["kind"] not in STRATEGY_KINDS:
            issue(path + ".kind", "strategy_kind_unknown", "Unbekannte Gegenmaßnahme")
        if type(row["asset_id"]) is not str or row["asset_id"] not in assets:
            issue(path + ".asset_id", "asset_unknown", "Maßnahmenziel nicht deklariert")
        start = number(row["start_hour"], path + ".start_hour", horizon_hours)
        through = number(row["through_hour"], path + ".through_hour", horizon_hours)
        if through <= start:
            issue(path, "strategy_window_invalid", "Maßnahmenende muss nach Beginn liegen")
        number(row["effectiveness"], path + ".effectiveness", Decimal(1))
        number(row["cost_per_hour"], path + ".cost_per_hour", Decimal(1000))
    if issues:
        raise ContractError(issues)
    visiting: set[str] = set()
    done: set[str] = set()

    def visit(key: str) -> None:
        if key in visiting:
            issue("$.assets", "dependency_cycle", "Kreisabhängigkeit in der ICT-Kette")
            return
        if key in done:
            return
        visiting.add(key)
        for dep in assets[key]["depends_on"]:
            visit(dep)
        visiting.remove(key)
        done.add(key)

    for key in sorted(assets):
        visit(key)
    if not issues:
        used = {key for s in value["services"] for key in s["asset_ids"]}
        for _ in range(len(assets)):
            used |= {dep for key in tuple(used) for dep in assets[key]["depends_on"]}
        if any(s["asset_id"] not in used for s in value["strategies"]):
            issue("$.strategies", "strategy_owner_missing", "Maßnahmenziel hat keinen verantwortlichen Service/VU")
    if issues:
        raise ContractError(issues)
    return value
