import sqlite3
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Event

import pytest
from starlette.testclient import TestClient

from ims.api.app import create_app
from ims.api.metadata_import import MetadataImportError
from ims.api.metadata_repository import build_seeded_metadata_repository, connect_metadata_db
from ims.api.run_control_adapter_start import start_run_control_adapter
from ims.api.run_control_execution_release import (
    build_default_execution_release_profiles,
    check_run_control_execution_release,
    parse_run_control_execution_release_payload,
)
from ims.api.run_control_execution_result_store import get_run_control_execution_result
from ims.api.run_control_preflight import preflight_run_control
from ims.api.run_control_queue import (
    WorkbenchRunControlQueueRepository,
    get_run_control_queue_entry,
)
from ims.api.run_control_requests import WorkbenchRunControlRequest


REPO_ROOT = Path(__file__).resolve().parent.parent


def _release_payload(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "schema_version": "ims.workbench.metadata.v1",
        "queue_id": "baseline-python-tests",
        "run_id": "baseline-python-tests",
        "scenario_id": "agrsich-reference-window",
        "release_profile_id": "vu14-calculated-diagnostic",
        "idempotency_key": "adapter-start-001",
        "expected_adapter_mode": "explicit_multi_period_fixture_adapter",
        "explicit_execution_release": True,
        "released_by": "local-reviewer",
        "released_at": "2026-08-24T12:00:00Z",
        "release_reason": "Kontrollierter lokaler Adapterstart",
    }
    payload.update(overrides)
    return payload


def _summary_payload() -> dict[str, object]:
    return {
        "mode": "explicit_multi_period_execution_summary",
        "period_count": 1,
        "processed_local_periods": [1],
        "processed_global_periods": [1],
        "total_vu_rule_applications": 0,
        "total_vn_insurance_rule_applications": 0,
        "total_vn_settlement_applications": 0,
        "total_vn_damage_settlement_applications": 0,
        "carryover_count": 0,
        "vu_carryover_count": 0,
        "vn_carryover_count": 0,
        "written_file_count": 0,
        "legacy_comparison_performed": False,
        "legacy_comparison_matches": None,
        "legacy_report_written_file_count": 0,
        "writes_performed": False,
        "execution_performed": True,
        "automatic_historical_rule_selection_performed": False,
        "simulation_performed": False,
    }


def _adapter_payload(fixture_path: str | Path) -> dict[str, object]:
    return {
        "status": "ok",
        "mode": "controlled_execution_adapter",
        "adapter_mode": "explicit_multi_period_fixture_adapter",
        "fixture_path": str(Path(fixture_path).resolve()),
        "fixture_kind": "explicit_multi_period_fixture",
        "explicit_execution_release": True,
        "requested_carry_forward_vu_state": False,
        "requested_carry_forward_vn_state": False,
        "summary": _summary_payload(),
        "contract": {},
        "http_enabled": False,
        "ui_enabled": False,
        "queue_worker_enabled": False,
        "writes_enabled": False,
        "writes_performed": False,
        "execution_performed": True,
        "simulation_performed": False,
        "automatic_historical_rule_selection_performed": False,
        "historical_full_equality_claimed": False,
    }


def _seed_validated_queue(db_path: Path):
    repository = build_seeded_metadata_repository(db_path)
    connection = connect_metadata_db(db_path)
    try:
        WorkbenchRunControlQueueRepository(connection).enqueue(
            WorkbenchRunControlRequest(
                run_id="baseline-python-tests",
                scenario_id="agrsich-reference-window",
                requested_by="local-user",
                created_at="2026-08-24T11:55:00Z",
                metadata_db=str(db_path),
            ),
            status="validated",
        )
    finally:
        connection.close()
    return repository


def _release(db_path: Path, payload: dict[str, object]):
    request = parse_run_control_execution_release_payload(payload)
    queue_entry = get_run_control_queue_entry(request.queue_id, db_path=db_path).entry
    return check_run_control_execution_release(
        request,
        queue_entry=queue_entry,
        preflight=preflight_run_control(request.run_id, db_path),
        profiles=build_default_execution_release_profiles(REPO_ROOT),
        trusted_fixture_root=REPO_ROOT / "tests" / "fixtures",
    )


