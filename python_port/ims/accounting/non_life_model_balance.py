"""Deterministic, scenario-sourced non-life model balance without legacy binding."""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from decimal import Decimal, localcontext

from ims.accounting.model_balance_contract import (
    BALANCE_FIELDS,
    MODEL_BALANCE_CONTRACT_VERSION,
)
from ims.model.sector_taxonomy import SECTOR_TAXONOMY_VERSION
from ims.model.vdefmd6_population import VDEFMD6_INSURER_COUNT


MODEL_BALANCE_INPUT_VERSION = "ims.insurer-model-balance-input.v1"
MODEL_BALANCE_RESULT_VERSION = "ims.insurer-model-balance-result.v1"
_AMOUNT_PATTERN = re.compile(r"-?(?:0|[1-9][0-9]{0,11})(?:\.[0-9]{1,4})?\Z")
_SECTOR_IDS = frozenset(("motor", "property_liability"))
_OPENING_FIELDS = tuple(field.field_id for field in BALANCE_FIELDS if field.kind == "opening_stock")
_FLOW_FIELDS = tuple(field.field_id for field in BALANCE_FIELDS if field.kind == "period_flow")
_NONNEGATIVE_FIELDS = frozenset(field.field_id for field in BALANCE_FIELDS if field.sign == "nonnegative")
_DOCUMENT_FIELDS = frozenset(
    (
        "schema_version", "model_balance_contract_schema_version",
        "sector_taxonomy_schema_version", "source_kind", "historical_mapping_status",
        "insurer_id", "sector_id", "opening", "periods",
    )
)


@dataclass(frozen=True, slots=True)
class ModelBalanceIssue:
    path: str
    code: str
    message: str


@dataclass(frozen=True, slots=True)
class ModelBalanceRow:
    period: int
    opening_cash: Decimal
    opening_claim_liability: Decimal
    opening_equity: Decimal
    premium_income: Decimal
    investment_income: Decimal
    claims_incurred: Decimal
    claims_paid: Decimal
    operating_expense: Decimal
    capital_contribution: Decimal
    capital_distribution: Decimal
    period_profit: Decimal
    closing_cash: Decimal
    closing_claim_liability: Decimal
    closing_equity: Decimal

    def to_dict(self) -> dict[str, int | str]:
        values = asdict(self)
        return {
            key: value if key == "period" else _canonical_amount(value)
            for key, value in values.items()
        }


@dataclass(frozen=True, slots=True)
class ModelBalanceReport:
    insurer_id: int | None
    sector_id: str | None
    requested_period_count: int
    rows: tuple[ModelBalanceRow, ...]
    issues: tuple[ModelBalanceIssue, ...]

    def to_dict(self) -> dict[str, object]:
        valid = not self.issues
        return {
            "schema_version": MODEL_BALANCE_RESULT_VERSION,
            "input_schema_version": MODEL_BALANCE_INPUT_VERSION,
            "model_balance_contract_schema_version": MODEL_BALANCE_CONTRACT_VERSION,
            "status": "ok" if valid else "error",
            "valid": valid,
            "insurer_id": self.insurer_id,
            "sector_id": self.sector_id,
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
            "historical_full_equality_claim": False,
        }


def _canonical_amount(value: Decimal) -> str:
    return format(Decimal(0) if value.is_zero() else value, ".4f")


def _issue(issues: list[ModelBalanceIssue], path: str, code: str, message: str) -> None:
    issues.append(ModelBalanceIssue(path, code, message))


def _exact_fields(
    value: dict, expected: frozenset[str], path: str, issues: list[ModelBalanceIssue]
) -> None:
    actual = {key for key in value if type(key) is str}
    for key in sorted(expected - actual):
        _issue(issues, f"{path}.{key}", "field_missing", f"Pflichtfeld fehlt: {key}")
    for key in sorted(actual - expected):
        _issue(issues, f"{path}.{key}", "field_unknown", f"Unbekanntes Feld: {key}")
    if len(actual) != len(value):
        _issue(issues, path, "field_name_invalid", "Feldnamen muessen Text sein")


def _amount(value: object, field: str, path: str, issues: list[ModelBalanceIssue]) -> Decimal | None:
    if type(value) is not str or _AMOUNT_PATTERN.fullmatch(value) is None:
        _issue(
            issues, path, "decimal_string_required",
            "Dezimalstring mit hoechstens 12 Vorkomma- und vier Nachkommastellen erforderlich",
        )
        return None
    amount = Decimal(value)
    if field in _NONNEGATIVE_FIELDS and amount < 0:
        _issue(issues, path, "negative_amount", "Betrag darf nicht negativ sein")
        return None
    return amount


def _amount_fields(
    value: object, names: tuple[str, ...], path: str, issues: list[ModelBalanceIssue]
) -> dict[str, Decimal]:
    if type(value) is not dict:
        _issue(issues, path, "object_required", "Betragsobjekt erforderlich")
        return {}
    _exact_fields(value, frozenset(names), path, issues)
    parsed: dict[str, Decimal] = {}
    for name in names:
        if name in value:
            amount = _amount(value[name], name, f"{path}.{name}", issues)
            if amount is not None:
                parsed[name] = amount
    return parsed


