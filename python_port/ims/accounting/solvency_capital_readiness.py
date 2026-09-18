"""Model-only management limits with an explicit regulatory capital gate."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, localcontext

from ims.accounting.solvency_model_balance import build_solvency_model_balance
from ims.accounting.solvency_risk_aggregation import (
    SOLVENCY_RISK_AGGREGATION_INPUT_VERSION,
    SOLVENCY_RISK_AGGREGATION_RESULT_VERSION,
    build_solvency_risk_aggregation,
)


SOLVENCY_CAPITAL_READINESS_INPUT_VERSION = "ims.solvency-capital-readiness-input.v1"
SOLVENCY_CAPITAL_READINESS_RESULT_VERSION = "ims.solvency-capital-readiness-result.v1"
_INPUT_FIELDS = frozenset(("schema_version", "solvency_risk_aggregation_input", "management_limits"))
_LIMIT_FIELDS = frozenset((
    "source_kind", "assumption_note", "max_net_model_stress_loss",
    "min_remaining_model_equity_proxy",
))
_AMOUNT = re.compile(r"(?:0|[1-9][0-9]{0,11})(?:\.[0-9]{1,4})?\Z")
_SOURCE_KIND = "management_workshop_declared_not_regulatory"
_REVIEW_START = date(2027, 1, 30)
_BLOCKERS = (
    ("reporting_date_and_legal_basis_unverified", "Szenariodatum ist kein belegter aufsichtsrechtlicher Stichtag."),
    ("valuation_and_technical_provisions_missing", "Marktwerte, Best Estimate und Risikomarge fehlen."),
    ("eligible_own_funds_missing", "Modell-Eigenkapital ist nicht als anrechenbare Eigenmittel bewertet."),
    ("scr_calibration_and_formula_missing", "99,5-%-Einjahreskalibrierung und Standardformel fehlen."),
    ("regulatory_loss_absorption_missing", "Technische und steuerliche Verlustabsorption sind nicht belegt."),
    ("mcr_inputs_and_floor_missing", "Netto-MCR-Eingaben, Kalibrierung und EUR-Untergrenze fehlen."),
    ("model_currency_to_eur_missing", "Eine belegte Umrechnung von Modellwaehrung in EUR fehlt."),
)
_REGULATORY_KEYS = (
    "eligible_own_funds", "scr", "mcr", "scr_coverage_ratio", "mcr_coverage_ratio",
)


@dataclass(frozen=True, slots=True)
class CapitalReadinessIssue:
    path: str
    code: str
    message: str

    def to_dict(self) -> dict[str, str]:
        return {"path": self.path, "code": self.code, "message": self.message}


@dataclass(frozen=True, slots=True)
class CapitalReadinessReport:
    core: dict[str, object] | None
    issues: tuple[CapitalReadinessIssue, ...]

    def to_dict(self) -> dict[str, object]:
        valid = self.core is not None and not self.issues
        core = self.core if valid else {
            "schema_version": SOLVENCY_CAPITAL_READINESS_RESULT_VERSION,
            "source_result_schema_version": SOLVENCY_RISK_AGGREGATION_RESULT_VERSION,
            "source_risk_aggregation_content_digest": None,
            "source_model_balance_content_digest": None,
            "input_digest": None,
            "insurer_id": None,
            "scenario_id": None,
            "variant_id": None,
            "checkpoint": None,
            "amount_unit": "model_currency_unit_not_eur",
            "review_applicability_window": None,
            "management_evaluation": None,
            "regulatory_metrics": _blocked_metrics(),
            "readiness_rows": [],
        }
        return {
            **core,
            "status": "ok" if valid else "error",
            "valid": valid,
            "content_digest": _digest(core) if valid else None,
            "issue_count": len(self.issues),
            "issues": [issue.to_dict() for issue in self.issues],
            "writes_performed": False,
            "runner_invoked": False,
            "statutory_balance_claim": False,
            "regulatory_own_funds_claim": False,
            "scr_or_mcr_calculated": False,
            "compliance_decision_enabled": False,
            "historical_full_equality_claim": False,
        }


def _digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    ).hexdigest()


def _amount(value: Decimal) -> str:
    return format(Decimal(0) if value.is_zero() else value, ".4f")


def _blocked_metrics() -> dict[str, object]:
    return {"status": "blocked_missing_regulatory_basis", **dict.fromkeys(_REGULATORY_KEYS)}


def _issue(issues: list[CapitalReadinessIssue], path: str, code: str, message: str) -> None:
    issues.append(CapitalReadinessIssue(path, code, message))


def _exact_fields(
    value: dict, expected: frozenset[str], path: str, issues: list[CapitalReadinessIssue],
) -> None:
    actual = {key for key in value if type(key) is str}
    for field in sorted(expected - actual):
        _issue(issues, f"{path}.{field}", "field_missing", f"Pflichtfeld fehlt: {field}")
    for field in sorted(actual - expected):
        _issue(issues, f"{path}.{field}", "field_unknown", f"Unbekanntes Feld: {field}")
    if len(actual) != len(value):
        _issue(issues, path, "field_name_invalid", "Feldnamen muessen Text sein")


def _parse_limits(value: object, issues: list[CapitalReadinessIssue]) -> dict[str, Decimal]:
    path = "$.management_limits"
    if type(value) is not dict:
        _issue(issues, path, "object_required", "Managementgrenzen-Objekt erforderlich")
        return {}
    _exact_fields(value, _LIMIT_FIELDS, path, issues)
    if value.get("source_kind") != _SOURCE_KIND:
        _issue(issues, f"{path}.source_kind", "source_kind_invalid", "Workshop-Szenarioquelle erforderlich")
    note = value.get("assumption_note")
    if type(note) is not str or not 1 <= len(note) <= 160 or note != note.strip() or not note.isprintable():
        _issue(
            issues, f"{path}.assumption_note", "note_invalid",
            "Druckbarer Annahmentext mit 1 bis 160 Zeichen erforderlich",
        )
    parsed: dict[str, Decimal] = {}
    for field in ("max_net_model_stress_loss", "min_remaining_model_equity_proxy"):
        candidate = value.get(field)
        if type(candidate) is not str or _AMOUNT.fullmatch(candidate) is None:
            _issue(
                issues, f"{path}.{field}", "amount_format_invalid",
                "Nichtnegativer Dezimaltext mit maximal vier Nachkommastellen erforderlich",
            )
        else:
            parsed[field] = Decimal(candidate)
    return parsed


def solvency_capital_readiness_contract_payload() -> dict[str, object]:
    return {
        "input_schema_version": SOLVENCY_CAPITAL_READINESS_INPUT_VERSION,
        "result_schema_version": SOLVENCY_CAPITAL_READINESS_RESULT_VERSION,
        "source_input_schema_version": SOLVENCY_RISK_AGGREGATION_INPUT_VERSION,
        "source_result_schema_version": SOLVENCY_RISK_AGGREGATION_RESULT_VERSION,
        "calculation_endpoint": "/api/accounting/solvency-capital-readiness",
        "management_source_kind": _SOURCE_KIND,
        "management_formula": (
            "remaining_model_equity_proxy = "
            "PR172.model_own_funds_proxy - PR175.net_model_stress_loss"
        ),
        "management_comparison": "inclusive_max_loss_and_min_remaining_model_equity",
        "amount_unit": "model_currency_unit_not_eur",
        "review_start_date": _REVIEW_START.isoformat(),
        "reference_date_is_regulatory_reporting_date": False,
        "regulatory_metrics_status": "blocked_missing_regulatory_basis",
        "blocked_regulatory_metrics": list(_REGULATORY_KEYS),
        "legal_sources": {
            "scr_calibration": "https://www.eiopa.europa.eu/rulebook/solvency-ii-single-rulebook/article-2188_en",
            "standard_formula": "https://www.eiopa.europa.eu/rulebook/solvency-ii-single-rulebook/article-2190_en",
            "basic_scr": "https://www.eiopa.europa.eu/rulebook/solvency-ii-single-rulebook/article-2191_en",
            "mcr": "https://www.eiopa.europa.eu/rulebook/solvency-ii-single-rulebook/article-2216_en",
            "review": (
                "https://www.eiopa.europa.eu/eiopa-completes-solvency-ii-review-mandate-"
                "final-guidelines-and-draft-technical-standards-revised-2026-07-15_en"
            ),
        },
        "writes_enabled": False,
        "runner_enabled": False,
        "regulatory_own_funds_claim": False,
        "scr_or_mcr_calculated": False,
        "compliance_decision_enabled": False,
        "historical_full_equality_claim": False,
    }


def build_solvency_capital_readiness(value: object) -> CapitalReadinessReport:
    """Check two workshop limits; keep all regulatory metrics blocked."""

    issues: list[CapitalReadinessIssue] = []
    if type(value) is not dict:
        _issue(issues, "$", "object_required", "Kapitalfreigabe-Eingang muss ein Objekt sein")
        return CapitalReadinessReport(None, tuple(issues))
    _exact_fields(value, _INPUT_FIELDS, "$", issues)
    if value.get("schema_version") != SOLVENCY_CAPITAL_READINESS_INPUT_VERSION:
        _issue(issues, "$.schema_version", "contract_value_mismatch", "Falsche Eingabeversion")
    limits = _parse_limits(value.get("management_limits"), issues)
    aggregation_input = value.get("solvency_risk_aggregation_input")
    aggregation = build_solvency_risk_aggregation(aggregation_input).to_dict()
    if not aggregation["valid"]:
        for item in aggregation["issues"]:
            _issue(issues, f"$.solvency_risk_aggregation_input{item['path'][1:]}", item["code"], item["message"])
    if issues:
        return CapitalReadinessReport(None, tuple(issues))

    balance_input = (
        aggregation_input["solvency_risk_modules_input"]
        ["solvency_scenario_shocks_input"]
        ["solvency_model_balance_input"]
    )
    balance = build_solvency_model_balance(balance_input).to_dict()
    if not balance["valid"] or balance["content_digest"] != aggregation["source_model_balance_content_digest"]:
        _issue(
            issues, "$.solvency_risk_aggregation_input", "source_digest_mismatch",
            "PR172-Quelle ist nicht identisch zum PR175-Digest",
        )
        return CapitalReadinessReport(None, tuple(issues))
    try:
        input_digest = _digest(value)
    except (TypeError, ValueError):
        _issue(issues, "$", "json_invalid", "Eingang muss kanonisch als JSON darstellbar sein")
        return CapitalReadinessReport(None, tuple(issues))

    with localcontext() as context:
        context.prec = 64
        own_funds = Decimal(balance["total_row"]["model_own_funds_proxy"])
        loss = Decimal(aggregation["totals"]["net_model_stress_loss"])
        remaining = own_funds - loss
        loss_limit_met = loss <= limits["max_net_model_stress_loss"]
        equity_floor_met = remaining >= limits["min_remaining_model_equity_proxy"]
        management = {
            "source_kind": _SOURCE_KIND,
            "assumption_note": value["management_limits"]["assumption_note"],
            "model_own_funds_proxy": _amount(own_funds),
            "net_model_stress_loss": _amount(loss),
            "remaining_model_equity_proxy": _amount(remaining),
            "max_net_model_stress_loss": _amount(limits["max_net_model_stress_loss"]),
            "min_remaining_model_equity_proxy": _amount(limits["min_remaining_model_equity_proxy"]),
            "loss_limit_met": loss_limit_met,
            "equity_floor_met": equity_floor_met,
            "both_limits_met": loss_limit_met and equity_floor_met,
            "decision_kind": "workshop_only_not_compliance",
        }
    reference_date = date.fromisoformat(balance["checkpoint"]["reference_date"])
    review_window = "before_2027_review" if reference_date < _REVIEW_START else "from_2027_review_unverified"
    blockers = [
        {"requirement_code": code, "status": "not_evidenced", "message": message}
        for code, message in _BLOCKERS
    ]
    if reference_date >= _REVIEW_START:
        blockers.append({
            "requirement_code": "review_2027_applicability_unverified",
            "status": "not_evidenced",
            "message": "Ab 30.01.2027 ist der revidierte Rechtsstand gesondert zu pruefen.",
        })
    return CapitalReadinessReport({
        "schema_version": SOLVENCY_CAPITAL_READINESS_RESULT_VERSION,
        "source_result_schema_version": aggregation["schema_version"],
        "source_risk_aggregation_content_digest": aggregation["content_digest"],
        "source_model_balance_content_digest": balance["content_digest"],
        "input_digest": input_digest,
        "insurer_id": aggregation["insurer_id"],
        "scenario_id": aggregation["scenario_id"],
        "variant_id": aggregation["variant_id"],
        "checkpoint": aggregation["checkpoint"],
        "amount_unit": "model_currency_unit_not_eur",
        "review_applicability_window": review_window,
        "management_evaluation": management,
        "regulatory_metrics": _blocked_metrics(),
        "readiness_rows": blockers,
    }, ())
