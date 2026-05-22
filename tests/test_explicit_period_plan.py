import json
from pathlib import Path

import pytest

from ims.engine.explicit_period_plan import (
    ExplicitPeriodPlan,
    ExplicitPeriodPlanUpdate,
    build_explicit_period_fixture_from_plan,
    run_explicit_multi_period_from_plan_fixture,
)


def _free_linear_parameters() -> dict[str, list[float]]:
    return {
        "premium_intercept_normal": [0.0, 0.0],
        "premium_factor_normal": [2.0, 2.0],
        "advertising_intercept_normal": [0.0, 0.0],
        "advertising_factor_normal": [1.0, 1.0],
        "premium_intercept_shock": [0.0, 0.0],
        "premium_factor_shock": [1.0, 1.0],
        "advertising_intercept_shock": [0.0, 0.0],
        "advertising_factor_shock": [1.0, 1.0],
    }


def _damage_parameters() -> dict[str, list[float]]:
    return {
        "damage_intercept_normal": [5.0, 7.0],
        "damage_factor_normal": [2.0, 3.0],
        "damage_intercept_shock": [50.0, 70.0],
        "damage_factor_shock": [20.0, 30.0],
    }


def _damage_snapshot(*, policyholder_id: int = 21) -> dict:
    return {
        "policyholder_id": policyholder_id,
        "previous_wealth": 100.0,
        "damage_thresholds": [0.8, 0.2],
        "parameters": _damage_parameters(),
        "draws": {
            "trigger_draws": [0.1, 0.5],
            "amount_draws": [2.0, 3.0],
        },
        "insurance_decisions": [
            {"sector_index": 0, "insured": True, "insurer_id": 11},
            {"sector_index": 1, "insured": False},
        ],
    }


def _insurance_rule_snapshot(*, policyholder_id: int = 21) -> dict:
    return {
        "policyholder_id": policyholder_id,
        "rule_kind": "compulsory",
        "active_insurer_ids": [11],
        "draws": {"insurer_choice_draws": [0.0, 0.0]},
    }


def _base_snapshot() -> dict:
    return {
        "context": {"period": 0, "max_periods": 12, "run_index": 0, "rng_seed": 0},
        "bav": {"entity_id": 1, "name": "BAV"},
        "insurers": [
            {
                "entity_id": 11,
                "name": "VU-11",
                "rule_id": 1,
                "rule_class": 1,
                "premiums_current_sector": [4.0, 6.0],
                "advertising_current_sector": [1.0, 1.0],
                "reserves_current": [40.0, 60.0],
                "policyholders_current_sector": [1.0, 2.0],
                "claims_count_current": [0, 0],
                "claims_sum_current": [0.0, 0.0],
            }
        ],
        "policyholders": [
            {
                "entity_id": 21,
                "name": "VN-21",
                "rule_id": 5,
                "rule_class": 1,
            }
        ],
    }


def _period_plan(*, carry_forward_vu_state: object = False, carry_forward_vn_state: object = True) -> dict:
    free_linear_snapshot = {
        "insurer_id": 11,
        "interest_rate": 0.0,
        "parameters": _free_linear_parameters(),
    }
    return {
        "metadata": {"purpose": "explicit VU/VN period plan"},
        "carry_forward_vu_state": carry_forward_vu_state,
        "carry_forward_vn_state": carry_forward_vn_state,
        "base_snapshot": _base_snapshot(),
        "period_updates": [
            {
                "context": {"period": 2, "run_index": 0, "rng_seed": 1002},
                "insurers": [],
                "policyholders": [],
                "vu_free_linear_rule_snapshots": [free_linear_snapshot],
                "vn_insurance_rule_snapshots": [_insurance_rule_snapshot()],
                "vn_damage_settlement_snapshots": [_damage_snapshot()],
            },
            {
                "context": {"period": 3, "run_index": 0, "rng_seed": 1003},
                "insurers": [],
                "policyholders": [],
                "vu_free_linear_rule_snapshots": [free_linear_snapshot],
                "vn_insurance_rule_snapshots": [_insurance_rule_snapshot()],
                "vn_damage_settlement_snapshots": [_damage_snapshot()],
            },
        ],
    }


