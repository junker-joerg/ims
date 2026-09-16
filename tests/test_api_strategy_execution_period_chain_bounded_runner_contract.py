import importlib

from fastapi.testclient import TestClient

from ims.api.app import create_app


def test_bounded_runner_contract_endpoint_is_read_only(tmp_path) -> None:
    client = TestClient(create_app(frontend_dist=tmp_path))
    endpoint = "/api/run-control/strategy-period-chain-bounded-runner-contract"

    response = client.get(endpoint)

    assert response.status_code == 200
    payload = response.json()
    assert payload["schema_version"] == (
        "ims.strategy-execution-period-chain-bounded-runner-contract.v1"
    )
    assert payload["horizon_policy"]["minimum_period_count"] == 2
    assert payload["horizon_policy"]["maximum_period_count"] == 5
    assert payload["current_release_state"]["released_period_counts"] == [2, 5]
    assert payload["current_release_state"][
        "contracted_not_released_period_counts"
    ] == [3, 4]
    assert payload["stable_two_period_prefix_policy"][
        "canonical_json_byte_equality_required"
    ] is True
    assert payload["bounded_runner_enabled"] is True
    assert payload["five_period_execution_enabled"] is True
    assert payload["five_period_chain_build_enabled"] is True
    assert payload["five_period_server_start_enabled"] is True
    assert payload["five_period_idempotency_persistence_enabled"] is True
    assert payload["five_period_result_persistence_enabled"] is True
    assert payload["five_period_immutable_chain_snapshot_persistence_enabled"] is True
    assert payload["five_period_ui_start_enabled"] is False
    assert payload["execution_performed"] is False
    assert payload["simulation_performed"] is False
    assert payload["next_gate"] == "PR147"
    assert client.post(endpoint, json={}).status_code == 405
    assert client.put(endpoint, json={}).status_code == 405
    assert client.delete(endpoint).status_code == 405


def test_starlette_fallback_exposes_same_bounded_runner_contract(
    monkeypatch,
    tmp_path,
) -> None:
    app_module = importlib.import_module("ims.api.app")
    monkeypatch.setattr(app_module, "FastAPI", None)
    client = TestClient(create_app(frontend_dist=tmp_path))
    endpoint = "/api/run-control/strategy-period-chain-bounded-runner-contract"

    response = client.get(endpoint)

    assert response.status_code == 200
    payload = response.json()
    assert payload["horizon_policy"]["maximum_period_count"] == 5
    assert payload["current_release_state"]["released_period_counts"] == [2, 5]
    assert payload["bounded_runner_enabled"] is True
    assert payload["next_gate"] == "PR147"
    assert client.post(endpoint, json={}).status_code == 405
