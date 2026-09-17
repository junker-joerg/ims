"""Pure, bounded health-period chain from validated sources and explicit flows."""

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import asdict, dataclass, replace
from decimal import Decimal, localcontext

from ims.accounting.health_model_balance import (
    HEALTH_BALANCE_INPUT_VERSION,
    HealthBalanceIssue,
    HealthBalanceRow,
    _amount,
    _canonical_amount,
    _exact_fields,
    _issue,
    _opening,
    build_health_model_balance,
)
from ims.accounting.health_period_sources import (
    HEALTH_PERIOD_SOURCES_INPUT_VERSION,
    _MAX_AMOUNT,
    validate_health_period_sources,
)
from ims.model.health_sector_contract import HEALTH_SECTOR_CONTRACT_VERSION
from ims.model.sector_taxonomy import SECTOR_TAXONOMY_VERSION
from ims.model.vdefmd6_population import VDEFMD6_INSURER_COUNT


HEALTH_PERIOD_CHAIN_INPUT_VERSION = "ims.health-period-chain-input.v1"
HEALTH_PERIOD_CHAIN_RESULT_VERSION = "ims.health-period-chain-result.v1"
HEALTH_PERIOD_CHAIN_HORIZONS = frozenset((1, 2, 5, 10, 25, 50, 100))
_MAX_RESULT_BYTES = 1_000_000
_DOCUMENT_FIELDS = frozenset((
    "schema_version", "health_sector_contract_schema_version",
    "sector_taxonomy_schema_version", "source_kind", "historical_mapping_status",
    "insurer_id", "sector_id", "opening", "sources", "periods",
))
_PERIOD_FIELDS = frozenset((
    "period", "benefits_paid", "investment_result", "operating_expense_paid",
    "capital_contribution", "capital_distribution",
))
_FLOW_FIELDS = tuple(sorted(_PERIOD_FIELDS - {"period"}))
_BALANCE_STOCKS = (
    "opening_cash", "opening_benefit_liability", "opening_equity",
    "closing_cash", "closing_benefit_liability", "closing_equity", "period_profit",
)


@dataclass(frozen=True, slots=True)
class HealthPeriodChainRow:
    balance: HealthBalanceRow
    new_business_policies: int
    exits: int
    premium_per_opening_policy: Decimal
    benefit_per_opening_policy: Decimal

    def to_dict(self) -> dict[str, int | str]:
        return {
            **self.balance.to_dict(),
            "new_business_policies": self.new_business_policies,
            "exits": self.exits,
            "premium_per_opening_policy": _canonical_amount(self.premium_per_opening_policy),
            "benefit_per_opening_policy": _canonical_amount(self.benefit_per_opening_policy),
        }


@dataclass(frozen=True, slots=True)
class HealthPeriodChainReport:
    insurer_id: int | None
    scenario_id: str | None
    variant_id: str | None
    requested_period_count: int
    rows: tuple[HealthPeriodChainRow, ...]
    issues: tuple[HealthBalanceIssue, ...]

    def to_dict(self) -> dict[str, object]:
        valid = not self.issues
        return {
            "schema_version": HEALTH_PERIOD_CHAIN_RESULT_VERSION,
            "input_schema_version": HEALTH_PERIOD_CHAIN_INPUT_VERSION,
            "health_sector_contract_schema_version": HEALTH_SECTOR_CONTRACT_VERSION,
            "source_input_schema_version": HEALTH_PERIOD_SOURCES_INPUT_VERSION,
            "status": "ok" if valid else "error",
            "valid": valid,
            "insurer_id": self.insurer_id,
            "sector_id": "health",
            "source_kind": "versioned_health_period_chain",
            "historical_mapping_status": "unresolved",
            "scenario_id": self.scenario_id,
            "variant_id": self.variant_id,
            "requested_period_count": self.requested_period_count,
            "calculated_period_count": len(self.rows) if valid else 0,
            "rows": [row.to_dict() for row in self.rows] if valid else [],
            "issue_count": len(self.issues),
            "issues": [asdict(issue) for issue in self.issues],
            "writes_performed": False,
            "app_runner_invoked": False,
            "health_period_chain_calculated": valid,
            "statutory_or_solvency_ii_claim": False,
            "historical_full_equality_claim": False,
        }


