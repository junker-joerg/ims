import json
from pathlib import Path

import pytest

from ims.engine.vn_agrsich_replay_plan import (
    VNAgrsichReplayPeriodUpdate,
    VNAgrsichReplayPlan,
    build_vn_agrsich_replay_fixture_from_period_plan,
    run_vn_agrsich_replay_from_period_plan_fixture,
)


def _damage_parameters() -> dict:
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


def _base_snapshot(*, policyholder_id: int = 21) -> dict:
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
                "advertising_current_sector": [0.0, 0.0],
                "reserves_current": [40.0, 60.0],
                "policyholders_current_sector": [1.0, 2.0],
                "claims_count_current": [0, 0],
                "claims_sum_current": [0.0, 0.0],
            }
        ],
        "policyholders": [
            {
                "entity_id": policyholder_id,
                "name": f"VN-{policyholder_id}",
                "rule_id": 5,
                "rule_class": 1,
            }
        ],
    }


def _period_plan(*, carry_forward_vn_state: object = True) -> dict:
    return {
        "metadata": {"purpose": "small VN Agrsich period plan"},
        "carry_forward_vn_state": carry_forward_vn_state,
        "base_snapshot": _base_snapshot(),
        "period_updates": [
            {
                "context": {"period": 1, "run_index": 0, "rng_seed": 901},
                "insurers": [],
                "policyholders": [],
                "vn_damage_settlement_snapshots": [_damage_snapshot()],
            },
            {
                "context": {"period": 2, "run_index": 0, "rng_seed": 902},
                "insurers": [],
                "policyholders": [],
                "vn_damage_settlement_snapshots": [_damage_snapshot()],
            },
        ],
    }


