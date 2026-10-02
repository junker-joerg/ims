"""Bounded, explicit AP5 market input; no I/O or global random state."""
from __future__ import annotations

from decimal import Decimal
import re

from ims.strategies.modern_bridge import ContractError, exact, identifier, integer, number

INPUT_VERSION = "ims.modern-market.v1"
RESULT_VERSION = "ims.modern-market-result.v1"
SECTORS = ("motor", "property_liability", "life", "health")
NON_LIFE = SECTORS[:2]
HORIZONS = (2, 5, 10, 25, 50, 100)
MAX_VUS = 41
MAX_COHORTS = 200
RULE_PARAMETERS = {
    "offer.fixed": {"price", "advertising"},
    "vu.vrvu01": {"premium_factor", "advertising_factor"},
    "life.opening_assets_rate": {"rate_per_period"},
    "health.declared_profile": {"price_per_policy", "new_business", "exits"},
}
FLOWS = {"old_claims_paid", "operating_expense", "investment_income", "capital_contribution", "capital_distribution"}
_AMOUNT = re.compile(r"-?(?:0|[1-9][0-9]{0,11})(?:\.[0-9]{1,4})?\Z")


def amount(value: object, path: str, *, signed: bool = False) -> Decimal:
    if type(value) is not str or not _AMOUNT.fullmatch(value):
        raise ContractError(path, "Endlicher Dezimalstring mit höchstens 12 Vor- und vier Nachkommastellen erforderlich")
    result = Decimal(value)
    if not signed and result < 0:
        raise ContractError(path, "Nichtnegativer Betrag erforderlich")
    return result


def array(value: object, path: str, maximum: int, minimum: int = 0) -> list:
    if type(value) is not list or not minimum <= len(value) <= maximum:
        raise ContractError(path, f"Liste mit {minimum} bis {maximum} Einträgen erforderlich")
    return value


def unique(value: object, path: str, used: set) -> str:
    key = identifier(value, path)
    if key in used:
        raise ContractError(path, "Doppelte Kennung")
    used.add(key)
    return key


def parameters(rule: str, values: dict, path: str, *, partial: bool = False) -> None:
    permitted = RULE_PARAMETERS[rule]
    if type(values) is not dict or (not partial and set(values) != permitted) or not set(values) <= permitted:
        raise ContractError(path, "Vollständige Parameter des benannten Regelkerns erforderlich")
    for key, value in values.items():
        if key in {"new_business", "exits"}:
            integer(value, path + "." + key, 0, 1000)
        else:
            number(value, path + "." + key, Decimal(-1) if key == "rate_per_period" else Decimal(0),
                   Decimal(1) if key == "rate_per_period" else Decimal(1000000))


def selected(doc: dict, side: str, actor: int, sector: str, period: int) -> dict:
    item = next(a for a in doc["assignments"][side] if a["insurer_id"] == actor and a["sector_id"] == sector
                and a["start"] <= period <= a["end"])
    return next(f for f in doc["families"] if f["family_id"] == item["family_id"])


