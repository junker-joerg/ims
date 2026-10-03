"""Four complete assumed AP7 cases derived from the immutable BaFin catalogue."""
from __future__ import annotations

from copy import deepcopy
from decimal import Decimal

from ims.market.presets import assignment, family, portfolio
from ims.market.reference import build_bundle
from ims.market.shock_contract import CASES, INPUT_VERSION, validate
from ims.market.shock_plan import equal_owners
from ims.strategies.modern_bridge import ContractError, money

NOTE = "Workshop-Annahmen: keine recherchierten Unternehmensstrategien, Tarife, Bilanz-/Prozessdaten oder Providerbeziehungen. BaFin-Quelle einschließlich Ausland und Rückversicherung; kein deutscher Direktmarkt."


def main_sector(actor: dict) -> tuple[str, Decimal]:
    def assets(sector: str) -> Decimal:
        source = actor["sectors"][sector]
        opening = source.get("opening", source.get("source", {}).get("opening", {}))
        return Decimal(opening.get("assets", opening.get("opening_backing_assets", opening.get("opening_cash", "0"))))
    return max(((sector, assets(sector)) for sector in actor["sectors"]), key=lambda item: (item[1], item[0]))


def process_owners(actors: dict, ids: list[int]) -> list[dict]:
    """Declared allocation by opening assets of the chosen administrative sector."""
    owners = [{"insurer_id": aid, "sector_id": main_sector(actors[aid])[0], "assets": main_sector(actors[aid])[1]} for aid in ids]
    total = sum((owner["assets"] for owner in owners), Decimal(0))
    if not total:
        return equal_owners(actors, ids)
    largest = max(owners, key=lambda owner: (owner["assets"], owner["insurer_id"]))
    weights = {owner["insurer_id"]: Decimal(money(owner["assets"] / total)) for owner in owners}
    weights[largest["insurer_id"]] += 1 - sum(weights.values(), Decimal(0))
    return [{"insurer_id": owner["insurer_id"], "sector_id": owner["sector_id"], "weight": money(weights[owner["insurer_id"]])} for owner in owners]


def response(key: str, kind: str, ids: list[int], value: str, cost: str, *, asset: str = "", replacement: str = "", hourly: str = "0") -> dict:
    return {"response_id": key, "kind": kind, "decision_period": 16, "lead_periods": 4, "duration_periods": 81,
            "insurer_ids": ids, "asset_id": asset, "replacement_asset_id": replacement, "value": value,
            "cost": cost, "cost_per_hour": hourly, "assumption_note": "Deklarierte Gegenmaßnahme: Entscheidung und Verfügbarkeit folgen den benannten Parametern; Preisantwort wird bei Eintritt wirksam. Keine tatsächliche Firmenstrategie."}


