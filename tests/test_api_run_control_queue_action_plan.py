import json
import os
import sqlite3
import subprocess
import sys
from pathlib import Path

from ims.api.metadata_repository import (
    build_seeded_metadata_repository,
    connect_metadata_db,
    initialize_metadata_schema,
    seed_metadata,
)
from ims.api.run_control_queue import (
    WorkbenchRunControlQueueRepository,
    enqueue_run_control_request,
    initialize_run_control_queue,
)
from ims.api.run_control_queue_action_plan import (
    RunControlQueueAction,
    RunControlQueueActionPlanIssue,
    RunControlQueueActionPlanResult,
    build_run_control_queue_action_plan,
    main,
)
from ims.api.run_control_requests import parse_run_control_request_payload


def _request_payload(
    *,
    run_id: str = "baseline-python-tests",
    scenario_id: str = "agrsich-reference-window",
    execution_enabled: bool = False,
) -> dict[str, object]:
    return {
        "schema_version": "ims.workbench.metadata.v1",
        "run_id": run_id,
        "scenario_id": scenario_id,
        "metadata_db": ".ims_workbench/metadata.sqlite",
        "requested_by": "local-user",
        "created_at": "2026-06-15T00:00:00Z",
        "execution_enabled": execution_enabled,
    }


def _write_request(tmp_path: Path, payload: dict[str, object] | None = None) -> Path:
    request_path = tmp_path / f"{(payload or _request_payload())['run_id']}.json"
    request_path.write_text(json.dumps(payload or _request_payload()), encoding="utf-8")
    return request_path


def _enqueue(
    db_path: Path,
    tmp_path: Path,
    *,
    status: str = "planned",
    run_id: str = "baseline-python-tests",
    scenario_id: str = "agrsich-reference-window",
) -> None:
    payload = _request_payload(run_id=run_id, scenario_id=scenario_id)
    if status == "planned":
        enqueue_run_control_request(_write_request(tmp_path, payload), db_path=db_path)
        return
    request = parse_run_control_request_payload(payload)
    with sqlite3.connect(db_path) as connection:
        connection.row_factory = sqlite3.Row
        WorkbenchRunControlQueueRepository(connection).enqueue(request, status=status)


def _prepare_sidecar_free_wal_queue_db(db_path: Path, tmp_path: Path) -> tuple[Path, Path]:
    wal_path = Path(f"{db_path}-wal")
    shm_path = Path(f"{db_path}-shm")
    request = parse_run_control_request_payload(_request_payload())
    connection = connect_metadata_db(db_path)
    try:
        connection.execute("PRAGMA journal_mode=WAL")
        initialize_metadata_schema(connection)
        seed_metadata(connection)
        WorkbenchRunControlQueueRepository(connection).enqueue(request)
        connection.execute("SELECT COUNT(*) FROM scenarios").fetchone()
        connection.execute("PRAGMA wal_checkpoint(TRUNCATE)")
    finally:
        connection.close()
    wal_path.unlink(missing_ok=True)
    shm_path.unlink(missing_ok=True)
    return wal_path, shm_path


def test_run_control_queue_action_plan_for_valid_planned_entry(tmp_path):
    db_path = tmp_path / "metadata.sqlite"
    build_seeded_metadata_repository(db_path)
    _enqueue(db_path, tmp_path)

    payload = build_run_control_queue_action_plan(db_path).to_dict()

    assert payload["status"] == "ok"
    assert payload["mode"] == "run_control_queue_action_plan"
    assert payload["queue_count"] == 1
    assert payload["actions"][0]["queue_id"] == "baseline-python-tests"
    assert payload["actions"][0]["next_action"] == "run_preflight"
    assert payload["actions"][0]["next_action_label"] == "Lokalen Preflight ausfuehren"
    assert payload["actions"][0]["blocked_by"] == []
    assert payload["actions"][0]["execution_allowed"] is False
    assert payload["actions"][0]["writes_performed"] is False
    assert payload["actions"][0]["execution_performed"] is False
    assert payload["writes_performed"] is False
    assert payload["execution_performed"] is False
    assert RunControlQueueAction is not None
    assert RunControlQueueActionPlanIssue is not None
    assert RunControlQueueActionPlanResult is not None


