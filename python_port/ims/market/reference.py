"""Explicit BaFin facts -> uncalibrated AP5 scenario, with a portable provenance bundle.

The immutable catalogue is supplied by the I/O layer. This module performs no
I/O and adds neither life demand nor ICT channels. Overrides are assumptions.
"""
from __future__ import annotations

from copy import deepcopy
from decimal import Decimal
import json

from ims.market.contract import HORIZONS, SECTORS, amount, validate
from ims.market.presets import assignment, family, portfolio
from ims.market.runner import MAX_RESULT_BYTES, calculate as market_calculate, digest, money
from ims.market.transport import wire_payload
from ims.strategies.modern_bridge import ContractError, exact, integer
from ims.strategies.modern_presets import workshop_case as seminar_case

CATALOG_DIGEST = "03ee33f97a772d8a88b69210784d5b4502ed533745bdd6f097eee699ec7c7b1a"
BUNDLE_VERSION = "ims.bafin-reference-bundle.v1"
TITLE = "BaFin-Gruppenauswertung 2024 – Workshop"
DEFAULT_WORKSHOP = {
    "nonlife_mix": {"motor": "0.4", "property_liability": "0.4", "unmodeled": "0.2"},
    "scale_model_currency_per_million_eur": "0.01",
    "model_price": "3", "loss_ratio": "0.6", "opening_assets_multiple": "100",
    "note": "Bearbeitbare Workshop-Annahmen, keine recherchierten Mengen, Risiken, Bilanzen oder Firmenstrategien. Die ausgewiesene Kfz/Sach/Rest-Aufteilung ist angenommener Mix.",
}


def catalog_checked(catalog: object) -> dict:
    if not isinstance(catalog, dict) or digest(catalog) != CATALOG_DIGEST:
        raise ContractError("$.source_catalog", "Originaler Faktenkatalog erforderlich; bearbeitete Werte separat als Workshop-Override führen")
    return catalog


def settings_checked(workshop: object) -> dict:
    value = exact(workshop, set(DEFAULT_WORKSHOP), "$.workshop")
    mix = exact(value["nonlife_mix"], {"motor", "property_liability", "unmodeled"}, "$.workshop.nonlife_mix")
    shares = [amount(v, "$.workshop.nonlife_mix") for v in mix.values()]
    if sum(shares) != 1 or any(v > 1 for v in shares):
        raise ContractError("$.workshop.nonlife_mix", "Kfz, Sach/Haftpflicht und nicht modellierter Rest müssen zusammen 1 ergeben")
    for key in ("scale_model_currency_per_million_eur", "model_price", "opening_assets_multiple"):
        number = amount(value[key], "$.workshop." + key)
        if number <= 0 or number > (Decimal(1) if key.startswith("scale_") else Decimal(1000)):
            raise ContractError("$.workshop." + key, "Positiver begrenzter Workshop-Parameter erforderlich")
    if amount(value["loss_ratio"], "$.workshop.loss_ratio") > 1:
        raise ContractError("$.workshop.loss_ratio", "Angenommene Schadenquote zwischen 0 und 1 erforderlich")
    if not isinstance(value["note"], str) or not 1 <= len(value["note"]) <= 1000:
        raise ContractError("$.workshop.note", "Workshop-Annahmen erläutern")
    return value


