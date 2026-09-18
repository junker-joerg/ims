import copy
from decimal import Decimal, localcontext

import pytest

from ims.accounting.four_sector_balance import SECTOR_IDS, build_four_sector_balance
from ims.accounting.solvency_model_balance import (
    SOLVENCY_MODEL_BALANCE_INPUT_VERSION,
    SOLVENCY_MODEL_BALANCE_RESULT_VERSION,
    build_solvency_model_balance,
    solvency_model_balance_contract_payload,
)
from ims.model.solvency_scope_contract import SOLVENCY_SCOPE_CONTRACT_VERSION
from tests.test_four_sector_balance import _hundred, _input as four_sector_input


AMOUNT_FIELDS = (
    "closing_assets", "closing_liabilities", "closing_equity", "asset_delta",
    "liability_delta", "adjusted_model_assets", "adjusted_model_liabilities",
    "model_own_funds_proxy", "proxy_change_vs_equity",
)


def _input() -> dict:
    adjustments = (
        ("motor", "10", "2"),
        ("property_liability", "-5", "1"),
        ("life", "0", "-3"),
        ("health", "4", "0"),
    )
    return {
        "schema_version": SOLVENCY_MODEL_BALANCE_INPUT_VERSION,
        "scope_contract_schema_version": SOLVENCY_SCOPE_CONTRACT_VERSION,
        "model_only_confirmed": True,
        "four_sector_input": four_sector_input(),
        "checkpoint": {
            "model_period": 1,
            "reference_date": "2026-09-18",
            "date_linkage": "scenario_declared",
        },
        "adjustments": [
            {
                "sector_id": sector_id,
                "asset_delta": asset_delta,
                "liability_delta": liability_delta,
                "assumption_id": f"seminar_{sector_id}",
                "assumption_note": f"Modellannahme fuer {sector_id}",
            }
            for sector_id, asset_delta, liability_delta in adjustments
        ],
    }


def test_model_bridge_is_exact_reproducible_and_traced_to_all_four_sectors() -> None:
    value = _input()
    before = copy.deepcopy(value)
    with localcontext() as context:
        context.prec = 3
        report = build_solvency_model_balance(value).to_dict()
    source = build_four_sector_balance(value["four_sector_input"]).to_dict()
    assert value == before
    assert report == build_solvency_model_balance(value).to_dict()
    assert report["schema_version"] == SOLVENCY_MODEL_BALANCE_RESULT_VERSION
    assert report["valid"] is True
    assert report["insurer_id"] == 1
    assert report["scenario_id"] == "seminar_health_01"
    assert report["variant_id"] == "baseline"
    assert report["checkpoint"] == value["checkpoint"]
    assert report["amount_unit"] == "model_currency_unit_not_eur"
    assert report["source_result_schema_version"] == source["schema_version"]
    assert report["source_scenario_linkage"] == "declared_non_life_and_life_verified_health"
    assert report["historical_mapping_status"] == "unresolved"
    assert [row["sector_id"] for row in report["sector_rows"]] == list(SECTOR_IDS)
    assert len(report["source_content_digest"]) == len(report["input_digest"]) == len(report["content_digest"]) == 64
    assert report["source_content_digest"] == source["content_digest"]
    assert report["source_input_digest"] == source["input_digest"]
    assert report["total_row"] == {
        "closing_assets": "453.0000",
        "closing_liabilities": "143.0000",
        "closing_equity": "310.0000",
        "asset_delta": "9.0000",
        "liability_delta": "0.0000",
        "adjusted_model_assets": "462.0000",
        "adjusted_model_liabilities": "143.0000",
        "model_own_funds_proxy": "319.0000",
        "proxy_change_vs_equity": "9.0000",
    }
    for field in AMOUNT_FIELDS:
        assert Decimal(report["total_row"][field]) == sum(
            Decimal(row[field]) for row in report["sector_rows"]
        )
    for index, row in enumerate(report["sector_rows"]):
        source_row = source["sectors"][index]["rows"][0]
        for field in ("closing_assets", "closing_liabilities", "closing_equity"):
            assert row[field] == source_row[field]
        assert row["assumption_id"] == value["adjustments"][index]["assumption_id"]
        assert Decimal(row["model_own_funds_proxy"]) == (
            Decimal(row["closing_equity"]) + Decimal(row["proxy_change_vs_equity"])
        )
    assert report["valuation_status"] == "model_only_not_regulatory"
    for flag in (
        "writes_performed", "runner_invoked", "statutory_balance_claim",
        "regulatory_own_funds_claim", "scr_or_mcr_calculated",
        "compliance_decision_enabled", "historical_full_equality_claim",
    ):
        assert report[flag] is False
    assert "scr" not in report and "mcr" not in report and "coverage_ratio" not in report


