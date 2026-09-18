"""Atomic IMS-2.x model-balance consolidation from four explicit sector inputs."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from decimal import Decimal, localcontext

from ims.accounting.health_period_chain import (
    HEALTH_PERIOD_CHAIN_HORIZONS,
    HEALTH_PERIOD_CHAIN_INPUT_VERSION,
    run_health_period_chain,
)
from ims.accounting.life_period_chain import LIFE_PERIOD_CHAIN_INPUT_VERSION, run_life_policy_period_chain
from ims.accounting.non_life_model_balance import MODEL_BALANCE_INPUT_VERSION, build_non_life_model_balance
from ims.model.vdefmd6_population import VDEFMD6_INSURER_COUNT


FOUR_SECTOR_BALANCE_INPUT_VERSION = "ims.four-sector-balance-input.v1"
FOUR_SECTOR_BALANCE_RESULT_VERSION = "ims.four-sector-balance-result.v1"
SECTOR_IDS = ("motor", "property_liability", "life", "health")
_FIELDS = frozenset(("schema_version", "insurer_id", "scenario_id", "variant_id", "sectors"))
_IDENTIFIER = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,39}\Z")
_STOCKS = ("assets", "liabilities", "equity")
_AMOUNTS = (
    "opening_assets", "opening_liabilities", "opening_equity", "period_profit",
    "capital_contribution", "capital_distribution", "closing_assets",
    "closing_liabilities", "closing_equity",
)
_SOURCE_FIELDS = {
    "motor": ("cash", "claim_liability"),
    "property_liability": ("cash", "claim_liability"),
    "life": ("backing_assets", "guarantee_liability"),
    "health": ("cash", "benefit_liability"),
}


@dataclass(frozen=True, slots=True)
class FourSectorIssue:
    path: str
    code: str
    message: str

    def to_dict(self) -> dict[str, str]:
        return {"path": self.path, "code": self.code, "message": self.message}


@dataclass(frozen=True, slots=True)
class FourSectorBalanceReport:
    insurer_id: int | None
    scenario_id: str | None
    variant_id: str | None
    input_digest: str | None
    sectors: tuple[dict[str, object], ...]
    total_rows: tuple[dict[str, object], ...]
    issues: tuple[FourSectorIssue, ...]

    def to_dict(self) -> dict[str, object]:
        valid = not self.issues
        core: dict[str, object] = {
            "schema_version": FOUR_SECTOR_BALANCE_RESULT_VERSION,
            "insurer_id": self.insurer_id,
            "scenario_id": self.scenario_id,
            "variant_id": self.variant_id,
            "period_count": len(self.total_rows) if valid else 0,
            "input_digest": self.input_digest if valid else None,
            "sector_ids": list(SECTOR_IDS),
            "scenario_linkage": "declared_non_life_and_life_verified_health",
            "historical_mapping_status": "unresolved",
            "sectors": list(self.sectors) if valid else [],
            "total_rows": list(self.total_rows) if valid else [],
        }
        digest = _digest(core) if valid else None
        return {
            **core,
            "status": "ok" if valid else "error",
            "valid": valid,
            "content_digest": digest,
            "issue_count": len(self.issues),
            "issues": [issue.to_dict() for issue in self.issues],
            "writes_performed": False,
            "runner_invoked": False,
            "historical_simulation_performed": False,
            "statutory_or_solvency_ii_claim": False,
            "historical_full_equality_claim": False,
        }


def _digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    ).hexdigest()


def _amount(value: Decimal) -> str:
    return format(Decimal(0) if value.is_zero() else value, ".4f")


def _issue(path: str, code: str, message: str) -> FourSectorIssue:
    return FourSectorIssue(path, code, message)


def four_sector_balance_contract_payload() -> dict[str, object]:
    return {
        "input_schema_version": FOUR_SECTOR_BALANCE_INPUT_VERSION,
        "result_schema_version": FOUR_SECTOR_BALANCE_RESULT_VERSION,
        "calculation_endpoint": "/api/accounting/four-sector-balance",
        "sector_ids": list(SECTOR_IDS),
        "sector_input_schema_versions": {
            "motor": MODEL_BALANCE_INPUT_VERSION,
            "property_liability": MODEL_BALANCE_INPUT_VERSION,
            "life": LIFE_PERIOD_CHAIN_INPUT_VERSION,
            "health": HEALTH_PERIOD_CHAIN_INPUT_VERSION,
        },
        "insurer_id_range": [1, VDEFMD6_INSURER_COUNT],
        "period_range": [1, 100],
        "supported_horizons": sorted(HEALTH_PERIOD_CHAIN_HORIZONS),
        "amount_representation": "decimal_string_4_fraction",
        "normalized_amount_fields": list(_AMOUNTS),
        "scenario_linkage": "declared_non_life_and_life_verified_health",
        "source_kind": "recalculated_explicit_inputs",
        "historical_mapping_status": "unresolved",
        "writes_enabled": False,
        "runner_enabled": False,
        "statutory_or_solvency_ii_claim": False,
        "historical_full_equality_claim": False,
    }


def _project(sector_id: str, row: dict[str, object]) -> dict[str, Decimal | int]:
    asset, liability = _SOURCE_FIELDS[sector_id]
    return {
        "period": row["period"],
        "opening_assets": Decimal(row[f"opening_{asset}"]),
        "opening_liabilities": Decimal(row[f"opening_{liability}"]),
        "opening_equity": Decimal(row["opening_equity"]),
        "period_profit": Decimal(row["period_profit"]),
        "capital_contribution": Decimal(row["capital_contribution"]),
        "capital_distribution": Decimal(row["capital_distribution"]),
        "closing_assets": Decimal(row[f"closing_{asset}"]),
        "closing_liabilities": Decimal(row[f"closing_{liability}"]),
        "closing_equity": Decimal(row["closing_equity"]),
    }


def _check_rows(rows: list[dict[str, Decimal | int]], path: str) -> list[FourSectorIssue]:
    issues = []
    for index, row in enumerate(rows):
        row_path = f"{path}[{index}]"
        if row["period"] != index + 1:
            issues.append(_issue(row_path, "period_sequence_invalid", "Periodenfolge weicht ab"))
        for prefix in ("opening", "closing"):
            if row[f"{prefix}_assets"] != row[f"{prefix}_liabilities"] + row[f"{prefix}_equity"]:
                issues.append(_issue(row_path, "identity_invalid", "Modellbilanz ist nicht ausgeglichen"))
        if row["closing_equity"] != (
            row["opening_equity"] + row["period_profit"]
            + row["capital_contribution"] - row["capital_distribution"]
        ):
            issues.append(_issue(row_path, "equity_movement_invalid", "Eigenkapitalbewegung weicht ab"))
        if index and any(
            row[f"opening_{field}"] != rows[index - 1][f"closing_{field}"]
            for field in _STOCKS
        ):
            issues.append(_issue(row_path, "carryover_invalid", "Vorperiodenschluss weicht vom Anfang ab"))
    return issues


def _serialized(rows: list[dict[str, Decimal | int]]) -> list[dict[str, object]]:
    return [
        {"period": row["period"], **{field: _amount(row[field]) for field in _AMOUNTS}}
        for row in rows
    ]


def build_four_sector_balance(value: object) -> FourSectorBalanceReport:
    """Recalculate every sector and publish nothing until all boundaries agree."""

    issues: list[FourSectorIssue] = []
    if type(value) is not dict:
        return FourSectorBalanceReport(None, None, None, None, (), (), (
            _issue("$", "object_required", "Vier-Sparten-Eingang muss ein Objekt sein"),
        ))
    actual = {key for key in value if type(key) is str}
    for field in sorted(_FIELDS - actual):
        issues.append(_issue(f"$.{field}", "field_missing", f"Pflichtfeld fehlt: {field}"))
    for field in sorted(actual - _FIELDS):
        issues.append(_issue(f"$.{field}", "field_unknown", f"Unbekanntes Feld: {field}"))
    if len(actual) != len(value):
        issues.append(_issue("$", "field_name_invalid", "Feldnamen muessen Text sein"))
    if value.get("schema_version") != FOUR_SECTOR_BALANCE_INPUT_VERSION:
        issues.append(_issue("$.schema_version", "contract_value_mismatch", "Falsche Eingabeversion"))
    insurer_id = value.get("insurer_id")
    if type(insurer_id) is not int or not 1 <= insurer_id <= VDEFMD6_INSURER_COUNT:
        issues.append(_issue("$.insurer_id", "insurer_id_invalid", "VU-ID von 1 bis 25 erforderlich"))
        insurer_id = None
    identifiers = {}
    for field in ("scenario_id", "variant_id"):
        candidate = value.get(field)
        if type(candidate) is not str or _IDENTIFIER.fullmatch(candidate) is None:
            issues.append(_issue(f"$.{field}", "identifier_invalid", "ASCII-Kennung mit 1 bis 40 Zeichen erforderlich"))
            candidate = None
        identifiers[field] = candidate
    sectors = value.get("sectors")
    if type(sectors) is not dict or set(sectors) != set(SECTOR_IDS):
        issues.append(_issue("$.sectors", "sector_set_invalid", "Genau Kfz, Sach-Haftpflicht, Leben und Kranken erforderlich"))
        return FourSectorBalanceReport(insurer_id, identifiers["scenario_id"], identifiers["variant_id"], None, (), (), tuple(issues))
    health_sources = sectors["health"].get("sources") if type(sectors["health"]) is dict else None
    if type(health_sources) is dict:
        for field in ("scenario_id", "variant_id"):
            if identifiers[field] is not None and health_sources.get(field) != identifiers[field]:
                issues.append(_issue(f"$.sectors.health.sources.{field}", "scenario_mismatch", "Krankenquelle gehoert zu einem anderen Szenario"))

    builders = {
        "motor": build_non_life_model_balance,
        "property_liability": build_non_life_model_balance,
        "life": run_life_policy_period_chain,
        "health": run_health_period_chain,
    }
    projected: dict[str, list[dict[str, Decimal | int]]] = {}
    with localcontext() as context:
        context.prec = 64
        for sector_id in SECTOR_IDS:
            report = builders[sector_id](sectors[sector_id])
            for item in report.issues:
                issues.append(_issue(f"$.sectors.{sector_id}{item.path[1:]}", item.code, item.message))
            if type(sectors[sector_id]) is dict and sectors[sector_id].get("sector_id") != sector_id:
                issues.append(_issue(f"$.sectors.{sector_id}.sector_id", "sector_mismatch", "Spartenkennung weicht vom Zuordnungsschluessel ab"))
            if insurer_id is not None and report.insurer_id != insurer_id:
                issues.append(_issue(f"$.sectors.{sector_id}.insurer_id", "insurer_mismatch", "Versicherer-ID weicht ab"))
            if report.issues:
                continue
            raw_rows = report.to_dict()["rows"]
            rows = [_project(sector_id, row) for row in raw_rows]
            issues.extend(_check_rows(rows, f"$.sectors.{sector_id}.rows"))
            projected[sector_id] = rows
        if projected and len({len(rows) for rows in projected.values()}) != 1:
            issues.append(_issue("$.sectors", "period_count_mismatch", "Alle Sparten muessen dasselbe Periodenfenster haben"))
        if issues:
            return FourSectorBalanceReport(insurer_id, identifiers["scenario_id"], identifiers["variant_id"], None, (), (), tuple(issues))
        period_count = len(projected["motor"])
        totals = [
            {
                "period": index + 1,
                **{
                    field: sum((projected[sector][index][field] for sector in SECTOR_IDS), Decimal(0))
                    for field in _AMOUNTS
                },
            }
            for index in range(period_count)
        ]
        issues.extend(_check_rows(totals, "$.total_rows"))
        if issues:
            return FourSectorBalanceReport(insurer_id, identifiers["scenario_id"], identifiers["variant_id"], None, (), (), tuple(issues))
        try:
            input_digest = _digest(value)
        except (TypeError, ValueError):
            return FourSectorBalanceReport(insurer_id, identifiers["scenario_id"], identifiers["variant_id"], None, (), (), (
                _issue("$", "json_invalid", "Eingang muss kanonisch als JSON darstellbar sein"),
            ))
        allocations = tuple({"sector_id": sector, "rows": _serialized(projected[sector])} for sector in SECTOR_IDS)
        return FourSectorBalanceReport(
            insurer_id, identifiers["scenario_id"], identifiers["variant_id"], input_digest,
            allocations, tuple(_serialized(totals)), (),
        )
