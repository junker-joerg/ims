import importlib

from fastapi.testclient import TestClient

from ims.api.app import create_app
from ims.api.strategy_execution_period_chain_build import (
    build_strategy_execution_period_chain,
    strategy_execution_period_chain_id_from_digest,
)
from ims.api.strategy_execution_period_chain_run_control import (
    STRATEGY_EXECUTION_PERIOD_CHAIN_RUN_CONTROL_REQUEST_VERSION,
)
from ims.api.strategy_execution_period_chain_store import (
    STRATEGY_EXECUTION_PERIOD_CHAIN_STORE_REQUEST_VERSION,
    persist_strategy_execution_period_chain,
)
from tests.period_chain_test_support import (
    chain_input,
    persist_chain_candidates,
)


def _persisted_identity(db_path, profile_root) -> tuple[str, str]:
    references = persist_chain_candidates(db_path, profile_root)
    period_chain_input = chain_input(references)
    build = build_strategy_execution_period_chain(
        period_chain_input,
        db_path=db_path,
    )
    assert build.chain is not None, build.issues
    persisted = persist_strategy_execution_period_chain(
        {
            "schema_version": STRATEGY_EXECUTION_PERIOD_CHAIN_STORE_REQUEST_VERSION,
            "period_chain_input": period_chain_input,
            "expected_chain_id": build.chain.chain_id,
            "expected_content_digest": build.chain.content_digest,
            "stored_at": "2026-09-11T14:00:00+02:00",
            "explicit_storage_release": True,
        },
        db_path=db_path,
    )
    return persisted.record.chain_id, persisted.record.content_digest


def _request(chain_id: str, digest: str) -> dict[str, object]:
    return {
        "schema_version": (
            STRATEGY_EXECUTION_PERIOD_CHAIN_RUN_CONTROL_REQUEST_VERSION
        ),
        "chain_id": chain_id,
        "expected_content_digest": digest,
        "idempotency_key": "api-pr138-check-001",
        "explicit_run_control_release": True,
        "released_by": "api-test-reviewer",
        "released_at": "2026-09-11T12:30:00Z",
        "release_reason": "API-Kettenfreigabe pruefen",
    }


def test_run_control_period_chain_contract_is_read_only(tmp_path) -> None:
    client = TestClient(create_app(frontend_dist=tmp_path))
    endpoint = "/api/run-control/strategy-period-chain-contract"

    response = client.get(endpoint)

    assert response.status_code == 200
    payload = response.json()
    assert payload["run_control_release_check_enabled"] is True
    assert payload["period_chain_start_allowed"] is False
    assert payload["execution_enabled"] is False
    assert client.post(endpoint, json={}).status_code == 405
    assert client.put(endpoint, json={}).status_code == 405
    assert client.delete(endpoint).status_code == 405


def test_run_control_period_chain_release_check_is_read_only_and_ready(
    monkeypatch,
    tmp_path,
) -> None:
    db_path = tmp_path / "metadata.sqlite"
    chain_id, digest = _persisted_identity(db_path, tmp_path)
    monkeypatch.setenv("IMS_METADATA_DB", str(db_path))
    client = TestClient(create_app(frontend_dist=tmp_path))
    endpoint = "/api/run-control/strategy-period-chain-release-check"
    before = db_path.read_bytes()

    response = client.post(endpoint, json=_request(chain_id, digest))

    assert response.status_code == 200
    assert db_path.read_bytes() == before
    payload = response.json()
    assert payload["status"] == "ready"
    assert payload["release_ready"] is True
    assert payload["period_chain"]["chain_id"] == chain_id
    assert payload["period_chain_digest_reverified"] is True
    assert payload["queue_entry_created"] is False
    assert payload["period_chain_start_allowed"] is False
    assert payload["carryover_invocation_performed"] is False
    assert payload["runner_invocation_performed"] is False
    assert payload["writes_performed"] is False
    assert payload["execution_performed"] is False
    assert payload["simulation_performed"] is False
    assert client.get(endpoint).status_code == 405
    assert client.put(endpoint, json={}).status_code == 405
    assert client.delete(endpoint).status_code == 405


def test_run_control_period_chain_release_check_rejects_bad_requests(
    monkeypatch,
    tmp_path,
) -> None:
    memory_client = TestClient(create_app(frontend_dist=tmp_path))
    endpoint = "/api/run-control/strategy-period-chain-release-check"
    unavailable = memory_client.post(endpoint, json={})
    assert unavailable.status_code == 400
    assert unavailable.json()["issues"][0]["code"] == (
        "explicit_sqlite_store_required"
    )

    db_path = tmp_path / "metadata.sqlite"
    chain_id, digest = _persisted_identity(db_path, tmp_path)
    monkeypatch.setenv("IMS_METADATA_DB", str(db_path))
    client = TestClient(create_app(frontend_dist=tmp_path))
    invalid_json = client.post(
        endpoint,
        content="{",
        headers={"content-type": "application/json"},
    )
    missing_release = _request(chain_id, digest)
    missing_release["explicit_run_control_release"] = False
    rejected = client.post(endpoint, json=missing_release)

    assert invalid_json.status_code == 400
    assert invalid_json.json()["issues"][0]["code"] == "invalid_json"
    assert invalid_json.json()["next_gate"] == "PR139"
    assert rejected.status_code == 400
    assert rejected.json()["issues"][0]["code"] == "run_control_release_required"
    assert rejected.json()["writes_performed"] is False


def test_run_control_period_chain_reports_missing_and_changed_digest(
    monkeypatch,
    tmp_path,
) -> None:
    db_path = tmp_path / "metadata.sqlite"
    chain_id, digest = _persisted_identity(db_path, tmp_path)
    monkeypatch.setenv("IMS_METADATA_DB", str(db_path))
    client = TestClient(create_app(frontend_dist=tmp_path))
    endpoint = "/api/run-control/strategy-period-chain-release-check"

    unknown_digest = "sha256:" + "f" * 64
    unknown = client.post(
        endpoint,
        json=_request(
            strategy_execution_period_chain_id_from_digest(unknown_digest),
            unknown_digest,
        ),
    )
    changed_last = "0" if digest[-1] != "0" else "1"
    changed = client.post(
        endpoint,
        json=_request(chain_id, digest[:-1] + changed_last),
    )

    assert unknown.status_code == 404
    assert unknown.json()["issues"][0]["code"] == "period_chain_not_found"
    assert changed.status_code == 409
    assert changed.json()["issues"][0]["code"] == "expected_digest_matches"
    assert changed.json()["execution_performed"] is False


def test_starlette_fallback_exposes_same_read_only_release_check(
    monkeypatch,
    tmp_path,
) -> None:
    db_path = tmp_path / "metadata.sqlite"
    chain_id, digest = _persisted_identity(db_path, tmp_path)
    monkeypatch.setenv("IMS_METADATA_DB", str(db_path))
    app_module = importlib.import_module("ims.api.app")
    monkeypatch.setattr(app_module, "FastAPI", None)
    client = TestClient(create_app(frontend_dist=tmp_path))

    contract = client.get("/api/run-control/strategy-period-chain-contract")
    checked = client.post(
        "/api/run-control/strategy-period-chain-release-check",
        json=_request(chain_id, digest),
    )

    assert contract.status_code == 200
    assert contract.json()["next_gate"] == "PR139"
    assert checked.status_code == 200
    assert checked.json()["release_ready"] is True
    assert checked.json()["writes_performed"] is False
    assert checked.json()["execution_performed"] is False
