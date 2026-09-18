"""Small, scenario-calibrated model stresses on validated PR173 exposures."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP, localcontext

from ims.accounting.solvency_scenario_shocks import (
    SOLVENCY_SHOCK_INPUT_VERSION,
    SOLVENCY_SHOCK_RESULT_VERSION,
    build_solvency_scenario_shocks,
    solvency_scenario_shocks_contract_payload,
)


SOLVENCY_RISK_MODULE_INPUT_VERSION = "ims.solvency-risk-modules-input.v1"
SOLVENCY_RISK_MODULE_RESULT_VERSION = "ims.solvency-risk-modules-result.v1"
_INPUT_FIELDS = frozenset(("schema_version", "solvency_scenario_shocks_input", "module_parameters"))
_PARAMETER_FIELDS = frozenset((
    "module_id", "module_kind", "exposure_id", "stress_rate",
    "parameter_source_kind", "assumption_note",
))
_IDENTIFIER = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,39}\Z")
_RATE = re.compile(r"(?:0|1)(?:\.[0-9]{1,4})?\Z")
_QUANTUM = Decimal("0.0001")
_SOURCE_KIND = "scenario_declared_not_regulatory"


@dataclass(frozen=True, slots=True)
class RiskModuleIssue:
    path: str
    code: str
    message: str

    def to_dict(self) -> dict[str, str]:
        return {"path": self.path, "code": self.code, "message": self.message}


@dataclass(frozen=True, slots=True)
class RiskModuleReport:
    core: dict[str, object] | None
    issues: tuple[RiskModuleIssue, ...]

    def to_dict(self) -> dict[str, object]:
        valid = self.core is not None and not self.issues
        core = self.core if valid else {
            "schema_version": SOLVENCY_RISK_MODULE_RESULT_VERSION,
            "source_result_schema_version": SOLVENCY_SHOCK_RESULT_VERSION,
            "source_exposure_content_digest": None,
            "source_model_balance_content_digest": None,
            "input_digest": None,
            "insurer_id": None,
            "scenario_id": None,
            "variant_id": None,
            "checkpoint": None,
            "amount_unit": "model_currency_unit_not_eur",
            "module_rows": [],
            "exposure_rows": [],
            "calibration_status": "scenario_only_not_regulatory",
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
            "regulatory_own_funds_claim": False,
            "scr_or_mcr_calculated": False,
            "capital_aggregation_performed": False,
            "compliance_decision_enabled": False,
            "historical_full_equality_claim": False,
        }


def _digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    ).hexdigest()


def _amount(value: Decimal) -> str:
    return format(Decimal(0) if value.is_zero() else value, ".4f")


def _issue(issues: list[RiskModuleIssue], path: str, code: str, message: str) -> None:
    issues.append(RiskModuleIssue(path, code, message))


def _exact_fields(
    value: dict, expected: frozenset[str], path: str, issues: list[RiskModuleIssue],
) -> None:
    actual = {key for key in value if type(key) is str}
    for field in sorted(expected - actual):
        _issue(issues, f"{path}.{field}", "field_missing", f"Pflichtfeld fehlt: {field}")
    for field in sorted(actual - expected):
        _issue(issues, f"{path}.{field}", "field_unknown", f"Unbekanntes Feld: {field}")
    if len(actual) != len(value):
        _issue(issues, path, "field_name_invalid", "Feldnamen muessen Text sein")


def _identifier(value: object, path: str, issues: list[RiskModuleIssue]) -> str | None:
    if type(value) is not str or _IDENTIFIER.fullmatch(value) is None:
        _issue(issues, path, "identifier_invalid", "ASCII-Kennung mit 1 bis 40 Zeichen erforderlich")
        return None
    return value


def _parameters(value: object, issues: list[RiskModuleIssue]) -> list[dict[str, object]]:
    if type(value) is not list or len(value) > 40:
        _issue(issues, "$.module_parameters", "module_count_invalid", "Hoestens 40 Modellmodule zulaessig")
        return []
    parsed: list[dict[str, object]] = []
    seen_modules: set[str] = set()
    seen_exposures: set[str] = set()
    driver_targets = solvency_scenario_shocks_contract_payload()["driver_targets"]
    for index, item in enumerate(value):
        path = f"$.module_parameters[{index}]"
        if type(item) is not dict:
            _issue(issues, path, "object_required", "Modulparameter muss ein Objekt sein")
            continue
        _exact_fields(item, _PARAMETER_FIELDS, path, issues)
        module_id = _identifier(item.get("module_id"), f"{path}.module_id", issues)
        exposure_id = _identifier(item.get("exposure_id"), f"{path}.exposure_id", issues)
        module_kind = item.get("module_kind")
        if type(module_kind) is not str or module_kind not in driver_targets:
            _issue(issues, f"{path}.module_kind", "module_kind_invalid", "Unbekanntes Modellmodul")
        rate_text = item.get("stress_rate")
        rate: Decimal | None = None
        if type(rate_text) is not str or _RATE.fullmatch(rate_text) is None:
            _issue(issues, f"{path}.stress_rate", "rate_format_invalid", "Dezimaltext von 0 bis 1 mit maximal vier Nachkommastellen erforderlich")
        else:
            rate = Decimal(rate_text)
            if rate > 1:
                _issue(issues, f"{path}.stress_rate", "rate_out_of_range", "Stresssatz darf 1 nicht uebersteigen")
        if item.get("parameter_source_kind") != _SOURCE_KIND:
            _issue(issues, f"{path}.parameter_source_kind", "source_kind_invalid", "Szenariodeklaration erforderlich")
        note = item.get("assumption_note")
        if type(note) is not str or not 1 <= len(note) <= 160 or note != note.strip() or not note.isprintable():
            _issue(issues, f"{path}.assumption_note", "note_invalid", "Druckbarer Annahmentext mit 1 bis 160 Zeichen erforderlich")
        if module_id is not None:
            if module_id in seen_modules:
                _issue(issues, f"{path}.module_id", "module_duplicate", "Modulkennung mehrfach angegeben")
            seen_modules.add(module_id)
        if exposure_id is not None:
            if exposure_id in seen_exposures:
                _issue(issues, f"{path}.exposure_id", "exposure_stressed_twice", "Teilbestand darf nur einmal gestresst werden")
            seen_exposures.add(exposure_id)
        parsed.append({
            "module_id": module_id, "module_kind": module_kind,
            "exposure_id": exposure_id, "stress_rate": rate,
            "assumption_note": note, "path": path,
        })
    return parsed


def solvency_risk_modules_contract_payload() -> dict[str, object]:
    return {
        "input_schema_version": SOLVENCY_RISK_MODULE_INPUT_VERSION,
        "result_schema_version": SOLVENCY_RISK_MODULE_RESULT_VERSION,
        "source_input_schema_version": SOLVENCY_SHOCK_INPUT_VERSION,
        "source_result_schema_version": SOLVENCY_SHOCK_RESULT_VERSION,
        "calculation_endpoint": "/api/accounting/solvency-risk-modules",
        "module_targets": solvency_scenario_shocks_contract_payload()["driver_targets"],
        "parameter_source_kind": _SOURCE_KIND,
        "stress_rate_range": "0_to_1_inclusive_decimal_string_4_fraction",
        "rounding": "ROUND_HALF_UP_to_4_fractional_places_once_per_exposure",
        "amount_unit": "model_currency_unit_not_eur",
        "max_modules_per_exposure": 1,
        "source_shocks_required_empty": True,
        "model_calculation_enabled": True,
        "writes_enabled": False,
        "runner_enabled": False,
        "regulatory_own_funds_claim": False,
        "scr_or_mcr_calculated": False,
        "capital_aggregation_performed": False,
        "compliance_decision_enabled": False,
        "historical_full_equality_claim": False,
    }


def build_solvency_risk_modules(value: object) -> RiskModuleReport:
    """Validate a PR173 baseline, then calculate isolated model stress rows."""

    issues: list[RiskModuleIssue] = []
    if type(value) is not dict:
        _issue(issues, "$", "object_required", "Modul-Eingang muss ein Objekt sein")
        return RiskModuleReport(None, tuple(issues))
    _exact_fields(value, _INPUT_FIELDS, "$", issues)
    if value.get("schema_version") != SOLVENCY_RISK_MODULE_INPUT_VERSION:
        _issue(issues, "$.schema_version", "contract_value_mismatch", "Falsche Eingabeversion")
    source_input = value.get("solvency_scenario_shocks_input")
    baseline = build_solvency_scenario_shocks(source_input).to_dict()
    if not baseline["valid"]:
        for item in baseline["issues"]:
            _issue(issues, f"$.solvency_scenario_shocks_input{item['path'][1:]}", item["code"], item["message"])
    if type(source_input) is dict and source_input.get("shocks") != []:
        _issue(issues, "$.solvency_scenario_shocks_input.shocks", "source_shocks_not_empty", "PR173-Quelle muss ungeschockt sein")
    parameters = _parameters(value.get("module_parameters"), issues)
    if issues:
        return RiskModuleReport(None, tuple(issues))

    exposures = {row["exposure_id"]: row for row in baseline["exposure_rows"]}
    driver_targets = solvency_scenario_shocks_contract_payload()["driver_targets"]
    for parameter in parameters:
        exposure = exposures.get(parameter["exposure_id"])
        path = parameter["path"]
        if exposure is None:
            _issue(issues, f"{path}.exposure_id", "exposure_unknown", "Modulziel ist nicht deklariert")
            continue
        target = driver_targets[parameter["module_kind"]]
        if exposure["balance_side"] != target["balance_side"] or exposure["sector_id"] not in target["sector_ids"]:
            _issue(issues, f"{path}.module_kind", "module_target_mismatch", "Modul passt nicht zu Sparte und Bilanzseite")
    if issues:
        return RiskModuleReport(None, tuple(issues))
    try:
        input_digest = _digest(value)
    except (TypeError, ValueError):
        _issue(issues, "$", "json_invalid", "Eingang muss kanonisch als JSON darstellbar sein")
        return RiskModuleReport(None, tuple(issues))

    with localcontext() as context:
        context.prec = 64
        module_rows: list[dict[str, object]] = []
        deltas: dict[str, Decimal] = {}
        for parameter in sorted(parameters, key=lambda item: item["module_id"]):
            exposure = exposures[parameter["exposure_id"]]
            base = Decimal(exposure["base_amount"])
            magnitude = (base * parameter["stress_rate"]).quantize(_QUANTUM, rounding=ROUND_HALF_UP)
            delta = -magnitude if exposure["balance_side"] == "assets" else magnitude
            deltas[parameter["exposure_id"]] = delta
            module_rows.append({
                "module_id": parameter["module_id"],
                "module_kind": parameter["module_kind"],
                "exposure_id": parameter["exposure_id"],
                "sector_id": exposure["sector_id"],
                "balance_side": exposure["balance_side"],
                "parameter_source_kind": _SOURCE_KIND,
                "assumption_note": parameter["assumption_note"],
                "base_amount": exposure["base_amount"],
                "stress_rate": _amount(parameter["stress_rate"]),
                "amount_delta": _amount(delta),
                "post_stress_amount": _amount(base + delta),
                "model_proxy_change": _amount(delta if exposure["balance_side"] == "assets" else -delta),
            })
        exposure_rows = [{
            **row,
            "amount_delta": _amount(deltas.get(row["exposure_id"], Decimal(0))),
            "shocked_amount": _amount(Decimal(row["base_amount"]) + deltas.get(row["exposure_id"], Decimal(0))),
        } for row in baseline["exposure_rows"]]
    return RiskModuleReport({
        "schema_version": SOLVENCY_RISK_MODULE_RESULT_VERSION,
        "source_result_schema_version": baseline["schema_version"],
        "source_exposure_content_digest": baseline["content_digest"],
        "source_model_balance_content_digest": baseline["source_content_digest"],
        "input_digest": input_digest,
        "insurer_id": baseline["insurer_id"],
        "scenario_id": baseline["scenario_id"],
        "variant_id": baseline["variant_id"],
        "checkpoint": baseline["checkpoint"],
        "amount_unit": "model_currency_unit_not_eur",
        "module_rows": module_rows,
        "exposure_rows": exposure_rows,
        "calibration_status": "scenario_only_not_regulatory",
    }, ())
