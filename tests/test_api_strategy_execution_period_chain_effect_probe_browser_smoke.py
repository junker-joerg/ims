from pathlib import Path

import pytest
from starlette.testclient import TestClient

from ims.api.metadata_import import MetadataImportError
from ims.api.strategy_execution_period_chain_effect_probe_browser_smoke import (
    create_strategy_period_chain_browser_smoke_app,
    require_strategy_period_chain_browser_smoke_host,
)
from ims.engine.explicit_period_runner import run_loaded_explicit_period


def _frontend_dist(tmp_path: Path) -> Path:
    dist = tmp_path / "dist"
    dist.mkdir()
    (dist / "index.html").write_text(
        "<!doctype html><title>IMS Workbench</title>", encoding="utf-8"
    )
    return dist


def _chain(client: TestClient) -> dict[str, object]:
    response = client.get("/api/strategies/execution-period-chains")
    assert response.status_code == 200
    payload = response.json()
    assert payload["period_chain_count"] == 1
    return payload["period_chains"][0]


def _start_request(
    chain: dict[str, object],
    *,
    key: str = "pr141-browser-success-001",
) -> dict[str, object]:
    return {
        "schema_version": (
            "ims.strategy-execution-period-chain-effect-probe-request.v1"
        ),
        "release": {
            "schema_version": (
                "ims.strategy-execution-period-chain-run-control-request.v1"
            ),
            "chain_id": chain["chain_id"],
            "expected_content_digest": chain["content_digest"],
            "idempotency_key": key,
            "explicit_run_control_release": True,
            "released_by": "pr141-browser-review",
            "released_at": "2026-09-14T09:15:00Z",
            "release_reason": "Vollstaendiger PR141-Browser-Smoke",
        },
        "explicit_two_period_effect_probe_execution": True,
    }


def test_browser_smoke_executes_and_persists_complete_two_period_path(
    tmp_path: Path,
) -> None:
    calls = 0

    def counting_runner(loaded, *, output_dir=None):
        nonlocal calls
        calls += 1
        return run_loaded_explicit_period(loaded, output_dir=output_dir)

    db_path = tmp_path / "metadata.sqlite"
    client = TestClient(
        create_strategy_period_chain_browser_smoke_app(
            db_path=db_path,
            frontend_dist=_frontend_dist(tmp_path),
            period_chain_effect_probe_runner=counting_runner,
        )
    )
    chain = _chain(client)

    started = client.post(
        "/api/run-control/strategy-period-chain-effect-probe-start",
        json=_start_request(chain),
    )
    result = client.get(
        "/api/run-control/strategy-period-chain-effect-probe-result/"
        f"{chain['chain_id']}"
    )
    history = client.get(
        "/api/run-control/strategy-period-chain-effect-probe-history/"
        f"{chain['chain_id']}"
    )

    assert started.status_code == 201
    assert started.json()["runner_invocation_count"] == 2
    assert started.json()["carryover_invocation_count"] == 2
    assert started.json()["result_persisted"] is True
    assert started.json()["partial_result_returned"] is False
    assert started.json()["output_files_written"] is False
    assert started.json()["simulation_performed"] is False
    assert started.json()["historical_full_equality_claim"] is False
    assert calls == 2
    assert result.status_code == 200
    assert result.json()["result_available"] is True
    result_payload = result.json()["record"]["result_payload"]
    assert [effect["period"] for effect in result_payload["period_effects"]] == [
        1,
        2,
    ]
    transition = result_payload["transition_effect"]
    assert transition["from_period"] == 1
    assert transition["to_period"] == 2
    assert transition["vu_carryover_executed"] is True
    assert transition["vn_carryover_executed"] is True
    assert history.status_code == 200
    assert history.json()["attempt_count"] == 1
    assert history.json()["attempts"][0]["status"] == "result_persisted"

    replay = client.post(
        "/api/run-control/strategy-period-chain-effect-probe-start",
        json=_start_request(chain),
    )
    assert replay.status_code == 200
    assert replay.json()["replayed"] is True
    assert replay.json()["runner_invocation_count"] == 0
    assert replay.json()["carryover_invocation_count"] == 0
    assert replay.json()["writes_performed"] is False
    assert calls == 2
    assert (
        client.get(
            "/api/run-control/strategy-period-chain-effect-probe-history/"
            f"{chain['chain_id']}"
        ).json()["attempt_count"]
        == 1
    )


