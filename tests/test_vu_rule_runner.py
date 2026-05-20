import json
from pathlib import Path

import pytest

from ims.engine.vu_rule_runner import (
    VUForeignInfoCarryover,
    VUForeignInfoMultiPeriodRunResult,
    VUForeignInfoPeriodRunResult,
    run_vu_foreign_info_multi_period_from_fixture,
    run_vu_foreign_info_multi_period_from_mappings,
    run_vu_foreign_info_period_from_fixture,
    run_vu_foreign_info_period_from_mapping,
)
from ims.io.scenario_loader import load_scenario_from_mapping
from ims.model.vu_rules import VUForeignInfoRuleKind


def _parameters() -> dict[str, list[float]]:
    return {
        "premium_intercept_normal": [1.0, 2.0],
        "premium_factor_normal": [0.5, 0.25],
        "advertising_intercept_normal": [3.0, 4.0],
        "advertising_factor_normal": [0.1, 0.2],
        "premium_intercept_shock": [10.0, 20.0],
        "premium_factor_shock": [1.0, 2.0],
        "advertising_intercept_shock": [30.0, 40.0],
        "advertising_factor_shock": [3.0, 4.0],
    }


def _reserve_markup_parameters() -> dict[str, list[float]]:
    return {
        "premium_below_normal": [1.1, 1.2],
        "premium_above_normal": [0.9, 0.8],
        "advertising_below_normal": [1.3, 1.4],
        "advertising_above_normal": [0.7, 0.6],
        "premium_below_shock": [2.1, 2.2],
        "premium_above_shock": [1.9, 1.8],
        "advertising_below_shock": [2.3, 2.4],
        "advertising_above_shock": [1.7, 1.6],
    }


def _expected_claim_parameters() -> dict[str, list[float]]:
    return {
        "premium_below_normal": [1.1, 1.2],
        "premium_above_normal": [0.9, 0.8],
        "advertising_below_normal": [1.3, 1.4],
        "advertising_above_normal": [0.7, 0.6],
        "premium_below_shock": [2.1, 2.2],
        "premium_above_shock": [1.9, 1.8],
        "advertising_below_shock": [2.3, 2.4],
        "advertising_above_shock": [1.7, 1.6],
    }


def _market_share_markup_parameters() -> dict[str, list[float]]:
    return {
        "premium_below_normal": [1.1, 1.2],
        "premium_above_normal": [0.9, 0.8],
        "advertising_below_normal": [1.3, 1.4],
        "advertising_above_normal": [0.7, 0.6],
        "premium_below_shock": [2.1, 2.2],
        "premium_above_shock": [1.9, 1.8],
        "advertising_below_shock": [2.3, 2.4],
        "advertising_above_shock": [1.7, 1.6],
    }


def _scenario() -> dict:
    return {
        "context": {"period": 2, "logtime": 3, "max_periods": 12, "run_index": 1},
        "bav": {"entity_id": 1, "name": "BAV"},
        "insurers": [
            {
                "entity_id": 10,
                "name": "VU-10",
                "active": True,
                "active_prev": True,
                "premiums_prev_sector": [100.0, 200.0],
                "advertising_prev_sector": [10.0, 20.0],
                "reserves_prev_sector": [1000.0, 100.0],
                "reserves_current": [50.0, 60.0],
                "policyholders_current": 30.0,
                "policyholders_current_sector": [30.0, 80.0],
                "claims_count_current": [2, 4],
                "claims_sum_current": [250.0, 600.0],
            },
            {
                "entity_id": 11,
                "name": "VU-11",
                "active": True,
                "active_prev": True,
                "premiums_prev_sector": [300.0, 400.0],
                "advertising_prev_sector": [30.0, 40.0],
                "reserves_prev_sector": [500.0, 900.0],
                "reserves_current": [70.0, 80.0],
                "policyholders_current": 0.0,
                "policyholders_current_sector": [0.0, 0.0],
                "claims_count_current": [0, 0],
                "claims_sum_current": [0.0, 0.0],
            },
        ],
        "policyholders": [
            {
                "entity_id": 20,
                "name": "VN-20",
                "active": True,
                "active_prev": True,
                "insurer_id": 10,
                "insured_prev_sector": [1.0, 0.0],
            }
        ],
        "vu_foreign_info_rule_snapshots": [
            {
                "insurer_id": 10,
                "rule_kind": "average",
                "interest_rate": 0.05,
                "parameters": _parameters(),
            },
            {
                "insurer_id": 11,
                "rule_kind": "attack",
                "interest_rate": 0.1,
                "change_shock": True,
                "parameters": _parameters(),
            },
        ],
    }


