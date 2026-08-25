import json
from pathlib import Path

import pytest

from ims.engine.replay_runner import (
    ReplayLegacyTarget,
    ReplayRunResult,
    run_agrsich_replay_from_fixture,
    run_agrsich_replay_from_mapping,
)
from ims.io.scenario_loader import load_scenario_from_mapping
from ims.model.legacy_agrsich_reference import (
    LegacyWindowComparison,
    compare_export_file_to_legacy_window,
    parse_legacy_insurer_dat,
)


FIXTURE_DIR = Path("tests/fixtures")
REFERENCE_DIR = Path("tests/references/legacy_agrsich")


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


def _vu_rule_snapshot(period: int, *, max_periods: int = 0, run_index: int = 0) -> dict:
    return {
        "context": {
            "period": period,
            "logtime": period + 10,
            "max_periods": max_periods,
            "run_index": run_index,
        },
        "bav": {"entity_id": 1, "name": "BAV"},
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
    }


def test_load_scenario_from_mapping_matches_file_loader_shape() -> None:
    data = json.loads((FIXTURE_DIR / "replay_vu14_window.json").read_text(encoding="utf-8"))

    scenario = load_scenario_from_mapping(data["snapshots"][0])

    assert scenario.context.period == 1
    assert scenario.context.max_periods == 100
    assert scenario.bav.entity_id == 1
    assert [insurer.entity_id for insurer in scenario.insurers] == [14]
    assert scenario.insurers[0].reserves_current == [0.0, 0.0]


def test_replay_runner_appends_vu14_window_and_matches_legacy(tmp_path: Path) -> None:
    result = run_agrsich_replay_from_fixture(FIXTURE_DIR / "replay_vu14_window.json", tmp_path)
    export_path = tmp_path / "imsvu014.dat"
    lines = _non_empty_lines(export_path)

    assert isinstance(result, ReplayRunResult)
    assert result.processed_periods == [1, 2, 3, 4]
    assert result.processed_local_periods == [1, 2, 3, 4]
    assert result.processed_global_periods == [1, 2, 3, 4]
    assert export_path in result.written_files
    assert lines[0].startswith("#t Pr1")
    assert sum(1 for line in lines if line.startswith("#t ")) == 1
    assert [int(line.split()[0]) for line in lines[1:]] == [1, 2, 3, 4]
    assert len(set(line.split()[0] for line in lines[1:])) == 4
    assert isinstance(result.legacy_comparison, LegacyWindowComparison)
    assert result.legacy_comparison.matches is True
    assert result.validation_report is not None
    assert result.validation_report.matches is True
    assert result.validation_report.total_rows == 4
    assert result.carryovers == []
    assert len(result.vu_period_results) == 4


def test_replay_runner_appends_vusk1_window_and_matches_legacy(tmp_path: Path) -> None:
    result = run_agrsich_replay_from_fixture(FIXTURE_DIR / "replay_vusk1_window.json", tmp_path)
    export_path = tmp_path / "imsvusk1.dat"
    lines = _non_empty_lines(export_path)

    assert result.processed_periods == [101, 102, 103, 104]
    assert result.processed_local_periods == [1, 2, 3, 4]
    assert result.processed_global_periods == [101, 102, 103, 104]
    assert export_path in result.written_files
    assert sum(1 for line in lines if line.startswith("#t ")) == 1
    assert [int(line.split()[0]) for line in lines[1:]] == [101, 102, 103, 104]
    assert len(set(line.split()[0] for line in lines[1:])) == 4
    assert result.legacy_comparison is not None
    assert result.legacy_comparison.matches is True
    assert result.validation_report is not None
    assert result.validation_report.file_summaries[0].filename == "imsvusk1.dat"


def test_compare_export_file_to_legacy_window_detects_targeted_deviation(tmp_path: Path) -> None:
    result = run_agrsich_replay_from_fixture(FIXTURE_DIR / "replay_vu14_window.json", tmp_path)
    export_path = tmp_path / "imsvu014.dat"
    lines = _non_empty_lines(export_path)
    parts = lines[2].split()
    parts[3] = "999.0"
    lines[2] = " ".join(parts)
    export_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    legacy_table = parse_legacy_insurer_dat(REFERENCE_DIR / "VU14L1.DAT")
    comparison = compare_export_file_to_legacy_window(export_path, legacy_table, 1, 4)

    assert result.legacy_comparison is not None
    assert result.legacy_comparison.matches is True
    assert comparison.matches is False
    bad_rows = [row for row in comparison.row_comparisons if not row.matches]
    assert [row.global_period for row in bad_rows] == [2]
    assert any(field.name == "Rs1" and field.matches is False for field in bad_rows[0].field_comparisons)


