"""Explicit common-source assembly of existing four-sector models."""

from copy import deepcopy
from hashlib import sha256
import json

from ims.accounting.four_sector_balance import SECTOR_IDS, build_four_sector_balance
from ims.accounting.model_balance_contract import MODEL_BALANCE_CONTRACT_VERSION
from ims.api.life_workshop_presets import life_workshop_presets_payload

INPUT_VERSION = "ims.management-case-input.v1"
RESULT_VERSION = "ims.management-case-result.v1"
HORIZONS = (2, 5, 10, 25, 50, 100)


def digest(value: object) -> str:
    return sha256(json.dumps(value, sort_keys=True, ensure_ascii=True, allow_nan=False, separators=(",", ":")).encode("ascii")).hexdigest()


def source_contract(value: dict, note: str) -> dict:
    return {"schema_version": "ims.management-common-sources.v1", "insurer_id": value["insurer_id"],
            "scenario_id": value["scenario_id"], "variant_id": value["variant_id"], "period_count": len(value["sectors"]["motor"]["periods"]),
            "economic_assumption": note, "historical_market_binding": "unresolved_not_claimed",
            "sector_bindings": {sector: {"input_digest": digest(value["sectors"][sector]), "linkage": "explicit_declared_same_scenario"} for sector in SECTOR_IDS}}


