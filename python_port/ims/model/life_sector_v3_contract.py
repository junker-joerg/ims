"""Read-only target contract for the staged life-sector expansion after PR159."""

from dataclasses import asdict, dataclass

from ims.model.life_sector_contract import LIFE_SECTOR_CONTRACT_V2_VERSION, LifeEquation, LifeField
from ims.model.sector_taxonomy import SECTOR_TAXONOMY_VERSION
from ims.model.vdefmd6_population import VDEFMD6_INSURER_COUNT


LIFE_SECTOR_V3_CONTRACT_VERSION = "ims.life-sector-contract.v3"


@dataclass(frozen=True, slots=True)
class LifePeriodStage:
    order: int
    stage_id: str
    source: str
    affects: tuple[str, ...]


LIFE_V3_FIELDS = (
    LifeField("opening_active_policies", "opening_stock", "integer", "nonnegative"),
    LifeField("opening_backing_assets", "opening_stock", "amount", "nonnegative"),
    LifeField("opening_guarantee_liability", "opening_stock", "amount", "nonnegative"),
    LifeField("opening_equity", "opening_stock", "amount", "signed"),
    LifeField("renewal_premiums_collected", "period_flow", "amount", "nonnegative"),
    LifeField("new_business_premiums_collected", "period_flow", "amount", "nonnegative"),
    LifeField("premiums_collected", "derived_flow", "amount", "nonnegative"),
    LifeField("renewal_liability_allocation", "period_flow", "amount", "nonnegative"),
    LifeField("new_business_liability_allocation", "period_flow", "amount", "nonnegative"),
    LifeField("premium_liability_allocation", "derived_flow", "amount", "nonnegative"),
    LifeField("investment_result", "period_flow", "amount", "signed"),
    LifeField("guarantee_accretion", "derived_flow", "amount", "nonnegative"),
    LifeField("deaths", "period_flow", "integer", "nonnegative"),
    LifeField("death_benefits_paid", "period_flow", "amount", "nonnegative"),
    LifeField("death_liability_release", "period_flow", "amount", "nonnegative"),
    LifeField("maturities", "period_flow", "integer", "nonnegative"),
    LifeField("maturity_benefits_paid", "period_flow", "amount", "nonnegative"),
    LifeField("maturity_liability_release", "period_flow", "amount", "nonnegative"),
    LifeField("liability_release", "derived_flow", "amount", "nonnegative"),
    LifeField("new_business_policies", "period_flow", "integer", "nonnegative"),
    LifeField("operating_expense_paid", "period_flow", "amount", "nonnegative"),
    LifeField("capital_contribution", "period_flow", "amount", "nonnegative"),
    LifeField("capital_distribution", "period_flow", "amount", "nonnegative"),
    LifeField("period_profit", "derived_flow", "amount", "signed"),
    LifeField("closing_active_policies", "closing_stock", "integer", "nonnegative"),
    LifeField("closing_backing_assets", "closing_stock", "amount", "nonnegative"),
    LifeField("closing_guarantee_liability", "closing_stock", "amount", "nonnegative"),
    LifeField("closing_equity", "closing_stock", "amount", "signed"),
)

LIFE_V3_EQUATIONS = (
    LifeEquation(
        "premiums_collected",
        "renewal_premiums_collected + new_business_premiums_collected",
    ),
    LifeEquation(
        "premium_liability_allocation",
        "renewal_liability_allocation + new_business_liability_allocation",
    ),
    LifeEquation(
        "liability_release", "death_liability_release + maturity_liability_release",
    ),
    LifeEquation(
        "closing_active_policies",
        "opening_active_policies - deaths - maturities + new_business_policies",
    ),
    LifeEquation(
        "closing_backing_assets",
        "opening_backing_assets + premiums_collected + investment_result"
        " + capital_contribution - death_benefits_paid - maturity_benefits_paid"
        " - operating_expense_paid - capital_distribution",
    ),
    LifeEquation(
        "closing_guarantee_liability",
        "opening_guarantee_liability + guarantee_accretion"
        " + premium_liability_allocation - liability_release",
    ),
    LifeEquation(
        "period_profit",
        "premiums_collected + investment_result - death_benefits_paid"
        " - maturity_benefits_paid - operating_expense_paid"
        " - (closing_guarantee_liability - opening_guarantee_liability)",
    ),
    LifeEquation(
        "closing_equity",
        "opening_equity + period_profit + capital_contribution - capital_distribution",
    ),
)

