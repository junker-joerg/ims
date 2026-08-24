import sqlite3
from pathlib import Path

from starlette.testclient import TestClient

from ims.api.app import create_app
from ims.api.metadata_repository import build_seeded_metadata_repository, connect_metadata_db
from ims.api.run_control_adapter_start import RUN_CONTROL_EXECUTION_ATTEMPT_SCHEMA
from ims.api.run_control_execution_history import get_run_control_execution_history
from ims.api.run_control_execution_result_store import (
    RunControlExecutionResultRecord,
    upsert_run_control_execution_result_record,
)
from ims.api.run_control_queue import WorkbenchRunControlQueueRepository
from ims.api.run_control_requests import WorkbenchRunControlRequest


QUEUE_ID = "baseline-python-tests"


def _seed_queue(db_path: Path, *, status: str = "validated"):
    repository = build_seeded_metadata_repository(db_path)
    connection = connect_metadata_db(db_path)
    try:
        WorkbenchRunControlQueueRepository(connection).enqueue(
            WorkbenchRunControlRequest(
                run_id=QUEUE_ID,
                scenario_id="agrsich-reference-window",
                requested_by="local-user",
                created_at="2026-08-24T11:55:00Z",
                metadata_db=str(db_path),
            ),
            status=status,
        )
    finally:
        connection.close()
    return repository


def _insert_attempt(db_path: Path, *, status: str = "starting") -> None:
    with sqlite3.connect(db_path) as connection:
        connection.execute(RUN_CONTROL_EXECUTION_ATTEMPT_SCHEMA)
        connection.execute(
            """
            INSERT INTO run_control_execution_attempts (
                attempt_id, queue_id, idempotency_key, request_fingerprint, status,
                released_by, released_at, release_reason, started_at, completed_at,
                failure_message, adapter_started, result_persisted, simulation_performed
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?, 0)
            """,
            (
                "adapter-history-001",
                QUEUE_ID,
                "workbench-ui-history-001",
                "fingerprint-001",
                status,
                "local-reviewer",
                "2026-08-24T12:00:00Z",
                "Kontrollierter lokaler Adapterstart",
                "2026-08-24T12:00:01Z",
                "2026-08-24T12:00:02Z" if status != "starting" else None,
                "synthetic adapter failure" if status == "failed" else None,
                int(status == "result_persisted"),
            ),
        )
        connection.execute(
            "UPDATE run_control_queue SET status = ?, execution_performed = ? WHERE queue_id = ?",
            (status, int(status == "result_persisted"), QUEUE_ID),
        )


def _insert_persisted_result(db_path: Path) -> None:
    record = RunControlExecutionResultRecord(
        queue_id=QUEUE_ID,
        run_id=QUEUE_ID,
        scenario_id="agrsich-reference-window",
        adapter_mode="explicit_multi_period_fixture_adapter",
        fixture_kind="explicit_multi_period_fixture",
        fixture_path="tests/fixtures/replay_vu14_period_plan.json",
        summary_mode="explicit_multi_period_execution_summary",
        result_status="ok",
        persisted_at="2026-08-24T12:00:02Z",
        result_payload={"status": "ok"},
        summary_payload={"mode": "explicit_multi_period_execution_summary"},
        validation_payload={"status": "ok"},
        adapter_execution_performed=True,
        simulation_performed=False,
        automatic_historical_rule_selection_performed=False,
        historical_full_equality_claimed=False,
    )
    connection = connect_metadata_db(db_path)
    try:
        upsert_run_control_execution_result_record(connection, record)
        connection.commit()
    finally:
        connection.close()


def test_execution_history_reads_validated_queue_without_creating_attempt_table(tmp_path: Path) -> None:
    db_path = tmp_path / "metadata.sqlite"
    _seed_queue(db_path)

    payload = get_run_control_execution_history(QUEUE_ID, db_path=db_path).to_dict()

    assert payload["queue_status"] == "validated"
    assert payload["attempt_count"] == 0
    assert payload["attempts"] == []
    assert payload["latest_attempt"] is None
    assert payload["persisted_result_available"] is False
    assert payload["automatic_retry_enabled"] is False
    assert payload["queue_worker_enabled"] is False
    assert payload["writes_performed"] is False
    assert payload["execution_performed"] is False
    assert payload["adapter_started"] is False
    assert payload["simulation_performed"] is False
    with sqlite3.connect(db_path) as connection:
        assert connection.execute(
            "SELECT COUNT(*) FROM sqlite_master WHERE name = 'run_control_execution_attempts'"
        ).fetchone()[0] == 0


def test_execution_history_exposes_starting_attempt_without_retry(tmp_path: Path) -> None:
    db_path = tmp_path / "metadata.sqlite"
    _seed_queue(db_path)
    _insert_attempt(db_path)

    payload = get_run_control_execution_history(QUEUE_ID, db_path=db_path).to_dict()

    assert payload["queue_status"] == "starting"
    assert payload["attempt_count"] == 1
    assert payload["latest_attempt"]["status"] == "starting"
    assert payload["latest_attempt"]["completed_at"] is None
    assert payload["latest_attempt"]["failure_message"] is None
    assert payload["automatic_retry_enabled"] is False


def test_execution_history_exposes_failed_attempt_message_readonly(tmp_path: Path) -> None:
    db_path = tmp_path / "metadata.sqlite"
    repository = _seed_queue(db_path)
    _insert_attempt(db_path, status="failed")
    client = TestClient(create_app(frontend_dist=tmp_path, metadata_repository=repository))

    response = client.get(f"/api/run-control/execution-history/{QUEUE_ID}")

    assert response.status_code == 200
    payload = response.json()
    assert payload["mode"] == "run_control_execution_history"
    assert payload["queue_status"] == "failed"
    assert payload["latest_attempt"]["failure_message"] == "synthetic adapter failure"
    assert payload["persisted_result_available"] is False
    assert payload["automatic_retry_enabled"] is False
    assert payload["writes_performed"] is False
    assert payload["simulation_performed"] is False


def test_execution_history_links_persisted_attempt_to_existing_result(tmp_path: Path) -> None:
    db_path = tmp_path / "metadata.sqlite"
    _seed_queue(db_path)
    _insert_attempt(db_path, status="result_persisted")
    _insert_persisted_result(db_path)

    first = get_run_control_execution_history(QUEUE_ID, db_path=db_path).to_dict()
    repeated = get_run_control_execution_history(QUEUE_ID, db_path=db_path).to_dict()

    assert first == repeated
    assert first["queue_status"] == "result_persisted"
    assert first["latest_attempt"]["result_persisted"] is True
    assert first["persisted_result_available"] is True
    assert first["persisted_at"] == "2026-08-24T12:00:02Z"
    assert first["historical_full_equality_claimed"] is False


def test_execution_history_endpoint_reports_unknown_queue_without_side_effects(tmp_path: Path) -> None:
    db_path = tmp_path / "metadata.sqlite"
    repository = _seed_queue(db_path)
    client = TestClient(create_app(frontend_dist=tmp_path, metadata_repository=repository))

    response = client.get("/api/run-control/execution-history/missing-queue")

    assert response.status_code == 404
    payload = response.json()
    assert payload["mode"] == "run_control_execution_history"
    assert payload["queue_id"] == "missing-queue"
    assert payload["attempts"] == []
    assert payload["automatic_retry_enabled"] is False
    assert payload["writes_performed"] is False
    assert payload["execution_performed"] is False
    assert payload["adapter_started"] is False
    assert payload["simulation_performed"] is False
