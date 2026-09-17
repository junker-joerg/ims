"""Deterministic small health balance from explicit IMS-2.x scenario values."""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from decimal import Decimal, localcontext

from ims.model.health_sector_contract import HEALTH_FIELDS, HEALTH_SECTOR_CONTRACT_VERSION
from ims.model.sector_taxonomy import SECTOR_TAXONOMY_VERSION
from ims.model.vdefmd6_population import VDEFMD6_INSURER_COUNT


HEALTH_BALANCE_INPUT_VERSION = "ims.health-model-balance-input.v1"
HEALTH_BALANCE_RESULT_VERSION = "ims.health-model-balance-result.v1"
_AMOUNT_PATTERN = re.compile(r"-?(?:0|[1-9][0-9]{0,11})(?:\.[0-9]{1,4})?\Z")
_DOCUMENT_FIELDS = frozenset((
    "schema_version", "health_sector_contract_schema_version",
    "sector_taxonomy_schema_version", "source_kind", "historical_mapping_status",
    "insurer_id", "sector_id", "opening", "periods",
))
_OPENING_FIELDS = tuple(field.field_id for field in HEALTH_FIELDS if field.kind == "opening_stock")
_FLOW_FIELDS = tuple(field.field_id for field in HEALTH_FIELDS if field.kind == "period_flow")
_SIGNED_FIELDS = frozenset(field.field_id for field in HEALTH_FIELDS if field.sign == "signed")


@dataclass(frozen=True, slots=True)
class HealthBalanceIssue:
    path: str
    code: str
    message: str


@dataclass(frozen=True, slots=True)
class HealthBalanceRow:
    period: int
    opening_active_policies: int
    opening_cash: Decimal
    opening_benefit_liability: Decimal
    opening_equity: Decimal
    premiums_collected: Decimal
    benefits_incurred: Decimal
    benefits_paid: Decimal
    investment_result: Decimal
    operating_expense_paid: Decimal
    capital_contribution: Decimal
    capital_distribution: Decimal
    period_profit: Decimal
    closing_active_policies: int
    closing_cash: Decimal
    closing_benefit_liability: Decimal
    closing_equity: Decimal

    def to_dict(self) -> dict[str, int | str]:
        return {
            key: value if type(value) is int else _canonical_amount(value)
            for key, value in asdict(self).items()
        }


@dataclass(frozen=True, slots=True)
class HealthBalanceReport:
    insurer_id: int | None
    requested_period_count: int
    rows: tuple[HealthBalanceRow, ...]
    issues: tuple[HealthBalanceIssue, ...]

    def to_dict(self) -> dict[str, object]:
        valid = not self.issues
        return {
            "schema_version": HEALTH_BALANCE_RESULT_VERSION,
            "input_schema_version": HEALTH_BALANCE_INPUT_VERSION,
            "health_sector_contract_schema_version": HEALTH_SECTOR_CONTRACT_VERSION,
            "status": "ok" if valid else "error",
            "valid": valid,
            "insurer_id": self.insurer_id,
            "sector_id": "health",
            "source_kind": "explicit_scenario",
            "historical_mapping_status": "unresolved",
            "requested_period_count": self.requested_period_count,
            "calculated_period_count": len(self.rows) if valid else 0,
            "rows": [row.to_dict() for row in self.rows] if valid else [],
            "issue_count": len(self.issues),
            "issues": [asdict(issue) for issue in self.issues],
            "writes_performed": False,
            "runner_invoked": False,
            "simulation_performed": False,
            "statutory_or_solvency_ii_claim": False,
            "historical_full_equality_claim": False,
        }


def _canonical_amount(value: Decimal) -> str:
    return format(Decimal(0) if value.is_zero() else value, ".4f")


def _issue(issues: list[HealthBalanceIssue], path: str, code: str, message: str) -> None:
    issues.append(HealthBalanceIssue(path, code, message))


