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
            "stored_at": "2026-09-09T09:00:00+02:00",
            "explicit_storage_release": True,
        },
    )
    assert stored.status_code == 201
    return identity["candidate_id"], identity["content_digest"]


def _request(candidate_id: str, digest: str) -> dict[str, object]:
    return {
        "schema_version": STRATEGY_EXECUTION_CANDIDATE_EFFECT_PROBE_REQUEST_VERSION,
        "release": {
            "schema_version": (
                STRATEGY_EXECUTION_CANDIDATE_RUN_CONTROL_REQUEST_VERSION
            ),
            "candidate_id": candidate_id,
            "expected_content_digest": digest,
            "idempotency_key": "api-pr130-effect-probe-001",
            "explicit_run_control_release": True,
            "released_by": "api-test-reviewer",
            "released_at": "2026-09-09T07:05:00Z",
            "release_reason": "API-Einperioden-Wirkungsprobe",
        },
        "explicit_effect_probe_execution": True,
    }


def test_effect_probe_contract_endpoint_is_read_only(tmp_path) -> None:
    client = TestClient(create_app(frontend_dist=tmp_path))
    endpoint = "/api/run-control/strategy-candidate-effect-probe-contract"

    response = client.get(endpoint)

    assert response.status_code == 200
    payload = response.json()
    assert payload["effect_probe_execution_enabled"] is True
    assert payload["single_period_only"] is True
    assert payload["ui_start_enabled"] is False
    assert payload["output_files_enabled"] is False
    assert payload["persistent_start_endpoint"] == (
        "/api/run-control/strategy-candidate-effect-probe-start"
    )
    assert client.post(endpoint, json={}).status_code == 405
    assert client.put(endpoint, json={}).status_code == 405
    assert client.delete(endpoint).status_code == 405


def test_effect_probe_endpoint_runs_one_ephemeral_period(monkeypatch, tmp_path) -> None:
    db_path = tmp_path / "metadata.sqlite"
    monkeypatch.setenv("IMS_METADATA_DB", str(db_path))
    client = TestClient(create_app(frontend_dist=tmp_path))
    candidate_id, digest = _persisted_identity(client)
    endpoint = "/api/run-control/strategy-candidate-effect-probe"

    response = client.post(endpoint, json=_request(candidate_id, digest))

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["period_count"] == 1
    assert payload["runner_invocation_count"] == 1
    assert payload["candidate_copy_isolated"] is True
    assert payload["effect"]["period"] == 2
    assert payload["effect"]["applications"]["vu_total"] == 1
    assert payload["result_persisted"] is False
    assert payload["writes_performed"] is False
    assert payload["carryover_performed"] is False
    assert payload["output_files_written"] is False
    assert payload["legacy_comparison_performed"] is False
    assert payload["execution_performed"] is True
    assert payload["simulation_performed"] is False
    assert client.get(endpoint).status_code == 405
    assert client.put(endpoint, json={}).status_code == 405
    assert client.delete(endpoint).status_code == 405


def test_effect_probe_endpoint_rejects_missing_store_and_execution_release(
    monkeypatch,
    tmp_path,
) -> None:
    endpoint = "/api/run-control/strategy-candidate-effect-probe"
    memory_client = TestClient(create_app(frontend_dist=tmp_path))

    unavailable = memory_client.post(endpoint, json={})

    assert unavailable.status_code == 400
    assert unavailable.json()["issues"][0]["code"] == (
        "explicit_sqlite_store_required"
    )

    db_path = tmp_path / "metadata.sqlite"
    monkeypatch.setenv("IMS_METADATA_DB", str(db_path))
    client = TestClient(create_app(frontend_dist=tmp_path))
    candidate_id, digest = _persisted_identity(client)
    request = _request(candidate_id, digest)
    request["explicit_effect_probe_execution"] = False

    rejected = client.post(endpoint, json=request)

    assert rejected.status_code == 400
    assert rejected.json()["issues"][0]["code"] == (
        "effect_probe_execution_release_required"
    )
    assert rejected.json()["runner_invocation_performed"] is False
    assert rejected.json()["execution_performed"] is False


def test_effect_probe_endpoint_blocks_unknown_and_changed_digest(
    monkeypatch,
    tmp_path,
) -> None:
    db_path = tmp_path / "metadata.sqlite"
    monkeypatch.setenv("IMS_METADATA_DB", str(db_path))
    client = TestClient(create_app(frontend_dist=tmp_path))
    candidate_id, digest = _persisted_identity(client)
    endpoint = "/api/run-control/strategy-candidate-effect-probe"

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
    assert unknown.json()["execution_performed"] is False
    assert changed.status_code == 409
    assert changed.json()["issues"][0]["code"] == "expected_digest_matches"
    assert changed.json()["runner_invocation_performed"] is False


def test_effect_probe_endpoint_reports_runner_failure_without_result(
    monkeypatch,
    tmp_path,
) -> None:
    db_path = tmp_path / "metadata.sqlite"
    monkeypatch.setenv("IMS_METADATA_DB", str(db_path))

    def failing_runner(loaded, *, output_dir=None):
        assert output_dir is None
        raise RuntimeError("synthetic API runner failure")

    client = TestClient(
        create_app(
            frontend_dist=tmp_path,
            candidate_effect_probe_runner=failing_runner,
        )
    )
    candidate_id, digest = _persisted_identity(client)

    response = client.post(
        "/api/run-control/strategy-candidate-effect-probe",
        json=_request(candidate_id, digest),
    )

    assert response.status_code == 409
    payload = response.json()
    assert payload["issues"][0]["code"] == "effect_probe_runner_failed"
    assert payload["candidate_resolved"] is True
    assert payload["candidate_digest_reverified"] is True
    assert payload["run_control_release_checked"] is True
    assert payload["effect_probe_execution_released"] is True
    assert payload["runner_invocation_performed"] is True
    assert payload["result_persisted"] is False
    assert payload["execution_performed"] is False
    assert payload["writes_performed"] is False
    assert payload["simulation_performed"] is False
