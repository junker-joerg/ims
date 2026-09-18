"""Read-only provenance and terminology boundary for the planned capital view."""

from ims.accounting.four_sector_balance import FOUR_SECTOR_BALANCE_RESULT_VERSION, SECTOR_IDS


SOLVENCY_SCOPE_CONTRACT_VERSION = "ims.solvency-scope-contract.v1"


def solvency_scope_contract_payload() -> dict[str, object]:
    """Describe candidate model data and missing regulatory bridges, not amounts."""

    return {
        "schema_version": SOLVENCY_SCOPE_CONTRACT_VERSION,
        "mode": "read_only_scope_and_sources",
        "reference_checked_on": "2026-09-18",
        "legal_version": {
            "jurisdiction": "EU",
            "conceptual_reference": "2009/138/EC_consolidated_2025-01-17",
            "pending_review": "2025/2_applies_from_2027-01-30",
            "level_2_formula_version_selected": False,
            "reporting_reference_date_selected": False,
            "ims_period_is_calendar_year": False,
            "applicable_rule_set_for_calculation_selected": False,
        },
        "sources": [
            {
                "source_id": "directive_2025",
                "url": "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A02009L0138-20250117",
                "role": "conceptual_reference_not_formula_lock",
            },
            {
                "source_id": "valuation",
                "url": "https://www.eiopa.europa.eu/rulebook/solvency-ii-single-rulebook/article-2158_en",
                "role": "article_75_valuation",
            },
            {
                "source_id": "technical_provisions",
                "url": "https://www.eiopa.europa.eu/rulebook/solvency-ii-single-rulebook/article-2160_en",
                "role": "article_77_best_estimate_and_risk_margin",
            },
            {
                "source_id": "basic_own_funds",
                "url": "https://www.eiopa.europa.eu/rulebook/solvency-ii-single-rulebook/article-2176_en",
                "role": "article_88_basic_own_funds",
            },
            {
                "source_id": "eligible_own_funds",
                "url": "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A02009L0138-20250117",
                "role": "article_98_eligibility_not_implemented",
            },
            {
                "source_id": "scr",
                "url": "https://www.eiopa.europa.eu/rulebook/solvency-ii-single-rulebook/article-2188_en",
                "role": "article_101_scr_scope_not_implemented_formula",
            },
            {
                "source_id": "scr_structure",
                "url": "https://www.eiopa.europa.eu/rulebook/solvency-ii-single-rulebook/article-2190_en",
                "role": "article_103_standard_formula_structure",
            },
            {
                "source_id": "mcr",
                "url": "https://www.eiopa.europa.eu/rulebook/solvency-ii-single-rulebook/article-2216_en",
                "role": "article_129_mcr_not_implemented_formula",
            },
            {
                "source_id": "level2",
                "url": "https://www.eiopa.europa.eu/browse/regulation-and-policy/solvency-ii_en",
                "role": "delegated_regulation_2015_35_version_open_for_calculation",
            },
            {
                "source_id": "review_2027",
                "url": "https://eur-lex.europa.eu/eli/dir/2025/2/oj/eng",
                "role": "future_framework_not_auto_applied",
            },
        ],
        "model_source": {
            "result_schema_version": FOUR_SECTOR_BALANCE_RESULT_VERSION,
            "sector_ids": list(SECTOR_IDS),
            "grain": ["insurer_id", "scenario_id", "variant_id", "period"],
            "candidate_fields": ["closing_assets", "closing_liabilities", "closing_equity"],
            "amount_unit": "model_currency_unit_not_eur",
            "historical_sector_mapping": "unresolved",
            "regulatory_valuation_status": "not_available",
        },
        "terminology": [
            {"term_id": "model_equity", "status": "model_only", "source_id": "four_sector_balance"},
            {"term_id": "solvency_assets_and_liabilities", "status": "not_available", "source_id": "valuation"},
            {"term_id": "technical_provisions", "status": "not_available", "source_id": "technical_provisions"},
            {"term_id": "basic_own_funds", "status": "not_available", "source_id": "basic_own_funds"},
            {"term_id": "eligible_own_funds", "status": "not_available", "source_id": "eligible_own_funds"},
            {"term_id": "scr", "status": "not_available", "source_id": "scr"},
            {"term_id": "mcr", "status": "not_available", "source_id": "mcr"},
            {"term_id": "coverage_ratio", "status": "not_available", "source_id": "scr"},
        ],
        "required_bridges": [
            {"bridge_id": "valuation_and_own_funds", "planned_pr": "PR172", "status": "missing"},
            {"bridge_id": "risk_exposures_and_shocks", "planned_pr": "PR173", "status": "missing"},
            {"bridge_id": "underwriting_and_market_modules", "planned_pr": "PR174", "status": "missing"},
            {"bridge_id": "counterparty_operational_and_aggregation", "planned_pr": "PR175", "status": "missing"},
            {"bridge_id": "model_capital_metrics", "planned_pr": "PR176", "status": "missing"},
            {"bridge_id": "validation_and_presentation", "planned_pr": "PR177-178", "status": "missing"},
        ],
        "calculation_enabled": False,
        "writes_enabled": False,
        "runner_enabled": False,
        "statutory_balance_claim": False,
        "regulatory_solvency_claim": False,
        "compliance_decision_enabled": False,
        "historical_full_equality_claim": False,
    }