LIFE_V3_PERIOD_ORDER = (
    LifePeriodStage(1, "opening", "explicit_initial_or_prior_closing", (
        "opening_active_policies", "opening_backing_assets",
        "opening_guarantee_liability", "opening_equity",
    )),
    LifePeriodStage(2, "investment", "explicit_scenario_or_future_insurer_rule", (
        "investment_result",
    )),
    LifePeriodStage(3, "guarantee_credit", "immutable_cohort_issue_terms", (
        "guarantee_accretion",
    )),
    LifePeriodStage(4, "renewal_premiums", "explicit_existing_policy_flows", (
        "renewal_premiums_collected", "renewal_liability_allocation",
    )),
    LifePeriodStage(5, "death_exits", "explicit_scenario_or_future_exogenous_curve", (
        "deaths", "death_benefits_paid", "death_liability_release",
    )),
    LifePeriodStage(6, "maturity_exits", "remaining_term_of_opening_policies", (
        "maturities", "maturity_benefits_paid", "maturity_liability_release",
    )),
    LifePeriodStage(7, "new_business_issue", "explicit_new_cohort_issue_terms", (
        "new_business_policies", "new_business_premiums_collected",
        "new_business_liability_allocation",
    )),
    LifePeriodStage(8, "expenses_and_capital", "explicit_scenario", (
        "operating_expense_paid", "capital_contribution", "capital_distribution",
    )),
    LifePeriodStage(9, "closing_reconciliation", "derived", (
        "closing_active_policies", "closing_backing_assets",
        "closing_guarantee_liability", "closing_equity", "period_profit",
    )),
)


