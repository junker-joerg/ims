import copy
from decimal import Decimal, localcontext

import pytest

from ims.accounting.solvency_risk_modules import (
    SOLVENCY_RISK_MODULE_INPUT_VERSION,
    SOLVENCY_RISK_MODULE_RESULT_VERSION,
    build_solvency_risk_modules,
    solvency_risk_modules_contract_payload,
)
from ims.accounting.solvency_scenario_shocks import build_solvency_scenario_shocks
from tests.test_solvency_scenario_shocks import _input as shock_input


def _parameter(module_id: str, module_kind: str, exposure_id: str, rate: str) -> dict:
    return {
        "module_id": module_id,
        "module_kind": module_kind,
        "exposure_id": exposure_id,
        "stress_rate": rate,
        "parameter_source_kind": "scenario_declared_not_regulatory",
        "assumption_note": f"Deklarierter Stress {module_id}",
    }


def _input() -> dict:
    source = shock_input()
    source["shocks"] = []
    source["exposures"].extend([
        {
            "exposure_id": "property_claims",
            "sector_id": "property_liability",
            "balance_side": "liabilities",
            "base_amount": "1",
            "source_kind": "scenario_declared_non_overlapping_subposition",
        },
        {
            "exposure_id": "health_benefit",
            "sector_id": "health",
            "balance_side": "liabilities",
            "base_amount": "1",
            "source_kind": "scenario_declared_non_overlapping_subposition",
        },
    ])
    return {
        "schema_version": SOLVENCY_RISK_MODULE_INPUT_VERSION,
        "solvency_scenario_shocks_input": source,
        "module_parameters": [
            _parameter("market", "asset_market_value", "motor_assets", "0.25"),
            _parameter("nonlife", "non_life_claim_obligation", "motor_claims", "0.50"),
            _parameter("property", "non_life_claim_obligation", "property_claims", "0.20"),
            _parameter("life", "life_obligation", "life_liability", "0.125"),
            _parameter("health", "health_benefit_obligation", "health_benefit", "0.10"),
        ],
    }


def test_modules_are_exact_reproducible_and_connect_to_pr173() -> None:
    value = _input()
    before = copy.deepcopy(value)
    with localcontext() as context:
        context.prec = 3
        result = build_solvency_risk_modules(value).to_dict()
    assert value == before
    assert result == build_solvency_risk_modules(value).to_dict()
    assert result["valid"] is True, result["issues"]
    assert result["schema_version"] == SOLVENCY_RISK_MODULE_RESULT_VERSION
    assert result["amount_unit"] == "model_currency_unit_not_eur"
    assert len(result["source_exposure_content_digest"]) == len(result["input_digest"]) == len(result["content_digest"]) == 64
    baseline = build_solvency_scenario_shocks(value["solvency_scenario_shocks_input"]).to_dict()
    assert result["source_exposure_content_digest"] == baseline["content_digest"]
    assert result["source_model_balance_content_digest"] == baseline["source_content_digest"]
    assert result["checkpoint"] == baseline["checkpoint"]
    modules = {row["module_id"]: row for row in result["module_rows"]}
    assert modules["market"]["amount_delta"] == "-0.2500"
    assert modules["market"]["post_stress_amount"] == "0.7500"
    assert modules["nonlife"]["amount_delta"] == "0.5000"
    assert modules["property"]["amount_delta"] == "0.2000"
    assert modules["life"]["amount_delta"] == "0.1250"
    assert modules["health"]["amount_delta"] == "0.1000"
    assert all(Decimal(row["model_proxy_change"]) <= 0 for row in result["module_rows"])
    assert sum(Decimal(row["model_proxy_change"]) for row in result["module_rows"]) == Decimal("-1.175")
    assert result["calibration_status"] == "scenario_only_not_regulatory"
    for flag in (
        "writes_performed", "runner_invoked", "regulatory_own_funds_claim",
        "scr_or_mcr_calculated", "capital_aggregation_performed",
        "compliance_decision_enabled", "historical_full_equality_claim",
    ):
        assert result[flag] is False
    assert "scr" not in result and "mcr" not in result and "coverage_ratio" not in result

    derived = copy.deepcopy(value["solvency_scenario_shocks_input"])
    derived["shocks"] = [{
        "shock_id": row["module_id"],
        "driver_kind": row["module_kind"],
        "exposure_id": row["exposure_id"],
        "amount_delta": row["amount_delta"],
        "assumption_note": row["assumption_note"],
    } for row in result["module_rows"]]
    pr173 = build_solvency_scenario_shocks(derived).to_dict()
    assert pr173["valid"] is True, pr173["issues"]
    assert result["exposure_rows"] == pr173["exposure_rows"]
    assert sum(Decimal(row["model_proxy_change"]) for row in result["module_rows"]) == Decimal(pr173["total_impact"]["model_proxy_change"])
    assert [row for row in result["exposure_rows"] if row["exposure_id"] == "health_assets"][0]["amount_delta"] == "0.0000"


