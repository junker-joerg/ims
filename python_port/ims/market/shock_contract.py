"""Accepted AP7 event, demand and physical process contract; no I/O."""
from __future__ import annotations

from decimal import Decimal
import json

from ims.market.contract import array, amount, unique, validate as validate_market
from ims.market.reference import BUNDLE_VERSION, CATALOG_DIGEST, TITLE, catalog_checked, model_from_reference, reference_values, settings_checked
from ims.strategies.modern_bridge import ContractError, exact, identifier, integer, number

INPUT_VERSION = "ims.market-shock-bundle.v1"
RESULT_VERSION = "ims.market-shock-result.v1"
CASES = {
    "google_motor_entry": "Google kommt in die Kfz-Versicherung",
    "life_demand_shock": "LV wird unattraktiv",
    "dora_2_workshop": "Regulierungsschock ICT DORA 2.0",
    "us_hyperscaler_outage": "Alle US-Hyperscaler fallen aus",
}
MAX_INPUT_BYTES = 16 * 1024 * 1024
MAX_RESULT_BYTES = 64 * 1024 * 1024
MAX_JOBS = 40_000


def note(value: object, path: str) -> None:
    if type(value) is not str or not 1 <= len(value) <= 2000:
        raise ContractError(path, "Sichtbarer Annahmen-/Erklärhinweis erforderlich")


def targets(value: object, actors: dict, path: str) -> list[int]:
    values = array(value, path, 41, 1)
    if any(type(aid) is not int or aid not in actors for aid in values) or len(set(values)) != len(values):
        raise ContractError(path, "Eindeutige bekannte Ziel-VUs erforderlich")
    return values


def validate_reference(value: object) -> tuple[dict, dict]:
    bundle = exact(value, {"schema_version", "title", "source_catalog", "catalog_digest", "workshop", "overrides", "model_input"}, "$.reference_bundle")
    if (bundle["schema_version"], bundle["title"], bundle["catalog_digest"]) != (BUNDLE_VERSION, TITLE, CATALOG_DIGEST):
        raise ContractError("$.reference_bundle", "Angenommenes BaFin-Referenzbündel erforderlich")
    catalog = catalog_checked(bundle["source_catalog"])
    settings = settings_checked(bundle["workshop"])
    reference = reference_values(catalog, bundle["overrides"], settings)
    source = validate_market(bundle["model_input"])
    expected = model_from_reference(catalog, source["period_count"], settings, reference)
    identities = lambda doc: {(actor["insurer_id"], actor["insurance_group_id"], actor["name"]) for actor in doc["insurers"]}
    if identities(source) != identities(expected):
        raise ContractError("$.reference_bundle", "Unveränderte 40 Quellenidentitäten erforderlich")
    if source != expected:
        raise ContractError("$.reference_bundle.model_input", "Referenzabbildung muss zum Quellen-/Overridebeleg passen; eigene AP7-Annahmen gehören in model_input")
    reference.update(model_binding="derived_ap7_workshop", model_binding_note="Abgeleiteter AP7-Modellfall; Strategien, neue Produkte, Finanzierung und Provider sind Annahmen.")
    return source, reference