def _exact_fields(
    value: dict, expected: frozenset[str], path: str, issues: list[HealthBalanceIssue]
) -> None:
    actual = {key for key in value if type(key) is str}
    for key in sorted(expected - actual):
        _issue(issues, f"{path}.{key}", "field_missing", f"Pflichtfeld fehlt: {key}")
    for key in sorted(actual - expected):
        _issue(issues, f"{path}.{key}", "field_unknown", f"Unbekanntes Feld: {key}")
    if len(actual) != len(value):
        _issue(issues, path, "field_name_invalid", "Feldnamen muessen Text sein")


def _amount(
    value: object, field: str, path: str, issues: list[HealthBalanceIssue]
) -> Decimal | None:
    if type(value) is not str or _AMOUNT_PATTERN.fullmatch(value) is None:
        _issue(issues, path, "decimal_string_required", "Dezimalstring mit hoechstens 12+4 Stellen erforderlich")
        return None
    amount = Decimal(value)
    if field not in _SIGNED_FIELDS and amount < 0:
        _issue(issues, path, "negative_amount", "Betrag darf nicht negativ sein")
        return None
    return amount


def _opening(value: object, issues: list[HealthBalanceIssue]) -> dict[str, Decimal | int]:
    if type(value) is not dict:
        _issue(issues, "$.opening", "object_required", "Anfangsbestand muss ein Objekt sein")
        return {}
    _exact_fields(value, frozenset(_OPENING_FIELDS), "$.opening", issues)
    parsed: dict[str, Decimal | int] = {}
    count = value.get("opening_active_policies")
    if type(count) is not int or not 0 <= count <= 1_000_000_000:
        _issue(issues, "$.opening.opening_active_policies", "count_invalid", "Ganzzahl von 0 bis 1 Milliarde erforderlich")
    else:
        parsed["opening_active_policies"] = count
    for name in _OPENING_FIELDS:
        if name == "opening_active_policies" or name not in value:
            continue
        amount = _amount(value[name], name, f"$.opening.{name}", issues)
        if amount is not None:
            parsed[name] = amount
    return parsed


def _periods(value: object, issues: list[HealthBalanceIssue]) -> list[dict[str, Decimal]]:
    if type(value) is not list or not 1 <= len(value) <= 2:
        _issue(issues, "$.periods", "period_count_invalid", "PR169 erlaubt genau 1 oder 2 Perioden")
        return []
    parsed: list[dict[str, Decimal]] = []
    expected = frozenset(("period", *_FLOW_FIELDS))
    for index, item in enumerate(value):
        path = f"$.periods[{index}]"
        if type(item) is not dict:
            _issue(issues, path, "object_required", "Periodenobjekt erforderlich")
            continue
        _exact_fields(item, expected, path, issues)
        if type(item.get("period")) is not int or item["period"] != index + 1:
            _issue(issues, f"{path}.period", "period_sequence_invalid", "Perioden muessen bei 1 beginnen und lueckenlos folgen")
        row: dict[str, Decimal] = {}
        for name in _FLOW_FIELDS:
            if name in item:
                amount = _amount(item[name], name, f"{path}.{name}", issues)
                if amount is not None:
                    row[name] = amount
        parsed.append(row)
    return parsed


