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


def test_scenario_loader_rejects_non_object_insurer_entries() -> None:
    with pytest.raises(ScenarioValidationError, match="insurer entries must be objects: index 0"):
        load_scenario_from_mapping(
            {
                "context": {"period": 2, "max_periods": 3},
                "bav": {"entity_id": 1, "name": "BAV"},
                "insurers": ["VU-10"],
                "policyholders": [],
            }
        )


def test_scenario_loader_rejects_policyholder_entries_without_entity_id() -> None:
    with pytest.raises(ScenarioValidationError, match="policyholder entries require field: entity_id at index 0"):
        load_scenario_from_mapping(
            {
                "context": {"period": 2, "max_periods": 3},
                "bav": {"entity_id": 1, "name": "BAV"},
                "insurers": [],
                "policyholders": [{"name": "VN ohne ID"}],
            }
        )


def test_scenario_loader_rejects_duplicate_insurer_entity_ids() -> None:
    with pytest.raises(ScenarioValidationError, match="duplicate insurer entity_id values: 10"):
        load_scenario_from_mapping(
            {
                "context": {"period": 2, "max_periods": 3},
                "bav": {"entity_id": 1, "name": "BAV"},
                "insurers": [
                    {"entity_id": 10, "name": "VU-10-a"},
                    {"entity_id": 10, "name": "VU-10-b"},
                ],
                "policyholders": [],
            }
        )


def test_scenario_loader_rejects_duplicate_policyholder_entity_ids() -> None:
    with pytest.raises(ScenarioValidationError, match="duplicate policyholder entity_id values: 20"):
        load_scenario_from_mapping(
            {
                "context": {"period": 2, "max_periods": 3},
                "bav": {"entity_id": 1, "name": "BAV"},
                "insurers": [],
                "policyholders": [
                    {"entity_id": 20, "name": "VN-20-a"},
                    {"entity_id": 20, "name": "VN-20-b"},
                ],
            }
        )


def test_scenario_loader_rejects_unknown_policyholder_insurer_reference() -> None:
    with pytest.raises(ScenarioValidationError, match="policyholder insurer_id references unknown insurers: 99"):
        load_scenario_from_mapping(
            {
                "context": {"period": 2, "max_periods": 3},
                "bav": {"entity_id": 1, "name": "BAV"},
                "insurers": [{"entity_id": 10, "name": "VU-10"}],
                "policyholders": [
                    {"entity_id": 20, "name": "VN-20", "insurer_id": 99},
                ],
            }
        )


def test_scenario_loader_allows_unassigned_policyholder() -> None:
    scenario = load_scenario_from_mapping(
        {
            "context": {"period": 2, "max_periods": 3},
            "bav": {"entity_id": 1, "name": "BAV"},
            "insurers": [{"entity_id": 10, "name": "VU-10"}],
            "policyholders": [
                {"entity_id": 20, "name": "VN-20", "insurer_id": None},
            ],
        }
    )

    assert scenario.policyholders[0].insurer_id is None
    assert scenario.policyholders[0].chosen_insurer_current is None


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
                    "policyholders_current": 77.0,
                    "premiums_current_sector": [11.0, 22.0],
                    "advertising_current_sector": [3.0, 4.0],
                    "policyholders_current_sector": [5.0, 6.0],
                }
            ],
            "policyholders": [],
        }
    )

    assert scenario.insurers[0].premiums_current_sector == [11.0, 22.0]
    assert scenario.insurers[0].advertising_current_sector == [3.0, 4.0]
    assert scenario.insurers[0].policyholders_current_sector == [5.0, 6.0]


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
    assert scenario.insurers[0].policyholders_current_sector == [0.0, 0.0]


def test_scenario_loader_duplicates_scalar_current_policyholders_for_compatibility() -> None:
    scenario = load_scenario_from_mapping(
        {
            "context": {"period": 2, "max_periods": 3},
            "bav": {"entity_id": 1, "name": "BAV"},
            "insurers": [
                {
                    "entity_id": 10,
                    "name": "VU",
                    "policyholders_current": 12.0,
                }
            ],
            "policyholders": [],
        }
    )

    assert scenario.insurers[0].policyholders_current_sector == [12.0, 12.0]


