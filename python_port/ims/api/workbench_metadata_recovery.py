from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
import tempfile
from dataclasses import dataclass, replace as dataclass_replace
from pathlib import Path
from typing import Sequence

from ims.api.metadata import METADATA_SCHEMA_VERSION
from ims.api.metadata_import import MetadataImportError
from ims.api.sqlite_readonly import readonly_sqlite_uri


RECOVERY_CONTRACT_VERSION = "pr68-v1"
RECOVERY_TABLE_KEYS = {
    "scenarios": "id",
    "runs": "id",
    "run_control_queue": "queue_id",
    "run_control_execution_attempts": "attempt_id",
    "run_control_execution_results": "queue_id",
}


@dataclass(frozen=True)
class WorkbenchMetadataRecoveryState:
    db_path: str
    queue_id: str
    run_id: str
    scenario_id: str
    queue_status: str
    queue_execution_performed: bool
    attempt_count: int
    latest_attempt_status: str
    result_status: str
    persisted_at: str
    table_row_counts: dict[str, int]
    critical_digest: str
    validated_result_state: bool = True

    def to_dict(self) -> dict[str, object]:
        return {
            "db_path": self.db_path,
            "queue_id": self.queue_id,
            "run_id": self.run_id,
            "scenario_id": self.scenario_id,
            "queue_status": self.queue_status,
            "queue_execution_performed": self.queue_execution_performed,
            "attempt_count": self.attempt_count,
            "latest_attempt_status": self.latest_attempt_status,
            "result_status": self.result_status,
            "persisted_at": self.persisted_at,
            "table_row_counts": dict(self.table_row_counts),
            "critical_digest": self.critical_digest,
            "validated_result_state": self.validated_result_state,
        }


@dataclass(frozen=True)
class WorkbenchMetadataRecoveryResult:
    operation: str
    queue_id: str
    source_db: str
    target_db: str | None
    source_state: WorkbenchMetadataRecoveryState
    target_state: WorkbenchMetadataRecoveryState | None
    states_match: bool
    output_created: bool
    writes_performed: bool
    mode: str = "workbench_metadata_recovery"

    def to_dict(self) -> dict[str, object]:
        return {
            "status": "ok",
            "mode": self.mode,
            "schema_version": METADATA_SCHEMA_VERSION,
            "recovery_contract_version": RECOVERY_CONTRACT_VERSION,
            "operation": self.operation,
            "queue_id": self.queue_id,
            "source_db": self.source_db,
            "target_db": self.target_db,
            "source_state": self.source_state.to_dict(),
            "target_state": self.target_state.to_dict() if self.target_state is not None else None,
            "states_match": self.states_match,
            "output_created": self.output_created,
            "update_probe_ready": self.states_match,
            "rollback_probe_ready": self.states_match,
            "writes_performed": self.writes_performed,
            "execution_performed": False,
            "adapter_started": False,
            "simulation_performed": False,
            "automatic_historical_rule_selection_performed": False,
            "historical_full_equality_claimed": False,
        }


def inspect_workbench_metadata_recovery(
    db_path: Path | str,
    *,
    queue_id: str,
) -> WorkbenchMetadataRecoveryResult:
    state = _inspect_validated_state(db_path, queue_id=queue_id)
    return WorkbenchMetadataRecoveryResult(
        operation="inspect",
        queue_id=queue_id,
        source_db=state.db_path,
        target_db=None,
        source_state=state,
        target_state=None,
        states_match=True,
        output_created=False,
        writes_performed=False,
    )


def backup_workbench_metadata(
    source_db: Path | str,
    out_path: Path | str,
    *,
    queue_id: str,
) -> WorkbenchMetadataRecoveryResult:
    return _copy_and_verify(
        operation="backup",
        source_db=source_db,
        out_path=out_path,
        queue_id=queue_id,
    )


def restore_workbench_metadata(
    backup_db: Path | str,
    out_path: Path | str,
    *,
    queue_id: str,
) -> WorkbenchMetadataRecoveryResult:
    return _copy_and_verify(
        operation="restore",
        source_db=backup_db,
        out_path=out_path,
        queue_id=queue_id,
    )