def _non_empty_lines(path: Path) -> list[str]:
    return [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def test_vn_period_plan_builds_replay_periods_from_start_state() -> None:
    replay_fixture = build_vn_agrsich_replay_fixture_from_period_plan(_period_plan())

    assert replay_fixture["carry_forward_vn_state"] is True
    assert [period["context"]["period"] for period in replay_fixture["periods"]] == [1, 2]
    assert replay_fixture["periods"][0]["context"]["rng_seed"] == 901
    assert replay_fixture["periods"][1]["vn_damage_settlement_snapshots"][0]["policyholder_id"] == 21


def test_vn_period_plan_preserves_legacy_targets_in_fixture() -> None:
    data = _period_plan()
    data["legacy_report_name"] = "vn_plan_validation"
    data["legacy_targets"] = [
        {
            "legacy_path": "legacy/reference_imsvnr05.dat",
            "export_filename": "imsvnr05.dat",
            "subject_type": "policyholder",
        }
    ]

    replay_fixture = build_vn_agrsich_replay_fixture_from_period_plan(data)

    assert replay_fixture["legacy_report_name"] == "vn_plan_validation"
    assert replay_fixture["legacy_targets"] == data["legacy_targets"]


def test_vn_period_plan_replay_carries_state_between_periods(tmp_path: Path) -> None:
    plan_path = tmp_path / "vn_agrsich_period_plan.json"
    plan_path.write_text(json.dumps(_period_plan()), encoding="utf-8")

    result = run_vn_agrsich_replay_from_period_plan_fixture(plan_path, tmp_path / "out")
    insurer_lines = _non_empty_lines(tmp_path / "out" / "imsvu011.dat")

    assert result.processed_periods == [1, 2]
    assert len(result.carryovers) == 1
    assert result.carryovers[0].policyholder_ids == [21]
    assert insurer_lines[2].split() == [
        "2",
        "4.0",
        "0.0",
        "30.0",
        "5.0",
        "2",
        "18.0",
        "6.0",
        "0.0",
        "60.0",
        "5.0",
        "0",
        "0.0",
    ]


def test_vn_period_plan_runs_legacy_targets_and_writes_report(tmp_path: Path) -> None:
    legacy_path = tmp_path / "legacy" / "reference_imsvnr05.dat"
    legacy_path.parent.mkdir()
    legacy_path.write_text(
        "\n".join(
            [
                "#t Vu1 Vs1 Vp1 Ev1 Sh1 Vu2 Vs2 Vp2 Ev2 Sh2 Vm",
                "1 11 1.0 4.0 87.0 9.0 11 0.0 0.0 100.0 0.0 87.0",
                "2 11 1.0 4.0 87.0 9.0 11 0.0 0.0 100.0 0.0 87.0",
                "",
            ]
        ),
        encoding="utf-8",
    )
    data = _period_plan()
    data["legacy_report_name"] = "vn_plan_validation"
    data["legacy_targets"] = [
        {
            "legacy_path": "legacy/reference_imsvnr05.dat",
            "export_filename": "imsvnr05.dat",
            "subject_type": "policyholder",
        }
    ]
    plan_path = tmp_path / "vn_agrsich_period_plan_with_legacy.json"
    plan_path.write_text(json.dumps(data), encoding="utf-8")

    result = run_vn_agrsich_replay_from_period_plan_fixture(plan_path, tmp_path / "out")

    assert result.legacy_comparison is not None
    assert result.legacy_comparison.matches is True
    assert result.legacy_report is not None
    assert result.legacy_report.matches is True
    assert [path.name for path in result.written_legacy_report_files] == [
        "vn_plan_validation.json",
        "vn_plan_validation.csv",
        "vn_plan_validation_fields.csv",
        "vn_plan_validation_groups.csv",
        "vn_plan_validation_periods.csv",
        "vn_plan_validation_deviations.csv",
    ]


def test_vn_period_plan_can_override_entity_fields() -> None:
    data = _period_plan()
    data["period_updates"][1]["policyholders"] = [{"entity_id": 21, "name": "VN-21-Updated"}]

    replay_fixture = build_vn_agrsich_replay_fixture_from_period_plan(data)

    assert replay_fixture["periods"][0]["policyholders"][0]["name"] == "VN-21"
    assert replay_fixture["periods"][1]["policyholders"][0]["name"] == "VN-21-Updated"


def test_vn_period_plan_applies_context_overrides() -> None:
    data = _period_plan()
    data["period_updates"][0]["context"] = {
        "period": 1,
        "logtime": 4,
        "max_periods": 100,
        "run_index": 1,
        "rng_seed": 1901,
    }

    replay_fixture = build_vn_agrsich_replay_fixture_from_period_plan(data)
    context = replay_fixture["periods"][0]["context"]

    assert context["period"] == 1
    assert context["logtime"] == 4
    assert context["max_periods"] == 100
    assert context["run_index"] == 1
    assert context["rng_seed"] == 1901


def test_vn_period_plan_rejects_non_boolean_carryover_flag() -> None:
    with pytest.raises(ValueError, match="carry_forward_vn_state must be a boolean"):
        build_vn_agrsich_replay_fixture_from_period_plan(
            _period_plan(carry_forward_vn_state="false")
        )


def test_vn_period_plan_rejects_non_list_legacy_targets() -> None:
    data = _period_plan()
    data["legacy_targets"] = {"legacy_path": "reference.dat"}

    with pytest.raises(ValueError, match="legacy_targets must be a list"):
        build_vn_agrsich_replay_fixture_from_period_plan(data)


def test_vn_period_plan_rejects_unknown_entity_update() -> None:
    data = _period_plan()
    data["period_updates"][0]["insurers"] = [{"entity_id": 999, "name": "missing"}]

    with pytest.raises(ValueError, match="unknown insurers entity_id: 999"):
        build_vn_agrsich_replay_fixture_from_period_plan(data)


def test_vn_period_plan_rejects_non_list_entity_updates() -> None:
    data = _period_plan()
    data["period_updates"][0]["insurers"] = None

    with pytest.raises(ValueError, match="field insurers must be a list"):
        build_vn_agrsich_replay_fixture_from_period_plan(data)

    data = _period_plan()
    data["period_updates"][0]["policyholders"] = {"entity_id": 21}

    with pytest.raises(ValueError, match="field policyholders must be a list"):
        build_vn_agrsich_replay_fixture_from_period_plan(data)


def test_vn_period_plan_rejects_non_list_snapshots() -> None:
    data = _period_plan()
    data["period_updates"][0]["vn_damage_settlement_snapshots"] = {"policyholder_id": 21}

    with pytest.raises(ValueError, match="vn_damage_settlement_snapshots must be a list"):
        build_vn_agrsich_replay_fixture_from_period_plan(data)


def test_vn_period_plan_api_import_shapes() -> None:
    assert VNAgrsichReplayPlan is not None
    assert VNAgrsichReplayPeriodUpdate is not None
