from __future__ import annotations

import argparse
import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from ims.api.metadata import METADATA_SCHEMA_VERSION
from ims.api.metadata_import import MetadataImportError
from ims.api.metadata_import_cli import _metadata_read_repository
from ims.api.run_control_queue import RUN_CONTROL_QUEUE_STATUSES, list_run_control_queue


@dataclass(frozen=True)
class RunControlQueueDiagnosticIssue:
    code: str
    severity: str
    message: str

    def to_dict(self) -> dict[str, str]:
        return {
            "code": self.code,
            "severity": self.severity,
            "message": self.message,
        }


@dataclass(frozen=True)
class RunControlQueueDiagnosticsResult:
    db_path: str
    metadata_source: dict[str, object]
    queue_initialized: bool
    queue_readable: bool
    queue_count: int
    queue_ids: tuple[str, ...]
    missing_scenario_queue_ids: tuple[str, ...]
    execution_enabled_queue_ids: tuple[str, ...]
    execution_performed_queue_ids: tuple[str, ...]
    unsupported_status_queue_ids: tuple[str, ...]
    issues: tuple[RunControlQueueDiagnosticIssue, ...]
    writes_performed: bool = False
    execution_performed: bool = False

    def to_dict(self) -> dict[str, object]:
        return {
            "status": _status_from_issues(self.issues),
            "mode": "run_control_queue_diagnostics",
            "schema_version": METADATA_SCHEMA_VERSION,
            "db_path": self.db_path,
            "metadata_source": self.metadata_source,
            "queue_initialized": self.queue_initialized,
            "queue_readable": self.queue_readable,
            "queue_count": self.queue_count,
            "queue_ids": list(self.queue_ids),
            "missing_scenario_queue_ids": list(self.missing_scenario_queue_ids),
            "execution_enabled_queue_ids": list(self.execution_enabled_queue_ids),
            "execution_performed_queue_ids": list(self.execution_performed_queue_ids),
            "unsupported_status_queue_ids": list(self.unsupported_status_queue_ids),
            "issues": [issue.to_dict() for issue in self.issues],
            "writes_performed": self.writes_performed,
            "execution_performed": self.execution_performed,
        }


