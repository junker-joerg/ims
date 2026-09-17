"""Deterministic life accounting for named cohorts and explicit new business."""

from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import asdict, dataclass
from decimal import Decimal, ROUND_HALF_EVEN, localcontext
from typing import TypeVar, cast

from ims.accounting.life_closed_cohort_balance import (
    _RATE_PATTERN, _QUANTUM, _amount, _exact_fields, _issue,
)
from ims.accounting.life_model_balance import LifeBalanceIssue
from ims.model.life_sector_v3_contract import LIFE_SECTOR_V3_CONTRACT_VERSION
from ims.model.sector_taxonomy import SECTOR_TAXONOMY_VERSION
from ims.model.vdefmd6_population import VDEFMD6_INSURER_COUNT


LIFE_COHORT_INPUT_VERSION = "ims.life-cohort-balance-input.v1"
LIFE_COHORT_RESULT_VERSION = "ims.life-cohort-balance-result.v1"
_COHORT_ID_PATTERN = re.compile(r"[A-Za-z][A-Za-z0-9_-]{0,31}\Z")
_DOCUMENT_FIELDS = frozenset((
    "schema_version", "life_sector_contract_schema_version",
    "sector_taxonomy_schema_version", "source_kind", "historical_mapping_status",
    "insurer_id", "sector_id", "opening", "periods",
))
_COHORT_FIELDS = frozenset((
    "cohort_id", "issue_period", "issue_term_periods", "remaining_periods",
    "active_policies", "guaranteed_rate_per_period", "guarantee_liability",
))
_FLOW_FIELDS = frozenset((
    "cohort_id", "renewal_premiums_collected", "renewal_liability_allocation",
    "deaths", "death_benefits_paid",
))
_ISSUE_FIELDS = frozenset((
    "cohort_id", "issue_term_periods", "guaranteed_rate_per_period",
    "new_business_policies", "new_business_premiums_collected",
    "new_business_liability_allocation",
))
_PERIOD_FIELDS = frozenset((
    "period", "cohort_flows", "new_business", "investment_result",
    "operating_expense_paid", "capital_contribution", "capital_distribution",
))


@dataclass(frozen=True, slots=True)
class LifeCohort:
    cohort_id: str
    issue_period: int
    issue_term_periods: int
    remaining_periods: int
    active_policies: int
    guaranteed_rate_per_period: Decimal
    guarantee_liability: Decimal


@dataclass(frozen=True, slots=True)
class LifeCohortFlow:
    cohort_id: str
    renewal_premiums_collected: Decimal
    renewal_liability_allocation: Decimal
    deaths: int
    death_benefits_paid: Decimal


@dataclass(frozen=True, slots=True)
class LifeCohortIssue:
    cohort_id: str
    issue_term_periods: int
    guaranteed_rate_per_period: Decimal
    new_business_policies: int
    new_business_premiums_collected: Decimal
    new_business_liability_allocation: Decimal


_Item = TypeVar("_Item", LifeCohort, LifeCohortFlow, LifeCohortIssue)


@dataclass(frozen=True, slots=True)
class LifeCohortMovement:
    cohort_id: str
    renewal_premiums_collected: Decimal
    renewal_liability_allocation: Decimal
    guarantee_accretion: Decimal
    deaths: int
    death_benefits_paid: Decimal
    death_liability_release: Decimal
    maturities: int
    maturity_benefits_paid: Decimal
    maturity_liability_release: Decimal


