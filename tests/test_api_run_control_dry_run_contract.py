import json
import os
import subprocess
import sys
from pathlib import Path

from ims.api.run_control_dry_run_contract import (
    WorkbenchRunControlDryRunContract,
    build_run_control_dry_run_contract,
    main,
    run_control_dry_run_contract_payload,
)


def test_run_control_dry_run_contract_reports_stable_json_shape():
    payload = run_control_dry_run_contract_payload()

    assert payload["status"] == "warning"
    assert payload["mode"] == "run_control_dry_run_contract"
    assert payload["schema_version"] == "ims.workbench.metadata.v1"
    assert "run_id" in payload["expected_inputs"]
    assert "run_control_preflight_visible" in payload["required_preconditions"]
    assert "simulation_execution" in payload["forbidden_boundaries"]
    assert "http_post" in payload["forbidden_boundaries"]
    assert payload["http_enabled"] is False
    assert payload["writes_enabled"] is False
    assert payload["execution_enabled"] is False
    assert payload["writes_performed"] is False
    assert payload["execution_performed"] is False
    assert isinstance(build_run_control_dry_run_contract(), WorkbenchRunControlDryRunContract)


def test_run_control_dry_run_contract_cli_prints_stable_json(capsys):
    exit_code = main([])

    payload = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert payload["mode"] == "run_control_dry_run_contract"
    assert payload["execution_performed"] is False


def test_run_control_dry_run_contract_rejects_arguments(capsys):
    try:
        main(["--run-id", "baseline-python-tests"])
    except SystemExit as exc:
        assert str(exc) == "run_control_dry_run_contract does not accept arguments"
    else:  # pragma: no cover
        raise AssertionError("expected SystemExit")
    assert capsys.readouterr().out == ""


def test_run_control_dry_run_contract_does_not_create_sqlite_file(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    payload = build_run_control_dry_run_contract().to_dict()

    assert payload["writes_performed"] is False
    assert not (tmp_path / ".ims_workbench" / "metadata.sqlite").exists()


def test_run_control_dry_run_contract_module_entrypoint_rejects_arguments():
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path(__file__).resolve().parent.parent / "python_port")
    completed = subprocess.run(
        [sys.executable, "-m", "ims.api.run_control_dry_run_contract", "--db", "metadata.sqlite"],
        capture_output=True,
        check=False,
        env=env,
        text=True,
    )

    assert completed.returncode != 0
    assert "does not accept arguments" in completed.stderr
    assert completed.stdout == ""
