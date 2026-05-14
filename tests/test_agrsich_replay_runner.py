import json
from pathlib import Path

from ims.engine.replay_runner import (
    ReplayRunResult,
    run_agrsich_replay_from_fixture,
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


def test_load_scenario_from_mapping_matches_file_loader_shape() -> None:
    data = json.loads((FIXTURE_DIR / "replay_vu14_window.json").read_text(encoding="utf-8"))

    scenario = load_scenario_from_mapping(data["snapshots"][0])

    assert scenario.context.period == 1
    assert scenario.context.max_periods == 100
    assert scenario.bav.entity_id == 1
    assert [insurer.entity_id for insurer in scenario.insurers] == [14]
    assert scenario.insurers[0].reserves_current == [202.0, 252.0]


def test_replay_runner_appends_vu14_window_and_matches_legacy(tmp_path: Path) -> None:
    result = run_agrsich_replay_from_fixture(FIXTURE_DIR / "replay_vu14_window.json", tmp_path)
    export_path = tmp_path / "imsvu014.dat"
    lines = _non_empty_lines(export_path)

    assert isinstance(result, ReplayRunResult)
    assert result.processed_periods == [1, 2, 3, 4]
    assert export_path in result.written_files
    assert lines[0].startswith("#t Pr1")
    assert sum(1 for line in lines if line.startswith("#t ")) == 1
    assert [int(line.split()[0]) for line in lines[1:]] == [1, 2, 3, 4]
    assert len(set(line.split()[0] for line in lines[1:])) == 4
    assert isinstance(result.legacy_comparison, LegacyWindowComparison)
    assert result.legacy_comparison.matches is True


def test_replay_runner_appends_vusk1_window_and_matches_legacy(tmp_path: Path) -> None:
    result = run_agrsich_replay_from_fixture(FIXTURE_DIR / "replay_vusk1_window.json", tmp_path)
    export_path = tmp_path / "imsvusk1.dat"
    lines = _non_empty_lines(export_path)

    assert result.processed_periods == [101, 102, 103, 104]
    assert export_path in result.written_files
    assert sum(1 for line in lines if line.startswith("#t ")) == 1
    assert [int(line.split()[0]) for line in lines[1:]] == [101, 102, 103, 104]
    assert len(set(line.split()[0] for line in lines[1:])) == 4
    assert result.legacy_comparison is not None
    assert result.legacy_comparison.matches is True


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
