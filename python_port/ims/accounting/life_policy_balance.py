"""Fully enumerated small life cases with explicit policy maturity payments."""

from __future__ import annotations

import copy
from dataclasses import asdict, dataclass
from decimal import Decimal, localcontext

from ims.accounting.life_cohort_balance import (
    LifeCohort, LifeCohortFlow, LifeCohortIssue, LifeCohortMovement,
    _Opening, _Period, _amount, _calculate, _cohort_id,
    _exact_fields, _integer, _issue, _json_value, _new_issue,
    _opening as cohort_opening, _rate,
)
from ims.accounting.life_model_balance import LifeBalanceIssue
from ims.model.life_sector_v3_contract import LIFE_SECTOR_V3_CONTRACT_VERSION
from ims.model.sector_taxonomy import SECTOR_TAXONOMY_VERSION
from ims.model.vdefmd6_population import VDEFMD6_INSURER_COUNT


LIFE_POLICY_INPUT_VERSION = "ims.life-policy-balance-input.v1"
LIFE_POLICY_RESULT_VERSION = "ims.life-policy-balance-result.v1"
_DOCUMENT_FIELDS = frozenset((
    "schema_version", "life_sector_contract_schema_version",
    "sector_taxonomy_schema_version", "source_kind", "historical_mapping_status",
    "insurer_id", "sector_id", "mode", "opening", "periods",
))
_POLICY_FIELDS = frozenset((
    "policy_id", "cohort_id", "issue_term_periods", "remaining_periods",
    "guaranteed_rate_per_period", "guarantee_liability",
))
_FLOW_FIELDS = frozenset((
    "policy_id", "renewal_premiums_collected", "renewal_liability_allocation",
    "death", "death_benefits_paid", "maturity_benefits_paid",
))
_NEW_POLICY_FIELDS = frozenset((
    "policy_id", "new_business_premiums_collected",
    "new_business_liability_allocation",
))
_ISSUE_FIELDS = frozenset((
    "cohort_id", "issue_term_periods", "guaranteed_rate_per_period",
    "new_business_policies", "new_business_premiums_collected",
    "new_business_liability_allocation", "policies",
))
_PERIOD_FIELDS = frozenset((
    "period", "policy_flows", "new_business", "investment_result",
    "operating_expense_paid", "capital_contribution", "capital_distribution",
))


@dataclass(frozen=True, slots=True)
class _PolicyMeta:
    cohort_id: str
    issue_period: int
    issue_term_periods: int
    guaranteed_rate_per_period: Decimal


@dataclass(frozen=True, slots=True)
class LifePolicyReport:
    insurer_id: int | None
    requested_period_count: int
    rows: tuple[dict[str, object], ...]
    issues: tuple[LifeBalanceIssue, ...]

    def to_dict(self) -> dict[str, object]:
        valid = not self.issues
        return {
            "schema_version": LIFE_POLICY_RESULT_VERSION,
            "input_schema_version": LIFE_POLICY_INPUT_VERSION,
            "life_sector_contract_schema_version": LIFE_SECTOR_V3_CONTRACT_VERSION,
            "mode": "fully_enumerated_policies",
            "status": "ok" if valid else "error",
            "valid": valid,
            "insurer_id": self.insurer_id,
            "sector_id": "life",
            "source_kind": "explicit_scenario",
            "historical_mapping_status": "unresolved",
            "requested_period_count": self.requested_period_count,
            "calculated_period_count": len(self.rows) if valid else 0,
            "rows": [copy.deepcopy(row) for row in self.rows] if valid else [],
            "issue_count": len(self.issues),
            "issues": [asdict(issue) for issue in self.issues],
            "writes_performed": False,
            "runner_invoked": False,
            "simulation_performed": False,
            "statutory_or_solvency_ii_claim": False,
            "historical_full_equality_claim": False,
        }


