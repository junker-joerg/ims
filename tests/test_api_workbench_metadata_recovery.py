import json
import sqlite3
from pathlib import Path

import pytest

from ims.api.metadata_import import MetadataImportError
from ims.api.metadata_repository import build_seeded_metadata_repository, connect_metadata_db
from ims.api.run_control_adapter_start import RUN_CONTROL_EXECUTION_ATTEMPT_SCHEMA
from ims.api.run_control_execution_result_store import (
    RunControlExecutionResultRecord,
    upsert_run_control_execution_result_record,
)
from ims.api.run_control_queue import WorkbenchRunControlQueueRepository
from ims.api.run_control_requests import WorkbenchRunControlRequest
from ims.api.workbench_metadata_recovery import (
    WorkbenchMetadataRecoveryResult,
    WorkbenchMetadataRecoveryState,
    backup_workbench_metadata,
    inspect_workbench_metadata_recovery,
    main,
    restore_workbench_metadata,
    verify_workbench_metadata_recovery,
)


QUEUE_ID = "baseline-python-tests"


def test_metadata_recovery_inspects_validated_result_state_readonly(tmp_path):
    db_path = tmp_path / "metadata.sqlite"
    _seed_validated_result_state(db_path)

    payload = inspect_workbench_metadata_recovery(db_path, queue_id=QUEUE_ID).to_dict()

    assert payload["status"] == "ok"
    assert payload["operation"] == "inspect"
    assert payload["recovery_contract_version"] == "pr68-v1"
    assert payload["source_state"]["validated_result_state"] is True
    assert payload["source_state"]["queue_status"] == "result_persisted"
    assert payload["source_state"]["latest_attempt_status"] == "result_persisted"
    assert payload["source_state"]["result_status"] == "ok"
    assert payload["source_state"]["table_row_counts"]["run_control_execution_results"] == 1
    assert len(payload["source_state"]["critical_digest"]) == 64
    assert payload["target_state"] is None
    assert payload["output_created"] is False
    assert payload["writes_performed"] is False
    assert payload["execution_performed"] is False
    assert payload["adapter_started"] is False
    assert payload["simulation_performed"] is False
    assert payload["historical_full_equality_claimed"] is False


def test_metadata_recovery_backup_restore_and_verify_preserve_all_tables(tmp_path):
    source_db = tmp_path / "metadata.sqlite"
    backup_db = tmp_path / "metadata.backup.sqlite"
    restored_db = tmp_path / "metadata.restored.sqlite"
    _seed_validated_result_state(source_db)

    backup = backup_workbench_metadata(source_db, backup_db, queue_id=QUEUE_ID).to_dict()
    restore = restore_workbench_metadata(backup_db, restored_db, queue_id=QUEUE_ID).to_dict()
    verify = verify_workbench_metadata_recovery(source_db, restored_db, queue_id=QUEUE_ID).to_dict()

    assert backup["operation"] == "backup"
    assert backup["states_match"] is True
    assert backup["output_created"] is True
    assert backup["writes_performed"] is True
    assert restore["operation"] == "restore"
    assert restore["states_match"] is True
    assert restore["output_created"] is True
    assert verify["operation"] == "verify"
    assert verify["states_match"] is True
    assert verify["update_probe_ready"] is True
    assert verify["rollback_probe_ready"] is True
    assert verify["writes_performed"] is False
    assert source_db.is_file()
    assert backup_db.is_file()
    assert restored_db.is_file()
    assert backup["source_state"]["critical_digest"] == restore["target_state"]["critical_digest"]
    assert restore["target_state"]["table_row_counts"] == {
        "scenarios": 2,
        "runs": 2,
        "run_control_queue": 1,
        "run_control_execution_attempts": 1,
        "run_control_execution_results": 1,
    }