def test_scenario_loader_reads_sector_specific_current_policyholder_status() -> None:
    scenario = load_scenario_from_mapping(
        {
            "context": {"period": 2, "max_periods": 3},
            "bav": {"entity_id": 1, "name": "BAV"},
            "insurers": [],
            "policyholders": [
                {
                    "entity_id": 20,
                    "name": "VN",
                    "insured_current": 0.5,
                    "insured_current_sector": [1.0, 0.0],
                }
            ],
        }
    )

    assert scenario.policyholders[0].insured_current == 0.5
    assert scenario.policyholders[0].insured_current_sector == [1.0, 0.0]


def test_scenario_loader_duplicates_scalar_current_policyholder_status_for_compatibility() -> None:
    scenario = load_scenario_from_mapping(
        {
            "context": {"period": 2, "max_periods": 3},
            "bav": {"entity_id": 1, "name": "BAV"},
            "insurers": [],
            "policyholders": [
                {
                    "entity_id": 20,
                    "name": "VN",
                    "insured_current": 0.5,
                }
            ],
        }
    )

    assert scenario.policyholders[0].insured_current_sector == [0.5, 0.5]


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


def test_scenario_loader_reads_optional_vu_random_rule_snapshots() -> None:
    scenario = load_scenario_from_mapping(
        {
            "context": {"period": 2, "max_periods": 3},
            "bav": {"entity_id": 1, "name": "BAV"},
            "insurers": [{"entity_id": 10, "name": "VU"}, {"entity_id": 11, "name": "VU-11"}],
            "policyholders": [],
            "vu_random_uniform_rule_snapshots": [
                {
                    "insurer_id": 10,
                    "random_draws": [0.1, 0.2, 0.3, 0.4],
                    "interest_rate": 0.04,
                    "change_shock": True,
                    "parameters": {
                        "premium_factor_normal": [10.0, 20.0],
                        "advertising_factor_normal": [30.0, 40.0],
                        "premium_factor_shock": [50.0, 60.0],
                        "advertising_factor_shock": [70.0, 80.0],
                    },
                }
            ],
            "vu_random_normal_rule_snapshots": [
                {
                    "insurer_id": 11,
                    "normal_draws": [0.1, -0.2, 0.3, -0.4],
                    "parameters": {
                        "premium_intercept_normal": [1.0, 2.0],
                        "premium_factor_normal": [10.0, 20.0],
                        "advertising_intercept_normal": [3.0, 4.0],
                        "advertising_factor_normal": [30.0, 40.0],
                        "premium_intercept_shock": [5.0, 6.0],
                        "premium_factor_shock": [50.0, 60.0],
                        "advertising_intercept_shock": [7.0, 8.0],
                        "advertising_factor_shock": [70.0, 80.0],
                    },
                }
            ],
        }
    )

    assert len(scenario.vu_random_uniform_rule_snapshots) == 1
    assert scenario.vu_random_uniform_rule_snapshots[0].random_draws == [0.1, 0.2, 0.3, 0.4]
    assert scenario.vu_random_uniform_rule_snapshots[0].change_shock is True
    assert len(scenario.vu_random_normal_rule_snapshots) == 1
    assert scenario.vu_random_normal_rule_snapshots[0].normal_draws == [0.1, -0.2, 0.3, -0.4]


