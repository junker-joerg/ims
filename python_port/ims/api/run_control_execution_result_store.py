from __future__ import annotations

import argparse
import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Sequence

from ims.api.metadata import METADATA_SCHEMA_VERSION
from ims.api.metadata_import import MetadataImportError
from ims.api.metadata_repository import connect_metadata_db
from ims.api.run_control_adapter_result_contract import (
    validate_run_control_adapter_result_payload,
)
from ims.api.sqlite_readonly import readonly_sqlite_uri


RUN_CONTROL_EXECUTION_RESULT_SCHEMA = """
CREATE TABLE IF NOT EXISTS run_control_execution_results (
    queue_id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL,
    scenario_id TEXT NOT NULL,
    adapter_mode TEXT NOT NULL,
    fixture_kind TEXT NOT NULL,
    fixture_path TEXT NOT NULL,
    summary_mode TEXT NOT NULL,
    result_status TEXT NOT NULL,
    persisted_at TEXT NOT NULL,
    result_payload_json TEXT NOT NULL,
    summary_payload_json TEXT NOT NULL,
    validation_payload_json TEXT NOT NULL,
    adapter_execution_performed INTEGER NOT NULL CHECK (adapter_execution_performed IN (0, 1)),
    simulation_performed INTEGER NOT NULL CHECK (simulation_performed IN (0, 1)),
    automatic_historical_rule_selection_performed INTEGER NOT NULL CHECK (
        automatic_historical_rule_selection_performed IN (0, 1)
    ),
    historical_full_equality_claimed INTEGER NOT NULL CHECK (historical_full_equality_claimed IN (0, 1))
)
"""


@dataclass(frozen=True)
class RunControlExecutionResultRecord:
    queue_id: str
    run_id: str
    scenario_id: str
    adapter_mode: str
    fixture_kind: str
    fixture_path: str
    summary_mode: str
    result_status: str
    persisted_at: str
    result_payload: dict[str, object]
    summary_payload: dict[str, object]
    validation_payload: dict[str, object]
    adapter_execution_performed: bool
    simulation_performed: bool
    automatic_historical_rule_selection_performed: bool
    historical_full_equality_claimed: bool

    def to_dict(self) -> dict[str, object]:
        return {
            "queue_id": self.queue_id,
            "run_id": self.run_id,
            "scenario_id": self.scenario_id,
            "adapter_mode": self.adapter_mode,
            "fixture_kind": self.fixture_kind,
            "fixture_path": self.fixture_path,
            "summary_mode": self.summary_mode,
            "result_status": self.result_status,
            "persisted_at": self.persisted_at,
            "result_payload": dict(self.result_payload),
            "summary_payload": dict(self.summary_payload),
            "validation_payload": dict(self.validation_payload),
            "adapter_execution_performed": self.adapter_execution_performed,
            "simulation_performed": self.simulation_performed,
            "automatic_historical_rule_selection_performed": (
                self.automatic_historical_rule_selection_performed
            ),
            "historical_full_equality_claimed": self.historical_full_equality_claimed,
        }


@dataclass(frozen=True)
class RunControlExecutionResultStoreResult:
    mode: str
    db_path: str
    record: RunControlExecutionResultRecord | None = None
    writes_performed: bool = False
    execution_performed: bool = False
    adapter_started: bool = False
    simulation_performed: bool = False
    automatic_historical_rule_selection_performed: bool = False
    historical_full_equality_claimed: bool = False

    def to_dict(self) -> dict[str, object]:
        payload: dict[str, object] = {
            "status": "ok",
            "mode": self.mode,
            "schema_version": METADATA_SCHEMA_VERSION,
            "db_path": self.db_path,
            "writes_performed": self.writes_performed,
            "execution_performed": self.execution_performed,
            "adapter_started": self.adapter_started,
            "simulation_performed": self.simulation_performed,
            "automatic_historical_rule_selection_performed": (
                self.automatic_historical_rule_selection_performed
            ),
            "historical_full_equality_claimed": self.historical_full_equality_claimed,
        }
        if self.record is not None:
            payload["record"] = self.record.to_dict()
        return payload


