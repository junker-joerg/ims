import copy
from decimal import Decimal, ROUND_HALF_UP, localcontext

import pytest

from ims.accounting.solvency_risk_aggregation import (
    SOLVENCY_RISK_AGGREGATION_INPUT_VERSION,
    SOLVENCY_RISK_AGGREGATION_RESULT_VERSION,
    build_solvency_risk_aggregation,
    solvency_risk_aggregation_contract_payload,
)
from ims.accounting.solvency_risk_modules import build_solvency_risk_modules
from tests.test_solvency_risk_modules import _input as modules_input


KINDS = (
    "asset_market_value", "non_life_claim_obligation", "life_obligation",
    "health_benefit_obligation", "counterparty_model_loss", "operational_model_loss",
)


def _input() -> dict:
    return {
        "schema_version": SOLVENCY_RISK_AGGREGATION_INPUT_VERSION,
        "solvency_risk_modules_input": modules_input(),
        "counterparty_cases": [{
            "case_id": "cp_health", "exposure_id": "health_assets",
            "loss_rate": "0.4", "source_kind": "scenario_declared_not_regulatory",
            "assumption_note": "Eigenstaendige Gegenpartei-Teilposition",
        }],
        "operational_events": [{
            "event_id": "ict_outage", "loss_amount": "0.2",
            "source_kind": "scenario_declared_not_regulatory",
            "assumption_note": "Separater Betriebsverlust im Seminarfall",
        }],
        "aggregation_assumptions": {
            "source_kind": "scenario_declared_not_regulatory",
            "assumption_note": "Gemeinsamer Szenariofaktor, keine empirische Kalibrierung",
            "factor_loadings": dict.fromkeys(KINDS, "1"),
        },
        "loss_absorption": {
            "buffer_id": "scenario_buffer", "capacity_amount": "0.25",
            "applied_amount": "0.175",
            "source_kind": "scenario_declared_independent_model_buffer",
            "assumption_note": "Separater Modellpuffer ohne Doppelzaehlung angenommen",
        },
    }


def test_aggregation_is_reproducible_source_bound_and_not_regulatory() -> None:
    value = _input()
    before = copy.deepcopy(value)
    with localcontext() as context:
        context.prec = 3
        result = build_solvency_risk_aggregation(value).to_dict()
    assert value == before
    assert result == build_solvency_risk_aggregation(value).to_dict()
    assert result["valid"] is True, result["issues"]
    assert result["schema_version"] == SOLVENCY_RISK_AGGREGATION_RESULT_VERSION
    source = build_solvency_risk_modules(value["solvency_risk_modules_input"]).to_dict()
    assert result["source_module_content_digest"] == source["content_digest"]
    assert result["source_exposure_content_digest"] == source["source_exposure_content_digest"]
    assert result["source_model_balance_content_digest"] == source["source_model_balance_content_digest"]
    assert len(result["input_digest"]) == len(result["content_digest"]) == 64
    assert result["checkpoint"] == source["checkpoint"]
    assert result["amount_unit"] == "model_currency_unit_not_eur"
    assert {row["risk_kind"]: row["model_loss_amount"] for row in result["component_rows"]} == {
        "asset_market_value": "0.2500",
        "non_life_claim_obligation": "0.7000",
        "life_obligation": "0.1250",
        "health_benefit_obligation": "0.1000",
        "counterparty_model_loss": "0.4000",
        "operational_model_loss": "0.2000",
    }
    assert result["counterparty_rows"][0]["model_loss_amount"] == "0.4000"
    assert result["operational_rows"][0]["model_loss_amount"] == "0.2000"
    assert result["totals"] == {
        "unadjusted_sum_of_components": "1.7750",
        "gross_model_stress_loss": "1.7750",
        "scenario_diversification_proxy": "0.0000",
        "model_buffer_capacity": "0.2500",
        "model_buffer_applied": "0.1750",
        "net_model_stress_loss": "1.6000",
    }
    assert len(result["correlation_rows"]) == 15
    assert all(row["correlation"] == "1.00000000" for row in result["correlation_rows"])
    assert result["model_risk_aggregation_performed"] is True
    for flag in (
        "writes_performed", "runner_invoked", "regulatory_own_funds_claim",
        "scr_or_mcr_calculated", "capital_aggregation_performed",
        "compliance_decision_enabled", "historical_full_equality_claim",
    ):
        assert result[flag] is False
    assert "scr" not in result and "mcr" not in result and "coverage_ratio" not in result


def test_factor_boundaries_and_psd_form() -> None:
    value = _input()
    value["aggregation_assumptions"]["factor_loadings"] = dict.fromkeys(KINDS, "0")
    independent = build_solvency_risk_aggregation(value).to_dict()
    assert independent["valid"] is True
    expected = sum((Decimal(row["model_loss_amount"]) ** 2 for row in independent["component_rows"]), Decimal(0))
    with localcontext() as context:
        context.prec = 64
        expected = expected.sqrt().quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)
    assert Decimal(independent["totals"]["gross_model_stress_loss"]) == expected
    assert all(row["correlation"] == "0.00000000" for row in independent["correlation_rows"])
    assert expected < Decimal("1.7750")

    value["aggregation_assumptions"]["factor_loadings"] = dict.fromkeys(KINDS, "0.5")
    mixed = build_solvency_risk_aggregation(value).to_dict()
    assert mixed["valid"] is True
    assert all(row["correlation"] == "0.25000000" for row in mixed["correlation_rows"])
    assert expected < Decimal(mixed["totals"]["gross_model_stress_loss"]) < Decimal("1.7750")
    loadings = value["aggregation_assumptions"]["factor_loadings"]
    vectors = (dict.fromkeys(KINDS, Decimal(1)), {
        kind: Decimal(index - 3) for index, kind in enumerate(KINDS)
    })
    for vector in vectors:
        quadratic = sum((vector[kind] ** 2 * (1 - Decimal(loadings[kind]) ** 2) for kind in KINDS), Decimal(0))
        quadratic += sum((vector[kind] * Decimal(loadings[kind]) for kind in KINDS), Decimal(0)) ** 2
        assert quadratic >= 0


