import pytest

from ims.engine.rng import create_rng, rand_normal_standard
from ims.engine.vn_rule_runner import (
    run_vn_settlement_multi_period_from_mappings,
    run_vn_settlement_period_from_mapping,
)
from ims.io.scenario_loader import load_scenario_from_mapping
from ims.model.entities import Insurer, Policyholder
from ims.model.vn_damage_rules import VNDamageRuleDraws, VNDamageRuleParameters
from ims.model.vn_rules import (
    VNDamageSettlementSnapshot,
    VNInsuranceDecision,
    apply_vn_damage_settlement_snapshot,
    apply_vn_damage_settlement_snapshots,
    load_vn_damage_settlement_snapshots_from_mapping,
)


def _damage_parameters_mapping() -> dict:
    return {
        "damage_intercept_normal": [5.0, 7.0],
        "damage_factor_normal": [2.0, 3.0],
        "damage_intercept_shock": [50.0, 70.0],
        "damage_factor_shock": [20.0, 30.0],
    }


def _vn_period_scenario(period: int = 5, *, policyholder_id: int = 21, rng_seed: int = 123) -> dict:
    return {
        "context": {"period": period, "max_periods": 6, "rng_seed": rng_seed},
        "bav": {"entity_id": 1, "name": "BAV"},
        "insurers": [
            {
                "entity_id": 11,
                "name": "VU-11",
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
                "insurance_decisions": [
                    {"sector_index": 0, "insured": True, "insurer_id": 11},
                    {"sector_index": 1, "insured": False},
                ],
            }
        ],
    }


def test_vn_damage_settlement_snapshot_can_use_runner_draw_source() -> None:
    insurer = Insurer(
        entity_id=14,
        premiums_current_sector=[8.0, 9.0],
        reserves_current=[100.0, 200.0],
        policyholders_current_sector=[2.0, 3.0],
    )
    policyholder = Policyholder(entity_id=35)
    snapshot = VNDamageSettlementSnapshot(
        policyholder_id=35,
        parameters=VNDamageRuleParameters(
            damage_intercept_normal=[10.0, 20.0],
            damage_factor_normal=[2.0, 3.0],
            damage_intercept_shock=[100.0, 200.0],
            damage_factor_shock=[4.0, 5.0],
        ),
        damage_thresholds=[0.7, 0.4],
        insurance_decisions=[
            VNInsuranceDecision(sector_index=0, insured=True, insurer_id=14),
            VNInsuranceDecision(sector_index=1, insured=False),
        ],
        previous_wealth=1000.0,
    )

    application = apply_vn_damage_settlement_snapshot(
        policyholder,
        [insurer],
        snapshot,
        damage_draw_provider=lambda: VNDamageRuleDraws(
            trigger_draws=[0.6, 0.5],
            amount_draws=[1.5, 2.0],
        ),
    )

    assert snapshot.draws is None
    assert application.damage_result.trigger_draws == [0.6, 0.5]
    assert application.damage_result.amount_draws == [1.5, 2.0]
    assert application.damage_result.damages == [13.0, 0.0]


def test_vn_damage_settlement_snapshot_requires_draw_source() -> None:
    snapshot = VNDamageSettlementSnapshot(
        policyholder_id=35,
        parameters=VNDamageRuleParameters(
            damage_intercept_normal=[10.0, 20.0],
            damage_factor_normal=[2.0, 3.0],
            damage_intercept_shock=[100.0, 200.0],
            damage_factor_shock=[4.0, 5.0],
        ),
        damage_thresholds=[0.7, 0.4],
        insurance_decisions=[
            VNInsuranceDecision(sector_index=0, insured=False),
            VNInsuranceDecision(sector_index=1, insured=False),
        ],
        previous_wealth=1000.0,
    )

    with pytest.raises(ValueError, match="draws"):
        apply_vn_damage_settlement_snapshots([Policyholder(entity_id=35)], [], [snapshot])


def test_vn_damage_settlement_loader_allows_omitted_draws() -> None:
    snapshots = load_vn_damage_settlement_snapshots_from_mapping(
        [
            {
                "policyholder_id": 80,
                "previous_wealth": 300.0,
                "damage_thresholds": [0.7, 0.4],
                "parameters": {
                    "damage_intercept_normal": [1.0, 2.0],
                    "damage_factor_normal": [3.0, 4.0],
                    "damage_intercept_shock": [5.0, 6.0],
                    "damage_factor_shock": [7.0, 8.0],
                },
                "insurance_decisions": [
                    {"sector_index": 0, "insured": False},
                    {"sector_index": 1, "insured": False},
                ],
            }
        ]
    )

    assert snapshots[0].draws is None


def test_scenario_loader_allows_vn_damage_settlement_snapshots_without_explicit_draws() -> None:
    scenario = load_scenario_from_mapping(_vn_period_scenario())

    assert scenario.vn_damage_settlement_snapshots[0].draws is None


def test_vn_rule_runner_draws_missing_damage_settlement_normals_from_context() -> None:
    rng = create_rng(123)
    first_trigger = rand_normal_standard(rng)
    first_amount = rand_normal_standard(rng)
    second_trigger = rand_normal_standard(rng)
    second_amount = rand_normal_standard(rng)

    result = run_vn_settlement_period_from_mapping(_vn_period_scenario())

    application = result.damage_settlement_applications[0]
    assert application.damage_result.trigger_draws == [first_trigger, second_trigger]
    assert application.damage_result.amount_draws == [first_amount, second_amount]
    assert application.damage_result.damages == [
        5.0 + 2.0 * first_amount if 0.8 > first_trigger else 0.0,
        7.0 + 3.0 * second_amount if 0.2 > second_trigger else 0.0,
    ]


def test_vn_multi_period_runner_continues_missing_damage_draw_stream() -> None:
    rng = create_rng(123)
    first_period_draws = [rand_normal_standard(rng) for _ in range(4)]
    second_period_draws = [rand_normal_standard(rng) for _ in range(4)]

    result = run_vn_settlement_multi_period_from_mappings(
        [
            _vn_period_scenario(5, policyholder_id=21, rng_seed=123),
            _vn_period_scenario(6, policyholder_id=22, rng_seed=123),
        ]
    )

    first_application = result.period_results[0].damage_settlement_applications[0]
    second_application = result.period_results[1].damage_settlement_applications[0]
    assert first_application.damage_result.trigger_draws == [
        first_period_draws[0],
        first_period_draws[2],
    ]
    assert first_application.damage_result.amount_draws == [
        first_period_draws[1],
        first_period_draws[3],
    ]
    assert second_application.damage_result.trigger_draws == [
        second_period_draws[0],
        second_period_draws[2],
    ]
    assert second_application.damage_result.amount_draws == [
        second_period_draws[1],
        second_period_draws[3],
    ]