def _scenario_for_period(period: int, *, insurer_id: int = 10) -> dict:
    scenario = _scenario()
    scenario["context"]["period"] = period
    scenario["context"]["logtime"] = period + 10
    scenario["insurers"] = [dict(scenario["insurers"][0])]
    scenario["insurers"][0]["entity_id"] = insurer_id
    scenario["insurers"][0]["name"] = f"VU-{insurer_id}"
    scenario["policyholders"] = []
    scenario["vu_foreign_info_rule_snapshots"] = [
        {
            "insurer_id": insurer_id,
            "rule_kind": "average",
            "interest_rate": 0.05,
            "parameters": _parameters(),
        }
    ]
    return scenario


def test_vu_rule_runner_computes_bav_foreign_info_before_applying_snapshots() -> None:
    result = run_vu_foreign_info_period_from_mapping(_scenario())

    assert isinstance(result, VUForeignInfoPeriodRunResult)
    assert result.context_period == 2
    assert result.context_logtime == 3
    assert result.foreign_info.insurer.dp == [200.0, 300.0]
    assert result.foreign_info.insurer.dw == [20.0, 30.0]
    assert result.foreign_info.insurer.pm == [100.0, 200.0]
    assert result.foreign_info.insurer.wm == [30.0, 40.0]
    assert result.foreign_info.insurer.mp == [100.0, 400.0]
    assert result.foreign_info.insurer.mw == [10.0, 40.0]
    assert result.foreign_info.policyholder.dg == [1.0, 0.0]


def test_vu_rule_runner_updates_targeted_insurers_and_returns_diagnostics() -> None:
    result = run_vu_foreign_info_period_from_mapping(_scenario())

    insurer_by_id = {insurer.entity_id: insurer for insurer in result.insurers}
    assert insurer_by_id[10].premiums_current_sector == [101.0, 77.0]
    assert insurer_by_id[10].advertising_current_sector == [5.0, 10.0]
    assert insurer_by_id[10].reserves_current == [52.5, 63.0]
    assert insurer_by_id[11].premiums_current_sector == [110.0, 820.0]
    assert insurer_by_id[11].advertising_current_sector == [60.0, 200.0]
    assert insurer_by_id[11].reserves_current == [77.0, 88.0]
    assert [application.insurer_id for application in result.rule_applications] == [10, 11]
    assert result.rule_applications[0].rule_kind == VUForeignInfoRuleKind.AVERAGE
    assert result.rule_applications[1].rule_kind == VUForeignInfoRuleKind.ATTACK
    assert result.reserve_markup_applications == []
    assert result.expected_claim_applications == []
    assert result.market_share_markup_applications == []


def test_vu_rule_runner_applies_reserve_markup_snapshots_after_foreign_info() -> None:
    scenario = _scenario()
    scenario["vu_foreign_info_rule_snapshots"] = []
    scenario["vu_reserve_markup_rule_snapshots"] = [
        {
            "insurer_id": 10,
            "reserve_thresholds": [55.0, 55.0],
            "interest_rate": 0.05,
            "parameters": _reserve_markup_parameters(),
        }
    ]

    result = run_vu_foreign_info_period_from_mapping(scenario)

    assert result.rule_applications == []
    assert len(result.reserve_markup_applications) == 1
    assert result.reserve_markup_applications[0].insurer_id == 10
    insurer = result.insurers[0]
    assert insurer.premiums_current_sector == [0.0, 0.0]
    assert insurer.advertising_current_sector == [0.0, 0.0]
    assert insurer.reserves_current == pytest.approx([52.5, 63.0])


def test_vu_rule_runner_counts_foreign_info_and_reserve_markup_applications() -> None:
    scenario = _scenario_for_period(2)
    scenario["vu_reserve_markup_rule_snapshots"] = [
        {
            "insurer_id": 10,
            "reserve_thresholds": [55.0, 55.0],
            "parameters": _reserve_markup_parameters(),
        }
    ]

    result = run_vu_foreign_info_multi_period_from_mappings([scenario])

    assert result.total_rule_applications == 2
    assert len(result.period_results[0].rule_applications) == 1
    assert len(result.period_results[0].reserve_markup_applications) == 1


def test_vu_rule_runner_applies_expected_claim_snapshots_after_prior_rules() -> None:
    scenario = _scenario()
    scenario["vu_foreign_info_rule_snapshots"] = []
    scenario["vu_expected_claim_rule_snapshots"] = [
        {
            "insurer_id": 10,
            "interest_rate": 0.05,
            "parameters": _expected_claim_parameters(),
        }
    ]

    result = run_vu_foreign_info_period_from_mapping(scenario)

    assert result.rule_applications == []
    assert result.reserve_markup_applications == []
    assert len(result.expected_claim_applications) == 1
    assert result.expected_claim_applications[0].insurer_id == 10
    insurer = result.insurers[0]
    assert insurer.premiums_current_sector == pytest.approx([0.0, 0.0])
    assert insurer.advertising_current_sector == pytest.approx([0.0, 0.0])
    assert insurer.reserves_current == pytest.approx([52.5, 63.0])


