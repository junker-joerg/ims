"""Resolve versioned life investment and mortality sources without running a case."""

from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import asdict, dataclass
from decimal import Decimal, ROUND_HALF_EVEN, ROUND_HALF_UP, localcontext

from ims.accounting.life_closed_cohort_balance import _QUANTUM, _amount, _exact_fields, _issue
from ims.accounting.life_cohort_balance import _cohort_id, _integer, _rate
from ims.accounting.life_model_balance import LifeBalanceIssue
from ims.model.life_sector_v3_contract import LIFE_SECTOR_V3_CONTRACT_VERSION
from ims.model.sector_taxonomy import SECTOR_TAXONOMY_VERSION
from ims.model.vdefmd6_population import VDEFMD6_INSURER_COUNT


LIFE_ASSUMPTIONS_INPUT_VERSION = "ims.life-assumptions-input.v1"
LIFE_ASSUMPTIONS_RESULT_VERSION = "ims.life-assumptions-result.v1"
_SIGNED_RATE_PATTERN = re.compile(r"-?(?:0(?:\.[0-9]{1,6})?|1(?:\.0{1,6})?)\Z")
_PLAN_FIELDS = frozenset((
    "schema_version", "life_sector_contract_schema_version",
    "sector_taxonomy_schema_version", "source_kind", "historical_mapping_status",
    "insurer_id", "sector_id", "period_count", "investment", "mortality",
))
_BASIS_FIELDS = frozenset(("insurer_id", "period", "opening_backing_assets", "opening_policies"))
_POLICY_FIELDS = frozenset(("policy_id", "cohort_id"))
_WINDOW_FIELDS = frozenset(("start_period", "end_period", "rate_per_period"))
_INVESTMENT_MODES = frozenset(("explicit_scenario", "insurer_rule_on_opening_backing_assets"))
_MORTALITY_MODES = frozenset(("explicit_death_policy_ids", "exogenous_deterministic_rate_curve"))


@dataclass(frozen=True, slots=True)
class _Source:
    mode: str
    values: dict[int, object]


@dataclass(frozen=True, slots=True)
class _Plan:
    insurer_id: int
    period_count: int
    investment: _Source
    mortality: _Source


@dataclass(frozen=True, slots=True)
class _Basis:
    insurer_id: int
    period: int
    assets: Decimal
    policies: tuple[tuple[str, str], ...]


@dataclass(frozen=True, slots=True)
class LifeAssumptionResolution:
    insurer_id: int | None
    period: int | None
    investment_mode: str | None
    mortality_mode: str | None
    opening_backing_assets: Decimal | None
    opening_active_policies: int | None
    investment_rate: Decimal | None
    mortality_rate: Decimal | None
    investment_result: Decimal | None
    death_policy_ids: tuple[str, ...]
    deaths_by_cohort: tuple[tuple[str, int], ...]
    issues: tuple[LifeBalanceIssue, ...]

    def to_dict(self) -> dict[str, object]:
        valid = not self.issues
        return {
            "schema_version": LIFE_ASSUMPTIONS_RESULT_VERSION,
            "input_schema_version": LIFE_ASSUMPTIONS_INPUT_VERSION,
            "life_sector_contract_schema_version": LIFE_SECTOR_V3_CONTRACT_VERSION,
            "status": "ok" if valid else "error",
            "valid": valid,
            "insurer_id": self.insurer_id,
            "sector_id": "life",
            "source_kind": "versioned_assumption_plan",
            "historical_mapping_status": "unresolved",
            "period": self.period,
            "investment_mode": self.investment_mode,
            "mortality_mode": self.mortality_mode,
            "opening_backing_assets": _money(self.opening_backing_assets) if valid else None,
            "opening_active_policies": self.opening_active_policies if valid else None,
            "investment_rate_per_period": _rate_text(self.investment_rate) if valid else None,
            "mortality_rate_per_period": _rate_text(self.mortality_rate) if valid else None,
            "investment_result": _money(self.investment_result) if valid else None,
            "death_policy_ids": list(self.death_policy_ids) if valid else [],
            "death_count": len(self.death_policy_ids) if valid else None,
            "deaths_by_cohort": [
                {"cohort_id": cohort_id, "deaths": count}
                for cohort_id, count in self.deaths_by_cohort
            ] if valid else [],
            "issue_count": len(self.issues),
            "issues": [asdict(issue) for issue in self.issues],
            "writes_performed": False,
            "runner_invoked": False,
            "simulation_performed": False,
            "statutory_or_solvency_ii_claim": False,
            "historical_full_equality_claim": False,
        }


