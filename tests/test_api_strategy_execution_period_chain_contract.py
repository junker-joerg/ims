from fastapi.testclient import TestClient

from ims.api.app import create_app


def test_strategy_execution_period_chain_contract_endpoint_is_read_only(
    tmp_path,
) -> None:
    client = TestClient(create_app(frontend_dist=tmp_path))
    endpoint = "/api/strategies/execution-period-chain-contract"

    response = client.get(endpoint)

    assert response.status_code == 200
    payload = response.json()
    assert payload["schema_version"] == (
        "ims.strategy-execution-period-chain-contract.v1"
    )
    assert payload["period_chain_schema_version"] == (
        "ims.strategy-execution-period-chain.v1"
    )
    assert payload["candidate_schema_version"] == (
        "ims.strategy-execution-candidate.v1"
    )
    assert payload["historical_horizon"]["maximum_periods_per_run"] == 100
    assert payload["period_sequence_policy"]["contiguous"] is True
    assert payload["period_chain_validation_enabled"] is True
    assert payload["period_chain_candidate_resolution_enabled"] is True
    assert payload["carryover_definition_count"] == 3
    assert payload["period_chain_runner_enabled"] is False
    assert payload["carryover_execution_enabled"] is False
    assert payload["multi_period_execution_enabled"] is False
    assert payload["output_files_enabled"] is False
    assert payload["legacy_comparison_enabled"] is False
    assert payload["next_gate"] == "PR136"
    assert client.post(endpoint, json={}).status_code == 405
    assert client.put(endpoint, json={}).status_code == 405
    assert client.delete(endpoint).status_code == 405