def reference_values(catalog: dict, overrides: object, workshop: dict) -> dict:
    if not isinstance(overrides, list) or len(overrides) > 326:
        raise ContractError("$.overrides", "Höchstens 326 benannte Workshop-Overrides erforderlich")
    original = {r["workbook_row"]: r for r in catalog["entities"]}
    edited = {}
    for item in overrides:
        exact(item, {"entity_row", "premium_million_eur", "note"}, "$.overrides")
        key = integer(item["entity_row"], "$.overrides.entity_row", 5, 330)
        if key not in original or key in edited:
            raise ContractError("$.overrides", "Eindeutiger vorhandener Rechtsträger-Zellbezug erforderlich")
        amount(item["premium_million_eur"], "$.overrides.premium_million_eur")
        if not isinstance(item["note"], str) or not 1 <= len(item["note"]) <= 400:
            raise ContractError("$.overrides.note", "Bearbeiteten Wert als Workshop-Annahme erklären")
        edited[key] = item
    groups = {g["name"]: {**g, "sectors": {s: Decimal(0) for s in ("Leben", "Kranken", "Schaden/Unfall")},
                          "entity_rows": [], "override_rows": []} for g in catalog["groups"]}
    for key, row in original.items():
        group = groups[row["group_assertion"]]
        raw = edited[key]["premium_million_eur"] if key in edited else row["premium_million_eur"]
        if raw is None:
            raise ContractError("$.source_catalog", "Unbekannte Beiträge verhindern die Referenzauswahl")
        group["sectors"][row["source_sector"]] += Decimal(raw)
        group["entity_rows"].append(key)
        if key in edited:
            group["override_rows"].append(key)
    for group in groups.values():
        group["total"] = sum(group["sectors"].values())
    ranked = sorted(groups.values(), key=lambda g: (-g["total"], g["group_id"]))
    if ranked[39]["total"] <= 0:
        raise ContractError("$.overrides", "40 positive Gruppenbeträge für den Referenzfall erforderlich")
    universe = sum(g["total"] for g in ranked)
    selected_total = sum(g["total"] for g in ranked[:40])
    mix = workshop["nonlife_mix"]
    selected = []
    for rank, group in enumerate(ranked[:40], 1):
        nonlife = group["sectors"]["Schaden/Unfall"]
        modeled = {"motor": nonlife * Decimal(mix["motor"]),
                   "property_liability": nonlife * Decimal(mix["property_liability"]),
                   "life": group["sectors"]["Leben"], "health": group["sectors"]["Kranken"]}
        selected.append({**group, "rank": rank, "total": str(group["total"]),
                         "sectors": {s: str(v) for s, v in group["sectors"].items()},
                         "model_basis_million_eur": {s: str(v) for s, v in modeled.items()},
                         "selected_weight": str(group["total"] / selected_total),
                         "source_weight": str(group["total"] / universe),
                         "unmodeled_million_eur": str(nonlife * Decimal(mix["unmodeled"]))})
    unm = sum(Decimal(g["unmodeled_million_eur"]) for g in selected)
    return {"data_year": 2024, "source_scope": deepcopy(catalog["source_scope"]),
            "selection_kind": "workshop_override_ranking" if edited else "original_editorial_earned_ranking",
            "groups": selected, "candidate_group_count": len(ranked),
            "universe_total_million_eur": str(universe), "selected_total_million_eur": str(selected_total),
            "modeled_selected_million_eur": str(selected_total - unm),
            "rest": {"unselected_groups_million_eur": str(universe - selected_total),
                     "selected_unmodeled_million_eur": str(unm),
                     "note": "Disjunkte Restkomponenten des erfassten Quellenumfangs, kein vollständiger deutscher Markt."},
            "rank_40": {"group_id": ranked[39]["group_id"], "name": ranked[39]["name"], "total": money(ranked[39]["total"])},
            "rank_41": {"group_id": ranked[40]["group_id"], "name": ranked[40]["name"], "total": money(ranked[40]["total"])},
            "gap_million_eur": money(ranked[39]["total"] - ranked[40]["total"]),
            "german_direct_selection_verified": False,
            "precision": "Quellenintervalle siehe unverändertes Audit; Overrides sind Annahmen. Gleichstände nach stabiler Gruppen-ID, keine Präzisionsbehauptung für bearbeitete Auswahl."}


