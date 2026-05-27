from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ims.api.metadata import (
    METADATA_SCHEMA_VERSION,
    MetadataSource,
    RunMetadata,
    ScenarioMetadata,
    ValidationSummary,
)
from ims.api.metadata_repository import MetadataValidationError, WorkbenchMetadataRepository


SCENARIO_STATUSES = {"reference", "draft", "planned"}
RUN_STATUSES = {"validated", "prepared", "planned"}
SOURCE_KINDS = {"fixture", "in_memory", "derived"}
VALIDATION_STATUSES = {"validated", "not_claimed", "planned"}


class MetadataImportError(ValueError):
    pass


@dataclass(frozen=True)
class MetadataImportBundle:
    scenarios: tuple[ScenarioMetadata, ...]
    runs: tuple[RunMetadata, ...]


@dataclass(frozen=True)
class MetadataImportResult:
    scenario_count: int
    run_count: int
    scenario_ids: tuple[str, ...]
    run_ids: tuple[str, ...]


def load_metadata_import(path: Path | str) -> MetadataImportBundle:
    try:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise MetadataImportError(f"metadata import JSON is invalid: {exc.msg}") from exc
    return parse_metadata_import_payload(payload)


def parse_metadata_import_payload(payload: object) -> MetadataImportBundle:
    if not isinstance(payload, dict):
        raise MetadataImportError("metadata import payload must be an object")
    schema_version = _required_text(payload, "schema_version")
    if schema_version != METADATA_SCHEMA_VERSION:
        raise MetadataImportError(f"schema_version must be {METADATA_SCHEMA_VERSION}")

    scenarios_payload = _required_list(payload, "scenarios")
    runs_payload = _required_list(payload, "runs")
    scenarios = tuple(_parse_scenario(item, f"scenarios[{index}]") for index, item in enumerate(scenarios_payload))
    runs = tuple(_parse_run(item, f"runs[{index}]") for index, item in enumerate(runs_payload))
    return MetadataImportBundle(scenarios=scenarios, runs=runs)


def import_metadata_file(path: Path | str, repository: WorkbenchMetadataRepository) -> MetadataImportResult:
    return import_metadata_bundle(load_metadata_import(path), repository)


def validate_metadata_bundle(
    bundle: MetadataImportBundle,
    repository: WorkbenchMetadataRepository,
) -> None:
    scenario_ids = _repository_scenario_ids(repository) | {scenario.id for scenario in bundle.scenarios}
    for run in bundle.runs:
        if run.scenario_id not in scenario_ids:
            raise MetadataImportError(f"run {run.id} references unknown scenario_id {run.scenario_id}")

    try:
        for scenario in bundle.scenarios:
            repository.validate_scenario(scenario)
        for run in bundle.runs:
            repository.validate_run(run)
    except MetadataValidationError as exc:
        raise MetadataImportError(str(exc)) from exc


def import_metadata_bundle(
    bundle: MetadataImportBundle,
    repository: WorkbenchMetadataRepository,
) -> MetadataImportResult:
    validate_metadata_bundle(bundle, repository)

    try:
        for scenario in bundle.scenarios:
            repository.upsert_scenario(scenario)
        for run in bundle.runs:
            repository.upsert_run(run)
    except MetadataValidationError as exc:
        raise MetadataImportError(str(exc)) from exc

    return MetadataImportResult(
        scenario_count=len(bundle.scenarios),
        run_count=len(bundle.runs),
        scenario_ids=tuple(scenario.id for scenario in bundle.scenarios),
        run_ids=tuple(run.id for run in bundle.runs),
    )


def _parse_scenario(payload: object, path: str) -> ScenarioMetadata:
    if not isinstance(payload, dict):
        raise MetadataImportError(f"{path} must be an object")
    source = _parse_source(payload.get("source"), f"{path}.source")
    validation = _parse_validation(payload.get("validation"), f"{path}.validation")
    status = _required_choice(payload, "status", SCENARIO_STATUSES, f"{path}.status")
    return ScenarioMetadata(
        id=_required_text(payload, "id", path),
        display_name=_required_text(payload, "display_name", path),
        status=status,  # type: ignore[arg-type]
        domain_scope=_required_text(payload, "domain_scope", path),
        source=source,
        validation=validation,
        updated_at=_required_text(payload, "updated_at", path),
        notes=_required_text(payload, "notes", path),
    )


def _parse_run(payload: object, path: str) -> RunMetadata:
    if not isinstance(payload, dict):
        raise MetadataImportError(f"{path} must be an object")
    source = _parse_source(payload.get("source"), f"{path}.source")
    validation = _parse_validation(payload.get("validation"), f"{path}.validation")
    status = _required_choice(payload, "status", RUN_STATUSES, f"{path}.status")
    execution_enabled = payload.get("execution_enabled")
    if not isinstance(execution_enabled, bool):
        raise MetadataImportError(f"{path}.execution_enabled must be a boolean")
    return RunMetadata(
        id=_required_text(payload, "id", path),
        display_name=_required_text(payload, "display_name", path),
        scenario_id=_required_text(payload, "scenario_id", path),
        status=status,  # type: ignore[arg-type]
        source=source,
        validation=validation,
        period_window=_required_text(payload, "period_window", path),
        execution_enabled=execution_enabled,
        updated_at=_required_text(payload, "updated_at", path),
    )


def _parse_source(payload: object, path: str) -> MetadataSource:
    if not isinstance(payload, dict):
        raise MetadataImportError(f"{path} must be an object")
    kind = _required_choice(payload, "kind", SOURCE_KINDS, f"{path}.kind")
    source_path = payload.get("path")
    if source_path is not None and not isinstance(source_path, str):
        raise MetadataImportError(f"{path}.path must be a string or null")
    return MetadataSource(
        kind=kind,  # type: ignore[arg-type]
        label=_required_text(payload, "label", path),
        path=source_path,
    )


def _parse_validation(payload: object, path: str) -> ValidationSummary:
    if not isinstance(payload, dict):
        raise MetadataImportError(f"{path} must be an object")
    status = _required_choice(payload, "status", VALIDATION_STATUSES, f"{path}.status")
    return ValidationSummary(
        status=status,  # type: ignore[arg-type]
        scope=_required_text(payload, "scope", path),
        claim=_required_text(payload, "claim", path),
    )


def _repository_scenario_ids(repository: WorkbenchMetadataRepository) -> set[str]:
    payload = repository.list_scenarios()
    items = payload.get("items")
    if not isinstance(items, list):
        raise MetadataImportError("repository scenario payload is invalid")
    return {item["id"] for item in items if isinstance(item, dict) and isinstance(item.get("id"), str)}


def _required_list(payload: dict[str, object], field_name: str) -> list[object]:
    value = payload.get(field_name)
    if not isinstance(value, list):
        raise MetadataImportError(f"{field_name} must be a list")
    return value


def _required_text(payload: dict[str, Any], field_name: str, path: str | None = None) -> str:
    value = payload.get(field_name)
    label = f"{path}.{field_name}" if path else field_name
    if not isinstance(value, str) or not value.strip():
        raise MetadataImportError(f"{label} must be a non-empty string")
    return value


def _required_choice(
    payload: dict[str, object],
    field_name: str,
    allowed: set[str],
    label: str,
) -> str:
    value = payload.get(field_name)
    if not isinstance(value, str) or value not in allowed:
        allowed_values = ", ".join(sorted(allowed))
        raise MetadataImportError(f"{label} must be one of: {allowed_values}")
    return value