def test_run_control_queue_action_plan_for_validated_entry_waits_for_release(tmp_path):
    db_path = tmp_path / "metadata.sqlite"
    build_seeded_metadata_repository(db_path)
    _enqueue(db_path, tmp_path, status="validated")

    payload = build_run_control_queue_action_plan(db_path).to_dict()

    assert payload["status"] == "ok"
    assert payload["actions"][0]["queue_status"] == "validated"
    assert payload["actions"][0]["next_action"] == "await_execution_release"
    assert payload["actions"][0]["execution_allowed"] is False


def test_run_control_queue_action_plan_for_blocked_entry_resolves_blockers(tmp_path):
    db_path = tmp_path / "metadata.sqlite"
    build_seeded_metadata_repository(db_path)
    _enqueue(db_path, tmp_path, status="blocked")

    payload = build_run_control_queue_action_plan(db_path).to_dict()

    assert payload["status"] == "ok"
    assert payload["actions"][0]["queue_status"] == "blocked"
    assert payload["actions"][0]["next_action"] == "resolve_blockers"
    assert "run_control_queue_status_blocked" in payload["actions"][0]["blocked_by"]
    assert payload["actions"][0]["execution_performed"] is False


def test_run_control_queue_action_plan_for_unknown_status_inspects_queue_status(tmp_path):
    db_path = tmp_path / "metadata.sqlite"
    build_seeded_metadata_repository(db_path)
    initialize_run_control_queue(db_path)
    with sqlite3.connect(db_path) as connection:
        connection.execute(
            """
            INSERT INTO run_control_queue (
                queue_id,
                run_id,
                scenario_id,
                metadata_db,
                requested_by,
                created_at,
                status,
                execution_enabled,
                execution_performed
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "unknown-status",
                "baseline-python-tests",
                "agrsich-reference-window",
                None,
                "local-test",
                "2026-06-15T00:00:00Z",
                "running",
                0,
                0,
            ),
        )

    payload = build_run_control_queue_action_plan(db_path).to_dict()

    assert payload["status"] == "warning"
    assert payload["actions"][0]["queue_status"] == "running"
    assert payload["actions"][0]["next_action"] == "inspect_queue_status"
    assert "run_control_queue_unsupported_status" in payload["actions"][0]["blocked_by"]


def test_run_control_queue_action_plan_reports_missing_scenario_reference(tmp_path):
    db_path = tmp_path / "metadata.sqlite"
    build_seeded_metadata_repository(db_path)
    _enqueue(db_path, tmp_path, run_id="queued-missing-scenario", scenario_id="missing-scenario")

    payload = build_run_control_queue_action_plan(db_path).to_dict()

    assert payload["status"] == "warning"
    assert payload["actions"][0]["next_action"] == "resolve_blockers"
    assert "run_control_queue_missing_scenario" in payload["actions"][0]["blocked_by"]
    assert payload["issues"][0]["code"] == "run_control_queue_missing_scenario"


def test_run_control_queue_action_plan_blocks_execution_enabled_true(tmp_path):
    db_path = tmp_path / "metadata.sqlite"
    build_seeded_metadata_repository(db_path)
    initialize_run_control_queue(db_path)
    with sqlite3.connect(db_path) as connection:
        connection.execute(
            """
            INSERT INTO run_control_queue (
                queue_id,
                run_id,
                scenario_id,
                metadata_db,
                requested_by,
                created_at,
                status,
                execution_enabled,
                execution_performed
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "bad-execution",
                "bad-execution",
                "agrsich-reference-window",
                None,
                "local-test",
                "2026-06-15T00:00:00Z",
                "planned",
                1,
                0,
            ),
        )

    payload = build_run_control_queue_action_plan(db_path).to_dict()

    assert payload["status"] == "error"
    assert payload["actions"][0]["next_action"] == "resolve_blockers"
    assert "run_control_queue_execution_enabled" in payload["actions"][0]["blocked_by"]
    assert payload["actions"][0]["execution_allowed"] is False


def test_run_control_queue_action_plan_handles_queue_only_database(tmp_path):
    db_path = tmp_path / "metadata.sqlite"
    initialize_run_control_queue(db_path)
    _enqueue(db_path, tmp_path, run_id="queue-only-run", scenario_id="queue-only-scenario")

    payload = build_run_control_queue_action_plan(db_path).to_dict()

    assert payload["status"] == "warning"
    assert payload["queue_count"] == 1
    assert payload["actions"][0]["next_action"] == "resolve_blockers"
    assert "run_control_queue_missing_metadata_schema" in payload["actions"][0]["blocked_by"]
    assert payload["writes_performed"] is False


