"""Pure, bounded life-period chain using verified policy and assumption contracts."""

from __future__ import annotations

import copy
from collections.abc import Callable
from dataclasses import asdict, dataclass

from ims.accounting.life_assumptions import resolve_life_period_assumptions
from ims.accounting.life_closed_cohort_balance import _amount, _exact_fields, _issue
from ims.accounting.life_cohort_balance import _cohort_id, _integer
from ims.accounting.life_model_balance import LifeBalanceIssue
from ims.accounting.life_policy_balance import (
    LIFE_POLICY_INPUT_VERSION,
    build_life_policy_balance,
)
from ims.model.life_sector_v3_contract import LIFE_SECTOR_V3_CONTRACT_VERSION
from ims.model.sector_taxonomy import SECTOR_TAXONOMY_VERSION
from ims.model.vdefmd6_population import VDEFMD6_INSURER_COUNT


LIFE_PERIOD_CHAIN_INPUT_VERSION = "ims.life-period-chain-input.v1"
LIFE_PERIOD_CHAIN_RESULT_VERSION = "ims.life-period-chain-result.v1"
_DOCUMENT_FIELDS = frozenset((
    "schema_version", "life_sector_contract_schema_version",
    "sector_taxonomy_schema_version", "source_kind", "historical_mapping_status",
    "insurer_id", "sector_id", "opening", "assumptions", "periods",
))
_PERIOD_FIELDS = frozenset((
    "period", "policy_flows", "new_business", "operating_expense_paid",
    "capital_contribution", "capital_distribution",
))
_FLOW_FIELDS = frozenset((
    "policy_id", "renewal_premiums_collected", "renewal_liability_allocation",
    "death_benefit_if_death", "maturity_benefit_if_due",
))
_CARRYOVER_FIELDS = (
    "active_policies", "backing_assets", "guarantee_liability", "equity",
)


@dataclass(frozen=True, slots=True)
class LifePeriodChainReport:
    insurer_id: int | None
    requested_period_count: int
    rows: tuple[dict[str, object], ...]
    resolved_sources: tuple[dict[str, object], ...]
    policy_periods: int
    issues: tuple[LifeBalanceIssue, ...]

    def to_dict(self) -> dict[str, object]:
        valid = not self.issues
        return {
            "schema_version": LIFE_PERIOD_CHAIN_RESULT_VERSION,
            "input_schema_version": LIFE_PERIOD_CHAIN_INPUT_VERSION,
            "life_sector_contract_schema_version": LIFE_SECTOR_V3_CONTRACT_VERSION,
            "status": "ok" if valid else "error",
            "valid": valid,
            "insurer_id": self.insurer_id,
            "sector_id": "life",
            "source_kind": "versioned_life_period_chain",
            "historical_mapping_status": "unresolved",
            "requested_period_count": self.requested_period_count,
            "calculated_period_count": len(self.rows) if valid else 0,
            "policy_periods": self.policy_periods if valid else 0,
            "rows": list(copy.deepcopy(self.rows)) if valid else [],
            "resolved_sources": list(copy.deepcopy(self.resolved_sources)) if valid else [],
            "issue_count": len(self.issues),
            "issues": [asdict(issue) for issue in self.issues],
            "writes_performed": False,
            "app_runner_invoked": False,
            "historical_simulation_performed": False,
            "life_period_chain_calculated": valid,
            "statutory_or_solvency_ii_claim": False,
            "historical_full_equality_claim": False,
        }


def _flows(value: object, path: str, issues: list[LifeBalanceIssue]) -> list[dict] | None:
    if type(value) is not list or len(value) > 100:
        _issue(issues, path, "policy_flow_list_invalid", "Hoechstens 100 Anfangspolicenfluesse erforderlich")
        return None
    result = []
    ids = set()
    for index, item in enumerate(value):
        item_path = f"{path}[{index}]"
        if type(item) is not dict:
            _issue(issues, item_path, "object_required", "Policenfluss muss ein Objekt sein")
            continue
        _exact_fields(item, _FLOW_FIELDS, item_path, issues)
        policy_id = _cohort_id(item.get("policy_id"), f"{item_path}.policy_id", issues)
        amounts = {
            name: _amount(item.get(name), f"{item_path}.{name}", issues)
            for name in (
                "renewal_premiums_collected", "renewal_liability_allocation",
                "death_benefit_if_death", "maturity_benefit_if_due",
            )
        }
        premium = amounts["renewal_premiums_collected"]
        allocation = amounts["renewal_liability_allocation"]
        if premium is not None and allocation is not None and allocation > premium:
            _issue(issues, f"{item_path}.renewal_liability_allocation", "premium_allocation_exceeds_collected", "Zuweisung uebersteigt eingezogene Praemie")
        if policy_id is None or None in amounts.values():
            continue
        if policy_id in ids:
            _issue(issues, f"{item_path}.policy_id", "policy_flow_duplicate", "Policenfluss kommt mehrfach vor")
        ids.add(policy_id)
        result.append(item)
    return sorted(result, key=lambda flow: flow["policy_id"])