@pytest.mark.parametrize(("module_kind", "exposure_id"), [
    ("asset_market_value", "motor_assets"),
    ("life_obligation", "life_liability"),
])
@pytest.mark.parametrize("rate", ["0", "0.1", "0.5", "1"])
def test_larger_rate_never_reduces_model_loss(module_kind: str, exposure_id: str, rate: str) -> None:
    value = _input()
    value["module_parameters"] = [_parameter("one", module_kind, exposure_id, rate)]
    result = build_solvency_risk_modules(value).to_dict()
    assert result["valid"] is True
    row = result["module_rows"][0]
    assert Decimal(row["model_proxy_change"]) == -Decimal(rate)
    assert Decimal(row["post_stress_amount"]) >= 0


def test_round_half_up_once_per_exposure() -> None:
    value = _input()
    value["solvency_scenario_shocks_input"]["exposures"][0]["base_amount"] = "0.0002"
    value["module_parameters"] = [_parameter("market", "asset_market_value", "motor_assets", "0.25")]
    row = build_solvency_risk_modules(value).to_dict()["module_rows"][0]
    assert row["amount_delta"] == "-0.0001"
    assert row["post_stress_amount"] == "0.0001"


def test_empty_module_set_keeps_every_exposure_unchanged() -> None:
    value = _input()
    value["module_parameters"] = []
    result = build_solvency_risk_modules(value).to_dict()
    assert result["valid"] is True
    assert result["module_rows"] == []
    assert all(row["amount_delta"] == "0.0000" for row in result["exposure_rows"])


@pytest.mark.parametrize(("mutation", "code"), [
    (lambda value: value.update({"schema_version": "wrong"}), "contract_value_mismatch"),
    (lambda value: value.update({"extra": 1}), "field_unknown"),
    (lambda value: value["module_parameters"][0].update({"extra": 1}), "field_unknown"),
    (lambda value: value["module_parameters"][0].update({"module_kind": "scr_market"}), "module_kind_invalid"),
    (lambda value: value["module_parameters"][0].update({"module_kind": "life_obligation"}), "module_target_mismatch"),
    (lambda value: value["module_parameters"][0].update({"exposure_id": "missing"}), "exposure_unknown"),
    (lambda value: value["module_parameters"][0].update({"stress_rate": "-0.1"}), "rate_format_invalid"),
    (lambda value: value["module_parameters"][0].update({"stress_rate": "1.1"}), "rate_out_of_range"),
    (lambda value: value["module_parameters"][0].update({"stress_rate": "0.00001"}), "rate_format_invalid"),
    (lambda value: value["module_parameters"][0].update({"stress_rate": "1e-2"}), "rate_format_invalid"),
    (lambda value: value["module_parameters"][0].update({"parameter_source_kind": "regulatory"}), "source_kind_invalid"),
    (lambda value: value["module_parameters"][0].update({"assumption_note": " "}), "note_invalid"),
    (lambda value: value["module_parameters"][1].update({"module_id": "market"}), "module_duplicate"),
    (lambda value: value["module_parameters"][1].update({"exposure_id": "motor_assets"}), "exposure_stressed_twice"),
    (lambda value: value["solvency_scenario_shocks_input"]["shocks"].append(shock_input()["shocks"][0]), "source_shocks_not_empty"),
    (lambda value: value["solvency_scenario_shocks_input"]["exposures"][0].update({"base_amount": "999999"}), "exposure_overallocated"),
])
def test_invalid_module_input_is_atomic(mutation, code: str) -> None:
    value = _input()
    mutation(value)
    result = build_solvency_risk_modules(value).to_dict()
    assert result["valid"] is False
    assert result["module_rows"] == []
    assert result["exposure_rows"] == []
    assert result["source_exposure_content_digest"] is None
    assert result["content_digest"] is None
    assert code in {issue["code"] for issue in result["issues"]}


def test_contract_discloses_limited_model_calibration() -> None:
    contract = solvency_risk_modules_contract_payload()
    assert contract["source_input_schema_version"] == "ims.solvency-scenario-shocks-input.v1"
    assert contract["source_shocks_required_empty"] is True
    assert contract["rounding"] == "ROUND_HALF_UP_to_4_fractional_places_once_per_exposure"
    assert contract["module_targets"]["health_benefit_obligation"] == {
        "balance_side": "liabilities", "sector_ids": ["health"],
    }
    assert contract["scr_or_mcr_calculated"] is False
    assert contract["capital_aggregation_performed"] is False
