import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from ims.api.metadata import METADATA_SCHEMA_VERSION
from ims.api.metadata_write_contracts import (
    MetadataWriteContractValidationResult,
    WorkbenchMetadataWriteArea,
    WorkbenchMetadataWriteContract,
    build_metadata_write_contract,
    main,
    validate_metadata_write_contract,
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


def test_metadata_write_contract_check_accepts_valid_bundle_without_writing(tmp_path):
    import_path = tmp_path / "metadata_import.json"
    db_path = tmp_path / "metadata.sqlite"
    import_path.write_text(json.dumps(_valid_import_payload()), encoding="utf-8")

    result = validate_metadata_write_contract(import_path)
    payload = result.to_dict()

    assert payload["status"] == "ok"
    assert payload["mode"] == "write_contract_check"
    assert payload["scenario_count"] == 1
    assert payload["run_count"] == 1
    assert payload["scenario_ids"] == ["local-imported-scenario"]
    assert payload["run_ids"] == ["local-imported-run"]
    assert "execution_enabled" in payload["accepted_fields"]["run_metadata"]
    assert payload["rejected_fields"] == []
    assert payload["issues"] == []
    assert payload["writes_performed"] is False
    assert payload["execution_performed"] is False
    assert not db_path.exists()
    assert MetadataWriteContractValidationResult is not None


def test_metadata_write_contract_check_rejects_execution_enabled_true(tmp_path, capsys):
    import_path = tmp_path / "metadata_import.json"
    payload = _valid_import_payload()
    payload["runs"][0]["execution_enabled"] = True
    import_path.write_text(json.dumps(payload), encoding="utf-8")

    exit_code = main(["check", str(import_path)])
    output = json.loads(capsys.readouterr().out)

    assert exit_code == 2
    assert output["status"] == "error"
    assert output["mode"] == "write_contract_check"
    assert "execution_enabled" in output["message"]
    assert output["writes_performed"] is False
    assert output["execution_performed"] is False


def test_metadata_write_contract_check_rejects_forbidden_fachlogik_field(tmp_path, capsys):
    import_path = tmp_path / "metadata_import.json"
    payload = _valid_import_payload()
    payload["runs"][0]["fachlogik_state"] = {"internal": "blocked"}
    import_path.write_text(json.dumps(payload), encoding="utf-8")

    exit_code = main(["check", str(import_path)])
    output = json.loads(capsys.readouterr().out)

    assert exit_code == 2
    assert output["status"] == "error"
    assert "runs[0].fachlogik_state" in output["message"]
    assert output["writes_performed"] is False


def test_metadata_write_contract_check_prints_stable_json(tmp_path, capsys):
    import_path = tmp_path / "metadata_import.json"
    import_path.write_text(json.dumps(_valid_import_payload()), encoding="utf-8")

    exit_code = main(["check", str(import_path)])
    output = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert output["status"] == "ok"
    assert output["mode"] == "write_contract_check"
    assert output["accepted_fields"]["scenario_metadata"] == [
        "id",
        "display_name",
        "status",
        "domain_scope",
        "source",
        "validation",
        "updated_at",
        "notes",
    ]
    assert output["accepted_fields"]["run_metadata"] == [
        "id",
        "display_name",
        "scenario_id",
        "status",
        "source",
        "validation",
        "period_window",
        "execution_enabled",
        "updated_at",
    ]
    assert output["rejected_fields"] == []
    assert output["writes_performed"] is False


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
    assert "accepts no arguments except" in completed.stderr
    assert completed.stdout == ""


def _valid_import_payload():
    return {
        "schema_version": METADATA_SCHEMA_VERSION,
        "scenarios": [
            {
                "id": "local-imported-scenario",
                "display_name": "Lokal importiertes Szenario",
                "status": "draft",
                "domain_scope": "Metadaten",
                "source": {
                    "kind": "fixture",
                    "label": "Lokale Importdatei",
                    "path": "local/metadata.json",
                },
                "validation": {
                    "status": "planned",
                    "scope": "keine Fachvalidierung",
                    "claim": "Importiert nur Workbench-Metadaten.",
                },
                "updated_at": "2026-05-27T00:00:00Z",
                "notes": "Lokaler Metadatenimport ohne Simulationssteuerung.",
            }
        ],
        "runs": [
            {
                "id": "local-imported-run",
                "display_name": "Importierter Metadatenlauf",
                "scenario_id": "local-imported-scenario",
                "status": "planned",
                "source": {
                    "kind": "fixture",
                    "label": "Lokale Importdatei",
                    "path": "local/metadata.json",
                },
                "validation": {
                    "status": "planned",
                    "scope": "keine Simulation",
                    "claim": "Beschreibender Run-Metadatensatz.",
                },
                "period_window": "keine Simulation",
                "execution_enabled": False,
                "updated_at": "2026-05-27T00:00:00Z",
            }
        ],
    }