def _periods(value: object, issues: list[HealthBalanceIssue]) -> list[dict[str, Decimal]]:
    if type(value) is not list or len(value) not in HEALTH_PERIOD_CHAIN_HORIZONS:
        _issue(issues, "$.periods", "horizon_invalid", "Nur 1, 2, 5, 10, 25, 50 oder 100 Perioden sind freigegeben")
        return []
    periods: list[dict[str, Decimal]] = []
    for index, item in enumerate(value):
        path = f"$.periods[{index}]"
        if type(item) is not dict:
            _issue(issues, path, "object_required", "Periodenfluss muss ein Objekt sein")
            continue
        _exact_fields(item, _PERIOD_FIELDS, path, issues)
        if type(item.get("period")) is not int or item["period"] != index + 1:
            _issue(issues, f"{path}.period", "period_sequence_invalid", "Perioden muessen bei 1 beginnen und lueckenlos folgen")
        flow: dict[str, Decimal] = {}
        for field in _FLOW_FIELDS:
            parsed = _amount(item.get(field), field, f"{path}.{field}", issues)
            if parsed is not None:
                flow[field] = parsed
        periods.append(flow)
    return periods


def _source_values(source: dict, field: str) -> dict[int, Decimal]:
    values: dict[int, Decimal] = {}
    for window in source[field]["windows"]:
        amount = Decimal(window["amount_per_opening_policy"])
        for period in range(window["start_period"], window["end_period"] + 1):
            values[period] = amount
    return values


def _source_counts(source: dict, field: str) -> dict[int, int]:
    return {entry["period"]: entry["count"] for entry in source[field]["periods"]}


def _balance_input(
    insurer_id: int, opening: dict[str, Decimal | int], flow: dict[str, Decimal],
) -> dict[str, object]:
    return {
        "schema_version": HEALTH_BALANCE_INPUT_VERSION,
        "health_sector_contract_schema_version": HEALTH_SECTOR_CONTRACT_VERSION,
        "sector_taxonomy_schema_version": SECTOR_TAXONOMY_VERSION,
        "source_kind": "explicit_scenario",
        "historical_mapping_status": "unresolved",
        "insurer_id": insurer_id,
        "sector_id": "health",
        "opening": {
            key: value if type(value) is int else _canonical_amount(value)
            for key, value in opening.items()
        },
        "periods": [{"period": 1, **{
            key: _canonical_amount(value) for key, value in flow.items()
        }}],
    }


def _balance_issue(issue: HealthBalanceIssue, index: int) -> HealthBalanceIssue:
    if issue.path.startswith("$.periods[0]"):
        path = f"$.periods[{index}]" + issue.path[len("$.periods[0]"):]
    elif issue.path.startswith("$.opening") and index > 0:
        path = f"$.periods[{index}].opening" + issue.path[len("$.opening"):]
    else:
        path = issue.path
    return HealthBalanceIssue(path, issue.code, issue.message)