def validate(value: object) -> tuple[dict, dict]:
    if len(json.dumps(value, ensure_ascii=False, allow_nan=False, separators=(",", ":")).encode("utf-8")) > MAX_INPUT_BYTES:
        raise ContractError("$", "AP7-Eingang überschreitet 16 MiB")
    doc = exact(value, {"schema_version", "case_id", "title", "assumption_note", "reference_bundle", "model_input", "period_hours", "comparison", "events", "responses", "activation", "life", "ict"}, "$")
    if doc["schema_version"] != INPUT_VERSION or doc["case_id"] not in CASES or doc["title"] != CASES[doc["case_id"]]:
        raise ContractError("$", "Versionierter benannter AP7-Schockfall erforderlich")
    note(doc["assumption_note"], "$.assumption_note")
    if doc["period_hours"] != "24" or type(doc["period_hours"]) is not str:
        raise ContractError("$.period_hours", "Angenommene Abbildung: 24 Prozessstunden je Modellperiode")
    if doc["comparison"] not in ("shock_with_response", "no_shock_vs_shock"):
        raise ContractError("$.comparison", "Benannte Vergleichsachse erforderlich")
    base, reference = validate_reference(doc["reference_bundle"])
    market = validate_market(doc["model_input"])
    if (market["period_count"], market["seed"]) != (base["period_count"], base["seed"]):
        raise ContractError("$.model_input", "Gemeinsamer Horizont und Quellen-Seed erforderlich")
    actors = {actor["insurer_id"]: actor for actor in market["insurers"]}
    base_actors = {actor["insurer_id"]: actor for actor in base["insurers"]}
    for aid, actor in base_actors.items():
        if aid not in actors or (actor["name"], actor["insurance_group_id"]) != (actors[aid]["name"], actors[aid]["insurance_group_id"]):
            raise ContractError("$.model_input.insurers", "BaFin-Identitäten erhalten; Ergänzungen explizit synthetisch")
    extras = set(actors) - set(base_actors)
    if doc["case_id"] == "google_motor_entry" and len(extras) != 1:
        raise ContractError("$.model_input.insurers", "Google-Fall benötigt einen ausdrücklich fiktiven 41. Anbieter")
    if len(extras) > 1:
        raise ContractError("$.model_input.insurers", "Höchstens ein fiktiver Anbieter 41")
    ict = exact(doc["ict"], {"assets", "resources", "services", "holding_cost_per_job_hour"}, "$.ict")
    amount(ict["holding_cost_per_job_hour"], "$.ict.holding_cost_per_job_hour")
    assets, ids = {}, set()
    for asset in array(ict["assets"], "$.ict.assets", 40, 1):
        exact(asset, {"asset_id", "label", "control", "depends_on", "assumption_note"}, "$.ict.assets")
        aid = unique(asset["asset_id"], "$.ict.assets.asset_id", ids)
        note(asset["label"], "$.ict.assets.label")
        note(asset["assumption_note"], "$.ict.assets.assumption_note")
        if asset["control"] not in ("US", "EU", "unknown"):
            raise ContractError("$.ict.assets.control", "Deklarierte Kontrolle US/EU/unknown erforderlich")
        dependencies = array(asset["depends_on"], "$.ict.assets.depends_on", 40)
        if len(set(dependencies)) != len(dependencies):
            raise ContractError("$.ict.assets.depends_on", "Keine doppelten Abhängigkeiten")
        assets[aid] = asset
    visiting, visited = set(), set()
    def walk(key: str) -> None:
        if key not in assets or key in visiting:
            raise ContractError("$.ict.assets", "Bekannter azyklischer vollständiger Ersatz-/Abhängigkeitsgraph erforderlich")
        if key in visited:
            return
        visiting.add(key)
        for dependency in assets[key]["depends_on"]:
            walk(dependency)
        visiting.remove(key)
        visited.add(key)
    for key in assets:
        walk(key)
    resources, ids = {}, set()
    for resource in array(ict["resources"], "$.ict.resources", 40, 1):
        exact(resource, {"resource_id", "asset_id", "capacity_per_hour", "cost_per_hour", "owners"}, "$.ict.resources")
        rid = unique(resource["resource_id"], "$.ict.resources.resource_id", ids)
        if resource["asset_id"] not in assets:
            raise ContractError("$.ict.resources.asset_id", "Bekannter Ressourcenpfad erforderlich")
        amount(resource["capacity_per_hour"], "$.ict.resources.capacity_per_hour")
        amount(resource["cost_per_hour"], "$.ict.resources.cost_per_hour")
        total, owners = Decimal(0), set()
        for owner in array(resource["owners"], "$.ict.resources.owners", 164, 1):
            exact(owner, {"insurer_id", "sector_id", "weight"}, "$.ict.resources.owners")
            aid, sector = owner["insurer_id"], owner["sector_id"]
            if type(aid) is not int or aid not in actors or sector not in actors[aid]["sectors"] or (aid, sector) in owners:
                raise ContractError("$.ict.resources.owners", "Eindeutiger vorhandener VU-/Spartenkostenträger erforderlich")
            total += amount(owner["weight"], "$.ict.resources.owners.weight")
            owners.add((aid, sector))
        if total != 1:
            raise ContractError("$.ict.resources.owners", "Kosten-Gewichtssumme exakt 1 erforderlich")
        resources[rid] = resource
    ids, processes = set(), set()
    for service in array(ict["services"], "$.ict.services", 246):
        exact(service, {"service_id", "insurer_id", "sector_id", "kind", "resource_id", "arrivals_per_period", "assumption_note"}, "$.ict.services")
        unique(service["service_id"], "$.ict.services.service_id", ids)
        aid, sector = service["insurer_id"], service["sector_id"]
        if type(aid) is not int or aid not in actors or sector not in actors[aid]["sectors"] or service["resource_id"] not in resources:
            raise ContractError("$.ict.services", "Bekannter VU-/Sparten-/Ressourcenbezug erforderlich")
        if service["kind"] not in ("underwriting", "claims", "service") or (aid, sector, service["kind"]) in processes:
            raise ContractError("$.ict.services", "Eindeutiger erklärter Prozesskanal erforderlich")
        integer(service["arrivals_per_period"], "$.ict.services.arrivals_per_period", 0, 20)
        if service["kind"] == "underwriting" and service["arrivals_per_period"] != 0:
            raise ContractError("$.ict.services", "Antrags-/Wechselmengen entstehen nur aus dem Markt, kein doppelter exogener Zufluss")
        note(service["assumption_note"], "$.ict.services.assumption_note")
        processes.add((aid, sector, service["kind"]))
    event_ids = set()
    for event in array(doc["events"], "$.events", 20, 1):
        exact(event, {"event_id", "kind", "start_hour", "duration_hours", "intensity", "insurer_ids", "asset_ids", "channels", "cost", "assumption_note"}, "$.events")
        unique(event["event_id"], "$.events.event_id", event_ids)
        if event["kind"] not in ("entry", "life_demand", "regulatory", "provider_outage"):
            raise ContractError("$.events.kind", "Benannter AP7-Wirkungskanal erforderlich")
        start = number(event["start_hour"], "$.events.start_hour", Decimal(120), Decimal(2400))
        duration = number(event["duration_hours"], "$.events.duration_hours", Decimal("0.0001"), Decimal(2400))
        if event["kind"] in ("entry", "life_demand") and start % 24:
            raise ContractError("$.events.start_hour", "Markteintritt/Nachfrage beginnen am Periodenanfang")
        number(event["intensity"], "$.events.intensity", Decimal(0), Decimal(1))
        targets(event["insurer_ids"], actors, "$.events.insurer_ids")
        affected = array(event["asset_ids"], "$.events.asset_ids", 40)
        if len(set(affected)) != len(affected) or any(key not in assets for key in affected):
            raise ContractError("$.events.asset_ids", "Eindeutige bekannte Zielressourcen erforderlich")
        channels = array(event["channels"], "$.events.channels", 5, 1)
        if any(channel not in ("offers", "life_demand", "capacity", "cost", "administration") for channel in channels):
            raise ContractError("$.events.channels", "Explizite unterstützte Wirkungskanäle erforderlich")
        amount(event["cost"], "$.events.cost")
        note(event["assumption_note"], "$.events.assumption_note")
        permitted = {"entry": {"offers", "cost"}, "life_demand": {"life_demand", "cost"},
                     "regulatory": {"capacity", "cost", "administration"}, "provider_outage": {"capacity", "cost", "administration"}}[event["kind"]]
        required = {"entry": "offers", "life_demand": "life_demand", "regulatory": "capacity", "provider_outage": "capacity"}[event["kind"]]
        if not set(channels) <= permitted or required not in channels:
            raise ContractError("$.events.channels", "Wirkungskanäle müssen zum ausgeführten Ereignistyp passen")
        if Decimal(event["cost"]) and "cost" not in channels:
            raise ContractError("$.events.channels", "Ereigniszahlung benötigt den ausdrücklich benannten Kostenkanal")
        if event["kind"] == "entry" and Decimal(event["intensity"]) != 1:
            raise ContractError("$.events.intensity", "Eintritt ist ein Aktivierungsereignis mit Intensität 1, keine skalierte Kundenmenge")
        if event["kind"] in ("regulatory", "provider_outage") and set(event["insurer_ids"]) != set(actors):
            raise ContractError("$.events.insurer_ids", "Gemeinsamer Provider-/Ressourcenschock deklariert alle eingebundenen Akteure; betroffene Pfade werden transitiv ausgewertet")
        if doc["case_id"] == "us_hyperscaler_outage" and event["kind"] == "provider_outage" and set(affected) != {key for key, asset in assets.items() if asset["control"] == "US"}:
            raise ContractError("$.events.asset_ids", "Der gemeinsame US-Ausfall muss alle ausdrücklich US-kontrollierten Vorleistungen erfassen")
        if event["kind"] == "entry" and start + duration < market["period_count"] * 24:
            raise ContractError("$.events.duration_hours", "Eintritt bleibt bis zum Horizont aktiv; Austritt benötigt einen eigenen Bestandsvertrag")
    activations = set()
    for activation in array(doc["activation"], "$.activation", 1):
        exact(activation, {"insurer_id", "event_id", "capital", "reachable_group_ids"}, "$.activation")
        aid = activation["insurer_id"]
        if type(aid) is not int or aid not in extras or aid in activations:
            raise ContractError("$.activation", "Explizit finanzierter synthetischer Anbieter erforderlich")
        event = next((event for event in doc["events"] if event["event_id"] == activation["event_id"]), None)
        if not event or event["kind"] != "entry" or event["insurer_ids"] != [aid]:
            raise ContractError("$.activation", "Genau ein zugehöriges Eintrittsereignis erforderlich")
        if set(actors[aid]["sectors"]) != {"motor"}:
            raise ContractError("$.activation", "Anbieter 41 eröffnet ausschließlich den Kfz-Workshopkanal")
        portfolio = actors[aid]["sectors"]["motor"]
        if any(Decimal(stock) for stock in portfolio["opening"].values()) or any(Decimal(row["capital_contribution"]) for row in portfolio["periods"]):
            raise ContractError("$.activation", "Null-Anfangsbestand; Eintrittskapital wird durch das Ereignis genau einmal eingebucht")
        amount(activation["capital"], "$.activation.capital")
        groups = {cohort["group_id"] for cohort in market["customer_groups"] if cohort["sector_id"] == "motor"}
        reachable = array(activation["reachable_group_ids"], "$.activation.reachable_group_ids", 200)
        if len(set(reachable)) != len(reachable) or not set(reachable) <= groups:
            raise ContractError("$.activation", "Explizite bekannte Reichweitenkohorten erforderlich")
        activations.add(aid)
    if activations != extras:
        raise ContractError("$.activation", "Jeder zusätzliche Anbieter benötigt seinen Aktivierungs-/Finanzierungsbeleg")
    life = exact(doc["life"], {"pool_per_period", "start_period", "offers"}, "$.life")
    integer(life["pool_per_period"], "$.life.pool_per_period", 0, 20)
    integer(life["start_period"], "$.life.start_period", 6, 100)
    ids = set()
    for offer in array(life["offers"], "$.life.offers", 40):
        exact(offer, {"insurer_id", "premium", "allocation", "renewal_premium", "renewal_allocation", "term_periods", "guarantee_rate", "admission_per_period"}, "$.life.offers")
        aid = offer["insurer_id"]
        if type(aid) is not int or aid not in actors or "life" not in actors[aid]["sectors"] or aid in ids or (aid, "life", "underwriting") not in processes:
            raise ContractError("$.life.offers", "Eindeutiger Lebensanbieter mit wirksamem Antragsprozess erforderlich")
        for key in ("premium", "allocation", "renewal_premium", "renewal_allocation"):
            amount(offer[key], "$.life.offers." + key)
        if Decimal(offer["allocation"]) > Decimal(offer["premium"]) or Decimal(offer["renewal_allocation"]) > Decimal(offer["renewal_premium"]):
            raise ContractError("$.life.offers", "Garantiezuführung darf eingezogene Prämie nicht übersteigen")
        integer(offer["term_periods"], "$.life.offers.term_periods", 1, 20)
        integer(offer["admission_per_period"], "$.life.offers.admission_per_period", 1, 4)
        number(offer["guarantee_rate"], "$.life.offers.guarantee_rate", Decimal(0), Decimal(1))
        ids.add(aid)
    for event in doc["events"]:
        if event["kind"] == "life_demand" and not ids <= set(event["insurer_ids"]):
            raise ContractError("$.events.insurer_ids", "Der deklarierte Interessentenpool gilt für den gesamten Lebens-Modellmarkt")
    exact(doc["responses"], {"baseline", "variant"}, "$.responses")
    for side in ("baseline", "variant"):
        ids = set()
        capacity_windows: dict[str, list[tuple[int, int]]] = {}
        for response in array(doc["responses"][side], "$.responses." + side, 20):
            exact(response, {"response_id", "kind", "decision_period", "lead_periods", "duration_periods", "insurer_ids", "asset_id", "replacement_asset_id", "value", "cost", "cost_per_hour", "assumption_note"}, "$.responses")
            unique(response["response_id"], "$.responses.response_id", ids)
            if response["kind"] not in ("price", "life_attractiveness", "fallback", "capacity"):
                raise ContractError("$.responses.kind", "Benannte ausführbare Gegenmaßnahme erforderlich")
            decision = integer(response["decision_period"], "$.responses.decision_period", 6, 100)
            integer(response["lead_periods"], "$.responses.lead_periods", 0, 100)
            integer(response["duration_periods"], "$.responses.duration_periods", 1, 100)
            targets(response["insurer_ids"], actors, "$.responses.insurer_ids")
            amount(response["value"], "$.responses.value")
            amount(response["cost"], "$.responses.cost")
            amount(response["cost_per_hour"], "$.responses.cost_per_hour")
            note(response["assumption_note"], "$.responses.assumption_note")
            if response["kind"] in ("fallback", "capacity"):
                matching = [resource for resource in resources.values() if resource["asset_id"] == response["asset_id"]]
                if len(matching) != 1:
                    raise ContractError("$.responses.asset_id", "Genau ein deklarierter gemeinsamer Ressourcenpfad erforderlich")
                if set(response["insurer_ids"]) != {owner["insurer_id"] for owner in matching[0]["owners"]}:
                    raise ContractError("$.responses.insurer_ids", "Gemeinsame Ressourcenmaßnahme benennt alle erklärten Kostenträger")
            if response["kind"] == "capacity":
                start = decision + response["lead_periods"]
                end = start + response["duration_periods"]
                previous = capacity_windows.setdefault(response["asset_id"], [])
                if any(start < other_end and other_start < end for other_start, other_end in previous):
                    raise ContractError("$.responses", "Überlappende Personal-Kapazitätsfaktoren benötigen einen eigenen Budgetvertrag")
                previous.append((start, end))
            if response["kind"] == "price" and any("motor" not in actors[aid]["sectors"] for aid in response["insurer_ids"]):
                raise ContractError("$.responses.insurer_ids", "Preisantwort benötigt Kfz-Angebote")
            if response["kind"] == "life_attractiveness" and set(response["insurer_ids"]) != {offer["insurer_id"] for offer in life["offers"]}:
                raise ContractError("$.responses.insurer_ids", "Attraktivitätsantwort gilt für den gesamten deklarierten Lebenspool")
            if response["kind"] == "fallback" and response["replacement_asset_id"] not in assets:
                raise ContractError("$.responses.replacement_asset_id", "Konkreter Ersatzpfad erforderlich")
            if response["kind"] in ("fallback", "life_attractiveness") and Decimal(response["value"]) > 1:
                raise ContractError("$.responses.value", "Wirkungs-/Attraktivitätsanteil zwischen 0 und 1")
    return doc, reference