def initialize_run_control_execution_result_store(
    db_path: Path | str,
) -> RunControlExecutionResultStoreResult:
    resolved_path = Path(db_path).expanduser().resolve()
    connection = connect_metadata_db(resolved_path)
    try:
        with connection:
            connection.execute(RUN_CONTROL_EXECUTION_RESULT_SCHEMA)
    finally:
        connection.close()
    return RunControlExecutionResultStoreResult(
        mode="run_control_execution_result_store_init",
        db_path=str(resolved_path),
        writes_performed=True,
    )


def persist_run_control_adapter_result(
    queue_id: str,
    adapter_result_path: Path | str,
    *,
    db_path: Path | str,
    persisted_at: str,
    explicit_persistence_release: bool = False,
) -> RunControlExecutionResultStoreResult:
    if not explicit_persistence_release:
        raise MetadataImportError("explicit persistence release is required")
    if not queue_id.strip():
        raise MetadataImportError("run control queue id must not be empty")
    if not persisted_at.strip():
        raise MetadataImportError("persisted_at must not be empty")

    resolved_db_path = Path(db_path).expanduser().resolve()
    payload = _load_adapter_result_payload(adapter_result_path)
    validation = validate_run_control_adapter_result_payload(payload)
    validation_payload = validation.to_dict()
    if not validation.result_accepted:
        issue_codes = ", ".join(issue.code for issue in validation.issues)
        raise MetadataImportError(f"adapter result does not match the Run-Control contract: {issue_codes}")
    if payload.get("explicit_execution_release") is not True:
        raise MetadataImportError("adapter result must document explicit_execution_release=true")

    connection = connect_metadata_db(resolved_db_path)
    try:
        with connection:
            connection.execute(RUN_CONTROL_EXECUTION_RESULT_SCHEMA)
            queue_row = _queue_row(connection, queue_id)
            if queue_row is None:
                raise MetadataImportError(f"run control queue entry not found: {queue_id}")
            if queue_row["status"] not in {"validated", "result_persisted"}:
                raise MetadataImportError(
                    "run control execution result persistence requires queue status validated"
                )
            if bool(queue_row["execution_enabled"]):
                raise MetadataImportError("run control queue entry unexpectedly enables execution")
            if bool(queue_row["execution_performed"]):
                raise MetadataImportError("run control queue entry unexpectedly reports execution")

            record = _build_record(queue_row, payload, validation_payload, persisted_at)
            connection.execute(
                """
                INSERT INTO run_control_execution_results (
                    queue_id,
                    run_id,
                    scenario_id,
                    adapter_mode,
                    fixture_kind,
                    fixture_path,
                    summary_mode,
                    result_status,
                    persisted_at,
                    result_payload_json,
                    summary_payload_json,
                    validation_payload_json,
                    adapter_execution_performed,
                    simulation_performed,
                    automatic_historical_rule_selection_performed,
                    historical_full_equality_claimed
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(queue_id) DO UPDATE SET
                    run_id = excluded.run_id,
                    scenario_id = excluded.scenario_id,
                    adapter_mode = excluded.adapter_mode,
                    fixture_kind = excluded.fixture_kind,
                    fixture_path = excluded.fixture_path,
                    summary_mode = excluded.summary_mode,
                    result_status = excluded.result_status,
                    persisted_at = excluded.persisted_at,
                    result_payload_json = excluded.result_payload_json,
                    summary_payload_json = excluded.summary_payload_json,
                    validation_payload_json = excluded.validation_payload_json,
                    adapter_execution_performed = excluded.adapter_execution_performed,
                    simulation_performed = excluded.simulation_performed,
                    automatic_historical_rule_selection_performed =
                        excluded.automatic_historical_rule_selection_performed,
                    historical_full_equality_claimed = excluded.historical_full_equality_claimed
                """,
                _record_values(record),
            )
            connection.execute(
                """
                UPDATE run_control_queue
                SET status = ?
                WHERE queue_id = ?
                """,
                ("result_persisted", queue_id),
            )
    finally:
        connection.close()

    return RunControlExecutionResultStoreResult(
        mode="run_control_execution_result_store_persist",
        db_path=str(resolved_db_path),
        record=record,
        writes_performed=True,
    )


