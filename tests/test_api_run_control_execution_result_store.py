import json
import os
import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest
from starlette.testclient import TestClient

from ims.api.app import create_app
from ims.api.metadata_import import MetadataImportError
from ims.api.metadata_repository import build_seeded_metadata_repository
from ims.api.run_control_execution_result_store import (
    RunControlExecutionResultRecord,
    RunControlExecutionResultStoreResult,
    get_run_control_execution_result,
    initialize_run_control_execution_result_store,
    main,
    persist_run_control_adapter_result,
)
from ims.api.run_control_queue import WorkbenchRunControlQueueRepository, get_run_control_queue_entry
from ims.api.run_control_requests import parse_run_control_request_payload


def _request_payload() -> dict[str, object]:
    return {
        "schema_version": "ims.workbench.metadata.v1",
        "run_id": "baseline-python-tests",
        "scenario_id": "agrsich-reference-window",
        "metadata_db": ".ims_workbench/metadata.sqlite",
        "requested_by": "local-user",
        "created_at": "2026-06-15T00:00:00Z",
        "execution_enabled": False,
    }


def _summary_payload() -> dict[str, object]:
    return {
        "mode": "explicit_multi_period_execution_summary",
        "period_count": 2,
        "processed_local_periods": [1, 2],
        "processed_global_periods": [1, 2],
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


def _adapter_result_payload() -> dict[str, object]:
    return {
        "status": "ok",
        "mode": "controlled_execution_adapter",
        "adapter_mode": "explicit_multi_period_fixture_adapter",
        "fixture_path": "tests/fixtures/replay_vn_policyholder_transition_plan.json",
        "fixture_kind": "explicit_vu_vn_period_plan_fixture",
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


def _write_adapter_result(tmp_path: Path, payload: dict[str, object] | None = None) -> Path:
    path = tmp_path / "adapter_result.json"
    path.write_text(json.dumps(payload or _adapter_result_payload()), encoding="utf-8")
    return path


def _enqueue_validated(db_path: Path) -> None:
    request = parse_run_control_request_payload(_request_payload())
    with sqlite3.connect(db_path) as connection:
        connection.row_factory = sqlite3.Row
        WorkbenchRunControlQueueRepository(connection).enqueue(request, status="validated")


def test_run_control_execution_result_store_initializes_explicit_schema(tmp_path) -> None:
    db_path = tmp_path / "metadata.sqlite"

    payload = initialize_run_control_execution_result_store(db_path).to_dict()

    assert payload["status"] == "ok"
    assert payload["mode"] == "run_control_execution_result_store_init"
    assert payload["writes_performed"] is True
    assert payload["execution_performed"] is False
    assert payload["adapter_started"] is False
    with sqlite3.connect(db_path) as connection:
        table_count = connection.execute(
            """
            SELECT COUNT(*)
            FROM sqlite_master
            WHERE type = 'table' AND name = 'run_control_execution_results'
            """
        ).fetchone()[0]
    assert table_count == 1


def test_run_control_execution_result_store_persists_validated_result_without_start(tmp_path) -> None:
    db_path = tmp_path / "metadata.sqlite"
    build_seeded_metadata_repository(db_path)
    _enqueue_validated(db_path)
    result_path = _write_adapter_result(tmp_path)

    payload = persist_run_control_adapter_result(
        "baseline-python-tests",
        result_path,
        db_path=db_path,
        persisted_at="2026-07-15T00:00:00Z",
        explicit_persistence_release=True,
    ).to_dict()
    show_payload = get_run_control_execution_result(
        "baseline-python-tests",
        db_path=db_path,
    ).to_dict()
    queue_payload = get_run_control_queue_entry("baseline-python-tests", db_path=db_path).to_dict()

    assert payload["status"] == "ok"
    assert payload["mode"] == "run_control_execution_result_store_persist"
    assert payload["writes_performed"] is True
    assert payload["execution_performed"] is False
    assert payload["adapter_started"] is False
    assert payload["simulation_performed"] is False
    assert payload["record"]["queue_id"] == "baseline-python-tests"
    assert payload["record"]["result_status"] == "ok"
    assert payload["record"]["summary_mode"] == "explicit_multi_period_execution_summary"
    assert payload["record"]["adapter_execution_performed"] is True
    assert payload["record"]["simulation_performed"] is False
    assert show_payload["record"]["persisted_at"] == "2026-07-15T00:00:00Z"
    assert show_payload["writes_performed"] is False
    assert show_payload["execution_performed"] is False
    assert queue_payload["entry"]["status"] == "result_persisted"
    assert queue_payload["entry"]["execution_performed"] is False
    assert RunControlExecutionResultRecord is not None
    assert RunControlExecutionResultStoreResult is not None


def test_run_control_execution_result_endpoint_shows_persisted_result_readonly(tmp_path) -> None:
    db_path = tmp_path / "metadata.sqlite"
    repository = build_seeded_metadata_repository(db_path)
    _enqueue_validated(db_path)
    result_path = _write_adapter_result(tmp_path)
    persist_run_control_adapter_result(
        "baseline-python-tests",
        result_path,
        db_path=db_path,
        persisted_at="2026-07-15T00:00:00Z",
        explicit_persistence_release=True,
    )
    app = create_app(frontend_dist=tmp_path, metadata_repository=repository)
    client = TestClient(app)

    response = client.get("/api/run-control/execution-result/baseline-python-tests")

    assert response.status_code == 200
    payload = response.json()
    assert payload["mode"] == "run_control_execution_result_store_show"
    assert payload["record"]["queue_id"] == "baseline-python-tests"
    assert payload["record"]["summary_mode"] == "explicit_multi_period_execution_summary"
    assert payload["record"]["adapter_execution_performed"] is True
    assert payload["writes_performed"] is False
    assert payload["execution_performed"] is False
    assert payload["adapter_started"] is False
    assert payload["simulation_performed"] is False
    assert payload["historical_full_equality_claimed"] is False


def test_run_control_execution_result_endpoint_reports_missing_result_without_writing(tmp_path) -> None:
    db_path = tmp_path / "metadata.sqlite"
    repository = build_seeded_metadata_repository(db_path)
    app = create_app(frontend_dist=tmp_path, metadata_repository=repository)
    client = TestClient(app)

    response = client.get("/api/run-control/execution-result/missing-queue")

    assert response.status_code == 404
    payload = response.json()
    assert payload["mode"] == "run_control_execution_result_store_show"
    assert payload["writes_performed"] is False
    assert payload["execution_performed"] is False
    assert payload["adapter_started"] is False
    assert payload["simulation_performed"] is False
    assert "missing-queue" in payload["message"]


def test_run_control_execution_result_store_requires_explicit_release(tmp_path) -> None:
    db_path = tmp_path / "metadata.sqlite"
    build_seeded_metadata_repository(db_path)
    _enqueue_validated(db_path)
    result_path = _write_adapter_result(tmp_path)

    with pytest.raises(MetadataImportError, match="explicit persistence release is required"):
        persist_run_control_adapter_result(
            "baseline-python-tests",
            result_path,
            db_path=db_path,
            persisted_at="2026-07-15T00:00:00Z",
        )

    assert not get_run_control_queue_entry("baseline-python-tests", db_path=db_path).entry.execution_performed


def test_run_control_execution_result_store_rejects_planned_queue_entry(tmp_path) -> None:
    db_path = tmp_path / "metadata.sqlite"
    build_seeded_metadata_repository(db_path)
    request = parse_run_control_request_payload(_request_payload())
    with sqlite3.connect(db_path) as connection:
        connection.row_factory = sqlite3.Row
        WorkbenchRunControlQueueRepository(connection).enqueue(request, status="planned")
    result_path = _write_adapter_result(tmp_path)

    with pytest.raises(MetadataImportError, match="requires queue status validated"):
        persist_run_control_adapter_result(
            "baseline-python-tests",
            result_path,
            db_path=db_path,
            persisted_at="2026-07-15T00:00:00Z",
            explicit_persistence_release=True,
        )


def test_run_control_execution_result_store_rejects_invalid_result_without_writing(tmp_path) -> None:
    db_path = tmp_path / "metadata.sqlite"
    build_seeded_metadata_repository(db_path)
    _enqueue_validated(db_path)
    payload = _adapter_result_payload()
    payload["simulation_performed"] = True
    result_path = _write_adapter_result(tmp_path, payload)

    with pytest.raises(MetadataImportError, match="adapter result does not match"):
        persist_run_control_adapter_result(
            "baseline-python-tests",
            result_path,
            db_path=db_path,
            persisted_at="2026-07-15T00:00:00Z",
            explicit_persistence_release=True,
        )

    with pytest.raises(MetadataImportError, match="not readable or initialized"):
        get_run_control_execution_result("baseline-python-tests", db_path=db_path)


def test_run_control_execution_result_store_cli_persists_and_shows(tmp_path, capsys) -> None:
    db_path = tmp_path / "metadata.sqlite"
    build_seeded_metadata_repository(db_path)
    _enqueue_validated(db_path)
    result_path = _write_adapter_result(tmp_path)

    assert main(["init", "--db", str(db_path)]) == 0
    init_payload = json.loads(capsys.readouterr().out)
    assert init_payload["mode"] == "run_control_execution_result_store_init"

    assert (
        main(
            [
                "persist",
                "--db",
                str(db_path),
                "--queue-id",
                "baseline-python-tests",
                "--adapter-result",
                str(result_path),
                "--persisted-at",
                "2026-07-15T00:00:00Z",
                "--explicit-persistence-release",
            ]
        )
        == 0
    )
    persist_payload = json.loads(capsys.readouterr().out)
    assert persist_payload["mode"] == "run_control_execution_result_store_persist"
    assert persist_payload["adapter_started"] is False

    assert main(["show", "--db", str(db_path), "--queue-id", "baseline-python-tests"]) == 0
    show_payload = json.loads(capsys.readouterr().out)
    assert show_payload["mode"] == "run_control_execution_result_store_show"
    assert show_payload["record"]["queue_id"] == "baseline-python-tests"
    assert show_payload["writes_performed"] is False


def test_run_control_execution_result_store_module_entrypoint_reports_missing_release(tmp_path) -> None:
    db_path = tmp_path / "metadata.sqlite"
    build_seeded_metadata_repository(db_path)
    _enqueue_validated(db_path)
    result_path = _write_adapter_result(tmp_path)
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path(__file__).resolve().parent.parent / "python_port")
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "ims.api.run_control_execution_result_store",
            "persist",
            "--db",
            str(db_path),
            "--queue-id",
            "baseline-python-tests",
            "--adapter-result",
            str(result_path),
            "--persisted-at",
            "2026-07-15T00:00:00Z",
        ],
        capture_output=True,
        check=False,
        env=env,
        text=True,
    )

    assert completed.returncode != 0
    assert "explicit-persistence-release" in completed.stderr
    assert completed.stdout == ""
