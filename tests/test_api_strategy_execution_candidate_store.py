import json
from pathlib import Path

from fastapi.testclient import TestClient

from ims.api.app import create_app
from ims.api.strategy_execution_candidate_store import (
    STRATEGY_EXECUTION_CANDIDATE_STORE_REQUEST_VERSION,
)


FIXTURE = (
    Path(__file__).parent
    / "fixtures"
    / "strategy_execution_candidate_input_v1.json"
)


def _candidate_input() -> dict[str, object]:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def _store_request(client: TestClient) -> dict[str, object]:
    candidate_input = _candidate_input()
    build = client.post(
        "/api/strategies/execution-candidate-build",
        json=candidate_input,
    ).json()
    identity = build["candidate"]["identity"]
    return {
        "schema_version": STRATEGY_EXECUTION_CANDIDATE_STORE_REQUEST_VERSION,
        "candidate_input": candidate_input,
        "expected_candidate_id": identity["candidate_id"],
        "expected_content_digest": identity["content_digest"],
        "stored_at": "2026-09-08T12:00:00+02:00",
        "explicit_storage_release": True,
    }


def test_candidate_store_contract_endpoint_is_read_only(tmp_path) -> None:
    client = TestClient(create_app(frontend_dist=tmp_path))
    endpoint = "/api/strategies/execution-candidate-store-contract"

    response = client.get(endpoint)

    assert response.status_code == 200
    payload = response.json()
    assert payload["schema_version"] == "ims.strategy-execution-candidate-store.v1"
    assert payload["candidate_persistence_enabled"] is True
    assert payload["explicit_storage_release_required"] is True
    assert payload["candidate_update_enabled"] is False
    assert payload["runner_enabled"] is False
    assert client.post(endpoint, json={}).status_code == 405
    assert client.put(endpoint, json={}).status_code == 405
    assert client.delete(endpoint).status_code == 405


def test_candidate_store_persists_replays_and_reads(
    monkeypatch,
    tmp_path,
) -> None:
    db_path = tmp_path / "metadata.sqlite"
    monkeypatch.setenv("IMS_METADATA_DB", str(db_path))
    client = TestClient(create_app(frontend_dist=tmp_path))
    request = _store_request(client)
    endpoint = "/api/strategies/execution-candidate-store"

    created = client.post(endpoint, json=request)
    replayed = client.post(endpoint, json=request)
    read = client.get(
        f"/api/strategies/execution-candidates/{request['expected_candidate_id']}"
    )

    assert created.status_code == 201
    assert created.json()["new_record_created"] is True
    assert created.json()["candidate_persisted"] is True
    assert created.json()["execution_performed"] is False
    assert replayed.status_code == 200
    assert replayed.json()["replayed"] is True
    assert replayed.json()["writes_performed"] is False
    assert read.status_code == 200
    assert read.json()["record"] == created.json()["record"]
    assert read.json()["post_storage_digest_verified"] is True
    assert read.json()["writes_performed"] is False
    assert client.get(endpoint).status_code == 405
    assert client.put(endpoint, json=request).status_code == 405
    assert client.delete(endpoint).status_code == 405


def test_candidate_store_rejects_missing_sqlite_invalid_json_and_release(
    tmp_path,
) -> None:
    memory_client = TestClient(create_app(frontend_dist=tmp_path))
    endpoint = "/api/strategies/execution-candidate-store"

    unavailable = memory_client.post(endpoint, json={})

    assert unavailable.status_code == 400
    assert unavailable.json()["issues"][0]["code"] == (
        "explicit_sqlite_store_required"
    )
    assert unavailable.json()["writes_performed"] is False


def test_candidate_store_invalid_json_and_missing_release_are_atomic(
    monkeypatch,
    tmp_path,
) -> None:
    db_path = tmp_path / "metadata.sqlite"
    monkeypatch.setenv("IMS_METADATA_DB", str(db_path))
    client = TestClient(create_app(frontend_dist=tmp_path))
    endpoint = "/api/strategies/execution-candidate-store"
    request = _store_request(client)
    request["explicit_storage_release"] = False

    invalid_json = client.post(
        endpoint,
        content="{",
        headers={"content-type": "application/json"},
    )
    missing_release = client.post(endpoint, json=request)

    assert invalid_json.status_code == 400
    assert invalid_json.json()["issues"][0]["code"] == "invalid_json"
    assert invalid_json.json()["candidate_persisted"] is False
    assert missing_release.status_code == 409
    assert missing_release.json()["issues"][0]["code"] == "storage_release_required"
    assert missing_release.json()["writes_performed"] is False
    assert not db_path.exists()


def test_candidate_read_reports_unknown_id(monkeypatch, tmp_path) -> None:
    db_path = tmp_path / "metadata.sqlite"
    monkeypatch.setenv("IMS_METADATA_DB", str(db_path))
    client = TestClient(create_app(frontend_dist=tmp_path))
    request = _store_request(client)
    client.post("/api/strategies/execution-candidate-store", json=request)

    response = client.get(
        "/api/strategies/execution-candidates/strategy-candidate-unknown"
    )

    assert response.status_code == 404
    assert response.json()["issues"][0]["code"] == "candidate_not_found"
    assert response.json()["candidate_persisted"] is False
