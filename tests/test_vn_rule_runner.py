import json

import pytest

from ims.engine.context import SimulationContext
from ims.engine.vn_rule_runner import (
    VNSettlementMultiPeriodRunResult,
    VNSettlementPeriodRunResult,
    VNStateCarryover,
    run_vn_settlement_multi_period_from_fixture,
    run_vn_settlement_multi_period_from_mappings,
    run_vn_settlement_period,
    run_vn_settlement_period_from_mapping,
)
from ims.model.entities import Insurer, Policyholder
from ims.model.vn_damage_rules import VNDamageRuleDraws, VNDamageRuleParameters
from ims.model.vn_rules import (
    VNDamageSettlementSnapshot,
    VNInsuranceDecision,
    VNSectorSettlementDecision,
    VNSettlementSnapshot,
)


def _damage_parameters_mapping() -> dict:
    return {
        "damage_intercept_normal": [5.0, 7.0],
        "damage_factor_normal": [2.0, 3.0],
        "damage_intercept_shock": [50.0, 70.0],
        "damage_factor_shock": [20.0, 30.0],
    }


def _vn_period_scenario(period: int, *, policyholder_id: int = 21, insurer_id: int = 11) -> dict:
    return {
        "context": {"period": period, "max_periods": 6},
        "bav": {"entity_id": 1, "name": "BAV"},
        "insurers": [
            {
                "entity_id": insurer_id,
                "name": f"VU-{insurer_id}",
                "premiums_current_sector": [4.0, 6.0],
                "reserves_current": [40.0, 60.0],
                "policyholders_current_sector": [1.0, 2.0],
            }
        ],
        "policyholders": [{"entity_id": policyholder_id, "name": f"VN-{policyholder_id}"}],
        "vn_damage_settlement_snapshots": [
            {
                "policyholder_id": policyholder_id,
                "previous_wealth": 100.0,
                "damage_thresholds": [0.8, 0.2],
                "parameters": _damage_parameters_mapping(),
                "draws": {
                    "trigger_draws": [0.1, 0.5],
                    "amount_draws": [2.0, 3.0],
                },
                "insurance_decisions": [
                    {"sector_index": 0, "insured": True, "insurer_id": insurer_id},
                    {"sector_index": 1, "insured": False},
                ],
            }
        ],
    }


def test_vn_rule_runner_applies_explicit_settlement_snapshots() -> None:
    context = SimulationContext(period=4, max_periods=5)
    insurer = Insurer(
        entity_id=10,
        premiums_current_sector=[7.0, 8.0],
        reserves_current=[20.0, 30.0],
        policyholders_current_sector=[0.0, 0.0],
    )
    policyholder = Policyholder(entity_id=20)
    snapshot = VNSettlementSnapshot(
        policyholder_id=20,
        previous_wealth=50.0,
        decisions=[
            VNSectorSettlementDecision(sector_index=0, insured=True, insurer_id=10, damage=1.0),
            VNSectorSettlementDecision(sector_index=1, insured=False, damage=2.0),
        ],
    )

    result = run_vn_settlement_period(
        context,
        [insurer],
        [policyholder],
        settlement_snapshots=[snapshot],
    )

    assert isinstance(result, VNSettlementPeriodRunResult)
    assert result.period == 4
    assert result.total_settlement_applications == 1
    assert result.settlement_applications[0].policyholder_id == 20
    assert policyholder.paid_premium_current == [7.0, 0.0]
    assert policyholder.end_wealth_current == 40.0
    assert insurer.reserves_current == [26.0, 30.0]


def test_vn_rule_runner_applies_explicit_damage_settlement_snapshots() -> None:
    context = SimulationContext(period=5, max_periods=6)
    insurer = Insurer(
        entity_id=11,
        premiums_current_sector=[4.0, 6.0],
        reserves_current=[40.0, 60.0],
        policyholders_current_sector=[1.0, 2.0],
    )
    policyholder = Policyholder(entity_id=21)
    snapshot = VNDamageSettlementSnapshot(
        policyholder_id=21,
        parameters=VNDamageRuleParameters(
            damage_intercept_normal=[5.0, 7.0],
            damage_factor_normal=[2.0, 3.0],
            damage_intercept_shock=[50.0, 70.0],
            damage_factor_shock=[20.0, 30.0],
        ),
        damage_thresholds=[0.8, 0.2],
        draws=VNDamageRuleDraws(trigger_draws=[0.1, 0.5], amount_draws=[2.0, 3.0]),
        insurance_decisions=[
            VNInsuranceDecision(sector_index=0, insured=True, insurer_id=11),
            VNInsuranceDecision(sector_index=1, insured=False),
        ],
        previous_wealth=100.0,
    )

    result = run_vn_settlement_period(
        context,
        [insurer],
        [policyholder],
        damage_settlement_snapshots=[snapshot],
    )

    assert result.period == 5
    assert result.total_damage_settlement_applications == 1
    assert result.total_settlement_applications == 1
    assert result.damage_settlement_applications[0].damage_result.damages == [9.0, 0.0]
    assert policyholder.paid_premium_current == [4.0, 0.0]
    assert policyholder.end_wealth_current == 87.0
    assert insurer.reserves_current == [35.0, 60.0]


def test_vn_rule_runner_loads_period_from_mapping() -> None:
    result = run_vn_settlement_period_from_mapping(_vn_period_scenario(5))

    assert isinstance(result, VNSettlementPeriodRunResult)
    assert result.period == 5
    assert result.total_damage_settlement_applications == 1
    assert result.total_settlement_applications == 1
    assert result.damage_settlement_applications[0].damage_result.damages == [9.0, 0.0]
    assert result.damage_settlement_applications[0].settlement_result.end_wealth_current == 87.0


