from fastapi.testclient import TestClient

from ims.api.app import create_app


def test_assignment_vu_snapshot_materialization_contract_endpoint_is_read_only(
    tmp_path,
) -> None:
    client = TestClient(create_app(frontend_dist=tmp_path))
    endpoint = "/api/strategies/assignment-vu-snapshot-materialization-contract"

    response = client.get(endpoint)

    assert response.status_code == 200
    payload = response.json()
    assert payload["schema_version"] == (
        "ims.strategy-assignment-vu-snapshot-materialization-contract.v1"
    )
    assert payload["contract_issue_count"] == 0
    assert payload["strategy_count"] == 10
    assert payload["snapshot_type_count"] == 8
    assert payload["loader_fallbacks_are_inventory_only"] is True
    assert payload["future_materialization_defaults_defined"] is False
    assert payload["input_validation_enabled"] is False
    assert payload["snapshot_loader_invocation_enabled"] is False
    assert payload["snapshot_materialization_enabled"] is False
    assert payload["runner_enabled"] is False
    assert payload["execution_enabled"] is False
    assert payload["simulation_performed"] is False
    assert client.post(endpoint, json={}).status_code == 405
    assert client.put(endpoint, json={}).status_code == 405
    assert client.delete(endpoint).status_code == 405