def test_scenario_loader_reads_optional_vu_market_share_markup_rule_snapshots() -> None:
    scenario = load_scenario_from_mapping(
        {
            "context": {"period": 2, "max_periods": 3},
            "bav": {"entity_id": 1, "name": "BAV"},
            "insurers": [{"entity_id": 10, "name": "VU"}],
            "policyholders": [],
            "vu_market_share_markup_rule_snapshots": [
                {
                    "insurer_id": 10,
                    "market_share_thresholds": [0.4, 0.7],
                    "active_policyholder_count": 100,
                    "interest_rate": 0.04,
                    "change_shock": True,
                    "parameters": {
                        "premium_below_normal": [1.1, 1.2],
                        "premium_above_normal": [0.9, 0.8],
                        "advertising_below_normal": [1.3, 1.4],
                        "advertising_above_normal": [0.7, 0.6],
                        "premium_below_shock": [2.1, 2.2],
                        "premium_above_shock": [1.9, 1.8],
                        "advertising_below_shock": [2.3, 2.4],
                        "advertising_above_shock": [1.7, 1.6],
                    },
                }
            ],
        }
    )

    assert len(scenario.vu_market_share_markup_rule_snapshots) == 1
    snapshot = scenario.vu_market_share_markup_rule_snapshots[0]
    assert snapshot.insurer_id == 10
    assert snapshot.market_share_thresholds == [0.4, 0.7]
    assert snapshot.active_policyholder_count == 100
    assert snapshot.interest_rate == 0.04
    assert snapshot.change_shock is True


def test_scenario_loader_reads_optional_vu_net_switcher_markup_rule_snapshots() -> None:
    scenario = load_scenario_from_mapping(
        {
            "context": {"period": 3, "max_periods": 4},
            "bav": {"entity_id": 1, "name": "BAV"},
            "insurers": [{"entity_id": 10, "name": "VU"}],
            "policyholders": [],
            "vu_net_switcher_markup_rule_snapshots": [
                {
                    "insurer_id": 10,
                    "net_switcher_thresholds": [5.0, 10.0],
                    "previous_policyholders_sector": [20.0, 75.0],
                    "interest_rate": 0.04,
                    "change_shock": True,
                    "parameters": {
                        "premium_below_normal": [1.1, 1.2],
                        "premium_above_normal": [0.9, 0.8],
                        "advertising_below_normal": [1.3, 1.4],
                        "advertising_above_normal": [0.7, 0.6],
                        "premium_below_shock": [2.1, 2.2],
                        "premium_above_shock": [1.9, 1.8],
                        "advertising_below_shock": [2.3, 2.4],
                        "advertising_above_shock": [1.7, 1.6],
                    },
                }
            ],
        }
    )

    assert len(scenario.vu_net_switcher_markup_rule_snapshots) == 1
    snapshot = scenario.vu_net_switcher_markup_rule_snapshots[0]
    assert snapshot.insurer_id == 10
    assert snapshot.net_switcher_thresholds == [5.0, 10.0]
    assert snapshot.previous_policyholders_sector == [20.0, 75.0]
    assert snapshot.interest_rate == 0.04
    assert snapshot.change_shock is True