def life_sector_v3_contract_payload() -> dict[str, object]:
    """Describe future life flows and valuation without accepting or running them."""

    return {
        "schema_version": LIFE_SECTOR_V3_CONTRACT_VERSION,
        "base_contract_schema_version": LIFE_SECTOR_CONTRACT_V2_VERSION,
        "sector_taxonomy_schema_version": SECTOR_TAXONOMY_VERSION,
        "mode": "life_sector_extension_contract_read_only",
        "scope": {
            "sector_id": "life",
            "insurer_id_range": [1, VDEFMD6_INSURER_COUNT],
            "period_range": [1, 100],
            "period_unit": "IMS_model_period_not_calendar_year",
            "cohort_model": "multiple_named_cohorts_with_immutable_issue_terms",
            "policy_detail_mode": "fully_enumerated_small_case_only",
            "policy_detail_active_policy_limit": 100,
            "mode_switch_during_run": False,
            "historical_mapping_status": "unresolved",
        },
        "amounts": {
            "unit": "model_currency_unit",
            "input_representation": "decimal_string_12_integer_4_fraction_planned",
            "guaranteed_rate_representation": "decimal_string_0_to_1_with_6_fraction",
            "implicit_rounding_allowed": False,
        },
        "fields": [asdict(field) for field in LIFE_V3_FIELDS],
        "equations": [asdict(equation) for equation in LIFE_V3_EQUATIONS],
        "identities": [
            "opening_backing_assets = opening_guarantee_liability + opening_equity",
            "closing_backing_assets = closing_guarantee_liability + closing_equity",
            "deaths + maturities <= opening_active_policies",
            "closing_active_policies = opening_active_policies - deaths - maturities + new_business_policies",
            "renewal_liability_allocation <= renewal_premiums_collected",
            "new_business_liability_allocation <= new_business_premiums_collected",
            "liability_release <= opening_guarantee_liability + guarantee_accretion + renewal_liability_allocation",
            "opening_active_policies = sum(opening_cohorts.active_policies)",
            "closing_active_policies = sum(closing_cohorts.active_policies)",
            "opening_guarantee_liability = sum(opening_cohorts.guarantee_liability)",
            "closing_guarantee_liability = sum(closing_cohorts.guarantee_liability)",
        ],
        "carryover": [
            {"next_opening": f"opening_{name}", "previous_closing": f"closing_{name}"}
            for name in (
                "active_policies", "backing_assets", "guarantee_liability", "equity",
                "cohorts", "policy_values",
            )
        ],
        "period_order": [
            {**asdict(stage), "affects": list(stage.affects)}
            for stage in LIFE_V3_PERIOD_ORDER
        ],
        "cohort_ledger": {
            "fields": [
                "cohort_id", "issue_period", "issue_term_periods", "active_policies",
                "remaining_periods",
                "guaranteed_rate_per_period", "guarantee_liability",
            ],
            "cohort_id_unique_and_stable": True,
            "homogeneous_issue_term_and_guaranteed_rate_within_cohort": True,
            "issue_terms_immutable": [
                "issue_period", "issue_term_periods", "guaranteed_rate_per_period",
            ],
            "optional_immutable_issue_terms": ["maturity_benefit_at_issue"],
            "opening_and_closing_cohort_sums_required": True,
            "renewal_premium_and_allocation_per_cohort_required": True,
            "new_business_premium_and_allocation_per_new_cohort_required": True,
            "death_count_per_cohort_required": True,
            "guarantee_credit_base": "opening_cohort_guarantee_liability",
            "guarantee_credit_rounding": "round_half_even_to_0.0001_per_cohort",
            "death_release_without_policy_detail": (
                "round_half_even_to_0.0001_of_post_credit_and_renewal_allocation"
                "_cohort_liability_times_deaths_divided_by_opening_cohort_policies"
            ),
            "full_exit_releases_remaining_cohort_liability": True,
        },
        "policy_ledger": {
            "fields": [
                "policy_id", "cohort_id", "issue_term_periods", "remaining_periods",
                "guaranteed_rate_per_period", "guarantee_liability",
            ],
            "policy_id_unique_and_stable": True,
            "optional_immutable_issue_terms": ["maturity_benefit_at_issue"],
            "all_active_policies_enumerated_when_enabled": True,
            "opening_and_closing_active_policy_limit": 100,
            "cohort_liability_equals_sum_of_policy_liabilities": True,
            "guarantee_credit_rounding": "round_half_even_to_0.0001_per_policy",
            "exit_release": "sum_of_exiting_policy_guarantee_liabilities",
            "different_rounding_grains_are_not_claimed_equal": True,
        },
        "timing_and_valuation": {
            "balance_basis": "carried_book_guarantee_liability_not_statutory_or_market_value",
            "opening_and_closing_identity": "backing_assets = guarantee_liability + equity",
            "premium_timing": "existing_policy_premiums_after_guarantee_before_exits",
            "renewal_allocation_limit": "renewal_liability_allocation <= renewal_premiums_collected",
            "new_business_timing": "after_opening_policy_exits_before_closing",
            "new_business_allocation_limit": (
                "new_business_liability_allocation <= new_business_premiums_collected"
            ),
            "new_business_first_guarantee": "following_period",
            "new_business_same_period_exit_allowed": False,
            "death_before_maturity": True,
            "deaths_and_maturities_from_opening_active_only": True,
            "maturity_due": "opening_cohort_remaining_periods_equals_1_after_death",
            "death_benefit_source": "explicit_nonnegative_scenario_amount_until_product_terms",
            "death_benefit_equals_liability_release_assumed": False,
            "maturity_benefit_source": "explicit_nonnegative_scenario_or_issue_term",
            "maturity_benefit_sources_mutually_exclusive": True,
            "maturity_guarantee_floor": (
                "maturity_benefits_paid >= maturity_liability_release"
            ),
            "v2_maturity_equal_release_remains_special_case": True,
            "capital_timing": "period_end_after_exits_and_new_business",
            "capital_affects_profit_or_guarantee_liability": False,
            "capital_sector_allocation": "explicit_and_counted_once_at_insurer_total",
            "intermediate_liquidity_test": False,
            "closing_assets_nonnegative": True,
        },
        "future_source_modes": {
            "investment_result": ["explicit_scenario", "insurer_rule_on_opening_backing_assets"],
            "investment_modes_mutually_exclusive": True,
            "mortality": ["explicit_death_count", "exogenous_deterministic_rate_curve"],
            "mortality_is_policyholder_strategy": False,
            "random_draws_required": False,
            "mortality_rate_to_count_rounding": "pending_pr164",
        },
        "source_binding": {
            "opening_state": "explicit_scenario_or_prior_valid_closing",
            "cohort_issue_terms": "explicit_scenario_and_immutable_after_issue",
            "death_count": "explicit_scenario_until_pr164",
            "death_benefit": "explicit_scenario_until_product_term_decided",
            "maturity_benefit": "explicit_scenario_or_immutable_issue_term",
            "capital_movements": "explicit_scenario_and_sector_allocated",
            "investment_result": "explicit_scenario_until_pr164",
        },
        "compatibility": {
            "v1_and_v2_endpoints_unchanged": True,
            "v2_input_schema_version": "ims.life-model-balance-input.v1",
            "v2_result_schema_version": "ims.life-model-balance-result.v1",
            "v2_closed_cohort_zero_death_zero_new_business_is_special_case": True,
            "legacy_damage_sp_1_2_reused": False,
            "non_life_two_sector_total_changed": False,
        },
        "excluded": [
            "surrender", "bonus", "automatic_lapse_strategy", "statutory_balance",
            "solvency_ii_valuation", "historical_full_equality",
        ],
        "pending_decisions": [
            "v3_input_schema_and_atomic_validation_pr161",
            "policy_level_allocation_and_benefit_terms_pr163",
            "mortality_count_and_rule_assignment_pr164",
            "runner_handoff_and_budget_pr165",
        ],
        "input_validation_available": False,
        "calculation_available": False,
        "strategy_assignment_available": False,
        "runner_enabled": False,
        "writes_enabled": False,
        "simulation_performed": False,
        "statutory_or_solvency_ii_claim": False,
        "historical_full_equality_claim": False,
    }