@dataclass(frozen=True, slots=True)
class LifeCohortRow:
    period: int
    opening_active_policies: int
    opening_backing_assets: Decimal
    opening_guarantee_liability: Decimal
    opening_equity: Decimal
    opening_cohorts: tuple[LifeCohort, ...]
    cohort_movements: tuple[LifeCohortMovement, ...]
    new_business_cohorts: tuple[LifeCohortIssue, ...]
    renewal_premiums_collected: Decimal
    new_business_premiums_collected: Decimal
    premiums_collected: Decimal
    renewal_liability_allocation: Decimal
    new_business_liability_allocation: Decimal
    premium_liability_allocation: Decimal
    investment_result: Decimal
    guarantee_accretion: Decimal
    deaths: int
    death_benefits_paid: Decimal
    death_liability_release: Decimal
    maturities: int
    maturity_benefits_paid: Decimal
    maturity_liability_release: Decimal
    liability_release: Decimal
    new_business_policies: int
    operating_expense_paid: Decimal
    capital_contribution: Decimal
    capital_distribution: Decimal
    period_profit: Decimal
    closing_active_policies: int
    closing_backing_assets: Decimal
    closing_guarantee_liability: Decimal
    closing_equity: Decimal
    closing_cohorts: tuple[LifeCohort, ...]

    def to_dict(self) -> dict[str, object]:
        return cast(dict[str, object], _json_value(asdict(self)))


