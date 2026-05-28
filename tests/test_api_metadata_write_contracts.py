import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from ims.api.metadata_write_contracts import (
    WorkbenchMetadataWriteArea,
    WorkbenchMetadataWriteContract,
    build_metadata_write_contract,
    main,
)


def test_metadata_write_contract_reports_stable_boundaries():
    payload = build_metadata_write_contract().to_dict()

    assert payload["status"] == "ok"
    assert payload["schema_version"] == "ims.workbench.metadata.v1"
    assert payload["mode"] == "metadata_write_contract"
    assert payload["http_write_paths_enabled"] is False
    assert payload["ui_write_paths_enabled"] is False
    assert payload["simulation_execution_enabled"] is False
    assert payload["sqlite_migration_performed"] is False
    assert payload["writes_performed"] is False
    assert payload["allowed_local_write_paths"] == ["metadata_import_cli import --db"]


def test_metadata_write_contract_lists_allowed_and_forbidden_metadata_areas():
    payload = build_metadata_write_contract().to_dict()
    areas = {area["name"]: area for area in payload["metadata_areas"]}

    assert set(areas) == {"scenario_metadata", "run_metadata"}
    assert areas["scenario_metadata"]["prepared"] is True
    assert areas["scenario_metadata"]["http_enabled"] is False
    assert areas["scenario_metadata"]["ui_enabled"] is False
    assert "display_name" in areas["scenario_metadata"]["allowed_fields"]
    assert "historical_full_equality_claim" in areas["scenario_metadata"]["forbidden_fields"]
    assert areas["run_metadata"]["prepared"] is True
    assert areas["run_metadata"]["http_enabled"] is False
    assert areas["run_metadata"]["ui_enabled"] is False
    assert "period_window" in areas["run_metadata"]["allowed_fields"]
    assert "execution_enabled" in areas["run_metadata"]["allowed_fields"]
    assert "execution_enabled=true" in areas["run_metadata"]["forbidden_fields"]
    assert "execution_enabled=true" in payload["forbidden_boundaries"]
    assert "simulation_execution" in payload["forbidden_boundaries"]
    assert "fachlogik_data" in payload["forbidden_boundaries"]


def test_metadata_write_contract_cli_prints_json_without_writing(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)

    exit_code = main([])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["mode"] == "metadata_write_contract"
    assert payload["writes_performed"] is False
    assert not (tmp_path / ".ims_workbench" / "metadata.sqlite").exists()
    assert WorkbenchMetadataWriteArea is not None
    assert WorkbenchMetadataWriteContract is not None


def test_metadata_write_contract_cli_rejects_arguments(capsys):
    with pytest.raises(SystemExit):
        main(["--db", "metadata.sqlite"])

    assert capsys.readouterr().out == ""


def test_metadata_write_contract_module_entrypoint_rejects_arguments():
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path(__file__).resolve().parent.parent / "python_port")
    completed = subprocess.run(
        [sys.executable, "-m", "ims.api.metadata_write_contracts", "--db", "metadata.sqlite"],
        capture_output=True,
        check=False,
        env=env,
        text=True,
    )

    assert completed.returncode != 0
    assert "does not accept arguments" in completed.stderr
    assert completed.stdout == ""
