"""Read-only target contract for a separate, initially closed health portfolio."""

from dataclasses import asdict, dataclass

from ims.model.sector_taxonomy import SECTOR_TAXONOMY_VERSION
from ims.model.vdefmd6_population import VDEFMD6_INSURER_COUNT


HEALTH_SECTOR_CONTRACT_VERSION = "ims.health-sector-contract.v1"


@dataclass(frozen=True, slots=True)
class HealthField:
    field_id: str
    kind: str
    value_type: str
    sign: str


@dataclass(frozen=True, slots=True)
class HealthEquation:
    target: str
    expression: str


@dataclass(frozen=True, slots=True)
class HealthStrategyHook:
    hook_id: str
    actor_type: str
    parameters: tuple[str, ...]
    affects: tuple[str, ...]
    constraint: str


HEALTH_FIELDS = (
    HealthField("opening_active_policies", "opening_stock", "integer", "nonnegative"),
    HealthField("opening_cash", "opening_stock", "amount", "nonnegative"),
    HealthField("opening_benefit_liability", "opening_stock", "amount", "nonnegative"),
    HealthField("opening_equity", "opening_stock", "amount", "signed"),
    HealthField("premiums_collected", "period_flow", "amount", "nonnegative"),
    HealthField("benefits_incurred", "period_flow", "amount", "nonnegative"),
    HealthField("benefits_paid", "period_flow", "amount", "nonnegative"),
    HealthField("investment_result", "period_flow", "amount", "signed"),
    HealthField("operating_expense_paid", "period_flow", "amount", "nonnegative"),
    HealthField("capital_contribution", "period_flow", "amount", "nonnegative"),
    HealthField("capital_distribution", "period_flow", "amount", "nonnegative"),
    HealthField("period_profit", "derived_flow", "amount", "signed"),
    HealthField("closing_active_policies", "closing_stock", "integer", "nonnegative"),
    HealthField("closing_cash", "closing_stock", "amount", "nonnegative"),
    HealthField("closing_benefit_liability", "closing_stock", "amount", "nonnegative"),
    HealthField("closing_equity", "closing_stock", "amount", "signed"),
)

HEALTH_EQUATIONS = (
    HealthEquation("closing_active_policies", "opening_active_policies"),
    HealthEquation(
        "closing_benefit_liability",
        "opening_benefit_liability + benefits_incurred - benefits_paid",
    ),
    HealthEquation(
        "closing_cash",
        "opening_cash + premiums_collected + investment_result"
        " + capital_contribution - benefits_paid - operating_expense_paid"
        " - capital_distribution",
    ),
    HealthEquation(
        "period_profit",
        "premiums_collected + investment_result - benefits_incurred"
        " - operating_expense_paid",
    ),
    HealthEquation(
        "closing_equity",
        "opening_equity + period_profit + capital_contribution - capital_distribution",
    ),
)

HEALTH_IDENTITIES = (
    "opening_cash = opening_benefit_liability + opening_equity",
    "closing_cash = closing_benefit_liability + closing_equity",
    "benefits_paid <= opening_benefit_liability + benefits_incurred",
    "premiums_collected = 0 when opening_active_policies = 0",
    "benefits_incurred = 0 when opening_active_policies = 0",
)

HEALTH_CARRYOVER = (
    ("opening_active_policies", "closing_active_policies"),
    ("opening_cash", "closing_cash"),
    ("opening_benefit_liability", "closing_benefit_liability"),
    ("opening_equity", "closing_equity"),
)

HEALTH_STRATEGY_HOOKS = (
    HealthStrategyHook(
        "health_insurer_pricing", "insurer", ("premium_per_policy_per_period",),
        ("premiums_collected",),
        "future_only_explicit_price_and_active_stock_no_repricing_prior_periods",
    ),
    HealthStrategyHook(
        "health_policyholder_switching", "policyholder", ("switching_threshold",),
        ("closing_active_policies",),
        "future_only_not_applicable_to_initial_closed_portfolio",
    ),
)


def health_sector_contract_payload() -> dict[str, object]:
    """Describe health-specific flows without validating, storing or running them."""

    return {
        "schema_version": HEALTH_SECTOR_CONTRACT_VERSION,
        "sector_taxonomy_schema_version": SECTOR_TAXONOMY_VERSION,
        "mode": "health_sector_contract_read_only",
        "scope": {
            "sector_id": "health",
            "model_family": "health",
            "insurer_id_range": [1, VDEFMD6_INSURER_COUNT],
            "period_range": [1, 100],
            "period_unit": "IMS_model_period_not_calendar_year",
            "initial_portfolio": "one_closed_homogeneous_portfolio",
            "new_business_enabled": False,
            "exits_enabled": False,
            "historical_mapping_status": "unresolved",
        },
        "amounts": {
            "unit": "model_currency_unit",
            "numeric_representation": "decimal_string_12_integer_4_fraction_planned",
            "implicit_rounding_allowed": False,
        },
        "fields": [asdict(field) for field in HEALTH_FIELDS],
        "equations": [asdict(equation) for equation in HEALTH_EQUATIONS],
        "identities": list(HEALTH_IDENTITIES),
        "carryover": [
            {"next_opening": opening, "previous_closing": closing}
            for opening, closing in HEALTH_CARRYOVER
        ],
        "timing_and_valuation": {
            "premium": "collected_and_earned_in_same_model_period",
            "benefit_incurred": "recognized_in_current_period_profit_and_liability",
            "benefit_paid": "discharges_opening_or_current_benefit_liability_not_second_expense",
            "investment_result": "earned_and_collected_in_same_model_period",
            "operating_expense": "incurred_and_paid_in_same_model_period",
            "capital_movement": "separate_from_period_profit_and_benefit_liability",
            "opening_and_closing_identity": "cash = benefit_liability + equity",
            "benefit_liability_basis": "incurred_unpaid_benefits_not_ageing_reserve",
        },
        "strategy_hooks": [
            {**asdict(hook), "parameters": list(hook.parameters), "affects": list(hook.affects)}
            for hook in HEALTH_STRATEGY_HOOKS
        ],
        "source_binding": {
            "opening_state": "explicit_scenario_or_prior_valid_closing",
            "premiums_and_benefit_flows": "explicit_scenario_only_until_separate_rule_contract",
            "investment_expense_and_capital": "explicit_scenario_only",
            "benefit_incurred_is_insurer_strategy": False,
            "legacy_sp_1_2_reused": False,
            "legacy_rk_1_2_reused": False,
            "non_life_rule_catalog_reused": False,
        },
        "excluded": [
            "ageing_reserve", "tariff_and_age_structure", "morbidity_or_treatment_model",
            "receivables", "reinsurance", "statutory_balance_sheet", "solvency_ii_valuation",
        ],
        "pending_decisions": [
            "pr169_input_schema_and_atomic_balance_validation",
            "new_business_exit_and_policyholder_switching_timing",
            "insurer_pricing_source_and_parameter_assignment",
            "ageing_reserve_and_product_valuation_separate_contract",
            "pr170_cross_sector_capital_allocation_and_consolidation",
        ],
        "input_validation_available": False,
        "calculation_available": False,
        "strategy_assignment_available": False,
        "snapshot_materialization_enabled": False,
        "runner_enabled": False,
        "writes_enabled": False,
        "simulation_performed": False,
        "statutory_or_solvency_ii_claim": False,
        "historical_full_equality_claim": False,
    }
