from ims.api.metadata import list_run_metadata, list_scenario_metadata, metadata_capabilities


def test_scenario_metadata_schema_is_stable():
    payload = list_scenario_metadata()

    assert set(payload) == {"schema_version", "generated_at", "items"}
    assert payload["schema_version"] == "ims.workbench.metadata.v1"
    assert payload["generated_at"] == "2026-05-27T00:00:00Z"

    scenario = payload["items"][0]
    assert set(scenario) == {
        "id",
        "display_name",
        "status",
        "domain_scope",
        "source",
        "validation",
        "updated_at",
        "notes",
    }
    assert scenario["source"]["kind"] == "fixture"
    assert scenario["validation"]["status"] == "validated"


def test_run_metadata_schema_keeps_execution_disabled():
    payload = list_run_metadata()

    assert set(payload) == {"schema_version", "generated_at", "items"}
    run = payload["items"][0]
    assert set(run) == {
        "id",
        "display_name",
        "scenario_id",
        "status",
        "source",
        "validation",
        "period_window",
        "execution_enabled",
        "updated_at",
    }
    assert run["execution_enabled"] is False
    assert run["validation"]["scope"] == "560 Tests"


def test_metadata_capabilities_document_disabled_write_boundary():
    payload = metadata_capabilities()

    assert payload["schema_version"] == "ims.workbench.metadata.v1"
    assert payload["writes"]["scenario_metadata"]["enabled"] is False
    assert payload["writes"]["run_metadata"]["enabled"] is False
    assert payload["simulation_execution"]["enabled"] is False