def test_vu_rule_runner_counts_all_loaded_vu_rule_application_types() -> None:
    scenario = _scenario_for_period(2)
    scenario["vu_reserve_markup_rule_snapshots"] = [
        {
            "insurer_id": 10,
            "reserve_thresholds": [55.0, 55.0],
            "parameters": _reserve_markup_parameters(),
        }
    ]
    scenario["vu_expected_claim_rule_snapshots"] = [
        {
            "insurer_id": 10,
            "parameters": _expected_claim_parameters(),
        }
    ]

    result = run_vu_foreign_info_multi_period_from_mappings([scenario])

    assert result.total_rule_applications == 3
    assert len(result.period_results[0].rule_applications) == 1
    assert len(result.period_results[0].reserve_markup_applications) == 1
    assert len(result.period_results[0].expected_claim_applications) == 1


def test_vu_rule_runner_applies_market_share_markup_snapshots_after_prior_rules() -> None:
    scenario = _scenario()
    scenario["vu_foreign_info_rule_snapshots"] = []
    scenario["vu_market_share_markup_rule_snapshots"] = [
        {
            "insurer_id": 10,
            "market_share_thresholds": [0.4, 0.7],
            "active_policyholder_count": 100,
            "interest_rate": 0.05,
            "parameters": _market_share_markup_parameters(),
        }
    ]

    result = run_vu_foreign_info_period_from_mapping(scenario)

    assert result.rule_applications == []
    assert result.reserve_markup_applications == []
    assert result.expected_claim_applications == []
    assert len(result.market_share_markup_applications) == 1
    assert result.market_share_markup_applications[0].insurer_id == 10
    insurer = result.insurers[0]
    assert insurer.premiums_current_sector == pytest.approx([0.0, 0.0])
    assert insurer.advertising_current_sector == pytest.approx([0.0, 0.0])
    assert insurer.reserves_current == pytest.approx([52.5, 63.0])


def test_vu_rule_runner_counts_all_four_loaded_vu_rule_application_types() -> None:
    scenario = _scenario_for_period(2)
    scenario["vu_reserve_markup_rule_snapshots"] = [
        {
            "insurer_id": 10,
            "reserve_thresholds": [55.0, 55.0],
            "parameters": _reserve_markup_parameters(),
        }
    ]
    scenario["vu_expected_claim_rule_snapshots"] = [
        {
            "insurer_id": 10,
            "parameters": _expected_claim_parameters(),
        }
    ]
    scenario["vu_market_share_markup_rule_snapshots"] = [
        {
            "insurer_id": 10,
            "market_share_thresholds": [0.4, 0.7],
            "active_policyholder_count": 100,
            "parameters": _market_share_markup_parameters(),
        }
    ]

    result = run_vu_foreign_info_multi_period_from_mappings([scenario])

    assert result.total_rule_applications == 4
    assert len(result.period_results[0].rule_applications) == 1
    assert len(result.period_results[0].reserve_markup_applications) == 1
    assert len(result.period_results[0].expected_claim_applications) == 1
    assert len(result.period_results[0].market_share_markup_applications) == 1


def test_vu_rule_runner_collects_basic_aggregate_after_period_step() -> None:
    result = run_vu_foreign_info_period_from_mapping(_scenario())

    assert result.aggregate_snapshot.period == 2
    assert result.aggregate_snapshot.logtime == 3
    assert result.aggregate_snapshot.active_insurers == 2
    assert result.aggregate_snapshot.active_policyholders == 1
    assert result.aggregate_snapshot.assigned_policyholders == 1


def test_vu_rule_runner_can_run_without_snapshots() -> None:
    scenario = _scenario()
    scenario.pop("vu_foreign_info_rule_snapshots")

    result = run_vu_foreign_info_period_from_mapping(scenario)

    assert result.rule_applications == []
    assert result.insurers[0].premiums_current_sector == [0.0, 0.0]
    assert result.foreign_info.insurer.dp == [200.0, 300.0]


def test_vu_rule_runner_loads_fixture_path(tmp_path: Path) -> None:
    fixture_path = tmp_path / "vu_period.json"
    fixture_path.write_text(json.dumps(_scenario()), encoding="utf-8")

    result = run_vu_foreign_info_period_from_fixture(fixture_path)

    assert result.context_period == 2
    assert len(result.rule_applications) == 2


def test_vu_rule_runner_rejects_duplicate_snapshot_targets() -> None:
    scenario = _scenario()
    scenario["vu_foreign_info_rule_snapshots"].append(dict(scenario["vu_foreign_info_rule_snapshots"][0]))

    loaded = load_scenario_from_mapping(scenario)

    with pytest.raises(ValueError, match="duplicate"):
        run_vu_foreign_info_period_from_mapping(scenario)

    assert len(loaded.vu_foreign_info_rule_snapshots) == 3