def _money(value: Decimal | None) -> str | None:
    if value is None:
        return None
    return format(Decimal(0) if value.is_zero() else value, ".4f")


def _rate_text(value: Decimal | None) -> str | None:
    if value is None:
        return None
    return format(Decimal(0) if value.is_zero() else value, ".6f")


def _signed_rate(value: object, path: str, issues: list[LifeBalanceIssue]) -> Decimal | None:
    if type(value) is not str or _SIGNED_RATE_PATTERN.fullmatch(value) is None:
        _issue(issues, path, "investment_rate_invalid", "Signierter Satz von -1 bis 1 mit hoechstens sechs Dezimalstellen erforderlich")
        return None
    return Decimal(value)


def _death_ids(value: object, path: str, issues: list[LifeBalanceIssue]) -> tuple[str, ...] | None:
    if type(value) is not list or len(value) > 100:
        _issue(issues, path, "death_list_invalid", "Liste mit hoechstens 100 Policen-IDs erforderlich")
        return None
    ids = [_cohort_id(item, f"{path}[{index}]", issues) for index, item in enumerate(value)]
    valid = [item for item in ids if item is not None]
    if len(valid) != len(set(valid)):
        _issue(issues, path, "death_id_duplicate", "Todesfall-ID kommt mehrfach vor")
    return tuple(sorted(valid)) if len(valid) == len(ids) else None


def _explicit_series(
    value: object, path: str, period_count: int, field: str,
    parser: Callable[[object, str, list[LifeBalanceIssue]], object],
    issues: list[LifeBalanceIssue],
) -> dict[int, object]:
    if type(value) is not list or len(value) != period_count:
        _issue(issues, path, "period_coverage_invalid", "Genau ein expliziter Wert je Periode erforderlich")
        return {}
    result: dict[int, object] = {}
    for index, item in enumerate(value):
        item_path = f"{path}[{index}]"
        if type(item) is not dict:
            _issue(issues, item_path, "object_required", "Periodenwert muss ein Objekt sein")
            continue
        _exact_fields(item, frozenset(("period", field)), item_path, issues)
        period = _integer(item.get("period"), f"{item_path}.period", issues, 1, period_count)
        parsed = parser(item.get(field), f"{item_path}.{field}", issues)
        if period is None or parsed is None:
            continue
        if period in result:
            _issue(issues, f"{item_path}.period", "period_duplicate", "Periode kommt mehrfach vor")
        result[period] = parsed
    if set(result) != set(range(1, period_count + 1)):
        _issue(issues, path, "period_coverage_invalid", "Explizite Werte muessen alle Perioden abdecken")
    return result


def _windows(
    value: object, path: str, period_count: int,
    parser: Callable[[object, str, list[LifeBalanceIssue]], Decimal | None],
    issues: list[LifeBalanceIssue],
) -> dict[int, object]:
    if type(value) is not list or not 1 <= len(value) <= 100:
        _issue(issues, path, "window_list_invalid", "1 bis 100 Periodenfenster erforderlich")
        return {}
    parsed: list[tuple[int, int, Decimal]] = []
    for index, item in enumerate(value):
        item_path = f"{path}[{index}]"
        if type(item) is not dict:
            _issue(issues, item_path, "object_required", "Periodenfenster muss ein Objekt sein")
            continue
        _exact_fields(item, _WINDOW_FIELDS, item_path, issues)
        start = _integer(item.get("start_period"), f"{item_path}.start_period", issues, 1, period_count)
        end = _integer(item.get("end_period"), f"{item_path}.end_period", issues, 1, period_count)
        rate = parser(item.get("rate_per_period"), f"{item_path}.rate_per_period", issues)
        if None in (start, end, rate):
            continue
        if end < start:
            _issue(issues, item_path, "window_reversed", "Fensterende liegt vor dem Anfang")
            continue
        parsed.append((start, end, rate))
    result: dict[int, object] = {}
    expected = 1
    for start, end, rate in sorted(parsed):
        if start != expected:
            _issue(issues, path, "window_coverage_invalid", "Fenster muessen lueckenlos und ueberlappungsfrei sein")
        for period in range(start, end + 1):
            result[period] = rate
        expected = end + 1
    if expected != period_count + 1 or set(result) != set(range(1, period_count + 1)):
        _issue(issues, path, "window_coverage_invalid", "Fenster muessen genau den Horizont abdecken")
    return result