def _non_empty_lines(path: Path) -> list[str]:
    return [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def test_explicit_period_plan_builds_runner_fixture_from_base_snapshot() -> None:
    fixture = build_explicit_period_fixture_from_plan(_period_plan())

    assert fixture["carry_forward_vn_state"] is True
    assert fixture["carry_forward_vu_state"] is False
    assert [period["context"]["period"] for period in fixture["periods"]] == [2, 3]
    assert fixture["periods"][0]["vu_free_linear_rule_snapshots"][0]["insurer_id"] == 11
    assert fixture["periods"][0]["vn_insurance_rule_snapshots"][0]["rule_kind"] == "compulsory"
    assert fixture["periods"][1]["vn_damage_settlement_snapshots"][0]["policyholder_id"] == 21


def test_explicit_period_plan_preserves_legacy_targets_in_fixture() -> None:
    data = _period_plan()
    data["legacy_report_name"] = "plan_validation"
    data["legacy_targets"] = [
        {
            "legacy_path": "legacy/reference_imsvu011.dat",
            "export_filename": "imsvu011.dat",
            "subject_type": "insurer",
        }
    ]

    fixture = build_explicit_period_fixture_from_plan(data)

    assert fixture["legacy_report_name"] == "plan_validation"
    assert fixture["legacy_targets"] == data["legacy_targets"]


def test_explicit_period_plan_applies_context_overrides() -> None:
    data = _period_plan()
    data["period_updates"][0]["context"] = {
        "period": 2,
        "logtime": 7,
        "max_periods": 100,
        "run_index": 1,
        "rng_seed": 1202,
    }

    fixture = build_explicit_period_fixture_from_plan(data)
    context = fixture["periods"][0]["context"]

    assert context["period"] == 2
    assert context["logtime"] == 7
    assert context["max_periods"] == 100
    assert context["run_index"] == 1
    assert context["rng_seed"] == 1202


def test_explicit_period_plan_runs_combined_vu_vn_path(tmp_path: Path) -> None:
    plan_path = tmp_path / "explicit_period_plan.json"
    plan_path.write_text(json.dumps(_period_plan()), encoding="utf-8")

    result = run_explicit_multi_period_from_plan_fixture(plan_path, output_dir=tmp_path / "out")
    insurer_lines = _non_empty_lines(tmp_path / "out" / "imsvu011.dat")

    assert result.processed_periods == [2, 3]
    assert result.total_vu_rule_applications == 2
    assert result.total_vn_insurance_rule_applications == 2
    assert result.total_vn_damage_settlement_applications == 2
    assert len(result.carryovers) == 1
    assert result.carryovers[0].vn_carryover is not None
    assert insurer_lines[1].split()[1:4] == ["8.0", "1.0", "39.0"]
    assert insurer_lines[2].split()[1:4] == ["16.0", "1.0", "46.0"]


def test_explicit_period_plan_runs_legacy_targets_and_writes_report(tmp_path: Path) -> None:
    legacy_path = tmp_path / "legacy" / "reference_imsvu011.dat"
    legacy_path.parent.mkdir()
    legacy_path.write_text(
        "\n".join(
            [
                "#t Pr1 Wer1 Rs1 Vn1 Sc1 Sh1 Pr2 Wer2 Rs2 Vn2 Sc2 Sh2",
                "2 8.0 1.0 39.0 2.0 1 9.0 12.0 1.0 60.0 2.0 0 0.0",
                "3 16.0 1.0 46.0 3.0 2 18.0 24.0 1.0 60.0 2.0 0 0.0",
                "",
            ]
        ),
        encoding="utf-8",
    )
    data = _period_plan()
    data["legacy_report_name"] = "plan_validation"
    data["legacy_targets"] = [
        {
            "legacy_path": "legacy/reference_imsvu011.dat",
            "export_filename": "imsvu011.dat",
            "subject_type": "insurer",
        }
    ]
    plan_path = tmp_path / "explicit_period_plan_with_legacy.json"
    plan_path.write_text(json.dumps(data), encoding="utf-8")

    result = run_explicit_multi_period_from_plan_fixture(plan_path, output_dir=tmp_path / "out")

    assert result.legacy_comparison is not None
    assert result.legacy_comparison.matches is True
    assert result.legacy_report is not None
    assert result.legacy_report.matches is True
    assert [path.name for path in result.written_legacy_report_files] == [
        "plan_validation.json",
        "plan_validation.csv",
        "plan_validation_fields.csv",
        "plan_validation_groups.csv",
        "plan_validation_periods.csv",
        "plan_validation_deviations.csv",
    ]


def test_explicit_period_plan_can_override_entity_fields() -> None:
    data = _period_plan()
    data["period_updates"][1]["policyholders"] = [{"entity_id": 21, "name": "VN-21-Updated"}]

    fixture = build_explicit_period_fixture_from_plan(data)

    assert fixture["periods"][0]["policyholders"][0]["name"] == "VN-21"
    assert fixture["periods"][1]["policyholders"][0]["name"] == "VN-21-Updated"


def test_explicit_period_plan_rejects_non_boolean_flags() -> None:
    with pytest.raises(ValueError, match="carry_forward_vu_state must be a boolean"):
        build_explicit_period_fixture_from_plan(_period_plan(carry_forward_vu_state="false"))
    with pytest.raises(ValueError, match="carry_forward_vn_state must be a boolean"):
        build_explicit_period_fixture_from_plan(_period_plan(carry_forward_vn_state="false"))


def test_explicit_period_plan_rejects_non_list_legacy_targets() -> None:
    data = _period_plan()
    data["legacy_targets"] = {"legacy_path": "reference.dat"}

    with pytest.raises(ValueError, match="legacy_targets must be a list"):
        build_explicit_period_fixture_from_plan(data)


def test_explicit_period_plan_rejects_unknown_entity_update() -> None:
    data = _period_plan()
    data["period_updates"][0]["insurers"] = [{"entity_id": 999, "name": "missing"}]

    with pytest.raises(ValueError, match="unknown insurers entity_id: 999"):
        build_explicit_period_fixture_from_plan(data)


def test_explicit_period_plan_rejects_non_list_entity_updates() -> None:
    data = _period_plan()
    data["period_updates"][0]["insurers"] = None

    with pytest.raises(ValueError, match="field insurers must be a list"):
        build_explicit_period_fixture_from_plan(data)

    data = _period_plan()
    data["period_updates"][0]["policyholders"] = {"entity_id": 21}

    with pytest.raises(ValueError, match="field policyholders must be a list"):
        build_explicit_period_fixture_from_plan(data)


def test_explicit_period_plan_rejects_non_list_snapshot_updates() -> None:
    data = _period_plan()
    data["period_updates"][0]["vu_free_linear_rule_snapshots"] = {"insurer_id": 11}

    with pytest.raises(ValueError, match="vu_free_linear_rule_snapshots must be a list"):
        build_explicit_period_fixture_from_plan(data)


def test_explicit_period_plan_api_import_shapes() -> None:
    assert ExplicitPeriodPlan is not None
    assert ExplicitPeriodPlanUpdate is not None