def test_metadata_recovery_backup_includes_committed_live_wal_state(tmp_path):
    source_db = tmp_path / "metadata.sqlite"
    backup_db = tmp_path / "metadata.backup.sqlite"
    _seed_validated_result_state(source_db)
    writer = sqlite3.connect(source_db)
    try:
        assert writer.execute("PRAGMA journal_mode=WAL").fetchone()[0] == "wal"
        writer.execute("PRAGMA wal_autocheckpoint=0")
        writer.execute("UPDATE scenarios SET notes = ? WHERE id = ?", ("committed in WAL", "agrsich-reference-window"))
        writer.commit()
        assert Path(f"{source_db}-wal").is_file()
        assert Path(f"{source_db}-shm").is_file()

        payload = backup_workbench_metadata(source_db, backup_db, queue_id=QUEUE_ID).to_dict()
    finally:
        writer.close()

    assert payload["states_match"] is True
    with sqlite3.connect(backup_db) as connection:
        notes = connection.execute(
            "SELECT notes FROM scenarios WHERE id = ?",
            ("agrsich-reference-window",),
        ).fetchone()[0]
    assert notes == "committed in WAL"


def test_metadata_recovery_blocks_incomplete_result_before_writing(tmp_path):
    source_db = tmp_path / "metadata.sqlite"
    backup_db = tmp_path / "metadata.backup.sqlite"
    _seed_validated_result_state(source_db)
    with sqlite3.connect(source_db) as connection:
        connection.execute(
            "UPDATE run_control_queue SET status = ?, execution_performed = 0 WHERE queue_id = ?",
            ("validated", QUEUE_ID),
        )

    with pytest.raises(MetadataImportError, match="queue status result_persisted"):
        backup_workbench_metadata(source_db, backup_db, queue_id=QUEUE_ID)

    assert not backup_db.exists()
    assert not list(tmp_path.glob(".metadata.backup.sqlite.*.tmp"))


def test_metadata_recovery_blocks_simulation_marker_before_writing(tmp_path):
    source_db = tmp_path / "metadata.sqlite"
    backup_db = tmp_path / "metadata.backup.sqlite"
    _seed_validated_result_state(source_db)
    with sqlite3.connect(source_db) as connection:
        connection.execute(
            "UPDATE run_control_execution_results SET simulation_performed = 1 WHERE queue_id = ?",
            (QUEUE_ID,),
        )

    with pytest.raises(MetadataImportError, match="result simulation_performed=true"):
        backup_workbench_metadata(source_db, backup_db, queue_id=QUEUE_ID)

    assert not backup_db.exists()
    assert not list(tmp_path.glob(".metadata.backup.sqlite.*.tmp"))


def test_metadata_recovery_refuses_existing_output(tmp_path):
    source_db = tmp_path / "metadata.sqlite"
    out_path = tmp_path / "existing.sqlite"
    _seed_validated_result_state(source_db)
    out_path.write_text("preserve me", encoding="utf-8")

    with pytest.raises(MetadataImportError, match="output already exists"):
        backup_workbench_metadata(source_db, out_path, queue_id=QUEUE_ID)

    assert out_path.read_text(encoding="utf-8") == "preserve me"


def test_metadata_recovery_verify_detects_changed_candidate(tmp_path):
    source_db = tmp_path / "metadata.sqlite"
    candidate_db = tmp_path / "candidate.sqlite"
    _seed_validated_result_state(source_db)
    backup_workbench_metadata(source_db, candidate_db, queue_id=QUEUE_ID)
    with sqlite3.connect(candidate_db) as connection:
        connection.execute(
            "UPDATE scenarios SET notes = ? WHERE id = ?",
            ("changed candidate", "agrsich-reference-window"),
        )

    with pytest.raises(MetadataImportError, match="states do not match"):
        verify_workbench_metadata_recovery(source_db, candidate_db, queue_id=QUEUE_ID)


