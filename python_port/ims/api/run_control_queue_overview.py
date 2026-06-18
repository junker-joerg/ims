from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ims.api.metadata import METADATA_GENERATED_AT, METADATA_SCHEMA_VERSION
from ims.api.metadata_import import MetadataImportError
from ims.api.run_control_queue import get_run_control_queue_entry, list_run_control_queue


@dataclass(frozen=True)
class RunControlQueueOverviewIssue:
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
class RunControlQueueOverview:
    status: str
    source: dict[str, object]
    entries: tuple[dict[str, object], ...]
    issues: tuple[RunControlQueueOverviewIssue, ...] = ()

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": METADATA_SCHEMA_VERSION,
            "generated_at": METADATA_GENERATED_AT,
            "status": self.status,
            "mode": "run_control_queue_overview",
            "source": self.source,
            "queue_count": len(self.entries),
            "entries": list(self.entries),
            "issues": [issue.to_dict() for issue in self.issues],
            "writes_enabled": False,
            "execution_enabled": False,
            "execution_performed": False,
        }


def run_control_queue_overview_payload(metadata_source: dict[str, object]) -> dict[str, object]:
    return build_run_control_queue_overview(metadata_source).to_dict()


def run_control_queue_detail_payload(metadata_source: dict[str, object], queue_id: str) -> dict[str, object] | None:
    detail = build_run_control_queue_detail(metadata_source, queue_id)
    if detail is None:
        return None
    return {
        "schema_version": METADATA_SCHEMA_VERSION,
        "generated_at": METADATA_GENERATED_AT,
        "status": "ok",
        "mode": "run_control_queue_detail",
        "source": dict(metadata_source),
        "entry": detail,
        "writes_enabled": False,
        "execution_enabled": False,
        "execution_performed": False,
    }


def build_run_control_queue_overview(metadata_source: dict[str, object]) -> RunControlQueueOverview:
    source = dict(metadata_source)
    if source.get("storage_kind") != "sqlite" or not source.get("path"):
        return RunControlQueueOverview(
            status="ok",
            source=source,
            entries=(),
            issues=(
                RunControlQueueOverviewIssue(
                    code="run_control_queue_not_configured",
                    severity="info",
                    message="run control queue requires an explicit SQLite metadata source",
                ),
            ),
        )

    db_path = Path(str(source["path"]))
    if not db_path.is_file():
        return RunControlQueueOverview(
            status="warning",
            source=source,
            entries=(),
            issues=(
                RunControlQueueOverviewIssue(
                    code="run_control_queue_db_missing",
                    severity="warning",
                    message=f"run control queue database does not exist: {db_path}",
                ),
            ),
        )

    try:
        queue_result = list_run_control_queue(db_path).to_dict()
    except MetadataImportError as exc:
        is_uninitialized = _is_uninitialized_queue(str(exc))
        return RunControlQueueOverview(
            status="ok" if is_uninitialized else "warning",
            source=source,
            entries=(),
            issues=(
                RunControlQueueOverviewIssue(
                    code="run_control_queue_not_initialized"
                    if is_uninitialized
                    else "run_control_queue_unreadable",
                    severity="info" if is_uninitialized else "warning",
                    message=str(exc),
                ),
            ),
        )

    entries = tuple(entry for entry in queue_result.get("entries", ()) if isinstance(entry, dict))
    return RunControlQueueOverview(
        status="ok",
        source=source,
        entries=entries,
    )


def build_run_control_queue_detail(metadata_source: dict[str, object], queue_id: str) -> dict[str, object] | None:
    source = dict(metadata_source)
    if not queue_id.strip() or source.get("storage_kind") != "sqlite" or not source.get("path"):
        return None

    db_path = Path(str(source["path"]))
    if not db_path.is_file():
        return None

    try:
        result = get_run_control_queue_entry(queue_id, db_path=db_path).to_dict()
    except MetadataImportError:
        return None

    entry = result.get("entry")
    return entry if isinstance(entry, dict) else None


def _is_uninitialized_queue(message: str) -> bool:
    return "no such table: run_control_queue" in message
