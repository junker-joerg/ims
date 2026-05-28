import json
import os
import sqlite3
import subprocess
import sys
from pathlib import Path

from ims.api.metadata_repository import SCHEMA_STATEMENTS, build_seeded_metadata_repository
from ims.api.run_control_preflight import (
    WorkbenchRunControlPreflightResult,
    main,
    preflight_run_control,
)


def test_run_control_preflight_reads_seeded_memory_without_execution(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    result = preflight_run_control("baseline-python-tests")
    payload = result.to_dict()

    assert payload["status"] == "ok"
    assert payload["mode"] == "run_control_preflight"
    assert payload["run_id"] == "baseline-python-tests"
    assert payload["scenario_id"] == "agrsich-reference-window"
    assert payload["run_found"] is True
    assert payload["scenario_found"] is True
    assert payload["metadata_source"]["storage_kind"] == "memory"
    assert payload["execution_enabled"] is False
    assert payload["execution_allowed"] is False
    assert payload["writes_performed"] is False
    assert payload["execution_performed"] is False
    assert payload["issues"] == []
    assert not (tmp_path / ".ims_workbench" / "metadata.sqlite").exists()
    assert WorkbenchRunControlPreflightResult is not None


def test_run_control_preflight_reads_explicit_sqlite_file(tmp_path):
    db_path = tmp_path / "metadata.sqlite"
    build_seeded_metadata_repository(db_path)

    payload = preflight_run_control("workbench-shell-preview", db_path).to_dict()

    assert payload["status"] == "ok"
    assert payload["run_id"] == "workbench-shell-preview"
    assert payload["scenario_id"] == "local-workbench-draft"
    assert payload["metadata_source"]["storage_kind"] == "sqlite"
    assert payload["metadata_source"]["path"] == str(db_path.resolve())
    assert payload["execution_allowed"] is False


def test_run_control_preflight_reports_unknown_run():
    payload = preflight_run_control("missing-run").to_dict()

    assert payload["status"] == "error"
    assert payload["run_id"] == "missing-run"
    assert payload["scenario_id"] is None
    assert payload["run_found"] is False
    assert payload["scenario_found"] is False
    assert payload["execution_allowed"] is False
    assert payload["execution_performed"] is False
    assert payload["issues"] == ["run metadata not found: missing-run"]


def test_run_control_preflight_reports_missing_scenario_reference(tmp_path):
    db_path = tmp_path / "metadata.sqlite"
    _create_run_only_db(db_path, scenario_id="missing-scenario", execution_enabled=False)

    payload = preflight_run_control("orphan-run", db_path).to_dict()

    assert payload["status"] == "error"
    assert payload["run_found"] is True
    assert payload["scenario_id"] == "missing-scenario"
    assert payload["scenario_found"] is False
    assert payload["execution_allowed"] is False
    assert payload["issues"] == ["scenario metadata not found for run orphan-run: missing-scenario"]


def test_run_control_preflight_reports_execution_enabled_true(tmp_path):
    db_path = tmp_path / "metadata.sqlite"
    _create_run_only_db(db_path, scenario_id="missing-scenario", execution_enabled=True)

    payload = preflight_run_control("orphan-run", db_path).to_dict()

    assert payload["status"] == "error"
    assert payload["execution_enabled"] is True
    assert payload["execution_allowed"] is False
    assert "run execution remains disabled: orphan-run" in payload["issues"]
    assert "scenario metadata not found for run orphan-run: missing-scenario" in payload["issues"]


def test_run_control_preflight_rejects_missing_explicit_db(tmp_path, capsys):
    db_path = tmp_path / "missing.sqlite"

    exit_code = main(["--run-id", "baseline-python-tests", "--db", str(db_path)])

    output = json.loads(capsys.readouterr().out)
    assert exit_code == 2
    assert output["status"] == "error"
    assert "does not exist" in output["message"]
    assert not db_path.exists()


def test_run_control_preflight_reports_unreadable_explicit_db(tmp_path, capsys):
    db_path = tmp_path / "broken.sqlite"
    db_path.write_text("not sqlite", encoding="utf-8")

    exit_code = main(["--run-id", "baseline-python-tests", "--db", str(db_path)])

    output = json.loads(capsys.readouterr().out)
    assert exit_code == 2
    assert output["status"] == "error"
    assert "not readable" in output["message"]


def test_run_control_preflight_cli_prints_stable_json(capsys):
    exit_code = main(["--run-id", "baseline-python-tests"])

    output = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert output["status"] == "ok"
    assert output["mode"] == "run_control_preflight"
    assert output["run_id"] == "baseline-python-tests"
    assert output["execution_allowed"] is False
    assert output["writes_performed"] is False
    assert output["execution_performed"] is False


def test_run_control_preflight_module_entrypoint_prints_json():
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path(__file__).resolve().parent.parent / "python_port")
    completed = subprocess.run(
        [sys.executable, "-m", "ims.api.run_control_preflight", "--run-id", "baseline-python-tests"],
        capture_output=True,
        check=False,
        env=env,
        text=True,
    )

    output = json.loads(completed.stdout)
    assert completed.returncode == 0
    assert output["status"] == "ok"
    assert output["execution_performed"] is False


def _create_run_only_db(db_path: Path, *, scenario_id: str, execution_enabled: bool) -> None:
    connection = sqlite3.connect(db_path)
    try:
        for statement in SCHEMA_STATEMENTS:
            connection.execute(statement)
        connection.execute(
            """
            INSERT INTO runs (
                id,
                display_name,
                scenario_id,
                status,
                source_kind,
                source_label,
                source_path,
                validation_status,
                validation_scope,
                validation_claim,
                period_window,
                execution_enabled,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "orphan-run",
                "Orphan Run",
                scenario_id,
                "planned",
                "in_memory",
                "Testmetadaten",
                None,
                "planned",
                "Run-Control-Preflight",
                "Keine Simulation.",
                "keine Simulation",
                int(execution_enabled),
                "2026-05-27T00:00:00Z",
            ),
        )
        connection.commit()
    finally:
        connection.close()