def _periods(value: object, issues: list[LifeBalanceIssue]) -> list[dict] | None:
    if type(value) is not list or not 1 <= len(value) <= 100:
        _issue(issues, "$.periods", "period_count_invalid", "1 bis 100 Perioden erforderlich")
        return None
    result = []
    for index, item in enumerate(value):
        path = f"$.periods[{index}]"
        if type(item) is not dict:
            _issue(issues, path, "object_required", "Periodeneingang muss ein Objekt sein")
            continue
        _exact_fields(item, _PERIOD_FIELDS, path, issues)
        if type(item.get("period")) is not int or item["period"] != index + 1:
            _issue(issues, f"{path}.period", "period_sequence_invalid", "Perioden muessen bei 1 beginnen und lueckenlos folgen")
        flows = _flows(item.get("policy_flows"), f"{path}.policy_flows", issues)
        new = item.get("new_business")
        if type(new) is not list or len(new) > 100:
            _issue(issues, f"{path}.new_business", "new_business_list_invalid", "Hoechstens 100 neue Kohorten je Periode")
        else:
            new_policy_count = 0
            for new_index, bundle in enumerate(new):
                bundle_path = f"{path}.new_business[{new_index}]"
                if type(bundle) is not dict:
                    _issue(issues, bundle_path, "object_required", "Neue Kohorte muss ein Objekt sein")
                    continue
                policies = bundle.get("policies")
                if type(policies) is not list or len(policies) > 100:
                    _issue(issues, f"{bundle_path}.policies", "policy_list_invalid", "Hoechstens 100 neue Policen je Kohorte")
                else:
                    new_policy_count += len(policies)
            if new_policy_count > 100:
                _issue(issues, f"{path}.new_business", "new_policy_budget_exceeded", "Hoechstens 100 neue Policen je Periode")
        for name in ("operating_expense_paid", "capital_contribution", "capital_distribution"):
            _amount(item.get(name), f"{path}.{name}", issues)
        if flows is not None and type(new) is list and len(new) <= 100:
            result.append({**item, "policy_flows": flows})
    return result


def _initial_basis(opening: object, insurer_id: int, issues: list[LifeBalanceIssue]) -> dict | None:
    if type(opening) is not dict:
        _issue(issues, "$.opening", "object_required", "Anfangsbestand muss ein Objekt sein")
        return None
    policies = opening.get("policies")
    if type(policies) is not list or len(policies) > 100:
        _issue(issues, "$.opening.policies", "policy_list_invalid", "Hoechstens 100 vollstaendige Anfangspolicen erforderlich")
        return None
    refs = []
    for index, policy in enumerate(policies):
        if type(policy) is not dict:
            _issue(issues, f"$.opening.policies[{index}]", "object_required", "Anfangspolice muss ein Objekt sein")
            continue
        refs.append({"policy_id": policy.get("policy_id"), "cohort_id": policy.get("cohort_id")})
    return {
        "insurer_id": insurer_id,
        "period": 1,
        "opening_backing_assets": opening.get("opening_backing_assets"),
        "opening_policies": refs,
    }


def _materialized_period(template: dict, source: dict) -> dict:
    dead = set(source["death_policy_ids"])
    flows = []
    for flow in template["policy_flows"]:
        death = flow["policy_id"] in dead
        flows.append({
            "policy_id": flow["policy_id"],
            "renewal_premiums_collected": flow["renewal_premiums_collected"],
            "renewal_liability_allocation": flow["renewal_liability_allocation"],
            "death": death,
            "death_benefits_paid": flow["death_benefit_if_death"] if death else "0",
            "maturity_benefits_paid": "0" if death else flow["maturity_benefit_if_due"],
        })
    return {
        "period": template["period"],
        "policy_flows": flows,
        "new_business": copy.deepcopy(template["new_business"]),
        "investment_result": source["investment_result"],
        "operating_expense_paid": template["operating_expense_paid"],
        "capital_contribution": template["capital_contribution"],
        "capital_distribution": template["capital_distribution"],
    }


def _carryover(previous: dict, current: dict) -> bool:
    if current["opening_policies"] != previous["closing_policies"]:
        return False
    if current["opening_cohorts"] != previous["closing_cohorts"]:
        return False
    return all(
        current[f"opening_{name}"] == previous[f"closing_{name}"]
        for name in _CARRYOVER_FIELDS
    )


