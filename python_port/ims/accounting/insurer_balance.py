"""Atomic consolidation of two explicitly sourced non-life model balances."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from decimal import Decimal, localcontext

from ims.accounting.model_balance_contract import BALANCE_FIELDS, MODEL_BALANCE_CONTRACT_VERSION
from ims.accounting.non_life_model_balance import (
    MODEL_BALANCE_INPUT_VERSION,
    MODEL_BALANCE_RESULT_VERSION,
    ModelBalanceIssue,
    ModelBalanceReport,
    ModelBalanceRow,
    build_non_life_model_balance,
)
from ims.model.vdefmd6_population import VDEFMD6_INSURER_COUNT
from ims.model.sector_taxonomy import SECTOR_TAXONOMY_VERSION


INSURER_BALANCE_INPUT_VERSION = "ims.insurer-balance-input.v1"
INSURER_BALANCE_RESULT_VERSION = "ims.insurer-balance-result.v1"
INSURER_BALANCE_CONTRACT_VERSION = "ims.insurer-balance-workbench-contract.v1"
SECTOR_IDS = ("motor", "property_liability")
_DOCUMENT_FIELDS = frozenset(("schema_version", "insurer_id", "sectors"))


@dataclass(frozen=True, slots=True)
class InsurerBalanceReport:
    insurer_id: int | None
    sectors: tuple[ModelBalanceReport, ...]
    total_rows: tuple[ModelBalanceRow, ...]
    issues: tuple[ModelBalanceIssue, ...]

    def to_dict(self) -> dict[str, object]:
        valid = not self.issues
        sector_rows = [
            {"sector_id": report.sector_id, "rows": [row.to_dict() for row in report.rows]}
            for report in self.sectors
        ] if valid else []
        totals = [row.to_dict() for row in self.total_rows] if valid else []
        core = {
            "schema_version": INSURER_BALANCE_RESULT_VERSION,
            "insurer_id": self.insurer_id,
            "period_count": len(totals),
            "source_kind": "explicit_scenario",
            "historical_mapping_status": "unresolved",
            "sectors": sector_rows,
            "total_rows": totals,
        }
        digest = hashlib.sha256(
            json.dumps(core, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
        ).hexdigest() if valid else None
        return {
            **core,
            "status": "ok" if valid else "error",
            "valid": valid,
            "content_digest": digest,
            "issue_count": len(self.issues),
            "issues": [
                {"path": issue.path, "code": issue.code, "message": issue.message}
                for issue in self.issues
            ],
            "writes_performed": False,
            "runner_invoked": False,
            "simulation_performed": False,
            "historical_full_equality_claim": False,
        }


def _issue(path: str, code: str, message: str) -> ModelBalanceIssue:
    return ModelBalanceIssue(path, code, message)


def insurer_balance_workbench_contract_payload() -> dict[str, object]:
    return {
        "schema_version": INSURER_BALANCE_CONTRACT_VERSION,
        "input_schema_version": INSURER_BALANCE_INPUT_VERSION,
        "sector_input_schema_version": MODEL_BALANCE_INPUT_VERSION,
        "model_balance_contract_schema_version": MODEL_BALANCE_CONTRACT_VERSION,
        "sector_taxonomy_schema_version": SECTOR_TAXONOMY_VERSION,
        "sector_result_schema_version": MODEL_BALANCE_RESULT_VERSION,
        "result_schema_version": INSURER_BALANCE_RESULT_VERSION,
        "calculation_endpoint": "/api/accounting/insurer-balance",
        "xlsx_endpoint": "/api/accounting/insurer-balance.xlsx",
        "sector_ids": list(SECTOR_IDS),
        "insurer_id_range": [1, VDEFMD6_INSURER_COUNT],
        "period_range": [1, 100],
        "amount_representation": "decimal_string_12_integer_4_fraction",
        "xlsx_amount_cells": "canonical_text",
        "xlsx_if_match_required": True,
        "source_kind": "explicit_scenario",
        "historical_mapping_status": "unresolved",
        "writes_enabled": False,
        "runner_enabled": False,
        "simulation_performed": False,
        "historical_full_equality_claim": False,
    }


def build_insurer_balance(value: object) -> InsurerBalanceReport:
    """Validate both sectors before producing any consolidated row."""

    issues: list[ModelBalanceIssue] = []
    if type(value) is not dict:
        return InsurerBalanceReport(None, (), (), (
            _issue("$", "object_required", "Versichererbilanz-Eingang muss ein Objekt sein"),
        ))
    actual_fields = {key for key in value if type(key) is str}
    for key in sorted(_DOCUMENT_FIELDS - actual_fields):
        issues.append(_issue(f"$.{key}", "field_missing", f"Pflichtfeld fehlt: {key}"))
    for key in sorted(actual_fields - _DOCUMENT_FIELDS):
        issues.append(_issue(f"$.{key}", "field_unknown", f"Unbekanntes Feld: {key}"))
    if len(actual_fields) != len(value):
        issues.append(_issue("$", "field_name_invalid", "Feldnamen muessen Text sein"))
    if value.get("schema_version") != INSURER_BALANCE_INPUT_VERSION:
        issues.append(_issue("$.schema_version", "contract_value_mismatch", "Falsche Eingabeversion"))
    insurer_id = value.get("insurer_id")
    if type(insurer_id) is not int or not 1 <= insurer_id <= VDEFMD6_INSURER_COUNT:
        issues.append(_issue("$.insurer_id", "insurer_id_invalid", "Vdefmd6-VU-ID von 1 bis 25 erforderlich"))
        insurer_id = None

    sector_values = value.get("sectors")
    if type(sector_values) is not list or len(sector_values) != len(SECTOR_IDS):
        issues.append(_issue("$.sectors", "sector_count_invalid", "Genau Kfz und Sach-Haftpflicht erforderlich"))
        return InsurerBalanceReport(insurer_id, (), (), tuple(issues))
    reports: list[ModelBalanceReport] = []
    for index, sector_value in enumerate(sector_values):
        report = build_non_life_model_balance(sector_value)
        for item in report.issues:
            issues.append(_issue(f"$.sectors[{index}]{item.path[1:]}", item.code, item.message))
        if insurer_id is not None and report.insurer_id != insurer_id:
            issues.append(_issue(f"$.sectors[{index}].insurer_id", "insurer_mismatch", "Versicherer-ID weicht ab"))
        reports.append(report)
    if {report.sector_id for report in reports} != set(SECTOR_IDS):
        issues.append(_issue("$.sectors", "sector_pair_invalid", "Kfz und Sach-Haftpflicht je genau einmal erforderlich"))
    if reports[0].rows and reports[1].rows and len(reports[0].rows) != len(reports[1].rows):
        issues.append(_issue("$.sectors", "period_count_mismatch", "Sparten muessen dasselbe Periodenfenster haben"))
    if issues:
        return InsurerBalanceReport(insurer_id, (), (), tuple(issues))

    reports.sort(key=lambda report: SECTOR_IDS.index(report.sector_id))
    totals: list[ModelBalanceRow] = []
    with localcontext() as context:
        context.prec = 64
        for index, pair in enumerate(zip(reports[0].rows, reports[1].rows, strict=True)):
            left, right = pair
            amounts = {
                field.field_id: getattr(left, field.field_id) + getattr(right, field.field_id)
                for field in BALANCE_FIELDS
            }
            total = ModelBalanceRow(period=index + 1, **amounts)
            for prefix in ("opening", "closing"):
                if getattr(total, f"{prefix}_cash") != (
                    getattr(total, f"{prefix}_claim_liability") + getattr(total, f"{prefix}_equity")
                ):
                    issues.append(_issue(f"$.total_rows[{index}]", "total_identity_invalid", "Gesamtbilanz ist nicht ausgeglichen"))
            if totals and any(
                getattr(total, f"opening_{name}") != getattr(totals[-1], f"closing_{name}")
                for name in ("cash", "claim_liability", "equity")
            ):
                issues.append(_issue(f"$.total_rows[{index}]", "total_carryover_invalid", "Gesamt-Carryover weicht ab"))
            if issues:
                return InsurerBalanceReport(insurer_id, (), (), tuple(issues))
            totals.append(total)
    return InsurerBalanceReport(insurer_id, tuple(reports), tuple(totals), ())