def test_vu_rule_multi_period_runner_processes_increasing_period_scenarios() -> None:
    result = run_vu_foreign_info_multi_period_from_mappings(
        [_scenario_for_period(2), _scenario_for_period(3)]
    )

    assert isinstance(result, VUForeignInfoMultiPeriodRunResult)
    assert result.processed_periods == [2, 3]
    assert result.total_rule_applications == 2
    assert result.carryovers == []
    assert [period.context_logtime for period in result.period_results] == [12, 13]
    assert result.period_results[0].insurers[0].premiums_current_sector == [51.0, 52.0]
    assert result.period_results[1].aggregate_snapshot.period == 3


def test_vu_rule_multi_period_runner_can_carry_current_insurer_state_forward() -> None:
    result = run_vu_foreign_info_multi_period_from_mappings(
        [_scenario_for_period(2), _scenario_for_period(3)],
        carry_forward_insurer_state=True,
    )

    assert result.processed_periods == [2, 3]
    assert result.total_rule_applications == 2
    assert len(result.carryovers) == 1
    assert isinstance(result.carryovers[0], VUForeignInfoCarryover)
    assert result.carryovers[0].from_period == 2
    assert result.carryovers[0].to_period == 3
    assert result.carryovers[0].insurer_ids == [10]

    second = result.period_results[1]
    assert second.foreign_info.insurer.dp == [51.0, 52.0]
    assert second.foreign_info.insurer.dw == [4.0, 8.0]
    assert second.foreign_info.insurer.mp == [51.0, 52.0]
    assert second.insurers[0].premiums_current_sector == [26.5, 15.0]
    assert second.insurers[0].advertising_current_sector == [3.4, 5.6]
    assert second.insurers[0].reserves_current == pytest.approx([55.125, 66.15])
    assert second.insurers[0].policyholders_current_sector == [30.0, 80.0]


def test_vu_rule_multi_period_runner_only_carries_matching_insurers() -> None:
    result = run_vu_foreign_info_multi_period_from_mappings(
        [_scenario_for_period(2, insurer_id=10), _scenario_for_period(3, insurer_id=11)],
        carry_forward_insurer_state=True,
    )

    assert result.carryovers == []
    assert result.period_results[1].foreign_info.insurer.dp == [100.0, 200.0]


def test_vu_rule_multi_period_runner_loads_fixture_object(tmp_path: Path) -> None:
    fixture_path = tmp_path / "vu_multi_period.json"
    fixture_path.write_text(
        json.dumps(
            {
                "metadata": {"name": "small-vu-run"},
                "periods": [_scenario_for_period(2), _scenario_for_period(3)],
            }
        ),
        encoding="utf-8",
    )

    result = run_vu_foreign_info_multi_period_from_fixture(fixture_path)

    assert result.processed_periods == [2, 3]
    assert len(result.period_results) == 2


def test_vu_rule_multi_period_runner_loads_fixture_list(tmp_path: Path) -> None:
    fixture_path = tmp_path / "vu_multi_period_list.json"
    fixture_path.write_text(json.dumps([_scenario_for_period(2), _scenario_for_period(3)]), encoding="utf-8")

    result = run_vu_foreign_info_multi_period_from_fixture(fixture_path)

    assert result.processed_periods == [2, 3]


def test_vu_rule_multi_period_runner_fixture_supports_carryover(tmp_path: Path) -> None:
    fixture_path = tmp_path / "vu_multi_period_carry.json"
    fixture_path.write_text(json.dumps([_scenario_for_period(2), _scenario_for_period(3)]), encoding="utf-8")

    result = run_vu_foreign_info_multi_period_from_fixture(
        fixture_path,
        carry_forward_insurer_state=True,
    )

    assert result.carryovers[0].insurer_ids == [10]
    assert result.period_results[1].foreign_info.insurer.dp == [51.0, 52.0]


def test_vu_rule_multi_period_runner_rejects_duplicate_periods() -> None:
    with pytest.raises(ValueError, match="duplicate periods"):
        run_vu_foreign_info_multi_period_from_mappings(
            [_scenario_for_period(2), _scenario_for_period(2, insurer_id=11)]
        )


def test_vu_rule_multi_period_runner_rejects_unsorted_periods() -> None:
    with pytest.raises(ValueError, match="increasing periods"):
        run_vu_foreign_info_multi_period_from_mappings(
            [_scenario_for_period(3), _scenario_for_period(2)]
        )


def test_vu_rule_multi_period_runner_rejects_empty_input() -> None:
    with pytest.raises(ValueError, match="at least one"):
        run_vu_foreign_info_multi_period_from_mappings([])
