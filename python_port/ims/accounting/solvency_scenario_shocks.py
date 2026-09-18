"""Model-only, explicitly mapped one-checkpoint shock effects."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from decimal import Decimal, localcontext

from ims.accounting.four_sector_balance import SECTOR_IDS
from ims.accounting.solvency_model_balance import (
    SOLVENCY_MODEL_BALANCE_INPUT_VERSION,
    SOLVENCY_MODEL_BALANCE_RESULT_VERSION,
    build_solvency_model_balance,
)


SOLVENCY_SHOCK_INPUT_VERSION = "ims.solvency-scenario-shocks-input.v1"
SOLVENCY_SHOCK_RESULT_VERSION = "ims.solvency-scenario-shocks-result.v1"
_INPUT_FIELDS = frozenset(("schema_version", "solvency_model_balance_input", "exposures", "shocks"))
_EXPOSURE_FIELDS = frozenset(("exposure_id", "sector_id", "balance_side", "base_amount", "source_kind"))
_SHOCK_FIELDS = frozenset(("shock_id", "driver_kind", "exposure_id", "amount_delta", "assumption_note"))
_IDENTIFIER = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,39}\Z")
_AMOUNT = re.compile(r"-?(?:0|[1-9][0-9]{0,11})(?:\.[0-9]{1,4})?\Z")
_SOURCE_KIND = "scenario_declared_non_overlapping_subposition"
_DRIVER_TARGETS = {
    "asset_market_value": ("assets", frozenset(SECTOR_IDS)),
    "non_life_claim_obligation": ("liabilities", frozenset(("motor", "property_liability"))),
    "life_obligation": ("liabilities", frozenset(("life",))),
    "health_benefit_obligation": ("liabilities", frozenset(("health",))),
}


@dataclass(frozen=True, slots=True)
class ShockIssue:
    path: str
    code: str
    message: str

    def to_dict(self) -> dict[str, str]:
        return {"path": self.path, "code": self.code, "message": self.message}


@dataclass(frozen=True, slots=True)
class ShockReport:
    core: dict[str, object] | None
    issues: tuple[ShockIssue, ...]

    def to_dict(self) -> dict[str, object]:
        valid = self.core is not None and not self.issues
        core = self.core if valid else {
            "schema_version": SOLVENCY_SHOCK_RESULT_VERSION,
            "source_result_schema_version": SOLVENCY_MODEL_BALANCE_RESULT_VERSION,
            "source_content_digest": None,
            "input_digest": None,
            "insurer_id": None,
            "scenario_id": None,
            "variant_id": None,
            "checkpoint": None,
            "amount_unit": "model_currency_unit_not_eur",
            "exposure_rows": [],
            "shock_rows": [],
            "sector_impacts": [],
            "total_impact": None,
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


def _issue(issues: list[ShockIssue], path: str, code: str, message: str) -> None:
    issues.append(ShockIssue(path, code, message))


def _exact_fields(value: dict, expected: frozenset[str], path: str, issues: list[ShockIssue]) -> None:
    actual = {key for key in value if type(key) is str}
    for field in sorted(expected - actual):
        _issue(issues, f"{path}.{field}", "field_missing", f"Pflichtfeld fehlt: {field}")
    for field in sorted(actual - expected):
        _issue(issues, f"{path}.{field}", "field_unknown", f"Unbekanntes Feld: {field}")
    if len(actual) != len(value):
        _issue(issues, path, "field_name_invalid", "Feldnamen muessen Text sein")


def _identifier(value: object, path: str, issues: list[ShockIssue]) -> str | None:
    if type(value) is not str or _IDENTIFIER.fullmatch(value) is None:
        _issue(issues, path, "identifier_invalid", "ASCII-Kennung mit 1 bis 40 Zeichen erforderlich")
        return None
    return value


def _decimal(value: object, path: str, issues: list[ShockIssue]) -> Decimal | None:
    if type(value) is not str or _AMOUNT.fullmatch(value) is None:
        _issue(issues, path, "decimal_string_required", "Begrenzter Dezimaltext mit maximal vier Nachkommastellen erforderlich")
        return None
    return Decimal(value)


def _exposures(value: object, issues: list[ShockIssue]) -> dict[str, dict[str, object]]:
    if type(value) is not list or not 1 <= len(value) <= 40:
        _issue(issues, "$.exposures", "exposure_count_invalid", "1 bis 40 Teilbestaende erforderlich")
        return {}
    parsed: dict[str, dict[str, object]] = {}
    for index, item in enumerate(value):
        path = f"$.exposures[{index}]"
        if type(item) is not dict:
            _issue(issues, path, "object_required", "Teilbestand muss ein Objekt sein")
            continue
        _exact_fields(item, _EXPOSURE_FIELDS, path, issues)
        exposure_id = _identifier(item.get("exposure_id"), f"{path}.exposure_id", issues)
        sector_id = item.get("sector_id")
        if type(sector_id) is not str or sector_id not in SECTOR_IDS:
            _issue(issues, f"{path}.sector_id", "sector_invalid", "Unbekannte Sparte")
        side = item.get("balance_side")
        if side not in ("assets", "liabilities") or type(side) is not str:
            _issue(issues, f"{path}.balance_side", "balance_side_invalid", "Nur assets oder liabilities zulaessig")
        amount = _decimal(item.get("base_amount"), f"{path}.base_amount", issues)
        if amount is not None and amount < 0:
            _issue(issues, f"{path}.base_amount", "negative_exposure", "Teilbestand darf nicht negativ sein")
        if item.get("source_kind") != _SOURCE_KIND:
            _issue(issues, f"{path}.source_kind", "source_kind_invalid", "Explizite Szenario-Teilposition erforderlich")
        if exposure_id is not None:
            if exposure_id in parsed:
                _issue(issues, f"{path}.exposure_id", "exposure_duplicate", "Teilbestand mehrfach angegeben")
            else:
                parsed[exposure_id] = {
                    "sector_id": sector_id, "balance_side": side, "base_amount": amount,
                    "source_kind": item.get("source_kind"),
                }
    return parsed


def _shocks(value: object, issues: list[ShockIssue]) -> list[dict[str, object]]:
    if type(value) is not list or len(value) > 40:
        _issue(issues, "$.shocks", "shock_count_invalid", "Hoestens 40 Schocks zulaessig")
        return []
    parsed: list[dict[str, object]] = []
    seen_shocks: set[str] = set()
    seen_exposures: set[str] = set()
    for index, item in enumerate(value):
        path = f"$.shocks[{index}]"
        if type(item) is not dict:
            _issue(issues, path, "object_required", "Schock muss ein Objekt sein")
            continue
        _exact_fields(item, _SHOCK_FIELDS, path, issues)
        shock_id = _identifier(item.get("shock_id"), f"{path}.shock_id", issues)
        exposure_id = _identifier(item.get("exposure_id"), f"{path}.exposure_id", issues)
        driver = item.get("driver_kind")
        if type(driver) is not str or driver not in _DRIVER_TARGETS:
            _issue(issues, f"{path}.driver_kind", "driver_invalid", "Unbekannter Modelltreiber")
        delta = _decimal(item.get("amount_delta"), f"{path}.amount_delta", issues)
        note = item.get("assumption_note")
        if type(note) is not str or not 1 <= len(note) <= 160 or note != note.strip() or not note.isprintable():
            _issue(issues, f"{path}.assumption_note", "note_invalid", "Druckbarer Annahmentext mit 1 bis 160 Zeichen erforderlich")
        if shock_id is not None:
            if shock_id in seen_shocks:
                _issue(issues, f"{path}.shock_id", "shock_duplicate", "Schockkennung mehrfach angegeben")
            seen_shocks.add(shock_id)
        if exposure_id is not None:
            if exposure_id in seen_exposures:
                _issue(issues, f"{path}.exposure_id", "exposure_shocked_twice", "Teilbestand darf nur einmal geschockt werden")
            seen_exposures.add(exposure_id)
        parsed.append({
            "shock_id": shock_id, "driver_kind": driver, "exposure_id": exposure_id,
            "amount_delta": delta, "assumption_note": note, "path": path,
        })
    return parsed


def solvency_scenario_shocks_contract_payload() -> dict[str, object]:
    return {
        "input_schema_version": SOLVENCY_SHOCK_INPUT_VERSION,
        "result_schema_version": SOLVENCY_SHOCK_RESULT_VERSION,
        "source_input_schema_version": SOLVENCY_MODEL_BALANCE_INPUT_VERSION,
        "source_result_schema_version": SOLVENCY_MODEL_BALANCE_RESULT_VERSION,
        "calculation_endpoint": "/api/accounting/solvency-scenario-shocks",
        "sector_ids": list(SECTOR_IDS),
        "driver_targets": {
            key: {"balance_side": side, "sector_ids": sorted(sectors)}
            for key, (side, sectors) in _DRIVER_TARGETS.items()
        },
        "exposure_source_kind": _SOURCE_KIND,
        "amount_representation": "signed_decimal_string_12_integer_4_fraction",
        "amount_unit": "model_currency_unit_not_eur",
        "shock_kind": "explicit_absolute_delta_per_named_exposure",
        "max_shocks_per_exposure": 1,
        "model_calculation_enabled": True,
        "writes_enabled": False,
        "runner_enabled": False,
        "regulatory_own_funds_claim": False,
        "scr_or_mcr_calculated": False,
        "compliance_decision_enabled": False,
        "historical_full_equality_claim": False,
    }


def build_solvency_scenario_shocks(value: object) -> ShockReport:
    """Recalculate PR172, validate the whole mapping, then publish an impact ledger."""

    issues: list[ShockIssue] = []
    if type(value) is not dict:
        _issue(issues, "$", "object_required", "Szenarioschock-Eingang muss ein Objekt sein")
        return ShockReport(None, tuple(issues))
    _exact_fields(value, _INPUT_FIELDS, "$", issues)
    if value.get("schema_version") != SOLVENCY_SHOCK_INPUT_VERSION:
        _issue(issues, "$.schema_version", "contract_value_mismatch", "Falsche Eingabeversion")
    source = build_solvency_model_balance(value.get("solvency_model_balance_input")).to_dict()
    if not source["valid"]:
        for item in source["issues"]:
            _issue(issues, f"$.solvency_model_balance_input{item['path'][1:]}", item["code"], item["message"])
    exposures = _exposures(value.get("exposures"), issues)
    shocks = _shocks(value.get("shocks"), issues)
    if issues:
        return ShockReport(None, tuple(issues))

    with localcontext() as context:
        context.prec = 64
        stocks = {
            (row["sector_id"], side): Decimal(row[f"adjusted_model_{side}"])
            for row in source["sector_rows"] for side in ("assets", "liabilities")
        }
        allocations = {key: Decimal(0) for key in stocks}
        for exposure in exposures.values():
            key = (exposure["sector_id"], exposure["balance_side"])
            allocations[key] += exposure["base_amount"]
        for (sector_id, side), amount in allocations.items():
            if amount > stocks[(sector_id, side)]:
                _issue(issues, "$.exposures", "exposure_overallocated", f"{sector_id}/{side} uebersteigt Modellbestand")

        deltas: dict[str, Decimal] = {}
        for shock in shocks:
            path = shock["path"]
            exposure_id = shock["exposure_id"]
            exposure = exposures.get(exposure_id)
            if exposure is None:
                _issue(issues, f"{path}.exposure_id", "exposure_unknown", "Schockziel ist nicht deklariert")
                continue
            side, sectors = _DRIVER_TARGETS[shock["driver_kind"]]
            if exposure["balance_side"] != side or exposure["sector_id"] not in sectors:
                _issue(issues, f"{path}.driver_kind", "driver_target_mismatch", "Treiber passt nicht zu Sparte und Bilanzseite")
            if exposure["base_amount"] + shock["amount_delta"] < 0:
                _issue(issues, f"{path}.amount_delta", "negative_shocked_exposure", "Geschockter Teilbestand darf nicht negativ sein")
            deltas[exposure_id] = shock["amount_delta"]
        if issues:
            return ShockReport(None, tuple(issues))
        try:
            input_digest = _digest(value)
        except (TypeError, ValueError):
            _issue(issues, "$", "json_invalid", "Eingang muss kanonisch als JSON darstellbar sein")
            return ShockReport(None, tuple(issues))

        exposure_rows = [{
            "exposure_id": exposure_id,
            "sector_id": exposure["sector_id"],
            "balance_side": exposure["balance_side"],
            "source_kind": _SOURCE_KIND,
            "base_amount": _amount(exposure["base_amount"]),
            "amount_delta": _amount(deltas.get(exposure_id, Decimal(0))),
            "shocked_amount": _amount(exposure["base_amount"] + deltas.get(exposure_id, Decimal(0))),
        } for exposure_id, exposure in sorted(exposures.items())]
        shock_rows = [{
            "shock_id": shock["shock_id"],
            "driver_kind": shock["driver_kind"],
            "exposure_id": shock["exposure_id"],
            "amount_delta": _amount(shock["amount_delta"]),
            "assumption_note": shock["assumption_note"],
        } for shock in sorted(shocks, key=lambda item: item["shock_id"])]
        sector_impacts = []
        for sector_id in SECTOR_IDS:
            asset_delta = sum((
                deltas.get(exposure_id, Decimal(0)) for exposure_id, exposure in exposures.items()
                if exposure["sector_id"] == sector_id and exposure["balance_side"] == "assets"
            ), Decimal(0))
            liability_delta = sum((
                deltas.get(exposure_id, Decimal(0)) for exposure_id, exposure in exposures.items()
                if exposure["sector_id"] == sector_id and exposure["balance_side"] == "liabilities"
            ), Decimal(0))
            sector_impacts.append({
                "sector_id": sector_id,
                "asset_delta": _amount(asset_delta),
                "liability_delta": _amount(liability_delta),
                "model_proxy_change": _amount(asset_delta - liability_delta),
            })
        total_assets = sum((Decimal(row["asset_delta"]) for row in sector_impacts), Decimal(0))
        total_liabilities = sum((Decimal(row["liability_delta"]) for row in sector_impacts), Decimal(0))
        return ShockReport({
            "schema_version": SOLVENCY_SHOCK_RESULT_VERSION,
            "source_result_schema_version": source["schema_version"],
            "source_content_digest": source["content_digest"],
            "input_digest": input_digest,
            "insurer_id": source["insurer_id"],
            "scenario_id": source["scenario_id"],
            "variant_id": source["variant_id"],
            "checkpoint": source["checkpoint"],
            "amount_unit": "model_currency_unit_not_eur",
            "exposure_rows": exposure_rows,
            "shock_rows": shock_rows,
            "sector_impacts": sector_impacts,
            "total_impact": {
                "asset_delta": _amount(total_assets),
                "liability_delta": _amount(total_liabilities),
                "model_proxy_change": _amount(total_assets - total_liabilities),
            },
            "valuation_status": "model_only_not_regulatory",
        }, ())
