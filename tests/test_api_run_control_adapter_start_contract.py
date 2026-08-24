import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
from starlette.testclient import TestClient

from ims.api.app import create_app
from ims.api.run_control_adapter_start_contract import (
    RunControlAdapterStartContract,
    build_run_control_adapter_start_contract,
    main,
    run_control_adapter_start_contract_payload,
)


def test_run_control_adapter_start_contract_reports_hard_gated_shape() -> None:
    payload = run_control_adapter_start_contract_payload()

    assert payload["status"] == "ok"
    assert payload["mode"] == "run_control_adapter_start_contract"
    assert payload["schema_version"] == "ims.workbench.metadata.v1"
    assert payload["endpoint"] == "/api/run-control/adapter-start-contract"
    assert payload["release_check_endpoint"] == "/api/run-control/adapter-release-check"
    assert payload["planned_start_endpoint"] == "/api/run-control/adapter-start"
    assert payload["source_adapter_module"] == "ims.api.controlled_execution_adapter"
    assert payload["release_validation_module"] == "ims.api.run_control_execution_release"
    assert payload["expected_adapter_mode"] == "explicit_multi_period_fixture_adapter"
    assert payload["expected_summary_mode"] == "explicit_multi_period_execution_summary"
    assert "queue_id" in payload["required_request_fields"]
    assert "explicit_execution_release" in payload["required_request_fields"]
    assert "release_profile_id" in payload["required_request_fields"]
    assert "idempotency_key" in payload["required_request_fields"]
    assert "released_by" in payload["required_request_fields"]
    assert "released_at" in payload["required_request_fields"]
    assert "release_reason" in payload["required_request_fields"]
    assert "queue_entry_exists" in payload["required_preconditions"]
    assert "explicit_execution_release_true" in payload["required_preconditions"]
    assert "fixture_path_from_known_local_metadata" in payload["required_preconditions"]
    assert "browser_upload" in payload["forbidden_request_fields"]
    assert "free_output_path" in payload["forbidden_request_fields"]
    assert "execution_enabled_true_from_queue_metadata" in payload["forbidden_request_fields"]
    assert "adapter_start_from_contract" in payload["forbidden_boundaries"]
    assert "post_adapter_start_endpoint" not in payload["forbidden_boundaries"]
    assert "queue_worker" in payload["forbidden_boundaries"]
    assert "ui_start_button" in payload["forbidden_boundaries"]
    assert payload["contract_only"] is False
    assert payload["http_enabled"] is True
    assert payload["api_accepts_start_payload"] is True
    assert payload["api_validates_start_payload"] is True
    assert payload["api_accepts_release_payload"] is True
    assert payload["api_validates_release_payload"] is True
    assert payload["api_starts_adapter"] is True
    assert payload["ui_start_enabled"] is False
    assert payload["queue_worker_enabled"] is False
    assert payload["writes_enabled"] is True
    assert payload["execution_enabled"] is True
    assert payload["writes_performed"] is False
    assert payload["execution_performed"] is False
    assert payload["simulation_performed"] is False
    assert payload["automatic_historical_rule_selection_performed"] is False
    assert payload["historical_full_equality_claimed"] is False
    assert isinstance(build_run_control_adapter_start_contract(), RunControlAdapterStartContract)


def test_run_control_adapter_start_contract_cli_prints_json_without_writing(
    tmp_path, monkeypatch, capsys
) -> None:
    monkeypatch.chdir(tmp_path)

    exit_code = main([])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["mode"] == "run_control_adapter_start_contract"
    assert payload["api_starts_adapter"] is True
    assert payload["execution_performed"] is False
    assert not (tmp_path / ".ims_workbench" / "metadata.sqlite").exists()


def test_run_control_adapter_start_contract_rejects_arguments(capsys) -> None:
    with pytest.raises(SystemExit):
        main(["--queue-id", "baseline-python-tests"])

    assert capsys.readouterr().out == ""


def test_run_control_adapter_start_contract_module_entrypoint_rejects_arguments() -> None:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path(__file__).resolve().parent.parent / "python_port")
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "ims.api.run_control_adapter_start_contract",
            "--queue-id",
            "baseline-python-tests",
        ],
        capture_output=True,
        check=False,
        env=env,
        text=True,
    )

    assert completed.returncode != 0
    assert "does not accept arguments" in completed.stderr
    assert completed.stdout == ""


def test_run_control_adapter_start_contract_endpoint_describes_backend_start(tmp_path) -> None:
    app = create_app(frontend_dist=tmp_path)
    client = TestClient(app)

    response = client.get("/api/run-control/adapter-start-contract")

    assert response.status_code == 200
    payload = response.json()
    assert payload["mode"] == "run_control_adapter_start_contract"
    assert payload["endpoint"] == "/api/run-control/adapter-start-contract"
    assert payload["planned_start_endpoint"] == "/api/run-control/adapter-start"
    assert payload["api_accepts_start_payload"] is True
    assert payload["api_starts_adapter"] is True
    assert payload["ui_start_enabled"] is False
    assert payload["queue_worker_enabled"] is False
    assert payload["writes_performed"] is False
    assert payload["execution_performed"] is False
    assert payload["simulation_performed"] is False
    assert not (tmp_path / ".ims_workbench" / "metadata.sqlite").exists()


def test_run_control_adapter_start_endpoint_rejects_non_sqlite_source(tmp_path) -> None:
    app = create_app(frontend_dist=tmp_path)
    client = TestClient(app)

    response = client.post(
        "/api/run-control/adapter-start",
        json={
            "queue_id": "baseline-python-tests",
            "run_id": "baseline-python-tests",
            "scenario_id": "agrsich-reference-window",
            "explicit_execution_release": True,
        },
    )

    assert response.status_code == 400
    assert response.json()["adapter_started"] is False
    assert not (tmp_path / ".ims_workbench" / "metadata.sqlite").exists()
