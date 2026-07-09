from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class RunControlCoreDiagnosticsBridgeIssue:
    source: str
    code: str
    severity: str
    message: str
    queue_ids: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, object]:
        return {
            "source": self.source,
            "code": self.code,
            "severity": self.severity,
            "message": self.message,
            "queue_ids": list(self.queue_ids),
        }


@dataclass(frozen=True)
class RunControlCoreDiagnosticsBridgeAction:
    queue_id: str
    run_id: str
    scenario_id: str
    queue_status: str
    queue_next_action: str
    core_validation_status: str
    bridge_next_action: str
    blocked_by: tuple[str, ...]
    execution_summary_next_action: str
    execution_allowed: bool = False
    writes_performed: bool = False
    execution_performed: bool = False

    def to_dict(self) -> dict[str, object]:
        return {
            "queue_id": self.queue_id,
            "run_id": self.run_id,
            "scenario_id": self.scenario_id,
            "queue_status": self.queue_status,
            "queue_next_action": self.queue_next_action,
            "core_validation_status": self.core_validation_status,
            "bridge_next_action": self.bridge_next_action,
            "blocked_by": list(self.blocked_by),
            "execution_summary_next_action": self.execution_summary_next_action,
            "execution_allowed": self.execution_allowed,
            "writes_performed": self.writes_performed,
            "execution_performed": self.execution_performed,
        }


@dataclass(frozen=True)
class RunControlCoreDiagnosticsBridgeResult:
    status: str
    queue_action_plan_mode: str
    core_validation_mode: str
    queue_count: int
    action_count: int
    period_plan_count: int
    period_count: int
    global_periods: tuple[int, ...]
    legacy_reference_count: int
    execution_summary_available: bool
    execution_summary_next_action: str
    actions: tuple[RunControlCoreDiagnosticsBridgeAction, ...]
    issues: tuple[RunControlCoreDiagnosticsBridgeIssue, ...]
    writes_performed: bool = False
    execution_performed: bool = False

    def to_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "mode": "run_control_core_diagnostics_bridge",
            "queue_action_plan_mode": self.queue_action_plan_mode,
            "core_validation_mode": self.core_validation_mode,
            "queue_count": self.queue_count,
            "action_count": self.action_count,
            "period_plan_count": self.period_plan_count,
            "period_count": self.period_count,
            "global_periods": list(self.global_periods),
            "legacy_reference_count": self.legacy_reference_count,
            "execution_summary_available": self.execution_summary_available,
            "execution_summary_next_action": self.execution_summary_next_action,
            "actions": [action.to_dict() for action in self.actions],
            "issues": [issue.to_dict() for issue in self.issues],
            "writes_performed": self.writes_performed,
            "execution_performed": self.execution_performed,
        }


def build_run_control_core_diagnostics_bridge(
    queue_action_plan: Any,
    core_validation_overview: Any,
) -> RunControlCoreDiagnosticsBridgeResult:
    queue_payload = _as_payload(queue_action_plan)
    core_payload = _as_payload(core_validation_overview)
    upstream_issues = _issues_from_payload("queue_action_plan", queue_payload) + _issues_from_payload(
        "core_validation_overview",
        core_payload,
    )
    actions = tuple(_bridge_action(action, core_payload) for action in _list(queue_payload.get("actions")))
    issues = upstream_issues + _issues_from_actions(actions)
    return RunControlCoreDiagnosticsBridgeResult(
        status=_status_from_parts(
            [
                str(queue_payload.get("status", "ok")),
                str(core_payload.get("status", "ok")),
            ],
            issues,
        ),
        queue_action_plan_mode=str(queue_payload.get("mode", "")),
        core_validation_mode=str(core_payload.get("mode", "")),
        queue_count=_int_value(queue_payload.get("queue_count")),
        action_count=len(actions),
        period_plan_count=_int_value(core_payload.get("plan_count")),
        period_count=_int_value(core_payload.get("period_count")),
        global_periods=tuple(_int_value(value) for value in _list(core_payload.get("global_periods"))),
        legacy_reference_count=_int_value(core_payload.get("legacy_reference_count")),
        execution_summary_available=bool(core_payload.get("execution_summary_available", False)),
        execution_summary_next_action=str(
            core_payload.get("execution_summary_next_action", "await_precomputed_execution_summary")
        ),
        actions=actions,
        issues=issues,
    )


