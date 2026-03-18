"""Load minimal JSON scenarios for the IMS Python port scaffold.

The loader only validates a small set of technical fields and builds a generic
`SimulationContext`. It intentionally avoids domain rules and market logic.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ims.engine.context import SimulationContext
from ims.model.entities import BAV, Insurer, Policyholder


REQUIRED_CONTEXT_FIELDS = {"max_periods"}


class ScenarioValidationError(ValueError):
    """Raised when a minimal scenario is structurally invalid."""


def load_scenario(path: str | Path) -> SimulationContext:
    """Load a minimal JSON scenario into a generic simulation context."""

    scenario_path = Path(path)
    payload = json.loads(scenario_path.read_text(encoding="utf-8"))
    return build_context_from_payload(payload)


def build_context_from_payload(payload: dict[str, Any]) -> SimulationContext:
    """Build a simulation context from parsed JSON payload data."""

    context_data = payload.get("context")
    if not isinstance(context_data, dict):
        raise ScenarioValidationError("scenario.context must be an object")

    missing_fields = sorted(REQUIRED_CONTEXT_FIELDS - context_data.keys())
    if missing_fields:
        raise ScenarioValidationError(
            f"scenario.context missing required fields: {', '.join(missing_fields)}"
        )

    entities = payload.get("entities", {})
    if not isinstance(entities, dict):
        raise ScenarioValidationError("scenario.entities must be an object")

    return SimulationContext(
        period=_as_int(context_data.get("period", 0), field_name="context.period"),
        logtime=_as_int(context_data.get("logtime", 0), field_name="context.logtime"),
        max_periods=_as_int(context_data["max_periods"], field_name="context.max_periods"),
        run_index=_as_int(context_data.get("run_index", 0), field_name="context.run_index"),
        rng_seed=_as_optional_int(context_data.get("rng_seed"), field_name="context.rng_seed"),
        registries={"source": "scenario_loader"},
        stores={
            "bavs": _load_bavs(entities.get("bavs", [])),
            "insurers": _load_insurers(entities.get("insurers", [])),
            "policyholders": _load_policyholders(entities.get("policyholders", [])),
        },
    )


def _load_bavs(raw_items: Any) -> list[BAV]:
    return [BAV(**_require_identified_item(item, kind="bavs")) for item in _require_list(raw_items, kind="bavs")]


def _load_insurers(raw_items: Any) -> list[Insurer]:
    return [Insurer(**_require_identified_item(item, kind="insurers")) for item in _require_list(raw_items, kind="insurers")]


def _load_policyholders(raw_items: Any) -> list[Policyholder]:
    result: list[Policyholder] = []
    for item in _require_list(raw_items, kind="policyholders"):
        normalized = _require_identified_item(item, kind="policyholders")
        result.append(
            Policyholder(
                identifier=normalized["identifier"],
                name=normalized["name"],
                insurer_id=item.get("insurer_id"),
                bav_id=item.get("bav_id"),
            )
        )
    return result


def _require_list(raw_items: Any, *, kind: str) -> list[dict[str, Any]]:
    if not isinstance(raw_items, list):
        raise ScenarioValidationError(f"scenario.entities.{kind} must be a list")
    return raw_items


def _require_identified_item(item: Any, *, kind: str) -> dict[str, str]:
    if not isinstance(item, dict):
        raise ScenarioValidationError(f"scenario.entities.{kind} items must be objects")
    identifier = item.get("identifier")
    name = item.get("name")
    if not isinstance(identifier, str) or not identifier:
        raise ScenarioValidationError(f"scenario.entities.{kind} items need a non-empty identifier")
    if not isinstance(name, str) or not name:
        raise ScenarioValidationError(f"scenario.entities.{kind} items need a non-empty name")
    return {"identifier": identifier, "name": name}


def _as_int(value: Any, *, field_name: str) -> int:
    if not isinstance(value, int):
        raise ScenarioValidationError(f"{field_name} must be an integer")
    return value


def _as_optional_int(value: Any, *, field_name: str) -> int | None:
    if value is None:
        return None
    return _as_int(value, field_name=field_name)
