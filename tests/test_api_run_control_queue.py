import json
import os
import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest

from ims.api.metadata_import import MetadataImportError
from ims.api.run_control_queue import (
    RUN_CONTROL_QUEUE_STATUSES,
    WorkbenchRunControlQueueEntry,
    WorkbenchRunControlQueueRepository,
    WorkbenchRunControlQueueResult,
    enqueue_run_control_request,
    get_run_control_queue_entry,
    initialize_run_control_queue,
    list_run_control_queue,
    main,
)
from ims.api.run_control_requests import parse_run_control_request_payload


def _valid_request_payload() -> dict[str, object]:
    return {
        "schema_version": "ims.workbench.metadata.v1",
        "run_id": "baseline-python-tests",
        "scenario_id": "baseline-regression",
        "metadata_db": ".ims_workbench/metadata.sqlite",
        "requested_by": "local-user",
        "created_at": "2026-06-15T00:00:00Z",
        "execution_enabled": False,
    }


def _write_request(tmp_path: Path, payload: dict[str, object] | None = None) -> Path:
    request_path = tmp_path / "run_control_request.json"
    request_path.write_text(json.dumps(payload or _valid_request_payload()), encoding="utf-8")
    return request_path


def test_run_control_queue_initializes_explicit_schema(tmp_path):
    db_path = tmp_path / "metadata.sqlite"

    payload = initialize_run_control_queue(db_path).to_dict()

    assert payload["status"] == "ok"
    assert payload["mode"] == "run_control_queue_init"
    assert payload["writes_performed"] is True
    assert payload["execution_performed"] is False
    with sqlite3.connect(db_path) as connection:
        table_count = connection.execute(
            "SELECT COUNT(*) FROM sqlite_master WHERE type = 'table' AND name = 'run_control_queue'"
        ).fetchone()[0]
    assert table_count == 1


def test_run_control_queue_enqueue_and_list_without_execution(tmp_path):
    db_path = tmp_path / "metadata.sqlite"
    request_path = _write_request(tmp_path)

    enqueue_payload = enqueue_run_control_request(request_path, db_path=db_path).to_dict()
    list_payload = list_run_control_queue(db_path).to_dict()

    assert enqueue_payload["mode"] == "run_control_queue_enqueue"
    assert enqueue_payload["entry"]["queue_id"] == "baseline-python-tests"
    assert enqueue_payload["entry"]["status"] == "planned"
    assert enqueue_payload["entry"]["execution_enabled"] is False
    assert enqueue_payload["writes_performed"] is True
    assert enqueue_payload["execution_performed"] is False
    assert list_payload["mode"] == "run_control_queue_list"
    assert list_payload["entries"][0]["queue_id"] == "baseline-python-tests"
    assert list_payload["writes_performed"] is False
    assert list_payload["execution_performed"] is False


def test_run_control_queue_show_reads_single_entry(tmp_path):
    db_path = tmp_path / "metadata.sqlite"
    request_path = _write_request(tmp_path)
    enqueue_run_control_request(request_path, db_path=db_path)

    payload = get_run_control_queue_entry("baseline-python-tests", db_path=db_path).to_dict()

    assert payload["mode"] == "run_control_queue_show"
    assert payload["entry"]["request"]["scenario_id"] == "baseline-regression"
    assert payload["entry"]["execution_performed"] is False


def test_run_control_queue_rejects_execution_enabled_true(tmp_path):
    db_path = tmp_path / "metadata.sqlite"
    payload = _valid_request_payload()
    payload["execution_enabled"] = True
    request_path = _write_request(tmp_path, payload)

    with pytest.raises(MetadataImportError, match="execution_enabled=true is forbidden"):
        enqueue_run_control_request(request_path, db_path=db_path)

    assert not db_path.exists()


def test_run_control_queue_list_rejects_missing_explicit_db(tmp_path):
    missing_db = tmp_path / "missing.sqlite"

    with pytest.raises(MetadataImportError, match="database does not exist"):
        list_run_control_queue(missing_db)

    assert not missing_db.exists()


def test_run_control_queue_show_reports_missing_entry(tmp_path):
    db_path = tmp_path / "metadata.sqlite"
    initialize_run_control_queue(db_path)

    with pytest.raises(MetadataImportError, match="entry not found"):
        get_run_control_queue_entry("missing-run", db_path=db_path)


def test_run_control_queue_repository_rejects_unknown_status():
    request = parse_run_control_request_payload(_valid_request_payload())
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    repository = WorkbenchRunControlQueueRepository(connection)

    with pytest.raises(MetadataImportError, match="status is not supported"):
        repository.enqueue(request, status="running")

    assert "planned" in RUN_CONTROL_QUEUE_STATUSES
    assert WorkbenchRunControlQueueEntry is not None
    assert WorkbenchRunControlQueueResult is not None


def test_run_control_queue_cli_init_enqueue_list_and_show(tmp_path, capsys):
    db_path = tmp_path / "metadata.sqlite"
    request_path = _write_request(tmp_path)

    assert main(["init", "--db", str(db_path)]) == 0
    init_payload = json.loads(capsys.readouterr().out)
    assert init_payload["mode"] == "run_control_queue_init"

    assert main(["enqueue", str(request_path), "--db", str(db_path)]) == 0
    enqueue_payload = json.loads(capsys.readouterr().out)
    assert enqueue_payload["entry"]["queue_id"] == "baseline-python-tests"
    assert enqueue_payload["writes_performed"] is True

    assert main(["list", "--db", str(db_path)]) == 0
    list_payload = json.loads(capsys.readouterr().out)
    assert list_payload["entries"][0]["queue_id"] == "baseline-python-tests"
    assert list_payload["writes_performed"] is False

    assert main(["show", "baseline-python-tests", "--db", str(db_path)]) == 0
    show_payload = json.loads(capsys.readouterr().out)
    assert show_payload["entry"]["request"]["execution_enabled"] is False


def test_run_control_queue_cli_reports_error_json(tmp_path, capsys):
    db_path = tmp_path / "metadata.sqlite"
    payload = _valid_request_payload()
    payload["execution_enabled"] = True
    request_path = _write_request(tmp_path, payload)

    exit_code = main(["enqueue", str(request_path), "--db", str(db_path)])

    output = json.loads(capsys.readouterr().out)
    assert exit_code == 2
    assert output["status"] == "error"
    assert output["mode"] == "run_control_queue_enqueue"
    assert output["writes_performed"] is False
    assert output["execution_performed"] is False


def test_run_control_queue_module_entrypoint_prints_json(tmp_path):
    db_path = tmp_path / "metadata.sqlite"
    request_path = _write_request(tmp_path)
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path(__file__).resolve().parent.parent / "python_port")
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "ims.api.run_control_queue",
            "enqueue",
            str(request_path),
            "--db",
            str(db_path),
        ],
        capture_output=True,
        check=False,
        env=env,
        text=True,
    )

    payload = json.loads(completed.stdout)
    assert completed.returncode == 0
    assert payload["mode"] == "run_control_queue_enqueue"
    assert payload["execution_performed"] is False
