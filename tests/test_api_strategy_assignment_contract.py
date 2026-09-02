from starlette.testclient import TestClient

from ims.api.app import create_app


def test_assignment_contract_endpoint_exposes_read_only_contract(tmp_path) -> None:
    client = TestClient(create_app(frontend_dist=tmp_path))

    response = client.get("/api/strategies/assignment-contract")

    assert response.status_code == 200
    payload = response.json()
    assert payload["schema_version"] == "ims.strategy-assignment-contract.v1"
    assert payload["catalog_schema_version"] == "ims.strategy-catalog.v1"
    assert payload["mode"] == "strategy_assignment_contract_read_only"
    assert len(payload["assignment_targets"]) == 2
    assert len(payload["parameter_schemas"]) == 13
    assert len(payload["source_profiles"]) == 18
    assert payload["source_summary"]["insurer_count"] == 25
    assert payload["source_summary"]["policyholder_count"] == 200


def test_assignment_contract_endpoint_preserves_sector_and_source_boundaries(tmp_path) -> None:
    client = TestClient(create_app(frontend_dist=tmp_path))

    payload = client.get("/api/strategies/assignment-contract").json()
    sector = payload["sector_contract"]
    profiles = payload["source_profiles"]

    assert sector["position_count"] == 2
    assert sector["named_sectors_available"] is False
    assert sector["strategy_shared_across_positions"] is True
    assert sector["sector_specific_strategy_supported"] is False
    assert not any(profile["strategy_id"] == "vu.vrvu10" for profile in profiles)
    assert any(
        profile["target_id_start"] == 151
        and profile["target_id_end"] == 190
        and profile["activation_period"] == 50
        for profile in profiles
    )
    assert all(profile["parameter_values_exposed"] is False for profile in profiles)
    assert all(
        "parameters" not in profile and "parameter_values" not in profile
        for profile in profiles
    )


def test_assignment_contract_endpoint_keeps_all_mutating_paths_closed(tmp_path) -> None:
    client = TestClient(create_app(frontend_dist=tmp_path))

    payload = client.get("/api/strategies/assignment-contract").json()
    assert payload["assignment_editing_enabled"] is False
    assert payload["parameter_editing_enabled"] is False
    assert payload["sector_specific_strategy_enabled"] is False
    assert payload["scheduled_strategy_switch_enabled"] is False
    assert payload["writes_enabled"] is False
    assert payload["execution_enabled"] is False
    assert payload["simulation_performed"] is False
    assert payload["historical_full_equality_claim"] is False
    assert client.post("/api/strategies/assignment-contract", json={}).status_code == 405
    assert client.put("/api/strategies/assignment-contract", json={}).status_code == 405
    assert client.delete("/api/strategies/assignment-contract").status_code == 405