def _list(value: object, path: str, issues: list[LifeBalanceIssue], *, nonempty: bool = False) -> list:
    if type(value) is not list or len(value) > 100 or (nonempty and not value):
        _issue(issues, path, "policy_list_invalid", "Vollstaendige Liste mit hoechstens 100 Policen erforderlich")
        return []
    return value


def _opening_policy(
    value: object, path: str, cohorts: dict[str, LifeCohort],
    issues: list[LifeBalanceIssue],
) -> tuple[str, LifeCohort, _PolicyMeta] | None:
    if type(value) is not dict:
        _issue(issues, path, "object_required", "Policenobjekt erforderlich")
        return None
    _exact_fields(value, _POLICY_FIELDS, path, issues)
    policy_id = _cohort_id(value.get("policy_id"), f"{path}.policy_id", issues)
    cohort_id = _cohort_id(value.get("cohort_id"), f"{path}.cohort_id", issues)
    term = _integer(value.get("issue_term_periods"), f"{path}.issue_term_periods", issues, 1, 100)
    remaining = _integer(value.get("remaining_periods"), f"{path}.remaining_periods", issues, 1, 100)
    rate = _rate(value.get("guaranteed_rate_per_period"), f"{path}.guaranteed_rate_per_period", issues)
    liability = _amount(value.get("guarantee_liability"), f"{path}.guarantee_liability", issues)
    parent = cohorts.get(cohort_id) if cohort_id is not None else None
    if cohort_id is not None and parent is None:
        _issue(issues, f"{path}.cohort_id", "unknown_cohort_id", "Police verweist auf keine Anfangskohorte")
    if parent is not None and None not in (term, remaining, rate):
        if (term, remaining, rate) != (
            parent.issue_term_periods, parent.remaining_periods,
            parent.guaranteed_rate_per_period,
        ):
            _issue(issues, path, "policy_issue_terms_mismatch", "Policen-Laufzeit oder Garantiesatz widerspricht der Kohorte")
    if None in (policy_id, cohort_id, term, remaining, rate, liability) or parent is None:
        return None
    state = LifeCohort(
        policy_id, parent.issue_period, term, remaining, 1, rate, liability,
    )
    return policy_id, state, _PolicyMeta(cohort_id, parent.issue_period, term, rate)


def _opening(value: object, issues: list[LifeBalanceIssue]) -> tuple[_Opening | None, dict[str, _PolicyMeta], set[str]]:
    path = "$.opening"
    if type(value) is not dict:
        _issue(issues, path, "object_required", "Anfangsbestand muss ein Objekt sein")
        return None, {}, set()
    _exact_fields(value, frozenset((
        "opening_active_policies", "opening_backing_assets",
        "opening_guarantee_liability", "opening_equity", "cohorts", "policies",
    )), path, issues)
    base = {key: value.get(key) for key in (
        "opening_active_policies", "opening_backing_assets",
        "opening_guarantee_liability", "opening_equity", "cohorts",
    )}
    aggregate = cohort_opening(base, issues)
    parents = {cohort.cohort_id: cohort for cohort in aggregate.cohorts} if aggregate is not None else {}
    policies: dict[str, LifeCohort] = {}
    metadata: dict[str, _PolicyMeta] = {}
    for index, item in enumerate(_list(value.get("policies"), f"{path}.policies", issues)):
        parsed = _opening_policy(item, f"{path}.policies[{index}]", parents, issues)
        if parsed is None:
            continue
        policy_id, state, meta = parsed
        if policy_id in policies:
            _issue(issues, f"{path}.policies[{index}].policy_id", "policy_id_duplicate", "Policen-ID kommt mehrfach vor")
        policies[policy_id] = state
        metadata[policy_id] = meta
    if aggregate is None:
        return None, metadata, set(parents)
    if len(policies) != aggregate.active_policies:
        _issue(issues, f"{path}.policies", "policy_count_mismatch", "Policenzahl stimmt nicht zum Anfangsbestand")
    with localcontext() as context:
        context.prec = 64
        for parent in aggregate.cohorts:
            members = [policy for policy_id, policy in policies.items() if metadata[policy_id].cohort_id == parent.cohort_id]
            if len(members) != parent.active_policies:
                _issue(issues, f"{path}.policies", "cohort_policy_count_mismatch", "Policenzahl stimmt nicht zur Kohorte")
            if sum((member.guarantee_liability for member in members), Decimal(0)) != parent.guarantee_liability:
                _issue(issues, f"{path}.policies", "cohort_policy_liability_mismatch", "Policenbuchwerte stimmen nicht zur Kohorte")
    pseudo = _Opening(
        aggregate.active_policies, aggregate.backing_assets,
        aggregate.guarantee_liability, aggregate.equity,
        tuple(policies[name] for name in sorted(policies)),
    )
    return pseudo, metadata, set(parents)


