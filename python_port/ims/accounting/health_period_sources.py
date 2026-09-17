"""Validate explicit health portfolio sources without calculating a period chain."""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from decimal import Decimal, localcontext

from ims.accounting.health_model_balance import HealthBalanceIssue, _amount, _exact_fields, _issue
from ims.model.health_sector_contract import HEALTH_SECTOR_CONTRACT_VERSION
from ims.model.sector_taxonomy import SECTOR_TAXONOMY_VERSION
from ims.model.vdefmd6_population import VDEFMD6_INSURER_COUNT


HEALTH_PERIOD_SOURCES_INPUT_VERSION = "ims.health-period-sources-input.v1"
HEALTH_PERIOD_SOURCES_RESULT_VERSION = "ims.health-period-sources-result.v1"
_IDENTIFIER = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,39}\Z")
_MAX_POLICIES = 1_000_000_000
_MAX_AMOUNT = Decimal("999999999999.9999")
_DOCUMENT_FIELDS = frozenset((
    "schema_version", "health_sector_contract_schema_version",
    "sector_taxonomy_schema_version", "source_kind", "historical_mapping_status",
    "insurer_id", "sector_id", "scenario_id", "variant_id", "period_count",
    "opening_active_policies", "new_business", "exits", "pricing", "benefits",
))


@dataclass(frozen=True, slots=True)
class HealthPeriodSourcesReport:
    insurer_id: int | None
    scenario_id: str | None
    variant_id: str | None
    requested_period_count: int
    issues: tuple[HealthBalanceIssue, ...]

    def to_dict(self) -> dict[str, object]:
        valid = not self.issues
        return {
            "schema_version": HEALTH_PERIOD_SOURCES_RESULT_VERSION,
            "input_schema_version": HEALTH_PERIOD_SOURCES_INPUT_VERSION,
            "health_sector_contract_schema_version": HEALTH_SECTOR_CONTRACT_VERSION,
            "status": "ok" if valid else "error",
            "valid": valid,
            "insurer_id": self.insurer_id,
            "sector_id": "health",
            "scenario_id": self.scenario_id,
            "variant_id": self.variant_id,
            "requested_period_count": self.requested_period_count,
            "validated_period_count": self.requested_period_count if valid else 0,
            "issue_count": len(self.issues),
            "issues": [asdict(issue) for issue in self.issues],
            "writes_performed": False,
            "runner_invoked": False,
            "simulation_performed": False,
            "historical_full_equality_claim": False,
        }


def _identifier(value: object, path: str, issues: list[HealthBalanceIssue]) -> str | None:
    if type(value) is not str or _IDENTIFIER.fullmatch(value) is None:
        _issue(issues, path, "identifier_invalid", "ASCII-Kennung mit 1 bis 40 Zeichen erforderlich")
        return None
    return value


def _count(value: object, path: str, issues: list[HealthBalanceIssue]) -> int | None:
    if type(value) is not int or not 0 <= value <= _MAX_POLICIES:
        _issue(issues, path, "count_invalid", "Ganzzahl von 0 bis 1 Milliarde erforderlich")
        return None
    return value


def _period(value: object, path: str, period_count: int, issues: list[HealthBalanceIssue]) -> int | None:
    if type(value) is not int or not 1 <= value <= period_count:
        _issue(issues, path, "period_invalid", "Periode muss im gewaehlten Horizont liegen")
        return None
    return value


def _count_source(
    value: object, path: str, actor: str, period_count: int,
    issues: list[HealthBalanceIssue],
) -> dict[int, int]:
    if type(value) is not dict:
        _issue(issues, path, "object_required", "Quellenobjekt erforderlich")
        return {}
    _exact_fields(value, frozenset(("actor_type", "mode", "periods")), path, issues)
    if value.get("actor_type") != actor:
        _issue(issues, f"{path}.actor_type", "actor_mismatch", f"Akteur muss {actor!r} sein")
    if value.get("mode") != "explicit_scenario_counts":
        _issue(issues, f"{path}.mode", "source_mode_invalid", "Nur explizite Szenariozahlen sind freigegeben")
    rows = value.get("periods")
    if type(rows) is not list or len(rows) != period_count:
        _issue(issues, f"{path}.periods", "period_coverage_invalid", "Genau ein Wert je Periode erforderlich")
        return {}
    counts: dict[int, int] = {}
    seen: set[int] = set()
    for index, row in enumerate(rows):
        row_path = f"{path}.periods[{index}]"
        if type(row) is not dict:
            _issue(issues, row_path, "object_required", "Periodenwert muss ein Objekt sein")
            continue
        _exact_fields(row, frozenset(("period", "count")), row_path, issues)
        period = _period(row.get("period"), f"{row_path}.period", period_count, issues)
        count = _count(row.get("count"), f"{row_path}.count", issues)
        if period is not None:
            if period in seen:
                _issue(issues, f"{row_path}.period", "period_duplicate", "Periode kommt mehrfach vor")
            seen.add(period)
            if count is not None:
                counts[period] = count
    if seen != set(range(1, period_count + 1)):
        _issue(issues, f"{path}.periods", "period_coverage_invalid", "Alle Perioden muessen genau einmal belegt sein")
    return counts


