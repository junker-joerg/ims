import json
import re
from dataclasses import FrozenInstanceError

import pytest

from ims.model.life_sector_contract import (
    LIFE_EQUATIONS,
    LIFE_FIELDS,
    LIFE_SECTOR_CONTRACT_VERSION,
    LIFE_STRATEGY_HOOKS,
    life_sector_contract_payload,
)
from ims.model.sector_taxonomy import SECTOR_TAXONOMY_VERSION


def test_life_contract_is_separate_and_read_only() -> None:
    payload = json.loads(json.dumps(life_sector_contract_payload(), sort_keys=True))

    assert payload["schema_version"] == LIFE_SECTOR_CONTRACT_VERSION
    assert payload["sector_taxonomy_schema_version"] == SECTOR_TAXONOMY_VERSION
    assert payload["scope"]["sector_id"] == "life"
    assert payload["scope"]["model_family"] == "life"
    assert payload["scope"]["initial_cohort_model"] == "one_closed_homogeneous_cohort"
    assert payload["scope"]["period_unit"] == "IMS_model_period_not_calendar_year"
    assert payload["scope"]["new_business_enabled"] is False
    assert payload["source_binding"]["legacy_sp_1_2_reused"] is False
    assert payload["source_binding"]["legacy_rk_1_2_reused"] is False
    assert payload["source_binding"]["non_life_rule_catalog_reused"] is False
    for key in (
        "calculation_available", "strategy_assignment_available",
        "snapshot_materialization_enabled", "writes_enabled", "execution_enabled",
        "simulation_performed", "statutory_or_solvency_ii_claim",
        "historical_full_equality_claim",
    ):
        assert payload[key] is False
    assert payload == life_sector_contract_payload()


def test_state_flow_and_equations_are_closed_over_declared_fields() -> None:
    fields = {field.field_id: field for field in LIFE_FIELDS}
    assert len(fields) == len(LIFE_FIELDS)
    assert {field.kind for field in LIFE_FIELDS} == {
        "opening_stock", "issue_term", "period_flow", "derived_flow", "closing_stock",
    }
    assert fields["guaranteed_rate_per_period"].kind == "issue_term"
    assert fields["investment_result"].sign == "signed"
    assert fields["opening_equity"].sign == "signed"
    assert fields["closing_guarantee_liability"].kind == "closing_stock"
    assert fields["deaths"].value_type == "integer"
    assert fields["surrenders"].value_type == "integer"

    targets = {equation.target for equation in LIFE_EQUATIONS}
    assert targets == {
        "closing_active_policies", "closing_backing_assets",
        "closing_guarantee_liability", "period_profit", "closing_equity",
    }
    for equation in LIFE_EQUATIONS:
        assert set(re.findall(r"[a-z_]+", equation.expression)) <= fields.keys()

    payload = life_sector_contract_payload()
    assert payload["immutable_issue_terms"] == ["guaranteed_rate_per_period"]
    assert "opening_backing_assets = opening_guarantee_liability + opening_equity" in payload["identities"]
    assert "closing_backing_assets = closing_guarantee_liability + closing_equity" in payload["identities"]
    carryover = payload["carryover"]
    assert len(carryover) == 5
    assert all(item["next_opening"].replace("opening_", "") ==
               item["previous_closing"].replace("closing_", "") for item in carryover)


def test_strategy_hooks_do_not_mutate_issue_guarantee_or_old_catalog() -> None:
    assert {hook.actor_type for hook in LIFE_STRATEGY_HOOKS} == {"insurer", "policyholder"}
    assert {hook.hook_id for hook in LIFE_STRATEGY_HOOKS} == {
        "life_insurer_bonus_crediting", "life_policyholder_surrender",
    }
    assert all("guaranteed_rate_per_period" not in hook.affects for hook in LIFE_STRATEGY_HOOKS)
    assert LIFE_STRATEGY_HOOKS[0].affects == ("bonus_accretion",)
    assert "surrenders" in LIFE_STRATEGY_HOOKS[1].affects
    with pytest.raises(FrozenInstanceError):
        LIFE_FIELDS[0].field_id = "legacy"  # type: ignore[misc]


def test_contract_keeps_valuation_decisions_open() -> None:
    payload = life_sector_contract_payload()
    assert payload["amounts"]["implicit_rounding_allowed"] is False
    assert payload["amounts"]["guarantee_credit_rounding"] == "pending_pr159"
    assert "guarantee_credit_base_and_rounding" in payload["pending_decisions"]
    assert "liability_release_by_exit_reason" in payload["pending_decisions"]
