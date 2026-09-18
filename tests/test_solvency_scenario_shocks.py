import copy
from decimal import Decimal, localcontext

import pytest

from ims.accounting.solvency_model_balance import build_solvency_model_balance
from ims.accounting.solvency_scenario_shocks import (
    SOLVENCY_SHOCK_INPUT_VERSION,
    SOLVENCY_SHOCK_RESULT_VERSION,
    build_solvency_scenario_shocks,
    solvency_scenario_shocks_contract_payload,
)
from tests.test_solvency_model_balance import _input as model_balance_input


def _input() -> dict:
    return {
        "schema_version": SOLVENCY_SHOCK_INPUT_VERSION,
        "solvency_model_balance_input": model_balance_input(),
        "exposures": [
            {
                "exposure_id": exposure_id,
                "sector_id": sector_id,
                "balance_side": side,
                "base_amount": amount,
                "source_kind": "scenario_declared_non_overlapping_subposition",
            }
            for exposure_id, sector_id, side, amount in (
                ("motor_assets", "motor", "assets", "1"),
                ("motor_claims", "motor", "liabilities", "1"),
                ("life_liability", "life", "liabilities", "1"),
                ("health_assets", "health", "assets", "1"),
            )
        ],
        "shocks": [
            {
                "shock_id": "market_fall",
                "driver_kind": "asset_market_value",
                "exposure_id": "motor_assets",
                "amount_delta": "-0.25",
                "assumption_note": "Deklarierter Marktwertverlust",
            },
            {
                "shock_id": "life_stress",
                "driver_kind": "life_obligation",
                "exposure_id": "life_liability",
                "amount_delta": "0.50",
                "assumption_note": "Deklarierte Verpflichtungserhoehung",
            },
        ],
    }


def test_only_explicit_targets_change_and_source_is_unchanged() -> None:
    value = _input()
    original = copy.deepcopy(value)
    source = build_solvency_model_balance(value["solvency_model_balance_input"]).to_dict()
    with localcontext() as context:
        context.prec = 3
        result = build_solvency_scenario_shocks(value).to_dict()
    assert value == original
    assert result == build_solvency_scenario_shocks(value).to_dict()
    assert result["valid"] is True, result["issues"]
    assert result["schema_version"] == SOLVENCY_SHOCK_RESULT_VERSION
    assert result["source_content_digest"] == source["content_digest"]
    assert result["checkpoint"] == source["checkpoint"]
    assert result["insurer_id"] == source["insurer_id"]
    assert len(result["input_digest"]) == len(result["content_digest"]) == 64
    rows = {row["exposure_id"]: row for row in result["exposure_rows"]}
    assert rows["motor_assets"]["amount_delta"] == "-0.2500"
    assert rows["motor_assets"]["shocked_amount"] == "0.7500"
    assert rows["life_liability"]["shocked_amount"] == "1.5000"
    for exposure_id in ("motor_claims", "health_assets"):
        assert rows[exposure_id]["amount_delta"] == "0.0000"
        assert rows[exposure_id]["shocked_amount"] == rows[exposure_id]["base_amount"]
    assert result["total_impact"] == {
        "asset_delta": "-0.2500",
        "liability_delta": "0.5000",
        "model_proxy_change": "-0.7500",
    }
    assert sum(Decimal(row["model_proxy_change"]) for row in result["sector_impacts"]) == Decimal("-0.75")
    assert build_solvency_model_balance(value["solvency_model_balance_input"]).to_dict() == source
    for flag in (
        "writes_performed", "runner_invoked", "regulatory_own_funds_claim",
        "scr_or_mcr_calculated", "compliance_decision_enabled",
        "historical_full_equality_claim",
    ):
        assert result[flag] is False
    assert "scr" not in result and "mcr" not in result and "coverage_ratio" not in result


def test_no_shock_is_an_unchanged_baseline_with_explicit_exposures() -> None:
    value = _input()
    value["shocks"] = []
    result = build_solvency_scenario_shocks(value).to_dict()
    assert result["valid"] is True
    assert result["shock_rows"] == []
    assert result["total_impact"]["model_proxy_change"] == "0.0000"
    assert all(row["base_amount"] == row["shocked_amount"] for row in result["exposure_rows"])


