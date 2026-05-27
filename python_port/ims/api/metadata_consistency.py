from __future__ import annotations

from ims.api.metadata import METADATA_GENERATED_AT, METADATA_SCHEMA_VERSION


def metadata_consistency_payload(
    scenarios_response: dict[str, object],
    runs_response: dict[str, object],
    capabilities: dict[str, object],
) -> dict[str, object]:
    scenarios = _items(scenarios_response)
    runs = _items(runs_response)
    scenario_ids = {str(scenario.get("id", "")) for scenario in scenarios}
    missing_reference_runs = [
        str(run.get("id", ""))
        for run in runs
        if str(run.get("scenario_id", "")) not in scenario_ids
    ]
    execution_enabled_runs = [
        str(run.get("id", ""))
        for run in runs
        if bool(run.get("execution_enabled"))
    ]
    scenario_writes_enabled = _enabled(capabilities, "writes", "scenario_metadata")
    run_writes_enabled = _enabled(capabilities, "writes", "run_metadata")
    simulation_enabled = _enabled(capabilities, "simulation_execution")
    issue_count = len(missing_reference_runs) + len(execution_enabled_runs)
    if scenario_writes_enabled or run_writes_enabled:
        issue_count += 1
    if simulation_enabled:
        issue_count += 1

    return {
        "schema_version": METADATA_SCHEMA_VERSION,
        "generated_at": METADATA_GENERATED_AT,
        "status": "ok" if issue_count == 0 else "warning",
        "scenario_count": len(scenarios),
        "run_count": len(runs),
        "runs_with_known_scenario": len(runs) - len(missing_reference_runs),
        "runs_with_missing_scenario": missing_reference_runs,
        "runs_with_execution_enabled": execution_enabled_runs,
        "writes_enabled": scenario_writes_enabled or run_writes_enabled,
        "simulation_enabled": simulation_enabled,
        "issue_count": issue_count,
    }


def _items(response: dict[str, object]) -> list[dict[str, object]]:
    items = response.get("items", [])
    if not isinstance(items, list):
        return []
    return [item for item in items if isinstance(item, dict)]


def _enabled(payload: dict[str, object], *path: str) -> bool:
    current: object = payload
    for key in path:
        if not isinstance(current, dict):
            return False
        current = current.get(key, {})
    if not isinstance(current, dict):
        return False
    return bool(current.get("enabled"))
