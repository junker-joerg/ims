import json
from pathlib import Path

from fastapi.testclient import TestClient

from ims.api.app import create_app
from ims.api.strategy_execution_candidate_run_control import (
    STRATEGY_EXECUTION_CANDIDATE_RUN_CONTROL_REQUEST_VERSION,
)
from ims.api.strategy_execution_candidate_store import (
    STRATEGY_EXECUTION_CANDIDATE_STORE_REQUEST_VERSION,
)
from ims.strategies.execution_candidate_build import (
    strategy_execution_candidate_id_from_digest,
)


FIXTURE = (
    Path(__file__).parent
    / "fixtures"
    / "strategy_execution_candidate_input_v1.json"
)


def _persisted_identity(client: TestClient) -> tuple[str, str]:
    candidate_input = json.loads(FIXTURE.read_text(encoding="utf-8"))
    build = client.post(
        "/api/strategies/execution-candidate-build",
        json=candidate_input,
    ).json()
    identity = build["candidate"]["identity"]
    stored = client.post(
        "/api/strategies/execution-candidate-store",
        json={
            "schema_version": STRATEGY_EXECUTION_CANDIDATE_STORE_REQUEST_VERSION,
            "candidate_input": candidate_input,
            "expected_candidate_id": identity["candidate_id"],
            "expected_content_digest": identity["content_digest"],
            "stored_at": "2026-09-08T12:00:00+02:00",
            "explicit_storage_release": True,
        },
    )
    assert stored.status_code == 201
    return identity["candidate_id"], identity["content_digest"]


def _request(candidate_id: str, digest: str) -> dict[str, object]:
    return {
        "schema_version": STRATEGY_EXECUTION_CANDIDATE_RUN_CONTROL_REQUEST_VERSION,
        "candidate_id": candidate_id,
        "expected_content_digest": digest,
        "idempotency_key": "api-pr129-check-001",
        "explicit_run_control_release": True,
        "released_by": "api-test-reviewer",
        "released_at": "2026-09-08T10:30:00Z",
        "release_reason": "API-Freigabegrenze pruefen",
    }


def test_run_control_candidate_contract_is_read_only(tmp_path) -> None:
    client = TestClient(create_app(frontend_dist=tmp_path))
    endpoint = "/api/run-control/strategy-candidate-contract"

    response = client.get(endpoint)

    assert response.status_code == 200
    payload = response.json()
    assert payload["run_control_release_check_enabled"] is True
    assert payload["adapter_start_allowed"] is False
    assert payload["execution_enabled"] is False
    assert client.post(endpoint, json={}).status_code == 405
    assert client.put(endpoint, json={}).status_code == 405
    assert client.delete(endpoint).status_code == 405


def test_run_control_candidate_release_check_is_read_only_and_ready(
    monkeypatch,
    tmp_path,
) -> None:
    db_path = tmp_path / "metadata.sqlite"
    monkeypatch.setenv("IMS_METADATA_DB", str(db_path))
    client = TestClient(create_app(frontend_dist=tmp_path))
    candidate_id, digest = _persisted_identity(client)
    endpoint = "/api/run-control/strategy-candidate-release-check"

    response = client.post(endpoint, json=_request(candidate_id, digest))

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ready"
    assert payload["release_ready"] is True
    assert payload["candidate"]["candidate_id"] == candidate_id
    assert payload["candidate_digest_reverified"] is True
    assert payload["queue_entry_created"] is False
    assert payload["adapter_start_allowed"] is False
    assert payload["runner_invocation_performed"] is False
    assert payload["writes_performed"] is False
    assert payload["execution_performed"] is False
    assert payload["simulation_performed"] is False
    assert client.get(endpoint).status_code == 405
    assert client.put(endpoint, json={}).status_code == 405
    assert client.delete(endpoint).status_code == 405


def test_run_control_candidate_release_check_rejects_bad_requests(
    monkeypatch,
    tmp_path,
) -> None:
    memory_client = TestClient(create_app(frontend_dist=tmp_path))
    endpoint = "/api/run-control/strategy-candidate-release-check"
    unavailable = memory_client.post(endpoint, json={})
    assert unavailable.status_code == 400
    assert unavailable.json()["issues"][0]["code"] == (
        "explicit_sqlite_store_required"
    )

    db_path = tmp_path / "metadata.sqlite"
    monkeypatch.setenv("IMS_METADATA_DB", str(db_path))
    client = TestClient(create_app(frontend_dist=tmp_path))
    candidate_id, digest = _persisted_identity(client)
    invalid_json = client.post(
        endpoint,
        content="{",
        headers={"content-type": "application/json"},
    )
    missing_release = _request(candidate_id, digest)
    missing_release["explicit_run_control_release"] = False
    rejected = client.post(endpoint, json=missing_release)

    assert invalid_json.status_code == 400
    assert invalid_json.json()["issues"][0]["code"] == "invalid_json"
    assert rejected.status_code == 400
    assert rejected.json()["issues"][0]["code"] == "run_control_release_required"
    assert rejected.json()["writes_performed"] is False


def test_run_control_candidate_release_check_reports_missing_and_changed_digest(
    monkeypatch,
    tmp_path,
) -> None:
    db_path = tmp_path / "metadata.sqlite"
    monkeypatch.setenv("IMS_METADATA_DB", str(db_path))
    client = TestClient(create_app(frontend_dist=tmp_path))
    candidate_id, digest = _persisted_identity(client)
    endpoint = "/api/run-control/strategy-candidate-release-check"

    unknown_digest = "sha256:" + "f" * 64
    unknown = client.post(
        endpoint,
        json=_request(
            strategy_execution_candidate_id_from_digest(unknown_digest),
            unknown_digest,
        ),
    )
    changed_last = "0" if digest[-1] != "0" else "1"
    changed = client.post(
        endpoint,
        json=_request(candidate_id, digest[:-1] + changed_last),
    )

    assert unknown.status_code == 404
    assert unknown.json()["issues"][0]["code"] == "candidate_not_found"
    assert changed.status_code == 409
    assert changed.json()["issues"][0]["code"] == "expected_digest_matches"
    assert changed.json()["execution_performed"] is False