def workshop_case(case_id: str, horizon: int, insurer_id: int) -> dict:
    if case_id not in ("inflation", "price", "capital") or type(horizon) is not int or horizon not in HORIZONS or type(insurer_id) is not int or not 1 <= insurer_id <= 25:
        raise ValueError("Deklarierter Fall, freigegebener Horizont und VU-ID 1–25 erforderlich")
    scenario_id = "management_" + case_id
    sides = {}
    for side in ("baseline", "variant"):
        sectors = {}
        for sector in ("motor", "property_liability"):
            sectors[sector] = {"schema_version": "ims.insurer-model-balance-input.v1", "model_balance_contract_schema_version": MODEL_BALANCE_CONTRACT_VERSION, "sector_taxonomy_schema_version": "ims.sector-taxonomy.v1", "source_kind": "explicit_scenario", "historical_mapping_status": "unresolved", "insurer_id": insurer_id, "sector_id": sector,
                               "opening": {"opening_cash": "10000", "opening_claim_liability": "1000", "opening_equity": "9000"},
                               "periods": [{"period": p, "premium_income": "250" if side == "variant" and case_id == "price" and sector == "motor" and p >= 6 else "300", "investment_income": "5", "claims_incurred": "150" if side == "variant" and case_id == "inflation" and p >= 6 else "100", "claims_paid": "150" if side == "variant" and case_id == "inflation" and p >= 6 else "100", "operating_expense": "100", "capital_contribution": "0", "capital_distribution": "0"} for p in range(1, horizon + 1)]}
        life = deepcopy(life_workshop_presets_payload()["cases"][0]["baseline"])
        life["insurer_id"] = insurer_id
        life["opening"] = {"opening_active_policies": 1, "opening_backing_assets": "10000", "opening_guarantee_liability": "1000", "opening_equity": "9000",
                           "cohorts": [{"cohort_id": "L", "issue_period": 0, "issue_term_periods": 100, "remaining_periods": 100, "active_policies": 1, "guaranteed_rate_per_period": "0", "guarantee_liability": "1000"}],
                           "policies": [{"policy_id": "L1", "cohort_id": "L", "issue_term_periods": 100, "remaining_periods": 100, "guaranteed_rate_per_period": "0", "guarantee_liability": "1000"}]}
        life["assumptions"].update(insurer_id=insurer_id, period_count=horizon)
        life["assumptions"]["investment"] = {"mode": "explicit_scenario", "periods": [{"period": p, "investment_result": "-5" if side == "variant" and case_id == "capital" and p >= 6 else "5"} for p in range(1, horizon + 1)]}
        life["assumptions"]["mortality"] = {"mode": "explicit_death_policy_ids", "periods": [{"period": p, "death_policy_ids": []} for p in range(1, horizon + 1)]}
        life["periods"] = [{"period": p, "policy_flows": [{"policy_id": "L1", "renewal_premiums_collected": "300", "renewal_liability_allocation": "0", "death_benefit_if_death": "0", "maturity_benefit_if_due": "1000" if p == 100 else "0"}], "new_business": [], "operating_expense_paid": "100", "capital_contribution": "0", "capital_distribution": "0"} for p in range(1, horizon + 1)]
        sectors["life"] = life
        health = {"schema_version": "ims.health-period-chain-input.v1", "health_sector_contract_schema_version": "ims.health-sector-contract.v2", "sector_taxonomy_schema_version": "ims.sector-taxonomy.v1", "source_kind": "versioned_health_period_chain", "historical_mapping_status": "unresolved", "insurer_id": insurer_id, "sector_id": "health",
                  "opening": {"opening_active_policies": 100, "opening_cash": "10000", "opening_benefit_liability": "200", "opening_equity": "9800"},
                  "sources": {"schema_version": "ims.health-period-sources-input.v1", "health_sector_contract_schema_version": "ims.health-sector-contract.v2", "sector_taxonomy_schema_version": "ims.sector-taxonomy.v1", "source_kind": "versioned_health_period_sources", "historical_mapping_status": "unresolved", "insurer_id": insurer_id, "sector_id": "health", "scenario_id": scenario_id, "variant_id": side, "period_count": horizon, "opening_active_policies": 100,
                              "new_business": {"actor_type": "market", "mode": "explicit_scenario_counts", "periods": [{"period": p, "count": 1} for p in range(1, horizon + 1)]},
                              "exits": {"actor_type": "policyholder", "mode": "explicit_scenario_counts", "periods": [{"period": p, "count": 1} for p in range(1, horizon + 1)]},
                              "pricing": {"actor_type": "insurer", "mode": "explicit_insurer_price_windows", "windows": [{"start_period": p, "end_period": p, "amount_per_opening_policy": "3"} for p in range(1, horizon + 1)]},
                              "benefits": {"actor_type": "exogenous", "mode": "explicit_benefit_cost_windows", "windows": [{"start_period": p, "end_period": p, "amount_per_opening_policy": "2.4" if side == "variant" and case_id == "inflation" and p >= 6 else "1.8"} for p in range(1, horizon + 1)]}},
                  "periods": [{"period": p, "benefits_paid": "240" if side == "variant" and case_id == "inflation" and p >= 6 else "180", "investment_result": "2", "operating_expense_paid": "30", "capital_contribution": "0", "capital_distribution": "0"} for p in range(1, horizon + 1)]}
        sectors["health"] = health
        value = {"schema_version": "ims.four-sector-balance-input.v1", "insurer_id": insurer_id, "scenario_id": scenario_id, "variant_id": side, "sectors": sectors}
        note = "Ausdrücklich gemeinsam deklarierter unkalibrierter Vier-Sparten-Workshop in Modellwährung. Anfangsbilanzen je Sparte getrennt; keine gemeinsame historische VN-Population und keine Zuordnung der anonymen historischen Positionen. Änderungen ab Periode 6 sind exogene Eingaben, keine ausgeführten Katalogstrategien."
        sides[side] = {"four_sector_input": value, "source_contract": source_contract(value, note)}
    return {"schema_version": INPUT_VERSION, "case_id": case_id, "sides": sides}


