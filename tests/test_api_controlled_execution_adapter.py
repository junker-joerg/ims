import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from ims.api.controlled_execution_adapter import (
    ControlledExecutionAdapterResult,
    detect_controlled_execution_fixture_kind,
    main,
    run_controlled_execution_adapter,
)


REPO_ROOT = Path(__file__).resolve().parent.parent
PLAN_FIXTURE = REPO_ROOT / "tests" / "fixtures" / "replay_vn_policyholder_transition_plan.json"


def _minimal_period(period: int) -> dict[str, object]:
    return {
        "context": {"period": period, "max_periods": 12, "run_index": 0, "rng_seed": 5000 + period},
        "bav": {"entity_id": 1, "name": "Adapter-Test-BAV"},
        "insurers": [
            {
                "entity_id": 10,
                "name": "Adapter-Test-VU",
                "active": True,
                "active_prev": True,
                "rule_id": 1,
                "rule_class": 1,
                "premiums_current": 10.0 + period,
                "advertising_current": 1.0,
                "reserves_current": [20.0, 30.0],
                "policyholders_current": 0.0,
                "claims_count_current": [0, 0],
                "claims_sum_current": [0.0, 0.0],
            }
        ],
        "policyholders": [],
    }


def _write_explicit_fixture(tmp_path: Path) -> Path:
    fixture_path = tmp_path / "explicit_periods.json"
    fixture_path.write_text(
        json.dumps({"periods": [_minimal_period(1), _minimal_period(2)]}),
        encoding="utf-8",
    )
    return fixture_path


def test_controlled_execution_adapter_requires_explicit_release(tmp_path: Path) -> None:
    fixture_path = _write_explicit_fixture(tmp_path)

    with pytest.raises(ValueError, match="explicit_execution_release"):
        run_controlled_execution_adapter(fixture_path)


def test_controlled_execution_adapter_runs_explicit_fixture_without_writes(tmp_path: Path) -> None:
    fixture_path = _write_explicit_fixture(tmp_path)

    result = run_controlled_execution_adapter(
        fixture_path,
        explicit_execution_release=True,
    )
    payload = result.to_dict()

    assert isinstance(result, ControlledExecutionAdapterResult)
    assert payload["mode"] == "controlled_execution_adapter"
    assert payload["fixture_kind"] == "explicit_multi_period_fixture"
    assert payload["explicit_execution_release"] is True
    assert payload["http_enabled"] is False
    assert payload["ui_enabled"] is False
    assert payload["queue_worker_enabled"] is False
    assert payload["writes_enabled"] is False
    assert payload["writes_performed"] is False
    assert payload["execution_performed"] is True
    assert payload["simulation_performed"] is False
    assert payload["automatic_historical_rule_selection_performed"] is False
    assert payload["historical_full_equality_claimed"] is False
    assert payload["summary"]["mode"] == "explicit_multi_period_execution_summary"
    assert payload["summary"]["period_count"] == 2
    assert payload["summary"]["written_file_count"] == 0
    assert not (tmp_path / "imsvu010.dat").exists()


def test_controlled_execution_adapter_runs_plan_fixture_without_output_path() -> None:
    result = run_controlled_execution_adapter(
        PLAN_FIXTURE,
        explicit_execution_release=True,
    )
    payload = result.to_dict()

    assert payload["fixture_kind"] == "explicit_vu_vn_period_plan_fixture"
    assert payload["summary"]["mode"] == "explicit_multi_period_execution_summary"
    assert payload["summary"]["period_count"] == 2
    assert payload["summary"]["processed_global_periods"] == [21, 22]
    assert payload["summary"]["writes_performed"] is False
    assert payload["summary"]["simulation_performed"] is False


def test_controlled_execution_adapter_cli_prints_json_without_output_files(tmp_path: Path, capsys) -> None:
    fixture_path = _write_explicit_fixture(tmp_path)

    exit_code = main(["--fixture", str(fixture_path), "--explicit-execution-release"])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["mode"] == "controlled_execution_adapter"
    assert payload["summary"]["execution_performed"] is True
    assert payload["summary"]["writes_performed"] is False
    assert {path.name for path in tmp_path.iterdir()} == {"explicit_periods.json"}


def test_controlled_execution_adapter_rejects_free_output_path(tmp_path: Path) -> None:
    fixture_path = _write_explicit_fixture(tmp_path)
    env = os.environ.copy()
    env["PYTHONPATH"] = str(REPO_ROOT / "python_port")
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "ims.api.controlled_execution_adapter",
            "--fixture",
            str(fixture_path),
            "--explicit-execution-release",
            "--output-dir",
            str(tmp_path / "out"),
        ],
        capture_output=True,
        check=False,
        env=env,
        text=True,
    )

    assert completed.returncode != 0
    assert "unrecognized arguments" in completed.stderr
    assert not (tmp_path / "out").exists()


def test_controlled_execution_adapter_detects_fixture_kind(tmp_path: Path) -> None:
    fixture_path = _write_explicit_fixture(tmp_path)

    assert detect_controlled_execution_fixture_kind(fixture_path) == "explicit_multi_period_fixture"
    assert detect_controlled_execution_fixture_kind(PLAN_FIXTURE) == "explicit_vu_vn_period_plan_fixture"