def model_from_reference(catalog: dict, n: int, workshop: dict, reference: dict) -> dict:
    templates = seminar_case("price", n)["accounting_source"]["sectors"]
    scale, price = Decimal(workshop["scale_model_currency_per_million_eur"]), Decimal(workshop["model_price"])
    asset_multiple, loss_ratio = Decimal(workshop["opening_assets_multiple"]), Decimal(workshop["loss_ratio"])
    doc = {"schema_version": "ims.modern-market.v1", "case_id": "bafin_2024_workshop", "period_count": n, "seed": 20261002,
           "provenance": {"kind": "declared_scenario", "units": "model_currency", "description": catalog["source_scope"]["notice"]},
           "insurers": [], "customer_groups": [], "peer_groups": [], "families": [],
           "assignments": {"baseline": [], "variant": []}, "measures": {"baseline": [], "variant": []}, "damage_indicators": ["1"] * n}
    for sector in SECTORS[:2]:
        doc["families"] += [family(sector + "_Referenzpreis", sector, "offer.fixed", {"price": money(price), "advertising": "0"}),
                            family(sector + "_Preisantwort", sector, "offer.fixed", {"price": money(price * Decimal("0.9")), "advertising": "0"})]
    doc["families"].append(family("Leben_Anlage", "life", "life.opening_assets_rate", {"rate_per_period": "0.0005"}))
    for group in reference["groups"]:
        aid, gid = group["insurer_id"], group["group_id"]
        actor = {"insurer_id": aid, "insurance_group_id": gid, "name": group["name"], "sectors": {}}
        for sector, basis in group["model_basis_million_eur"].items():
            if Decimal(basis) == 0:
                continue  # Declared model omission, not a claim of actual inactivity.
            target = Decimal(money(Decimal(basis) * scale))
            if target <= 0:
                raise ContractError("$.workshop", "Skalierung rundet eine positive aktive Modellbasis auf null")
            assets, liability = Decimal(money(target * asset_multiple)), Decimal(money(target * 2))
            if assets < liability:
                raise ContractError("$.workshop.opening_assets_multiple", "Workshop-Aktiva müssen die deklarierte Anfangsreserve decken")
            if sector in SECTORS[:2]:
                quantity = Decimal(money(target / price))
                if quantity <= 0:
                    raise ContractError("$.workshop.model_price", "Positive Modellmenge nach vierstelliger Rundung erforderlich")
                source = portfolio(n, assets="0", capacity=money(quantity * Decimal("1.25")))
                source["opening"] = {"assets": money(assets), "liabilities": "0", "equity": money(assets)}
                actor["sectors"][sector] = source
                doc["customer_groups"].append({"group_id": gid + "_" + sector, "sector_id": sector, "quantity": money(quantity), "initial_insurer_id": aid,
                    "insurance_threshold": "1", "risk_periods": [{"period": p, "loss": money(quantity * price * loss_ratio), "paid_share": "1"} for p in range(1, n + 1)]})
                fid = sector + "_Referenzpreis"
            elif sector == "life":
                source = deepcopy(templates[sector])
                source["opening"].update(opening_backing_assets=money(assets), opening_guarantee_liability=money(liability), opening_equity=money(assets - liability))
                for item in (*source["opening"]["cohorts"], *source["opening"]["policies"]):
                    item["guarantee_liability"] = money(liability)
                for row in source["periods"]:
                    row["operating_expense_paid"] = money(target * Decimal("0.1"))
                    flow = row["policy_flows"][0]
                    flow.update(renewal_premiums_collected=money(target), maturity_benefit_if_due=money(liability) if row["period"] == 100 else "0")
                actor["sectors"][sector] = {"source": source}
                fid = "Leben_Anlage"
            else:
                source = deepcopy(templates[sector])
                source["opening"].update(opening_cash=money(assets), opening_benefit_liability=money(liability), opening_equity=money(assets - liability))
                for window in source["sources"]["benefits"]["windows"]:
                    window["amount_per_opening_policy"] = money(target * loss_ratio / 100)
                for row in source["periods"]:
                    # Consistent with rounded per-opening-policy benefits in the existing channel.
                    row.update(benefits_paid=money(Decimal(money(target * loss_ratio / 100)) * 100),
                               investment_result="0", operating_expense_paid=money(target * Decimal("0.1")))
                actor["sectors"][sector] = {"source": source}
                fid = gid + "_Krankenprofil"
                doc["families"].append(family(fid, "health", "health.declared_profile", {"price_per_policy": money(target / 100), "new_business": 0, "exits": 0}))
            doc["assignments"]["baseline"].append(assignment(aid, sector, fid))
        if not actor["sectors"]:
            raise ContractError("$.workshop.nonlife_mix", "Jede ausgewählte Gruppe benötigt mindestens eine positive erklärte Modellbasis")
        doc["insurers"].append(actor)
    doc["assignments"]["variant"] = deepcopy(doc["assignments"]["baseline"])
    target = next((a["insurer_id"] for a in doc["insurers"] if "motor" in a["sectors"]), None)
    if n > 5 and target is not None:
        for item in doc["assignments"]["variant"]:
            if item["insurer_id"] == target and item["sector_id"] == "motor":
                item["end"] = 5
        doc["assignments"]["variant"].append(assignment(target, "motor", "motor_Preisantwort", 6))
    return validate(doc)


