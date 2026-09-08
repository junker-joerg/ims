from fastapi.testclient import TestClient

from ims.api.app import create_app


def test_strategy_execution_candidate_contract_endpoint_is_read_only(tmp_path) -> None:
    client = TestClient(create_app(frontend_dist=tmp_path))
    endpoint = "/api/strategies/execution-candidate-contract"

    response = client.get(endpoint)

    assert response.status_code == 200
    payload = response.json()
    assert payload["schema_version"] == (
        "ims.strategy-execution-candidate-contract.v1"
    )
    assert payload["candidate_schema_version"] == (
        "ims.strategy-execution-candidate.v1"
    )
    assert payload["required_section_count"] == 8
    assert payload["collection_count"] == 11
    assert payload["open_requirement_count"] == 6
    assert payload["candidate_input_validation_enabled"] is False
    assert payload["candidate_creation_enabled"] is False
    assert payload["runner_enabled"] is False
    assert payload["execution_enabled"] is False
    assert payload["simulation_performed"] is False
    assert client.post(endpoint, json={}).status_code == 405
    assert client.put(endpoint, json={}).status_code == 405
    assert client.delete(endpoint).status_code == 405
