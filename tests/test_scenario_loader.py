"""Tests for the minimal JSON scenario loader."""

from pathlib import Path

import pytest

from ims.io.scenario_loader import ScenarioValidationError, load_scenario


def test_load_scenario_builds_generic_simulation_context() -> None:
    fixture_path = Path(__file__).parent / "fixtures" / "minimal_scenario.json"

    context = load_scenario(fixture_path)

    assert context.max_periods == 12
    assert context.rng_seed == 42
    assert context.registries["source"] == "scenario_loader"
    assert len(context.stores["bavs"]) == 1
    assert context.stores["policyholders"][0].insurer_id == "ins-1"


def test_load_scenario_rejects_missing_required_context_field(tmp_path: Path) -> None:
    broken_scenario = tmp_path / "broken.json"
    broken_scenario.write_text('{"context": {"period": 0}, "entities": {}}', encoding="utf-8")

    with pytest.raises(ScenarioValidationError, match="max_periods"):
        load_scenario(broken_scenario)