def test_scenario_loader_reads_optional_vu_free_linear_rule_snapshots() -> None:
    scenario = load_scenario_from_mapping(
        {
            "context": {"period": 2, "max_periods": 3},
            "bav": {"entity_id": 1, "name": "BAV"},
            "insurers": [{"entity_id": 10, "name": "VU"}],
            "policyholders": [],
            "vu_free_linear_rule_snapshots": [
                {
                    "insurer_id": 10,
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

    assert len(scenario.vu_free_linear_rule_snapshots) == 1
    snapshot = scenario.vu_free_linear_rule_snapshots[0]
    assert snapshot.insurer_id == 10
    assert snapshot.interest_rate == 0.04
    assert snapshot.change_shock is True
    assert snapshot.parameters.premium_factor_normal == [0.5, 0.25]


def test_scenario_loader_reads_optional_vn_settlement_snapshots() -> None:
    scenario = load_scenario_from_mapping(
        {
            "context": {"period": 2, "max_periods": 3},
            "bav": {"entity_id": 1, "name": "BAV"},
            "insurers": [{"entity_id": 10, "name": "VU"}],
            "policyholders": [{"entity_id": 20, "name": "VN"}],
            "vn_settlement_snapshots": [
                {
                    "policyholder_id": 20,
                    "previous_wealth": 100.0,
                    "previous_wealth_sector": [60.0, 40.0],
                    "decisions": [
                        {"sector_index": 0, "insured": True, "insurer_id": 10, "premium": 5.0, "damage": 2.0},
                        {"sector_index": 1, "insured": False, "damage": 3.0},
                    ],
                }
            ],
        }
    )

    assert len(scenario.vn_settlement_snapshots) == 1
    snapshot = scenario.vn_settlement_snapshots[0]
    assert snapshot.policyholder_id == 20
    assert snapshot.previous_wealth == 100.0
    assert snapshot.previous_wealth_sector == [60.0, 40.0]
    assert snapshot.decisions[0].insurer_id == 10
    assert snapshot.decisions[1].insured is False


def test_scenario_loader_reads_optional_vn_damage_settlement_snapshots() -> None:
    scenario = load_scenario_from_mapping(
        {
            "context": {"period": 2, "max_periods": 3},
            "bav": {"entity_id": 1, "name": "BAV"},
            "insurers": [{"entity_id": 10, "name": "VU"}],
            "policyholders": [{"entity_id": 20, "name": "VN"}],
            "vn_damage_settlement_snapshots": [
                {
                    "policyholder_id": 20,
                    "previous_wealth": 100.0,
                    "previous_wealth_sector": [60.0],
                    "damage_thresholds": [0.7, 0.4],
                    "parameters": {
                        "damage_intercept_normal": [1.0, 2.0],
                        "damage_factor_normal": [3.0, 4.0],
                        "damage_intercept_shock": [5.0, 6.0],
                        "damage_factor_shock": [7.0, 8.0],
                    },
                    "draws": {
                        "trigger_draws": [0.1, 0.2],
                        "amount_draws": [0.3, 0.4],
                    },
                    "insurance_decisions": [
                        {"sector_index": 0, "insured": True, "insurer_id": 10, "premium": 5.0},
                        {"sector_index": 1, "insured": False},
                    ],
                }
            ],
        }
    )

    assert len(scenario.vn_damage_settlement_snapshots) == 1
    snapshot = scenario.vn_damage_settlement_snapshots[0]
    assert snapshot.policyholder_id == 20
    assert snapshot.previous_wealth_sector == [60.0, 60.0]
    assert snapshot.parameters.damage_factor_normal == [3.0, 4.0]
    assert snapshot.draws.trigger_draws == [0.1, 0.2]
    assert snapshot.insurance_decisions[0].insurer_id == 10


def test_scenario_loader_rejects_unknown_vn_settlement_references() -> None:
    with pytest.raises(ScenarioValidationError, match="unknown insurers: 99"):
        load_scenario_from_mapping(
            {
                "context": {"period": 2, "max_periods": 3},
                "bav": {"entity_id": 1, "name": "BAV"},
                "insurers": [{"entity_id": 10, "name": "VU"}],
                "policyholders": [{"entity_id": 20, "name": "VN"}],
                "vn_settlement_snapshots": [
                    {
                        "policyholder_id": 20,
                        "previous_wealth": 100.0,
                        "decisions": [
                            {"sector_index": 0, "insured": True, "insurer_id": 99, "damage": 2.0},
                            {"sector_index": 1, "insured": False, "damage": 3.0},
                        ],
                    }
                ],
            }
        )

    with pytest.raises(ScenarioValidationError, match="unknown policyholders: 21"):
        load_scenario_from_mapping(
            {
                "context": {"period": 2, "max_periods": 3},
                "bav": {"entity_id": 1, "name": "BAV"},
                "insurers": [{"entity_id": 10, "name": "VU"}],
                "policyholders": [{"entity_id": 20, "name": "VN"}],
                "vn_settlement_snapshots": [
                    {
                        "policyholder_id": 21,
                        "previous_wealth": 100.0,
                        "decisions": [
                            {"sector_index": 0, "insured": False, "damage": 2.0},
                            {"sector_index": 1, "insured": False, "damage": 3.0},
                        ],
                    }
                ],
            }
        )


def test_scenario_loader_rejects_unknown_vn_damage_settlement_references() -> None:
    with pytest.raises(ScenarioValidationError, match="unknown insurers: 99"):
        load_scenario_from_mapping(
            {
                "context": {"period": 2, "max_periods": 3},
                "bav": {"entity_id": 1, "name": "BAV"},
                "insurers": [{"entity_id": 10, "name": "VU"}],
                "policyholders": [{"entity_id": 20, "name": "VN"}],
                "vn_damage_settlement_snapshots": [
                    {
                        "policyholder_id": 20,
                        "previous_wealth": 100.0,
                        "damage_thresholds": [0.7, 0.4],
                        "parameters": {
                            "damage_intercept_normal": [1.0, 2.0],
                            "damage_factor_normal": [3.0, 4.0],
                            "damage_intercept_shock": [5.0, 6.0],
                            "damage_factor_shock": [7.0, 8.0],
                        },
                        "draws": {
                            "trigger_draws": [0.1, 0.2],
                            "amount_draws": [0.3, 0.4],
                        },
                        "insurance_decisions": [
                            {"sector_index": 0, "insured": True, "insurer_id": 99},
                            {"sector_index": 1, "insured": False},
                        ],
                    }
                ],
            }
        )


def test_scenario_loader_rejects_overlapping_vn_snapshot_targets() -> None:
    with pytest.raises(ScenarioValidationError, match="must target disjoint policyholders: 20"):
        load_scenario_from_mapping(
            {
                "context": {"period": 2, "max_periods": 3},
                "bav": {"entity_id": 1, "name": "BAV"},
                "insurers": [{"entity_id": 10, "name": "VU"}],
                "policyholders": [{"entity_id": 20, "name": "VN"}],
                "vn_damage_settlement_snapshots": [
                    {
                        "policyholder_id": 20,
                        "previous_wealth": 100.0,
                        "damage_thresholds": [0.7, 0.4],
                        "parameters": {
                            "damage_intercept_normal": [1.0, 2.0],
                            "damage_factor_normal": [3.0, 4.0],
                            "damage_intercept_shock": [5.0, 6.0],
                            "damage_factor_shock": [7.0, 8.0],
                        },
                        "draws": {
                            "trigger_draws": [0.1, 0.2],
                            "amount_draws": [0.3, 0.4],
                        },
                        "insurance_decisions": [
                            {"sector_index": 0, "insured": True, "insurer_id": 10},
                            {"sector_index": 1, "insured": False},
                        ],
                    }
                ],
                "vn_settlement_snapshots": [
                    {
                        "policyholder_id": 20,
                        "previous_wealth": 100.0,
                        "decisions": [
                            {"sector_index": 0, "insured": False, "damage": 1.0},
                            {"sector_index": 1, "insured": False, "damage": 2.0},
                        ],
                    }
                ],
            }
        )

    with pytest.raises(ScenarioValidationError, match="unknown policyholders: 21"):
        load_scenario_from_mapping(
            {
                "context": {"period": 2, "max_periods": 3},
                "bav": {"entity_id": 1, "name": "BAV"},
                "insurers": [{"entity_id": 10, "name": "VU"}],
                "policyholders": [{"entity_id": 20, "name": "VN"}],
                "vn_damage_settlement_snapshots": [
                    {
                        "policyholder_id": 21,
                        "previous_wealth": 100.0,
                        "damage_thresholds": [0.7, 0.4],
                        "parameters": {
                            "damage_intercept_normal": [1.0, 2.0],
                            "damage_factor_normal": [3.0, 4.0],
                            "damage_intercept_shock": [5.0, 6.0],
                            "damage_factor_shock": [7.0, 8.0],
                        },
                        "draws": {
                            "trigger_draws": [0.1, 0.2],
                            "amount_draws": [0.3, 0.4],
                        },
                        "insurance_decisions": [
                            {"sector_index": 0, "insured": False},
                            {"sector_index": 1, "insured": False},
                        ],
                    }
                ],
            }
        )
