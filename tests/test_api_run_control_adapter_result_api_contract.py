import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from ims.api.run_control_adapter_result_api_contract import (
    RunControlAdapterResultApiContract,
    build_run_control_adapter_result_api_contract,
    main,
    run_control_adapter_result_api_contract_payload,
)


def test_run_control_adapter_result_api_contract_reports_readonly_endpoint_shape() -> None:
    payload = run_control_adapter_result_api_contract_payload()

    assert payload["status"] == "ok"
    assert payload["mode"] == "run_control_adapter_result_api_contract"
    assert payload["schema_version"] == "ims.workbench.metadata.v1"
    assert payload["endpoint"] == "/api/run-control/adapter-result-contract"
    assert payload["expected_result_mode"] == "controlled_execution_adapter"
    assert payload["expected_validation_mode"] == "run_control_adapter_result_validation"
    assert payload["expected_contract_mode"] == "run_control_adapter_result_contract"
    assert payload["source_contract_module"] == "ims.api.run_control_adapter_result_contract"
    assert "precomputed_controlled_execution_adapter_json" in payload["expected_inputs"]
    assert "local_run_control_adapter_result_contract_check" in payload["expected_inputs"]
    assert "adapter_result_payload_precomputed_outside_api" in payload["required_preconditions"]
    assert "summary" in payload["accepted_result_fields"]
    assert "simulation_performed" in payload["accepted_summary_fields"]
    assert "browser_upload" in payload["forbidden_fields"]
    assert "adapter_start_from_run_control" in payload["forbidden_boundaries"]
    assert "http_payload_validation" in payload["forbidden_boundaries"]
    assert "browser_file_picker" in payload["forbidden_boundaries"]
    assert payload["precomputed_result_required"] is True
    assert payload["api_accepts_result_payload"] is False
    assert payload["api_validates_result_payload"] is False
    assert payload["api_starts_adapter"] is False
    assert payload["http_enabled"] is True
    assert payload["ui_enabled"] is False
    assert payload["queue_worker_enabled"] is False
    assert payload["writes_performed"] is False
    assert payload["execution_performed"] is False
    assert payload["simulation_performed"] is False
    assert isinstance(build_run_control_adapter_result_api_contract(), RunControlAdapterResultApiContract)


def test_run_control_adapter_result_api_contract_cli_prints_json_without_writing(
    tmp_path, monkeypatch, capsys
) -> None:
    monkeypatch.chdir(tmp_path)

    exit_code = main([])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["mode"] == "run_control_adapter_result_api_contract"
    assert payload["api_accepts_result_payload"] is False
    assert payload["api_starts_adapter"] is False
    assert not (tmp_path / ".ims_workbench" / "metadata.sqlite").exists()


def test_run_control_adapter_result_api_contract_rejects_arguments(capsys) -> None:
    with pytest.raises(SystemExit):
        main(["check", "adapter_result.json"])

    assert capsys.readouterr().out == ""


def test_run_control_adapter_result_api_contract_module_entrypoint_rejects_arguments() -> None:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path(__file__).resolve().parent.parent / "python_port")
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "ims.api.run_control_adapter_result_api_contract",
            "adapter_result.json",
        ],
        capture_output=True,
        check=False,
        env=env,
        text=True,
    )

    assert completed.returncode != 0
    assert "does not accept arguments" in completed.stderr
    assert completed.stdout == ""
