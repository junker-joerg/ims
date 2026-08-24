from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from ims.api.metadata import METADATA_SCHEMA_VERSION
from ims.api.metadata_import import MetadataImportError
from ims.api.run_control_preflight import preflight_run_control
from ims.api.run_control_queue import WorkbenchRunControlQueueEntry, list_run_control_queue
from ims.api.run_control_queue_diagnostics import diagnose_run_control_queue


@dataclass(frozen=True)
class RunControlQueueActionPlanIssue:
    code: str
    severity: str
    message: str
    queue_ids: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, object]:
        return {
            "code": self.code,
            "severity": self.severity,
            "message": self.message,
            "queue_ids": list(self.queue_ids),
        }


@dataclass(frozen=True)
class RunControlQueueAction:
    queue_id: str
    run_id: str
    scenario_id: str
    queue_status: str
    next_action: str
    next_action_label: str
    blocked_by: tuple[str, ...]
    execution_allowed: bool = False
    writes_performed: bool = False
    execution_performed: bool = False

    def to_dict(self) -> dict[str, object]:
        return {
            "queue_id": self.queue_id,
            "run_id": self.run_id,
            "scenario_id": self.scenario_id,
            "queue_status": self.queue_status,
            "next_action": self.next_action,
            "next_action_label": self.next_action_label,
            "blocked_by": list(self.blocked_by),
            "execution_allowed": self.execution_allowed,
            "writes_performed": self.writes_performed,
            "execution_performed": self.execution_performed,
        }


@dataclass(frozen=True)
class RunControlQueueActionPlanResult:
    db_path: str
    metadata_source: dict[str, object]
    queue_count: int
    actions: tuple[RunControlQueueAction, ...]
    issues: tuple[RunControlQueueActionPlanIssue, ...]
    queue_id: str | None = None
    writes_performed: bool = False
    execution_performed: bool = False

    def to_dict(self) -> dict[str, object]:
        payload: dict[str, object] = {
            "status": _status_from_issues(self.issues),
            "mode": "run_control_queue_action_plan",
            "schema_version": METADATA_SCHEMA_VERSION,
            "db_path": self.db_path,
            "metadata_source": self.metadata_source,
            "queue_count": self.queue_count,
            "actions": [action.to_dict() for action in self.actions],
            "issues": [issue.to_dict() for issue in self.issues],
            "writes_performed": self.writes_performed,
            "execution_performed": self.execution_performed,
        }
        if self.queue_id is not None:
            payload["queue_id"] = self.queue_id
        return payload