def _window_source(
    value: object, path: str, actor: str, mode: str, period_count: int,
    issues: list[HealthBalanceIssue],
) -> dict[int, Decimal]:
    if type(value) is not dict:
        _issue(issues, path, "object_required", "Quellenobjekt erforderlich")
        return {}
    _exact_fields(value, frozenset(("actor_type", "mode", "windows")), path, issues)
    if value.get("actor_type") != actor:
        _issue(issues, f"{path}.actor_type", "actor_mismatch", f"Akteur muss {actor!r} sein")
    if value.get("mode") != mode:
        _issue(issues, f"{path}.mode", "source_mode_invalid", f"Quellenmodus muss {mode!r} sein")
    windows = value.get("windows")
    if type(windows) is not list or not 1 <= len(windows) <= period_count:
        _issue(issues, f"{path}.windows", "window_count_invalid", "1 bis period_count Fenster erforderlich")
        return {}
    values: dict[int, Decimal] = {}
    for index, window in enumerate(windows):
        window_path = f"{path}.windows[{index}]"
        if type(window) is not dict:
            _issue(issues, window_path, "object_required", "Fenster muss ein Objekt sein")
            continue
        _exact_fields(window, frozenset((
            "start_period", "end_period", "amount_per_opening_policy",
        )), window_path, issues)
        start = _period(window.get("start_period"), f"{window_path}.start_period", period_count, issues)
        end = _period(window.get("end_period"), f"{window_path}.end_period", period_count, issues)
        amount = _amount(
            window.get("amount_per_opening_policy"), "amount_per_opening_policy",
            f"{window_path}.amount_per_opening_policy", issues,
        )
        if start is None or end is None or amount is None:
            continue
        if end < start:
            _issue(issues, window_path, "window_reversed", "Fensterende liegt vor dem Anfang")
            continue
        for period in range(start, end + 1):
            if period in values:
                _issue(issues, f"{window_path}.start_period", "window_overlap", "Fenster ueberlappen sich")
            values[period] = amount
    if set(values) != set(range(1, period_count + 1)):
        _issue(issues, f"{path}.windows", "window_coverage_invalid", "Fenster muessen den Horizont lueckenlos abdecken")
    return values


def validate_health_period_sources(value: object) -> HealthPeriodSourcesReport:
    """Check a complete health source plan atomically; produce no balance or rows."""

    issues: list[HealthBalanceIssue] = []
    if type(value) is not dict:
        _issue(issues, "$", "object_required", "Kranken-Quellenplan muss ein Objekt sein")
        return HealthPeriodSourcesReport(None, None, None, 0, tuple(issues))
    _exact_fields(value, _DOCUMENT_FIELDS, "$", issues)
    for field, expected in (
        ("schema_version", HEALTH_PERIOD_SOURCES_INPUT_VERSION),
        ("health_sector_contract_schema_version", HEALTH_SECTOR_CONTRACT_VERSION),
        ("sector_taxonomy_schema_version", SECTOR_TAXONOMY_VERSION),
        ("source_kind", "versioned_health_period_sources"),
        ("historical_mapping_status", "unresolved"),
        ("sector_id", "health"),
    ):
        if value.get(field) != expected:
            _issue(issues, f"$.{field}", "contract_value_mismatch", f"{field} muss {expected!r} sein")
    insurer = value.get("insurer_id")
    if type(insurer) is not int or not 1 <= insurer <= VDEFMD6_INSURER_COUNT:
        _issue(issues, "$.insurer_id", "insurer_id_invalid", "Vdefmd6-VU-ID von 1 bis 25 erforderlich")
        insurer = None
    scenario_id = _identifier(value.get("scenario_id"), "$.scenario_id", issues)
    variant_id = _identifier(value.get("variant_id"), "$.variant_id", issues)
    period_count = value.get("period_count")
    if type(period_count) is not int or not 1 <= period_count <= 100:
        _issue(issues, "$.period_count", "period_count_invalid", "1 bis 100 IMS-Modellperioden erforderlich")
        return HealthPeriodSourcesReport(insurer, scenario_id, variant_id, 0, tuple(issues))
    opening = _count(value.get("opening_active_policies"), "$.opening_active_policies", issues)
    new_business = _count_source(value.get("new_business"), "$.new_business", "market", period_count, issues)
    exits = _count_source(value.get("exits"), "$.exits", "policyholder", period_count, issues)
    pricing = _window_source(
        value.get("pricing"), "$.pricing", "insurer", "explicit_insurer_price_windows",
        period_count, issues,
    )
    benefits = _window_source(
        value.get("benefits"), "$.benefits", "exogenous", "explicit_benefit_cost_windows",
        period_count, issues,
    )
    if not issues and opening is not None:
        with localcontext() as context:
            context.prec = 64
            active = opening
            for period in range(1, period_count + 1):
                if exits[period] > active:
                    _issue(issues, "$.exits.periods", "exits_exceed_opening", f"Abgang in Periode {period} uebersteigt den aktiven Anfangsbestand")
                    break
                stock_overflow = active - exits[period] + new_business[period] > _MAX_POLICIES
                if stock_overflow:
                    _issue(issues, "$.new_business.periods", "closing_count_overflow", f"Schlussbestand in Periode {period} uebersteigt eine Milliarde")
                for source, values in (("pricing", pricing), ("benefits", benefits)):
                    if active * values[period] > _MAX_AMOUNT:
                        _issue(issues, f"$.{source}.windows", "flow_amount_overflow", "Stueckbetrag mal Anfangsbestand uebersteigt 12+4 Stellen")
                if stock_overflow:
                    break
                active = active - exits[period] + new_business[period]
    return HealthPeriodSourcesReport(insurer, scenario_id, variant_id, period_count, tuple(issues))
