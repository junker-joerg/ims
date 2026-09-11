from pathlib import Path

import pytest
from starlette.testclient import TestClient

from ims.api.metadata_import import MetadataImportError
from ims.api.strategy_execution_candidate_effect_probe_browser_smoke import (
    create_strategy_candidate_browser_smoke_app,
    require_strategy_candidate_browser_smoke_host,
)


def _frontend_dist(tmp_path: Path) -> Path:
    dist = tmp_path / "dist"
    dist.mkdir()
    (dist / "index.html").write_text(
        "<!doctype html><title>IMS Workbench</title>", encoding="utf-8"
    )
    return dist


def _candidate(client: TestClient) -> dict[str, object]:
    response = client.get("/api/strategies/execution-candidates")
    assert response.status_code == 200
    payload = response.json()
    assert payload["candidate_count"] == 1
    return payload["candidates"][0]


def _start_request(
    candidate: dict[str, object],
    *,
    key: str = "pr132-browser-success-001",
) -> dict[str, object]:
    return {
        "schema_version": "ims.strategy-execution-candidate-effect-probe-request.v1",
        "release": {
            "schema_version": "ims.strategy-execution-candidate-run-control-request.v1",
            "candidate_id": candidate["candidate_id"],
            "expected_content_digest": candidate["content_digest"],
            "idempotency_key": key,
            "explicit_run_control_release": True,
            "released_by": "pr132-browser-review",
            "released_at": "2026-09-11T07:15:00Z",
            "release_reason": "Vollstaendiger PR132-Browser-Smoke",
        },
        "explicit_effect_probe_execution": True,
    }


def test_browser_smoke_executes_and_persists_the_complete_single_period_path(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "metadata.sqlite"
    client = TestClient(
        create_strategy_candidate_browser_smoke_app(
            db_path=db_path,
            frontend_dist=_frontend_dist(tmp_path),
        )
    )
    candidate = _candidate(client)

    started = client.post(
        "/api/run-control/strategy-candidate-effect-probe-start",
        json=_start_request(candidate),
    )
    result = client.get(
        "/api/run-control/strategy-candidate-effect-probe-result/"
        f"{candidate['candidate_id']}"
    )
    history = client.get(
        "/api/run-control/strategy-candidate-effect-probe-history/"
        f"{candidate['candidate_id']}"
    )

    assert started.status_code == 201
    assert started.json()["runner_invocation_count"] == 1
    assert started.json()["result_persisted"] is True
    assert started.json()["record"]["result_payload"]["period_count"] == 1
    assert started.json()["carryover_performed"] is False
    assert started.json()["output_files_written"] is False
    assert started.json()["simulation_performed"] is False
    assert started.json()["historical_full_equality_claim"] is False
    assert result.status_code == 200
    assert result.json()["result_available"] is True
    assert result.json()["record"]["result_payload"]["effect"]["period"] == 2
    assert history.status_code == 200
    assert history.json()["attempt_count"] == 1
    assert history.json()["attempts"][0]["status"] == "result_persisted"

    replay = client.post(
        "/api/run-control/strategy-candidate-effect-probe-start",
        json=_start_request(candidate),
    )
    assert replay.status_code == 200
    assert replay.json()["replayed"] is True
    assert replay.json()["runner_invocation_count"] == 0
    assert (
        client.get(
            "/api/run-control/strategy-candidate-effect-probe-history/"
            f"{candidate['candidate_id']}"
        ).json()["attempt_count"]
        == 1
    )


def test_browser_smoke_error_paths_are_atomic_and_visible_in_history(
    tmp_path: Path,
) -> None:
    def failing_runner(*args, **kwargs):
        raise RuntimeError("deterministic PR132 runner failure")

    db_path = tmp_path / "metadata.sqlite"
    client = TestClient(
        create_strategy_candidate_browser_smoke_app(
            db_path=db_path,
            frontend_dist=_frontend_dist(tmp_path),
            candidate_effect_probe_runner=failing_runner,
        )
    )
    candidate = _candidate(client)
    missing_confirmation = _start_request(candidate, key="pr132-missing-release")
    missing_confirmation["explicit_effect_probe_execution"] = False
    wrong_digest = _start_request(candidate, key="pr132-wrong-digest")
    wrong_digest["release"]["expected_content_digest"] = "sha256:" + "0" * 64

    blocked = client.post(
        "/api/run-control/strategy-candidate-effect-probe-start",
        json=missing_confirmation,
    )
    conflict = client.post(
        "/api/run-control/strategy-candidate-effect-probe-start",
        json=wrong_digest,
    )
    failed = client.post(
        "/api/run-control/strategy-candidate-effect-probe-start",
        json=_start_request(candidate, key="pr132-runner-failure"),
    )
    result = client.get(
        "/api/run-control/strategy-candidate-effect-probe-result/"
        f"{candidate['candidate_id']}"
    )
    history = client.get(
        "/api/run-control/strategy-candidate-effect-probe-history/"
        f"{candidate['candidate_id']}"
    )

    assert blocked.status_code == 400
    assert blocked.json()["issues"][0]["code"] == (
        "effect_probe_execution_release_required"
    )
    assert blocked.json()["writes_performed"] is False
    assert conflict.status_code == 409
    assert conflict.json()["issues"][0]["code"] == "request_identity_consistent"
    assert conflict.json()["runner_invocation_performed"] is False
    assert conflict.json()["writes_performed"] is False
    assert failed.status_code == 409
    assert failed.json()["issues"][0]["code"] == "effect_probe_runner_failed"
    assert failed.json()["runner_invocation_performed"] is True
    assert failed.json()["result_persisted"] is False
    assert result.status_code == 200
    assert result.json()["result_available"] is False
    assert history.status_code == 200
    assert history.json()["attempt_count"] == 1
    assert history.json()["attempts"][0]["status"] == "failed"
    assert "deterministic PR132 runner failure" in (
        history.json()["attempts"][0]["failure_message"]
    )


def test_browser_smoke_requires_fresh_db_built_frontend_and_loopback(
    tmp_path: Path,
) -> None:
    with pytest.raises(MetadataImportError, match="built frontend"):
        create_strategy_candidate_browser_smoke_app(
            db_path=tmp_path / "missing.sqlite",
            frontend_dist=tmp_path / "missing-dist",
        )

    db_path = tmp_path / "existing.sqlite"
    db_path.touch()
    with pytest.raises(MetadataImportError, match="fresh metadata database"):
        create_strategy_candidate_browser_smoke_app(
            db_path=db_path,
            frontend_dist=_frontend_dist(tmp_path),
        )

    assert require_strategy_candidate_browser_smoke_host("127.0.0.1") == "127.0.0.1"
    assert require_strategy_candidate_browser_smoke_host("LOCALHOST") == "localhost"
    assert require_strategy_candidate_browser_smoke_host("::1") == "::1"
    with pytest.raises(MetadataImportError, match="loopback host"):
        require_strategy_candidate_browser_smoke_host("0.0.0.0")