def _policy_flow(value: object, path: str, issues: list[LifeBalanceIssue]) -> tuple[LifeCohortFlow, Decimal] | None:
    if type(value) is not dict:
        _issue(issues, path, "object_required", "Policenfluss erforderlich")
        return None
    _exact_fields(value, _FLOW_FIELDS, path, issues)
    policy_id = _cohort_id(value.get("policy_id"), f"{path}.policy_id", issues)
    premium = _amount(value.get("renewal_premiums_collected"), f"{path}.renewal_premiums_collected", issues)
    allocation = _amount(value.get("renewal_liability_allocation"), f"{path}.renewal_liability_allocation", issues)
    death = value.get("death")
    if type(death) is not bool:
        _issue(issues, f"{path}.death", "death_flag_invalid", "Explizites boolesches Todesfallkennzeichen erforderlich")
    death_benefit = _amount(value.get("death_benefits_paid"), f"{path}.death_benefits_paid", issues)
    maturity_benefit = _amount(value.get("maturity_benefits_paid"), f"{path}.maturity_benefits_paid", issues)
    if premium is not None and allocation is not None and allocation > premium:
        _issue(issues, f"{path}.renewal_liability_allocation", "premium_allocation_exceeds_collected", "Zuweisung uebersteigt eingezogene Praemie")
    if death is False and death_benefit is not None and death_benefit > 0:
        _issue(issues, f"{path}.death_benefits_paid", "death_benefit_without_death", "Todesfallleistung ohne Tod unzulaessig")
    if None in (policy_id, premium, allocation, death_benefit, maturity_benefit) or type(death) is not bool:
        return None
    return LifeCohortFlow(policy_id, premium, allocation, int(death), death_benefit), maturity_benefit


def _new_policy(value: object, path: str, issues: list[LifeBalanceIssue]) -> tuple[str, Decimal, Decimal] | None:
    if type(value) is not dict:
        _issue(issues, path, "object_required", "Neupolice erforderlich")
        return None
    _exact_fields(value, _NEW_POLICY_FIELDS, path, issues)
    policy_id = _cohort_id(value.get("policy_id"), f"{path}.policy_id", issues)
    premium = _amount(value.get("new_business_premiums_collected"), f"{path}.new_business_premiums_collected", issues)
    allocation = _amount(value.get("new_business_liability_allocation"), f"{path}.new_business_liability_allocation", issues)
    if premium is not None and allocation is not None and allocation > premium:
        _issue(issues, f"{path}.new_business_liability_allocation", "premium_allocation_exceeds_collected", "Zuweisung uebersteigt eingezogene Praemie")
    if None in (policy_id, premium, allocation):
        return None
    return policy_id, premium, allocation


