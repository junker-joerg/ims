import json

import pytest

from ims.api.metadata import METADATA_SCHEMA_VERSION
from ims.api.metadata_import import (
    MetadataImportError,
    import_metadata_file,
    parse_metadata_import_payload,
)
from ims.api.metadata_repository import build_seeded_metadata_repository


def test_import_metadata_file_upserts_local_metadata(tmp_path):
    repository = build_seeded_metadata_repository(tmp_path / "metadata.sqlite")
    import_path = tmp_path / "metadata_import.json"
    import_path.write_text(json.dumps(_valid_import_payload()), encoding="utf-8")

    result = import_metadata_file(import_path, repository)

    scenarios = repository.list_scenarios()["items"]
    runs = repository.list_runs()["items"]
    assert result.scenario_count == 1
    assert result.run_count == 1
    assert "local-imported-scenario" in result.scenario_ids
    assert "local-imported-run" in result.run_ids
    scenario_by_id = {scenario["id"]: scenario for scenario in scenarios}
    run_by_id = {run["id"]: run for run in runs}
    assert scenario_by_id["local-imported-scenario"]["display_name"] == "Lokal importiertes Szenario"
    assert run_by_id["local-imported-run"]["period_window"] == "keine Simulation"
    assert run_by_id["local-imported-run"]["execution_enabled"] is False


def test_import_rejects_missing_required_field():
    payload = _valid_import_payload()
    del payload["scenarios"][0]["display_name"]

    with pytest.raises(MetadataImportError, match="display_name"):
        parse_metadata_import_payload(payload)


def test_import_rejects_unknown_run_scenario_reference(tmp_path):
    repository = build_seeded_metadata_repository(tmp_path / "metadata.sqlite")
    payload = _valid_import_payload()
    payload["runs"][0]["scenario_id"] = "missing-scenario"
    import_path = tmp_path / "metadata_import.json"
    import_path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(MetadataImportError, match="unknown scenario_id"):
        import_metadata_file(import_path, repository)


def test_import_keeps_execution_enabled_forbidden(tmp_path):
    repository = build_seeded_metadata_repository(tmp_path / "metadata.sqlite")
    payload = _valid_import_payload()
    payload["runs"][0]["execution_enabled"] = True
    import_path = tmp_path / "metadata_import.json"
    import_path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(MetadataImportError, match="execution_enabled"):
        import_metadata_file(import_path, repository)


def test_import_rejects_unknown_schema_version():
    payload = _valid_import_payload()
    payload["schema_version"] = "ims.workbench.metadata.v2"

    with pytest.raises(MetadataImportError, match=METADATA_SCHEMA_VERSION):
        parse_metadata_import_payload(payload)


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
