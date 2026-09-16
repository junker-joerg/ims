"""Read-only target contract for a separate, initially closed life cohort."""

from dataclasses import asdict, dataclass

from ims.model.sector_taxonomy import SECTOR_TAXONOMY_VERSION
from ims.model.vdefmd6_population import VDEFMD6_INSURER_COUNT


LIFE_SECTOR_CONTRACT_VERSION = "ims.life-sector-contract.v1"


@dataclass(frozen=True, slots=True)
class LifeField:
    field_id: str
    kind: str
    value_type: str
    sign: str


@dataclass(frozen=True, slots=True)
class LifeEquation:
    target: str
    expression: str


@dataclass(frozen=True, slots=True)
class LifeStrategyHook:
    hook_id: str
    actor_type: str
    parameters: tuple[str, ...]
    affects: tuple[str, ...]
    constraint: str


LIFE_FIELDS = (
    LifeField("opening_active_policies", "opening_stock", "integer", "nonnegative"),
    LifeField("opening_remaining_periods", "opening_stock", "integer", "nonnegative"),
    LifeField("opening_backing_assets", "opening_stock", "amount", "nonnegative"),
    LifeField("opening_guarantee_liability", "opening_stock", "amount", "nonnegative"),
    LifeField("opening_equity", "opening_stock", "amount", "signed"),
    LifeField("guaranteed_rate_per_period", "issue_term", "decimal_rate", "nonnegative"),
    LifeField("premiums_collected", "period_flow", "amount", "nonnegative"),
    LifeField("investment_result", "period_flow", "amount", "signed"),
    LifeField("death_benefits_paid", "period_flow", "amount", "nonnegative"),
    LifeField("maturity_benefits_paid", "period_flow", "amount", "nonnegative"),
    LifeField("surrender_benefits_paid", "period_flow", "amount", "nonnegative"),
    LifeField("operating_expense_paid", "period_flow", "amount", "nonnegative"),
    LifeField("capital_contribution", "period_flow", "amount", "nonnegative"),
    LifeField("capital_distribution", "period_flow", "amount", "nonnegative"),
    LifeField("premium_liability_allocation", "period_flow", "amount", "nonnegative"),
    LifeField("guarantee_accretion", "period_flow", "amount", "nonnegative"),
    LifeField("bonus_accretion", "period_flow", "amount", "nonnegative"),
    LifeField("liability_release", "period_flow", "amount", "nonnegative"),
    LifeField("deaths", "period_flow", "integer", "nonnegative"),
    LifeField("maturities", "period_flow", "integer", "nonnegative"),
    LifeField("surrenders", "period_flow", "integer", "nonnegative"),
    LifeField("period_profit", "derived_flow", "amount", "signed"),
    LifeField("closing_active_policies", "closing_stock", "integer", "nonnegative"),
    LifeField("closing_remaining_periods", "closing_stock", "integer", "nonnegative"),
    LifeField("closing_backing_assets", "closing_stock", "amount", "nonnegative"),
    LifeField("closing_guarantee_liability", "closing_stock", "amount", "nonnegative"),
    LifeField("closing_equity", "closing_stock", "amount", "signed"),
)

LIFE_EQUATIONS = (
    LifeEquation(
        "closing_active_policies",
        "opening_active_policies - deaths - maturities - surrenders",
    ),
    LifeEquation(
        "closing_backing_assets",
        "opening_backing_assets + premiums_collected + investment_result"
        " + capital_contribution - death_benefits_paid - maturity_benefits_paid"
        " - surrender_benefits_paid - operating_expense_paid - capital_distribution",
    ),
    LifeEquation(
        "closing_guarantee_liability",
        "opening_guarantee_liability + premium_liability_allocation"
        " + guarantee_accretion + bonus_accretion - liability_release",
    ),
    LifeEquation(
        "period_profit",
        "premiums_collected + investment_result - death_benefits_paid"
        " - maturity_benefits_paid - surrender_benefits_paid - operating_expense_paid"
        " - (closing_guarantee_liability - opening_guarantee_liability)",
    ),
    LifeEquation(
        "closing_equity",
        "opening_equity + period_profit + capital_contribution - capital_distribution",
    ),
)

