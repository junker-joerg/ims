import json
from pathlib import Path

from fastapi.testclient import TestClient

from ims.api.app import create_app
from ims.api.strategy_execution_candidate_effect_probe import (
    STRATEGY_EXECUTION_CANDIDATE_EFFECT_PROBE_REQUEST_VERSION,
)
from ims.api.strategy_execution_candidate_run_control import (
    STRATEGY_EXECUTION_CANDIDATE_RUN_CONTROL_REQUEST_VERSION,
)
from ims.api.strategy_execution_candidate_store import (
    STRATEGY_EXECUTION_CANDIDATE_STORE_REQUEST_VERSION,
)
from ims.engine.explicit_period_runner import run_loaded_explicit_period


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
            "stored_at": "2026-09-09T09:00:00+02:00",
            "explicit_storage_release": True,
        },
    )
    assert stored.status_code == 201
    return identity["candidate_id"], identity["content_digest"]


def _request(
    candidate_id: str,
    digest: str,
    *,
    idempotency_key: str = "api-pr131-effect-probe-start-001",
) -> dict[str, object]:
    return {
        "schema_version": (
            STRATEGY_EXECUTION_CANDIDATE_EFFECT_PROBE_REQUEST_VERSION
        ),
        "release": {
            "schema_version": (
                STRATEGY_EXECUTION_CANDIDATE_RUN_CONTROL_REQUEST_VERSION
            ),
            "candidate_id": candidate_id,
            "expected_content_digest": digest,
            "idempotency_key": idempotency_key,
            "explicit_run_control_release": True,
            "released_by": "workbench-test",
            "released_at": "2026-09-09T08:30:00Z",
            "release_reason": "Kontrollierter Workbench-Start",
        },
        "explicit_effect_probe_execution": True,
    }


def test_start_contract_and_read_endpoints_are_read_only(tmp_path) -> None:
    client = TestClient(create_app(frontend_dist=tmp_path))
    contract = (
        "/api/run-control/strategy-candidate-effect-probe-start-contract"
    )

    response = client.get(contract)

    assert response.status_code == 200
    payload = response.json()
    assert payload["ui_start_enabled"] is True
    assert payload["idempotency_persistence_enabled"] is True
    assert payload["immutable_result_persistence_enabled"] is True
    assert payload["result_endpoint_template"].endswith("/{candidate_id}")
    assert payload["history_endpoint_template"].endswith("/{candidate_id}")
    assert client.post(contract, json={}).status_code == 405
    assert client.put(contract, json={}).status_code == 405
    assert client.delete(contract).status_code == 405
    for endpoint in (
        "/api/run-control/strategy-candidate-effect-probe-result/unknown",
        "/api/run-control/strategy-candidate-effect-probe-history/unknown",
    ):
        assert client.post(endpoint, json={}).status_code == 405
        assert client.put(endpoint, json={}).status_code == 405
        assert client.delete(endpoint).status_code == 405


def test_start_persists_once_and_read_endpoints_show_result_and_history(
    monkeypatch,
    tmp_path,
) -> None:
    db_path = tmp_path / "metadata.sqlite"
    monkeypatch.setenv("IMS_METADATA_DB", str(db_path))
    calls = 0

    def counting_runner(loaded, *, output_dir=None):
        nonlocal calls
        calls += 1
        return run_loaded_explicit_period(loaded, output_dir=output_dir)

    client = TestClient(
        create_app(
            frontend_dist=tmp_path,
            candidate_effect_probe_runner=counting_runner,
        )
    )
    candidate_id, digest = _persisted_identity(client)
    start_endpoint = (
        "/api/run-control/strategy-candidate-effect-probe-start"
    )

    first = client.post(start_endpoint, json=_request(candidate_id, digest))
    replay = client.post(start_endpoint, json=_request(candidate_id, digest))
    result = client.get(
        "/api/run-control/strategy-candidate-effect-probe-result/"
        + candidate_id
    )
    history = client.get(
        "/api/run-control/strategy-candidate-effect-probe-history/"
        + candidate_id
    )

    assert first.status_code == 201
    assert replay.status_code == 200
    assert first.json()["replayed"] is False
    assert replay.json()["replayed"] is True
    assert replay.json()["runner_invocation_performed"] is False
    assert calls == 1
    assert result.status_code == 200
    assert result.json()["result_available"] is True
    assert result.json()["record"]["result_payload"]["effect"]["period"] == 2
    assert result.json()["writes_performed"] is False
    assert result.json()["execution_performed"] is False
    assert history.status_code == 200
    assert history.json()["attempt_count"] == 1
    assert history.json()["latest_attempt"]["status"] == "result_persisted"
    assert history.json()["result_available"] is True
    assert history.json()["simulation_performed"] is False
    assert client.get(start_endpoint).status_code == 405
    assert client.put(start_endpoint, json={}).status_code == 405
    assert client.delete(start_endpoint).status_code == 405