def _calculate(
    insurer_id: int, opening: dict[str, Decimal | int], periods: list[dict[str, Decimal]]
) -> HealthBalanceReport:
    rows: list[HealthBalanceRow] = []
    for index, flow in enumerate(periods):
        path = f"$.periods[{index}]"
        issues: list[HealthBalanceIssue] = []
        if opening["opening_active_policies"] == 0:
            for name in ("premiums_collected", "benefits_incurred"):
                if flow[name] != 0:
                    _issue(issues, f"{path}.{name}", "flow_without_active_policies", "Ohne aktive Vertraege kein neuer Beitrags- oder Leistungsfluss")
        available_benefits = opening["opening_benefit_liability"] + flow["benefits_incurred"]
        if flow["benefits_paid"] > available_benefits:
            _issue(issues, f"{path}.benefits_paid", "benefits_exceed_liability", "Auszahlung uebersteigt offene und angefallene Leistungen")
        closing_liability = available_benefits - flow["benefits_paid"]
        closing_cash = (
            opening["opening_cash"] + flow["premiums_collected"]
            + flow["investment_result"] + flow["capital_contribution"]
            - flow["benefits_paid"] - flow["operating_expense_paid"]
            - flow["capital_distribution"]
        )
        period_profit = (
            flow["premiums_collected"] + flow["investment_result"]
            - flow["benefits_incurred"] - flow["operating_expense_paid"]
        )
        closing_equity = (
            opening["opening_equity"] + period_profit
            + flow["capital_contribution"] - flow["capital_distribution"]
        )
        if closing_cash < 0:
            _issue(issues, path, "negative_closing_cash", "Kassen-Schlussbestand waere negativ")
        if closing_cash != closing_liability + closing_equity:
            _issue(issues, path, "closing_identity_invalid", "Schlussbilanz ist nicht ausgeglichen")
        if issues:
            return HealthBalanceReport(insurer_id, len(periods), (), tuple(issues))
        rows.append(HealthBalanceRow(
            period=index + 1,
            **opening,
            **flow,
            period_profit=period_profit,
            closing_active_policies=opening["opening_active_policies"],
            closing_cash=closing_cash,
            closing_benefit_liability=closing_liability,
            closing_equity=closing_equity,
        ))
        opening = {
            "opening_active_policies": opening["opening_active_policies"],
            "opening_cash": closing_cash,
            "opening_benefit_liability": closing_liability,
            "opening_equity": closing_equity,
        }
    return HealthBalanceReport(insurer_id, len(periods), tuple(rows), ())


def build_health_model_balance(value: object) -> HealthBalanceReport:
    """Validate the complete small case before exposing any calculated row."""

    issues: list[HealthBalanceIssue] = []
    if type(value) is not dict:
        _issue(issues, "$", "object_required", "Kranken-Eingang muss ein Objekt sein")
        return HealthBalanceReport(None, 0, (), tuple(issues))
    _exact_fields(value, _DOCUMENT_FIELDS, "$", issues)
    for name, expected in (
        ("schema_version", HEALTH_BALANCE_INPUT_VERSION),
        ("health_sector_contract_schema_version", HEALTH_SECTOR_CONTRACT_VERSION),
        ("sector_taxonomy_schema_version", SECTOR_TAXONOMY_VERSION),
        ("source_kind", "explicit_scenario"),
        ("historical_mapping_status", "unresolved"),
        ("sector_id", "health"),
    ):
        if value.get(name) != expected:
            _issue(issues, f"$.{name}", "contract_value_mismatch", f"{name} muss {expected!r} sein")
    insurer_id = value.get("insurer_id")
    if type(insurer_id) is not int or not 1 <= insurer_id <= VDEFMD6_INSURER_COUNT:
        _issue(issues, "$.insurer_id", "insurer_id_invalid", "Vdefmd6-VU-ID von 1 bis 25 erforderlich")
        insurer_id = None
    opening = _opening(value.get("opening"), issues)
    raw_periods = value.get("periods")
    requested_count = len(raw_periods) if type(raw_periods) is list else 0
    periods = _periods(raw_periods, issues)
    if issues:
        return HealthBalanceReport(insurer_id, requested_count, (), tuple(issues))
    assert insurer_id is not None
    with localcontext() as context:
        context.prec = 64
        if opening["opening_cash"] != opening["opening_benefit_liability"] + opening["opening_equity"]:
            _issue(issues, "$.opening", "opening_identity_invalid", "Kasse muss Leistungsverpflichtung plus Eigenkapital sein")
            return HealthBalanceReport(insurer_id, requested_count, (), tuple(issues))
        return _calculate(insurer_id, opening, periods)
