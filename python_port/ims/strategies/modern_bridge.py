"""Declared modern exposure/billing bridge around bounded, mapped rule kernels."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_EVEN, localcontext
import re

from ims.accounting.four_sector_balance import build_four_sector_balance
from ims.accounting.management_case import digest
from ims.model.entities import Insurer
from ims.model.vn_insurance_rules import VNBestInfoInsuranceRuleParameters, apply_vn_best_info_insurance_rule
from ims.model.vu_rules import VURandomUniformRuleParameters, apply_vu_random_uniform_rule

INPUT_VERSION = "ims.modern-strategy-input.v1"
RESULT_VERSION = "ims.modern-strategy-result.v1"
TIME_CONTRACT = "inclusive_action_before_billing_opening_period_1_common_prefix_1_5"
NON_LIFE = ("motor", "property_liability")
HORIZONS = (2, 5, 10, 25, 50, 100)
Q = Decimal("0.0001")
_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,39}\Z")
_NUMBER = re.compile(r"-?(?:0|[1-9][0-9]{0,11})(?:\.[0-9]{1,6})?\Z")
# actor, permitted sectors, channel, exact parameter names
RULES = {
    "vu.vrvu01": ("insurer", NON_LIFE, "offer", ("premium_factor", "advertising_factor", "premium_factor_shock", "advertising_factor_shock")),
    "vn.vrvn06": ("policyholder", NON_LIFE, "selection", ("insurance_threshold", "insurance_threshold_shock")),
    "life.opening_assets_rate": ("insurer", ("life",), "investment", ("rate_per_period",)),
    "health.opening_policy_price": ("insurer", ("health",), "pricing", ("amount_per_opening_policy",)),
    "health.declared_new_business": ("insurer", ("health",), "new_business", ("count",)),
    "health.declared_exits": ("policyholder", ("health",), "exits", ("count",)),
}


class ContractError(ValueError):
    def __init__(self, path: str, message: str):
        super().__init__(message)
        self.path = path


def exact(value: object, fields: set[str], path: str) -> dict:
    if not isinstance(value, dict) or set(value) != fields:
        raise ContractError(path, "Vollständige benannte Felder erforderlich; unbekannte Felder sind gesperrt")
    return value


def identifier(value: object, path: str) -> str:
    if not isinstance(value, str) or not _ID.fullmatch(value):
        raise ContractError(path, "Benannte ID mit höchstens 40 ASCII-Zeichen erforderlich")
    return value


def number(value: object, path: str, minimum: Decimal = Decimal(0), maximum: Decimal = Decimal("1000000")) -> Decimal:
    if type(value) is not str or not _NUMBER.fullmatch(value):
        raise ContractError(path, "Endliche Dezimalzeichenfolge mit höchstens sechs Nachkommastellen erforderlich")
    result = Decimal(value)
    if not minimum <= result <= maximum:
        raise ContractError(path, f"Wert muss zwischen {minimum} und {maximum} liegen")
    return result


def integer(value: object, path: str, minimum: int = 0, maximum: int = 100) -> int:
    if type(value) is not int or not minimum <= value <= maximum:
        raise ContractError(path, f"Ganzzahl von {minimum} bis {maximum} erforderlich")
    return value


def money(value: Decimal | str | float) -> str:
    return format(Decimal(str(value)).quantize(Q, rounding=ROUND_HALF_EVEN), ".4f")


@dataclass(frozen=True, slots=True)
class Assignment:
    target: str
    sector: str
    channel: str
    rule: str
    start: int
    end: int
    parameters: dict


def active(assignments: list[Assignment], target: str, sector: str, channel: str, period: int) -> Assignment | None:
    return next((item for item in assignments if (item.target, item.sector, item.channel) == (target, sector, channel) and item.start <= period <= item.end), None)


def parse(value: object) -> tuple[dict, dict[str, list[Assignment]]]:
    doc = exact(value, {"schema_version", "case_id", "period_count", "insurer_id", "time_contract", "units", "insurer_groups", "policyholder_groups", "health_group", "market_periods", "strategies", "accounting_source"}, "$")
    if doc["schema_version"] != INPUT_VERSION or doc["time_contract"] != TIME_CONTRACT or doc["units"] != "declared_model_currency_per_covered_exposure_per_period":
        raise ContractError("$", "Bestätigter moderner Einheiten-/Zeitvertrag erforderlich")
    identifier(doc["case_id"], "$.case_id")
    n = integer(doc["period_count"], "$.period_count", 2)
    if n not in HORIZONS:
        raise ContractError("$.period_count", "Freigegebener Horizont erforderlich")
    focus = integer(doc["insurer_id"], "$.insurer_id", 1, 25)
    offers = doc["insurer_groups"]
    if not isinstance(offers, list) or not 1 <= len(offers) <= 25:
        raise ContractError("$.insurer_groups", "1–25 ausdrücklich benannte VU-Gruppen erforderlich")
    group_ids, insurer_ids = set(), set()
    for index, offer in enumerate(offers):
        path = f"$.insurer_groups[{index}]"
        exact(offer, {"group_id", "insurer_id", "opening_prices", "opening_advertising"}, path)
        group = identifier(offer["group_id"], path + ".group_id")
        actor = integer(offer["insurer_id"], path + ".insurer_id", 1, 25)
        if group in group_ids or actor in insurer_ids:
            raise ContractError(path, "VU-ID und Gruppen-ID dürfen nicht doppelt sein")
        group_ids.add(group); insurer_ids.add(actor)
        for field in ("opening_prices", "opening_advertising"):
            exact(offer[field], set(NON_LIFE), path + "." + field)
            for sector, amount in offer[field].items(): number(amount, path + "." + field + "." + sector)
    if focus not in insurer_ids:
        raise ContractError("$.insurer_id", "Bilanzierte VU fehlt in der benannten Angebotsmenge")
    groups = doc["policyholder_groups"]
    if not isinstance(groups, list) or not 1 <= len(groups) <= 50:
        raise ContractError("$.policyholder_groups", "1–50 benannte VN-Expositionsgruppen erforderlich")
    for index, group in enumerate(groups):
        path = f"$.policyholder_groups[{index}]"
        exact(group, {"group_id", "sector_id", "exposure", "initial_insurer_id", "initial_insured"}, path)
        key = identifier(group["group_id"], path + ".group_id")
        if key in group_ids or group["sector_id"] not in NON_LIFE:
            raise ContractError(path, "Eindeutige Gruppe und benannte Nichtleben-Sparte erforderlich")
        group_ids.add(key)
        exposure = number(group["exposure"], path + ".exposure", Q)
        if exposure.as_tuple().exponent < -4:
            raise ContractError(path + ".exposure", "Expositionsgewicht mit höchstens vier Nachkommastellen erforderlich")
        if type(group["initial_insured"]) is not bool or type(group["initial_insurer_id"]) is not int or group["initial_insurer_id"] not in insurer_ids:
            raise ContractError(path, "Expliziter Anfangsvertrag mit bekanntem Anbieter erforderlich")
    health = exact(doc["health_group"], {"group_id", "opening_policies"}, "$.health_group")
    if identifier(health["group_id"], "$.health_group.group_id") in group_ids:
        raise ContractError("$.health_group", "Kranken-Gruppe muss eindeutig sein")
    group_ids.add(health["group_id"])
    integer(health["opening_policies"], "$.health_group.opening_policies", 0, 1000000)
    periods = doc["market_periods"]
    if not isinstance(periods, list) or len(periods) != n:
        raise ContractError("$.market_periods", "Alle Periodenkontexte genau einmal erforderlich")
    for index, context in enumerate(periods):
        path = f"$.market_periods[{index}]"
        exact(context, {"period", "damage_indicator", "change_shock", "draws"}, path)
        if type(context["period"]) is not int or context["period"] != index + 1 or type(context["change_shock"]) is not bool:
            raise ContractError(path, "Lückenlose Perioden und expliziter Schockstatus erforderlich")
        number(context["damage_indicator"], path + ".damage_indicator", Decimal(0), Decimal(1))
        exact(context["draws"], {offer["group_id"] for offer in offers}, path + ".draws")
        for key, draws in context["draws"].items():
            if not isinstance(draws, list) or len(draws) != 4:
                raise ContractError(path + ".draws." + key, "Vier vollständig enthaltene Gleichverteilungswerte erforderlich")
            for draw in draws: number(draw, path + ".draws." + key, Decimal(0), Decimal(1))
    assignments: dict[str, list[Assignment]] = {}
    exact(doc["strategies"], {"baseline", "variant"}, "$.strategies")
    offer_ids = {offer["group_id"] for offer in offers}
    nonlife_ids = {group["group_id"]: group["sector_id"] for group in groups}
    for side, entries in doc["strategies"].items():
        if not isinstance(entries, list) or len(entries) > 300:
            raise ContractError("$.strategies." + side, "Höchstens 300 explizite Zuordnungen erforderlich")
        parsed = []
        for index, item in enumerate(entries):
            path = f"$.strategies.{side}[{index}]"
            exact(item, {"actor_type", "target_id", "sector_id", "strategy_id", "period_from", "period_through", "parameters"}, path)
            rule = item["strategy_id"]
            if type(rule) is not str or rule not in RULES:
                raise ContractError(path + ".strategy_id", "Nur quellenkartierte begrenzte Strategien sind ausführbar")
            actor, sectors, channel, fields = RULES[rule]
            target, sector = item["target_id"], item["sector_id"]
            if type(target) is not str or type(sector) is not str or item["actor_type"] != actor or sector not in sectors:
                raise ContractError(path, "Akteur, Gruppe und Strategiekanal passen nicht zusammen")
            permitted = target in offer_ids if actor == "insurer" else nonlife_ids.get(target) == sector if sector in NON_LIFE else target == health["group_id"]
            if not permitted or (sector in ("life", "health") and actor == "insurer" and next(offer["insurer_id"] for offer in offers if offer["group_id"] == target) != focus):
                raise ContractError(path, "Zielgruppe gehört nicht zum bilanzierten Strategiekanal")
            start = integer(item["period_from"], path + ".period_from", 1, n)
            end = integer(item["period_through"], path + ".period_through", start, n)
            parameters = exact(item["parameters"], set(fields), path + ".parameters")
            for field, amount in parameters.items():
                if field == "count": integer(amount, path + ".parameters.count", 0, 1000)
                else:
                    lower = Decimal(-1) if field == "rate_per_period" else Decimal(0)
                    upper = Decimal(1) if field == "rate_per_period" or "threshold" in field else Decimal("1000000")
                    number(amount, path + ".parameters." + field, lower, upper)
            candidate = Assignment(target, sector, channel, rule, start, end, parameters)
            if any((old.target, old.sector, old.channel) == (target, sector, channel) and max(old.start, start) <= min(old.end, end) for old in parsed):
                raise ContractError(path, "Inklusive Strategiefenster dieses Gruppenkanals überschneiden sich")
            parsed.append(candidate)
        assignments[side] = parsed
    keys = {(item.target, item.sector, item.channel) for values in assignments.values() for item in values}
    for period in range(1, min(n, 5) + 1):
        for key in keys:
            left, right = (active(assignments[side], *key, period) for side in ("baseline", "variant"))
            if (None if left is None else (left.rule, left.parameters)) != (None if right is None else (right.rule, right.parameters)):
                raise ContractError("$.strategies", "Beide Varianten benötigen denselben Strategieanfang in Perioden 1–5")
    ledger = doc["accounting_source"]
    checked = build_four_sector_balance(ledger).to_dict()
    if not checked["valid"]:
        issue = checked["issues"][0]
        raise ContractError("$.accounting_source" + issue["path"].removeprefix("$"), issue["message"])
    if checked["insurer_id"] != focus or checked["period_count"] != n or ledger["variant_id"] != "baseline" or ledger["sectors"]["health"]["opening"]["opening_active_policies"] != health["opening_policies"]:
        raise ContractError("$.accounting_source", "Gemeinsame VU, Horizont, Baseline und Kranken-Anfangsbestand erforderlich")
    return doc, assignments


def _calculate(doc: dict, assignments: dict[str, list[Assignment]]) -> dict:
    n, focus = doc["period_count"], doc["insurer_id"]
    offers = sorted(doc["insurer_groups"], key=lambda item: item["insurer_id"])
    focus_group = next(item["group_id"] for item in offers if item["insurer_id"] == focus)
    sides, generated, traces = {}, {}, {}
    for side in ("baseline", "variant"):
        ledger = deepcopy(doc["accounting_source"])
        ledger["variant_id"] = side
        ledger["sectors"]["health"]["sources"]["variant_id"] = side
        selected = assignments[side]
        trace = []
        life_source = ledger["sectors"]["life"]
        if any(item.sector == "life" for item in selected):
            # A complete existing rate-source plan, not fabricated explicit returns.
            # Outside assigned windows preserve the original explicit-source flow:
            # mix is not allowed by the existing source contract, so require full coverage.
            rates = [active(selected, focus_group, "life", "investment", p) for p in range(1, n + 1)]
            if any(item is None for item in rates):
                raise ContractError("$.strategies." + side, "Lebens-Anlagesatz benötigt vollständige inklusive Periodenabdeckung")
            life_source["assumptions"]["investment"] = {"mode": "insurer_rule_on_opening_backing_assets", "windows": [{"start_period": p, "end_period": p, "rate_per_period": rates[p - 1].parameters["rate_per_period"]} for p in range(1, n + 1)]}
        for context in doc["market_periods"]:
            period = context["period"]
            prices, advertising = {}, {}
            for offer in offers:
                current = [active(selected, offer["group_id"], sector, "offer", period) for sector in NON_LIFE]
                factors = {}
                for field in RULES["vu.vrvu01"][3]:
                    factors[field] = [float(item.parameters[field]) if item else 0.0 for item in current]
                parameters = VURandomUniformRuleParameters(
                    premium_factor_normal=factors["premium_factor"], advertising_factor_normal=factors["advertising_factor"],
                    premium_factor_shock=factors["premium_factor_shock"], advertising_factor_shock=factors["advertising_factor_shock"])
                opening_prices = [float(offer["opening_prices"][sector]) for sector in NON_LIFE]
                opening_advertising = [float(offer["opening_advertising"][sector]) for sector in NON_LIFE]
                result = apply_vu_random_uniform_rule(Insurer(offer["insurer_id"], premiums_current_sector=opening_prices, advertising_current_sector=opening_advertising), parameters, period=period,
                    random_draws=[float(draw) for draw in context["draws"][offer["group_id"]]], interest_rate=0.0, change_shock=context["change_shock"])
                prices[offer["insurer_id"]] = [money(result.premiums_current_sector[i] if current[i] else opening_prices[i]) for i in range(2)]
                advertising[offer["insurer_id"]] = [money(result.advertising_current_sector[i] if current[i] else opening_advertising[i]) for i in range(2)]
            for index, sector in enumerate(NON_LIFE):
                exposure, premium, decisions = Decimal(0), Decimal(0), []
                for group in sorted(doc["policyholder_groups"], key=lambda item: item["group_id"]):
                    if group["sector_id"] != sector: continue
                    assignment = active(selected, group["group_id"], sector, "selection", period)
                    if assignment is None:
                        insured, provider = group["initial_insured"], group["initial_insurer_id"]
                    else:
                        params = assignment.parameters
                        initial_price = prices[group["initial_insurer_id"]][index]
                        initial = [{"sector_index": i, "insured": group["initial_insured"], "insurer_id": group["initial_insurer_id"] if group["initial_insured"] else None, "premium": float(initial_price) if group["initial_insured"] else None} for i in range(2)]
                        choice = apply_vn_best_info_insurance_rule(VNBestInfoInsuranceRuleParameters([float(params["insurance_threshold"])] * 2, [float(params["insurance_threshold_shock"])] * 2), period=period,
                            market_damage_indicator=float(context["damage_indicator"]), insurer_inputs=[{"insurer_id": offer["insurer_id"], "premiums_current_sector": [float(price) for price in prices[offer["insurer_id"]]]} for offer in offers],
                            initial_decisions=initial, change_shock=context["change_shock"], information_cost_per_insurer=0.0)
                        insured, provider = choice.insured[index], choice.chosen_insurer_ids[index]
                    weight = Decimal(group["exposure"]) if insured and provider == focus else Decimal(0)
                    booked = Decimal(money(weight * Decimal(prices[focus][index])))
                    exposure += weight; premium += booked
                    decisions.append({"group_id": group["group_id"], "strategy_id": assignment.rule if assignment else "declared_initial_contract", "insured": insured, "chosen_insurer_id": provider if insured else None,
                        "declared_exposure": group["exposure"], "covered_exposure_at_billed_insurer": money(weight), "booked_premium": money(booked)})
                row = ledger["sectors"][sector]["periods"][period - 1]
                row["premium_income"] = money(premium)
                row["operating_expense"] = money(Decimal(row["operating_expense"]) + Decimal(advertising[focus][index]))
                offer_assignment = active(selected, focus_group, sector, "offer", period)
                trace.append({"period": period, "sector_id": sector, "insurer_group": focus_group, "strategy_id": offer_assignment.rule if offer_assignment else "declared_opening_offer",
                    "parameters": deepcopy(offer_assignment.parameters) if offer_assignment else {}, "draws": context["draws"][focus_group], "quoted_price": prices[focus][index], "covered_exposure": money(exposure),
                    "premium_income": row["premium_income"], "advertising_expense": advertising[focus][index], "group_decisions": decisions})
            health_source = ledger["sectors"]["health"]["sources"]
            for channel, target in (("pricing", focus_group), ("new_business", focus_group), ("exits", doc["health_group"]["group_id"])):
                assignment = active(selected, target, "health", channel, period)
                if assignment:
                    if channel == "pricing":
                        # Normalize potentially long windows to exact one-period windows.
                        health_source[channel]["windows"] = [{"start_period": p, "end_period": p, "amount_per_opening_policy": next(win["amount_per_opening_policy"] for win in health_source[channel]["windows"] if win["start_period"] <= p <= win["end_period"])} for p in range(1, n + 1)]
                        health_source[channel]["windows"][period - 1]["amount_per_opening_policy"] = assignment.parameters["amount_per_opening_policy"]
                    else: health_source[channel]["periods"][period - 1]["count"] = assignment.parameters["count"]
        report = build_four_sector_balance(ledger).to_dict()
        if not report["valid"]:
            issue = report["issues"][0]
            raise ContractError("$.generated." + side + issue["path"].removeprefix("$"), issue["message"])
        for entry in trace:
            sector_result = next(item for item in report["sectors"] if item["sector_id"] == entry["sector_id"])
            entry["model_balance"] = sector_result["rows"][entry["period"] - 1]
        for sector in ("life", "health"):
            sector_result = next(item for item in report["sectors"] if item["sector_id"] == sector)
            health_opening = ledger["sectors"]["health"]["opening"]["opening_active_policies"]
            for period in range(1, n + 1):
                decisions = [item for item in selected if item.sector == sector and item.start <= period <= item.end]
                model_row = sector_result["rows"][period - 1]
                if sector == "life":
                    investment = life_source["assumptions"]["investment"]
                    if investment["mode"] == "insurer_rule_on_opening_backing_assets":
                        period_source = deepcopy(next(win for win in investment["windows"] if win["start_period"] <= period <= win["end_period"]))
                        period_source["opening_backing_assets"] = model_row["opening_assets"]
                        period_source["investment_result"] = money(Decimal(model_row["opening_assets"]) * Decimal(period_source["rate_per_period"]))
                    else: period_source = deepcopy(investment["periods"][period - 1])
                else:
                    source = ledger["sectors"]["health"]["sources"]
                    price = next(win["amount_per_opening_policy"] for win in source["pricing"]["windows"] if win["start_period"] <= period <= win["end_period"])
                    new_business, exits = (source[channel]["periods"][period - 1]["count"] for channel in ("new_business", "exits"))
                    period_source = {"period": period, "amount_per_opening_policy": price, "opening_policies": health_opening, "premium_income": money(Decimal(price) * health_opening), "new_business": new_business, "exits": exits,
                        "benefits_paid_exogenous": ledger["sectors"]["health"]["periods"][period - 1]["benefits_paid"]}
                    health_opening += new_business - exits
                trace.append({"period": period, "sector_id": sector, "insurer_group": focus_group,
                    "source_decisions": [{"strategy_id": item.rule, "target_id": item.target, "parameters": deepcopy(item.parameters), "channel": item.channel} for item in decisions],
                    "generated_period_source": period_source, "model_balance": model_row})
        trace.sort(key=lambda item: (item["period"], ("motor", "property_liability", "life", "health").index(item["sector_id"])))
        generated[side], sides[side], traces[side] = ledger, report, trace
    if sides["baseline"]["total_rows"][:min(n, 5)] != sides["variant"]["total_rows"][:min(n, 5)]:
        raise ContractError("$.strategies", "Gemeinsamer tatsächlicher Bilanzprefix 1–5 stimmt nicht überein")
    core = {"source_input": deepcopy(doc), "input_digest": digest(doc), "period_count": n, "insurer_id": focus, "scenario_id": doc["accounting_source"]["scenario_id"],
        "sides": sides, "generated_sources": generated, "decision_traces": traces,
        "coupling_scope": "approved_declared_modern_exposure_billing_with_mapped_kernels", "uncoupled_channels": ["historical_sector_identity", "full_insurer_market", "endogenous_claims_and_mortality", "life_policyholder_strategy", "cross_sector_funding", "unmapped_catalog_rules"],
        "regulatory_metrics": {"scr": None, "mcr": None, "coverage_ratio": None}}
    return {"schema_version": RESULT_VERSION, "valid": True, "issues": [], "content_digest": digest(core), **core, "writes_performed": False, "historical_runner_invoked": False, "partial_result_returned": False, "historical_full_equality_claim": False, "statutory_or_solvency_ii_claim": False}


def calculate(value: object) -> dict:
    try:
        with localcontext() as context:
            context.prec = 64
            doc, assignments = parse(value)
            return _calculate(doc, assignments)
    except ContractError as exc:
        return {"schema_version": RESULT_VERSION, "valid": False, "issues": [{"path": exc.path, "code": "modern_contract_invalid", "message": str(exc)}], "content_digest": None,
            "sides": {}, "generated_sources": {}, "decision_traces": {}, "partial_result_returned": False, "writes_performed": False, "historical_runner_invoked": False}


def contract_payload() -> dict:
    return {"schema_version": INPUT_VERSION, "time_contract": TIME_CONTRACT, "units": "declared_model_currency_per_covered_exposure_per_period", "supported_horizons": list(HORIZONS),
        "rules": [{"strategy_id": key, "actor_type": actor, "sector_ids": list(sectors), "channel": channel, "parameter_fields": list(fields)} for key, (actor, sectors, channel, fields) in RULES.items()],
        "rounding": "float_kernel_to_decimal_4_half_even_then_decimal_billing", "historical_full_equality_claim": False, "regulatory_metrics_enabled": False}
