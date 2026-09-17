import copy
import json
from decimal import localcontext
from pathlib import Path

import pytest

from ims.accounting.life_assumptions import (
    LIFE_ASSUMPTIONS_RESULT_VERSION,
    resolve_life_period_assumptions,
)


FIXTURE = Path(__file__).parent / "fixtures" / "life_assumptions_v1.json"


def _plan() -> dict:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def _opening(period: int = 1, assets: str = "150") -> dict:
    return {
        "insurer_id": 1,
        "period": period,
        "opening_backing_assets": assets,
        "opening_policies": [
            {"policy_id": "A1", "cohort_id": "A"},
            {"policy_id": "A2", "cohort_id": "A"},
            {"policy_id": "B1", "cohort_id": "B"},
        ],
    }


def _codes(plan: dict, opening: dict | None = None) -> set[str]:
    result = resolve_life_period_assumptions(plan, opening if opening is not None else _opening()).to_dict()
    assert result["valid"] is False
    assert result["investment_result"] is None
    assert result["death_policy_ids"] == []
    assert result["deaths_by_cohort"] == []
    return {item["code"] for item in result["issues"]}


def test_curve_results_rounding_and_provenance() -> None:
    plan, opening = _plan(), _opening()
    before = copy.deepcopy((plan, opening))
    report = resolve_life_period_assumptions(plan, opening)
    result = report.to_dict()
    assert result["schema_version"] == LIFE_ASSUMPTIONS_RESULT_VERSION
    assert result["valid"] is True
    assert result["investment_mode"] == "insurer_rule_on_opening_backing_assets"
    assert result["mortality_mode"] == "exogenous_deterministic_rate_curve"
    assert result["opening_backing_assets"] == "150.0000"
    assert result["opening_active_policies"] == 3
    assert result["investment_rate_per_period"] == "0.050000"
    assert result["mortality_rate_per_period"] == "0.500000"
    assert result["investment_result"] == "7.5000"
    assert result["death_policy_ids"] == ["A1", "B1"]
    assert result["deaths_by_cohort"] == [
        {"cohort_id": "A", "deaths": 1},
        {"cohort_id": "B", "deaths": 1},
    ]
    assert result["death_count"] == 2
    assert result == report.to_dict() == resolve_life_period_assumptions(plan, opening).to_dict()
    assert json.loads(json.dumps(result)) == result
    assert (plan, opening) == before
    assert all(result[key] is False for key in (
        "writes_performed", "runner_invoked", "simulation_performed",
        "statutory_or_solvency_ii_claim", "historical_full_equality_claim",
    ))


def test_rule_is_on_opening_assets_and_excludes_new_money() -> None:
    result = resolve_life_period_assumptions(_plan(), _opening(2, "143")).to_dict()
    assert result["investment_result"] == "7.1500"
    assert result["mortality_rate_per_period"] == "0.250000"
    assert result["death_policy_ids"] == ["A1"]
    assert result["deaths_by_cohort"] == [
        {"cohort_id": "A", "deaths": 1},
        {"cohort_id": "B", "deaths": 0},
    ]


def test_negative_investment_and_independent_explicit_mortality() -> None:
    plan = _plan()
    plan["mortality"] = {
        "mode": "explicit_death_policy_ids",
        "periods": [
            {"period": 2, "death_policy_ids": []},
            {"period": 1, "death_policy_ids": ["B1", "A2"]},
            {"period": 3, "death_policy_ids": []},
        ],
    }
    first = resolve_life_period_assumptions(plan, _opening()).to_dict()
    assert first["valid"] is True
    assert first["investment_result"] == "7.5000"
    assert first["mortality_rate_per_period"] is None
    assert first["death_policy_ids"] == ["A2", "B1"]
    third = resolve_life_period_assumptions(plan, _opening(3, "100")).to_dict()
    assert third["investment_result"] == "-10.0000"
    assert third["death_policy_ids"] == []


def test_explicit_investment_and_curve_mortality_are_independent() -> None:
    plan = _plan()
    plan["investment"] = {
        "mode": "explicit_scenario",
        "periods": [
            {"period": 3, "investment_result": "-1"},
            {"period": 1, "investment_result": "9.25"},
            {"period": 2, "investment_result": "0"},
        ],
    }
    result = resolve_life_period_assumptions(plan, _opening()).to_dict()
    assert result["valid"] is True
    assert result["investment_result"] == "9.2500"
    assert result["investment_rate_per_period"] is None
    assert result["death_policy_ids"] == ["A1", "B1"]


def test_half_even_money_and_half_up_death_counts_are_distinct() -> None:
    plan = _plan()
    plan["period_count"] = 1
    plan["investment"]["windows"] = [{
        "start_period": 1, "end_period": 1, "rate_per_period": "0.5",
    }]
    plan["mortality"]["windows"] = [{
        "start_period": 1, "end_period": 1, "rate_per_period": "0.5",
    }]
    opening = _opening(1, "0.0001")
    opening["opening_policies"] = [{"policy_id": "A1", "cohort_id": "A"}]
    with localcontext() as context:
        context.prec = 3
        result = resolve_life_period_assumptions(plan, opening).to_dict()
    assert result["valid"] is True
    assert result["investment_result"] == "0.0000"
    assert result["death_policy_ids"] == ["A1"]
    assert result["deaths_by_cohort"] == [{"cohort_id": "A", "deaths": 1}]


