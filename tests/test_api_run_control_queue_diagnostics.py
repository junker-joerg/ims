import json
import os
import sqlite3
import subprocess
import sys
from pathlib import Path

from ims.api.metadata_repository import build_seeded_metadata_repository
from ims.api.run_control_queue import enqueue_run_control_request, initialize_run_control_queue
from ims.api.run_control_queue_diagnostics import (
    RunControlQueueDiagnosticIssue,
    RunControlQueueDiagnosticsResult,
    diagnose_run_control_queue,
    main,
)


def _valid_request_payload() -> dict[str, object]:
    return {
        "schema_version": "ims.workbench.metadata.v1",
        "run_id": "baseline-python-tests",
        "scenario_id": "agrsich-reference-window",
        "metadata_db": ".ims_workbench/metadata.sqlite",
        "requested_by": "local-user",
        "created_at": "2026-06-15T00:00:00Z",
        "execution_enabled": False,
    }


def _write_request(tmp_path: Path, payload: dict[str, object] | None = None) -> Path:
    request_path = tmp_path / "run_control_request.json"
    request_path.write_text(json.dumps(payload or _valid_request_payload()), encoding="utf-8")
    return request_path


def test_run_control_queue_diagnostics_accepts_valid_queue(tmp_path):
    db_path = tmp_path / "metadata.sqlite"
    build_seeded_metadata_repository(db_path)
    enqueue_run_control_request(_write_request(tmp_path), db_path=db_path)

    payload = diagnose_run_control_queue(db_path).to_dict()

    assert payload["status"] == "ok"
    assert payload["mode"] == "run_control_queue_diagnostics"
    assert payload["schema_version"] == "ims.workbench.metadata.v1"
    assert payload["queue_initialized"] is True
    assert payload["queue_readable"] is True
    assert payload["queue_count"] == 1
    assert payload["queue_ids"] == ["baseline-python-tests"]
    assert payload["missing_scenario_queue_ids"] == []
    assert payload["execution_enabled_queue_ids"] == []
    assert payload["execution_performed_queue_ids"] == []
    assert payload["unsupported_status_queue_ids"] == []
    assert payload["writes_performed"] is False
    assert payload["execution_performed"] is False
    assert payload["issues"] == []


def test_run_control_queue_diagnostics_reports_uninitialized_queue(tmp_path):
    db_path = tmp_path / "metadata.sqlite"
    build_seeded_metadata_repository(db_path)

    payload = diagnose_run_control_queue(db_path).to_dict()

    assert payload["status"] == "ok"
    assert payload["queue_initialized"] is False
    assert payload["queue_readable"] is False
    assert payload["queue_count"] == 0
    assert payload["issues"][0]["code"] == "run_control_queue_not_initialized"
    assert payload["issues"][0]["severity"] == "info"
    assert payload["writes_performed"] is False


def test_run_control_queue_diagnostics_reports_missing_scenario_reference(tmp_path):
    db_path = tmp_path / "metadata.sqlite"
    build_seeded_metadata_repository(db_path)
    payload = _valid_request_payload()
    payload["run_id"] = "queued-missing-scenario"
    payload["scenario_id"] = "missing-scenario"
    enqueue_run_control_request(_write_request(tmp_path, payload), db_path=db_path)

    result = diagnose_run_control_queue(db_path).to_dict()

    assert result["status"] == "warning"
    assert result["missing_scenario_queue_ids"] == ["queued-missing-scenario"]
    assert result["issues"][0]["code"] == "run_control_queue_missing_scenario"
    assert result["execution_enabled_queue_ids"] == []
    assert result["execution_performed"] is False


def test_run_control_queue_diagnostics_reports_execution_and_status_boundaries(tmp_path):
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
                "running",
                1,
                1,
            ),
        )

    payload = diagnose_run_control_queue(db_path).to_dict()
    issue_codes = {issue["code"] for issue in payload["issues"]}

    assert payload["status"] == "error"
    assert payload["execution_enabled_queue_ids"] == ["bad-execution"]
    assert payload["execution_performed_queue_ids"] == ["bad-execution"]
    assert payload["unsupported_status_queue_ids"] == ["bad-execution"]
    assert "run_control_queue_execution_enabled" in issue_codes
    assert "run_control_queue_execution_performed" in issue_codes
    assert "run_control_queue_unsupported_status" in issue_codes


def test_run_control_queue_diagnostics_cli_prints_stable_json(tmp_path, capsys):
    db_path = tmp_path / "metadata.sqlite"
    build_seeded_metadata_repository(db_path)
    enqueue_run_control_request(_write_request(tmp_path), db_path=db_path)

    exit_code = main(["--db", str(db_path)])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["mode"] == "run_control_queue_diagnostics"
    assert payload["queue_ids"] == ["baseline-python-tests"]
    assert payload["writes_performed"] is False
    assert payload["execution_performed"] is False


def test_run_control_queue_diagnostics_cli_reports_missing_db(tmp_path, capsys):
    db_path = tmp_path / "missing.sqlite"

    exit_code = main(["--db", str(db_path)])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 2
    assert payload["status"] == "error"
    assert payload["mode"] == "run_control_queue_diagnostics"
    assert payload["writes_performed"] is False
    assert payload["execution_performed"] is False
    assert not db_path.exists()


def test_run_control_queue_diagnostics_module_entrypoint_prints_json(tmp_path):
    db_path = tmp_path / "metadata.sqlite"
    build_seeded_metadata_repository(db_path)
    enqueue_run_control_request(_write_request(tmp_path), db_path=db_path)
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path(__file__).resolve().parent.parent / "python_port")

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "ims.api.run_control_queue_diagnostics",
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
    assert payload["mode"] == "run_control_queue_diagnostics"
    assert payload["queue_count"] == 1


def test_run_control_queue_diagnostics_public_types_importable():
    assert RunControlQueueDiagnosticIssue is not None
    assert RunControlQueueDiagnosticsResult is not None