def test_metadata_recovery_cli_backup_prints_stable_json(tmp_path, capsys):
    source_db = tmp_path / "metadata.sqlite"
    backup_db = tmp_path / "metadata.backup.sqlite"
    _seed_validated_result_state(source_db)

    exit_code = main(
        [
            "backup",
            "--source-db",
            str(source_db),
            "--out",
            str(backup_db),
            "--queue-id",
            QUEUE_ID,
        ]
    )
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["status"] == "ok"
    assert payload["mode"] == "workbench_metadata_recovery"
    assert payload["operation"] == "backup"
    assert payload["output_created"] is True
    assert payload["writes_performed"] is True
    assert payload["execution_performed"] is False
    assert payload["simulation_performed"] is False


def test_metadata_recovery_cli_missing_parent_reports_no_write(tmp_path, capsys):
    source_db = tmp_path / "metadata.sqlite"
    out_path = tmp_path / "missing" / "metadata.backup.sqlite"
    _seed_validated_result_state(source_db)

    exit_code = main(
        [
            "backup",
            "--source-db",
            str(source_db),
            "--out",
            str(out_path),
            "--queue-id",
            QUEUE_ID,
        ]
    )
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 2
    assert payload["status"] == "error"
    assert "output parent does not exist" in payload["message"]
    assert payload["output_created"] is False
    assert payload["writes_performed"] is False
    assert payload["execution_performed"] is False
    assert payload["simulation_performed"] is False
    assert not out_path.parent.exists()


def test_metadata_recovery_public_types_importable():
    assert WorkbenchMetadataRecoveryResult is not None
    assert WorkbenchMetadataRecoveryState is not None


def _seed_validated_result_state(db_path: Path) -> None:
    build_seeded_metadata_repository(db_path)
    connection = connect_metadata_db(db_path)
    try:
        WorkbenchRunControlQueueRepository(connection).enqueue(
            WorkbenchRunControlRequest(
                run_id=QUEUE_ID,
                scenario_id="agrsich-reference-window",
                requested_by="local-user",
                created_at="2026-08-25T10:00:00Z",
                metadata_db=str(db_path.resolve()),
            ),
            status="result_persisted",
        )
        connection.execute(
            "UPDATE run_control_queue SET execution_performed = 1 WHERE queue_id = ?",
            (QUEUE_ID,),
        )
        connection.execute(RUN_CONTROL_EXECUTION_ATTEMPT_SCHEMA)
        connection.execute(
            """
            INSERT INTO run_control_execution_attempts (
                attempt_id, queue_id, idempotency_key, request_fingerprint, status,
                released_by, released_at, release_reason, started_at, completed_at,
                failure_message, adapter_started, result_persisted, simulation_performed
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, NULL, 1, 1, 0)
            """,
            (
                "adapter-recovery-001",
                QUEUE_ID,
                "workbench-recovery-001",
                "recovery-fingerprint-001",
                "result_persisted",
                "local-reviewer",
                "2026-08-25T10:01:00Z",
                "PR68 Recovery-Probe",
                "2026-08-25T10:01:01Z",
                "2026-08-25T10:01:02Z",
            ),
        )
        upsert_run_control_execution_result_record(
            connection,
            RunControlExecutionResultRecord(
                queue_id=QUEUE_ID,
                run_id=QUEUE_ID,
                scenario_id="agrsich-reference-window",
                adapter_mode="explicit_multi_period_fixture_adapter",
                fixture_kind="explicit_multi_period_fixture",
                fixture_path="tests/fixtures/replay_vu14_period_plan.json",
                summary_mode="explicit_multi_period_execution_summary",
                result_status="ok",
                persisted_at="2026-08-25T10:01:02Z",
                result_payload={"status": "ok", "simulation_performed": False},
                summary_payload={"mode": "explicit_multi_period_execution_summary"},
                validation_payload={"status": "ok"},
                adapter_execution_performed=True,
                simulation_performed=False,
                automatic_historical_rule_selection_performed=False,
                historical_full_equality_claimed=False,
            ),
        )
        connection.commit()
    finally:
        connection.close()
