import json
import re
from dataclasses import FrozenInstanceError

import pytest

from ims.model.health_sector_contract import (
    HEALTH_CARRYOVER,
    HEALTH_EQUATIONS,
    HEALTH_FIELDS,
    HEALTH_SECTOR_CONTRACT_VERSION,
    HEALTH_STRATEGY_HOOKS,
    health_sector_contract_payload,
)
from ims.model.sector_taxonomy import SECTOR_TAXONOMY_VERSION


def test_health_contract_is_separate_deterministic_and_read_only() -> None:
    payload = health_sector_contract_payload()
    assert payload == json.loads(json.dumps(payload)) == health_sector_contract_payload()
    assert payload["schema_version"] == HEALTH_SECTOR_CONTRACT_VERSION
    assert payload["sector_taxonomy_schema_version"] == SECTOR_TAXONOMY_VERSION
    assert payload["scope"]["sector_id"] == "health"
    assert payload["scope"]["initial_portfolio"] == "one_closed_homogeneous_portfolio"
    assert payload["scope"]["period_unit"] == "IMS_model_period_not_calendar_year"
    assert payload["scope"]["new_business_enabled"] is False
    assert payload["scope"]["exits_enabled"] is False
    assert payload["scope"]["historical_mapping_status"] == "unresolved"
    for key in (
        "input_validation_available", "calculation_available", "strategy_assignment_available",
        "snapshot_materialization_enabled", "runner_enabled", "writes_enabled",
        "simulation_performed", "statutory_or_solvency_ii_claim",
        "historical_full_equality_claim",
    ):
        assert payload[key] is False


def test_fields_equations_and_carryover_close_without_double_counting() -> None:
    fields = {field.field_id: field for field in HEALTH_FIELDS}
    assert len(fields) == len(HEALTH_FIELDS)
    assert fields["opening_active_policies"].value_type == "integer"
    assert fields["closing_benefit_liability"].kind == "closing_stock"
    assert fields["opening_equity"].sign == "signed"
    assert fields["investment_result"].sign == "signed"
    assert fields["benefits_incurred"].kind == "period_flow"
    assert fields["benefits_paid"].kind == "period_flow"
    equations = {equation.target: equation.expression for equation in HEALTH_EQUATIONS}
    assert len(equations) == len(HEALTH_EQUATIONS)
    assert set(equations) == {
        "closing_active_policies", "closing_cash", "closing_benefit_liability",
        "closing_equity", "period_profit",
    }
    for expression in equations.values():
        assert set(re.findall(r"[a-z_]+", expression)) <= fields.keys()
    assert equations["closing_active_policies"] == "opening_active_policies"
    assert "benefits_incurred" in equations["period_profit"]
    assert "benefits_paid" not in equations["period_profit"]
    assert "benefits_paid" in equations["closing_cash"]
    assert "benefits_paid" in equations["closing_benefit_liability"]
    assert "benefits_incurred" not in equations["closing_cash"]
    assert HEALTH_CARRYOVER == tuple(
        (f"opening_{name}", f"closing_{name}")
        for name in ("active_policies", "cash", "benefit_liability", "equity")
    )
    assert "opening_cash = opening_benefit_liability + opening_equity" in (
        health_sector_contract_payload()["identities"]
    )
    assert "closing_cash = closing_benefit_liability + closing_equity" in (
        health_sector_contract_payload()["identities"]
    )
    assert "benefits_paid <= opening_benefit_liability + benefits_incurred" in (
        health_sector_contract_payload()["identities"]
    )


def test_balanced_example_satisfies_contract_without_executing_it() -> None:
    # A single illustrative check of the algebra, not a health calculator.
    opening_cash, opening_liability, opening_equity = 100, 20, 80
    premium, incurred, paid, investment, expense = 30, 18, 15, 2, 4
    contribution, distribution = 5, 3
    closing_liability = opening_liability + incurred - paid
    closing_cash = opening_cash + premium + investment + contribution - paid - expense - distribution
    profit = premium + investment - incurred - expense
    closing_equity = opening_equity + profit + contribution - distribution
    assert closing_cash == closing_liability + closing_equity
    assert (closing_cash, closing_liability, closing_equity, profit) == (115, 23, 92, 10)


def test_future_hooks_do_not_reclassify_exogenous_benefits_as_insurer_strategy() -> None:
    payload = health_sector_contract_payload()
    assert {hook.actor_type for hook in HEALTH_STRATEGY_HOOKS} == {
        "insurer", "policyholder",
    }
    assert {hook.hook_id for hook in HEALTH_STRATEGY_HOOKS} == {
        "health_insurer_pricing", "health_policyholder_switching",
    }
    assert all("future_only" in hook.constraint for hook in HEALTH_STRATEGY_HOOKS)
    assert all("benefits_incurred" not in hook.affects for hook in HEALTH_STRATEGY_HOOKS)
    assert payload["source_binding"]["benefit_incurred_is_insurer_strategy"] is False
    assert payload["source_binding"]["legacy_sp_1_2_reused"] is False
    assert payload["source_binding"]["legacy_rk_1_2_reused"] is False
    assert payload["source_binding"]["non_life_rule_catalog_reused"] is False
    assert "ageing_reserve" in payload["excluded"]
    assert payload["timing_and_valuation"]["benefit_liability_basis"] == (
        "incurred_unpaid_benefits_not_ageing_reserve"
    )
    with pytest.raises(FrozenInstanceError):
        HEALTH_FIELDS[0].field_id = "legacy"  # type: ignore[misc]