def _bridge_action(
    queue_action: Mapping[str, Any],
    core_payload: Mapping[str, Any],
) -> RunControlCoreDiagnosticsBridgeAction:
    queue_next_action = str(queue_action.get("next_action", "inspect_queue_status"))
    queue_blockers = tuple(str(item) for item in _list(queue_action.get("blocked_by")))
    core_status = str(core_payload.get("status", "ok"))
    execution_summary_next_action = str(
        core_payload.get("execution_summary_next_action", "await_precomputed_execution_summary")
    )
    bridge_next_action, core_blockers = _bridge_next_action(
        queue_next_action=queue_next_action,
        queue_blockers=queue_blockers,
        core_payload=core_payload,
    )
    blocked_by = tuple(dict.fromkeys(queue_blockers + core_blockers))
    return RunControlCoreDiagnosticsBridgeAction(
        queue_id=str(queue_action.get("queue_id", "")),
        run_id=str(queue_action.get("run_id", "")),
        scenario_id=str(queue_action.get("scenario_id", "")),
        queue_status=str(queue_action.get("queue_status", "")),
        queue_next_action=queue_next_action,
        core_validation_status=core_status,
        bridge_next_action=bridge_next_action,
        blocked_by=blocked_by,
        execution_summary_next_action=execution_summary_next_action,
    )


def _bridge_next_action(
    *,
    queue_next_action: str,
    queue_blockers: tuple[str, ...],
    core_payload: Mapping[str, Any],
) -> tuple[str, tuple[str, ...]]:
    if queue_next_action == "inspect_queue_status":
        return "inspect_queue_status", ()
    if queue_next_action == "resolve_blockers" or queue_blockers:
        return "resolve_blockers", ()

    core_status = str(core_payload.get("status", "ok"))
    next_validation_actions = tuple(str(action) for action in _list(core_payload.get("next_validation_actions")))
    if core_status == "error":
        return "resolve_core_validation_blockers", ("core_validation_error",)
    if "await_historical_reference" in next_validation_actions:
        return "resolve_core_validation_blockers", ("core_validation_await_historical_reference",)
    if not bool(core_payload.get("execution_summary_available", False)):
        return "await_precomputed_execution_summary", ("execution_summary_missing",)
    return queue_next_action, ()


def _issues_from_payload(
    source: str,
    payload: Mapping[str, Any],
) -> tuple[RunControlCoreDiagnosticsBridgeIssue, ...]:
    issues: list[RunControlCoreDiagnosticsBridgeIssue] = []
    for raw_issue in _list(payload.get("issues")):
        if not isinstance(raw_issue, Mapping):
            continue
        issues.append(
            RunControlCoreDiagnosticsBridgeIssue(
                source=source,
                code=str(raw_issue.get("code", "diagnostic_issue")),
                severity=str(raw_issue.get("severity", "warning")),
                message=str(raw_issue.get("message", "")),
                queue_ids=tuple(str(queue_id) for queue_id in _list(raw_issue.get("queue_ids"))),
            )
        )
    return tuple(issues)


def _issues_from_actions(
    actions: tuple[RunControlCoreDiagnosticsBridgeAction, ...],
) -> tuple[RunControlCoreDiagnosticsBridgeIssue, ...]:
    seen: set[tuple[str, tuple[str, ...]]] = set()
    issues: list[RunControlCoreDiagnosticsBridgeIssue] = []
    messages = {
        "core_validation_error": "core validation overview is in error state",
        "core_validation_await_historical_reference": (
            "core validation overview still awaits historical references"
        ),
        "execution_summary_missing": "precomputed execution summary is not available",
    }
    for action in actions:
        for blocker in action.blocked_by:
            if blocker not in messages:
                continue
            key = (blocker, (action.queue_id,))
            if key in seen:
                continue
            seen.add(key)
            issues.append(
                RunControlCoreDiagnosticsBridgeIssue(
                    source="run_control_core_diagnostics_bridge",
                    code=blocker,
                    severity="warning",
                    message=messages[blocker],
                    queue_ids=(action.queue_id,),
                )
            )
    return tuple(issues)


def _status_from_parts(
    statuses: list[str],
    issues: tuple[RunControlCoreDiagnosticsBridgeIssue, ...],
) -> str:
    combined = statuses + [issue.severity for issue in issues]
    if "error" in combined:
        return "error"
    if "warning" in combined:
        return "warning"
    return "ok"


def _as_payload(value: Any) -> Mapping[str, Any]:
    if isinstance(value, Mapping):
        return value
    to_dict = getattr(value, "to_dict", None)
    if callable(to_dict):
        payload = to_dict()
        if isinstance(payload, Mapping):
            return payload
    raise TypeError("run control core diagnostics bridge requires mapping payloads or to_dict() objects")


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _int_value(value: Any) -> int:
    return value if isinstance(value, int) else 0