def run_life_policy_period_chain(
    value: object, *, should_cancel: Callable[[], bool] | None = None,
) -> LifePeriodChainReport:
    """Resolve sources and account for every period; return all rows or none."""

    issues: list[LifeBalanceIssue] = []
    if type(value) is not dict:
        _issue(issues, "$", "object_required", "Lebensketten-Eingang muss ein Objekt sein")
        return LifePeriodChainReport(None, 0, (), (), 0, tuple(issues))
    _exact_fields(value, _DOCUMENT_FIELDS, "$", issues)
    for name, expected in (
        ("schema_version", LIFE_PERIOD_CHAIN_INPUT_VERSION),
        ("life_sector_contract_schema_version", LIFE_SECTOR_V3_CONTRACT_VERSION),
        ("sector_taxonomy_schema_version", SECTOR_TAXONOMY_VERSION),
        ("source_kind", "versioned_life_period_chain"),
        ("historical_mapping_status", "unresolved"),
        ("sector_id", "life"),
    ):
        if value.get(name) != expected:
            _issue(issues, f"$.{name}", "contract_value_mismatch", f"{name} muss {expected!r} sein")
    insurer_id = _integer(value.get("insurer_id"), "$.insurer_id", issues, 1, VDEFMD6_INSURER_COUNT)
    raw_periods = value.get("periods")
    requested = len(raw_periods) if type(raw_periods) is list else 0
    templates = _periods(raw_periods, issues)
    assumptions = value.get("assumptions")
    if type(assumptions) is not dict:
        _issue(issues, "$.assumptions", "object_required", "Versionierter Annahmeplan erforderlich")
    else:
        if insurer_id is not None and (type(assumptions.get("insurer_id")) is not int or assumptions["insurer_id"] != insurer_id):
            _issue(issues, "$.assumptions.insurer_id", "assumption_insurer_mismatch", "Annahmeplan und Lebensfall haben verschiedene VU-IDs")
        if type(assumptions.get("period_count")) is not int or assumptions["period_count"] != requested:
            _issue(issues, "$.assumptions.period_count", "assumption_horizon_mismatch", "Annahmeplan und Lebensfall haben verschiedene Horizonte")
    basis = _initial_basis(value.get("opening"), insurer_id, issues) if insurer_id is not None else None
    if issues or templates is None or basis is None:
        return LifePeriodChainReport(insurer_id, requested, (), (), 0, tuple(issues))

    case = {
        "schema_version": LIFE_POLICY_INPUT_VERSION,
        "life_sector_contract_schema_version": LIFE_SECTOR_V3_CONTRACT_VERSION,
        "sector_taxonomy_schema_version": SECTOR_TAXONOMY_VERSION,
        "source_kind": "explicit_scenario",
        "historical_mapping_status": "unresolved",
        "insurer_id": insurer_id,
        "sector_id": "life",
        "mode": "fully_enumerated_policies",
        "opening": copy.deepcopy(value["opening"]),
        "periods": [],
    }
    sources = []
    rows = []
    policy_periods = 0
    for index, template in enumerate(templates):
        if should_cancel is not None and should_cancel():
            _issue(issues, f"$.periods[{index}]", "run_cancelled", "Lebenskette vor der naechsten Periode abgebrochen")
            break
        source_report = resolve_life_period_assumptions(assumptions, basis)
        if source_report.issues:
            for issue in source_report.issues:
                if issue.path.startswith("$.opening"):
                    path = ("$.opening" if index == 0 else f"$.periods[{index}].opening") + issue.path[len("$.opening"):]
                else:
                    path = f"$.assumptions{issue.path[1:]}"
                issues.append(LifeBalanceIssue(path, issue.code, issue.message))
            break
        source = source_report.to_dict()
        active_ids = {policy["policy_id"] for policy in basis["opening_policies"]}
        flow_ids = {flow["policy_id"] for flow in template["policy_flows"]}
        if flow_ids != active_ids:
            _issue(issues, f"$.periods[{index}].policy_flows", "policy_flows_mismatch", "Genau ein Fluss je aktiver Anfangspolice erforderlich")
            break
        case["periods"].append(_materialized_period(template, source))
        calculated = build_life_policy_balance(case)
        if calculated.issues:
            issues.extend(calculated.issues)
            break
        current = calculated.rows[-1]
        if rows and not _carryover(rows[-1], current):
            _issue(issues, f"$.periods[{index}]", "life_carryover_mismatch", "Anfangsbestand weicht vom geprueften Vorperiodenschluss ab")
            break
        policy_periods += current["opening_active_policies"]
        if policy_periods > 10_000:
            _issue(issues, f"$.periods[{index}]", "policy_period_budget_exceeded", "Hoechstens 10000 aktive Policen-Perioden")
            break
        rows.append(current)
        sources.append(source)
        basis = {
            "insurer_id": insurer_id,
            "period": index + 2,
            "opening_backing_assets": current["closing_backing_assets"],
            "opening_policies": [
                {"policy_id": policy["policy_id"], "cohort_id": policy["cohort_id"]}
                for policy in current["closing_policies"]
            ],
        }
    if issues:
        return LifePeriodChainReport(insurer_id, requested, (), (), 0, tuple(issues))
    return LifePeriodChainReport(insurer_id, requested, tuple(rows), tuple(sources), policy_periods, ())