@pytest.mark.parametrize(("driver", "exposure_id"), [
    ("asset_market_value", "health_assets"),
    ("non_life_claim_obligation", "motor_claims"),
    ("life_obligation", "life_liability"),
    ("health_benefit_obligation", "health_benefit"),
])
def test_each_declared_driver_has_a_valid_target(driver: str, exposure_id: str) -> None:
    value = _input()
    if exposure_id == "health_benefit":
        value["exposures"][3].update({
            "exposure_id": exposure_id,
            "balance_side": "liabilities",
        })
    value["shocks"] = [{
        "shock_id": "one_shock",
        "driver_kind": driver,
        "exposure_id": exposure_id,
        "amount_delta": "0.25",
        "assumption_note": "Expliziter Modellschock",
    }]
    result = build_solvency_scenario_shocks(value).to_dict()
    assert result["valid"] is True, result["issues"]
    assert len(result["shock_rows"]) == 1
    assert sum(row["amount_delta"] != "0.0000" for row in result["exposure_rows"]) == 1


@pytest.mark.parametrize(("mutation", "code"), [
    (lambda value: value.update({"schema_version": "wrong"}), "contract_value_mismatch"),
    (lambda value: value.update({"surprise": 1}), "field_unknown"),
    (lambda value: value["exposures"][0].update({"extra": 1}), "field_unknown"),
    (lambda value: value["exposures"][0].update({"base_amount": "1e3"}), "decimal_string_required"),
    (lambda value: value["exposures"][0].update({"base_amount": "-1"}), "negative_exposure"),
    (lambda value: value["exposures"][0].update({"source_kind": "inferred"}), "source_kind_invalid"),
    (lambda value: value["exposures"][0].update({"base_amount": "999999"}), "exposure_overallocated"),
    (lambda value: value["exposures"][1].update({"exposure_id": "motor_assets"}), "exposure_duplicate"),
    (lambda value: value["shocks"][0].update({"exposure_id": "missing"}), "exposure_unknown"),
    (lambda value: value["shocks"][0].update({"driver_kind": "life_obligation"}), "driver_target_mismatch"),
    (lambda value: value["shocks"][0].update({"amount_delta": "-2"}), "negative_shocked_exposure"),
    (lambda value: value["shocks"][0].update({"amount_delta": "NaN"}), "decimal_string_required"),
    (lambda value: value["shocks"][0].update({"assumption_note": " "}), "note_invalid"),
    (lambda value: value["shocks"][1].update({"shock_id": "market_fall"}), "shock_duplicate"),
    (lambda value: value["shocks"][1].update({"exposure_id": "motor_assets"}), "exposure_shocked_twice"),
    (lambda value: value["solvency_model_balance_input"]["checkpoint"].update({"reference_date": "2026-02-30"}), "date_invalid"),
    (lambda value: value["solvency_model_balance_input"]["adjustments"][0].update({"asset_delta": "-99999"}), "negative_adjusted_stock"),
])
def test_invalid_mapping_is_atomic(mutation, code: str) -> None:
    value = _input()
    mutation(value)
    result = build_solvency_scenario_shocks(value).to_dict()
    assert result["valid"] is False
    assert result["exposure_rows"] == []
    assert result["shock_rows"] == []
    assert result["sector_impacts"] == []
    assert result["total_impact"] is None
    assert result["source_content_digest"] is None
    assert result["content_digest"] is None
    assert code in {issue["code"] for issue in result["issues"]}


def test_contract_limits_mapping_and_regulatory_claims() -> None:
    contract = solvency_scenario_shocks_contract_payload()
    assert contract["source_input_schema_version"] == "ims.solvency-model-balance-input.v1"
    assert contract["max_shocks_per_exposure"] == 1
    assert contract["driver_targets"]["life_obligation"] == {
        "balance_side": "liabilities", "sector_ids": ["life"],
    }
    assert contract["scr_or_mcr_calculated"] is False
    assert contract["writes_enabled"] is False
