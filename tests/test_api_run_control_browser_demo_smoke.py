from pathlib import Path

import pytest
from starlette.testclient import TestClient

from ims.api.metadata_import import MetadataImportError
from ims.api.run_control_browser_demo_smoke import (
    BROWSER_DEMO_SMOKE_QUEUE_ID,
    BROWSER_DEMO_SMOKE_SCENARIO_ID,
    create_browser_demo_smoke_app,
    require_browser_demo_smoke_host,
)


def _release_payload() -> dict[str, object]:
    return {
        "schema_version": "ims.workbench.metadata.v1",
        "queue_id": BROWSER_DEMO_SMOKE_QUEUE_ID,
        "run_id": BROWSER_DEMO_SMOKE_QUEUE_ID,
        "scenario_id": BROWSER_DEMO_SMOKE_SCENARIO_ID,
        "release_profile_id": "vu14-calculated-diagnostic",
        "idempotency_key": "pr66-browser-smoke-start-001",
        "expected_adapter_mode": "explicit_multi_period_fixture_adapter",
        "explicit_execution_release": True,
        "released_by": "pr66-browser-review",
        "released_at": "2026-08-25T08:00:00Z",
        "release_reason": "Kontrollierter PR66-Browser-Smoke",
        "carry_forward_vu_state": False,
        "carry_forward_vn_state": False,
    }


def _frontend_dist(tmp_path: Path) -> Path:
    dist = tmp_path / "dist"
    dist.mkdir()
    (dist / "index.html").write_text("<!doctype html><title>IMS Workbench</title>", encoding="utf-8")
    return dist


def test_browser_demo_smoke_persists_one_controlled_result_without_simulation(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "metadata.sqlite"
    adapter_calls: list[dict[str, object]] = []
    client = TestClient(
        create_browser_demo_smoke_app(
            db_path=db_path,
            frontend_dist=_frontend_dist(tmp_path),
            adapter_calls=adapter_calls,
        )
    )

    queue = client.get("/api/run-control/queue")
    assert queue.status_code == 200
    assert queue.json()["queue_count"] == 1
    assert queue.json()["entries"][0]["queue_id"] == BROWSER_DEMO_SMOKE_QUEUE_ID
    assert queue.json()["entries"][0]["status"] == "validated"
    assert queue.json()["entries"][0]["execution_enabled"] is False
    assert queue.json()["entries"][0]["execution_performed"] is False

    release = client.post("/api/run-control/adapter-release-check", json=_release_payload())
    assert release.status_code == 200
    assert release.json()["release_ready"] is True
    assert release.json()["simulation_performed"] is False

    started = client.post("/api/run-control/adapter-start", json=_release_payload())
    assert started.status_code == 201
    assert started.json()["queue_status"] == "result_persisted"
    assert started.json()["adapter_started"] is True
    assert started.json()["result_persisted"] is True
    assert started.json()["simulation_performed"] is False
    assert started.json()["historical_full_equality_claimed"] is False
    assert len(adapter_calls) == 1

    result = client.get(f"/api/run-control/execution-result/{BROWSER_DEMO_SMOKE_QUEUE_ID}")
    history = client.get(f"/api/run-control/execution-history/{BROWSER_DEMO_SMOKE_QUEUE_ID}")
    assert result.status_code == 200
    assert result.json()["record"]["simulation_performed"] is False
    assert result.json()["record"]["historical_full_equality_claimed"] is False
    assert history.status_code == 200
    assert history.json()["queue_status"] == "result_persisted"
    assert history.json()["attempt_count"] == 1
    assert history.json()["latest_attempt"]["status"] == "result_persisted"
    assert history.json()["automatic_retry_enabled"] is False
    assert history.json()["queue_worker_enabled"] is False
    assert history.json()["simulation_performed"] is False

    replay = client.post("/api/run-control/adapter-start", json=_release_payload())
    refreshed_result = client.get(
        f"/api/run-control/execution-result/{BROWSER_DEMO_SMOKE_QUEUE_ID}"
    )
    refreshed_history = client.get(
        f"/api/run-control/execution-history/{BROWSER_DEMO_SMOKE_QUEUE_ID}"
    )
    assert replay.status_code == 200
    assert replay.json()["replayed"] is True
    assert replay.json()["adapter_started"] is False
    assert replay.json()["writes_performed"] is False
    assert refreshed_result.json() == result.json()
    assert refreshed_history.json() == history.json()
    assert len(adapter_calls) == 1


def test_browser_demo_smoke_requires_fresh_db_built_frontend_and_loopback(
    tmp_path: Path,
) -> None:
    missing_dist = tmp_path / "missing-dist"
    with pytest.raises(MetadataImportError, match="built frontend"):
        create_browser_demo_smoke_app(
            db_path=tmp_path / "missing.sqlite",
            frontend_dist=missing_dist,
        )

    db_path = tmp_path / "existing.sqlite"
    db_path.touch()
    with pytest.raises(MetadataImportError, match="fresh metadata database"):
        create_browser_demo_smoke_app(
            db_path=db_path,
            frontend_dist=_frontend_dist(tmp_path),
        )

    assert require_browser_demo_smoke_host("127.0.0.1") == "127.0.0.1"
    assert require_browser_demo_smoke_host("LOCALHOST") == "localhost"
    assert require_browser_demo_smoke_host("::1") == "::1"
    with pytest.raises(MetadataImportError, match="loopback host"):
        require_browser_demo_smoke_host("0.0.0.0")