def _new_bundle(
    value: object, path: str, period: int,
    metadata: dict[str, _PolicyMeta], cohort_ids: set[str],
    issues: list[LifeBalanceIssue],
) -> tuple[LifeCohortIssue | None, tuple[LifeCohortIssue, ...]]:
    if type(value) is not dict:
        _issue(issues, path, "object_required", "Neugeschaefts-Kohorte erforderlich")
        return None, ()
    _exact_fields(value, _ISSUE_FIELDS, path, issues)
    core = _new_issue({key: value.get(key) for key in _ISSUE_FIELDS if key != "policies"}, path, issues)
    if core is not None:
        if core.cohort_id in cohort_ids:
            _issue(issues, f"{path}.cohort_id", "cohort_id_reused", "Kohorten-ID wurde bereits vergeben")
        cohort_ids.add(core.cohort_id)
    new: list[LifeCohortIssue] = []
    entries = _list(value.get("policies"), f"{path}.policies", issues, nonempty=True)
    for index, item in enumerate(entries):
        parsed = _new_policy(item, f"{path}.policies[{index}]", issues)
        if parsed is None or core is None:
            continue
        policy_id, premium, allocation = parsed
        if policy_id in metadata:
            _issue(issues, f"{path}.policies[{index}].policy_id", "policy_id_reused", "Policen-ID wurde bereits vergeben")
        metadata[policy_id] = _PolicyMeta(
            core.cohort_id, period, core.issue_term_periods,
            core.guaranteed_rate_per_period,
        )
        new.append(LifeCohortIssue(
            policy_id, core.issue_term_periods, core.guaranteed_rate_per_period,
            1, premium, allocation,
        ))
    if core is not None:
        if len(new) != core.new_business_policies:
            _issue(issues, f"{path}.policies", "new_policy_count_mismatch", "Anzahl neuer Policen stimmt nicht zur Kohorte")
        with localcontext() as context:
            context.prec = 64
            if sum((item.new_business_premiums_collected for item in new), Decimal(0)) != core.new_business_premiums_collected:
                _issue(issues, f"{path}.policies", "new_policy_premium_mismatch", "Policenpraemien stimmen nicht zur Kohorte")
            if sum((item.new_business_liability_allocation for item in new), Decimal(0)) != core.new_business_liability_allocation:
                _issue(issues, f"{path}.policies", "new_policy_allocation_mismatch", "Policenzuweisungen stimmen nicht zur Kohorte")
    return core, tuple(sorted(new, key=lambda item: item.cohort_id))


def _periods(
    value: object, metadata: dict[str, _PolicyMeta], cohort_ids: set[str],
    issues: list[LifeBalanceIssue],
) -> tuple[tuple[_Period, ...], dict[tuple[int, str], Decimal], dict[int, tuple[LifeCohortIssue, ...]]]:
    if type(value) is not list or not 1 <= len(value) <= 100:
        _issue(issues, "$.periods", "period_count_invalid", "1 bis 100 Perioden erforderlich")
        return (), {}, {}
    periods: list[_Period] = []
    benefits: dict[tuple[int, str], Decimal] = {}
    bundles: dict[int, tuple[LifeCohortIssue, ...]] = {}
    for index, item in enumerate(value):
        path = f"$.periods[{index}]"
        if type(item) is not dict:
            _issue(issues, path, "object_required", "Periodenobjekt erforderlich")
            continue
        _exact_fields(item, _PERIOD_FIELDS, path, issues)
        if type(item.get("period")) is not int or item["period"] != index + 1:
            _issue(issues, f"{path}.period", "period_sequence_invalid", "Perioden muessen bei 1 beginnen und lueckenlos folgen")
        flows: list[LifeCohortFlow] = []
        for flow_index, raw in enumerate(_list(item.get("policy_flows"), f"{path}.policy_flows", issues)):
            parsed = _policy_flow(raw, f"{path}.policy_flows[{flow_index}]", issues)
            if parsed is None:
                continue
            flow, paid = parsed
            key = (index + 1, flow.cohort_id)
            if key in benefits:
                _issue(issues, f"{path}.policy_flows[{flow_index}].policy_id", "policy_flow_duplicate", "Policenfluss kommt mehrfach vor")
            flows.append(flow)
            benefits[key] = paid
        new: list[LifeCohortIssue] = []
        cohort_bundles: list[LifeCohortIssue] = []
        for issue_index, raw in enumerate(_list(item.get("new_business"), f"{path}.new_business", issues)):
            core, policies = _new_bundle(
                raw, f"{path}.new_business[{issue_index}]", index + 1,
                metadata, cohort_ids, issues,
            )
            if core is not None:
                cohort_bundles.append(core)
            new.extend(policies)
        if len(new) > 100:
            _issue(issues, f"{path}.new_business", "policy_limit_exceeded", "Hoechstens 100 neue Policen je Periode")
        amounts = {}
        for name in ("investment_result", "operating_expense_paid", "capital_contribution", "capital_distribution"):
            amounts[name] = _amount(item.get(name), f"{path}.{name}", issues, signed=name == "investment_result")
        if None in amounts.values():
            continue
        periods.append(_Period(
            index + 1, tuple(sorted(flows, key=lambda flow: flow.cohort_id)),
            tuple(sorted(new, key=lambda issue: issue.cohort_id)), **amounts,
        ))
        bundles[index + 1] = tuple(sorted(cohort_bundles, key=lambda issue: issue.cohort_id))
    return tuple(periods), benefits, bundles