def test_order_and_extension_keep_prefix_values() -> None:
    plan = _plan()
    opening = _opening()
    base = resolve_life_period_assumptions(plan, opening).to_dict()
    reversed_plan = copy.deepcopy(plan)
    reversed_plan["investment"]["windows"].reverse()
    reversed_plan["mortality"]["windows"].reverse()
    reversed_opening = copy.deepcopy(opening)
    reversed_opening["opening_policies"].reverse()
    assert resolve_life_period_assumptions(reversed_plan, reversed_opening).to_dict() == base
    shorter = copy.deepcopy(plan)
    shorter["period_count"] = 2
    shorter["investment"]["windows"] = shorter["investment"]["windows"][:1]
    shorter["mortality"]["windows"][1]["end_period"] = 2
    assert resolve_life_period_assumptions(shorter, opening).to_dict() == base


@pytest.mark.parametrize(("mutation", "code"), [
    (lambda plan: plan["investment"].update({"periods": []}), "field_unknown"),
    (lambda plan: plan["mortality"].update({"periods": []}), "field_unknown"),
    (lambda plan: plan["investment"]["windows"][1].update({"start_period": 2}), "window_coverage_invalid"),
    (lambda plan: plan["mortality"]["windows"][1].update({"start_period": 3}), "window_coverage_invalid"),
    (lambda plan: plan["investment"]["windows"][0].update({"end_period": 0}), "count_invalid"),
    (lambda plan: plan["mortality"]["windows"][0].update({"rate_per_period": "1.1"}), "rate_invalid"),
    (lambda plan: plan["investment"]["windows"][0].update({"rate_per_period": "-1.1"}), "investment_rate_invalid"),
    (lambda plan: plan.update({"insurer_id": 26}), "count_invalid"),
    (lambda plan: plan.update({"period_count": True}), "count_invalid"),
    (lambda plan: plan.update({"schema_version": "unknown"}), "contract_value_mismatch"),
])
def test_invalid_plans_are_atomic(mutation, code: str) -> None:
    plan = _plan()
    mutation(plan)
    assert code in _codes(plan)


def test_unknown_explicit_death_and_duplicate_opening_are_atomic() -> None:
    plan = _plan()
    plan["mortality"] = {
        "mode": "explicit_death_policy_ids",
        "periods": [{"period": number, "death_policy_ids": ["X"] if number == 1 else []}
                    for number in range(1, 4)],
    }
    assert "death_policy_not_active" in _codes(plan)
    plan["mortality"]["periods"][0]["death_policy_ids"] = ["A1", "A1"]
    assert "death_id_duplicate" in _codes(plan)
    plan = _plan()
    opening = _opening()
    opening["opening_policies"][1]["policy_id"] = "A1"
    assert "policy_id_duplicate" in _codes(plan, opening)


def test_explicit_series_duplicate_and_missing_period_rejected() -> None:
    plan = _plan()
    plan["investment"] = {
        "mode": "explicit_scenario",
        "periods": [
            {"period": 1, "investment_result": "0"},
            {"period": 1, "investment_result": "0"},
            {"period": 3, "investment_result": "0"},
        ],
    }
    codes = _codes(plan)
    assert "period_duplicate" in codes
    assert "period_coverage_invalid" in codes


def test_period_outside_horizon_and_invalid_basis_rejected() -> None:
    plan = _plan()
    assert "period_outside_plan" in _codes(plan, _opening(4))
    opening = _opening()
    opening["insurer_id"] = 2
    assert "insurer_id_mismatch" in _codes(plan, opening)
    opening = _opening()
    opening["opening_backing_assets"] = "-1"
    assert "negative_amount" in _codes(plan, opening)


def test_full_horizon_and_policy_limit_are_bounded() -> None:
    plan = _plan()
    plan["period_count"] = 100
    for source in ("investment", "mortality"):
        plan[source]["windows"] = [{
            "start_period": 1, "end_period": 100,
            "rate_per_period": "0.10",
        }]
    opening = _opening(100, "100")
    opening["opening_policies"] = [
        {"policy_id": f"A{number}", "cohort_id": "A"}
        for number in range(100)
    ]
    result = resolve_life_period_assumptions(plan, opening).to_dict()
    assert result["valid"] is True
    assert result["investment_result"] == "10.0000"
    assert result["death_count"] == 10
    assert result["death_policy_ids"] == sorted(
        item["policy_id"] for item in opening["opening_policies"]
    )[:10]
    assert result["deaths_by_cohort"] == [{"cohort_id": "A", "deaths": 10}]
    opening["opening_policies"].append({"policy_id": "A100", "cohort_id": "A"})
    assert "policy_list_invalid" in _codes(plan, opening)
