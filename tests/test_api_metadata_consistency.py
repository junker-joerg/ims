from starlette.testclient import TestClient

from ims.api.app import create_app
from ims.api.metadata import metadata_capabilities
from ims.api.metadata_consistency import metadata_consistency_payload
from ims.api.metadata_repository import build_seeded_metadata_repository


def test_metadata_consistency_endpoint_reports_seeded_metadata_clean(tmp_path):
    repository = build_seeded_metadata_repository(tmp_path / "metadata.sqlite")
    app = create_app(frontend_dist=tmp_path, metadata_repository=repository)
    client = TestClient(app)

    response = client.get("/api/metadata/consistency")

    assert response.status_code == 200
    payload = response.json()
    assert payload["schema_version"] == "ims.workbench.metadata.v1"
    assert payload["status"] == "ok"
    assert payload["scenario_count"] == 2
    assert payload["run_count"] == 2
    assert payload["runs_with_known_scenario"] == 2
    assert payload["runs_with_missing_scenario"] == []
    assert payload["runs_with_execution_enabled"] == []
    assert payload["writes_enabled"] is False
    assert payload["simulation_enabled"] is False
    assert payload["issue_count"] == 0


def test_metadata_consistency_payload_reports_reference_and_execution_warnings():
    scenarios = {
        "items": [
            {
                "id": "known-scenario",
            }
        ]
    }
    runs = {
        "items": [
            {
                "id": "safe-run",
                "scenario_id": "known-scenario",
                "execution_enabled": False,
            },
            {
                "id": "orphan-run",
                "scenario_id": "missing-scenario",
                "execution_enabled": True,
            },
        ]
    }

    payload = metadata_consistency_payload(scenarios, runs, metadata_capabilities())

    assert payload["status"] == "warning"
    assert payload["scenario_count"] == 1
    assert payload["run_count"] == 2
    assert payload["runs_with_known_scenario"] == 1
    assert payload["runs_with_missing_scenario"] == ["orphan-run"]
    assert payload["runs_with_execution_enabled"] == ["orphan-run"]
    assert payload["issue_count"] == 2