def test_read_endpoints_show_empty_evidence_for_unstarted_candidate(
    monkeypatch,
    tmp_path,
) -> None:
    db_path = tmp_path / "metadata.sqlite"
    monkeypatch.setenv("IMS_METADATA_DB", str(db_path))
    client = TestClient(create_app(frontend_dist=tmp_path))
    candidate_id, _ = _persisted_identity(client)

    result = client.get(
        "/api/run-control/strategy-candidate-effect-probe-result/"
        + candidate_id
    )
    history = client.get(
        "/api/run-control/strategy-candidate-effect-probe-history/"
        + candidate_id
    )

    assert result.status_code == 200
    assert result.json()["result_available"] is False
    assert result.json()["record"] is None
    assert history.status_code == 200
    assert history.json()["attempt_count"] == 0
    assert history.json()["attempts"] == []


def test_start_requires_sqlite_and_explicit_release(monkeypatch, tmp_path) -> None:
    client = TestClient(create_app(frontend_dist=tmp_path))
    endpoint = "/api/run-control/strategy-candidate-effect-probe-start"

    missing_store = client.post(endpoint, json={})

    assert missing_store.status_code == 400
    assert missing_store.json()["issues"][0]["code"] == (
        "explicit_sqlite_store_required"
    )

    db_path = tmp_path / "metadata.sqlite"
    monkeypatch.setenv("IMS_METADATA_DB", str(db_path))
    sqlite_client = TestClient(create_app(frontend_dist=tmp_path))
    candidate_id, digest = _persisted_identity(sqlite_client)
    request = _request(candidate_id, digest)
    request["explicit_effect_probe_execution"] = False

    rejected = sqlite_client.post(endpoint, json=request)

    assert rejected.status_code == 400
    assert rejected.json()["issues"][0]["code"] == (
        "effect_probe_execution_release_required"
    )
    history = sqlite_client.get(
        "/api/run-control/strategy-candidate-effect-probe-history/"
        + candidate_id
    ).json()
    assert history["attempt_count"] == 0


def test_start_failure_is_persisted_and_visible_in_history(
    monkeypatch,
    tmp_path,
) -> None:
    db_path = tmp_path / "metadata.sqlite"
    monkeypatch.setenv("IMS_METADATA_DB", str(db_path))

    def failing_runner(loaded, *, output_dir=None):
        raise RuntimeError("synthetic API start failure")

    client = TestClient(
        create_app(
            frontend_dist=tmp_path,
            candidate_effect_probe_runner=failing_runner,
        )
    )
    candidate_id, digest = _persisted_identity(client)

    response = client.post(
        "/api/run-control/strategy-candidate-effect-probe-start",
        json=_request(candidate_id, digest),
    )
    history = client.get(
        "/api/run-control/strategy-candidate-effect-probe-history/"
        + candidate_id
    )

    assert response.status_code == 409
    payload = response.json()
    assert payload["issues"][0]["code"] == "effect_probe_runner_failed"
    assert payload["candidate_digest_reverified"] is True
    assert payload["attempt_persisted"] is True
    assert payload["runner_invocation_performed"] is True
    assert payload["result_persisted"] is False
    assert payload["simulation_performed"] is False
    assert history.status_code == 200
    assert history.json()["latest_attempt"]["status"] == "failed"
    assert history.json()["latest_attempt"]["failure_message"].endswith(
        "synthetic API start failure"
    )


def test_start_and_read_endpoints_reject_unknown_candidate(
    monkeypatch,
    tmp_path,
) -> None:
    db_path = tmp_path / "metadata.sqlite"
    monkeypatch.setenv("IMS_METADATA_DB", str(db_path))
    client = TestClient(create_app(frontend_dist=tmp_path))
    known_id, _ = _persisted_identity(client)
    unknown_id = known_id[:-1] + ("0" if known_id[-1] != "0" else "1")
    unknown_digest = "sha256:" + unknown_id.removeprefix("strategy-candidate-") + "0" * 40

    start = client.post(
        "/api/run-control/strategy-candidate-effect-probe-start",
        json=_request(unknown_id, unknown_digest),
    )
    result = client.get(
        "/api/run-control/strategy-candidate-effect-probe-result/" + unknown_id
    )
    history = client.get(
        "/api/run-control/strategy-candidate-effect-probe-history/" + unknown_id
    )

    assert start.status_code == 404
    assert start.json()["issues"][0]["code"] == "candidate_not_found"
    assert result.status_code == 404
    assert history.status_code == 404
