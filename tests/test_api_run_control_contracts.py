import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from ims.api.metadata import metadata_capabilities
from ims.api.run_control_dry_run_contract import build_run_control_dry_run_contract
from ims.api.run_control_contracts import WorkbenchRunControlContract, build_run_control_contract, main


def test_run_control_contract_reports_stable_json_shape():
    payload = build_run_control_contract().to_dict()

    assert payload["status"] == "ok"
    assert payload["mode"] == "run_control_contract"
    assert payload["schema_version"] == "ims.workbench.metadata.v1"
    assert payload["execution_enabled"] is False
    assert payload["http_enabled"] is False
    assert payload["ui_enabled"] is False
    assert payload["writes_performed"] is False
    assert payload["execution_performed"] is False


def test_run_control_contract_declares_future_inputs_and_forbidden_boundaries():
    payload = build_run_control_contract().to_dict()

    assert payload["allowed_future_inputs"] == [
        "run_id",
        "scenario_id",
        "metadata_db",
        "requested_by",
        "created_at",
        "execution_enabled",
    ]
    assert payload["forbidden_boundaries"] == [
        "simulation_execution",
        "fachlogik_mutation",
        "historical_full_equality_claim",
        "browser_upload",
        "http_write_endpoint",
    ]


def test_run_control_contract_keeps_capabilities_execution_disabled():
    capabilities = metadata_capabilities()

    assert capabilities["simulation_execution"]["enabled"] is False
    assert capabilities["writes"]["scenario_metadata"]["enabled"] is False
    assert capabilities["writes"]["run_metadata"]["enabled"] is False


def test_run_control_dry_run_contract_enables_only_http_check_boundary():
    payload = build_run_control_dry_run_contract().to_dict()

    assert payload["status"] == "ok"
    assert payload["mode"] == "run_control_dry_run_contract"
    assert payload["http_enabled"] is True
    assert payload["writes_enabled"] is False
    assert payload["execution_enabled"] is False
    assert payload["writes_performed"] is False
    assert payload["execution_performed"] is False
    assert "request_body" in payload["expected_inputs"]
    assert "run_control_dry_run_endpoint_visible" in payload["required_preconditions"]
    assert "http_post" not in payload["forbidden_boundaries"]
    assert "queue_write" in payload["forbidden_boundaries"]


def test_run_control_contract_cli_prints_stable_json(capsys):
    exit_code = main([])

    payload = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert payload["status"] == "ok"
    assert payload["mode"] == "run_control_contract"
    assert payload["execution_performed"] is False
    assert WorkbenchRunControlContract is not None


def test_run_control_contract_does_not_create_sqlite_file(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    payload = build_run_control_contract().to_dict()

    assert payload["status"] == "ok"
    assert not (tmp_path / ".ims_workbench" / "metadata.sqlite").exists()


def test_run_control_contract_rejects_arguments(capsys):
    with pytest.raises(SystemExit):
        main(["--db", "metadata.sqlite"])

    assert capsys.readouterr().out == ""


def test_run_control_contract_module_entrypoint_rejects_arguments():
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path(__file__).resolve().parent.parent / "python_port")
    completed = subprocess.run(
        [sys.executable, "-m", "ims.api.run_control_contracts", "--db", "metadata.sqlite"],
        capture_output=True,
        check=False,
        env=env,
        text=True,
    )

    assert completed.returncode != 0
    assert "does not accept arguments" in completed.stderr
    assert completed.stdout == ""