def _source(
    value: object, path: str, period_count: int, modes: frozenset[str],
    explicit_mode: str, explicit_field: str,
    explicit_parser: Callable[[object, str, list[LifeBalanceIssue]], object],
    curve_parser: Callable[[object, str, list[LifeBalanceIssue]], Decimal | None],
    issues: list[LifeBalanceIssue],
) -> _Source | None:
    if type(value) is not dict:
        _issue(issues, path, "object_required", "Quellenobjekt erforderlich")
        return None
    mode = value.get("mode")
    if type(mode) is not str or mode not in modes:
        _issue(issues, f"{path}.mode", "source_mode_invalid", "Bekannter exklusiver Quellenmodus erforderlich")
        return None
    field = "periods" if mode == explicit_mode else "windows"
    _exact_fields(value, frozenset(("mode", field)), path, issues)
    if mode == explicit_mode:
        values = _explicit_series(value.get(field), f"{path}.{field}", period_count, explicit_field, explicit_parser, issues)
    else:
        values = _windows(value.get(field), f"{path}.{field}", period_count, curve_parser, issues)
    return _Source(mode, values)


def _plan(value: object, issues: list[LifeBalanceIssue]) -> _Plan | None:
    if type(value) is not dict:
        _issue(issues, "$", "object_required", "Annahmeplan muss ein Objekt sein")
        return None
    _exact_fields(value, _PLAN_FIELDS, "$", issues)
    for field, expected in (
        ("schema_version", LIFE_ASSUMPTIONS_INPUT_VERSION),
        ("life_sector_contract_schema_version", LIFE_SECTOR_V3_CONTRACT_VERSION),
        ("sector_taxonomy_schema_version", SECTOR_TAXONOMY_VERSION),
        ("source_kind", "versioned_assumption_plan"),
        ("historical_mapping_status", "unresolved"),
        ("sector_id", "life"),
    ):
        if value.get(field) != expected:
            _issue(issues, f"$.{field}", "contract_value_mismatch", f"{field} muss {expected!r} sein")
    insurer = _integer(value.get("insurer_id"), "$.insurer_id", issues, 1, VDEFMD6_INSURER_COUNT)
    count = _integer(value.get("period_count"), "$.period_count", issues, 1, 100)
    if count is None:
        return None
    investment = _source(
        value.get("investment"), "$.investment", count, _INVESTMENT_MODES,
        "explicit_scenario", "investment_result",
        lambda raw, path, found: _amount(raw, path, found, signed=True),
        _signed_rate, issues,
    )
    mortality = _source(
        value.get("mortality"), "$.mortality", count, _MORTALITY_MODES,
        "explicit_death_policy_ids", "death_policy_ids", _death_ids, _rate, issues,
    )
    if None in (insurer, investment, mortality):
        return None
    return _Plan(insurer, count, investment, mortality)


