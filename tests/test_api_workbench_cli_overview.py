import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from ims.api.workbench_cli_overview import (
    WorkbenchCliCommand,
    WorkbenchCliOverviewResult,
    build_workbench_cli_overview,
    main,
)


def test_workbench_cli_overview_reports_stable_json_shape():
    payload = build_workbench_cli_overview().to_dict()

    assert payload["status"] == "ok"
    assert payload["mode"] == "cli_overview"
    assert isinstance(payload["commands"], list)
    assert payload["boundaries"]["writes_enabled"] is False
    assert payload["boundaries"]["export_requires_explicit_out"] is True
    assert payload["boundaries"]["import_requires_explicit_db"] is True
    assert payload["boundaries"]["execution_enabled"] is False
    assert payload["boundaries"]["starts_server"] is False
    assert payload["boundaries"]["creates_sqlite_file"] is False
    assert payload["rest_plan"]["remaining_prs_estimate"] == "0"
    assert payload["rest_plan"]["next_blocks"] == []
    assert "kontrollierte echte Run-Steuerung" in payload["rest_plan"]["deferred_blocks"]


def test_workbench_cli_overview_contains_expected_commands():
    commands = build_workbench_cli_overview().to_dict()["commands"]
    names = [command["name"] for command in commands]

    assert names == [
        "workbench_diagnostics",
        "workbench_start_plan",
        "workbench_readiness",
        "metadata_import_cli check",
        "metadata_import_cli preview",
        "metadata_import_cli snapshot",
        "metadata_import_cli export",
        "metadata_import_cli roundtrip",
        "metadata_import_cli dry-run",
        "metadata_write_contracts",
        "metadata_write_contracts check",
        "run_control_contracts",
        "run_control_preflight",
        "metadata_import_cli import --db",
    ]
    assert all(command["starts_server"] is False for command in commands)
    assert all(command["starts_simulation"] is False for command in commands)


def test_workbench_cli_overview_marks_only_explicit_export_and_import_as_writing():
    commands = build_workbench_cli_overview().to_dict()["commands"]
    writing_commands = [command["name"] for command in commands if command["writes_enabled"]]
    read_only_commands = [command["name"] for command in commands if not command["writes_enabled"]]

    assert writing_commands == ["metadata_import_cli export", "metadata_import_cli import --db"]
    assert "Importbericht" in commands[-1]["purpose"]
    assert "metadata_import_cli import --db" not in build_workbench_cli_overview().to_dict()["boundaries"][
        "read_only_commands"
    ]
    assert read_only_commands == [
        "workbench_diagnostics",
        "workbench_start_plan",
        "workbench_readiness",
        "metadata_import_cli check",
        "metadata_import_cli preview",
        "metadata_import_cli snapshot",
        "metadata_import_cli roundtrip",
        "metadata_import_cli dry-run",
        "metadata_write_contracts",
        "metadata_write_contracts check",
        "run_control_contracts",
        "run_control_preflight",
    ]


def test_workbench_cli_overview_cli_prints_stable_json(capsys):
    exit_code = main([])

    payload = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert payload["status"] == "ok"
    assert payload["mode"] == "cli_overview"
    assert payload["commands"][0]["name"] == "workbench_diagnostics"


def test_workbench_cli_overview_does_not_create_sqlite_file(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    payload = build_workbench_cli_overview().to_dict()

    assert payload["status"] == "ok"
    assert not (tmp_path / ".ims_workbench" / "metadata.sqlite").exists()


def test_workbench_cli_overview_rejects_arguments(capsys):
    with pytest.raises(SystemExit):
        main(["--db", "metadata.sqlite"])

    assert capsys.readouterr().out == ""
    assert WorkbenchCliCommand is not None
    assert WorkbenchCliOverviewResult is not None


def test_workbench_cli_overview_module_entrypoint_rejects_arguments():
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path(__file__).resolve().parent.parent / "python_port")
    completed = subprocess.run(
        [sys.executable, "-m", "ims.api.workbench_cli_overview", "--db", "metadata.sqlite"],
        capture_output=True,
        check=False,
        env=env,
        text=True,
    )

    assert completed.returncode != 0
    assert "does not accept arguments" in completed.stderr
    assert completed.stdout == ""
