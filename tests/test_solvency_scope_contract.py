import json

from ims.accounting.four_sector_balance import FOUR_SECTOR_BALANCE_RESULT_VERSION, SECTOR_IDS
from ims.model.solvency_scope_contract import (
    SOLVENCY_SCOPE_CONTRACT_VERSION,
    solvency_scope_contract_payload,
)


def test_scope_contract_names_sources_and_never_promotes_model_equity() -> None:
    payload = json.loads(json.dumps(solvency_scope_contract_payload()))

    assert payload["schema_version"] == SOLVENCY_SCOPE_CONTRACT_VERSION
    assert payload["reference_checked_on"] == "2026-09-18"
    assert payload["model_source"]["result_schema_version"] == FOUR_SECTOR_BALANCE_RESULT_VERSION
    assert payload["model_source"]["sector_ids"] == list(SECTOR_IDS)
    assert payload["model_source"]["candidate_fields"] == [
        "closing_assets", "closing_liabilities", "closing_equity",
    ]
    assert payload["model_source"]["amount_unit"] == "model_currency_unit_not_eur"
    assert payload["model_source"]["regulatory_valuation_status"] == "not_available"
    terms = {item["term_id"]: item for item in payload["terminology"]}
    assert terms["model_equity"]["status"] == "model_only"
    assert {term for term, item in terms.items() if item["status"] == "not_available"} == {
        "solvency_assets_and_liabilities", "technical_provisions", "basic_own_funds",
        "eligible_own_funds", "scr", "mcr", "coverage_ratio",
    }
    sources = {item["source_id"]: item for item in payload["sources"]}
    assert len(sources) == len(payload["sources"])
    assert {item["source_id"] for item in payload["terminology"] if item["source_id"] != "four_sector_balance"} <= set(sources)
    assert all(item["url"].startswith("https://") for item in sources.values())


def test_no_legal_regime_or_capital_result_is_implicitly_selected() -> None:
    payload = solvency_scope_contract_payload()
    legal = payload["legal_version"]
    assert legal["conceptual_reference"] == "2009/138/EC_consolidated_2025-01-17"
    assert legal["pending_review"] == "2025/2_applies_from_2027-01-30"
    for field in (
        "level_2_formula_version_selected", "reporting_reference_date_selected",
        "ims_period_is_calendar_year", "applicable_rule_set_for_calculation_selected",
    ):
        assert legal[field] is False
    assert {item["planned_pr"] for item in payload["required_bridges"]} == {
        "PR172", "PR173", "PR174", "PR175", "PR176", "PR177-178",
    }
    assert all(item["status"] == "missing" for item in payload["required_bridges"])
    for field in (
        "calculation_enabled", "writes_enabled", "runner_enabled", "statutory_balance_claim",
        "regulatory_solvency_claim", "compliance_decision_enabled", "historical_full_equality_claim",
    ):
        assert payload[field] is False
    assert "scr_amount" not in payload
    assert "mcr_amount" not in payload
    assert "coverage_ratio" not in payload
    assert solvency_scope_contract_payload() == payload
