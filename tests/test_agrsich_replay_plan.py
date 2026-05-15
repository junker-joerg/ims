import json
from pathlib import Path

from ims.engine.replay_plan import (
    ReplayPlan,
    ReplayPeriodUpdate,
    build_replay_fixture_from_period_plan,
    run_agrsich_replay_from_period_plan_fixture,
)


FIXTURE_DIR = Path("tests/fixtures")


def _non_empty_lines(path: Path) -> list[str]:
    return [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def test_period_plan_builds_replay_snapshots_from_start_state() -> None:
    data = json.loads((FIXTURE_DIR / "replay_vu14_period_plan.json").read_text(encoding="utf-8"))

    replay_fixture = build_replay_fixture_from_period_plan(data)

    assert replay_fixture["legacy_window"]["start_period"] == 1
    assert [snapshot["context"]["period"] for snapshot in replay_fixture["snapshots"]] == [1, 2, 3, 4]
    assert [snapshot["insurers"][0]["premiums_current"] for snapshot in replay_fixture["snapshots"]] == [
        101.0,
        102.0,
        103.0,
        104.0,
    ]
    assert replay_fixture["snapshots"][0]["insurers"][0]["name"] == "Replay VU 14"


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
    data["period_updates"][1]["insurers"][0]["reserves_current"] = [999.0, 254.0]
    plan_path = tmp_path / "bad_plan.json"
    plan_path.write_text(json.dumps(data), encoding="utf-8")

    result = run_agrsich_replay_from_period_plan_fixture(plan_path, tmp_path / "out")

    assert result.legacy_comparison is not None
    assert result.legacy_comparison.matches is False
    bad_rows = [row for row in result.legacy_comparison.row_comparisons if not row.matches]
    assert [row.global_period for row in bad_rows] == [2]
    assert any(field.name == "Rs1" and field.matches is False for field in bad_rows[0].field_comparisons)


def test_period_plan_api_import_shapes() -> None:
    assert ReplayPlan is not None
    assert ReplayPeriodUpdate is not None