def get_run_control_execution_result(
    queue_id: str,
    *,
    db_path: Path | str,
) -> RunControlExecutionResultStoreResult:
    if not queue_id.strip():
        raise MetadataImportError("run control queue id must not be empty")
    resolved_path = Path(db_path).expanduser().resolve()
    if not resolved_path.is_file():
        raise MetadataImportError(f"run control execution result database does not exist: {resolved_path}")
    connection = _connect_result_store_readonly(resolved_path)
    try:
        row = connection.execute(
            """
            SELECT
                queue_id,
                run_id,
                scenario_id,
                adapter_mode,
                fixture_kind,
                fixture_path,
                summary_mode,
                result_status,
                persisted_at,
                result_payload_json,
                summary_payload_json,
                validation_payload_json,
                adapter_execution_performed,
                simulation_performed,
                automatic_historical_rule_selection_performed,
                historical_full_equality_claimed
            FROM run_control_execution_results
            WHERE queue_id = ?
            """,
            (queue_id,),
        ).fetchone()
    except sqlite3.DatabaseError as exc:
        raise MetadataImportError(
            f"run control execution result database is not readable or initialized: {exc}"
        ) from exc
    finally:
        connection.close()
    if row is None:
        raise MetadataImportError(f"run control execution result not found: {queue_id}")
    return RunControlExecutionResultStoreResult(
        mode="run_control_execution_result_store_show",
        db_path=str(resolved_path),
        record=_row_to_record(row),
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "init":
            payload = initialize_run_control_execution_result_store(args.db).to_dict()
        elif args.command == "persist":
            payload = persist_run_control_adapter_result(
                args.queue_id,
                args.adapter_result,
                db_path=args.db,
                persisted_at=args.persisted_at,
                explicit_persistence_release=args.explicit_persistence_release,
            ).to_dict()
        elif args.command == "show":
            payload = get_run_control_execution_result(args.queue_id, db_path=args.db).to_dict()
        else:  # pragma: no cover - argparse prevents this branch
            raise MetadataImportError(f"unsupported result store command: {args.command}")
    except MetadataImportError as exc:
        _print_json(
            {
                "status": "error",
                "mode": f"run_control_execution_result_store_{args.command}",
                "message": str(exc),
                "issues": [str(exc)],
                "writes_performed": False,
                "execution_performed": False,
                "adapter_started": False,
                "simulation_performed": False,
            }
        )
        return 2
    _print_json(payload)
    return 0


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m ims.api.run_control_execution_result_store",
        description="Speichert vorab validierte Run-Control-Adapterresultate ohne Adapterstart.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="Resultat-Schema in expliziter SQLite-Datei anlegen.")
    init_parser.add_argument("--db", required=True, type=Path, help="Expliziter SQLite-Zielpfad.")

    persist_parser = subparsers.add_parser("persist", help="Vorab geprueftes Adapterresultat speichern.")
    persist_parser.add_argument("--db", required=True, type=Path, help="Expliziter SQLite-Zielpfad.")
    persist_parser.add_argument("--queue-id", required=True, help="Queue-ID des validierten Eintrags.")
    persist_parser.add_argument("--adapter-result", required=True, type=Path, help="Lokales Adapter-Resultat-JSON.")
    persist_parser.add_argument("--persisted-at", required=True, help="Expliziter Persistenzzeitpunkt.")
    persist_parser.add_argument(
        "--explicit-persistence-release",
        action="store_true",
        required=True,
        help="Explizite lokale Freigabe fuer diese Ergebnis-Persistenz.",
    )

    show_parser = subparsers.add_parser("show", help="Persistiertes Resultat lesend anzeigen.")
    show_parser.add_argument("--db", required=True, type=Path, help="Expliziter SQLite-Quellpfad.")
    show_parser.add_argument("--queue-id", required=True, help="Queue-ID.")
    return parser


def _load_adapter_result_payload(path: Path | str) -> dict[str, object]:
    with Path(path).expanduser().resolve().open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise MetadataImportError("adapter result payload must be a JSON object")
    return payload


def _queue_row(connection: sqlite3.Connection, queue_id: str) -> sqlite3.Row | None:
    try:
        return connection.execute(
            """
            SELECT
                queue_id,
                run_id,
                scenario_id,
                status,
                execution_enabled,
                execution_performed
            FROM run_control_queue
            WHERE queue_id = ?
            """,
            (queue_id,),
        ).fetchone()
    except sqlite3.DatabaseError as exc:
        raise MetadataImportError(f"run control queue is not readable or initialized: {exc}") from exc


def _build_record(
    queue_row: sqlite3.Row,
    payload: Mapping[str, object],
    validation_payload: dict[str, object],
    persisted_at: str,
) -> RunControlExecutionResultRecord:
    summary = payload.get("summary")
    if not isinstance(summary, dict):
        raise MetadataImportError("adapter result summary must be a JSON object")
    return RunControlExecutionResultRecord(
        queue_id=str(queue_row["queue_id"]),
        run_id=str(queue_row["run_id"]),
        scenario_id=str(queue_row["scenario_id"]),
        adapter_mode=str(payload["adapter_mode"]),
        fixture_kind=str(payload["fixture_kind"]),
        fixture_path=str(payload["fixture_path"]),
        summary_mode=str(summary["mode"]),
        result_status=str(payload["status"]),
        persisted_at=persisted_at,
        result_payload=dict(payload),
        summary_payload=dict(summary),
        validation_payload=validation_payload,
        adapter_execution_performed=bool(payload["execution_performed"]),
        simulation_performed=bool(payload["simulation_performed"]),
        automatic_historical_rule_selection_performed=bool(
            payload["automatic_historical_rule_selection_performed"]
        ),
        historical_full_equality_claimed=bool(payload["historical_full_equality_claimed"]),
    )


def _record_values(record: RunControlExecutionResultRecord) -> tuple[object, ...]:
    return (
        record.queue_id,
        record.run_id,
        record.scenario_id,
        record.adapter_mode,
        record.fixture_kind,
        record.fixture_path,
        record.summary_mode,
        record.result_status,
        record.persisted_at,
        _stable_json(record.result_payload),
        _stable_json(record.summary_payload),
        _stable_json(record.validation_payload),
        int(record.adapter_execution_performed),
        int(record.simulation_performed),
        int(record.automatic_historical_rule_selection_performed),
        int(record.historical_full_equality_claimed),
    )


def _row_to_record(row: sqlite3.Row) -> RunControlExecutionResultRecord:
    return RunControlExecutionResultRecord(
        queue_id=row["queue_id"],
        run_id=row["run_id"],
        scenario_id=row["scenario_id"],
        adapter_mode=row["adapter_mode"],
        fixture_kind=row["fixture_kind"],
        fixture_path=row["fixture_path"],
        summary_mode=row["summary_mode"],
        result_status=row["result_status"],
        persisted_at=row["persisted_at"],
        result_payload=json.loads(row["result_payload_json"]),
        summary_payload=json.loads(row["summary_payload_json"]),
        validation_payload=json.loads(row["validation_payload_json"]),
        adapter_execution_performed=bool(row["adapter_execution_performed"]),
        simulation_performed=bool(row["simulation_performed"]),
        automatic_historical_rule_selection_performed=bool(
            row["automatic_historical_rule_selection_performed"]
        ),
        historical_full_equality_claimed=bool(row["historical_full_equality_claimed"]),
    )


def _connect_result_store_readonly(path: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(
        readonly_sqlite_uri(path, description="run control execution result store"),
        uri=True,
        check_same_thread=False,
    )
    connection.row_factory = sqlite3.Row
    return connection


def _stable_json(payload: Mapping[str, object]) -> str:
    return json.dumps(payload, ensure_ascii=True, sort_keys=True, separators=(",", ":"))


def _print_json(payload: dict[str, object]) -> None:
    print(json.dumps(payload, ensure_ascii=True, sort_keys=True))


if __name__ == "__main__":
    raise SystemExit(main())
