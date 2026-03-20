from dataclasses import dataclass
import json
from pathlib import Path

from ims.engine.context import SimulationContext
from ims.model.entities import BAV, Insurer, Policyholder


@dataclass(slots=True)
class LoadedScenario:
    """Minimales Ergebnis eines geladenen Szenarios."""

    context: SimulationContext
    bav: BAV
    insurers: list[Insurer]
    policyholders: list[Policyholder]


class ScenarioValidationError(ValueError):
    """Signalisiert ein grob ungültiges Szenarioformat."""


def load_scenario(path: str | Path) -> LoadedScenario:
    scenario_path = Path(path)
    with scenario_path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)

    if not isinstance(data, dict):
        raise ScenarioValidationError("scenario must be a JSON object")

    try:
        context_data = data["context"]
        bav_data = data["bav"]
        insurer_items = data["insurers"]
        policyholder_items = data["policyholders"]
    except KeyError as exc:
        raise ScenarioValidationError(f"missing top-level field: {exc.args[0]}") from exc

    if not isinstance(context_data, dict):
        raise ScenarioValidationError("context must be an object")
    if not isinstance(bav_data, dict):
        raise ScenarioValidationError("bav must be an object")
    if not isinstance(insurer_items, list) or not isinstance(policyholder_items, list):
        raise ScenarioValidationError("insurers and policyholders must be lists")

    context = SimulationContext(
        period=int(context_data.get("period", 0)),
        logtime=int(context_data.get("logtime", 0)),
        max_periods=int(context_data["max_periods"]),
        run_index=int(context_data.get("run_index", 0)),
        rng_seed=int(context_data.get("rng_seed", 0)),
    )
    bav = BAV(
        entity_id=int(bav_data["entity_id"]),
        active=bool(bav_data.get("active", True)),
        name=str(bav_data["name"]),
    )
    insurers = [
        Insurer(
            entity_id=int(item["entity_id"]),
            active=bool(item.get("active", True)),
            name=str(item["name"]),
            premiums_prev=float(item.get("premiums_prev", 0.0)),
            advertising_prev=float(item.get("advertising_prev", 0.0)),
            reserves_prev=float(item.get("reserves_prev", 0.0)),
        )
        for item in insurer_items
    ]
    policyholders = [
        Policyholder(
            entity_id=int(item["entity_id"]),
            active=bool(item.get("active", True)),
            name=str(item["name"]),
            insurer_id=int(item["insurer_id"]) if item.get("insurer_id") is not None else None,
            insured_prev=float(item.get("insured_prev", 0.0)),
        )
        for item in policyholder_items
    ]
    return LoadedScenario(
        context=context,
        bav=bav,
        insurers=insurers,
        policyholders=policyholders,
    )