def calculate(value: object) -> dict:
    issues = []
    def problem(path, message): issues.append({"path": path, "code": "source_contract_invalid", "message": message})
    if not isinstance(value, dict) or set(value) != {"schema_version", "case_id", "sides"} or value.get("schema_version") != INPUT_VERSION or not isinstance(value.get("case_id"), str):
        problem("$", "Vollständiger Management-Quellenvertrag erforderlich")
    sides = value.get("sides") if isinstance(value, dict) else None
    if not isinstance(sides, dict) or set(sides) != {"baseline", "variant"}:
        problem("$.sides", "Baseline und Variante gemeinsam erforderlich")
        sides = {}
    results, contracts = {}, {}
    for side, envelope in sides.items():
        path = f"$.sides.{side}"
        if not isinstance(envelope, dict) or set(envelope) != {"four_sector_input", "source_contract"}:
            problem(path, "Teilrechnung und expliziter gemeinsamer Quellenvertrag erforderlich")
            continue
        source, contract = envelope["four_sector_input"], envelope["source_contract"]
        if not isinstance(source, dict) or not isinstance(source.get("sectors"), dict) or set(source["sectors"]) != set(SECTOR_IDS) or not isinstance(contract, dict):
            problem(path, "Vier vollständige Quellen und Bindungen erforderlich")
            continue
        note = contract.get("economic_assumption")
        if not isinstance(note, str) or not note.strip() or len(note) > 2000:
            problem(path + ".source_contract", "Wirtschaftliche Zusammengehörigkeit ausdrücklich erklären")
            continue
        try:
            expected = source_contract(source, note)
            if contract != expected or source.get("variant_id") != side:
                problem(path + ".source_contract", "Quellen-Digests, gemeinsame Identität oder Variante stimmen nicht überein")
                continue
        except (TypeError, ValueError, KeyError):
            problem(path, "Quellenvertrag nicht kanonisch darstellbar")
            continue
        report = build_four_sector_balance(source).to_dict()
        issues.extend({**issue, "path": path + ".four_sector_input" + issue["path"].removeprefix("$")} for issue in report["issues"])
        if report["valid"]:
            if report["period_count"] not in HORIZONS:
                problem(path, "Horizont nicht freigegeben")
            results[side], contracts[side] = report, deepcopy(contract)
    if len(results) == 2 and any(results["baseline"][field] != results["variant"][field] for field in ("insurer_id", "scenario_id", "period_count")):
        problem("$.sides", "Beide Seiten benötigen dieselbe VU, dasselbe deklarierte Szenario und denselben Horizont")
    base = {"schema_version": RESULT_VERSION, "valid": not issues, "issues": issues, "partial_result_returned": False, "writes_performed": False, "runner_invoked": False, "historical_full_equality_claim": False, "statutory_or_solvency_ii_claim": False}
    if issues:
        return {**base, "content_digest": None, "sides": {}, "source_contracts": {}, "period_count": 0}
    core = {"case_id": value["case_id"], "input_digest": digest(value), "source_input": deepcopy(value), "insurer_id": results["baseline"]["insurer_id"], "scenario_id": results["baseline"]["scenario_id"], "period_count": results["baseline"]["period_count"], "sides": results, "source_contracts": contracts,
            "coupling_scope": "additive_declared_sector_models_no_historical_market_mapping", "regulatory_metrics": {"scr": None, "mcr": None, "coverage_ratio": None}}
    return {**base, **core, "content_digest": digest(core)}


def declare_sources(value: object) -> dict:
    """Explicitly renew bindings after edits; never change source identities."""
    if not isinstance(value, dict) or set(value) != {"source_input", "explicit_common_source_declaration"} or value["explicit_common_source_declaration"] is not True:
        return {"valid": False, "issues": [{"path": "$", "code": "declaration_required", "message": "Gemeinsame wirtschaftliche Quellen ausdrücklich erklären"}], "content_digest": None, "source_input": None, "writes_performed": False}
    source = deepcopy(value["source_input"])
    try:
        if not isinstance(source, dict) or not isinstance(source["sides"], dict) or set(source["sides"]) != {"baseline", "variant"}: raise ValueError()
        for envelope in source["sides"].values():
            part = envelope["four_sector_input"]
            report = build_four_sector_balance(part).to_dict()
            if not report["valid"]: return {**report, "source_input": None}
            note = envelope["source_contract"]["economic_assumption"]
            envelope["source_contract"] = source_contract(part, note)
    except (KeyError, TypeError, ValueError):
        return {"valid": False, "issues": [{"path": "$", "code": "declaration_invalid", "message": "Vollständige Quellen und wirtschaftliche Erklärung erforderlich"}], "content_digest": None, "source_input": None, "writes_performed": False}
    checked = calculate(source)
    return {"valid": checked["valid"], "issues": checked["issues"], "source_input": source if checked["valid"] else None, "content_digest": digest(source) if checked["valid"] else None, "writes_performed": False}
