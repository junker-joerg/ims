from pathlib import Path

import pytest

from ims.io.scenario_loader import LoadedScenario, ScenarioValidationError, load_scenario, load_scenario_from_mapping


def test_scenario_loader_loads_minimal_scenario(minimal_scenario_path: Path) -> None:
    scenario = load_scenario(minimal_scenario_path)

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
        load_scenario(Path(__file__).resolve().parent / "fixtures" / "does_not_exist.json")


def test_scenario_loader_raises_for_invalid_top_level_shape(tmp_path: Path) -> None:
    invalid_path = tmp_path / "invalid.json"
    invalid_path.write_text('{"context": []}', encoding="utf-8")

    with pytest.raises(ScenarioValidationError, match="missing top-level field|context must be an object"):
        load_scenario(invalid_path)


def test_scenario_loader_reads_sector_specific_previous_frmdinf_inputs() -> None:
    scenario = load_scenario_from_mapping(
        {
            "context": {"period": 2, "max_periods": 3},
            "bav": {"entity_id": 1, "name": "BAV"},
            "insurers": [
                {
                    "entity_id": 10,
                    "name": "VU",
                    "premiums_prev": 99.0,
                    "advertising_prev": 99.0,
                    "reserves_prev": 99.0,
                    "premiums_prev_sector": [11.0, 22.0],
                    "advertising_prev_sector": [3.0, 4.0],
                    "reserves_prev_sector": [50.0, 60.0],
                }
            ],
            "policyholders": [
                {
                    "entity_id": 20,
                    "name": "VN",
                    "insured_prev": 0.0,
                    "insured_prev_sector": [1.0, 0.0],
                }
            ],
        }
    )

    assert scenario.insurers[0].premiums_prev_sector == [11.0, 22.0]
    assert scenario.insurers[0].advertising_prev_sector == [3.0, 4.0]
    assert scenario.insurers[0].reserves_prev_sector == [50.0, 60.0]
    assert scenario.policyholders[0].insured_prev_sector == [1.0, 0.0]


def test_scenario_loader_reads_sector_specific_current_vu_rule_inputs() -> None:
    scenario = load_scenario_from_mapping(
        {
            "context": {"period": 2, "max_periods": 3},
            "bav": {"entity_id": 1, "name": "BAV"},
            "insurers": [
                {
                    "entity_id": 10,
                    "name": "VU",
                    "premiums_current": 99.0,
                    "advertising_current": 88.0,
                    "premiums_current_sector": [11.0, 22.0],
                    "advertising_current_sector": [3.0, 4.0],
                }
            ],
            "policyholders": [],
        }
    )

    assert scenario.insurers[0].premiums_current_sector == [11.0, 22.0]
    assert scenario.insurers[0].advertising_current_sector == [3.0, 4.0]


def test_scenario_loader_duplicates_scalar_current_vu_rule_inputs_for_compatibility() -> None:
    scenario = load_scenario_from_mapping(
        {
            "context": {"period": 2, "max_periods": 3},
            "bav": {"entity_id": 1, "name": "BAV"},
            "insurers": [
                {
                    "entity_id": 10,
                    "name": "VU",
                    "premiums_current": 12.0,
                    "advertising_current": 5.0,
                }
            ],
            "policyholders": [],
        }
    )

    assert scenario.insurers[0].premiums_current_sector == [12.0, 12.0]
    assert scenario.insurers[0].advertising_current_sector == [5.0, 5.0]


def test_scenario_loader_reads_optional_vu_foreign_info_rule_snapshots() -> None:
    scenario = load_scenario_from_mapping(
        {
            "context": {"period": 2, "max_periods": 3},
            "bav": {"entity_id": 1, "name": "BAV"},
            "insurers": [{"entity_id": 10, "name": "VU"}],
            "policyholders": [],
            "vu_foreign_info_rule_snapshots": [
                {
                    "insurer_id": 10,
                    "rule_kind": "dumping",
                    "interest_rate": 0.04,
                    "change_shock": True,
                    "parameters": {
                        "premium_intercept_normal": [1.0, 2.0],
                        "premium_factor_normal": [0.5, 0.25],
                        "advertising_intercept_normal": [3.0, 4.0],
                        "advertising_factor_normal": [0.1, 0.2],
                        "premium_intercept_shock": [10.0, 20.0],
                        "premium_factor_shock": [1.0, 2.0],
                        "advertising_intercept_shock": [30.0, 40.0],
                        "advertising_factor_shock": [3.0, 4.0],
                    },
                }
            ],
        }
    )

    assert len(scenario.vu_foreign_info_rule_snapshots) == 1
    snapshot = scenario.vu_foreign_info_rule_snapshots[0]
    assert snapshot.insurer_id == 10
    assert snapshot.rule_kind == "dumping"
    assert snapshot.interest_rate == 0.04
    assert snapshot.change_shock is True
    assert snapshot.parameters.premium_factor_normal == [0.5, 0.25]
