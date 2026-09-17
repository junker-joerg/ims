"""Versioned, explicitly sourced life workshop examples; no new model rules."""

from __future__ import annotations

from copy import deepcopy

from ims.accounting.life_period_chain import LIFE_PERIOD_CHAIN_INPUT_VERSION
from ims.accounting.life_assumptions import LIFE_ASSUMPTIONS_INPUT_VERSION
from ims.model.life_sector_v3_contract import LIFE_SECTOR_V3_CONTRACT_VERSION
from ims.model.sector_taxonomy import SECTOR_TAXONOMY_VERSION


LIFE_WORKSHOP_PRESETS_VERSION = "ims.life-workshop-presets.v1"


def _policy(policy_id: str, cohort_id: str, term: int, rate: str, liability: str) -> dict:
    return {
        "policy_id": policy_id, "cohort_id": cohort_id,
        "issue_term_periods": term, "remaining_periods": term,
        "guaranteed_rate_per_period": rate, "guarantee_liability": liability,
    }


def _flow(policy_id: str, premium: str, allocation: str, death: str, maturity: str) -> dict:
    return {
        "policy_id": policy_id,
        "renewal_premiums_collected": premium,
        "renewal_liability_allocation": allocation,
        "death_benefit_if_death": death,
        "maturity_benefit_if_due": maturity,
    }


def _base() -> dict:
    return {
        "schema_version": LIFE_PERIOD_CHAIN_INPUT_VERSION,
        "life_sector_contract_schema_version": LIFE_SECTOR_V3_CONTRACT_VERSION,
        "sector_taxonomy_schema_version": SECTOR_TAXONOMY_VERSION,
        "source_kind": "versioned_life_period_chain",
        "historical_mapping_status": "unresolved",
        "insurer_id": 1, "sector_id": "life",
        "opening": {
            "opening_active_policies": 3,
            "opening_backing_assets": "150",
            "opening_guarantee_liability": "120",
            "opening_equity": "30",
            "cohorts": [
                {"cohort_id": "A", "issue_period": 0, "issue_term_periods": 2,
                 "remaining_periods": 2, "active_policies": 2,
                 "guaranteed_rate_per_period": "0.05", "guarantee_liability": "100"},
                {"cohort_id": "B", "issue_period": 0, "issue_term_periods": 1,
                 "remaining_periods": 1, "active_policies": 1,
                 "guaranteed_rate_per_period": "0.10", "guarantee_liability": "20"},
            ],
            "policies": [
                _policy("A1", "A", 2, "0.05", "40"),
                _policy("A2", "A", 2, "0.05", "60"),
                _policy("B1", "B", 1, "0.10", "20"),
            ],
        },
        "assumptions": {
            "schema_version": LIFE_ASSUMPTIONS_INPUT_VERSION,
            "life_sector_contract_schema_version": LIFE_SECTOR_V3_CONTRACT_VERSION,
            "sector_taxonomy_schema_version": SECTOR_TAXONOMY_VERSION,
            "source_kind": "versioned_assumption_plan",
            "historical_mapping_status": "unresolved",
            "insurer_id": 1, "sector_id": "life", "period_count": 2,
            "investment": {"mode": "explicit_scenario", "periods": [
                {"period": 1, "investment_result": "5"},
                {"period": 2, "investment_result": "2"},
            ]},
            "mortality": {"mode": "explicit_death_policy_ids", "periods": [
                {"period": 1, "death_policy_ids": []},
                {"period": 2, "death_policy_ids": []},
            ]},
        },
        "periods": [
            {
                "period": 1,
                "policy_flows": [
                    _flow("A1", "5", "4", "0", "0"),
                    _flow("A2", "5", "4", "65", "0"),
                    _flow("B1", "0", "0", "0", "25"),
                ],
                "new_business": [], "operating_expense_paid": "1",
                "capital_contribution": "20", "capital_distribution": "0",
            },
            {
                "period": 2,
                "policy_flows": [
                    _flow("A1", "5", "4", "0", "60"),
                    _flow("A2", "0", "0", "0", "75"),
                ],
                "new_business": [], "operating_expense_paid": "1",
                "capital_contribution": "0", "capital_distribution": "5",
            },
        ],
    }


def life_workshop_presets_payload() -> dict[str, object]:
    base = _base()
    death = deepcopy(base)
    death["assumptions"]["mortality"]["periods"][0]["death_policy_ids"] = ["A2"]
    death["periods"][1]["policy_flows"] = [
        flow for flow in death["periods"][1]["policy_flows"]
        if flow["policy_id"] != "A2"
    ]

    new_business = deepcopy(base)
    new_business["periods"][0]["new_business"] = [{
        "cohort_id": "C", "issue_term_periods": 1,
        "guaranteed_rate_per_period": "0.20",
        "new_business_policies": 1,
        "new_business_premiums_collected": "10",
        "new_business_liability_allocation": "8",
        "policies": [{
            "policy_id": "C1", "new_business_premiums_collected": "10",
            "new_business_liability_allocation": "8",
        }],
    }]
    new_business["periods"][1]["policy_flows"].append(
        _flow("C1", "0", "0", "0", "12")
    )

    capital = deepcopy(base)
    capital["assumptions"]["investment"]["periods"][0]["investment_result"] = "0"
    capital["assumptions"]["investment"]["periods"][1]["investment_result"] = "0"
    capital["periods"][0]["capital_contribution"] = "40"

    return {
        "schema_version": LIFE_WORKSHOP_PRESETS_VERSION,
        "source_kind": "curated_ims_2x_workshop_cases",
        "historical_mapping_status": "unresolved",
        "cases": [
            {"id": "death", "name": "Todesfall", "focus": "Leistung und freigesetzte Garantie",
             "baseline": deepcopy(base), "variant": death},
            {"id": "new_business", "name": "Neugeschaeft", "focus": "Beitrag, Verpflichtung und spaeterer Ablauf",
             "baseline": deepcopy(base), "variant": new_business},
            {"id": "capital", "name": "Anlage und Kapital", "focus": "Anlageergebnis, Einlage und Eigenkapital",
             "baseline": deepcopy(base), "variant": capital},
        ],
    }
