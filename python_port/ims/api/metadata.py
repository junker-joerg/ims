from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Literal


ScenarioState = Literal["reference", "draft", "planned"]
RunState = Literal["validated", "prepared", "planned"]


@dataclass(frozen=True)
class ScenarioMetadata:
    id: str
    name: str
    scope: str
    state: ScenarioState
    source: str
    notes: str


@dataclass(frozen=True)
class RunMetadata:
    id: str
    label: str
    scenario_id: str
    state: RunState
    period_window: str
    validation_scope: str


SCENARIOS: tuple[ScenarioMetadata, ...] = (
    ScenarioMetadata(
        id="agrsich-reference-window",
        name="Agrsich Referenzfenster",
        scope="VU/VN-Agrsich",
        state="reference",
        source="tests/fixtures",
        notes="Portierte Pfade mit begrenzten Legacy-Fenstern; keine Vollgleichheitsbehauptung.",
    ),
    ScenarioMetadata(
        id="local-workbench-draft",
        name="Lokaler Workbench-Entwurf",
        scope="Metadaten",
        state="draft",
        source="in-memory",
        notes="Vorbereitung fuer spaetere lokale Szenarioverwaltung.",
    ),
)

RUNS: tuple[RunMetadata, ...] = (
    RunMetadata(
        id="baseline-python-tests",
        label="Python-Regressionssuite",
        scenario_id="agrsich-reference-window",
        state="validated",
        period_window="portierte Referenzfenster",
        validation_scope="548 Tests",
    ),
    RunMetadata(
        id="workbench-shell-preview",
        label="Workbench-Shell Vorschau",
        scenario_id="local-workbench-draft",
        state="prepared",
        period_window="keine Simulation",
        validation_scope="Health/API/UI-Shell",
    ),
)


def list_scenario_metadata() -> list[dict[str, str]]:
    return [asdict(scenario) for scenario in SCENARIOS]


def list_run_metadata() -> list[dict[str, str]]:
    return [asdict(run) for run in RUNS]
