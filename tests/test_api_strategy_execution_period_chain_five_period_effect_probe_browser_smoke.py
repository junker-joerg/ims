from pathlib import Path

import pytest
from starlette.testclient import TestClient

from ims.api.metadata_import import MetadataImportError
from ims.api.strategy_execution_period_chain_five_period_effect_probe_browser_smoke import (
    create_strategy_five_period_browser_smoke_app,
    require_strategy_five_period_browser_smoke_host,
)
from ims.engine.explicit_period_runner import run_loaded_explicit_period


def _frontend_dist(tmp_path: Path) -> Path:
    dist = tmp_path / "dist"
    dist.mkdir()
    (dist / "index.html").write_text(
        "<!doctype html><title>IMS Workbench</title>", encoding="utf-8"
    )
    return dist


def _prepared(client: TestClient) -> tuple[dict[str, object], dict[str, str]]:
    overview = client.get("/api/strategies/execution-period-chains")
    assert overview.status_code == 200
    chains = overview.json()["period_chains"]
    assert len(chains) == 2
    five = next(chain for chain in chains if chain["period_count"] == 5)
    two = next(chain for chain in chains if chain["period_count"] == 2)
    baseline = client.get(
        "/api/run-control/strategy-period-chain-effect-probe-result/"
        f"{two['chain_id']}"
    )
    detail = client.get(
        f"/api/strategies/execution-period-chains/{five['chain_id']}"
    )
    assert baseline.status_code == 200
    assert baseline.json()["result_available"] is True
    assert detail.status_code == 200
    assert detail.json()["record"]["period_chain_input"]["max_periods"] == 5
    return five, {
        "chain_id": two["chain_id"],
        "expected_content_digest": two["content_digest"],
        "expected_result_digest": baseline.json()["record"]["result_digest"],
        "period_chain_input": detail.json()["record"]["period_chain_input"],
    }


def _start_request(
    chain: dict[str, object],
    prepared: dict[str, object],
    *,
    key: str = "pr146-browser-success-001",
) -> dict[str, object]:
    return {
        "schema_version": (
            "ims.strategy-execution-five-period-effect-probe-start-request.v1"
        ),
        "effect_probe_request": {
            "schema_version": (
                "ims.strategy-execution-five-period-effect-probe-request.v1"
            ),
            "period_chain_input": prepared["period_chain_input"],
            "prefix_baseline": {
                "chain_id": prepared["chain_id"],
                "expected_content_digest": prepared["expected_content_digest"],
                "expected_result_digest": prepared["expected_result_digest"],
            },
            "explicit_five_period_effect_probe_execution": True,
        },
        "release": {
            "schema_version": (
                "ims.strategy-execution-period-chain-run-control-request.v1"
            ),
            "chain_id": chain["chain_id"],
            "expected_content_digest": chain["content_digest"],
            "idempotency_key": key,
            "explicit_run_control_release": True,
            "released_by": "pr146-browser-review",
            "released_at": "2026-09-16T08:10:00Z",
            "release_reason": "Vollstaendiger PR146-Browser-Smoke",
        },
        "explicit_five_period_effect_probe_start": True,
    }


def test_browser_smoke_executes_persists_and_replays_five_period_path(
    tmp_path: Path,
) -> None:
    calls: list[int] = []

    def counting_runner(loaded, *, output_dir=None):
        calls.append(loaded.context.period)
        return run_loaded_explicit_period(loaded, output_dir=output_dir)

    client = TestClient(
        create_strategy_five_period_browser_smoke_app(
            db_path=tmp_path / "metadata.sqlite",
            frontend_dist=_frontend_dist(tmp_path),
            period_chain_effect_probe_runner=counting_runner,
        )
    )
    chain, prepared = _prepared(client)
    assert chain["readiness"]["exact_five_period_horizon"] is True
    assert chain["readiness"]["five_period_effect_probe_start_available"] is True
    request = _start_request(chain, prepared)

    started = client.post(
        "/api/run-control/strategy-period-chain-five-period-effect-probe-start",
        json=request,
    )
    result = client.get(
        "/api/run-control/strategy-period-chain-five-period-effect-probe-result/"
        f"{chain['chain_id']}"
    )
    history = client.get(
        "/api/run-control/strategy-period-chain-five-period-effect-probe-history/"
        f"{chain['chain_id']}"
    )

    assert started.status_code == 201
    assert started.json()["runner_invocation_count"] == 5
    assert started.json()["carryover_invocation_count"] == 8
    assert started.json()["prefix_baseline_verified"] is True
    assert calls == [1, 2, 3, 4, 5]
    assert result.status_code == 200
    payload = result.json()["record"]["result_payload"]
    assert [effect["period"] for effect in payload["period_effects"]] == [
        1,
        2,
        3,
        4,
        5,
    ]
    assert payload["two_period_prefix_verified"] is True
    assert len(payload["transition_effects"]) == 4
    assert history.status_code == 200
    assert history.json()["attempt_count"] == 1

    replay = client.post(
        "/api/run-control/strategy-period-chain-five-period-effect-probe-start",
        json=request,
    )
    assert replay.status_code == 200
    assert replay.json()["replayed"] is True
    assert replay.json()["runner_invocation_count"] == 0
    assert replay.json()["carryover_invocation_count"] == 0
    assert replay.json()["writes_performed"] is False
    assert calls == [1, 2, 3, 4, 5]