def build_case(catalog: dict, case_id: str, period_count: int = 100) -> dict:
    if type(case_id) is not str or case_id not in CASES:
        raise ContractError("$.case_id", "Einer der vier benannten AP7-Fälle erforderlich")
    reference = build_bundle(catalog, period_count)
    model = deepcopy(reference["model_input"])
    model["case_id"] = "ap7_" + case_id
    model["provenance"]["description"] += " " + NOTE
    model["assignments"]["variant"] = deepcopy(model["assignments"]["baseline"])
    model["measures"] = {"baseline": [], "variant": []}
    original_ids = [actor["insurer_id"] for actor in model["insurers"]]
    motor_ids = [actor["insurer_id"] for actor in model["insurers"] if "motor" in actor["sectors"]]
    life_ids = [actor["insurer_id"] for actor in model["insurers"] if "life" in actor["sectors"]]
    assets = []
    topology = [
        ("portal", "Gemeinsamer Antrags-/Verwaltungsprozess", "EU", ["us-runtime", "us-iam"]),
        ("us-runtime", "Deklarierter US-Hyperscaler: Rechen-/Datenpfad", "US", []),
        ("us-iam", "Gemeinsame US-Identitätsvorleistung", "US", []),
        ("q-independent", "Unabhängiger Q-Ersatzpfad", "EU", ["eu-iam", "eu-dns", "eu-keys", "eu-data", "eu-network"]),
        ("q-dependent", "Q mit gemeinsamem US-IAM", "EU", ["us-iam"]),
        ("eu-iam", "Deklarierte EU-Identität", "EU", []), ("eu-dns", "Deklarierter EU-DNS", "EU", []),
        ("eu-keys", "Deklarierte EU-Schlüssel", "EU", []), ("eu-data", "Deklarierte EU-Daten", "EU", []),
        ("eu-network", "Deklariertes EU-Netz", "EU", []),
    ]
    for aid, label, control, dependencies in topology:
        assets.append({"asset_id": aid, "label": label, "control": control, "depends_on": dependencies, "assumption_note": NOTE})
    event = {"event_id": "ap7-shock", "kind": "provider_outage", "start_hour": "480", "duration_hours": "36",
             "intensity": "1", "insurer_ids": original_ids, "asset_ids": ["us-runtime", "us-iam"],
             "channels": ["capacity", "administration"], "cost": "0", "assumption_note": NOTE}
    activations, responses = [], {"baseline": [], "variant": []}
    if case_id == "google_motor_entry":
        if not motor_ids:
            raise ContractError("$.model_input", "Eintrittsfall benötigt modellierte Kfz-Kohorten")
        extra_id = 1_000_000
        total = sum((Decimal(cohort["quantity"]) for cohort in model["customer_groups"] if cohort["sector_id"] == "motor"), Decimal(0))
        model["insurers"].append({"insurer_id": extra_id, "insurance_group_id": "Fiktiver_Google_AP7", "name": "Google · fiktiver Anbieter 41",
                                  "sectors": {"motor": portfolio(period_count, assets="0", capacity=money(total * Decimal("0.25")))}})
        model["families"].append(family("Google_Fiktiv", "motor", "offer.fixed", {"price": "2.4", "advertising": "2"}))
        for side in ("baseline", "variant"):
            model["assignments"][side].append(assignment(extra_id, "motor", "Google_Fiktiv"))
        event.update(kind="entry", duration_hours="1920", insurer_ids=[extra_id], asset_ids=[], channels=["offers"])
        activations.append({"insurer_id": extra_id, "event_id": event["event_id"], "capital": "100000",
                            "reachable_group_ids": [cohort["group_id"] for cohort in model["customer_groups"] if cohort["sector_id"] == "motor"]})
        responses["variant"] = [response("Preisantwort", "price", [motor_ids[0]], "2.1", "100")]
    elif case_id == "life_demand_shock":
        event.update(kind="life_demand", duration_hours="1920", intensity="0.75", asset_ids=[], channels=["life_demand"])
        responses["variant"] = [response("Vertriebsantwort", "life_attractiveness", life_ids, "0.5", "6")]
    elif case_id == "dora_2_workshop":
        event.update(kind="regulatory", duration_hours="240", intensity="0.5", asset_ids=["portal"], channels=["capacity", "cost", "administration"], cost="100")
        event["assumption_note"] = "DORA 2.0 ist ein hypothetischer Seminarname. Zehn Perioden Umstellung: angenommener Kapazitätsverlust 50 %, Umstellungskosten 100; keine behauptete neue Vorschrift. " + NOTE
        responses["variant"] = [response("Vorbereitete_Kapazitaet", "capacity", original_ids, "2", "6", asset="portal", hourly="0.03")]
    else:
        responses["variant"] = [response("Q_Vorsorge", "fallback", original_ids, "1", "6", asset="portal", replacement="q-independent", hourly="0.03")]
    actors = {actor["insurer_id"]: actor for actor in model["insurers"]}
    services = []
    for aid, actor in sorted(actors.items()):
        for sector in ("motor", "property_liability", "life"):
            if sector in actor["sectors"]:
                services.append({"service_id": f"U_{aid}_{sector}", "insurer_id": aid, "sector_id": sector, "kind": "underwriting",
                                 "resource_id": "shared-staff-platform", "arrivals_per_period": 0,
                                 "assumption_note": "Ein ganzer Kohortenwechsel oder Lebensantrag benötigt eine deklarierte Arbeitseinheit; keine empirische Prozessmessung."})
        if aid in original_ids:
            sector = main_sector(actor)[0]
            for kind in ("claims", "service"):
                services.append({"service_id": f"{kind}_{aid}", "insurer_id": aid, "sector_id": sector, "kind": kind,
                                 "resource_id": "shared-staff-platform", "arrivals_per_period": 1,
                                 "assumption_note": "Ab P6 eine Verwaltungsarbeit je Modellperiode, zugeordnet der nach Anfangsaktiva tragenden Modellsparte; keine Verschiebung von Versicherungszahlungen. Dies ist eine Prozess-/Kostenannahme, kein Sparten-Funding."})
    bundle = {"schema_version": INPUT_VERSION, "case_id": case_id, "title": CASES[case_id], "assumption_note": NOTE,
              "reference_bundle": reference, "model_input": model, "period_hours": "24", "comparison": "shock_with_response",
              "events": [event], "responses": responses, "activation": activations,
              "life": {"pool_per_period": 4, "start_period": 6, "offers": [
                  {"insurer_id": aid, "premium": "3", "allocation": "2", "renewal_premium": "3", "renewal_allocation": "2",
                   "term_periods": 10, "guarantee_rate": "0.001", "admission_per_period": 2} for aid in life_ids]},
              "ict": {"assets": assets, "resources": [{"resource_id": "shared-staff-platform", "asset_id": "portal",
                        "capacity_per_hour": "4", "cost_per_hour": "0.02", "owners": process_owners(actors, original_ids)}],
                      "services": services, "holding_cost_per_job_hour": "0.0001"}}
    validate(bundle)
    return bundle
