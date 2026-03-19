from pathlib import Path

import pytest

from ims.io.scenario_loader import LoadedScenario, ScenarioValidationError, load_scenario


def test_scenario_loader_loads_minimal_scenario() -> None:
    scenario = load_scenario(Path("tests/fixtures/minimal_scenario.json"))

    assert isinstance(scenario, LoadedScenario)
    assert scenario.context.max_periods == 12
    assert scenario.context.rng_seed == 123
    assert scenario.bav.entity_id == 100
    assert len(scenario.insurers) == 1
    assert scenario.insurers[0].name == "Muster-VU"
    assert len(scenario.policyholders) == 1
    assert scenario.policyholders[0].insurer_id == 200


def test_scenario_loader_raises_for_missing_file() -> None:
    with pytest.raises(FileNotFoundError):
        load_scenario("tests/fixtures/does_not_exist.json")


def test_scenario_loader_raises_for_invalid_top_level_shape(tmp_path: Path) -> None:
    invalid_path = tmp_path / "invalid.json"
    invalid_path.write_text('{"context": []}', encoding="utf-8")

    with pytest.raises(ScenarioValidationError, match="missing top-level field|context must be an object"):
        load_scenario(invalid_path)