def _basis(value: object, issues: list[LifeBalanceIssue]) -> _Basis | None:
    path = "$.opening"
    if type(value) is not dict:
        _issue(issues, path, "object_required", "Anfangsbestand muss ein Objekt sein")
        return None
    _exact_fields(value, _BASIS_FIELDS, path, issues)
    insurer = _integer(value.get("insurer_id"), f"{path}.insurer_id", issues, 1, VDEFMD6_INSURER_COUNT)
    period = _integer(value.get("period"), f"{path}.period", issues, 1, 100)
    assets = _amount(value.get("opening_backing_assets"), f"{path}.opening_backing_assets", issues)
    raw_policies = value.get("opening_policies")
    if type(raw_policies) is not list or len(raw_policies) > 100:
        _issue(issues, f"{path}.opening_policies", "policy_list_invalid", "Hoechstens 100 vollstaendig gelistete Anfangspolicen erforderlich")
        return None
    policies: list[tuple[str, str]] = []
    for index, item in enumerate(raw_policies):
        item_path = f"{path}.opening_policies[{index}]"
        if type(item) is not dict:
            _issue(issues, item_path, "object_required", "Policenreferenz muss ein Objekt sein")
            continue
        _exact_fields(item, _POLICY_FIELDS, item_path, issues)
        policy_id = _cohort_id(item.get("policy_id"), f"{item_path}.policy_id", issues)
        cohort_id = _cohort_id(item.get("cohort_id"), f"{item_path}.cohort_id", issues)
        if policy_id is not None and cohort_id is not None:
            policies.append((policy_id, cohort_id))
    ids = [policy_id for policy_id, _ in policies]
    if len(ids) != len(set(ids)):
        _issue(issues, f"{path}.opening_policies", "policy_id_duplicate", "Policen-ID kommt mehrfach vor")
    if insurer is None or period is None or assets is None:
        return None
    return _Basis(insurer, period, assets, tuple(sorted(policies)))


def resolve_life_period_assumptions(plan_value: object, opening_value: object) -> LifeAssumptionResolution:
    """Resolve one period's sources atomically, without balance or runner effects."""

    issues: list[LifeBalanceIssue] = []
    plan = _plan(plan_value, issues)
    opening = _basis(opening_value, issues)
    if plan is not None and opening is not None and opening.insurer_id != plan.insurer_id:
        _issue(issues, "$.opening.insurer_id", "insurer_id_mismatch", "Anfangsbestand und Annahmeplan haben verschiedene VU-IDs")
    if plan is not None and opening is not None and opening.period > plan.period_count:
        _issue(issues, "$.opening.period", "period_outside_plan", "Periode liegt ausserhalb des Annahmeplans")
    insurer = plan.insurer_id if plan is not None else None
    period = opening.period if opening is not None else None
    investment_mode = plan.investment.mode if plan is not None else None
    mortality_mode = plan.mortality.mode if plan is not None else None
    if issues or plan is None or opening is None:
        return LifeAssumptionResolution(
            insurer, period, investment_mode, mortality_mode,
            None, None, None, None, None, (), (), tuple(issues),
        )

    investment_value = plan.investment.values[opening.period]
    mortality_value = plan.mortality.values[opening.period]
    investment_rate = None
    mortality_rate = None
    with localcontext() as context:
        context.prec = 64
        if investment_mode == "explicit_scenario":
            investment_result = investment_value
        else:
            investment_rate = investment_value
            investment_result = (opening.assets * investment_rate).quantize(_QUANTUM, rounding=ROUND_HALF_EVEN)
        cohorts: dict[str, list[str]] = {}
        for policy_id, cohort_id in opening.policies:
            cohorts.setdefault(cohort_id, []).append(policy_id)
        if mortality_mode == "explicit_death_policy_ids":
            death_ids = mortality_value
            unknown = set(death_ids) - {policy_id for policy_id, _ in opening.policies}
            if unknown:
                _issue(issues, "$.mortality.periods", "death_policy_not_active", "Todesfall-ID ist nicht im aktiven Anfangsbestand")
        else:
            mortality_rate = mortality_value
            death_ids = tuple(sorted(
                policy_id
                for cohort_id in sorted(cohorts)
                for policy_id in cohorts[cohort_id][:
                    int((Decimal(len(cohorts[cohort_id])) * mortality_rate).quantize(Decimal(1), rounding=ROUND_HALF_UP))
                ]
            ))
    if issues:
        return LifeAssumptionResolution(
            insurer, period, investment_mode, mortality_mode,
            None, None, None, None, None, (), (), tuple(issues),
        )
    death_set = set(death_ids)
    counts = tuple((cohort_id, sum(policy_id in death_set for policy_id in ids)) for cohort_id, ids in sorted(cohorts.items()))
    return LifeAssumptionResolution(
        insurer, period, investment_mode, mortality_mode,
        opening.assets, len(opening.policies), investment_rate, mortality_rate,
        investment_result, tuple(sorted(death_ids)), counts, (),
    )
