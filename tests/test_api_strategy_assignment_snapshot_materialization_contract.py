from fastapi.testclient import TestClient

from ims.api.app import create_app


def test_assignment_snapshot_materialization_contract_endpoint_is_read_only(
    tmp_path,
) -> None:
    client = TestClient(create_app(frontend_dist=tmp_path))
    endpoint = "/api/strategies/assignment-snapshot-materialization-contract"

    response = client.get(endpoint)

    assert response.status_code == 200
    payload = response.json()
    assert payload["schema_version"] == (
        "ims.strategy-assignment-snapshot-materialization-contract.v1"
    )
    assert payload["contract_issue_count"] == 0
    assert len(payload["vn_rule_definitions"]) == 6
    assert len(payload["nested_value_definitions"]) == 9
    assert payload["context_validator_uses_nested_contract"] is False
    assert payload["snapshot_materialization_enabled"] is False
    assert payload["execution_enabled"] is False
    assert payload["simulation_performed"] is False
    assert client.post(endpoint, json={}).status_code == 405
    assert client.put(endpoint, json={}).status_code == 405
    assert client.delete(endpoint).status_code == 405
