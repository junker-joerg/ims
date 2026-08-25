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


def _vn_period_scenario(
    period: int,
    *,
    policyholder_id: int = 21,
    insurer_id: int = 11,
    insurer_ids: list[int] | None = None,
    run_index: int = 0,
) -> dict:
    ids = insurer_ids if insurer_ids is not None else [insurer_id]
    return {
        "context": {"period": period, "max_periods": 6, "run_index": run_index},
        "bav": {"entity_id": 1, "name": "BAV"},
        "insurers": [
            {
                "entity_id": current_insurer_id,
                "name": f"VU-{current_insurer_id}",
                "premiums_current_sector": [4.0, 6.0],
                "reserves_current": [40.0, 60.0],
                "policyholders_current_sector": [1.0, 2.0],
            }
            for current_insurer_id in ids
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
    assert result.global_period == 4
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
    assert result.global_period == 5
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
    assert result.global_period == 5
    assert result.total_damage_settlement_applications == 1
    assert result.total_settlement_applications == 1
    assert result.damage_settlement_applications[0].damage_result.damages == [9.0, 0.0]
    assert result.damage_settlement_applications[0].settlement_result.end_wealth_current == 87.0
    assert result.policyholders[0].insurer_id == 11


def test_vn_rule_runner_applies_explicit_insurance_rule_snapshots() -> None:
    scenario = _vn_period_scenario(5, insurer_ids=[11, 12])
    scenario["vn_insurance_rule_snapshots"] = [
        {
            "policyholder_id": 21,
            "rule_kind": "best_info",
            "parameters": {
                "insurance_thresholds_normal": [0.5, 0.1],
                "insurance_thresholds_shock": [0.5, 0.1],
            },
            "market_damage_indicator": 0.5,
            "insurer_inputs": [
                {"insurer_id": 11, "premiums_current_sector": [6.0, 5.0]},
                {"insurer_id": 12, "premiums_current_sector": [4.0, 7.0]},
            ],
            "information_cost_per_insurer": 1.0,
        }
    ]

    result = run_vn_settlement_period_from_mapping(scenario)

    assert len(result.insurance_rule_applications) == 1
    application = result.insurance_rule_applications[0]
    assert application.policyholder_id == 21
    assert [decision.insurer_id for decision in application.decisions] == [12, None]
    assert application.result.information_cost == 4.0
    assert result.total_settlement_applications == 1
    settlement = result.damage_settlement_applications[0].settlement_result
    assert settlement.information_cost == 4.0
    assert settlement.end_wealth_current == 83.0
    assert result.policyholders[0].end_wealth_current == 83.0


def test_vn_rule_runner_feeds_insurance_rule_decisions_into_damage_settlement() -> None:
    scenario = _vn_period_scenario(5)
    scenario["vn_insurance_rule_snapshots"] = [
        {
            "policyholder_id": 21,
            "rule_kind": "compulsory",
            "active_insurer_ids": [11],
            "draws": {"insurer_choice_draws": [0.0, 0.0]},
        }
    ]
    del scenario["vn_damage_settlement_snapshots"][0]["insurance_decisions"]

    result = run_vn_settlement_period_from_mapping(scenario)

    assert len(result.insurance_rule_applications) == 1
    assert result.total_damage_settlement_applications == 1
    application = result.damage_settlement_applications[0]
    assert application.damage_result.damages == [9.0, 0.0]
    assert application.settlement_result.chosen_insurer_sector_current == [11, 11]
    assert result.policyholders[0].paid_premium_current == [4.0, 6.0]
    assert result.policyholders[0].end_wealth_current == 81.0
    assert result.insurers[0].policyholders_current_sector == [2.0, 3.0]


def test_vn_rule_runner_rejects_unresolved_damage_settlement_decisions() -> None:
    scenario = _vn_period_scenario(5)
    del scenario["vn_damage_settlement_snapshots"][0]["insurance_decisions"]

    with pytest.raises(ValueError, match="matching VN insurance rule snapshot"):
        run_vn_settlement_period_from_mapping(scenario)


def test_vn_rule_multi_period_runner_counts_insurance_rule_applications() -> None:
    first = _vn_period_scenario(5, policyholder_id=21)
    second = _vn_period_scenario(6, policyholder_id=22)
    first["vn_insurance_rule_snapshots"] = [
        {
            "policyholder_id": 21,
            "rule_kind": "compulsory",
            "active_insurer_ids": [11],
            "draws": {"insurer_choice_draws": [0.0, 0.0]},
        }
    ]
    second["vn_insurance_rule_snapshots"] = [
        {
            "policyholder_id": 22,
            "rule_kind": "compulsory",
            "active_insurer_ids": [11],
            "draws": {"insurer_choice_draws": [0.0, 0.0]},
        }
    ]

    result = run_vn_settlement_multi_period_from_mappings([first, second])

    assert result.total_insurance_rule_applications == 2
    assert [len(period.insurance_rule_applications) for period in result.period_results] == [1, 1]


def test_vn_rule_runner_rejects_unknown_insurance_rule_policyholder() -> None:
    scenario = _vn_period_scenario(5)
    scenario["vn_insurance_rule_snapshots"] = [
        {
            "policyholder_id": 999,
            "rule_kind": "compulsory",
            "active_insurer_ids": [11],
            "draws": {"insurer_choice_draws": [0.0, 0.0]},
        }
    ]

    with pytest.raises(ValueError, match="unknown policyholders"):
        run_vn_settlement_period_from_mapping(scenario)


def test_vn_rule_runner_rejects_unknown_insurance_rule_active_insurer() -> None:
    scenario = _vn_period_scenario(5)
    scenario["vn_insurance_rule_snapshots"] = [
        {
            "policyholder_id": 21,
            "rule_kind": "compulsory",
            "active_insurer_ids": [99],
            "draws": {"insurer_choice_draws": [0.0, 0.0]},
        }
    ]

    with pytest.raises(ValueError, match="unknown insurers: 99"):
        run_vn_settlement_period_from_mapping(scenario)


def test_vn_rule_runner_rejects_unknown_insurance_rule_initial_decision_insurer() -> None:
    scenario = _vn_period_scenario(1)
    scenario["vn_insurance_rule_snapshots"] = [
        {
            "policyholder_id": 21,
            "rule_kind": "random",
            "initial_decisions": [
                {"sector_index": 0, "insured": True, "insurer_id": 99},
                {"sector_index": 1, "insured": False},
            ],
        }
    ]

    with pytest.raises(ValueError, match="unknown insurers: 99"):
        run_vn_settlement_period_from_mapping(scenario)


def test_vn_rule_runner_rejects_unknown_insurance_rule_input_insurer() -> None:
    scenario = _vn_period_scenario(5)
    scenario["vn_insurance_rule_snapshots"] = [
        {
            "policyholder_id": 21,
            "rule_kind": "best_info",
            "parameters": {
                "insurance_thresholds_normal": [0.5, 0.1],
                "insurance_thresholds_shock": [0.5, 0.1],
            },
            "market_damage_indicator": 0.5,
            "insurer_inputs": [
                {"insurer_id": 99, "premiums_current_sector": [4.0, 7.0]},
            ],
        }
    ]

    with pytest.raises(ValueError, match="unknown insurers: 99"):
        run_vn_settlement_period_from_mapping(scenario)


def test_vn_rule_runner_rejects_unknown_insurance_rule_history_insurer() -> None:
    scenario = _vn_period_scenario(5)
    scenario["vn_insurance_rule_snapshots"] = [
        {
            "policyholder_id": 21,
            "rule_kind": "search_history",
            "parameters": {
                "insurance_thresholds_normal": [0.5, 0.1],
                "insurance_thresholds_shock": [0.5, 0.1],
            },
            "damage_probabilities": [0.6, 0.0],
            "active_insurer_ids": [11],
            "history": [
                {"period": 4, "sector_index": 0, "insured": True, "premium": 5.0, "insurer_id": 99},
                {"period": 4, "sector_index": 1, "insured": False, "premium": 0.0},
            ],
        }
    ]

    with pytest.raises(ValueError, match="unknown insurers: 99"):
        run_vn_settlement_period_from_mapping(scenario)


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
    assert result.processed_local_periods == [5, 6]
    assert result.processed_global_periods == [5, 6]
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
    assert result.carryovers[0].from_global_period == 5
    assert result.carryovers[0].to_global_period == 6
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


def test_vn_rule_multi_period_runner_keeps_insurer_id_consistent_after_changed_decision() -> None:
    result = run_vn_settlement_multi_period_from_mappings(
        [
            _vn_period_scenario(5, policyholder_id=21, insurer_id=11),
            _vn_period_scenario(6, policyholder_id=21, insurer_id=12, insurer_ids=[11, 12]),
        ],
        carry_forward_vn_state=True,
    )

    second_policyholder = result.period_results[1].policyholders[0]
    assert second_policyholder.insurer_id == 12
    assert second_policyholder.chosen_insurer_current == 12
    assert second_policyholder.chosen_insurer_sector_current == [12, None]


def test_vn_rule_multi_period_runner_orders_by_global_periods_across_runs() -> None:
    result = run_vn_settlement_multi_period_from_mappings(
        [
            _vn_period_scenario(5, policyholder_id=21, insurer_id=11, run_index=0),
            _vn_period_scenario(5, policyholder_id=21, insurer_id=11, run_index=1),
        ],
        carry_forward_vn_state=True,
    )

    assert result.processed_periods == [5, 5]
    assert result.processed_local_periods == [5, 5]
    assert result.processed_global_periods == [5, 11]
    assert [period_result.global_period for period_result in result.period_results] == [5, 11]
    assert result.carryovers[0].from_period == 5
    assert result.carryovers[0].to_period == 5
    assert result.carryovers[0].from_global_period == 5
    assert result.carryovers[0].to_global_period == 11


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
    assert result.processed_global_periods == [5, 6]
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


def test_vn_rule_multi_period_runner_fixture_rejects_non_boolean_carryover_flag(tmp_path) -> None:
    fixture_path = tmp_path / "vn_periods_with_bad_carryover.json"
    fixture_path.write_text(
        json.dumps(
            {
                "carry_forward_vn_state": "false",
                "periods": [
                    _vn_period_scenario(5, policyholder_id=21, insurer_id=11),
                    _vn_period_scenario(6, policyholder_id=21, insurer_id=11),
                ],
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="carry_forward_vn_state must be a boolean"):
        run_vn_settlement_multi_period_from_fixture(fixture_path)


def test_vn_rule_multi_period_runner_fixture_validates_bad_flag_before_override(tmp_path) -> None:
    fixture_path = tmp_path / "vn_periods_with_bad_carryover_override.json"
    fixture_path.write_text(
        json.dumps(
            {
                "carry_forward_vn_state": "false",
                "periods": [
                    _vn_period_scenario(5, policyholder_id=21, insurer_id=11),
                    _vn_period_scenario(6, policyholder_id=21, insurer_id=11),
                ],
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="carry_forward_vn_state must be a boolean"):
        run_vn_settlement_multi_period_from_fixture(
            fixture_path,
            carry_forward_vn_state=True,
        )


def test_vn_rule_multi_period_runner_rejects_duplicate_or_unsorted_periods() -> None:
    with pytest.raises(ValueError, match="duplicate periods"):
        run_vn_settlement_multi_period_from_mappings(
            [_vn_period_scenario(5), _vn_period_scenario(5, policyholder_id=22)]
        )

    with pytest.raises(ValueError, match="increasing periods"):
        run_vn_settlement_multi_period_from_mappings(
            [_vn_period_scenario(6), _vn_period_scenario(5, policyholder_id=22)]
        )

    with pytest.raises(ValueError, match="increasing periods"):
        run_vn_settlement_multi_period_from_mappings(
            [
                _vn_period_scenario(1, run_index=1),
                _vn_period_scenario(6, policyholder_id=22, run_index=0),
            ]
        )


def test_vn_rule_runner_allows_empty_snapshot_list() -> None:
    result = run_vn_settlement_period(
        SimulationContext(period=2, max_periods=3),
        [Insurer(entity_id=10)],
        [Policyholder(entity_id=20)],
    )

    assert result.period == 2
    assert result.global_period == 2
    assert result.total_settlement_applications == 0
    assert result.total_damage_settlement_applications == 0
    assert result.damage_settlement_applications == []
    assert result.settlement_applications == []
