import json
from dataclasses import FrozenInstanceError

import pytest

from ims.accounting.model_balance_contract import (
    BALANCE_EQUATIONS,
    BALANCE_FIELDS,
    MODEL_BALANCE_CONTRACT_VERSION,
    model_balance_contract_payload,
)


def test_model_balance_contract_is_complete_but_does_not_calculate() -> None:
    payload = json.loads(json.dumps(model_balance_contract_payload()))

    assert payload["schema_version"] == MODEL_BALANCE_CONTRACT_VERSION
    assert payload["scope"]["grain"] == ["insurer_id", "sector_id", "period"]
    assert payload["scope"]["sector_ids"] == ["motor", "property_liability"]
    assert payload["scope"]["historical_sector_mapping"] == "unresolved"
    assert payload["amounts"]["numeric_representation"] == "to_be_decided_before_pr156"
    assert payload["balance_calculation_available"] is False
    assert payload["writes_enabled"] is False
    assert payload["execution_enabled"] is False
    assert payload["simulation_performed"] is False
    assert payload["historical_full_equality_claim"] is False

    field_ids = [field["field_id"] for field in payload["fields"]]
    assert len(field_ids) == len(set(field_ids)) == 14
    assert {equation["target"] for equation in payload["equations"]} == {
        "period_profit", "closing_cash", "closing_claim_liability", "closing_equity"
    }
    assert {equation["target"]: equation["expression"] for equation in payload["equations"]} == {
        "period_profit": "premium_income + investment_income - claims_incurred - operating_expense",
        "closing_cash": "opening_cash + premium_income + investment_income + capital_contribution - claims_paid - operating_expense - capital_distribution",
        "closing_claim_liability": "opening_claim_liability + claims_incurred - claims_paid",
        "closing_equity": "opening_equity + period_profit + capital_contribution - capital_distribution",
    }
    assert payload["identities"] == [
        "opening_cash = opening_claim_liability + opening_equity",
        "closing_cash = closing_claim_liability + closing_equity",
    ]
    assert payload["carryover"] == [
        {"next_opening": "opening_cash", "previous_closing": "closing_cash"},
        {"next_opening": "opening_claim_liability", "previous_closing": "closing_claim_liability"},
        {"next_opening": "opening_equity", "previous_closing": "closing_equity"},
    ]


def test_contract_preserves_historical_and_accounting_boundaries() -> None:
    payload = model_balance_contract_payload()
    assert payload["source_binding"]["legacy_reserve_is_balance_item"] is False
    assert payload["source_binding"]["legacy_advertising_is_automatically_expensed"] is False
    assert payload["source_binding"]["premium_and_claim_sources"] == "reconcile_before_binding_in_pr156"
    assert payload["source_binding"]["opening_stocks_and_missing_flows"] == "explicit_scenario_inputs_required"
    assert {"life", "health", "solvency_ii", "statutory_balance_sheet"} <= set(payload["exclusions"])
    assert all(field.sign in {"signed", "nonnegative"} for field in BALANCE_FIELDS)
    assert len(BALANCE_EQUATIONS) == 4
    with pytest.raises(FrozenInstanceError):
        BALANCE_FIELDS[0].field_id = "legacy_reserve"  # type: ignore[misc]