@dataclass(frozen=True, slots=True)
class LifeCohortReport:
    insurer_id: int | None
    requested_period_count: int
    rows: tuple[LifeCohortRow, ...]
    issues: tuple[LifeBalanceIssue, ...]

    def to_dict(self) -> dict[str, object]:
        valid = not self.issues
        return {
            "schema_version": LIFE_COHORT_RESULT_VERSION,
            "input_schema_version": LIFE_COHORT_INPUT_VERSION,
            "life_sector_contract_schema_version": LIFE_SECTOR_V3_CONTRACT_VERSION,
            "status": "ok" if valid else "error",
            "valid": valid,
            "insurer_id": self.insurer_id,
            "sector_id": "life",
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


@dataclass(frozen=True, slots=True)
class _Opening:
    active_policies: int
    backing_assets: Decimal
    guarantee_liability: Decimal
    equity: Decimal
    cohorts: tuple[LifeCohort, ...]


@dataclass(frozen=True, slots=True)
class _Period:
    period: int
    cohort_flows: tuple[LifeCohortFlow, ...]
    new_business: tuple[LifeCohortIssue, ...]
    investment_result: Decimal
    operating_expense_paid: Decimal
    capital_contribution: Decimal
    capital_distribution: Decimal


def _json_value(value: object, key: str = "") -> object:
    if isinstance(value, Decimal):
        amount = Decimal(0) if value.is_zero() else value
        return format(amount, ".6f" if key == "guaranteed_rate_per_period" else ".4f")
    if isinstance(value, dict):
        return {name: _json_value(item, name) for name, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_value(item) for item in value]
    return value


def _integer(value: object, path: str, issues: list[LifeBalanceIssue], minimum: int, maximum: int) -> int | None:
    if type(value) is not int or not minimum <= value <= maximum:
        _issue(issues, path, "count_invalid", f"Ganzzahl von {minimum} bis {maximum} erforderlich")
        return None
    return value


def _cohort_id(value: object, path: str, issues: list[LifeBalanceIssue]) -> str | None:
    if type(value) is not str or _COHORT_ID_PATTERN.fullmatch(value) is None:
        _issue(issues, path, "cohort_id_invalid", "ASCII-ID mit Buchstabenbeginn und hoechstens 32 Zeichen erforderlich")
        return None
    return value


def _rate(value: object, path: str, issues: list[LifeBalanceIssue]) -> Decimal | None:
    if type(value) is not str or _RATE_PATTERN.fullmatch(value) is None:
        _issue(issues, path, "rate_invalid", "Garantiesatz von 0 bis 1 mit hoechstens sechs Dezimalstellen erforderlich")
        return None
    return Decimal(value)


def _cohort(value: object, path: str, issues: list[LifeBalanceIssue]) -> LifeCohort | None:
    if type(value) is not dict:
        _issue(issues, path, "object_required", "Kohortenobjekt erforderlich")
        return None
    _exact_fields(value, _COHORT_FIELDS, path, issues)
    cohort_id = _cohort_id(value.get("cohort_id"), f"{path}.cohort_id", issues)
    issue_period = _integer(value.get("issue_period"), f"{path}.issue_period", issues, -99, 0)
    term = _integer(value.get("issue_term_periods"), f"{path}.issue_term_periods", issues, 1, 100)
    remaining = _integer(value.get("remaining_periods"), f"{path}.remaining_periods", issues, 1, 100)
    active = _integer(value.get("active_policies"), f"{path}.active_policies", issues, 1, 1_000_000_000)
    rate = _rate(value.get("guaranteed_rate_per_period"), f"{path}.guaranteed_rate_per_period", issues)
    liability = _amount(value.get("guarantee_liability"), f"{path}.guarantee_liability", issues)
    if term is not None and remaining is not None and issue_period is not None:
        if remaining > term or issue_period != remaining - term:
            _issue(issues, path, "cohort_vintage_invalid", "Ausgabeperiode, Laufzeit und Restlaufzeit widersprechen sich")
    if None in (cohort_id, issue_period, term, remaining, active, rate, liability):
        return None
    return LifeCohort(cohort_id, issue_period, term, remaining, active, rate, liability)


def _flow(value: object, path: str, issues: list[LifeBalanceIssue]) -> LifeCohortFlow | None:
    if type(value) is not dict:
        _issue(issues, path, "object_required", "Kohortenfluss erforderlich")
        return None
    _exact_fields(value, _FLOW_FIELDS, path, issues)
    cohort_id = _cohort_id(value.get("cohort_id"), f"{path}.cohort_id", issues)
    premium = _amount(value.get("renewal_premiums_collected"), f"{path}.renewal_premiums_collected", issues)
    allocation = _amount(value.get("renewal_liability_allocation"), f"{path}.renewal_liability_allocation", issues)
    deaths = _integer(value.get("deaths"), f"{path}.deaths", issues, 0, 1_000_000_000)
    benefit = _amount(value.get("death_benefits_paid"), f"{path}.death_benefits_paid", issues)
    if premium is not None and allocation is not None and allocation > premium:
        _issue(issues, f"{path}.renewal_liability_allocation", "premium_allocation_exceeds_collected", "Zuweisung uebersteigt eingezogene Praemie")
    if deaths == 0 and benefit is not None and benefit > 0:
        _issue(issues, f"{path}.death_benefits_paid", "death_benefit_without_death", "Todesfallleistung ohne Todesfall unzulaessig")
    if None in (cohort_id, premium, allocation, deaths, benefit):
        return None
    return LifeCohortFlow(cohort_id, premium, allocation, deaths, benefit)


def _new_issue(value: object, path: str, issues: list[LifeBalanceIssue]) -> LifeCohortIssue | None:
    if type(value) is not dict:
        _issue(issues, path, "object_required", "Neugeschaeftsobjekt erforderlich")
        return None
    _exact_fields(value, _ISSUE_FIELDS, path, issues)
    cohort_id = _cohort_id(value.get("cohort_id"), f"{path}.cohort_id", issues)
    term = _integer(value.get("issue_term_periods"), f"{path}.issue_term_periods", issues, 1, 100)
    rate = _rate(value.get("guaranteed_rate_per_period"), f"{path}.guaranteed_rate_per_period", issues)
    count = _integer(value.get("new_business_policies"), f"{path}.new_business_policies", issues, 1, 1_000_000_000)
    premium = _amount(value.get("new_business_premiums_collected"), f"{path}.new_business_premiums_collected", issues)
    allocation = _amount(value.get("new_business_liability_allocation"), f"{path}.new_business_liability_allocation", issues)
    if premium is not None and allocation is not None and allocation > premium:
        _issue(issues, f"{path}.new_business_liability_allocation", "premium_allocation_exceeds_collected", "Zuweisung uebersteigt eingezogene Praemie")
    if None in (cohort_id, term, rate, count, premium, allocation):
        return None
    return LifeCohortIssue(cohort_id, term, rate, count, premium, allocation)


def _items(
    value: object, path: str, issues: list[LifeBalanceIssue],
    parser: Callable[[object, str, list[LifeBalanceIssue]], _Item | None],
) -> tuple[_Item, ...]:
    if type(value) is not list or len(value) > 100:
        _issue(issues, path, "cohort_list_invalid", "Liste mit hoechstens 100 Eintraegen erforderlich")
        return ()
    result: list[_Item] = []
    for index, item in enumerate(value):
        parsed = parser(item, f"{path}[{index}]", issues)
        if parsed is not None:
            result.append(parsed)
    ids = [item.cohort_id for item in result]
    if len(ids) != len(set(ids)):
        _issue(issues, path, "cohort_id_duplicate", "Kohorten-ID kommt mehrfach vor")
    return tuple(sorted(result, key=lambda item: item.cohort_id))


def _opening(value: object, issues: list[LifeBalanceIssue]) -> _Opening | None:
    path = "$.opening"
    if type(value) is not dict:
        _issue(issues, path, "object_required", "Anfangsbestand muss ein Objekt sein")
        return None
    _exact_fields(value, frozenset((
        "opening_active_policies", "opening_backing_assets",
        "opening_guarantee_liability", "opening_equity", "cohorts",
    )), path, issues)
    active = _integer(value.get("opening_active_policies"), f"{path}.opening_active_policies", issues, 0, 1_000_000_000)
    assets = _amount(value.get("opening_backing_assets"), f"{path}.opening_backing_assets", issues)
    liability = _amount(value.get("opening_guarantee_liability"), f"{path}.opening_guarantee_liability", issues)
    equity = _amount(value.get("opening_equity"), f"{path}.opening_equity", issues, signed=True)
    cohorts = _items(value.get("cohorts"), f"{path}.cohorts", issues, _cohort)
    if None in (active, assets, liability, equity):
        return None
    with localcontext() as context:
        context.prec = 64
        if assets != liability + equity:
            _issue(issues, path, "opening_identity_invalid", "Vermoegen muss Garantieverpflichtung plus Eigenkapital sein")
        if active != sum(cohort.active_policies for cohort in cohorts):
            _issue(issues, path, "opening_cohort_count_mismatch", "Anfangsstueckzahl stimmt nicht zur Kohortensumme")
        if liability != sum((cohort.guarantee_liability for cohort in cohorts), Decimal(0)):
            _issue(issues, path, "opening_cohort_liability_mismatch", "Anfangsverpflichtung stimmt nicht zur Kohortensumme")
    return _Opening(active, assets, liability, equity, cohorts)


def _periods(value: object, issues: list[LifeBalanceIssue]) -> tuple[_Period, ...]:
    if type(value) is not list or not 1 <= len(value) <= 100:
        _issue(issues, "$.periods", "period_count_invalid", "1 bis 100 Perioden erforderlich")
        return ()
    result = []
    for index, item in enumerate(value):
        path = f"$.periods[{index}]"
        if type(item) is not dict:
            _issue(issues, path, "object_required", "Periodenobjekt erforderlich")
            continue
        _exact_fields(item, _PERIOD_FIELDS, path, issues)
        if type(item.get("period")) is not int or item["period"] != index + 1:
            _issue(issues, f"{path}.period", "period_sequence_invalid", "Perioden muessen bei 1 beginnen und lueckenlos folgen")
        flows = _items(item.get("cohort_flows"), f"{path}.cohort_flows", issues, _flow)
        new = _items(item.get("new_business"), f"{path}.new_business", issues, _new_issue)
        amounts = {}
        for name in ("investment_result", "operating_expense_paid", "capital_contribution", "capital_distribution"):
            amounts[name] = _amount(item.get(name), f"{path}.{name}", issues, signed=name == "investment_result")
        if None in amounts.values():
            continue
        result.append(_Period(index + 1, flows, new, **amounts))
    return tuple(result)


def _calculate(insurer_id: int, opening: _Opening, periods: tuple[_Period, ...]) -> LifeCohortReport:
    rows: list[LifeCohortRow] = []
    cohorts = {cohort.cohort_id: cohort for cohort in opening.cohorts}
    seen_ids = set(cohorts)
    assets, liability, equity = opening.backing_assets, opening.guarantee_liability, opening.equity
    with localcontext() as context:
        context.prec = 64
        for index, period in enumerate(periods):
            path = f"$.periods[{index}]"
            issues: list[LifeBalanceIssue] = []
            flows = {flow.cohort_id: flow for flow in period.cohort_flows}
            if flows.keys() != cohorts.keys():
                _issue(issues, f"{path}.cohort_flows", "cohort_flows_mismatch", "Genau ein Fluss je aktiver Anfangskohorte erforderlich")
            new_ids = {issue.cohort_id for issue in period.new_business}
            if seen_ids & new_ids:
                _issue(issues, f"{path}.new_business", "cohort_id_reused", "Kohorten-ID wurde bereits vergeben")
            if len(seen_ids | new_ids) > 100:
                _issue(issues, f"{path}.new_business", "cohort_limit_exceeded", "Hoechstens 100 Kohorten-IDs je Fall")
            if issues:
                return LifeCohortReport(insurer_id, len(periods), (), tuple(issues))

            opening_cohorts = tuple(cohorts[name] for name in sorted(cohorts))
            closing = {}
            movements = []
            for cohort in opening_cohorts:
                flow = flows[cohort.cohort_id]
                if flow.deaths > cohort.active_policies:
                    _issue(issues, f"{path}.cohort_flows", "deaths_exceed_opening", "Todesfaelle uebersteigen den Kohorten-Anfangsbestand")
                    break
                guarantee = (cohort.guarantee_liability * cohort.guaranteed_rate_per_period).quantize(
                    _QUANTUM, rounding=ROUND_HALF_EVEN
                )
                before_exit = cohort.guarantee_liability + guarantee + flow.renewal_liability_allocation
                death_release = before_exit if flow.deaths == cohort.active_policies else (
                    before_exit * flow.deaths / cohort.active_policies
                ).quantize(_QUANTUM, rounding=ROUND_HALF_EVEN)
                survivors = cohort.active_policies - flow.deaths
                maturities = survivors if cohort.remaining_periods == 1 else 0
                maturity_release = before_exit - death_release if maturities else Decimal(0)
                remaining_liability = before_exit - death_release - maturity_release
                if survivors and not maturities:
                    closing[cohort.cohort_id] = LifeCohort(
                        cohort.cohort_id, cohort.issue_period, cohort.issue_term_periods,
                        cohort.remaining_periods - 1, survivors,
                        cohort.guaranteed_rate_per_period, remaining_liability,
                    )
                movements.append(LifeCohortMovement(
                    cohort.cohort_id, flow.renewal_premiums_collected,
                    flow.renewal_liability_allocation, guarantee, flow.deaths,
                    flow.death_benefits_paid, death_release, maturities,
                    maturity_release, maturity_release,
                ))
            if issues:
                return LifeCohortReport(insurer_id, len(periods), (), tuple(issues))

            for issue in period.new_business:
                closing[issue.cohort_id] = LifeCohort(
                    issue.cohort_id, period.period, issue.issue_term_periods,
                    issue.issue_term_periods, issue.new_business_policies,
                    issue.guaranteed_rate_per_period, issue.new_business_liability_allocation,
                )
            closing_cohorts = tuple(closing[name] for name in sorted(closing))
            renewal_premiums = sum((item.renewal_premiums_collected for item in movements), Decimal(0))
            new_premiums = sum((item.new_business_premiums_collected for item in period.new_business), Decimal(0))
            renewal_allocation = sum((item.renewal_liability_allocation for item in movements), Decimal(0))
            new_allocation = sum((item.new_business_liability_allocation for item in period.new_business), Decimal(0))
            guarantee = sum((item.guarantee_accretion for item in movements), Decimal(0))
            deaths = sum(item.deaths for item in movements)
            death_benefits = sum((item.death_benefits_paid for item in movements), Decimal(0))
            death_release = sum((item.death_liability_release for item in movements), Decimal(0))
            maturities = sum(item.maturities for item in movements)
            maturity_release = sum((item.maturity_liability_release for item in movements), Decimal(0))
            new_policies = sum(item.new_business_policies for item in period.new_business)
            opening_policies = sum(item.active_policies for item in opening_cohorts)
            closing_policies = sum(item.active_policies for item in closing_cohorts)
            closing_liability = sum((item.guarantee_liability for item in closing_cohorts), Decimal(0))
            premiums = renewal_premiums + new_premiums
            allocation = renewal_allocation + new_allocation
            release = death_release + maturity_release
            closing_assets = (
                assets + premiums + period.investment_result + period.capital_contribution
                - death_benefits - maturity_release - period.operating_expense_paid
                - period.capital_distribution
            )
            profit = (
                premiums + period.investment_result - death_benefits - maturity_release
                - period.operating_expense_paid - (closing_liability - liability)
            )
            closing_equity = equity + profit + period.capital_contribution - period.capital_distribution
            if closing_policies > 1_000_000_000:
                _issue(issues, path, "policy_limit_exceeded", "Hoechstens eine Milliarde aktive Policen je Segment")
            if closing_policies != opening_policies - deaths - maturities + new_policies:
                _issue(issues, path, "closing_count_invalid", "Schlussbestand stimmt nicht zur Bewegungsrechnung")
            if closing_liability != liability + guarantee + allocation - release:
                _issue(issues, path, "closing_liability_invalid", "Schlussverpflichtung stimmt nicht zur Kohortenrechnung")
            if closing_assets < 0:
                _issue(issues, path, "negative_closing_assets", "Deckende Vermoegenswerte waeren negativ")
            if closing_assets != closing_liability + closing_equity:
                _issue(issues, path, "closing_identity_invalid", "Schlussbilanz ist nicht ausgeglichen")
            if issues:
                return LifeCohortReport(insurer_id, len(periods), (), tuple(issues))

            rows.append(LifeCohortRow(
                period=period.period,
                opening_active_policies=opening_policies,
                opening_backing_assets=assets,
                opening_guarantee_liability=liability,
                opening_equity=equity,
                opening_cohorts=opening_cohorts,
                cohort_movements=tuple(movements),
                new_business_cohorts=period.new_business,
                renewal_premiums_collected=renewal_premiums,
                new_business_premiums_collected=new_premiums,
                premiums_collected=premiums,
                renewal_liability_allocation=renewal_allocation,
                new_business_liability_allocation=new_allocation,
                premium_liability_allocation=allocation,
                investment_result=period.investment_result,
                guarantee_accretion=guarantee,
                deaths=deaths,
                death_benefits_paid=death_benefits,
                death_liability_release=death_release,
                maturities=maturities,
                maturity_benefits_paid=maturity_release,
                maturity_liability_release=maturity_release,
                liability_release=release,
                new_business_policies=new_policies,
                operating_expense_paid=period.operating_expense_paid,
                capital_contribution=period.capital_contribution,
                capital_distribution=period.capital_distribution,
                period_profit=profit,
                closing_active_policies=closing_policies,
                closing_backing_assets=closing_assets,
                closing_guarantee_liability=closing_liability,
                closing_equity=closing_equity,
                closing_cohorts=closing_cohorts,
            ))
            cohorts = closing
            seen_ids.update(new_ids)
            assets, liability, equity = closing_assets, closing_liability, closing_equity
    return LifeCohortReport(insurer_id, len(periods), tuple(rows), ())


def build_life_cohort_balance(value: object) -> LifeCohortReport:
    """Validate a complete explicit cohort case before returning any row."""

    issues: list[LifeBalanceIssue] = []
    if type(value) is not dict:
        _issue(issues, "$", "object_required", "Lebensfall-Eingang muss ein Objekt sein")
        return LifeCohortReport(None, 0, (), tuple(issues))
    _exact_fields(value, _DOCUMENT_FIELDS, "$", issues)
    for name, expected in (
        ("schema_version", LIFE_COHORT_INPUT_VERSION),
        ("life_sector_contract_schema_version", LIFE_SECTOR_V3_CONTRACT_VERSION),
        ("sector_taxonomy_schema_version", SECTOR_TAXONOMY_VERSION),
        ("source_kind", "explicit_scenario"),
        ("historical_mapping_status", "unresolved"),
        ("sector_id", "life"),
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
        return LifeCohortReport(insurer_id, requested_count, (), tuple(issues))
    assert insurer_id is not None and opening is not None
    return _calculate(insurer_id, opening, periods)