def test_adapter_start_endpoint_persists_once_and_replays_without_rerun(tmp_path: Path) -> None:
    db_path = tmp_path / "metadata.sqlite"
    repository = _seed_validated_queue(db_path)
    calls: list[str] = []

    def fake_runner(fixture_path, **kwargs):
        calls.append(str(fixture_path))
        assert kwargs["explicit_execution_release"] is True
        return _adapter_payload(fixture_path)

    client = TestClient(
        create_app(
            frontend_dist=tmp_path,
            metadata_repository=repository,
            adapter_runner=fake_runner,
        )
    )

    first = client.post("/api/run-control/adapter-start", json=_release_payload())
    replay = client.post("/api/run-control/adapter-start", json=_release_payload())

    assert first.status_code == 201
    assert replay.status_code == 200
    assert first.json()["replayed"] is False
    assert replay.json()["replayed"] is True
    assert first.json()["result_persisted"] is True
    assert first.json()["simulation_performed"] is False
    assert replay.json()["adapter_started"] is False
    assert len(calls) == 1
    queue = get_run_control_queue_entry("baseline-python-tests", db_path=db_path).entry
    assert queue is not None
    assert queue.status == "result_persisted"
    assert queue.execution_performed is True
    assert get_run_control_execution_result(
        "baseline-python-tests", db_path=db_path
    ).record is not None
    with sqlite3.connect(db_path) as connection:
        attempt = connection.execute(
            "SELECT status, adapter_started, result_persisted, released_at, started_at "
            "FROM run_control_execution_attempts"
        ).fetchone()
    assert attempt[:4] == ("result_persisted", 1, 1, "2026-08-24T12:00:00Z")
    assert attempt[4].endswith("Z")


def test_adapter_start_rejects_changed_payload_for_same_idempotency_key(tmp_path: Path) -> None:
    db_path = tmp_path / "metadata.sqlite"
    repository = _seed_validated_queue(db_path)
    calls = 0

    def fake_runner(fixture_path, **kwargs):
        nonlocal calls
        calls += 1
        return _adapter_payload(fixture_path)

    client = TestClient(
        create_app(
            frontend_dist=tmp_path,
            metadata_repository=repository,
            adapter_runner=fake_runner,
        )
    )
    assert client.post("/api/run-control/adapter-start", json=_release_payload()).status_code == 201

    response = client.post(
        "/api/run-control/adapter-start",
        json=_release_payload(release_reason="Geaenderte Freigabe"),
    )

    assert response.status_code == 409
    assert "different release payload" in response.json()["message"]
    assert calls == 1


def test_adapter_start_claim_blocks_concurrent_duplicate(tmp_path: Path) -> None:
    db_path = tmp_path / "metadata.sqlite"
    _seed_validated_queue(db_path)
    release = _release(db_path, _release_payload())
    entered = Event()
    finish = Event()
    calls = 0

    def blocking_runner(fixture_path, **kwargs):
        nonlocal calls
        calls += 1
        entered.set()
        assert finish.wait(timeout=5)
        return _adapter_payload(fixture_path)

    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(
            start_run_control_adapter,
            release,
            db_path=db_path,
            adapter_runner=blocking_runner,
        )
        assert entered.wait(timeout=5)
        with pytest.raises(MetadataImportError, match="already starting"):
            start_run_control_adapter(
                release,
                db_path=db_path,
                adapter_runner=blocking_runner,
            )
        finish.set()
        result = future.result(timeout=5)

    assert result.replayed is False
    assert calls == 1


def test_adapter_start_failure_is_recorded_without_result_or_simulation_claim(tmp_path: Path) -> None:
    db_path = tmp_path / "metadata.sqlite"
    repository = _seed_validated_queue(db_path)

    def failing_runner(fixture_path, **kwargs):
        raise ValueError("synthetic adapter failure")

    client = TestClient(
        create_app(
            frontend_dist=tmp_path,
            metadata_repository=repository,
            adapter_runner=failing_runner,
        )
    )

    response = client.post("/api/run-control/adapter-start", json=_release_payload())

    assert response.status_code == 409
    assert response.json()["adapter_started"] is True
    assert response.json()["writes_performed"] is True
    assert response.json()["simulation_performed"] is False
    queue = get_run_control_queue_entry("baseline-python-tests", db_path=db_path).entry
    assert queue is not None
    assert queue.status == "failed"
    assert queue.execution_performed is False
    with pytest.raises(MetadataImportError, match="not found|not readable"):
        get_run_control_execution_result("baseline-python-tests", db_path=db_path)
    with sqlite3.connect(db_path) as connection:
        assert connection.execute(
            "SELECT status, adapter_started, result_persisted, simulation_performed "
            "FROM run_control_execution_attempts"
        ).fetchone() == ("failed", 1, 0, 0)