def test_browser_smoke_error_paths_are_atomic_and_visible_in_history(
    tmp_path: Path,
) -> None:
    calls: list[int] = []

    def failing_second_period_runner(loaded, *, output_dir=None):
        calls.append(loaded.context.period)
        if loaded.context.period == 2:
            raise RuntimeError("deterministic PR141 second-period failure")
        return run_loaded_explicit_period(loaded, output_dir=output_dir)

    db_path = tmp_path / "metadata.sqlite"
    client = TestClient(
        create_strategy_period_chain_browser_smoke_app(
            db_path=db_path,
            frontend_dist=_frontend_dist(tmp_path),
            period_chain_effect_probe_runner=failing_second_period_runner,
        )
    )
    chain = _chain(client)
    missing_confirmation = _start_request(
        chain, key="pr141-missing-release"
    )
    missing_confirmation["explicit_two_period_effect_probe_execution"] = False
    wrong_digest = _start_request(chain, key="pr141-wrong-digest")
    wrong_digest["release"]["expected_content_digest"] = "sha256:" + "0" * 64

    blocked = client.post(
        "/api/run-control/strategy-period-chain-effect-probe-start",
        json=missing_confirmation,
    )
    conflict = client.post(
        "/api/run-control/strategy-period-chain-effect-probe-start",
        json=wrong_digest,
    )
    failed = client.post(
        "/api/run-control/strategy-period-chain-effect-probe-start",
        json=_start_request(chain, key="pr141-runner-failure"),
    )
    result = client.get(
        "/api/run-control/strategy-period-chain-effect-probe-result/"
        f"{chain['chain_id']}"
    )
    history = client.get(
        "/api/run-control/strategy-period-chain-effect-probe-history/"
        f"{chain['chain_id']}"
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
    assert failed.json()["runner_invocation_count"] == 2
    assert failed.json()["partial_result_returned"] is False
    assert failed.json()["result_persisted"] is False
    assert calls == [1, 2]
    assert result.status_code == 200
    assert result.json()["result_available"] is False
    assert history.status_code == 200
    assert history.json()["attempt_count"] == 1
    assert history.json()["attempts"][0]["status"] == "failed"
    assert "deterministic PR141 second-period failure" in (
        history.json()["attempts"][0]["failure_message"]
    )


def test_browser_smoke_requires_fresh_inputs_and_loopback(tmp_path: Path) -> None:
    with pytest.raises(MetadataImportError, match="built frontend"):
        create_strategy_period_chain_browser_smoke_app(
            db_path=tmp_path / "missing.sqlite",
            frontend_dist=tmp_path / "missing-dist",
        )

    existing_db = tmp_path / "existing.sqlite"
    existing_db.touch()
    with pytest.raises(MetadataImportError, match="fresh metadata database"):
        create_strategy_period_chain_browser_smoke_app(
            db_path=existing_db,
            frontend_dist=_frontend_dist(tmp_path),
        )

    second_root = tmp_path / "second"
    second_root.mkdir()
    profile_root = second_root / "metadata-strategy-profiles"
    profile_root.mkdir()
    with pytest.raises(MetadataImportError, match="fresh profile directory"):
        create_strategy_period_chain_browser_smoke_app(
            db_path=second_root / "metadata.sqlite",
            frontend_dist=_frontend_dist(second_root),
        )

    assert require_strategy_period_chain_browser_smoke_host("127.0.0.1") == (
        "127.0.0.1"
    )
    assert require_strategy_period_chain_browser_smoke_host("LOCALHOST") == (
        "localhost"
    )
    assert require_strategy_period_chain_browser_smoke_host("::1") == "::1"
    with pytest.raises(MetadataImportError, match="loopback host"):
        require_strategy_period_chain_browser_smoke_host("0.0.0.0")
