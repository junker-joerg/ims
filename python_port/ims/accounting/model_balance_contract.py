"""Read-only contract for a simplified insurer-sector model balance."""

from dataclasses import asdict, dataclass

from ims.model.sector_taxonomy import SECTOR_DEFINITIONS, SECTOR_TAXONOMY_VERSION


MODEL_BALANCE_CONTRACT_VERSION = "ims.insurer-model-balance-contract.v1"


@dataclass(frozen=True, slots=True)
class BalanceField:
    field_id: str
    kind: str
    sign: str


@dataclass(frozen=True, slots=True)
class BalanceEquation:
    target: str
    expression: str
    purpose: str


BALANCE_FIELDS = (
    BalanceField("opening_cash", "opening_stock", "nonnegative"),
    BalanceField("opening_claim_liability", "opening_stock", "nonnegative"),
    BalanceField("opening_equity", "opening_stock", "signed"),
    BalanceField("premium_income", "period_flow", "nonnegative"),
    BalanceField("investment_income", "period_flow", "signed"),
    BalanceField("claims_incurred", "period_flow", "nonnegative"),
    BalanceField("claims_paid", "period_flow", "nonnegative"),
    BalanceField("operating_expense", "period_flow", "nonnegative"),
    BalanceField("capital_contribution", "period_flow", "nonnegative"),
    BalanceField("capital_distribution", "period_flow", "nonnegative"),
    BalanceField("period_profit", "derived_flow", "signed"),
    BalanceField("closing_cash", "closing_stock", "nonnegative"),
    BalanceField("closing_claim_liability", "closing_stock", "nonnegative"),
    BalanceField("closing_equity", "closing_stock", "signed"),
)

BALANCE_EQUATIONS = (
    BalanceEquation(
        "period_profit",
        "premium_income + investment_income - claims_incurred - operating_expense",
        "income_statement",
    ),
    BalanceEquation(
        "closing_cash",
        "opening_cash + premium_income + investment_income + capital_contribution"
        " - claims_paid - operating_expense - capital_distribution",
        "cash_movement",
    ),
    BalanceEquation(
        "closing_claim_liability",
        "opening_claim_liability + claims_incurred - claims_paid",
        "claims_movement",
    ),
    BalanceEquation(
        "closing_equity",
        "opening_equity + period_profit + capital_contribution - capital_distribution",
        "equity_movement",
    ),
)

BALANCE_IDENTITIES = (
    "opening_cash = opening_claim_liability + opening_equity",
    "closing_cash = closing_claim_liability + closing_equity",
)

BALANCE_CARRYOVER = (
    ("opening_cash", "closing_cash"),
    ("opening_claim_liability", "closing_claim_liability"),
    ("opening_equity", "closing_equity"),
)


def model_balance_contract_payload() -> dict[str, object]:
    """Describe planned inputs and invariants; never materialize a balance."""

    return {
        "schema_version": MODEL_BALANCE_CONTRACT_VERSION,
        "sector_taxonomy_schema_version": SECTOR_TAXONOMY_VERSION,
        "mode": "insurer_model_balance_contract_read_only",
        "scope": {
            "grain": ["insurer_id", "sector_id", "period"],
            "sector_ids": [
                sector.sector_id
                for sector in SECTOR_DEFINITIONS
                if sector.sector_id in {"motor", "property_liability"}
            ],
            "historical_sector_mapping": "unresolved",
            "inter_sector_capital_allocation": "explicit_input_required",
        },
        "amounts": {
            "unit": "model_currency_unit",
            "rounding": "none_implicit",
            "numeric_representation": "to_be_decided_before_pr156",
        },
        "fields": [asdict(field) for field in BALANCE_FIELDS],
        "equations": [asdict(equation) for equation in BALANCE_EQUATIONS],
        "identities": list(BALANCE_IDENTITIES),
        "carryover": [
            {"next_opening": opening, "previous_closing": closing}
            for opening, closing in BALANCE_CARRYOVER
        ],
        "simplifications": [
            "premiums_earned_and_collected_in_same_period",
            "investment_income_earned_and_collected_in_same_period",
            "operating_expense_incurred_and_paid_in_same_period",
            "cash_only_asset_and_claims_only_liability",
        ],
        "source_binding": {
            "legacy_reserve_is_balance_item": False,
            "legacy_advertising_is_automatically_expensed": False,
            "premium_and_claim_sources": "reconcile_before_binding_in_pr156",
            "opening_stocks_and_missing_flows": "explicit_scenario_inputs_required",
        },
        "exclusions": [
            "receivables", "unearned_premiums", "investment_assets", "reinsurance",
            "tax", "life", "health", "solvency_ii", "statutory_balance_sheet",
        ],
        "balance_calculation_available": False,
        "writes_enabled": False,
        "execution_enabled": False,
        "simulation_performed": False,
        "historical_full_equality_claim": False,
    }