def _parse_periods(value: object, issues: list[ModelBalanceIssue]) -> list[dict[str, Decimal]]:
    if type(value) is not list or not 1 <= len(value) <= 100:
        _issue(issues, "$.periods", "period_count_invalid", "1 bis 100 Perioden erforderlich")
        return []
    parsed: list[dict[str, Decimal]] = []
    expected = frozenset(("period", *_FLOW_FIELDS))
    for index, item in enumerate(value):
        path = f"$.periods[{index}]"
        if type(item) is not dict:
            _issue(issues, path, "object_required", "Periodenobjekt erforderlich")
            continue
        _exact_fields(item, expected, path, issues)
        period = item.get("period")
        if type(period) is not int or period != index + 1:
            _issue(issues, f"{path}.period", "period_sequence_invalid", "Perioden muessen bei 1 beginnen und lueckenlos folgen")
        row: dict[str, Decimal] = {}
        for name in _FLOW_FIELDS:
            if name in item:
                amount = _amount(item[name], name, f"{path}.{name}", issues)
                if amount is not None:
                    row[name] = amount
        parsed.append(row)
    return parsed


def _calculate_valid_balance(
    insurer_id: int,
    sector_id: str,
    opening: dict[str, Decimal],
    periods: list[dict[str, Decimal]],
) -> ModelBalanceReport:
    rows: list[ModelBalanceRow] = []
    for index, flow in enumerate(periods):
        period_profit = (
            flow["premium_income"] + flow["investment_income"]
            - flow["claims_incurred"] - flow["operating_expense"]
        )
        closing_cash = (
            opening["opening_cash"] + flow["premium_income"] + flow["investment_income"]
            + flow["capital_contribution"] - flow["claims_paid"]
            - flow["operating_expense"] - flow["capital_distribution"]
        )
        closing_claim_liability = (
            opening["opening_claim_liability"] + flow["claims_incurred"] - flow["claims_paid"]
        )
        closing_equity = (
            opening["opening_equity"] + period_profit + flow["capital_contribution"]
            - flow["capital_distribution"]
        )
        path = f"$.periods[{index}]"
        issues: list[ModelBalanceIssue] = []
        if closing_cash < 0:
            _issue(issues, path, "negative_closing_cash", "Cash-Schlussbestand waere negativ")
        if closing_claim_liability < 0:
            _issue(issues, path, "negative_closing_claim_liability", "Schadenverbindlichkeit waere negativ")
        if closing_cash != closing_claim_liability + closing_equity:
            _issue(issues, path, "closing_identity_invalid", "Schlussbilanz ist nicht ausgeglichen")
        if issues:
            return ModelBalanceReport(insurer_id, sector_id, len(periods), (), tuple(issues))

        rows.append(ModelBalanceRow(
            period=index + 1,
            **opening,
            **flow,
            period_profit=period_profit,
            closing_cash=closing_cash,
            closing_claim_liability=closing_claim_liability,
            closing_equity=closing_equity,
        ))
        opening = {
            "opening_cash": closing_cash,
            "opening_claim_liability": closing_claim_liability,
            "opening_equity": closing_equity,
        }
    return ModelBalanceReport(insurer_id, sector_id, len(periods), tuple(rows), ())


def build_non_life_model_balance(value: object) -> ModelBalanceReport:
    """Validate all explicit inputs and calculate only a complete model balance."""

    issues: list[ModelBalanceIssue] = []
    if type(value) is not dict:
        _issue(issues, "$", "object_required", "Bilanz-Eingang muss ein Objekt sein")
        return ModelBalanceReport(None, None, 0, (), tuple(issues))

    _exact_fields(value, _DOCUMENT_FIELDS, "$", issues)
    for name, expected in (
        ("schema_version", MODEL_BALANCE_INPUT_VERSION),
        ("model_balance_contract_schema_version", MODEL_BALANCE_CONTRACT_VERSION),
        ("sector_taxonomy_schema_version", SECTOR_TAXONOMY_VERSION),
        ("source_kind", "explicit_scenario"),
        ("historical_mapping_status", "unresolved"),
    ):
        if value.get(name) != expected:
            _issue(issues, f"$.{name}", "contract_value_mismatch", f"{name} muss {expected!r} sein")

    insurer_id = value.get("insurer_id")
    if type(insurer_id) is not int or not 1 <= insurer_id <= VDEFMD6_INSURER_COUNT:
        _issue(issues, "$.insurer_id", "insurer_id_invalid", "Vdefmd6-VU-ID von 1 bis 25 erforderlich")
        insurer_id = None
    sector_id = value.get("sector_id")
    if type(sector_id) is not str or sector_id not in _SECTOR_IDS:
        _issue(issues, "$.sector_id", "sector_id_invalid", "Kfz oder Sach-Haftpflicht erforderlich")
        sector_id = None

    opening = _amount_fields(value.get("opening"), _OPENING_FIELDS, "$.opening", issues)
    raw_periods = value.get("periods")
    requested_count = len(raw_periods) if type(raw_periods) is list else 0
    periods = _parse_periods(raw_periods, issues)
    if issues:
        return ModelBalanceReport(insurer_id, sector_id, requested_count, (), tuple(issues))
    assert insurer_id is not None and sector_id is not None
    with localcontext() as context:
        context.prec = 64
        if opening["opening_cash"] != opening["opening_claim_liability"] + opening["opening_equity"]:
            _issue(issues, "$.opening", "opening_identity_invalid", "Cash muss Schadenverbindlichkeit plus Eigenkapital sein")
            return ModelBalanceReport(insurer_id, sector_id, requested_count, (), tuple(issues))
        return _calculate_valid_balance(insurer_id, sector_id, opening, periods)