def test_browser_smoke_error_paths_are_atomic_and_visible(tmp_path: Path) -> None:
    calls: list[int] = []

    def failing_fourth_period_runner(loaded, *, output_dir=None):
        calls.append(loaded.context.period)
        if loaded.context.period == 4:
            raise RuntimeError("deterministic PR146 fourth-period failure")
        return run_loaded_explicit_period(loaded, output_dir=output_dir)

    client = TestClient(
        create_strategy_five_period_browser_smoke_app(
            db_path=tmp_path / "metadata.sqlite",
            frontend_dist=_frontend_dist(tmp_path),
            period_chain_effect_probe_runner=failing_fourth_period_runner,
        )
    )
    chain, prepared = _prepared(client)
    missing_confirmation = _start_request(
        chain, prepared, key="pr146-missing-release"
    )
    missing_confirmation["explicit_five_period_effect_probe_start"] = False
    wrong_digest = _start_request(chain, prepared, key="pr146-wrong-digest")
    wrong_digest["release"]["expected_content_digest"] = "sha256:" + "0" * 64

    blocked = client.post(
        "/api/run-control/strategy-period-chain-five-period-effect-probe-start",
        json=missing_confirmation,
    )
    conflict = client.post(
        "/api/run-control/strategy-period-chain-five-period-effect-probe-start",
        json=wrong_digest,
    )
    failed = client.post(
        "/api/run-control/strategy-period-chain-five-period-effect-probe-start",
        json=_start_request(chain, prepared, key="pr146-runner-failure"),
    )
    result = client.get(
        "/api/run-control/strategy-period-chain-five-period-effect-probe-result/"
        f"{chain['chain_id']}"
    )
    history = client.get(
        "/api/run-control/strategy-period-chain-five-period-effect-probe-history/"
        f"{chain['chain_id']}"
    )

    assert blocked.status_code == 400
    assert blocked.json()["issues"][0]["code"] == (
        "five_period_effect_probe_start_release_required"
    )
    assert blocked.json()["writes_performed"] is False
    assert conflict.status_code == 409
    assert conflict.json()["runner_invocation_performed"] is False
    assert conflict.json()["result_persisted"] is False
    assert failed.status_code == 409
    assert failed.json()["issues"][0]["code"] == "effect_probe_runner_failed"
    assert failed.json()["runner_invocation_count"] == 4
    assert failed.json()["result_persisted"] is False
    assert calls == [1, 2, 3, 4]
    assert result.status_code == 200
    assert result.json()["result_available"] is False
    assert history.status_code == 200
    assert history.json()["attempt_count"] == 2
    assert all(
        attempt["status"] == "failed"
        for attempt in history.json()["attempts"]
    )
    assert any(
        "deterministic PR146 fourth-period failure"
        in (attempt["failure_message"] or "")
        for attempt in history.json()["attempts"]
    )


def test_browser_smoke_requires_fresh_inputs_and_loopback(tmp_path: Path) -> None:
    with pytest.raises(MetadataImportError, match="built frontend"):
        create_strategy_five_period_browser_smoke_app(
            db_path=tmp_path / "missing.sqlite",
            frontend_dist=tmp_path / "missing-dist",
        )

    existing_db = tmp_path / "existing.sqlite"
    existing_db.touch()
    with pytest.raises(MetadataImportError, match="fresh metadata database"):
        create_strategy_five_period_browser_smoke_app(
            db_path=existing_db,
            frontend_dist=_frontend_dist(tmp_path),
        )

    second_root = tmp_path / "second"
    second_root.mkdir()
    profile_root = second_root / "metadata-five-period-strategy-profiles"
    profile_root.mkdir()
    with pytest.raises(MetadataImportError, match="fresh profile directory"):
        create_strategy_five_period_browser_smoke_app(
            db_path=second_root / "metadata.sqlite",
            frontend_dist=_frontend_dist(second_root),
        )

    assert require_strategy_five_period_browser_smoke_host("127.0.0.1") == (
        "127.0.0.1"
    )
    assert require_strategy_five_period_browser_smoke_host("LOCALHOST") == (
        "localhost"
    )
    assert require_strategy_five_period_browser_smoke_host("::1") == "::1"
    with pytest.raises(MetadataImportError, match="loopback host"):
        require_strategy_five_period_browser_smoke_host("0.0.0.0")
