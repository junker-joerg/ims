"""Complete synthetic AP5 markets; no real ranking or insurer strategy claims."""
from copy import deepcopy

from ims.market.contract import HORIZONS, INPUT_VERSION, NON_LIFE
from ims.strategies.modern_presets import workshop_case as seminar_case

CASES = {"market": "Synthetischer Markt: gemeinsame VUs und Familien", "switch": "Handfall: Wechsel mit Altreserve", "capacity": "Handfall: Kapazität und unversicherte Nachfrage"}


def portfolio(n: int, *, assets: str = "1000000", liability: str = "0", capacity: str = "30") -> dict:
    return {"opening": {"assets": assets, "liabilities": liability, "equity": str(int(assets) - int(liability))}, "capacity": capacity,
            "periods": [{"period": p, "old_claims_paid": "0", "operating_expense": "0", "investment_income": "0", "capital_contribution": "0", "capital_distribution": "0"} for p in range(1, n + 1)]}


def family(fid: str, sector: str, rule: str, params: dict) -> dict:
    return {"family_id": fid, "label": fid.replace("_", " "), "sector_id": sector, "rule": rule, "parameters": params}


def assignment(aid: int, sector: str, fid: str, start: int = 1, end: int = 100) -> dict:
    return {"insurer_id": aid, "sector_id": sector, "family_id": fid, "start": start, "end": end}


def workshop_case(case_id: str = "market", n: int = 100, count: int = 40) -> dict:
    if type(case_id) is not str or case_id not in CASES or type(n) is not int or n not in HORIZONS or type(count) is not int or not 1 <= count <= 41:
        raise ValueError("Benannter Fall, unterstützter Horizont und 1–41 VUs erforderlich")
    if case_id != "market":
        count = 2 if case_id == "switch" else 3
    doc = {"schema_version": INPUT_VERSION, "case_id": case_id, "period_count": n, "seed": 20261002,
           "provenance": {"kind": "synthetic_workshop", "units": "model_currency", "description": "Synthetische Anbieter, Bilanzen, Kunden und Schäden; kein Deutschland-Ranking, keine realen Strategien oder kalibrierten Ausfallraten."},
           "insurers": [], "customer_groups": [], "peer_groups": [], "families": [], "assignments": {"baseline": [], "variant": []},
           "measures": {"baseline": [], "variant": []}, "damage_indicators": ["0.1"] * n}
    if case_id == "market":
        sources = seminar_case("price", n)["accounting_source"]["sectors"]
        for sector in NON_LIFE:
            doc["families"] += [family(sector + "_Zufall_I", sector, "vu.vrvu01", {"premium_factor": "6", "advertising_factor": "0"}),
                                family(sector + "_Festpreis", sector, "offer.fixed", {"price": "3", "advertising": "0"}),
                                family(sector + "_Preisantwort", sector, "offer.fixed", {"price": "1.5", "advertising": "0"})]
        doc["families"] += [family("Leben_Anlage", "life", "life.opening_assets_rate", {"rate_per_period": "0.0005"}),
                            family("Kranken_Bestand", "health", "health.declared_profile", {"price_per_policy": "3", "new_business": 1, "exits": 1})]
        for aid in range(1, count + 1):
            sectors = {sector: portfolio(n) for sector in NON_LIFE}
            sectors.update({sector: {"source": deepcopy(sources[sector])} for sector in ("life", "health")})
            doc["insurers"].append({"insurer_id": aid, "insurance_group_id": f"Gruppe_{aid}", "name": f"Modellversicherer {aid:02}", "sectors": sectors})
            for sector in NON_LIFE:
                doc["customer_groups"].append({"group_id": f"{sector}_K{aid:02}", "sector_id": sector, "quantity": "10", "initial_insurer_id": aid,
                    "insurance_threshold": "0.5", "risk_periods": [{"period": p, "loss": "2", "paid_share": "0.5"} for p in range(1, n + 1)]})
                doc["assignments"]["baseline"].append(assignment(aid, sector, sector + ("_Zufall_I" if aid % 2 else "_Festpreis")))
            doc["assignments"]["baseline"] += [assignment(aid, "life", "Leben_Anlage"), assignment(aid, "health", "Kranken_Bestand")]
        doc["assignments"]["variant"] = deepcopy(doc["assignments"]["baseline"])
        for item in doc["assignments"]["variant"]:
            if item["insurer_id"] == 1 and item["sector_id"] == "motor":
                item["end"] = 5
        doc["assignments"]["variant"] += [assignment(1, "motor", "motor_Preisantwort", 6, 20), assignment(1, "motor", "motor_Zufall_I", 21)]
        doc["measures"]["variant"] = [{"measure_id": "Aufnahmeausbau", "insurer_id": 1, "sector_id": "motor", "decision_period": 6, "lead_periods": 2, "duration": 3, "cost": "3", "overrides": {"capacity": "60"}}]
    else:
        doc["families"] = [family("Anfang_null", "motor", "offer.fixed", {"price": "0", "advertising": "0"})]
        prices = [3, 2] if case_id == "switch" else [2, 2, 3]
        for aid, price in enumerate(prices, 1):
            liability = "20" if case_id == "switch" and aid == 1 else "0"
            capacity = "20" if case_id == "switch" else str([6, 8, 4][aid - 1])
            source = portfolio(n, assets="100", liability=liability, capacity=capacity)
            if case_id == "switch" and n >= 6:
                source["periods"][5]["operating_expense"] = "2" if aid == 1 else "1"
                source["periods"][5]["old_claims_paid"] = "5" if aid == 1 else "0"
            doc["insurers"].append({"insurer_id": aid, "insurance_group_id": f"Gruppe_{aid}", "name": f"Handfall VU{aid}", "sectors": {"motor": source}})
            fid = "Festpreis_" + str(price)
            if not any(item["family_id"] == fid for item in doc["families"]):
                doc["families"].append(family(fid, "motor", "offer.fixed", {"price": str(price), "advertising": "0"}))
            doc["assignments"]["baseline"] += [assignment(aid, "motor", "Anfang_null", end=5), assignment(aid, "motor", fid, 6)]
        quantities, losses = ([10], [40]) if case_id == "switch" else ([6, 8, 5], [9, 4, 7])
        for i, (quantity, loss) in enumerate(zip(quantities, losses), 1):
            doc["customer_groups"].append({"group_id": f"G{i}", "sector_id": "motor", "quantity": str(quantity),
                "initial_insurer_id": (1 if case_id == "switch" else i) if i <= 2 else None, "insurance_threshold": "1",
                "risk_periods": [{"period": p, "loss": str(loss) if p == 6 else "0", "paid_share": "1"} for p in range(1, n + 1)]})
        doc["assignments"]["variant"] = deepcopy(doc["assignments"]["baseline"])
    if count >= 2:
        doc["peer_groups"] = [{"group_id": "Vergleich_A", "label": "VU1 und VU2", "insurer_ids": [1, 2]},
                              {"group_id": "Vergleich_B", "label": "VU2 und letzte VU (überlappend)", "insurer_ids": sorted({2, count})}]
    return doc
