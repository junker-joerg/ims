import hashlib
import json
import re

from ims.model.life_sector_contract import (
    LIFE_SECTOR_CONTRACT_V1_VERSION,
    LIFE_SECTOR_CONTRACT_VERSION,
    life_sector_contract_payload,
)
from ims.model.life_sector_v3_contract import (
    LIFE_SECTOR_V3_CONTRACT_VERSION,
    LIFE_V3_EQUATIONS,
    LIFE_V3_FIELDS,
    LIFE_V3_PERIOD_ORDER,
    life_sector_v3_contract_payload,
)


def _canonical_digest(value: dict[str, object]) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def test_v1_v2_contracts_remain_byte_stable_and_v2_stays_default() -> None:
    assert LIFE_SECTOR_CONTRACT_VERSION == "ims.life-sector-contract.v2"
    assert life_sector_contract_payload()["schema_version"] == LIFE_SECTOR_CONTRACT_VERSION
    assert _canonical_digest(life_sector_contract_payload(LIFE_SECTOR_CONTRACT_V1_VERSION)) == (
        "371b4e971b6619b10af938d36dafd4d9c2fca294f68ee5f8301a9ee4ae62cf12"
    )
    assert _canonical_digest(life_sector_contract_payload()) == (
        "35f22955f1b188f56c1474b9083be70af940da6d15c4891882453c6694837ece"
    )


def test_v3_has_unique_fields_closed_equations_and_ordered_stages() -> None:
    payload = life_sector_v3_contract_payload()
    fields = {field.field_id for field in LIFE_V3_FIELDS}
    assert len(fields) == len(LIFE_V3_FIELDS)
    assert "surrenders" not in fields and "bonus_accretion" not in fields
    assert len({equation.target for equation in LIFE_V3_EQUATIONS}) == len(LIFE_V3_EQUATIONS)
    assert all(equation.target in fields for equation in LIFE_V3_EQUATIONS)
    assert all(
        set(re.findall(r"[a-z_]+", equation.expression)) <= fields
        for equation in LIFE_V3_EQUATIONS
    )
    assert [stage.order for stage in LIFE_V3_PERIOD_ORDER] == list(range(1, 10))
    assert len({stage.stage_id for stage in LIFE_V3_PERIOD_ORDER}) == len(LIFE_V3_PERIOD_ORDER)
    assert all(set(stage.affects) <= fields for stage in LIFE_V3_PERIOD_ORDER)
    assert [stage["stage_id"] for stage in payload["period_order"]] == [
        stage.stage_id for stage in LIFE_V3_PERIOD_ORDER
    ]


def test_v3_decides_sources_timing_release_and_balance_without_execution() -> None:
    payload = life_sector_v3_contract_payload()
    assert payload["schema_version"] == LIFE_SECTOR_V3_CONTRACT_VERSION
    assert payload["base_contract_schema_version"] == LIFE_SECTOR_CONTRACT_VERSION
    assert payload["scope"]["cohort_model"] == "multiple_named_cohorts_with_immutable_issue_terms"
    assert payload["scope"]["policy_detail_active_policy_limit"] == 100
    assert payload["scope"]["mode_switch_during_run"] is False
    assert payload["cohort_ledger"]["issue_terms_immutable"] == [
        "issue_period", "issue_term_periods", "guaranteed_rate_per_period",
    ]
    assert payload["cohort_ledger"]["renewal_premium_and_allocation_per_cohort_required"] is True
    assert payload["cohort_ledger"]["death_count_per_cohort_required"] is True
    assert payload["cohort_ledger"]["optional_immutable_issue_terms"] == [
        "maturity_benefit_at_issue",
    ]
    assert payload["policy_ledger"]["cohort_liability_equals_sum_of_policy_liabilities"] is True
    assert payload["policy_ledger"]["different_rounding_grains_are_not_claimed_equal"] is True
    assert (
        "liability_release <= opening_guarantee_liability + guarantee_accretion + renewal_liability_allocation"
        in payload["identities"]
    )

    stages = {stage["stage_id"]: stage["order"] for stage in payload["period_order"]}
    assert stages["guarantee_credit"] < stages["renewal_premiums"] < stages["death_exits"]
    assert stages["death_exits"] < stages["maturity_exits"] < stages["new_business_issue"]
    assert stages["new_business_issue"] < stages["expenses_and_capital"]
    timing = payload["timing_and_valuation"]
    assert timing["new_business_first_guarantee"] == "following_period"
    assert timing["new_business_same_period_exit_allowed"] is False
    assert timing["deaths_and_maturities_from_opening_active_only"] is True
    assert timing["maturity_due"] == "opening_cohort_remaining_periods_equals_1_after_death"
    assert timing["death_benefit_equals_liability_release_assumed"] is False
    assert timing["maturity_guarantee_floor"] == (
        "maturity_benefits_paid >= maturity_liability_release"
    )
    assert timing["capital_affects_profit_or_guarantee_liability"] is False
    assert payload["future_source_modes"]["investment_modes_mutually_exclusive"] is True
    assert payload["future_source_modes"]["mortality_is_policyholder_strategy"] is False
    assert payload["future_source_modes"]["random_draws_required"] is False
    assert payload["compatibility"]["v2_closed_cohort_zero_death_zero_new_business_is_special_case"] is True
    assert set(payload["excluded"]) >= {"surrender", "bonus", "historical_full_equality"}
    assert all(payload[key] is False for key in (
        "input_validation_available", "calculation_available", "strategy_assignment_available",
        "runner_enabled", "writes_enabled", "simulation_performed",
        "statutory_or_solvency_ii_claim", "historical_full_equality_claim",
    ))
    assert payload == json.loads(json.dumps(payload)) == life_sector_v3_contract_payload()