def test_compare_export_file_to_legacy_window_rejects_duplicate_period(tmp_path: Path) -> None:
    run_agrsich_replay_from_fixture(FIXTURE_DIR / "replay_vusk1_window.json", tmp_path)
    export_path = tmp_path / "imsvusk1.dat"
    lines = _non_empty_lines(export_path)
    lines.append(lines[1])
    export_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    legacy_table = parse_legacy_insurer_dat(REFERENCE_DIR / "VUSK1L4.DAT")
    comparison = compare_export_file_to_legacy_window(export_path, legacy_table, 101, 104)

    assert comparison.matches is False
    assert comparison.row_comparisons[-1].field_comparisons[0].expected == "unique global period"


def test_replay_runner_applies_vu_rule_snapshots_before_export(tmp_path: Path) -> None:
    result = run_agrsich_replay_from_mapping({"snapshots": [_vu_rule_snapshot(2)]}, tmp_path)
    export_path = tmp_path / "imsvu010.dat"
    lines = _non_empty_lines(export_path)

    assert result.carryovers == []
    assert len(result.vu_period_results) == 1
    assert len(result.vu_period_results[0].rule_applications) == 1
    assert lines[1].split() == [
        "2",
        "51.0",
        "4.0",
        "52.5",
        "30.0",
        "2",
        "250.0",
        "52.0",
        "8.0",
        "63.0",
        "80.0",
        "4",
        "600.0",
    ]


def test_replay_runner_compares_legacy_targets_and_writes_report(tmp_path: Path) -> None:
    legacy_path = tmp_path / "reference_imsvu010.dat"
    legacy_path.write_text(
        "\n".join(
            [
                "#t Pr1 Wer1 Rs1 Vn1 Sc1 Sh1 Pr2 Wer2 Rs2 Vn2 Sc2 Sh2",
                "2 51.0 4.0 52.5 30.0 2 250.0 52.0 8.0 63.0 80.0 4 600.0",
                "",
            ]
        ),
        encoding="utf-8",
    )

    result = run_agrsich_replay_from_mapping(
        {"snapshots": [_vu_rule_snapshot(2)]},
        tmp_path / "out",
        legacy_targets=[
            ReplayLegacyTarget(
                legacy_path=legacy_path,
                export_filename="imsvu010.dat",
                subject_type="insurer",
            )
        ],
        legacy_report_name="vu_replay_validation",
    )

    assert result.legacy_target_comparison is not None
    assert result.legacy_target_comparison.matches is True
    assert result.validation_report is not None
    assert result.validation_report.matches is True
    assert [path.name for path in result.written_legacy_report_files] == [
        "vu_replay_validation.json",
        "vu_replay_validation.csv",
        "vu_replay_validation_fields.csv",
        "vu_replay_validation_groups.csv",
        "vu_replay_validation_periods.csv",
        "vu_replay_validation_deviations.csv",
    ]


