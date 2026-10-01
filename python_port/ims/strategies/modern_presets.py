"""Complete, uncalibrated modern workshop cases, including all explicit draws."""

from copy import deepcopy

from ims.accounting.management_case import workshop_case as accounting_case
from ims.strategies.modern_bridge import INPUT_VERSION, TIME_CONTRACT, HORIZONS

CASES = {
    "price": "Preis erhöhen: VN wählen das günstigere konkurrierende Angebot",
    "inflation": "Exogene Schaden-/Leistungskosten und begrenzte Beitragsreaktion",
    "capital": "Anlagesatz auf die tatsächlichen Lebens-Anfangsaktiva",
}


def assignment(target: str, sector: str, rule: str, parameters: dict, start: int, end: int) -> dict:
    return {"actor_type": "policyholder" if rule.startswith("vn.") or rule == "health.declared_exits" else "insurer", "target_id": target, "sector_id": sector,
        "strategy_id": rule, "period_from": start, "period_through": end, "parameters": parameters}


def workshop_case(case_id: str = "price", horizon: int = 100) -> dict:
    if type(case_id) is not str or case_id not in CASES or type(horizon) is not int or horizon not in HORIZONS:
        raise ValueError("Benannter moderner Seminarfall und freigegebener Horizont erforderlich")
    accounting = deepcopy(accounting_case("capital", horizon, 1)["sides"]["baseline"]["four_sector_input"])
    accounting["scenario_id"] = "modern_" + case_id
    health = accounting["sectors"]["health"]
    health["sources"]["scenario_id"] = accounting["scenario_id"]
    for sector in ("motor", "property_liability"):
        for row in accounting["sectors"][sector]["periods"]:
            claim = "45" if case_id == "inflation" and row["period"] >= 6 else "30"
            row.update(claims_incurred=claim, claims_paid=claim, operating_expense="30")
    if case_id == "inflation":
        for row in health["sources"]["benefits"]["windows"]:
            if row["start_period"] >= 6: row["amount_per_opening_policy"] = "2.4"
        for row in health["periods"]:
            if row["period"] >= 6: row["benefits_paid"] = "240"
    offers = [{"group_id": "VU1", "insurer_id": 1, "opening_prices": {"motor": "3", "property_liability": "3"}, "opening_advertising": {"motor": "0", "property_liability": "0"}},
        {"group_id": "VU2", "insurer_id": 2, "opening_prices": {"motor": "3.5" if case_id == "inflation" else "3.2", "property_liability": "3.5" if case_id == "inflation" else "3.2"}, "opening_advertising": {"motor": "0", "property_liability": "0"}}]
    groups = [{"group_id": sector + "_" + suffix, "sector_id": sector, "exposure": "50", "initial_insurer_id": 1, "initial_insured": True} for sector in ("motor", "property_liability") for suffix in ("A", "B")]
    base = [assignment("VU1", sector, "vu.vrvu01", {"premium_factor": "6", "advertising_factor": "0", "premium_factor_shock": "6", "advertising_factor_shock": "0"}, 1, horizon) for sector in ("motor", "property_liability")]
    base += [assignment(group["group_id"], group["sector_id"], "vn.vrvn06", {"insurance_threshold": "0.5", "insurance_threshold_shock": "0.5"}, 1, horizon) for group in groups]
    base += [assignment("VU1", "life", "life.opening_assets_rate", {"rate_per_period": "0.0005"}, 1, horizon),
        assignment("VU1", "health", "health.opening_policy_price", {"amount_per_opening_policy": "3"}, 1, horizon),
        assignment("VU1", "health", "health.declared_new_business", {"count": 1}, 1, horizon),
        assignment("health_A", "health", "health.declared_exits", {"count": 1}, 1, horizon)]
    variant = deepcopy(base)
    if horizon >= 6:
        for item in list(variant):
            change = None
            if case_id == "price" and item["sector_id"] == "motor" and item["target_id"] == "VU1":
                change = {"premium_factor": "7.2", "advertising_factor": "4", "premium_factor_shock": "7.2", "advertising_factor_shock": "4"}
            if case_id == "inflation" and item["strategy_id"] == "health.opening_policy_price": change = {"amount_per_opening_policy": "3.4"}
            if case_id == "inflation" and item["strategy_id"] == "vu.vrvu01": change = {"premium_factor": "6.8", "advertising_factor": "0", "premium_factor_shock": "6.8", "advertising_factor_shock": "0"}
            if case_id == "capital" and item["sector_id"] == "life": change = {"rate_per_period": "0.001"}
            if change:
                item["period_through"] = 5
                variant.append({**deepcopy(item), "period_from": 6, "period_through": horizon, "parameters": change})
    return {"schema_version": INPUT_VERSION, "case_id": case_id, "period_count": horizon, "insurer_id": 1, "time_contract": TIME_CONTRACT,
        "units": "declared_model_currency_per_covered_exposure_per_period", "insurer_groups": offers, "policyholder_groups": groups, "health_group": {"group_id": "health_A", "opening_policies": 100},
        "market_periods": [{"period": p, "damage_indicator": "0.1", "change_shock": False, "draws": {offer["group_id"]: ["0.5"] * 4 for offer in offers}} for p in range(1, horizon + 1)],
        "strategies": {"baseline": base, "variant": variant}, "accounting_source": accounting}