def _policy_snapshot(state: LifeCohort, metadata: dict[str, _PolicyMeta]) -> dict[str, object]:
    result = _json_value(asdict(state))
    result["policy_id"] = result.pop("cohort_id")
    result["cohort_id"] = metadata[state.cohort_id].cohort_id
    return result


def _cohort_snapshots(
    states: tuple[LifeCohort, ...], metadata: dict[str, _PolicyMeta],
) -> list[dict[str, object]]:
    groups: dict[str, list[LifeCohort]] = {}
    for state in states:
        groups.setdefault(metadata[state.cohort_id].cohort_id, []).append(state)
    result = []
    for cohort_id in sorted(groups):
        members = groups[cohort_id]
        first = members[0]
        with localcontext() as context:
            context.prec = 64
            aggregate = LifeCohort(
                cohort_id, first.issue_period, first.issue_term_periods,
                first.remaining_periods, len(members),
                first.guaranteed_rate_per_period,
                sum((item.guarantee_liability for item in members), Decimal(0)),
            )
        result.append(_json_value(asdict(aggregate)))
    return result


def _policy_movement(movement: LifeCohortMovement, metadata: dict[str, _PolicyMeta]) -> dict[str, object]:
    result = _json_value(asdict(movement))
    result["policy_id"] = result.pop("cohort_id")
    result["cohort_id"] = metadata[movement.cohort_id].cohort_id
    return result


def _cohort_movements(
    movements: tuple[LifeCohortMovement, ...], metadata: dict[str, _PolicyMeta],
) -> list[dict[str, object]]:
    groups: dict[str, list[LifeCohortMovement]] = {}
    for movement in movements:
        groups.setdefault(metadata[movement.cohort_id].cohort_id, []).append(movement)
    result = []
    for cohort_id in sorted(groups):
        items = groups[cohort_id]
        with localcontext() as context:
            context.prec = 64
            aggregate = LifeCohortMovement(
                cohort_id,
                sum((item.renewal_premiums_collected for item in items), Decimal(0)),
                sum((item.renewal_liability_allocation for item in items), Decimal(0)),
                sum((item.guarantee_accretion for item in items), Decimal(0)),
                sum(item.deaths for item in items),
                sum((item.death_benefits_paid for item in items), Decimal(0)),
                sum((item.death_liability_release for item in items), Decimal(0)),
                sum(item.maturities for item in items),
                sum((item.maturity_benefits_paid for item in items), Decimal(0)),
                sum((item.maturity_liability_release for item in items), Decimal(0)),
            )
        result.append(_json_value(asdict(aggregate)))
    return result