def verify_workbench_metadata_recovery(
    source_db: Path | str,
    candidate_db: Path | str,
    *,
    queue_id: str,
) -> WorkbenchMetadataRecoveryResult:
    source_state = _inspect_validated_state(source_db, queue_id=queue_id)
    candidate_state = _inspect_validated_state(candidate_db, queue_id=queue_id)
    states_match = source_state.critical_digest == candidate_state.critical_digest
    if not states_match:
        raise MetadataImportError("workbench metadata recovery states do not match")
    return WorkbenchMetadataRecoveryResult(
        operation="verify",
        queue_id=queue_id,
        source_db=source_state.db_path,
        target_db=candidate_state.db_path,
        source_state=source_state,
        target_state=candidate_state,
        states_match=True,
        output_created=False,
        writes_performed=False,
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "inspect":
            result = inspect_workbench_metadata_recovery(args.db, queue_id=args.queue_id)
        elif args.command == "backup":
            result = backup_workbench_metadata(args.source_db, args.out, queue_id=args.queue_id)
        elif args.command == "restore":
            result = restore_workbench_metadata(args.backup_db, args.out, queue_id=args.queue_id)
        elif args.command == "verify":
            result = verify_workbench_metadata_recovery(
                args.source_db,
                args.candidate_db,
                queue_id=args.queue_id,
            )
        else:  # pragma: no cover - argparse prevents this branch
            raise MetadataImportError(f"unsupported recovery command: {args.command}")
    except MetadataImportError as exc:
        _print_json(
            {
                "status": "error",
                "mode": "workbench_metadata_recovery",
                "operation": args.command,
                "message": str(exc),
                "issues": [str(exc)],
                "output_created": False,
                "update_probe_ready": False,
                "rollback_probe_ready": False,
                "writes_performed": False,
                "execution_performed": False,
                "adapter_started": False,
                "simulation_performed": False,
                "automatic_historical_rule_selection_performed": False,
                "historical_full_equality_claimed": False,
            }
        )
        return 2
    _print_json(result.to_dict())
    return 0


def _copy_and_verify(
    *,
    operation: str,
    source_db: Path | str,
    out_path: Path | str,
    queue_id: str,
) -> WorkbenchMetadataRecoveryResult:
    source_state = _inspect_validated_state(source_db, queue_id=queue_id)
    resolved_source = Path(source_state.db_path)
    resolved_out = Path(out_path).expanduser().resolve()
    _validate_output_path(resolved_source, resolved_out)

    temporary_path = _temporary_target(resolved_out)
    try:
        _sqlite_backup(resolved_source, temporary_path, description=f"workbench metadata {operation}")
        temporary_state = _inspect_validated_state(temporary_path, queue_id=queue_id)
        if source_state.critical_digest != temporary_state.critical_digest:
            raise MetadataImportError(f"workbench metadata {operation} state does not match source")
        temporary_path.replace(resolved_out)
        target_state = dataclass_replace(temporary_state, db_path=str(resolved_out))
    except Exception:
        temporary_path.unlink(missing_ok=True)
        raise

    return WorkbenchMetadataRecoveryResult(
        operation=operation,
        queue_id=queue_id,
        source_db=source_state.db_path,
        target_db=target_state.db_path,
        source_state=source_state,
        target_state=target_state,
        states_match=source_state.critical_digest == target_state.critical_digest,
        output_created=True,
        writes_performed=True,
    )


def _inspect_validated_state(
    db_path: Path | str,
    *,
    queue_id: str,
) -> WorkbenchMetadataRecoveryState:
    if not queue_id.strip():
        raise MetadataImportError("workbench metadata recovery queue id must not be empty")
    resolved_path = Path(db_path).expanduser().resolve()
    if not resolved_path.is_file():
        raise MetadataImportError(f"workbench metadata recovery database does not exist: {resolved_path}")

    connection = _connect_readonly(resolved_path)
    try:
        _require_tables(connection)
        queue_row = connection.execute(
            "SELECT queue_id, run_id, scenario_id, status, execution_enabled, execution_performed "
            "FROM run_control_queue WHERE queue_id = ?",
            (queue_id,),
        ).fetchone()
        if queue_row is None:
            raise MetadataImportError(f"workbench metadata recovery queue entry not found: {queue_id}")
        attempt_rows = connection.execute(
            "SELECT attempt_id, status, completed_at, adapter_started, result_persisted, simulation_performed "
            "FROM run_control_execution_attempts WHERE queue_id = ? "
            "ORDER BY started_at DESC, attempt_id DESC",
            (queue_id,),
        ).fetchall()
        result_row = connection.execute(
            "SELECT run_id, scenario_id, result_status, persisted_at, result_payload_json, "
            "summary_payload_json, validation_payload_json, adapter_execution_performed, "
            "simulation_performed, automatic_historical_rule_selection_performed, "
            "historical_full_equality_claimed FROM run_control_execution_results WHERE queue_id = ?",
            (queue_id,),
        ).fetchone()
        _validate_result_state(queue_row, attempt_rows, result_row)
        table_row_counts, digest = _critical_digest(connection)
    except sqlite3.DatabaseError as exc:
        raise MetadataImportError(f"workbench metadata recovery database is not readable: {exc}") from exc
    finally:
        connection.close()

    latest_attempt = attempt_rows[0]
    assert result_row is not None
    return WorkbenchMetadataRecoveryState(
        db_path=str(resolved_path),
        queue_id=str(queue_row["queue_id"]),
        run_id=str(queue_row["run_id"]),
        scenario_id=str(queue_row["scenario_id"]),
        queue_status=str(queue_row["status"]),
        queue_execution_performed=bool(queue_row["execution_performed"]),
        attempt_count=len(attempt_rows),
        latest_attempt_status=str(latest_attempt["status"]),
        result_status=str(result_row["result_status"]),
        persisted_at=str(result_row["persisted_at"]),
        table_row_counts=table_row_counts,
        critical_digest=digest,
    )


def _validate_result_state(
    queue_row: sqlite3.Row,
    attempt_rows: Sequence[sqlite3.Row],
    result_row: sqlite3.Row | None,
) -> None:
    if queue_row["status"] != "result_persisted":
        raise MetadataImportError("workbench metadata recovery requires queue status result_persisted")
    if bool(queue_row["execution_enabled"]):
        raise MetadataImportError("workbench metadata recovery refuses execution_enabled=true")
    if not bool(queue_row["execution_performed"]):
        raise MetadataImportError("workbench metadata recovery requires completed queue execution audit")
    if not attempt_rows:
        raise MetadataImportError("workbench metadata recovery requires a persisted execution attempt")
    latest_attempt = attempt_rows[0]
    if (
        latest_attempt["status"] != "result_persisted"
        or latest_attempt["completed_at"] is None
        or not bool(latest_attempt["adapter_started"])
        or not bool(latest_attempt["result_persisted"])
    ):
        raise MetadataImportError("workbench metadata recovery execution attempt is not complete")
    if bool(latest_attempt["simulation_performed"]):
        raise MetadataImportError("workbench metadata recovery refuses simulation_performed=true")
    if result_row is None:
        raise MetadataImportError("workbench metadata recovery requires a persisted execution result")
    if (
        result_row["run_id"] != queue_row["run_id"]
        or result_row["scenario_id"] != queue_row["scenario_id"]
    ):
        raise MetadataImportError("workbench metadata recovery queue and result identities do not match")
    if result_row["result_status"] != "ok" or not bool(result_row["adapter_execution_performed"]):
        raise MetadataImportError("workbench metadata recovery persisted result is not accepted")
    if bool(result_row["simulation_performed"]):
        raise MetadataImportError("workbench metadata recovery refuses result simulation_performed=true")
    if bool(result_row["automatic_historical_rule_selection_performed"]):
        raise MetadataImportError("workbench metadata recovery refuses automatic historical rule selection")
    if bool(result_row["historical_full_equality_claimed"]):
        raise MetadataImportError("workbench metadata recovery refuses historical full equality claim")
    for field in ("result_payload_json", "summary_payload_json", "validation_payload_json"):
        try:
            payload = json.loads(str(result_row[field]))
        except json.JSONDecodeError as exc:
            raise MetadataImportError(f"workbench metadata recovery result field is invalid JSON: {field}") from exc
        if not isinstance(payload, dict):
            raise MetadataImportError(f"workbench metadata recovery result field must be an object: {field}")


def _critical_digest(connection: sqlite3.Connection) -> tuple[dict[str, int], str]:
    digest = hashlib.sha256()
    row_counts: dict[str, int] = {}
    for table_name, key_name in RECOVERY_TABLE_KEYS.items():
        quoted_table = _quote_identifier(table_name)
        quoted_key = _quote_identifier(key_name)
        columns = [str(row["name"]) for row in connection.execute(f"PRAGMA table_info({quoted_table})")]
        rows = connection.execute(f"SELECT * FROM {quoted_table} ORDER BY {quoted_key}").fetchall()
        row_counts[table_name] = len(rows)
        payload = {
            "table": table_name,
            "columns": columns,
            "rows": [[row[column] for column in columns] for row in rows],
        }
        digest.update(json.dumps(payload, ensure_ascii=True, separators=(",", ":")).encode("utf-8"))
    return row_counts, digest.hexdigest()


def _require_tables(connection: sqlite3.Connection) -> None:
    names = {
        str(row["name"])
        for row in connection.execute("SELECT name FROM sqlite_master WHERE type = 'table'").fetchall()
    }
    missing = sorted(set(RECOVERY_TABLE_KEYS) - names)
    if missing:
        raise MetadataImportError(f"workbench metadata recovery tables are missing: {', '.join(missing)}")


def _connect_readonly(path: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(
        readonly_sqlite_uri(path, description="workbench metadata recovery"),
        uri=True,
        check_same_thread=False,
    )
    connection.row_factory = sqlite3.Row
    return connection


def _sqlite_backup(source_path: Path, target_path: Path, *, description: str) -> None:
    source = _connect_readonly(source_path)
    target = sqlite3.connect(target_path)
    try:
        source.backup(target)
    except sqlite3.DatabaseError as exc:
        raise MetadataImportError(f"{description} failed: {exc}") from exc
    finally:
        target.close()
        source.close()


def _validate_output_path(source_path: Path, out_path: Path) -> None:
    if not out_path.parent.is_dir():
        raise MetadataImportError(f"workbench metadata recovery output parent does not exist: {out_path.parent}")
    if out_path.exists():
        raise MetadataImportError(f"workbench metadata recovery output already exists: {out_path}")
    if source_path == out_path:
        raise MetadataImportError("workbench metadata recovery source and output must differ")


def _temporary_target(out_path: Path) -> Path:
    temporary = tempfile.NamedTemporaryFile(
        prefix=f".{out_path.name}.",
        suffix=".tmp",
        dir=out_path.parent,
        delete=False,
    )
    temporary.close()
    return Path(temporary.name)


def _quote_identifier(identifier: str) -> str:
    return '"' + identifier.replace('"', '""') + '"'


def _print_json(payload: dict[str, object]) -> None:
    print(json.dumps(payload, ensure_ascii=True, sort_keys=True))


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m ims.api.workbench_metadata_recovery",
        description="Prueft explizite Backup-, Restore-, Update- und Rollback-Grenzen lokaler Metadaten.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    inspect_parser = subparsers.add_parser("inspect", help="Validierten Ergebnisstand rein lesend pruefen.")
    inspect_parser.add_argument("--db", required=True, type=Path)
    inspect_parser.add_argument("--queue-id", required=True)

    backup_parser = subparsers.add_parser("backup", help="Explizites SQLite-Backup erzeugen.")
    backup_parser.add_argument("--source-db", required=True, type=Path)
    backup_parser.add_argument("--out", required=True, type=Path)
    backup_parser.add_argument("--queue-id", required=True)

    restore_parser = subparsers.add_parser("restore", help="Explizites SQLite-Backup wiederherstellen.")
    restore_parser.add_argument("--backup-db", required=True, type=Path)
    restore_parser.add_argument("--out", required=True, type=Path)
    restore_parser.add_argument("--queue-id", required=True)

    verify_parser = subparsers.add_parser("verify", help="Quelle und Kandidat rein lesend vergleichen.")
    verify_parser.add_argument("--source-db", required=True, type=Path)
    verify_parser.add_argument("--candidate-db", required=True, type=Path)
    verify_parser.add_argument("--queue-id", required=True)
    return parser


if __name__ == "__main__":
    raise SystemExit(main())