def run_health_period_chain(
    value: object, *, should_cancel: Callable[[], bool] | None = None,
) -> HealthPeriodChainReport:
    """Calculate all requested periods in memory, or return no result rows."""

    issues: list[HealthBalanceIssue] = []
    if type(value) is not dict:
        _issue(issues, "$", "object_required", "Krankenketten-Eingang muss ein Objekt sein")
        return HealthPeriodChainReport(None, None, None, 0, (), tuple(issues))
    _exact_fields(value, _DOCUMENT_FIELDS, "$", issues)
    for field, expected in (
        ("schema_version", HEALTH_PERIOD_CHAIN_INPUT_VERSION),
        ("health_sector_contract_schema_version", HEALTH_SECTOR_CONTRACT_VERSION),
        ("sector_taxonomy_schema_version", SECTOR_TAXONOMY_VERSION),
        ("source_kind", "versioned_health_period_chain"),
        ("historical_mapping_status", "unresolved"),
        ("sector_id", "health"),
    ):
        if value.get(field) != expected:
            _issue(issues, f"$.{field}", "contract_value_mismatch", f"{field} muss {expected!r} sein")
    insurer = value.get("insurer_id")
    if type(insurer) is not int or not 1 <= insurer <= VDEFMD6_INSURER_COUNT:
        _issue(issues, "$.insurer_id", "insurer_id_invalid", "Vdefmd6-VU-ID von 1 bis 25 erforderlich")
        insurer = None
    opening = _opening(value.get("opening"), issues)
    raw_periods = value.get("periods")
    requested = len(raw_periods) if type(raw_periods) is list else 0
    periods = _periods(raw_periods, issues)
    raw_source = value.get("sources")
    source_report = validate_health_period_sources(raw_source)
    for issue in source_report.issues:
        issues.append(HealthBalanceIssue("$.sources" + issue.path[1:], issue.code, issue.message))
    scenario_id = source_report.scenario_id
    variant_id = source_report.variant_id
    if not source_report.issues and type(raw_source) is dict:
        if insurer is not None and raw_source["insurer_id"] != insurer:
            _issue(issues, "$.sources.insurer_id", "source_insurer_mismatch", "Quellenplan und Bilanz haben verschiedene VU-IDs")
        if raw_source["period_count"] != requested:
            _issue(issues, "$.sources.period_count", "source_horizon_mismatch", "Quellenplan und Kette haben verschiedene Horizonte")
        if opening.get("opening_active_policies") != raw_source["opening_active_policies"]:
            _issue(issues, "$.opening.opening_active_policies", "source_opening_mismatch", "Quellenplan und Bilanz haben verschiedene Anfangsvertraege")
    if not issues:
        with localcontext() as context:
            context.prec = 64
            if opening["opening_cash"] != opening["opening_benefit_liability"] + opening["opening_equity"]:
                _issue(issues, "$.opening", "opening_identity_invalid", "Kasse muss Leistungsverpflichtung plus Eigenkapital sein")
    if issues:
        return HealthPeriodChainReport(insurer, scenario_id, variant_id, requested, (), tuple(issues))

    assert insurer is not None and type(raw_source) is dict
    new = _source_counts(raw_source, "new_business")
    exits = _source_counts(raw_source, "exits")
    prices = _source_values(raw_source, "pricing")
    benefits = _source_values(raw_source, "benefits")
    rows: list[HealthPeriodChainRow] = []
    with localcontext() as context:
        context.prec = 64
        for index, template in enumerate(periods):
            if should_cancel is not None and should_cancel():
                _issue(issues, f"$.periods[{index}]", "run_cancelled", "Kranken-Periodenkette vor der naechsten Periode abgebrochen")
                break
            period = index + 1
            active = opening["opening_active_policies"]
            flow = {
                **template,
                "premiums_collected": active * prices[period],
                "benefits_incurred": active * benefits[period],
            }
            calculated = build_health_model_balance(_balance_input(insurer, opening, flow))
            if calculated.issues:
                issues.extend(_balance_issue(issue, index) for issue in calculated.issues)
                break
            balance = replace(
                calculated.rows[0], period=period,
                closing_active_policies=active - exits[period] + new[period],
            )
            if any(abs(getattr(balance, field)) > _MAX_AMOUNT for field in _BALANCE_STOCKS):
                _issue(issues, f"$.periods[{index}]", "balance_amount_overflow", "Bilanzwert uebersteigt 12+4 Stellen")
                break
            rows.append(HealthPeriodChainRow(
                balance, new[period], exits[period], prices[period], benefits[period],
            ))
            opening = {
                "opening_active_policies": balance.closing_active_policies,
                "opening_cash": balance.closing_cash,
                "opening_benefit_liability": balance.closing_benefit_liability,
                "opening_equity": balance.closing_equity,
            }
    if not issues:
        result_size = len(json.dumps(
            [row.to_dict() for row in rows], sort_keys=True, separators=(",", ":"),
        ).encode("utf-8"))
        if result_size > _MAX_RESULT_BYTES:
            _issue(issues, "$.periods", "result_budget_exceeded", "Ergebnisbudget von 1 MB ueberschritten")
    return HealthPeriodChainReport(
        insurer, scenario_id, variant_id, requested, tuple(rows) if not issues else (),
        tuple(issues),
    )
