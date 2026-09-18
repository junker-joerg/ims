"""Explicit model-only valuation bridge from a recalculated four-sector balance."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, localcontext

from ims.accounting.four_sector_balance import (
    FOUR_SECTOR_BALANCE_INPUT_VERSION,
    FOUR_SECTOR_BALANCE_RESULT_VERSION,
    SECTOR_IDS,
    build_four_sector_balance,
)
from ims.model.solvency_scope_contract import SOLVENCY_SCOPE_CONTRACT_VERSION


SOLVENCY_MODEL_BALANCE_INPUT_VERSION = "ims.solvency-model-balance-input.v1"
SOLVENCY_MODEL_BALANCE_RESULT_VERSION = "ims.solvency-model-balance-result.v1"
_INPUT_FIELDS = frozenset((
    "schema_version", "scope_contract_schema_version", "model_only_confirmed",
    "four_sector_input", "checkpoint", "adjustments",
))
_CHECKPOINT_FIELDS = frozenset(("model_period", "reference_date", "date_linkage"))
_ADJUSTMENT_FIELDS = frozenset((
    "sector_id", "asset_delta", "liability_delta", "assumption_id", "assumption_note",
))
_AMOUNT_PATTERN = re.compile(r"-?(?:0|[1-9][0-9]{0,11})(?:\.[0-9]{1,4})?\Z")
_IDENTIFIER = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,39}\Z")
_DATE_PATTERN = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}\Z")
_ROW_AMOUNTS = (
    "closing_assets", "closing_liabilities", "closing_equity", "asset_delta",
    "liability_delta", "adjusted_model_assets", "adjusted_model_liabilities",
    "model_own_funds_proxy", "proxy_change_vs_equity",
)


@dataclass(frozen=True, slots=True)
class SolvencyModelIssue:
    path: str
    code: str
    message: str

    def to_dict(self) -> dict[str, str]:
        return {"path": self.path, "code": self.code, "message": self.message}


@dataclass(frozen=True, slots=True)
class SolvencyModelReport:
    core: dict[str, object] | None
    issues: tuple[SolvencyModelIssue, ...]

    def to_dict(self) -> dict[str, object]:
        valid = self.core is not None and not self.issues
        core = self.core if valid else {
            "schema_version": SOLVENCY_MODEL_BALANCE_RESULT_VERSION,
            "scope_contract_schema_version": SOLVENCY_SCOPE_CONTRACT_VERSION,
            "insurer_id": None,
            "scenario_id": None,
            "variant_id": None,
            "checkpoint": None,
            "amount_unit": "model_currency_unit_not_eur",
            "source_result_schema_version": FOUR_SECTOR_BALANCE_RESULT_VERSION,
            "source_scenario_linkage": None,
            "historical_mapping_status": "unresolved",
            "source_content_digest": None,
            "source_input_digest": None,
            "input_digest": None,
            "sector_rows": [],
            "total_row": None,
            "valuation_status": "model_only_not_regulatory",
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


def _issue(issues: list[SolvencyModelIssue], path: str, code: str, message: str) -> None:
    issues.append(SolvencyModelIssue(path, code, message))


def _exact_fields(
    value: dict, expected: frozenset[str], path: str, issues: list[SolvencyModelIssue],
) -> None:
    actual = {key for key in value if type(key) is str}
    for field in sorted(expected - actual):
        _issue(issues, f"{path}.{field}", "field_missing", f"Pflichtfeld fehlt: {field}")
    for field in sorted(actual - expected):
        _issue(issues, f"{path}.{field}", "field_unknown", f"Unbekanntes Feld: {field}")
    if len(actual) != len(value):
        _issue(issues, path, "field_name_invalid", "Feldnamen muessen Text sein")


def _parse_checkpoint(value: object, issues: list[SolvencyModelIssue]) -> tuple[int, str] | None:
    if type(value) is not dict:
        _issue(issues, "$.checkpoint", "object_required", "Checkpoint-Objekt erforderlich")
        return None
    _exact_fields(value, _CHECKPOINT_FIELDS, "$.checkpoint", issues)
    period = value.get("model_period")
    if type(period) is not int or not 1 <= period <= 100:
        _issue(issues, "$.checkpoint.model_period", "period_invalid", "IMS-Periode 1 bis 100 erforderlich")
    reference_date = value.get("reference_date")
    if type(reference_date) is not str or _DATE_PATTERN.fullmatch(reference_date) is None:
        _issue(issues, "$.checkpoint.reference_date", "date_invalid", "ISO-Datum YYYY-MM-DD erforderlich")
    else:
        try:
            date.fromisoformat(reference_date)
        except ValueError:
            _issue(issues, "$.checkpoint.reference_date", "date_invalid", "Kalenderdatum ungueltig")
    if value.get("date_linkage") != "scenario_declared":
        _issue(issues, "$.checkpoint.date_linkage", "linkage_invalid", "Nur deklarierte Szenariozuordnung zulaessig")
    if any(item.path.startswith("$.checkpoint") for item in issues):
        return None
    return period, reference_date


def _parse_adjustments(
    value: object, issues: list[SolvencyModelIssue],
) -> dict[str, dict[str, object]]:
    if type(value) is not list or len(value) != len(SECTOR_IDS):
        _issue(issues, "$.adjustments", "sector_count_invalid", "Genau vier Spartenanpassungen erforderlich")
        return {}
    parsed: dict[str, dict[str, object]] = {}
    for index, item in enumerate(value):
        path = f"$.adjustments[{index}]"
        if type(item) is not dict:
            _issue(issues, path, "object_required", "Anpassungsobjekt erforderlich")
            continue
        _exact_fields(item, _ADJUSTMENT_FIELDS, path, issues)
        sector_id = item.get("sector_id")
        if type(sector_id) is not str or sector_id not in SECTOR_IDS:
            _issue(issues, f"{path}.sector_id", "sector_invalid", "Unbekannte Sparte")
        elif sector_id in parsed:
            _issue(issues, f"{path}.sector_id", "sector_duplicate", "Sparte mehrfach angegeben")
        amounts: dict[str, Decimal] = {}
        for field in ("asset_delta", "liability_delta"):
            candidate = item.get(field)
            if type(candidate) is not str or _AMOUNT_PATTERN.fullmatch(candidate) is None:
                _issue(issues, f"{path}.{field}", "decimal_string_required", "Begrenzter Dezimaltext mit maximal vier Nachkommastellen erforderlich")
            else:
                amounts[field] = Decimal(candidate)
        assumption_id = item.get("assumption_id")
        if type(assumption_id) is not str or _IDENTIFIER.fullmatch(assumption_id) is None:
            _issue(issues, f"{path}.assumption_id", "identifier_invalid", "ASCII-Kennung mit 1 bis 40 Zeichen erforderlich")
        note = item.get("assumption_note")
        if type(note) is not str or not 1 <= len(note) <= 160 or note != note.strip() or not note.isprintable():
            _issue(issues, f"{path}.assumption_note", "note_invalid", "Druckbarer Annahmentext mit 1 bis 160 Zeichen erforderlich")
        if type(sector_id) is str and sector_id in SECTOR_IDS and sector_id not in parsed:
            parsed[sector_id] = {**amounts, "assumption_id": assumption_id, "assumption_note": note}
    if set(parsed) != set(SECTOR_IDS):
        _issue(issues, "$.adjustments", "sector_set_invalid", "Jede der vier Sparten genau einmal erforderlich")
    return parsed


def _bridge_row(
    source: dict[str, object], adjustment: dict[str, object],
) -> dict[str, Decimal]:
    closing_assets = Decimal(source["closing_assets"])
    closing_liabilities = Decimal(source["closing_liabilities"])
    closing_equity = Decimal(source["closing_equity"])
    asset_delta = adjustment["asset_delta"]
    liability_delta = adjustment["liability_delta"]
    adjusted_assets = closing_assets + asset_delta
    adjusted_liabilities = closing_liabilities + liability_delta
    return {
        "closing_assets": closing_assets,
        "closing_liabilities": closing_liabilities,
        "closing_equity": closing_equity,
        "asset_delta": asset_delta,
        "liability_delta": liability_delta,
        "adjusted_model_assets": adjusted_assets,
        "adjusted_model_liabilities": adjusted_liabilities,
        "model_own_funds_proxy": adjusted_assets - adjusted_liabilities,
        "proxy_change_vs_equity": asset_delta - liability_delta,
    }


def _serialize_row(row: dict[str, Decimal]) -> dict[str, str]:
    return {field: _amount(row[field]) for field in _ROW_AMOUNTS}


def solvency_model_balance_contract_payload() -> dict[str, object]:
    return {
        "input_schema_version": SOLVENCY_MODEL_BALANCE_INPUT_VERSION,
        "result_schema_version": SOLVENCY_MODEL_BALANCE_RESULT_VERSION,
        "scope_contract_schema_version": SOLVENCY_SCOPE_CONTRACT_VERSION,
        "source_input_schema_version": FOUR_SECTOR_BALANCE_INPUT_VERSION,
        "source_result_schema_version": FOUR_SECTOR_BALANCE_RESULT_VERSION,
        "calculation_endpoint": "/api/accounting/solvency-model-balance",
        "sector_ids": list(SECTOR_IDS),
        "source_kind": "server_recalculated_four_sector_input",
        "checkpoint_kind": "one_selected_model_period_scenario_declared_date",
        "adjustment_kind": "explicit_scenario_model_deltas_only",
        "amount_representation": "signed_decimal_string_12_integer_4_fraction",
        "amount_unit": "model_currency_unit_not_eur",
        "formula": "model_own_funds_proxy = closing_equity + asset_delta - liability_delta",
        "model_calculation_enabled": True,
        "writes_enabled": False,
        "runner_enabled": False,
        "statutory_balance_claim": False,
        "regulatory_own_funds_claim": False,
        "scr_or_mcr_calculated": False,
        "compliance_decision_enabled": False,
        "historical_full_equality_claim": False,
    }


def build_solvency_model_balance(value: object) -> SolvencyModelReport:
    """Recalculate the model source and publish only a fully checked bridge."""

    issues: list[SolvencyModelIssue] = []
    if type(value) is not dict:
        _issue(issues, "$", "object_required", "Modell-Solvenzeingang muss ein Objekt sein")
        return SolvencyModelReport(None, tuple(issues))
    _exact_fields(value, _INPUT_FIELDS, "$", issues)
    if value.get("schema_version") != SOLVENCY_MODEL_BALANCE_INPUT_VERSION:
        _issue(issues, "$.schema_version", "contract_value_mismatch", "Falsche Eingabeversion")
    if value.get("scope_contract_schema_version") != SOLVENCY_SCOPE_CONTRACT_VERSION:
        _issue(issues, "$.scope_contract_schema_version", "scope_mismatch", "PR171-Vertragsversion erforderlich")
    if value.get("model_only_confirmed") is not True:
        _issue(issues, "$.model_only_confirmed", "model_boundary_unconfirmed", "Modellgrenze muss ausdruecklich bestaetigt sein")
    checkpoint = _parse_checkpoint(value.get("checkpoint"), issues)
    adjustments = _parse_adjustments(value.get("adjustments"), issues)
    if issues:
        return SolvencyModelReport(None, tuple(issues))

    source = build_four_sector_balance(value.get("four_sector_input")).to_dict()
    if not source["valid"]:
        for item in source["issues"]:
            _issue(issues, f"$.four_sector_input{item['path'][1:]}", item["code"], item["message"])
        return SolvencyModelReport(None, tuple(issues))
    period, reference_date = checkpoint
    if period > source["period_count"]:
        _issue(issues, "$.checkpoint.model_period", "period_out_of_range", "Periode liegt ausserhalb der neu berechneten Quelle")
        return SolvencyModelReport(None, tuple(issues))
    try:
        input_digest = _digest(value)
    except (TypeError, ValueError):
        _issue(issues, "$", "json_invalid", "Eingang muss kanonisch als JSON darstellbar sein")
        return SolvencyModelReport(None, tuple(issues))

    with localcontext() as context:
        context.prec = 64
        rows: list[dict[str, Decimal]] = []
        serialized: list[dict[str, object]] = []
        for sector in source["sectors"]:
            sector_id = sector["sector_id"]
            adjustment = adjustments[sector_id]
            row = _bridge_row(sector["rows"][period - 1], adjustment)
            for field in ("adjusted_model_assets", "adjusted_model_liabilities"):
                if row[field] < 0:
                    _issue(issues, f"$.adjustments.{sector_id}.{field}", "negative_adjusted_stock", "Angepasster Modellbestand darf nicht negativ sein")
            if row["model_own_funds_proxy"] != row["closing_equity"] + row["proxy_change_vs_equity"]:
                _issue(issues, f"$.adjustments.{sector_id}", "bridge_identity_invalid", "Eigenmittel-Proxy stimmt nicht zur Modellbilanz")
            rows.append(row)
            serialized.append({
                "sector_id": sector_id,
                "assumption_id": adjustment["assumption_id"],
                "assumption_note": adjustment["assumption_note"],
                **_serialize_row(row),
            })
        if issues:
            return SolvencyModelReport(None, tuple(issues))
        total = {field: sum((row[field] for row in rows), Decimal(0)) for field in _ROW_AMOUNTS}
        source_total = source["total_rows"][period - 1]
        if any(total[field] != Decimal(source_total[field]) for field in (
            "closing_assets", "closing_liabilities", "closing_equity",
        )) or total["model_own_funds_proxy"] != total["closing_equity"] + total["proxy_change_vs_equity"]:
            _issue(issues, "$.four_sector_input", "total_identity_invalid", "Vier-Sparten-Summe oder Bewertungsbruecke stimmt nicht")
            return SolvencyModelReport(None, tuple(issues))

        return SolvencyModelReport({
            "schema_version": SOLVENCY_MODEL_BALANCE_RESULT_VERSION,
            "scope_contract_schema_version": SOLVENCY_SCOPE_CONTRACT_VERSION,
            "insurer_id": source["insurer_id"],
            "scenario_id": source["scenario_id"],
            "variant_id": source["variant_id"],
            "checkpoint": {
                "model_period": period,
                "reference_date": reference_date,
                "date_linkage": "scenario_declared",
            },
            "amount_unit": "model_currency_unit_not_eur",
            "source_result_schema_version": source["schema_version"],
            "source_scenario_linkage": source["scenario_linkage"],
            "historical_mapping_status": source["historical_mapping_status"],
            "source_content_digest": source["content_digest"],
            "source_input_digest": source["input_digest"],
            "input_digest": input_digest,
            "sector_rows": serialized,
            "total_row": _serialize_row(total),
            "valuation_status": "model_only_not_regulatory",
        }, ())