def test_vn_rule_runner_rejects_conflicting_policyholder_targets_per_period() -> None:
    scenario = _vn_period_scenario(5)
    scenario["vn_settlement_snapshots"] = [
        {
            "policyholder_id": 21,
            "previous_wealth": 100.0,
            "decisions": [
                {"sector_index": 0, "insured": False, "damage": 1.0},
                {"sector_index": 1, "insured": False, "damage": 2.0},
            ],
        }
    ]

    with pytest.raises(ValueError, match="disjoint policyholders"):
        run_vn_settlement_period_from_mapping(scenario)


def test_vn_rule_multi_period_runner_processes_increasing_periods() -> None:
    result = run_vn_settlement_multi_period_from_mappings(
        [
            _vn_period_scenario(5, policyholder_id=21),
            _vn_period_scenario(6, policyholder_id=22),
        ]
    )

    assert isinstance(result, VNSettlementMultiPeriodRunResult)
    assert result.processed_periods == [5, 6]
    assert result.total_damage_settlement_applications == 2
    assert result.total_settlement_applications == 2
    assert [period_result.period for period_result in result.period_results] == [5, 6]
    assert result.carryovers == []


def test_vn_rule_multi_period_runner_can_carry_state_forward() -> None:
    result = run_vn_settlement_multi_period_from_mappings(
        [
            _vn_period_scenario(5, policyholder_id=21, insurer_id=11),
            _vn_period_scenario(6, policyholder_id=21, insurer_id=11),
        ],
        carry_forward_vn_state=True,
    )

    assert len(result.carryovers) == 1
    assert isinstance(result.carryovers[0], VNStateCarryover)
    assert result.carryovers[0].from_period == 5
    assert result.carryovers[0].to_period == 6
    assert result.carryovers[0].insurer_ids == [11]
    assert result.carryovers[0].policyholder_ids == [21]

    second_insurer = result.period_results[1].insurers[0]
    assert second_insurer.reserves_current == [30.0, 60.0]
    assert second_insurer.policyholders_current_sector == [3.0, 2.0]
    assert second_insurer.claims_count_current == [2, 0]
    assert second_insurer.claims_sum_current == [18.0, 0.0]

    second_policyholder = result.period_results[1].policyholders[0]
    assert second_policyholder.insured_prev_sector == [1.0, 0.0]
    assert second_policyholder.insurer_id == 11
    assert second_policyholder.end_wealth_current == 87.0


def test_vn_rule_multi_period_runner_without_carryover_keeps_explicit_period_state() -> None:
    result = run_vn_settlement_multi_period_from_mappings(
        [
            _vn_period_scenario(5, policyholder_id=21, insurer_id=11),
            _vn_period_scenario(6, policyholder_id=21, insurer_id=11),
        ],
        carry_forward_vn_state=False,
    )

    assert result.carryovers == []
    assert result.period_results[1].insurers[0].reserves_current == [35.0, 60.0]
    assert result.period_results[1].insurers[0].policyholders_current_sector == [2.0, 2.0]


def test_vn_rule_multi_period_runner_skips_carryover_for_missing_followup_entities() -> None:
    result = run_vn_settlement_multi_period_from_mappings(
        [
            _vn_period_scenario(5, policyholder_id=21, insurer_id=11),
            _vn_period_scenario(6, policyholder_id=22, insurer_id=12),
        ],
        carry_forward_vn_state=True,
    )

    assert result.carryovers == []
    assert result.period_results[1].insurers[0].entity_id == 12
    assert result.period_results[1].policyholders[0].entity_id == 22


def test_vn_rule_multi_period_runner_loads_fixture(tmp_path) -> None:
    fixture_path = tmp_path / "vn_periods.json"
    fixture_path.write_text(
        json.dumps({"periods": [_vn_period_scenario(5), _vn_period_scenario(6, policyholder_id=22)]}),
        encoding="utf-8",
    )

    result = run_vn_settlement_multi_period_from_fixture(fixture_path)

    assert result.processed_periods == [5, 6]
    assert result.total_damage_settlement_applications == 2


def test_vn_rule_multi_period_runner_fixture_supports_carryover(tmp_path) -> None:
    fixture_path = tmp_path / "vn_periods_with_carryover.json"
    fixture_path.write_text(
        json.dumps(
            {
                "carry_forward_vn_state": True,
                "periods": [
                    _vn_period_scenario(5, policyholder_id=21, insurer_id=11),
                    _vn_period_scenario(6, policyholder_id=21, insurer_id=11),
                ],
            }
        ),
        encoding="utf-8",
    )

    result = run_vn_settlement_multi_period_from_fixture(fixture_path)

    assert len(result.carryovers) == 1
    assert result.carryovers[0].policyholder_ids == [21]
    assert result.period_results[1].insurers[0].reserves_current == [30.0, 60.0]


def test_vn_rule_multi_period_runner_rejects_duplicate_or_unsorted_periods() -> None:
    with pytest.raises(ValueError, match="duplicate periods"):
        run_vn_settlement_multi_period_from_mappings(
            [_vn_period_scenario(5), _vn_period_scenario(5, policyholder_id=22)]
        )

    with pytest.raises(ValueError, match="increasing periods"):
        run_vn_settlement_multi_period_from_mappings(
            [_vn_period_scenario(6), _vn_period_scenario(5, policyholder_id=22)]
        )


def test_vn_rule_runner_allows_empty_snapshot_list() -> None:
    result = run_vn_settlement_period(
        SimulationContext(period=2, max_periods=3),
        [Insurer(entity_id=10)],
        [Policyholder(entity_id=20)],
    )

    assert result.period == 2
    assert result.total_settlement_applications == 0
    assert result.total_damage_settlement_applications == 0
    assert result.damage_settlement_applications == []
    assert result.settlement_applications == []
