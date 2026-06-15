import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from ims.api.metadata_import import MetadataImportError
from ims.api.run_control_requests import (
    WorkbenchRunControlRequest,
    WorkbenchRunControlRequestValidationResult,
    main,
    parse_run_control_request_payload,
    validate_run_control_request,
    validate_run_control_request_payload,
)


def _valid_request_payload() -> dict[str, object]:
    return {
        "schema_version": "ims.workbench.metadata.v1",
        "run_id": "baseline-python-tests",
        "scenario_id": "baseline-regression",
        "metadata_db": ".ims_workbench/metadata.sqlite",
        "requested_by": "local-user",
        "created_at": "2026-06-15T00:00:00Z",
        "execution_enabled": False,
    }


def test_run_control_request_validates_stable_shape():
    payload = validate_run_control_request_payload(_valid_request_payload()).to_dict()

    assert payload["status"] == "ok"
    assert payload["mode"] == "run_control_request_check"
    assert payload["request"]["run_id"] == "baseline-python-tests"
    assert payload["request"]["scenario_id"] == "baseline-regression"
    assert payload["request"]["execution_enabled"] is False
    assert payload["writes_performed"] is False
    assert payload["execution_performed"] is False
    assert "execution_enabled" in payload["accepted_fields"]


def test_run_control_request_allows_missing_optional_metadata_db():
    raw_payload = _valid_request_payload()
    raw_payload.pop("metadata_db")

    request = parse_run_control_request_payload(raw_payload)

    assert request.metadata_db is None
    assert "metadata_db" not in request.to_dict()


def test_run_control_request_rejects_execution_enabled_true():
    raw_payload = _valid_request_payload()
    raw_payload["execution_enabled"] = True

    with pytest.raises(MetadataImportError, match="execution_enabled=true is forbidden"):
        validate_run_control_request_payload(raw_payload)


def test_run_control_request_rejects_unknown_fachlogik_fields():
    raw_payload = _valid_request_payload()
    raw_payload["fachlogik_state"] = {"unsafe": True}

    with pytest.raises(MetadataImportError, match="rejected fields: fachlogik_state"):
        validate_run_control_request_payload(raw_payload)


def test_run_control_request_rejects_missing_required_fields():
    raw_payload = _valid_request_payload()
    raw_payload.pop("requested_by")

    with pytest.raises(MetadataImportError, match="missing required fields: requested_by"):
        validate_run_control_request_payload(raw_payload)


def test_run_control_request_file_check_does_not_create_sqlite_file(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    request_path = tmp_path / "run_control_request.json"
    request_path.write_text(json.dumps(_valid_request_payload()), encoding="utf-8")

    payload = validate_run_control_request(request_path).to_dict()

    assert payload["status"] == "ok"
    assert not (tmp_path / ".ims_workbench" / "metadata.sqlite").exists()


def test_run_control_request_cli_prints_stable_json(tmp_path, capsys):
    request_path = tmp_path / "run_control_request.json"
    request_path.write_text(json.dumps(_valid_request_payload()), encoding="utf-8")

    exit_code = main(["check", str(request_path)])

    payload = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert payload["status"] == "ok"
    assert payload["mode"] == "run_control_request_check"
    assert payload["request"]["execution_enabled"] is False
    assert WorkbenchRunControlRequest is not None
    assert WorkbenchRunControlRequestValidationResult is not None


def test_run_control_request_cli_reports_stable_error_json(tmp_path, capsys):
    request_path = tmp_path / "run_control_request.json"
    payload = _valid_request_payload()
    payload["execution_enabled"] = True
    request_path.write_text(json.dumps(payload), encoding="utf-8")

    exit_code = main(["check", str(request_path)])

    output = json.loads(capsys.readouterr().out)
    assert exit_code == 2
    assert output["status"] == "error"
    assert output["mode"] == "run_control_request_check"
    assert "execution_enabled=true is forbidden" in output["message"]
    assert output["writes_performed"] is False
    assert output["execution_performed"] is False


def test_run_control_request_module_entrypoint_prints_json(tmp_path):
    request_path = tmp_path / "run_control_request.json"
    request_path.write_text(json.dumps(_valid_request_payload()), encoding="utf-8")
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path(__file__).resolve().parent.parent / "python_port")
    completed = subprocess.run(
        [sys.executable, "-m", "ims.api.run_control_requests", "check", str(request_path)],
        capture_output=True,
        check=False,
        env=env,
        text=True,
    )

    payload = json.loads(completed.stdout)
    assert completed.returncode == 0
    assert payload["status"] == "ok"
    assert payload["execution_performed"] is False


def test_run_control_request_module_entrypoint_rejects_unsupported_arguments():
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path(__file__).resolve().parent.parent / "python_port")
    completed = subprocess.run(
        [sys.executable, "-m", "ims.api.run_control_requests", "--db", "metadata.sqlite"],
        capture_output=True,
        check=False,
        env=env,
        text=True,
    )

    assert completed.returncode != 0
    assert "accepts only: check <path>" in completed.stderr
    assert completed.stdout == ""