def test_counterparty_rounding_and_unaffected_source() -> None:
    value = _input()
    value["solvency_risk_modules_input"]["solvency_scenario_shocks_input"]["exposures"][3]["base_amount"] = "0.0002"
    value["counterparty_cases"][0]["loss_rate"] = "0.25"
    value["loss_absorption"]["applied_amount"] = "0"
    result = build_solvency_risk_aggregation(value).to_dict()
    assert result["valid"] is True, result["issues"]
    assert result["counterparty_rows"][0]["model_loss_amount"] == "0.0001"
    assert result["component_rows"][4]["model_loss_amount"] == "0.0001"


def test_empty_cases_and_zero_buffer_do_not_create_losses() -> None:
    value = _input()
    value["counterparty_cases"] = []
    value["operational_events"] = []
    value["loss_absorption"]["capacity_amount"] = "0"
    value["loss_absorption"]["applied_amount"] = "0"
    result = build_solvency_risk_aggregation(value).to_dict()
    assert result["valid"] is True
    assert result["counterparty_rows"] == result["operational_rows"] == []
    assert result["totals"]["net_model_stress_loss"] == "1.1750"


def test_all_zero_inputs_remain_zero() -> None:
    value = _input()
    value["solvency_risk_modules_input"]["module_parameters"] = []
    value["counterparty_cases"] = []
    value["operational_events"] = []
    value["loss_absorption"]["capacity_amount"] = "0"
    value["loss_absorption"]["applied_amount"] = "0"
    result = build_solvency_risk_aggregation(value).to_dict()
    assert result["valid"] is True, result["issues"]
    assert all(row["model_loss_amount"] == "0.0000" for row in result["component_rows"])
    assert result["totals"]["gross_model_stress_loss"] == "0.0000"
    assert result["totals"]["net_model_stress_loss"] == "0.0000"


@pytest.mark.parametrize(("mutation", "code"), [
    (lambda v: v.update({"schema_version": "wrong"}), "contract_value_mismatch"),
    (lambda v: v.update({"extra": 1}), "field_unknown"),
    (
        lambda v: v["solvency_risk_modules_input"]["module_parameters"][0].update({"stress_rate": "1.1"}),
        "rate_out_of_range",
    ),
    (lambda v: v["counterparty_cases"][0].update({"exposure_id": "motor_assets"}), "exposure_stressed_twice"),
    (lambda v: v["counterparty_cases"][0].update({"exposure_id": "motor_claims"}), "counterparty_target_invalid"),
    (lambda v: v["counterparty_cases"][0].update({"exposure_id": "absent"}), "exposure_unknown"),
    (lambda v: v["counterparty_cases"].append(copy.deepcopy(v["counterparty_cases"][0])), "case_duplicate"),
    (lambda v: v["counterparty_cases"][0].update({"loss_rate": "1.1"}), "rate_out_of_range"),
    (lambda v: v["counterparty_cases"][0].update({"source_kind": "regulatory"}), "source_kind_invalid"),
    (lambda v: v["operational_events"][0].update({"loss_amount": -1}), "amount_format_invalid"),
    (lambda v: v["operational_events"][0].update({"assumption_note": " "}), "note_invalid"),
    (lambda v: v["aggregation_assumptions"]["factor_loadings"].pop("life_obligation"), "field_missing"),
    (
        lambda v: v["aggregation_assumptions"]["factor_loadings"].update({"life_obligation": "-0.1"}),
        "rate_format_invalid",
    ),
    (lambda v: v["aggregation_assumptions"]["factor_loadings"].update({"life_obligation": "1.1"}), "rate_out_of_range"),
    (lambda v: v["loss_absorption"].update({"capacity_amount": "0.1"}), "buffer_capacity_exceeded"),
    (lambda v: v["loss_absorption"].update({"applied_amount": "99"}), "buffer_capacity_exceeded"),
    (lambda v: v["loss_absorption"].update({"source_kind": "balance_equity"}), "source_kind_invalid"),
])
def test_invalid_input_is_atomic(mutation, code: str) -> None:
    value = _input()
    mutation(value)
    result = build_solvency_risk_aggregation(value).to_dict()
    assert result["valid"] is False
    assert result["component_rows"] == []
    assert result["counterparty_rows"] == []
    assert result["operational_rows"] == []
    assert result["correlation_rows"] == []
    assert result["totals"] is None
    assert result["content_digest"] is None
    assert result["model_risk_aggregation_performed"] is False
    assert code in {issue["code"] for issue in result["issues"]}


def test_buffer_may_not_exceed_gross_even_if_capacity_is_large() -> None:
    value = _input()
    value["loss_absorption"]["capacity_amount"] = "2"
    value["loss_absorption"]["applied_amount"] = "2"
    result = build_solvency_risk_aggregation(value).to_dict()
    assert result["valid"] is False
    assert {issue["code"] for issue in result["issues"]} == {"buffer_gross_exceeded"}
    assert result["totals"] is None


def test_contract_discloses_model_only_boundary() -> None:
    contract = solvency_risk_aggregation_contract_payload()
    assert contract["risk_kinds"] == list(KINDS)
    assert contract["correlation_model"] == "one_common_factor_nonnegative_psd"
    assert contract["counterparty_exposure_must_be_unstressed_asset"] is True
    assert contract["scr_or_mcr_calculated"] is False
    assert contract["capital_aggregation_performed"] is False