def test_zero_adjustment_is_still_only_a_model_proxy_and_negative_proxy_is_visible() -> None:
    value = _input()
    for adjustment in value["adjustments"]:
        adjustment["asset_delta"] = "0"
        adjustment["liability_delta"] = "0"
    zero = build_solvency_model_balance(value).to_dict()
    assert zero["total_row"]["model_own_funds_proxy"] == zero["total_row"]["closing_equity"]
    assert zero["regulatory_own_funds_claim"] is False

    value = _input()
    for adjustment in value["adjustments"]:
        adjustment["liability_delta"] = "1000"
    negative = build_solvency_model_balance(value).to_dict()
    assert negative["valid"] is True
    assert Decimal(negative["total_row"]["model_own_funds_proxy"]) < 0


@pytest.mark.parametrize(("mutation", "code"), [
    (lambda value: value.update({"schema_version": "wrong"}), "contract_value_mismatch"),
    (lambda value: value.update({"scope_contract_schema_version": "wrong"}), "scope_mismatch"),
    (lambda value: value.update({"model_only_confirmed": False}), "model_boundary_unconfirmed"),
    (lambda value: value["checkpoint"].update({"model_period": 3}), "period_out_of_range"),
    (lambda value: value["checkpoint"].update({"reference_date": "2026-02-30"}), "date_invalid"),
    (lambda value: value["checkpoint"].update({"date_linkage": "calendar_year"}), "linkage_invalid"),
    (lambda value: value["adjustments"].pop(), "sector_count_invalid"),
    (lambda value: value["adjustments"][1].update({"sector_id": "motor"}), "sector_duplicate"),
    (lambda value: value["adjustments"][0].update({"asset_delta": "1e3"}), "decimal_string_required"),
    (lambda value: value["adjustments"][0].update({"asset_delta": "-99999"}), "negative_adjusted_stock"),
    (lambda value: value["adjustments"][0].update({"assumption_note": " "}), "note_invalid"),
    (lambda value: value["four_sector_input"]["sectors"]["life"].update({"insurer_id": 2}), "insurer_mismatch"),
])
def test_invalid_input_returns_no_partial_capital_bridge(mutation, code: str) -> None:
    value = _input()
    mutation(value)
    result = build_solvency_model_balance(value).to_dict()
    assert result["valid"] is False
    assert result["sector_rows"] == []
    assert result["total_row"] is None
    assert result["source_content_digest"] is None
    assert result["content_digest"] is None
    assert code in {issue["code"] for issue in result["issues"]}


def test_checkpoint_can_select_a_later_period_without_changing_source_history() -> None:
    value = _input()
    value["four_sector_input"] = _hundred()
    value["checkpoint"]["model_period"] = 100
    value["checkpoint"]["reference_date"] = "2034-12-31"
    for adjustment in value["adjustments"]:
        adjustment["asset_delta"] = "0"
        adjustment["liability_delta"] = "0"
    result = build_solvency_model_balance(value).to_dict()
    source = build_four_sector_balance(value["four_sector_input"]).to_dict()
    assert result["valid"] is True, result["issues"]
    assert result["source_content_digest"] == source["content_digest"]
    assert result["total_row"]["closing_assets"] == source["total_rows"][99]["closing_assets"]
    assert result["checkpoint"]["model_period"] == 100
    assert result["checkpoint"]["reference_date"] == "2034-12-31"


def test_contract_does_not_promise_legal_capital_values() -> None:
    contract = solvency_model_balance_contract_payload()
    assert contract["scope_contract_schema_version"] == SOLVENCY_SCOPE_CONTRACT_VERSION
    assert contract["source_result_schema_version"] == "ims.four-sector-balance-result.v1"
    assert contract["sector_ids"] == list(SECTOR_IDS)
    assert contract["model_calculation_enabled"] is True
    assert contract["regulatory_own_funds_claim"] is False
    assert contract["scr_or_mcr_calculated"] is False