def diagnose_run_control_queue(db_path: Path | str) -> RunControlQueueDiagnosticsResult:
    resolved_path = Path(db_path).expanduser().resolve()
    if not resolved_path.is_file():
        raise MetadataImportError(f"run control queue diagnostics database does not exist: {resolved_path}")

    repository = _metadata_read_repository(resolved_path, mode="run-control-queue-diagnostics")
    metadata_source = repository.metadata_source()

    issues: list[RunControlQueueDiagnosticIssue] = []
    try:
        queue_payload = list_run_control_queue(resolved_path).to_dict()
    except MetadataImportError as exc:
        message = str(exc)
        if _is_missing_queue_table(message):
            issues.append(
                RunControlQueueDiagnosticIssue(
                    code="run_control_queue_not_initialized",
                    severity="info",
                    message=message,
                )
            )
            return _diagnostics_result(
                resolved_path,
                metadata_source,
                queue_initialized=False,
                queue_readable=False,
                issues=issues,
            )
        issues.append(
            RunControlQueueDiagnosticIssue(
                code="run_control_queue_unreadable",
                severity="warning",
                message=message,
            )
        )
        return _diagnostics_result(
            resolved_path,
            metadata_source,
            queue_initialized=True,
            queue_readable=False,
            issues=issues,
        )

    entries = tuple(entry for entry in queue_payload.get("entries", ()) if isinstance(entry, dict))
    queue_ids = tuple(str(entry.get("queue_id", "")) for entry in entries)
    scenario_ids, scenario_issue = _scenario_ids(repository)
    if scenario_issue is not None:
        issues.append(scenario_issue)
    missing_scenario_ids: list[str] = []
    execution_enabled_ids: list[str] = []
    execution_performed_ids: list[str] = []
    unsupported_status_ids: list[str] = []

    for entry in entries:
        queue_id = str(entry.get("queue_id", ""))
        request = entry.get("request", {})
        scenario_id = str(request.get("scenario_id", "")) if isinstance(request, dict) else ""
        if scenario_issue is None and scenario_id not in scenario_ids:
            missing_scenario_ids.append(queue_id)
        if bool(entry.get("execution_enabled")):
            execution_enabled_ids.append(queue_id)
        if bool(entry.get("execution_performed")) and entry.get("status") != "result_persisted":
            execution_performed_ids.append(queue_id)
        if str(entry.get("status", "")) not in RUN_CONTROL_QUEUE_STATUSES:
            unsupported_status_ids.append(queue_id)

    _append_queue_issues(
        issues,
        missing_scenario_ids=missing_scenario_ids,
        execution_enabled_ids=execution_enabled_ids,
        execution_performed_ids=execution_performed_ids,
        unsupported_status_ids=unsupported_status_ids,
    )
    return RunControlQueueDiagnosticsResult(
        db_path=str(resolved_path),
        metadata_source=metadata_source,
        queue_initialized=True,
        queue_readable=True,
        queue_count=len(entries),
        queue_ids=queue_ids,
        missing_scenario_queue_ids=tuple(missing_scenario_ids),
        execution_enabled_queue_ids=tuple(execution_enabled_ids),
        execution_performed_queue_ids=tuple(execution_performed_ids),
        unsupported_status_queue_ids=tuple(unsupported_status_ids),
        issues=tuple(issues),
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    try:
        payload = diagnose_run_control_queue(args.db).to_dict()
    except MetadataImportError as exc:
        _print_json(
            {
                "status": "error",
                "mode": "run_control_queue_diagnostics",
                "message": str(exc),
                "issues": [str(exc)],
                "writes_performed": False,
                "execution_performed": False,
            }
        )
        return 2
    _print_json(payload)
    return 1 if payload["status"] == "error" else 0


def _scenario_ids(repository) -> tuple[set[str], RunControlQueueDiagnosticIssue | None]:
    try:
        scenarios = repository.list_scenarios()
    except sqlite3.DatabaseError as exc:
        if _is_missing_metadata_table(str(exc)):
            return set(), RunControlQueueDiagnosticIssue(
                code="run_control_queue_missing_metadata_schema",
                severity="warning",
                message=f"run control queue diagnostics metadata schema is not initialized: {exc}",
            )
        raise MetadataImportError(f"run control queue diagnostics database is not readable: {exc}") from exc
    items = scenarios.get("items", [])
    if not isinstance(items, list):
        return set(), None
    return (
        {
            str(item.get("id", ""))
            for item in items
            if isinstance(item, dict) and isinstance(item.get("id"), str)
        },
        None,
    )


def _diagnostics_result(
    db_path: Path,
    metadata_source: dict[str, object],
    *,
    queue_initialized: bool,
    queue_readable: bool,
    issues: Sequence[RunControlQueueDiagnosticIssue],
) -> RunControlQueueDiagnosticsResult:
    return RunControlQueueDiagnosticsResult(
        db_path=str(db_path),
        metadata_source=metadata_source,
        queue_initialized=queue_initialized,
        queue_readable=queue_readable,
        queue_count=0,
        queue_ids=(),
        missing_scenario_queue_ids=(),
        execution_enabled_queue_ids=(),
        execution_performed_queue_ids=(),
        unsupported_status_queue_ids=(),
        issues=tuple(issues),
    )


def _append_queue_issues(
    issues: list[RunControlQueueDiagnosticIssue],
    *,
    missing_scenario_ids: Sequence[str],
    execution_enabled_ids: Sequence[str],
    execution_performed_ids: Sequence[str],
    unsupported_status_ids: Sequence[str],
) -> None:
    if missing_scenario_ids:
        issues.append(
            RunControlQueueDiagnosticIssue(
                code="run_control_queue_missing_scenario",
                severity="warning",
                message=f"queue entries reference missing scenarios: {', '.join(missing_scenario_ids)}",
            )
        )
    if execution_enabled_ids:
        issues.append(
            RunControlQueueDiagnosticIssue(
                code="run_control_queue_execution_enabled",
                severity="error",
                message=f"queue entries unexpectedly enable execution: {', '.join(execution_enabled_ids)}",
            )
        )
    if execution_performed_ids:
        issues.append(
            RunControlQueueDiagnosticIssue(
                code="run_control_queue_execution_performed",
                severity="error",
                message=f"queue entries unexpectedly report execution: {', '.join(execution_performed_ids)}",
            )
        )
    if unsupported_status_ids:
        issues.append(
            RunControlQueueDiagnosticIssue(
                code="run_control_queue_unsupported_status",
                severity="warning",
                message=f"queue entries use unsupported status values: {', '.join(unsupported_status_ids)}",
            )
        )


def _status_from_issues(issues: Sequence[RunControlQueueDiagnosticIssue]) -> str:
    if any(issue.severity == "error" for issue in issues):
        return "error"
    if any(issue.severity == "warning" for issue in issues):
        return "warning"
    return "ok"


def _is_missing_queue_table(message: str) -> bool:
    return "no such table: run_control_queue" in message


def _is_missing_metadata_table(message: str) -> bool:
    return "no such table: scenarios" in message or "no such table: runs" in message


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m ims.api.run_control_queue_diagnostics",
        description="Diagnostiziert lokale Run-Control-Queue-Metadaten rein lesend.",
    )
    parser.add_argument("--db", type=Path, required=True, help="Expliziter SQLite-Quellpfad.")
    return parser


def _print_json(payload: dict[str, object]) -> None:
    print(json.dumps(payload, ensure_ascii=True, sort_keys=True))


if __name__ == "__main__":
    raise SystemExit(main())
