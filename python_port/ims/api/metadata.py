from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Generic, Literal, TypeVar


METADATA_SCHEMA_VERSION = "ims.workbench.metadata.v1"
METADATA_GENERATED_AT = "2026-05-27T00:00:00Z"

ScenarioState = Literal["reference", "draft", "planned"]
RunState = Literal["validated", "prepared", "planned"]
ValidationStatus = Literal["validated", "not_claimed", "planned"]
SourceKind = Literal["fixture", "in_memory", "derived"]

T = TypeVar("T")


@dataclass(frozen=True)
class MetadataSource:
    kind: SourceKind
    label: str
    path: str | None = None


@dataclass(frozen=True)
class ValidationSummary:
    status: ValidationStatus
    scope: str
    claim: str


@dataclass(frozen=True)
class ScenarioMetadata:
    id: str
    display_name: str
    status: ScenarioState
    domain_scope: str
    source: MetadataSource
    validation: ValidationSummary
    updated_at: str
    notes: str


@dataclass(frozen=True)
class RunMetadata:
    id: str
    display_name: str
    scenario_id: str
    status: RunState
    source: MetadataSource
    validation: ValidationSummary
    period_window: str
    execution_enabled: bool
    updated_at: str


@dataclass(frozen=True)
class MetadataResponse(Generic[T]):
    schema_version: str
    generated_at: str
    items: tuple[T, ...]


SCENARIOS: tuple[ScenarioMetadata, ...] = (
    ScenarioMetadata(
        id="agrsich-reference-window",
        display_name="Agrsich Referenzfenster",
        status="reference",
        domain_scope="VU/VN-Agrsich",
        source=MetadataSource(
            kind="fixture",
            label="Portierte Referenzfixtures",
            path="tests/fixtures",
        ),
        validation=ValidationSummary(
            status="validated",
            scope="portierte Referenzfenster",
            claim="Validiert nur konkret portierte Pfade; keine historische Vollgleichheit.",
        ),
        updated_at="2026-05-27T00:00:00Z",
        notes="Portierte Pfade mit begrenzten Legacy-Fenstern.",
    ),
    ScenarioMetadata(
        id="local-workbench-draft",
        display_name="Lokaler Workbench-Entwurf",
        status="draft",
        domain_scope="Metadaten",
        source=MetadataSource(
            kind="in_memory",
            label="Statische Workbench-Metadaten",
        ),
        validation=ValidationSummary(
            status="planned",
            scope="keine Fachvalidierung",
            claim="Vorbereitung fuer spaetere lokale Szenarioverwaltung.",
        ),
        updated_at="2026-05-27T00:00:00Z",
        notes="Noch keine Persistenz und keine Schreibendpunkte.",
    ),
)

RUNS: tuple[RunMetadata, ...] = (
    RunMetadata(
        id="baseline-python-tests",
        display_name="Python-Regressionssuite",
        scenario_id="agrsich-reference-window",
        status="validated",
        source=MetadataSource(
            kind="derived",
            label="Lokaler Testlauf",
        ),
        validation=ValidationSummary(
            status="validated",
            scope="548 Tests",
            claim="Regressionssuite fuer portierte Pfade und Workbench-Adapter.",
        ),
        period_window="portierte Referenzfenster",
        execution_enabled=False,
        updated_at="2026-05-27T00:00:00Z",
    ),
    RunMetadata(
        id="workbench-shell-preview",
        display_name="Workbench-Shell Vorschau",
        scenario_id="local-workbench-draft",
        status="prepared",
        source=MetadataSource(
            kind="in_memory",
            label="Lokale Browser-Vorschau",
        ),
        validation=ValidationSummary(
            status="planned",
            scope="Health/API/UI-Shell",
            claim="Keine Simulation und keine Persistenz.",
        ),
        period_window="keine Simulation",
        execution_enabled=False,
        updated_at="2026-05-27T00:00:00Z",
    ),
)


def scenario_metadata_response() -> MetadataResponse[ScenarioMetadata]:
    return MetadataResponse(
        schema_version=METADATA_SCHEMA_VERSION,
        generated_at=METADATA_GENERATED_AT,
        items=SCENARIOS,
    )


def run_metadata_response() -> MetadataResponse[RunMetadata]:
    return MetadataResponse(
        schema_version=METADATA_SCHEMA_VERSION,
        generated_at=METADATA_GENERATED_AT,
        items=RUNS,
    )


def metadata_response_to_dict(response: MetadataResponse[T]) -> dict[str, object]:
    payload = asdict(response)
    payload["items"] = list(payload["items"])
    return payload


def list_scenario_metadata() -> dict[str, object]:
    return metadata_response_to_dict(scenario_metadata_response())


def list_run_metadata() -> dict[str, object]:
    return metadata_response_to_dict(run_metadata_response())