def test_run_control_queue_action_plan_does_not_create_wal_sidecars(tmp_path):
    db_path = tmp_path / "metadata.sqlite"
    wal_path, shm_path = _prepare_sidecar_free_wal_queue_db(db_path, tmp_path)

    payload = build_run_control_queue_action_plan(db_path).to_dict()

    assert payload["status"] == "ok"
    assert payload["actions"][0]["next_action"] == "run_preflight"
    assert payload["writes_performed"] is False
    assert payload["execution_performed"] is False
    assert not wal_path.exists()
    assert not shm_path.exists()


def test_run_control_queue_action_plan_cli_does_not_create_wal_sidecars(tmp_path, capsys):
    db_path = tmp_path / "metadata.sqlite"
    wal_path, shm_path = _prepare_sidecar_free_wal_queue_db(db_path, tmp_path)

    exit_code = main(["--db", str(db_path)])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["mode"] == "run_control_queue_action_plan"
    assert payload["actions"][0]["next_action"] == "run_preflight"
    assert not wal_path.exists()
    assert not shm_path.exists()


def test_run_control_queue_action_plan_reports_uninitialized_queue(tmp_path):
    db_path = tmp_path / "metadata.sqlite"
    build_seeded_metadata_repository(db_path)

    payload = build_run_control_queue_action_plan(db_path).to_dict()

    assert payload["status"] == "warning"
    assert payload["queue_count"] == 0
    assert payload["actions"] == []
    assert any(issue["code"] == "run_control_queue_not_initialized" for issue in payload["issues"])
    assert payload["execution_performed"] is False


def test_run_control_queue_action_plan_queue_id_filters_entries(tmp_path):
    db_path = tmp_path / "metadata.sqlite"
    build_seeded_metadata_repository(db_path)
    _enqueue(db_path, tmp_path)
    _enqueue(db_path, tmp_path, run_id="workbench-shell-preview", scenario_id="local-workbench-draft")

    payload = build_run_control_queue_action_plan(db_path, queue_id="workbench-shell-preview").to_dict()

    assert payload["queue_id"] == "workbench-shell-preview"
    assert payload["queue_count"] == 1
    assert [action["queue_id"] for action in payload["actions"]] == ["workbench-shell-preview"]
    assert payload["actions"][0]["next_action"] == "run_preflight"


def test_run_control_queue_action_plan_reports_missing_queue_id_hint(tmp_path):
    db_path = tmp_path / "metadata.sqlite"
    build_seeded_metadata_repository(db_path)
    _enqueue(db_path, tmp_path)

    payload = build_run_control_queue_action_plan(db_path, queue_id="missing-queue").to_dict()

    assert payload["status"] == "warning"
    assert payload["queue_id"] == "missing-queue"
    assert payload["queue_count"] == 0
    assert payload["actions"] == []
    assert payload["issues"][0]["code"] == "run_control_queue_id_not_found"


def test_run_control_queue_action_plan_cli_prints_stable_json(tmp_path, capsys):
    db_path = tmp_path / "metadata.sqlite"
    build_seeded_metadata_repository(db_path)
    _enqueue(db_path, tmp_path)

    exit_code = main(["--db", str(db_path)])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["status"] == "ok"
    assert payload["mode"] == "run_control_queue_action_plan"
    assert payload["metadata_source"]["storage_kind"] == "sqlite"
    assert payload["actions"][0]["next_action"] == "run_preflight"
    assert payload["writes_performed"] is False
    assert payload["execution_performed"] is False


def test_run_control_queue_action_plan_missing_db_does_not_create_sqlite_file(tmp_path, capsys):
    db_path = tmp_path / "missing.sqlite"

    exit_code = main(["--db", str(db_path)])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 2
    assert payload["status"] == "error"
    assert payload["mode"] == "run_control_queue_action_plan"
    assert payload["writes_performed"] is False
    assert payload["execution_performed"] is False
    assert not db_path.exists()


def test_run_control_queue_action_plan_module_entrypoint_prints_json(tmp_path):
    db_path = tmp_path / "metadata.sqlite"
    build_seeded_metadata_repository(db_path)
    _enqueue(db_path, tmp_path)
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path(__file__).resolve().parent.parent / "python_port")

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "ims.api.run_control_queue_action_plan",
            "--db",
            str(db_path),
            "--queue-id",
            "baseline-python-tests",
        ],
        capture_output=True,
        check=False,
        env=env,
        text=True,
    )

    payload = json.loads(completed.stdout)
    assert completed.returncode == 0
    assert payload["queue_id"] == "baseline-python-tests"
    assert payload["actions"][0]["execution_allowed"] is False