def build_run_control_queue_action_plan(
    db_path: Path | str,
    *,
    queue_id: str | None = None,
) -> RunControlQueueActionPlanResult:
    resolved_path = Path(db_path).expanduser().resolve()
    diagnostics = diagnose_run_control_queue(resolved_path)
    diagnostic_payload = diagnostics.to_dict()
    issues = _diagnostic_issues(diagnostic_payload)

    if not diagnostics.queue_initialized:
        issues = issues + (
            RunControlQueueActionPlanIssue(
                code="run_control_queue_not_initialized",
                severity="warning",
                message="run control queue is not initialized; run the explicit init command before planning actions",
            ),
        )
        return RunControlQueueActionPlanResult(
            db_path=str(resolved_path),
            metadata_source=diagnostics.metadata_source,
            queue_count=0,
            actions=(),
            issues=issues,
            queue_id=queue_id,
        )

    if not diagnostics.queue_readable:
        return RunControlQueueActionPlanResult(
            db_path=str(resolved_path),
            metadata_source=diagnostics.metadata_source,
            queue_count=0,
            actions=(),
            issues=issues,
            queue_id=queue_id,
        )

    entries = list_run_control_queue(resolved_path).entries
    selected_entries = _filter_entries(entries, queue_id)
    if queue_id is not None and not selected_entries:
        issues = issues + (
            RunControlQueueActionPlanIssue(
                code="run_control_queue_id_not_found",
                severity="warning",
                message=f"run control queue entry not found for --queue-id: {queue_id}",
                queue_ids=(queue_id,),
            ),
        )

    actions = tuple(
        _action_for_entry(
            entry,
            db_path=resolved_path,
            diagnostic_blockers=_entry_diagnostic_blockers(entry.queue_id, diagnostics, issues),
        )
        for entry in selected_entries
    )
    return RunControlQueueActionPlanResult(
        db_path=str(resolved_path),
        metadata_source=diagnostics.metadata_source,
        queue_id=queue_id,
        queue_count=len(selected_entries) if queue_id is not None else diagnostics.queue_count,
        actions=actions,
        issues=issues + _preflight_issues(actions),
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    try:
        payload = build_run_control_queue_action_plan(args.db, queue_id=args.queue_id).to_dict()
    except MetadataImportError as exc:
        _print_json(
            {
                "status": "error",
                "mode": "run_control_queue_action_plan",
                "message": str(exc),
                "issues": [
                    {
                        "code": "run_control_queue_action_plan_unavailable",
                        "severity": "error",
                        "message": str(exc),
                        "queue_ids": [],
                    }
                ],
                "writes_performed": False,
                "execution_performed": False,
            }
        )
        return 2
    _print_json(payload)
    return 1 if payload["status"] == "error" else 0


def _action_for_entry(
    entry: WorkbenchRunControlQueueEntry,
    *,
    db_path: Path,
    diagnostic_blockers: tuple[str, ...],
) -> RunControlQueueAction:
    preflight_blockers = _preflight_blockers(entry, db_path) if not diagnostic_blockers else ()
    blocked_by = diagnostic_blockers + preflight_blockers
    if entry.status == "blocked":
        blocked_by = tuple(dict.fromkeys(blocked_by + ("run_control_queue_status_blocked",)))
        next_action = "resolve_blockers"
        label = "Blockierende Hinweise klaeren"
    elif entry.status == "planned":
        if blocked_by:
            next_action = "resolve_blockers"
            label = "Blockierende Hinweise klaeren"
        else:
            next_action = "run_preflight"
            label = "Lokalen Preflight ausfuehren"
    elif entry.status == "validated":
        if blocked_by:
            next_action = "resolve_blockers"
            label = "Blockierende Hinweise klaeren"
        else:
            next_action = "await_execution_release"
            label = "Auf separate Ausfuehrungsfreigabe warten"
    elif entry.status == "starting":
        next_action = "await_execution_completion"
        label = "Auf Abschluss des Adapterstarts warten"
    elif entry.status == "failed":
        next_action = "inspect_execution_failure"
        label = "Fehlgeschlagenen Adapterstart pruefen"
    elif entry.status == "result_persisted":
        next_action = "inspect_persisted_result"
        label = "Persistiertes Ergebnis pruefen"
    else:
        next_action = "inspect_queue_status"
        label = "Queue-Status pruefen"
    return RunControlQueueAction(
        queue_id=entry.queue_id,
        run_id=entry.request.run_id,
        scenario_id=entry.request.scenario_id,
        queue_status=entry.status,
        next_action=next_action,
        next_action_label=label,
        blocked_by=blocked_by,
        execution_performed=entry.execution_performed,
    )


def _preflight_blockers(entry: WorkbenchRunControlQueueEntry, db_path: Path) -> tuple[str, ...]:
    try:
        payload = preflight_run_control(entry.request.run_id, db_path).to_dict()
    except MetadataImportError:
        return ("run_control_preflight_unavailable",)
    if payload["status"] != "ok":
        return ("run_control_preflight_failed",)
    if payload.get("execution_enabled") or payload.get("execution_allowed"):
        return ("run_control_execution_boundary",)
    return ()


def _preflight_issues(actions: Sequence[RunControlQueueAction]) -> tuple[RunControlQueueActionPlanIssue, ...]:
    issues: list[RunControlQueueActionPlanIssue] = []
    for action in actions:
        preflight_codes = tuple(code for code in action.blocked_by if code.startswith("run_control_preflight"))
        if not preflight_codes:
            continue
        issues.append(
            RunControlQueueActionPlanIssue(
                code="run_control_preflight_blocked",
                severity="warning",
                message=f"queue entry requires blocker resolution before local preflight can pass: {action.queue_id}",
                queue_ids=(action.queue_id,),
            )
        )
    return tuple(issues)


def _diagnostic_issues(payload: dict[str, object]) -> tuple[RunControlQueueActionPlanIssue, ...]:
    raw_issues = payload.get("issues", [])
    if not isinstance(raw_issues, list):
        return ()
    issues: list[RunControlQueueActionPlanIssue] = []
    for raw_issue in raw_issues:
        if isinstance(raw_issue, dict):
            issues.append(
                RunControlQueueActionPlanIssue(
                    code=str(raw_issue.get("code", "run_control_queue_diagnostic_issue")),
                    severity=str(raw_issue.get("severity", "warning")),
                    message=str(raw_issue.get("message", "")),
                )
            )
        else:
            issues.append(
                RunControlQueueActionPlanIssue(
                    code="run_control_queue_diagnostic_issue",
                    severity="warning",
                    message=str(raw_issue),
                )
            )
    return tuple(issues)


def _entry_diagnostic_blockers(
    queue_id: str,
    diagnostics,
    issues: Sequence[RunControlQueueActionPlanIssue],
) -> tuple[str, ...]:
    blockers: list[str] = []
    queue_issue_map = (
        ("run_control_queue_missing_scenario", diagnostics.missing_scenario_queue_ids),
        ("run_control_queue_execution_enabled", diagnostics.execution_enabled_queue_ids),
        ("run_control_queue_execution_performed", diagnostics.execution_performed_queue_ids),
        ("run_control_queue_unsupported_status", diagnostics.unsupported_status_queue_ids),
    )
    for code, queue_ids in queue_issue_map:
        if queue_id in queue_ids:
            blockers.append(code)
    global_issue_codes = {
        issue.code
        for issue in issues
        if issue.code
        not in {
            "run_control_queue_missing_scenario",
            "run_control_queue_execution_enabled",
            "run_control_queue_execution_performed",
            "run_control_queue_unsupported_status",
            "run_control_queue_id_not_found",
        }
        and issue.severity in {"warning", "error"}
    }
    blockers.extend(sorted(global_issue_codes))
    return tuple(dict.fromkeys(blockers))


def _filter_entries(
    entries: Sequence[WorkbenchRunControlQueueEntry],
    queue_id: str | None,
) -> tuple[WorkbenchRunControlQueueEntry, ...]:
    if queue_id is None:
        return tuple(entries)
    return tuple(entry for entry in entries if entry.queue_id == queue_id)


def _status_from_issues(issues: Sequence[RunControlQueueActionPlanIssue]) -> str:
    if any(issue.severity == "error" for issue in issues):
        return "error"
    if any(issue.severity == "warning" for issue in issues):
        return "warning"
    return "ok"


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m ims.api.run_control_queue_action_plan",
        description="Leitet lokale Run-Control-Queue-Aktionsplaene rein lesend ab.",
    )
    parser.add_argument("--db", required=True, type=Path, help="Expliziter SQLite-Quellpfad.")
    parser.add_argument("--queue-id", help="Optionaler Queue-ID-Filter.")
    return parser


def _print_json(payload: dict[str, object]) -> None:
    print(json.dumps(payload, ensure_ascii=True, sort_keys=True))


if __name__ == "__main__":
    raise SystemExit(main())
