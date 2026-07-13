import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from ims.api.controlled_execution_adapter_contract import (
    ControlledExecutionAdapterContract,
    build_controlled_execution_adapter_contract,
    controlled_execution_adapter_contract_payload,
    main,
)


def test_controlled_execution_adapter_contract_reports_stable_boundaries() -> None:
    payload = build_controlled_execution_adapter_contract().to_dict()

    assert payload["status"] == "ok"
    assert payload["mode"] == "controlled_execution_adapter_contract"
    assert payload["schema_version"] == "ims.workbench.metadata.v1"
    assert payload["adapter_mode"] == "explicit_multi_period_fixture_adapter"
    assert payload["expected_summary_mode"] == "explicit_multi_period_execution_summary"
    assert (
        payload["source_runner"]
        == "ims.engine.explicit_period_runner.run_explicit_multi_period_from_fixture"
    )
    assert (
        payload["summary_builder"]
        == "ims.engine.explicit_period_runner.build_explicit_multi_period_execution_summary"
    )
    assert payload["contract_only"] is True
    assert payload["http_enabled"] is False
    assert payload["ui_enabled"] is False
    assert payload["queue_worker_enabled"] is False
    assert payload["runner_start_enabled"] is False
    assert payload["writes_enabled"] is False
    assert payload["execution_enabled"] is False
    assert payload["writes_performed"] is False
    assert payload["execution_performed"] is False
    assert payload["simulation_performed"] is False
    assert payload["automatic_historical_rule_selection_performed"] is False


def test_controlled_execution_adapter_contract_lists_inputs_and_summary_shape() -> None:
    payload = controlled_execution_adapter_contract_payload()

    assert payload["accepted_fixture_kinds"] == [
        "explicit_vu_vn_period_plan_fixture",
        "explicit_multi_period_fixture",
    ]
    assert payload["expected_inputs"] == [
        "fixture_path",
        "adapter_mode",
        "explicit_execution_release",
        "expected_summary_contract",
        "carry_forward_vu_state",
        "carry_forward_vn_state",
    ]
    assert payload["required_preconditions"] == [
        "three_fachliche_regression_tests_green",
        "controlled_execution_adapter_plan_reviewed",
        "execution_release_explicit",
        "execution_enabled_false_in_run_control_metadata",
        "api_ui_queue_start_paths_disabled",
    ]
    assert payload["expected_summary_fields"] == [
        "mode",
        "period_count",
        "processed_local_periods",
        "processed_global_periods",
        "total_vu_rule_applications",
        "total_vn_insurance_rule_applications",
        "total_vn_settlement_applications",
        "total_vn_damage_settlement_applications",
        "carryover_count",
        "vu_carryover_count",
        "vn_carryover_count",
        "written_file_count",
        "legacy_comparison_performed",
        "legacy_comparison_matches",
        "legacy_report_written_file_count",
        "writes_performed",
        "execution_performed",
        "automatic_historical_rule_selection_performed",
        "simulation_performed",
    ]
    assert "browser_upload" in payload["forbidden_inputs"]
    assert "execution_enabled_true_from_queue_metadata" in payload["forbidden_inputs"]
    assert "legacy_full_equality_expectation" in payload["forbidden_inputs"]
    assert "runner_start_from_contract" in payload["forbidden_boundaries"]
    assert "historical_full_equality_claim" in payload["forbidden_boundaries"]


def test_controlled_execution_adapter_contract_cli_prints_json_without_writing(
    tmp_path, monkeypatch, capsys
) -> None:
    monkeypatch.chdir(tmp_path)

    exit_code = main([])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["mode"] == "controlled_execution_adapter_contract"
    assert payload["runner_start_enabled"] is False
    assert payload["execution_performed"] is False
    assert not (tmp_path / ".ims_workbench" / "metadata.sqlite").exists()
    assert ControlledExecutionAdapterContract is not None


def test_controlled_execution_adapter_contract_rejects_arguments(capsys) -> None:
    with pytest.raises(SystemExit):
        main(["--fixture", "tests/fixtures/replay_vu14_period_plan.json"])

    assert capsys.readouterr().out == ""


def test_controlled_execution_adapter_contract_module_entrypoint_rejects_arguments() -> None:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path(__file__).resolve().parent.parent / "python_port")
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "ims.api.controlled_execution_adapter_contract",
            "--run",
        ],
        capture_output=True,
        check=False,
        env=env,
        text=True,
    )

    assert completed.returncode != 0
    assert "does not accept arguments" in completed.stderr
    assert completed.stdout == ""
