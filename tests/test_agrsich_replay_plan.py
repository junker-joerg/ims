import json
from pathlib import Path

import pytest

from ims.engine.replay_plan import (
    ReplayPlan,
    ReplayPeriodUpdate,
    build_replay_fixture_from_period_plan,
    run_agrsich_replay_from_period_plan_fixture,
)


FIXTURE_DIR = Path("tests/fixtures")


def _non_empty_lines(path: Path) -> list[str]:
    return [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _vu_rule_parameters() -> dict[str, list[float]]:
    return {
        "premium_intercept_normal": [1.0, 2.0],
        "premium_factor_normal": [0.5, 0.25],
        "advertising_intercept_normal": [3.0, 4.0],
        "advertising_factor_normal": [0.1, 0.2],
        "premium_intercept_shock": [10.0, 20.0],
        "premium_factor_shock": [1.0, 2.0],
        "advertising_intercept_shock": [30.0, 40.0],
        "advertising_factor_shock": [3.0, 4.0],
    }


def _vu_rule_period_plan(*, carry_forward_insurer_state: object = True) -> dict:
    return {
        "metadata": {"purpose": "small rule-driven carryover plan"},
        "carry_forward_insurer_state": carry_forward_insurer_state,
        "base_snapshot": {
            "context": {"period": 0, "logtime": 0, "max_periods": 0, "run_index": 0, "rng_seed": 9000},
            "bav": {"entity_id": 1, "name": "Plan-BAV"},
            "insurers": [
                {
                    "entity_id": 10,
                    "name": "VU-10",
                    "active": True,
                    "active_prev": True,
                    "rule_id": 1,
                    "rule_class": 1,
                    "premiums_prev_sector": [100.0, 200.0],
                    "advertising_prev_sector": [10.0, 20.0],
                    "reserves_prev_sector": [1000.0, 100.0],
                    "reserves_current": [50.0, 60.0],
                    "policyholders_current": 30.0,
                    "policyholders_current_sector": [30.0, 80.0],
                    "claims_count_current": [2, 4],
                    "claims_sum_current": [250.0, 600.0],
                }
            ],
            "policyholders": [],
            "vu_foreign_info_rule_snapshots": [
                {
                    "insurer_id": 10,
                    "rule_kind": "average",
                    "interest_rate": 0.05,
                    "parameters": _vu_rule_parameters(),
                }
            ],
        },
        "period_updates": [
            {"context": {"period": 2, "run_index": 0, "rng_seed": 9002}, "insurers": [], "policyholders": []},
            {"context": {"period": 3, "run_index": 0, "rng_seed": 9003}, "insurers": [], "policyholders": []},
        ],
    }


def test_period_plan_builds_replay_snapshots_from_start_state() -> None:
    data = json.loads((FIXTURE_DIR / "replay_vu14_period_plan.json").read_text(encoding="utf-8"))

    replay_fixture = build_replay_fixture_from_period_plan(data)

    assert replay_fixture["legacy_window"]["start_period"] == 1
    assert replay_fixture["carry_forward_insurer_state"] is False
    assert [snapshot["context"]["period"] for snapshot in replay_fixture["snapshots"]] == [1, 2, 3, 4]
    assert [snapshot["insurers"][0]["premiums_current"] for snapshot in replay_fixture["snapshots"]] == [
        40.0,
        39.2,
        38.4,
        37.6,
    ]
    assert replay_fixture["snapshots"][0]["insurers"][0]["name"] == "Replay VU 14"


def test_period_plan_preserves_legacy_targets_in_fixture() -> None:
    data = _vu_rule_period_plan()
    data["legacy_report_name"] = "vu_plan_validation"
    data["legacy_targets"] = [
        {
            "legacy_path": "legacy/reference_imsvu010.dat",
            "export_filename": "imsvu010.dat",
            "subject_type": "insurer",
        }
    ]

    replay_fixture = build_replay_fixture_from_period_plan(data)

    assert replay_fixture["legacy_report_name"] == "vu_plan_validation"
    assert replay_fixture["legacy_targets"] == data["legacy_targets"]


def test_period_plan_replay_matches_vu14_legacy_window(tmp_path: Path) -> None:
    result = run_agrsich_replay_from_period_plan_fixture(
        FIXTURE_DIR / "replay_vu14_period_plan.json",
        tmp_path,
    )

    assert result.processed_periods == [1, 2, 3, 4]
    assert result.legacy_comparison is not None
    assert result.legacy_comparison.matches is True

    lines = _non_empty_lines(tmp_path / "imsvu014.dat")
    assert sum(1 for line in lines if line.startswith("#t ")) == 1
    assert [int(line.split()[0]) for line in lines[1:]] == [1, 2, 3, 4]


def test_period_plan_replay_matches_vusk1_legacy_window(tmp_path: Path) -> None:
    result = run_agrsich_replay_from_period_plan_fixture(
        FIXTURE_DIR / "replay_vusk1_period_plan.json",
        tmp_path,
    )

    assert result.processed_periods == [101, 102, 103, 104]
    assert result.legacy_comparison is not None
    assert result.legacy_comparison.matches is True

    lines = _non_empty_lines(tmp_path / "imsvusk1.dat")
    assert sum(1 for line in lines if line.startswith("#t ")) == 1
    periods = [int(line.split()[0]) for line in lines[1:]]
    assert periods == [101, 102, 103, 104]
    assert len(periods) == len(set(periods))


def test_period_plan_replay_detects_bad_update(tmp_path: Path) -> None:
    data = json.loads((FIXTURE_DIR / "replay_vu14_period_plan.json").read_text(encoding="utf-8"))
    data["legacy_window"]["legacy_path"] = str(Path("tests/references/legacy_agrsich/VU14L1.DAT").resolve())
    data["period_updates"][1]["insurers"][0]["reserves_current"] = [999.0, 36.7]
    plan_path = tmp_path / "bad_plan.json"
    plan_path.write_text(json.dumps(data), encoding="utf-8")

    result = run_agrsich_replay_from_period_plan_fixture(plan_path, tmp_path / "out")

    assert result.legacy_comparison is not None
    assert result.legacy_comparison.matches is False
    bad_rows = [row for row in result.legacy_comparison.row_comparisons if not row.matches]
    assert [row.global_period for row in bad_rows] == [2]
    assert any(field.name == "Rs1" and field.matches is False for field in bad_rows[0].field_comparisons)


def test_period_plan_can_enable_vu_carryover_in_replay_fixture() -> None:
    replay_fixture = build_replay_fixture_from_period_plan(_vu_rule_period_plan())

    assert replay_fixture["carry_forward_insurer_state"] is True
    assert [snapshot["context"]["period"] for snapshot in replay_fixture["snapshots"]] == [2, 3]


def test_period_plan_applies_context_overrides() -> None:
    data = _vu_rule_period_plan()
    data["period_updates"][0]["context"] = {
        "period": 2,
        "logtime": 5,
        "max_periods": 100,
        "run_index": 1,
        "rng_seed": 9102,
    }

    replay_fixture = build_replay_fixture_from_period_plan(data)
    context = replay_fixture["snapshots"][0]["context"]

    assert context["period"] == 2
    assert context["logtime"] == 5
    assert context["max_periods"] == 100
    assert context["run_index"] == 1
    assert context["rng_seed"] == 9102


def test_period_plan_replay_carries_rule_state_between_periods(tmp_path: Path) -> None:
    plan_path = tmp_path / "vu_rule_carry_plan.json"
    plan_path.write_text(json.dumps(_vu_rule_period_plan()), encoding="utf-8")

    result = run_agrsich_replay_from_period_plan_fixture(plan_path, tmp_path / "out")
    lines = _non_empty_lines(tmp_path / "out" / "imsvu010.dat")

    assert result.processed_periods == [2, 3]
    assert len(result.carryovers) == 1
    assert result.carryovers[0].insurer_ids == [10]
    assert len(result.vu_period_results[1].rule_applications) == 1
    assert lines[2].split() == [
        "3",
        "26.5",
        "3.4",
        "55.125",
        "30.0",
        "2",
        "250.0",
        "15.0",
        "5.6",
        "66.15",
        "80.0",
        "4",
        "600.0",
    ]


def test_period_plan_replay_runs_legacy_targets_and_writes_report(tmp_path: Path) -> None:
    legacy_path = tmp_path / "legacy" / "reference_imsvu010.dat"
    legacy_path.parent.mkdir()
    legacy_path.write_text(
        "\n".join(
            [
                "#t Pr1 Wer1 Rs1 Vn1 Sc1 Sh1 Pr2 Wer2 Rs2 Vn2 Sc2 Sh2",
                "2 51.0 4.0 52.5 30.0 2 250.0 52.0 8.0 63.0 80.0 4 600.0",
                "3 26.5 3.4 55.125 30.0 2 250.0 15.0 5.6 66.15 80.0 4 600.0",
                "",
            ]
        ),
        encoding="utf-8",
    )
    data = _vu_rule_period_plan()
    data["legacy_report_name"] = "vu_plan_validation"
    data["legacy_targets"] = [
        {
            "legacy_path": "legacy/reference_imsvu010.dat",
            "export_filename": "imsvu010.dat",
            "subject_type": "insurer",
        }
    ]
    plan_path = tmp_path / "vu_period_plan_with_legacy_targets.json"
    plan_path.write_text(json.dumps(data), encoding="utf-8")

    result = run_agrsich_replay_from_period_plan_fixture(plan_path, tmp_path / "out")

    assert result.legacy_target_comparison is not None
    assert result.legacy_target_comparison.matches is True
    assert result.validation_report is not None
    assert result.validation_report.matches is True
    assert [path.name for path in result.written_legacy_report_files] == [
        "vu_plan_validation.json",
        "vu_plan_validation.csv",
        "vu_plan_validation_fields.csv",
        "vu_plan_validation_groups.csv",
        "vu_plan_validation_periods.csv",
        "vu_plan_validation_deviations.csv",
    ]


def test_period_plan_rejects_non_boolean_vu_carryover_flag() -> None:
    with pytest.raises(ValueError, match="carry_forward_insurer_state must be a boolean"):
        build_replay_fixture_from_period_plan(
            _vu_rule_period_plan(carry_forward_insurer_state="false")
        )


def test_period_plan_rejects_non_list_legacy_targets() -> None:
    data = _vu_rule_period_plan()
    data["legacy_targets"] = {"legacy_path": "reference.dat"}

    with pytest.raises(ValueError, match="legacy_targets must be a list"):
        build_replay_fixture_from_period_plan(data)


def test_period_plan_rejects_non_list_entity_updates() -> None:
    data = _vu_rule_period_plan()
    data["period_updates"][0]["insurers"] = None

    with pytest.raises(ValueError, match="field insurers must be a list"):
        build_replay_fixture_from_period_plan(data)

    data = _vu_rule_period_plan()
    data["period_updates"][0]["policyholders"] = {"entity_id": 1}

    with pytest.raises(ValueError, match="field policyholders must be a list"):
        build_replay_fixture_from_period_plan(data)


def test_period_plan_api_import_shapes() -> None:
    assert ReplayPlan is not None
    assert ReplayPeriodUpdate is not None
