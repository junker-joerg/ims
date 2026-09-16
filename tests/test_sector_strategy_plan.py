import copy
import json
from pathlib import Path

import pytest

from ims.strategies.sector_strategy_plan import (
    SECTOR_STRATEGY_PLAN_VALIDATION_VERSION,
    SECTOR_STRATEGY_PLAN_VERSION,
    sector_strategy_plan_contract_payload,
    validate_sector_strategy_plan,
)


FIXTURE = Path(__file__).parent / "fixtures" / "sector_strategy_plan_v1.json"


def _plan() -> dict:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def test_plan_validates_different_strategies_and_scalar_parameters_by_sector() -> None:
    plan = _plan()

    report = validate_sector_strategy_plan(plan).to_dict()

    assert report["schema_version"] == SECTOR_STRATEGY_PLAN_VALIDATION_VERSION
    assert report["valid"] is True
    assert report["accepted_assignment_count"] == 2
    assert report["historical_mapping_status"] == "unresolved"
    assert report["writes_performed"] is False
    assert report["snapshots_created"] is False
    assert report["execution_performed"] is False
    assert report["simulation_performed"] is False
    assert plan == _plan()


def test_plan_allows_adjacent_windows_and_policyholder_strategy() -> None:
    plan = _plan()
    first = plan["assignments"][0]
    first["period_through"] = 50
    second_window = copy.deepcopy(first)
    second_window["period_from"] = 51
    second_window["period_through"] = 100
    second_window["parameter_values"]["premium_factor_normal"] = 1.3
    plan["assignments"].append(second_window)
    plan["assignments"].append(
        {
            "actor_type": "policyholder",
            "target_id": 1,
            "sector_id": "motor",
            "strategy_id": "vn.vrvn02",
            "period_from": 1,
            "period_through": 100,
            "parameter_schema": "VNRandomInsuranceRuleParameters",
            "parameter_values": {
                "insurance_thresholds_normal": 0.5,
                "insurance_thresholds_shock": 0.7,
            },
        }
    )
    plan["assignments"].append(
        {
            "actor_type": "policyholder",
            "target_id": 1,
            "sector_id": "property_liability",
            "strategy_id": "vn.vrvn01",
            "period_from": 1,
            "period_through": 100,
            "parameter_schema": None,
            "parameter_values": None,
        }
    )

    report = validate_sector_strategy_plan(plan).to_dict()

    assert report["valid"] is True
    assert report["accepted_assignment_count"] == 5


@pytest.mark.parametrize(
    ("path", "value", "code"),
    [
        (("schema_version",), "ims.sector-strategy-plan.v0", "contract_value_mismatch"),
        (("historical_mapping_status",), "mapped", "contract_value_mismatch"),
        (("assignments", 0, "sector_id"), "life", "sector_strategy_not_available"),
        (("assignments", 0, "sector_id"), "health", "sector_strategy_not_available"),
        (("assignments", 0, "sector_id"), "legacy.damage_1", "sector_unknown"),
        (("assignments", 0, "target_id"), 26, "integer_out_of_range"),
        (("assignments", 0, "period_through"), 101, "integer_out_of_range"),
        (("assignments", 0, "period_through"), 0, "integer_out_of_range"),
        (("assignments", 0, "strategy_id"), "vn.vrvn02", "strategy_actor_mismatch"),
        (("assignments", 0, "parameter_schema"), "wrong", "parameter_schema_mismatch"),
        (("assignments", 0, "parameter_values", "premium_factor_normal"), [1.0, 1.0], "finite_number_required"),
        (("assignments", 0, "parameter_values", "premium_factor_normal"), True, "finite_number_required"),
        (("assignments", 0, "parameter_values", "premium_factor_normal"), float("nan"), "finite_number_required"),
    ],
)
def test_plan_rejects_invalid_entry_atomically(path: tuple, value: object, code: str) -> None:
    plan = _plan()
    target = plan
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = value

    report = validate_sector_strategy_plan(plan).to_dict()

    assert report["valid"] is False
    assert report["accepted_assignment_count"] == 0
    assert code in {issue["code"] for issue in report["issues"]}


def test_plan_rejects_overlapping_windows_but_not_separate_sectors() -> None:
    plan = _plan()
    duplicate = copy.deepcopy(plan["assignments"][0])
    duplicate["period_from"] = 50
    plan["assignments"].append(duplicate)

    report = validate_sector_strategy_plan(plan).to_dict()

    assert report["valid"] is False
    assert report["accepted_assignment_count"] == 0
    assert "period_window_overlap" in {issue["code"] for issue in report["issues"]}


def test_plan_rejects_reversed_window() -> None:
    plan = _plan()
    plan["assignments"][0]["period_from"] = 80
    plan["assignments"][0]["period_through"] = 79

    report = validate_sector_strategy_plan(plan).to_dict()

    assert report["accepted_assignment_count"] == 0
    assert "period_window_invalid" in {issue["code"] for issue in report["issues"]}


def test_plan_rejects_unknown_and_missing_parameters_and_fields() -> None:
    plan = _plan()
    del plan["assignments"][0]["parameter_values"]["premium_factor_shock"]
    plan["assignments"][1]["parameter_values"]["invented"] = 1.0
    plan["assignments"][1]["unknown_field"] = 1

    report = validate_sector_strategy_plan(plan).to_dict()

    assert report["valid"] is False
    assert report["accepted_assignment_count"] == 0
    codes = {issue["code"] for issue in report["issues"]}
    assert "field_missing" in codes
    assert "field_unknown" in codes


def test_parameterless_strategy_and_vn_sample_size_boundary() -> None:
    plan = _plan()
    plan["assignments"] = [
        {
            "actor_type": "policyholder",
            "target_id": 1,
            "sector_id": "motor",
            "strategy_id": "vn.vrvn01",
            "period_from": 1,
            "period_through": 100,
            "parameter_schema": None,
            "parameter_values": None,
        }
    ]
    assert validate_sector_strategy_plan(plan).valid is True

    plan["assignments"][0]["parameter_values"] = {}
    assert "parameters_not_supported" in {
        issue.code for issue in validate_sector_strategy_plan(plan).issues
    }

    plan["assignments"][0].update(
        strategy_id="vn.vrvn05",
        parameter_schema="VNSampleSearchInsuranceRuleParameters",
        parameter_values={
            "insurance_thresholds_normal": 0.5,
            "insurance_thresholds_shock": 0.7,
            "sample_sizes_normal": -1,
            "sample_sizes_shock": 2,
        },
    )
    assert "non_negative_integer_required" in {
        issue.code for issue in validate_sector_strategy_plan(plan).issues
    }


def test_plan_contract_makes_pending_lines_and_execution_boundary_explicit() -> None:
    contract = json.loads(json.dumps(sector_strategy_plan_contract_payload()))

    assert contract["schema_version"] == SECTOR_STRATEGY_PLAN_VERSION
    assert contract["eligible_sector_ids"] == ["motor", "property_liability"]
    assert contract["pending_sector_ids"] == ["life", "health"]
    assert contract["target_limits"] == {"insurer": 25, "policyholder": 200}
    assert contract["parameter_value_shape"] == "scalar_per_named_sector"
    assert contract["legacy_sector_binding_enabled"] is False
    assert contract["snapshot_materialization_enabled"] is False
    assert contract["execution_enabled"] is False