LIFE_IDENTITIES = (
    "opening_backing_assets = opening_guarantee_liability + opening_equity",
    "closing_backing_assets = closing_guarantee_liability + closing_equity",
    "deaths + maturities + surrenders <= opening_active_policies",
    "premium_liability_allocation <= premiums_collected",
    "opening_remaining_periods >= 1 when opening_active_policies > 0",
    "maturities = 0 before the final contract period",
    "closing_active_policies = 0 at the end of the final contract period",
    "closing_remaining_periods = opening_remaining_periods - 1 when closing_active_policies > 0",
    "closing_remaining_periods = 0 when closing_active_policies = 0",
)

LIFE_CARRYOVER = (
    ("opening_active_policies", "closing_active_policies"),
    ("opening_remaining_periods", "closing_remaining_periods"),
    ("opening_backing_assets", "closing_backing_assets"),
    ("opening_guarantee_liability", "closing_guarantee_liability"),
    ("opening_equity", "closing_equity"),
)

LIFE_STRATEGY_HOOKS = (
    LifeStrategyHook(
        "life_insurer_bonus_crediting", "insurer", ("bonus_rate_per_period",),
        ("bonus_accretion",), "cannot_reduce_guaranteed_rate_at_issue",
    ),
    LifeStrategyHook(
        "life_policyholder_surrender", "policyholder", ("surrender_trigger",),
        ("surrenders", "surrender_benefits_paid", "liability_release"),
        "decision_only_for_active_policies",
    ),
)


def life_sector_contract_payload() -> dict[str, object]:
    """Describe life-specific state and strategy boundaries without computing a value."""

    return {
        "schema_version": LIFE_SECTOR_CONTRACT_VERSION,
        "sector_taxonomy_schema_version": SECTOR_TAXONOMY_VERSION,
        "mode": "life_sector_contract_read_only",
        "scope": {
            "sector_id": "life",
            "model_family": "life",
            "insurer_id_range": [1, VDEFMD6_INSURER_COUNT],
            "period_range": [1, 100],
            "period_unit": "IMS_model_period_not_calendar_year",
            "initial_cohort_model": "one_closed_homogeneous_cohort",
            "new_business_enabled": False,
            "historical_mapping_status": "unresolved",
        },
        "amounts": {
            "unit": "model_currency_unit",
            "numeric_representation": "decimal_string_12_integer_4_fraction_planned",
            "implicit_rounding_allowed": False,
            "guarantee_credit_rounding": "pending_pr159",
        },
        "fields": [asdict(field) for field in LIFE_FIELDS],
        "equations": [asdict(equation) for equation in LIFE_EQUATIONS],
        "identities": list(LIFE_IDENTITIES),
        "immutable_issue_terms": ["guaranteed_rate_per_period"],
        "carryover": [
            {"next_opening": opening, "previous_closing": closing}
            for opening, closing in LIFE_CARRYOVER
        ],
        "strategy_hooks": [
            {
                **asdict(hook),
                "parameters": list(hook.parameters),
                "affects": list(hook.affects),
            }
            for hook in LIFE_STRATEGY_HOOKS
        ],
        "source_binding": {
            "opening_state": "explicit_scenario_required",
            "issue_term": "explicit_scenario_required_and_fixed_after_issue",
            "period_flows": "explicit_scenario_until_separately_implemented",
            "legacy_sp_1_2_reused": False,
            "legacy_rk_1_2_reused": False,
            "non_life_rule_catalog_reused": False,
        },
        "pending_decisions": [
            "premium_and_guarantee_credit_timing",
            "guarantee_credit_base_and_rounding",
            "liability_release_by_exit_reason",
            "strategy_parameter_semantics_and_assignment",
        ],
        "calculation_available": False,
        "strategy_assignment_available": False,
        "snapshot_materialization_enabled": False,
        "writes_enabled": False,
        "execution_enabled": False,
        "simulation_performed": False,
        "statutory_or_solvency_ii_claim": False,
        "historical_full_equality_claim": False,
    }
