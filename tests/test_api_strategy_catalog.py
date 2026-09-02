from starlette.testclient import TestClient

from ims.api.app import create_app


def test_strategy_catalog_endpoint_exposes_versioned_read_only_contract(tmp_path) -> None:
    client = TestClient(create_app(frontend_dist=tmp_path))

    response = client.get("/api/strategies/catalog")

    assert response.status_code == 200
    payload = response.json()
    assert payload["schema_version"] == "ims.strategy-catalog.v1"
    assert payload["mode"] == "strategy_catalog_read_only"
    assert payload["scope"] == "read_only_strategy_metadata"
    assert payload["historical_full_equality_claim"] is False
    assert payload["selection_enabled"] is False
    assert payload["parameter_editing_enabled"] is False
    assert payload["writes_enabled"] is False
    assert payload["execution_enabled"] is False
    assert payload["simulation_performed"] is False
    assert len(payload["families"]) == 8
    assert len(payload["strategies"]) == 16


def test_strategy_catalog_endpoint_preserves_vrvu10_and_family_boundaries(tmp_path) -> None:
    client = TestClient(create_app(frontend_dist=tmp_path))

    payload = client.get("/api/strategies/catalog").json()
    strategies = {item["strategy_id"]: item for item in payload["strategies"]}
    families = {item["family_id"]: item for item in payload["families"]}

    assert strategies["vu.vrvu10"]["historical_rule_class"] is None
    assert strategies["vu.vrvu10"]["included_in_vdefmd6"] is False
    assert strategies["vu.vrvu07"]["implementation_variant"] == "dumping"
    assert strategies["vn.vrvn06"]["family_id"] == "vn.market_search"
    assert all(family["taxonomy_only"] is True for family in families.values())


def test_strategy_catalog_endpoint_rejects_writes(tmp_path) -> None:
    client = TestClient(create_app(frontend_dist=tmp_path))

    assert client.post("/api/strategies/catalog", json={}).status_code == 405
    assert client.put("/api/strategies/catalog", json={}).status_code == 405
    assert client.delete("/api/strategies/catalog").status_code == 405
