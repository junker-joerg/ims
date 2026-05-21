import json
from pathlib import Path

import pytest

from ims.engine.vn_agrsich_replay import (
    VNAgrsichReplayPeriodResult,
    VNAgrsichReplayRunResult,
    run_vn_agrsich_replay_from_fixture,
    run_vn_agrsich_replay_from_mappings,
)


def _damage_parameters() -> dict:
    return {
        "damage_intercept_normal": [5.0, 7.0],
        "damage_factor_normal": [2.0, 3.0],
        "damage_intercept_shock": [50.0, 70.0],
        "damage_factor_shock": [20.0, 30.0],
    }


def _period_scenario(period: int, *, policyholder_id: int = 21) -> dict:
    return {
        "context": {"period": period, "max_periods": 12, "run_index": 0},
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
        "vn_damage_settlement_snapshots": [
            {
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
        ],
    }


def _non_empty_lines(path: Path) -> list[str]:
    return [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def test_vn_agrsich_replay_runs_periods_and_writes_mutated_exports(tmp_path: Path) -> None:
    result = run_vn_agrsich_replay_from_mappings(
        [_period_scenario(1), _period_scenario(2, policyholder_id=22)],
        tmp_path,
    )

    assert isinstance(result, VNAgrsichReplayRunResult)
    assert isinstance(result.period_results[0], VNAgrsichReplayPeriodResult)
    assert result.processed_periods == [1, 2]
    assert result.total_damage_settlement_applications == 2
    assert result.total_settlement_applications == 2
    assert {path.name for path in result.written_files} >= {"imsvu011.dat", "imsvnr05.dat"}

    insurer_lines = _non_empty_lines(tmp_path / "imsvu011.dat")
    assert insurer_lines[0].startswith("#t ")
    assert insurer_lines[1].split() == [
        "1",
        "4.0",
        "0.0",
        "35.0",
        "4.0",
        "1",
        "9.0",
        "6.0",
        "0.0",
        "60.0",
        "4.0",
        "0",
        "0.0",
    ]

    policyholder_lines = _non_empty_lines(tmp_path / "imsvnr05.dat")
    assert policyholder_lines[0].startswith("#t ")
    assert policyholder_lines[1].split() == [
        "1",
        "11",
        "1.0",
        "4.0",
        "87.0",
        "9.0",
        "11",
        "0.0",
        "0.0",
        "100.0",
        "0.0",
        "87.0",
    ]


def test_vn_agrsich_replay_loads_fixture(tmp_path: Path) -> None:
    fixture_path = tmp_path / "vn_agrsich_periods.json"
    fixture_path.write_text(
        json.dumps({"periods": [_period_scenario(1), _period_scenario(2, policyholder_id=22)]}),
        encoding="utf-8",
    )

    result = run_vn_agrsich_replay_from_fixture(fixture_path, tmp_path / "out")

    assert result.processed_periods == [1, 2]
    assert (tmp_path / "out" / "imsvu011.dat").exists()


def test_vn_agrsich_replay_rejects_duplicate_or_unsorted_periods(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="duplicate periods"):
        run_vn_agrsich_replay_from_mappings(
            [_period_scenario(1), _period_scenario(1, policyholder_id=22)],
            tmp_path,
        )

    with pytest.raises(ValueError, match="increasing periods"):
        run_vn_agrsich_replay_from_mappings(
            [_period_scenario(2), _period_scenario(1, policyholder_id=22)],
            tmp_path,
        )