def build_bundle(catalog: dict, n: int = 100, workshop: dict | None = None, overrides: list | None = None) -> dict:
    catalog_checked(catalog)
    if type(n) is not int or n not in HORIZONS:
        raise ContractError("$.period_count", "Freigegebener Markthorizont erforderlich")
    settings = settings_checked(deepcopy(DEFAULT_WORKSHOP if workshop is None else workshop))
    edits = deepcopy([] if overrides is None else overrides)
    reference = reference_values(catalog, edits, settings)
    return {"schema_version": BUNDLE_VERSION, "title": TITLE, "source_catalog": deepcopy(catalog),
            "catalog_digest": CATALOG_DIGEST, "workshop": settings, "overrides": edits,
            "model_input": model_from_reference(catalog, n, settings, reference)}


def calculate(value: object) -> dict:
    try:
        bundle = exact(value, {"schema_version", "title", "source_catalog", "catalog_digest", "workshop", "overrides", "model_input"}, "$")
        if bundle["schema_version"] != BUNDLE_VERSION or bundle["title"] != TITLE or bundle["catalog_digest"] != CATALOG_DIGEST:
            raise ContractError("$", "Versioniertes gekennzeichnetes BaFin-Referenzbündel erforderlich")
        catalog = catalog_checked(bundle["source_catalog"])
        workshop = settings_checked(bundle["workshop"])
        reference = reference_values(catalog, bundle["overrides"], workshop)
        doc = validate(bundle["model_input"])
        expected = model_from_reference(catalog, doc["period_count"], workshop, reference)
        identities = lambda d: {(a["insurer_id"], a["insurance_group_id"]) for a in d["insurers"]}
        if identities(doc) != identities(expected):
            raise ContractError("$.model_input.insurers", "40 ausgewählte stabile Gruppen-/VU-Identitäten erforderlich; Quellenänderungen zuerst neu abbilden")
        result = market_calculate(doc)
        if not result["valid"]:
            return result
        reference["model_binding"] = "preset_mapping" if digest(doc) == digest(expected) else "custom_workshop_model"
        reference["model_binding_note"] = "Modellmengen, Policen, Anfangsbilanzen und Strategien sind Annahmen; Rundung auf vier Dezimalstellen. Angepasste Modellquelle kann von der aus Quellengewichten erzeugten Vorlage abweichen."
        result.update(source_bundle=deepcopy(bundle), reference=reference, input_digest=digest(bundle))
        result["content_digest"] = digest({"market_result_digest": result["content_digest"], "bundle": bundle, "reference": reference})
        if len(json.dumps(wire_payload(result), ensure_ascii=False, separators=(",", ":")).encode("utf-8")) > MAX_RESULT_BYTES:
            raise ContractError("$", "Vollständiges Referenzergebnis überschreitet die Markt-Ressourcengrenze; kein Teilergebnis")
        return result
    except (ContractError, ValueError, TypeError, KeyError, ArithmeticError, RecursionError) as exc:
        return {"valid": False, "issues": [{"path": getattr(exc, "path", "$"), "code": "reference_contract_invalid", "message": str(exc)}],
                "sides": {}, "content_digest": None, "partial_result_returned": False, "writes_performed": False}