def _rows(
    engine_rows: tuple, metadata: dict[str, _PolicyMeta],
    bundles: dict[int, tuple[LifeCohortIssue, ...]],
) -> tuple[dict[str, object], ...]:
    rows = []
    for row in engine_rows:
        result = row.to_dict()
        result["opening_policies"] = [
            _policy_snapshot(item, metadata) for item in row.opening_cohorts
        ]
        result["closing_policies"] = [
            _policy_snapshot(item, metadata) for item in row.closing_cohorts
        ]
        result["opening_cohorts"] = _cohort_snapshots(row.opening_cohorts, metadata)
        result["closing_cohorts"] = _cohort_snapshots(row.closing_cohorts, metadata)
        result["policy_movements"] = [
            _policy_movement(item, metadata) for item in row.cohort_movements
        ]
        result["cohort_movements"] = _cohort_movements(row.cohort_movements, metadata)
        result["new_business_cohorts"] = [
            _json_value(asdict(item)) for item in bundles[row.period]
        ]
        result["new_policy_issues"] = []
        for item in row.new_business_cohorts:
            issue = _json_value(asdict(item))
            issue["policy_id"] = issue.pop("cohort_id")
            issue["cohort_id"] = metadata[item.cohort_id].cohort_id
            issue["issue_period"] = row.period
            result["new_policy_issues"].append(issue)
        rows.append(result)
    return tuple(rows)


def build_life_policy_balance(value: object) -> LifePolicyReport:
    """Validate a fully enumerated policy case and return all rows or none."""

    issues: list[LifeBalanceIssue] = []
    if type(value) is not dict:
        _issue(issues, "$", "object_required", "Policenfall-Eingang muss ein Objekt sein")
        return LifePolicyReport(None, 0, (), tuple(issues))
    _exact_fields(value, _DOCUMENT_FIELDS, "$", issues)
    for name, expected in (
        ("schema_version", LIFE_POLICY_INPUT_VERSION),
        ("life_sector_contract_schema_version", LIFE_SECTOR_V3_CONTRACT_VERSION),
        ("sector_taxonomy_schema_version", SECTOR_TAXONOMY_VERSION),
        ("source_kind", "explicit_scenario"),
        ("historical_mapping_status", "unresolved"),
        ("sector_id", "life"),
        ("mode", "fully_enumerated_policies"),
    ):
        if value.get(name) != expected:
            _issue(issues, f"$.{name}", "contract_value_mismatch", f"{name} muss {expected!r} sein")
    insurer_id = value.get("insurer_id")
    if type(insurer_id) is not int or not 1 <= insurer_id <= VDEFMD6_INSURER_COUNT:
        _issue(issues, "$.insurer_id", "insurer_id_invalid", "Vdefmd6-VU-ID von 1 bis 25 erforderlich")
        insurer_id = None
    opening, metadata, cohort_ids = _opening(value.get("opening"), issues)
    raw_periods = value.get("periods")
    requested = len(raw_periods) if type(raw_periods) is list else 0
    periods, benefits, bundles = _periods(raw_periods, metadata, cohort_ids, issues)
    if issues:
        return LifePolicyReport(insurer_id, requested, (), tuple(issues))
    assert insurer_id is not None and opening is not None
    engine = _calculate(
        insurer_id, opening, periods, maturity_benefits=benefits,
        max_issued_ids=100 * (len(periods) + 1), max_active_policies=100,
    )
    if engine.issues:
        translated = tuple(LifeBalanceIssue(
            issue.path.replace(".cohort_flows", ".policy_flows"),
            issue.code, issue.message,
        ) for issue in engine.issues)
        return LifePolicyReport(insurer_id, requested, (), translated)
    return LifePolicyReport(insurer_id, requested, _rows(engine.rows, metadata, bundles), ())
