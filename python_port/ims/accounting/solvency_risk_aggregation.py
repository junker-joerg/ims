"""Explicit, model-only aggregation of validated PR174 scenario losses."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP, localcontext

from ims.accounting.solvency_risk_modules import (
    SOLVENCY_RISK_MODULE_INPUT_VERSION,
    SOLVENCY_RISK_MODULE_RESULT_VERSION,
    build_solvency_risk_modules,
)


SOLVENCY_RISK_AGGREGATION_INPUT_VERSION = "ims.solvency-risk-aggregation-input.v1"
SOLVENCY_RISK_AGGREGATION_RESULT_VERSION = "ims.solvency-risk-aggregation-result.v1"
_KINDS = (
    "asset_market_value",
    "non_life_claim_obligation",
    "life_obligation",
    "health_benefit_obligation",
    "counterparty_model_loss",
    "operational_model_loss",
)
_INPUT_FIELDS = frozenset((
    "schema_version", "solvency_risk_modules_input", "counterparty_cases",
    "operational_events", "aggregation_assumptions", "loss_absorption",
))
_COUNTERPARTY_FIELDS = frozenset((
    "case_id", "exposure_id", "loss_rate", "source_kind", "assumption_note",
))
_OPERATIONAL_FIELDS = frozenset((
    "event_id", "loss_amount", "source_kind", "assumption_note",
))
_AGGREGATION_FIELDS = frozenset(("source_kind", "assumption_note", "factor_loadings"))
_BUFFER_FIELDS = frozenset((
    "buffer_id", "capacity_amount", "applied_amount", "source_kind", "assumption_note",
))
_IDENTIFIER = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,39}\Z")
_RATE = re.compile(r"(?:0|1)(?:\.[0-9]{1,4})?\Z")
_NONNEGATIVE_AMOUNT = re.compile(r"(?:0|[1-9][0-9]{0,11})(?:\.[0-9]{1,4})?\Z")
_SOURCE_KIND = "scenario_declared_not_regulatory"
_BUFFER_SOURCE_KIND = "scenario_declared_independent_model_buffer"
_QUANTUM = Decimal("0.0001")


@dataclass(frozen=True, slots=True)
class RiskAggregationIssue:
    path: str
    code: str
    message: str

    def to_dict(self) -> dict[str, str]:
        return {"path": self.path, "code": self.code, "message": self.message}


@dataclass(frozen=True, slots=True)
class RiskAggregationReport:
    core: dict[str, object] | None
    issues: tuple[RiskAggregationIssue, ...]

    def to_dict(self) -> dict[str, object]:
        valid = self.core is not None and not self.issues
        core = self.core if valid else {
            "schema_version": SOLVENCY_RISK_AGGREGATION_RESULT_VERSION,
            "source_result_schema_version": SOLVENCY_RISK_MODULE_RESULT_VERSION,
            "source_module_content_digest": None,
            "source_exposure_content_digest": None,
            "source_model_balance_content_digest": None,
            "input_digest": None,
            "insurer_id": None,
            "scenario_id": None,
            "variant_id": None,
            "checkpoint": None,
            "amount_unit": "model_currency_unit_not_eur",
            "component_rows": [],
            "counterparty_rows": [],
            "operational_rows": [],
            "correlation_rows": [],
            "totals": None,
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
            "model_risk_aggregation_performed": valid,
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


def _issue(issues: list[RiskAggregationIssue], path: str, code: str, message: str) -> None:
    issues.append(RiskAggregationIssue(path, code, message))


def _exact_fields(
    value: dict, expected: frozenset[str], path: str, issues: list[RiskAggregationIssue],
) -> None:
    actual = {key for key in value if type(key) is str}
    for field in sorted(expected - actual):
        _issue(issues, f"{path}.{field}", "field_missing", f"Pflichtfeld fehlt: {field}")
    for field in sorted(actual - expected):
        _issue(issues, f"{path}.{field}", "field_unknown", f"Unbekanntes Feld: {field}")
    if len(actual) != len(value):
        _issue(issues, path, "field_name_invalid", "Feldnamen muessen Text sein")


def _object(value: object, fields: frozenset[str], path: str, issues: list[RiskAggregationIssue]) -> dict:
    if type(value) is not dict:
        _issue(issues, path, "object_required", "Objekt erforderlich")
        return {}
    _exact_fields(value, fields, path, issues)
    return value


def _identifier(value: object, path: str, issues: list[RiskAggregationIssue]) -> str | None:
    if type(value) is not str or _IDENTIFIER.fullmatch(value) is None:
        _issue(issues, path, "identifier_invalid", "ASCII-Kennung mit 1 bis 40 Zeichen erforderlich")
        return None
    return value


def _decimal(
    value: object, path: str, issues: list[RiskAggregationIssue], *, rate: bool,
) -> Decimal | None:
    pattern = _RATE if rate else _NONNEGATIVE_AMOUNT
    if type(value) is not str or pattern.fullmatch(value) is None:
        _issue(
            issues, path, "rate_format_invalid" if rate else "amount_format_invalid",
            "Nichtnegativer Dezimaltext mit maximal vier Nachkommastellen erforderlich",
        )
        return None
    parsed = Decimal(value)
    if rate and parsed > 1:
        _issue(issues, path, "rate_out_of_range", "Satz darf 1 nicht uebersteigen")
    return parsed


def _source_note(
    value: dict, path: str, issues: list[RiskAggregationIssue], *, buffer: bool = False,
) -> None:
    expected = _BUFFER_SOURCE_KIND if buffer else _SOURCE_KIND
    if value.get("source_kind") != expected:
        _issue(issues, f"{path}.source_kind", "source_kind_invalid", "Explizite Szenarioquelle erforderlich")
    note = value.get("assumption_note")
    if type(note) is not str or not 1 <= len(note) <= 160 or note != note.strip() or not note.isprintable():
        _issue(
            issues, f"{path}.assumption_note", "note_invalid",
            "Druckbarer Annahmentext mit 1 bis 160 Zeichen erforderlich",
        )


def _cases(
    value: object, path: str, fields: frozenset[str], id_field: str,
    amount_field: str, issues: list[RiskAggregationIssue],
) -> list[dict[str, object]]:
    if type(value) is not list or len(value) > 20:
        _issue(issues, path, "case_count_invalid", "Liste mit hoechstens 20 Faellen erforderlich")
        return []
    parsed: list[dict[str, object]] = []
    seen: set[str] = set()
    for index, item in enumerate(value):
        item_path = f"{path}[{index}]"
        row = _object(item, fields, item_path, issues)
        identifier = _identifier(row.get(id_field), f"{item_path}.{id_field}", issues)
        if identifier is not None:
            if identifier in seen:
                _issue(issues, f"{item_path}.{id_field}", "case_duplicate", "Fallkennung mehrfach angegeben")
            seen.add(identifier)
        if id_field == "case_id":
            _identifier(row.get("exposure_id"), f"{item_path}.exposure_id", issues)
        _decimal(row.get(amount_field), f"{item_path}.{amount_field}", issues, rate=amount_field == "loss_rate")
        _source_note(row, item_path, issues)
        if type(item) is dict:
            parsed.append(row)
    return parsed


def solvency_risk_aggregation_contract_payload() -> dict[str, object]:
    return {
        "input_schema_version": SOLVENCY_RISK_AGGREGATION_INPUT_VERSION,
        "result_schema_version": SOLVENCY_RISK_AGGREGATION_RESULT_VERSION,
        "source_input_schema_version": SOLVENCY_RISK_MODULE_INPUT_VERSION,
        "source_result_schema_version": SOLVENCY_RISK_MODULE_RESULT_VERSION,
        "calculation_endpoint": "/api/accounting/solvency-risk-aggregation",
        "risk_kinds": list(_KINDS),
        "source_kind": _SOURCE_KIND,
        "buffer_source_kind": _BUFFER_SOURCE_KIND,
        "factor_loading_range": "0_to_1_inclusive_decimal_string_4_fraction",
        "correlation_model": "one_common_factor_nonnegative_psd",
        "gross_formula": "sqrt((sum(loss_i*loading_i))^2+sum(loss_i^2*(1-loading_i^2)))",
        "rounding": "ROUND_HALF_UP_to_4_fractional_places_once_per_case_and_gross_total",
        "counterparty_exposure_must_be_unstressed_asset": True,
        "max_counterparty_cases": 20,
        "max_operational_events": 20,
        "amount_unit": "model_currency_unit_not_eur",
        "writes_enabled": False,
        "runner_enabled": False,
        "model_risk_aggregation_enabled": True,
        "regulatory_own_funds_claim": False,
        "scr_or_mcr_calculated": False,
        "capital_aggregation_performed": False,
        "compliance_decision_enabled": False,
        "historical_full_equality_claim": False,
    }


def build_solvency_risk_aggregation(value: object) -> RiskAggregationReport:
    """Recalculate PR174 and aggregate only explicitly declared model losses."""

    issues: list[RiskAggregationIssue] = []
    root = _object(value, _INPUT_FIELDS, "$", issues)
    if root.get("schema_version") != SOLVENCY_RISK_AGGREGATION_INPUT_VERSION:
        _issue(issues, "$.schema_version", "contract_value_mismatch", "Falsche Eingabeversion")
    source = build_solvency_risk_modules(root.get("solvency_risk_modules_input")).to_dict()
    if not source["valid"]:
        for item in source["issues"]:
            _issue(issues, f"$.solvency_risk_modules_input{item['path'][1:]}", item["code"], item["message"])
    counterparties = _cases(
        root.get("counterparty_cases"), "$.counterparty_cases", _COUNTERPARTY_FIELDS,
        "case_id", "loss_rate", issues,
    )
    operations = _cases(
        root.get("operational_events"), "$.operational_events", _OPERATIONAL_FIELDS,
        "event_id", "loss_amount", issues,
    )
    assumption = _object(root.get("aggregation_assumptions"), _AGGREGATION_FIELDS, "$.aggregation_assumptions", issues)
    _source_note(assumption, "$.aggregation_assumptions", issues)
    loadings = _object(
        assumption.get("factor_loadings"), frozenset(_KINDS),
        "$.aggregation_assumptions.factor_loadings", issues,
    )
    for kind in _KINDS:
        _decimal(loadings.get(kind), f"$.aggregation_assumptions.factor_loadings.{kind}", issues, rate=True)
    buffer = _object(root.get("loss_absorption"), _BUFFER_FIELDS, "$.loss_absorption", issues)
    _identifier(buffer.get("buffer_id"), "$.loss_absorption.buffer_id", issues)
    capacity = _decimal(buffer.get("capacity_amount"), "$.loss_absorption.capacity_amount", issues, rate=False)
    applied = _decimal(buffer.get("applied_amount"), "$.loss_absorption.applied_amount", issues, rate=False)
    _source_note(buffer, "$.loss_absorption", issues, buffer=True)
    if capacity is not None and applied is not None and applied > capacity:
        _issue(
            issues, "$.loss_absorption.applied_amount", "buffer_capacity_exceeded",
            "Anrechnung uebersteigt deklarierte Kapazitaet",
        )
    if issues:
        return RiskAggregationReport(None, tuple(issues))

    exposures = {row["exposure_id"]: row for row in source["exposure_rows"]}
    stressed = {row["exposure_id"] for row in source["module_rows"]}
    used_exposures: set[str] = set()
    for index, row in enumerate(counterparties):
        path = f"$.counterparty_cases[{index}].exposure_id"
        exposure_id = row["exposure_id"]
        exposure = exposures.get(exposure_id)
        if exposure is None:
            _issue(issues, path, "exposure_unknown", "Gegenpartei-Teilposition nicht deklariert")
        elif exposure["balance_side"] != "assets":
            _issue(issues, path, "counterparty_target_invalid", "Gegenpartei-Fall erfordert Aktiva")
        if exposure_id in stressed or exposure_id in used_exposures:
            _issue(issues, path, "exposure_stressed_twice", "Teilposition mehrfach gestresst")
        used_exposures.add(exposure_id)
    if issues:
        return RiskAggregationReport(None, tuple(issues))
    try:
        input_digest = _digest(value)
    except (TypeError, ValueError):
        _issue(issues, "$", "json_invalid", "Eingang muss kanonisch als JSON darstellbar sein")
        return RiskAggregationReport(None, tuple(issues))

    with localcontext() as context:
        context.prec = 64
        losses = {kind: Decimal(0) for kind in _KINDS}
        for row in source["module_rows"]:
            losses[row["module_kind"]] -= Decimal(row["model_proxy_change"])
        counterparty_rows: list[dict[str, object]] = []
        for row in sorted(counterparties, key=lambda item: item["case_id"]):
            exposure = exposures[row["exposure_id"]]
            rate = Decimal(row["loss_rate"])
            loss = (Decimal(exposure["base_amount"]) * rate).quantize(_QUANTUM, rounding=ROUND_HALF_UP)
            losses["counterparty_model_loss"] += loss
            counterparty_rows.append({
                "case_id": row["case_id"], "exposure_id": row["exposure_id"],
                "sector_id": exposure["sector_id"], "base_amount": exposure["base_amount"],
                "loss_rate": _amount(rate), "model_loss_amount": _amount(loss),
                "source_kind": _SOURCE_KIND, "assumption_note": row["assumption_note"],
            })
        operational_rows: list[dict[str, object]] = []
        for row in sorted(operations, key=lambda item: item["event_id"]):
            loss = Decimal(row["loss_amount"])
            losses["operational_model_loss"] += loss
            operational_rows.append({
                "event_id": row["event_id"], "model_loss_amount": _amount(loss),
                "source_kind": _SOURCE_KIND, "assumption_note": row["assumption_note"],
            })
        factors = {kind: Decimal(loadings[kind]) for kind in _KINDS}
        common = sum((losses[kind] * factors[kind] for kind in _KINDS), Decimal(0))
        residual = sum((losses[kind] ** 2 * (1 - factors[kind] ** 2) for kind in _KINDS), Decimal(0))
        gross = (common ** 2 + residual).sqrt().quantize(_QUANTUM, rounding=ROUND_HALF_UP)
        if applied > gross:
            _issue(
                issues, "$.loss_absorption.applied_amount", "buffer_gross_exceeded",
                "Anrechnung uebersteigt Brutto-Modellverlust",
            )
            return RiskAggregationReport(None, tuple(issues))
        total = sum(losses.values(), Decimal(0))
        component_rows = [{
            "risk_kind": kind, "model_loss_amount": _amount(losses[kind]),
            "common_factor_loading": _amount(factors[kind]),
        } for kind in _KINDS]
        correlation_rows = [{
            "risk_kind_a": first, "risk_kind_b": second,
            "correlation": format(factors[first] * factors[second], ".8f"),
        } for index, first in enumerate(_KINDS) for second in _KINDS[index + 1:]]
        totals = {
            "unadjusted_sum_of_components": _amount(total),
            "gross_model_stress_loss": _amount(gross),
            "scenario_diversification_proxy": _amount(total - gross),
            "model_buffer_capacity": _amount(capacity),
            "model_buffer_applied": _amount(applied),
            "net_model_stress_loss": _amount(gross - applied),
        }
    return RiskAggregationReport({
        "schema_version": SOLVENCY_RISK_AGGREGATION_RESULT_VERSION,
        "source_result_schema_version": source["schema_version"],
        "source_module_content_digest": source["content_digest"],
        "source_exposure_content_digest": source["source_exposure_content_digest"],
        "source_model_balance_content_digest": source["source_model_balance_content_digest"],
        "input_digest": input_digest,
        "insurer_id": source["insurer_id"],
        "scenario_id": source["scenario_id"],
        "variant_id": source["variant_id"],
        "checkpoint": source["checkpoint"],
        "amount_unit": "model_currency_unit_not_eur",
        "component_rows": component_rows,
        "counterparty_rows": counterparty_rows,
        "operational_rows": operational_rows,
        "correlation_rows": correlation_rows,
        "totals": totals,
        "calibration_status": "scenario_only_not_regulatory",
    }, ())