def validate(value: object) -> dict:
    doc = exact(value, {"schema_version", "case_id", "period_count", "seed", "provenance", "insurers",
                        "customer_groups", "peer_groups", "families", "assignments", "measures", "damage_indicators"}, "$")
    if doc["schema_version"] != INPUT_VERSION:
        raise ContractError("$.schema_version", "Eigener moderner AP5-Marktvertrag erforderlich")
    identifier(doc["case_id"], "$.case_id")
    n = integer(doc["period_count"], "$.period_count", 2, 100)
    if n not in HORIZONS:
        raise ContractError("$.period_count", "Unterstützter Markt-Horizont erforderlich")
    integer(doc["seed"], "$.seed", 0, 2**53 - 1)
    provenance = exact(doc["provenance"], {"kind", "description", "units"}, "$.provenance")
    if provenance["kind"] not in {"synthetic_workshop", "declared_scenario"} or provenance["units"] != "model_currency":
        raise ContractError("$.provenance", "Erklärte Modellquelle und Modellwährung erforderlich")
    if type(provenance["description"]) is not str or not 1 <= len(provenance["description"]) <= 2000:
        raise ContractError("$.provenance.description", "Quellen-/Annahmenbeschreibung erforderlich")
    actors, insurance_groups, ids = {}, set(), set()
    for i, actor in enumerate(array(doc["insurers"], "$.insurers", MAX_VUS, 1)):
        path = f"$.insurers[{i}]"
        exact(actor, {"insurer_id", "insurance_group_id", "name", "sectors"}, path)
        aid = integer(actor["insurer_id"], path + ".insurer_id", 1, 1000000)
        if aid in actors:
            raise ContractError(path, "Doppelte VU-ID")
        actors[aid] = actor
        insurance_groups.add(identifier(actor["insurance_group_id"], path + ".insurance_group_id"))
        if type(actor["name"]) is not str or not 1 <= len(actor["name"]) <= 120:
            raise ContractError(path + ".name", "Anbietername erforderlich")
        sectors = actor["sectors"]
        if type(sectors) is not dict or not sectors or not set(sectors) <= set(SECTORS):
            raise ContractError(path + ".sectors", "Nur tatsächlich betriebene benannte Sparten angeben; fehlende Werte nicht als null tarnen")
        for sector, source in sectors.items():
            sp = path + ".sectors." + sector
            if sector in NON_LIFE:
                exact(source, {"opening", "capacity", "periods"}, sp)
                opening = exact(source["opening"], {"assets", "liabilities", "equity"}, sp + ".opening")
                stocks = {k: amount(v, sp + ".opening." + k, signed=k == "equity") for k, v in opening.items()}
                if stocks["assets"] != stocks["liabilities"] + stocks["equity"]:
                    raise ContractError(sp + ".opening", "Anfangsbilanz A=L+E erforderlich")
                amount(source["capacity"], sp + ".capacity")
                rows = array(source["periods"], sp + ".periods", n, n)
                for p, row in enumerate(rows, 1):
                    exact(row, FLOWS | {"period"}, sp + ".periods")
                    if type(row["period"]) is not int or row["period"] != p:
                        raise ContractError(sp + ".periods", "Lückenlose Perioden erforderlich")
                    for field in FLOWS:
                        amount(row[field], sp + ".periods." + field, signed=field == "investment_income")
            else:
                exact(source, {"source"}, sp)
                if type(source["source"]) is not dict or source["source"].get("insurer_id") != 1:
                    raise ContractError(sp, "Isolierte bestehende Spartenquelle mit lokaler Rechen-ID 1 erforderlich; moderne VU-ID bleibt außen")
                if source["source"].get("sector_id") != sector or len(source["source"].get("periods", [])) != n:
                    raise ContractError(sp, "Spartenquelle muss zum Horizont und zur Sparte passen")
    for i, cohort in enumerate(array(doc["customer_groups"], "$.customer_groups", MAX_COHORTS)):
        path = f"$.customer_groups[{i}]"
        exact(cohort, {"group_id", "sector_id", "quantity", "initial_insurer_id", "insurance_threshold", "risk_periods"}, path)
        unique(cohort["group_id"], path + ".group_id", ids)
        if type(cohort["sector_id"]) is not str or cohort["sector_id"] not in NON_LIFE:
            raise ContractError(path, "Nichtleben-Kohorte erforderlich; keine neue Lebens-Nachfrage")
        quantity = amount(cohort["quantity"], path + ".quantity")
        if quantity <= 0:
            raise ContractError(path, "Positive Kohortenmenge erforderlich")
        aid = cohort["initial_insurer_id"]
        if aid is not None and (type(aid) is not int or aid not in actors or cohort["sector_id"] not in actors[aid]["sectors"]):
            raise ContractError(path, "Anfangsträger muss in dieser Sparte aktiv sein")
        number(cohort["insurance_threshold"], path + ".insurance_threshold", Decimal(0), Decimal(1))
        for p, risk in enumerate(array(cohort["risk_periods"], path + ".risk_periods", n, n), 1):
            exact(risk, {"period", "loss", "paid_share"}, path + ".risk_periods")
            if type(risk["period"]) is not int or risk["period"] != p:
                raise ContractError(path, "Lückenlose Risikoperioden erforderlich")
            amount(risk["loss"], path + ".loss")
            number(risk["paid_share"], path + ".paid_share", Decimal(0), Decimal(1))
    if len(array(doc["damage_indicators"], "$.damage_indicators", n, n)) != n:
        raise ContractError("$.damage_indicators", "Vollständiger Indikatorpfad erforderlich")
    for indicator in doc["damage_indicators"]:
        number(indicator, "$.damage_indicators", Decimal(0), Decimal(1))
    peers = set()
    for peer in array(doc["peer_groups"], "$.peer_groups", 50):
        exact(peer, {"group_id", "label", "insurer_ids"}, "$.peer_groups")
        unique(peer["group_id"], "$.peer_groups.group_id", peers)
        if type(peer["label"]) is not str or not 1 <= len(peer["label"]) <= 120:
            raise ContractError("$.peer_groups", "Benannte Vergleichsgruppe erforderlich")
        members = array(peer["insurer_ids"], "$.peer_groups.insurer_ids", MAX_VUS, 1)
        if any(type(aid) is not int or aid not in actors for aid in members) or len(set(members)) != len(members):
            raise ContractError("$.peer_groups", "Eindeutige bekannte VUs erforderlich; Überlappung zwischen Gruppen ist erlaubt")
    family_ids, families = set(), {}
    for family in array(doc["families"], "$.families", 200, 1):
        exact(family, {"family_id", "label", "sector_id", "rule", "parameters"}, "$.families")
        fid = unique(family["family_id"], "$.families.family_id", family_ids)
        sector, rule = family["sector_id"], family["rule"]
        if type(rule) is not str or rule not in RULE_PARAMETERS or type(sector) is not str or sector not in SECTORS:
            raise ContractError("$.families", "Benannter ausführbarer Regelkern erforderlich")
        if (sector in NON_LIFE and rule not in {"offer.fixed", "vu.vrvu01"}) or (sector == "life" and rule != "life.opening_assets_rate") or (sector == "health" and rule != "health.declared_profile"):
            raise ContractError("$.families", "Familie muss zu ihrem Spartenkanal passen")
        if type(family["label"]) is not str or not 1 <= len(family["label"]) <= 120:
            raise ContractError("$.families", "Familienname erforderlich")
        parameters(rule, family["parameters"], "$.families.parameters")
        families[fid] = family
    for field in ("assignments", "measures"):
        exact(doc[field], {"baseline", "variant"}, "$." + field)
    for side in ("baseline", "variant"):
        coverage = {}
        for assignment in array(doc["assignments"][side], "$.assignments." + side, 1000, 1):
            exact(assignment, {"insurer_id", "sector_id", "family_id", "start", "end"}, "$.assignments")
            aid, sector, fid = assignment["insurer_id"], assignment["sector_id"], assignment["family_id"]
            if type(aid) is not int or aid not in actors or type(sector) is not str or sector not in actors[aid]["sectors"] or type(fid) is not str or fid not in families or families[fid]["sector_id"] != sector:
                raise ContractError("$.assignments", "Bekannter aktiver Akteur-/Sparten-/Familienbezug erforderlich")
            start = integer(assignment["start"], "$.assignments.start", 1, 100)
            end = integer(assignment["end"], "$.assignments.end", start, 100)
            for p in range(start, min(end, n) + 1):
                key = (aid, sector, p)
                if key in coverage:
                    raise ContractError("$.assignments", "Überlappende inklusive Familienfenster")
                coverage[key] = fid
        required = {(aid, sector, p) for aid, actor in actors.items() for sector in actor["sectors"] for p in range(1, n + 1)}
        if set(coverage) != required:
            raise ContractError("$.assignments", "Genau eine Familie für jede aktive VU/Sparte/Periode erforderlich")
        if side == "baseline":
            baseline = coverage
        elif any(coverage[key] != baseline[key] for key in required if key[2] <= 5):
            raise ContractError("$.assignments", "Gemeinsame Familien in Perioden 1–5 erforderlich")
        occupied, measure_ids = set(), set()
        for measure in array(doc["measures"][side], "$.measures." + side, 200):
            exact(measure, {"measure_id", "insurer_id", "sector_id", "decision_period", "lead_periods", "duration", "cost", "overrides"}, "$.measures")
            unique(measure["measure_id"], "$.measures.measure_id", measure_ids)
            aid, sector = measure["insurer_id"], measure["sector_id"]
            if type(aid) is not int or aid not in actors or type(sector) is not str or sector not in actors[aid]["sectors"]:
                raise ContractError("$.measures", "Aktiver Maßnahmenkanal erforderlich")
            decision = integer(measure["decision_period"], "$.measures.decision_period", 1, 100)
            lead = integer(measure["lead_periods"], "$.measures.lead_periods", 0, 100)
            duration = integer(measure["duration"], "$.measures.duration", 1, 100)
            amount(measure["cost"], "$.measures.cost")
            overrides = measure["overrides"]
            if type(overrides) is not dict or not overrides:
                raise ContractError("$.measures.overrides", "Benannter wirksamer Parameter erforderlich")
            permitted_rules = {f["rule"] for f in families.values() if f["sector_id"] == sector}
            parameter_values = {k: v for k, v in overrides.items() if k != "capacity"}
            if not any(set(parameter_values) <= RULE_PARAMETERS[rule] for rule in permitted_rules):
                raise ContractError("$.measures.overrides", "Maßnahmenparameter passt zu keinem erklärten Spartenprofil")
            for rule in permitted_rules:
                if set(parameter_values) <= RULE_PARAMETERS[rule]:
                    parameters(rule, parameter_values, "$.measures.overrides", partial=True)
                    break
            if "capacity" in overrides:
                if sector not in NON_LIFE:
                    raise ContractError("$.measures", "Kapazität ist ein Nichtleben-Aufnahmekanal")
                amount(overrides["capacity"], "$.measures.overrides.capacity")
            for p in range(decision + lead, min(decision + lead + duration, n + 1)):
                family = families[coverage[(aid, sector, p)]]
                params = {k: v for k, v in overrides.items() if k != "capacity"}
                parameters(family["rule"], params, "$.measures.overrides", partial=True)
                for key in overrides:
                    if key == "capacity":
                        if sector not in NON_LIFE:
                            raise ContractError("$.measures", "Kapazität ist ein Nichtleben-Aufnahmekanal")
                        amount(overrides[key], "$.measures.overrides.capacity")
                    occupied_key = (aid, sector, p, key)
                    if occupied_key in occupied:
                        raise ContractError("$.measures", "Widersprüchlich überlappende Maßnahmen")
                    occupied.add(occupied_key)
    return doc