def test_replay_runner_fixture_loads_legacy_targets(tmp_path: Path) -> None:
    legacy_path = tmp_path / "legacy" / "reference_imsvu010.dat"
    legacy_path.parent.mkdir()
    legacy_path.write_text(
        "\n".join(
            [
                "#t Pr1 Wer1 Rs1 Vn1 Sc1 Sh1 Pr2 Wer2 Rs2 Vn2 Sc2 Sh2",
                "2 51.0 4.0 52.5 30.0 2 250.0 52.0 8.0 63.0 80.0 4 600.0",
                "",
            ]
        ),
        encoding="utf-8",
    )
    fixture_path = tmp_path / "vu_replay_with_legacy_targets.json"
    fixture_path.write_text(
        json.dumps(
            {
                "snapshots": [_vu_rule_snapshot(2)],
                "legacy_report_name": "fixture_vu_report",
                "legacy_targets": [
                    {
                        "legacy_path": "legacy/reference_imsvu010.dat",
                        "export_filename": "imsvu010.dat",
                        "subject_type": "insurer",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    result = run_agrsich_replay_from_fixture(fixture_path, tmp_path / "out")

    assert result.legacy_target_comparison is not None
    assert result.legacy_target_comparison.matches is True
    assert (tmp_path / "out" / "fixture_vu_report.json").exists()


def test_replay_runner_can_carry_vu_state_into_followup_export(tmp_path: Path) -> None:
    result = run_agrsich_replay_from_mapping(
        {"snapshots": [_vu_rule_snapshot(2), _vu_rule_snapshot(3)]},
        tmp_path,
        carry_forward_insurer_state=True,
    )
    export_path = tmp_path / "imsvu010.dat"
    lines = _non_empty_lines(export_path)

    assert len(result.carryovers) == 1
    assert result.carryovers[0].from_period == 2
    assert result.carryovers[0].to_period == 3
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


def test_replay_runner_reports_local_and_global_periods_across_runs(tmp_path: Path) -> None:
    result = run_agrsich_replay_from_mapping(
        {
            "snapshots": [
                _vu_rule_snapshot(2, max_periods=12, run_index=0),
                _vu_rule_snapshot(2, max_periods=12, run_index=1),
            ]
        },
        tmp_path,
        carry_forward_insurer_state=True,
    )

    assert result.processed_periods == [2, 14]
    assert result.processed_local_periods == [2, 2]
    assert result.processed_global_periods == [2, 14]
    assert [period_result.period for period_result in result.period_results] == [2, 2]
    assert [period_result.global_period for period_result in result.period_results] == [2, 14]
    assert result.carryovers[0].from_period == 2
    assert result.carryovers[0].to_period == 2
    assert result.carryovers[0].from_global_period == 2
    assert result.carryovers[0].to_global_period == 14


def test_replay_runner_fixture_supports_vu_carryover(tmp_path: Path) -> None:
    fixture_path = tmp_path / "vu_replay_carry.json"
    fixture_path.write_text(
        json.dumps(
            {
                "carry_forward_insurer_state": True,
                "snapshots": [_vu_rule_snapshot(2), _vu_rule_snapshot(3)],
            }
        ),
        encoding="utf-8",
    )

    result = run_agrsich_replay_from_fixture(fixture_path, tmp_path / "out")

    assert result.carryovers[0].insurer_ids == [10]
    assert result.vu_period_results[1].foreign_info.insurer.dp == [51.0, 52.0]


def test_replay_runner_fixture_rejects_non_boolean_vu_carryover_flag(tmp_path: Path) -> None:
    fixture_path = tmp_path / "bad_vu_replay_carry.json"
    fixture_path.write_text(
        json.dumps(
            {
                "carry_forward_insurer_state": "false",
                "snapshots": [_vu_rule_snapshot(2)],
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="carry_forward_insurer_state must be a boolean"):
        run_agrsich_replay_from_fixture(fixture_path, tmp_path / "out")


def test_replay_runner_rejects_unsorted_periods_before_vu_carryover(tmp_path: Path) -> None:
    output_dir = tmp_path / "out"

    with pytest.raises(ValueError, match="increasing replay periods"):
        run_agrsich_replay_from_mapping(
            {"snapshots": [_vu_rule_snapshot(5), _vu_rule_snapshot(3)]},
            output_dir,
            carry_forward_insurer_state=True,
        )

    assert not output_dir.exists()


def test_replay_runner_rejects_duplicate_periods_before_vu_carryover(tmp_path: Path) -> None:
    output_dir = tmp_path / "out"

    with pytest.raises(ValueError, match="duplicate replay periods"):
        run_agrsich_replay_from_mapping(
            {"snapshots": [_vu_rule_snapshot(3), _vu_rule_snapshot(3)]},
            output_dir,
            carry_forward_insurer_state=True,
        )

    assert not output_dir.exists()


def test_replay_runner_fixture_carryover_rejects_unsorted_periods(tmp_path: Path) -> None:
    fixture_path = tmp_path / "unsorted_vu_replay_carry.json"
    fixture_path.write_text(
        json.dumps(
            {
                "carry_forward_insurer_state": True,
                "snapshots": [_vu_rule_snapshot(5), _vu_rule_snapshot(3)],
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="increasing replay periods"):
        run_agrsich_replay_from_fixture(fixture_path, tmp_path / "out")
