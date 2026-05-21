import pytest

from ims.model.entities import Insurer, Policyholder
from ims.model.vn_damage_rules import VNDamageRuleDraws, VNDamageRuleParameters, VNDamageRuleResult
from ims.model.vn_rules import (
    VNDamageSettlementSnapshot,
    VNInsuranceDecision,
    VNSectorSettlementDecision,
    VNSettlementSnapshot,
    apply_vn_damage_settlement_snapshot,
    apply_vn_settlement_snapshot,
    apply_vn_settlement_snapshots,
    build_vn_settlement_snapshot_from_damage_result,
    load_vn_damage_settlement_snapshots_from_mapping,
    load_vn_insurance_decisions_from_mapping,
    load_vn_settlement_snapshots_from_mapping,
)


def test_vn_settlement_updates_insured_and_self_insured_sectors() -> None:
    insurer = Insurer(
        entity_id=10,
        premiums_current=99.0,
        premiums_current_sector=[12.0, 20.0],
        reserves_current=[100.0, 200.0],
        policyholders_current_sector=[3.0, 4.0],
        claims_count_current=[1, 2],
        claims_sum_current=[5.0, 7.0],
    )
    policyholder = Policyholder(entity_id=30)
    snapshot = VNSettlementSnapshot(
        policyholder_id=30,
        previous_wealth=1000.0,
        previous_wealth_sector=[600.0, 400.0],
        decisions=[
            VNSectorSettlementDecision(
                sector_index=0,
                insured=True,
                insurer_id=10,
                premium=None,
                damage=4.0,
            ),
            VNSectorSettlementDecision(
                sector_index=1,
                insured=False,
                damage=9.0,
            ),
        ],
    )

    result = apply_vn_settlement_snapshot(policyholder, [insurer], snapshot)

    assert result.chosen_insurer_sector_current == [10, None]
    assert result.insured_current_sector == [1.0, 0.0]
    assert result.paid_premium_current == [12.0, 0.0]
    assert result.self_damage_current == [0.0, 9.0]
    assert result.claim_sum_current == [4.0, 9.0]
    assert result.end_wealth_sector_current == [584.0, 391.0]
    assert result.end_wealth_current == 975.0
    assert policyholder.chosen_insurer_current == 10
    assert policyholder.insured_current == 1.0
    assert policyholder.end_wealth_current == 975.0
    assert insurer.reserves_current == [108.0, 200.0]
    assert insurer.policyholders_current_sector == [4.0, 4.0]
    assert insurer.policyholders_current == 8.0
    assert insurer.claims_count_current == [2, 2]
    assert insurer.claims_sum_current == [9.0, 7.0]


def test_vn_settlement_uses_explicit_premium_and_counts_no_zero_damage_claim() -> None:
    insurer = Insurer(
        entity_id=11,
        premiums_current_sector=[12.0, 20.0],
        reserves_current=[50.0, 60.0],
        policyholders_current_sector=[0.0, 0.0],
        claims_count_current=[0, 0],
        claims_sum_current=[0.0, 0.0],
    )
    policyholder = Policyholder(entity_id=31)
    snapshot = VNSettlementSnapshot(
        policyholder_id=31,
        previous_wealth=100.0,
        decisions=[
            VNSectorSettlementDecision(
                sector_index=0,
                insured=True,
                insurer_id=11,
                premium=8.0,
                damage=0.0,
            ),
            VNSectorSettlementDecision(
                sector_index=1,
                insured=True,
                insurer_id=11,
                premium=9.0,
                damage=3.0,
            ),
        ],
    )

    result = apply_vn_settlement_snapshot(policyholder, [insurer], snapshot)

    assert result.paid_premium_current == [8.0, 9.0]
    assert result.claim_sum_current == [0.0, 3.0]
    assert result.end_wealth_current == 80.0
    assert insurer.reserves_current == [58.0, 66.0]
    assert insurer.claims_count_current == [0, 1]
    assert insurer.claims_sum_current == [0.0, 3.0]


def test_vn_settlement_preserves_scalar_policyholder_count_when_sector_vector_absent() -> None:
    insurer = Insurer(
        entity_id=12,
        premiums_current_sector=[7.0, 9.0],
        reserves_current=[20.0, 30.0],
        policyholders_current=5.0,
        claims_count_current=[0, 0],
        claims_sum_current=[0.0, 0.0],
    )
    policyholder = Policyholder(entity_id=32)
    snapshot = VNSettlementSnapshot(
        policyholder_id=32,
        previous_wealth=100.0,
        decisions=[
            VNSectorSettlementDecision(
                sector_index=0,
                insured=True,
                insurer_id=12,
                damage=2.0,
            ),
            VNSectorSettlementDecision(sector_index=1, insured=False, damage=0.0),
        ],
    )

    apply_vn_settlement_snapshot(policyholder, [insurer], snapshot)

    assert insurer.policyholders_current_sector == [6.0, 0.0]
    assert insurer.policyholders_current == 6.0


def test_vn_settlement_snapshot_can_be_built_from_damage_result_and_insurance_decisions() -> None:
    snapshot = build_vn_settlement_snapshot_from_damage_result(
        policyholder_id=33,
        previous_wealth=200.0,
        previous_wealth_sector=[120.0, 80.0],
        insurance_decisions=[
            VNInsuranceDecision(sector_index=1, insured=False),
            VNInsuranceDecision(sector_index=0, insured=True, insurer_id=13, premium=11.0),
        ],
        damage_result=VNDamageRuleResult(
            damages=[4.0, 6.0],
            triggered=[True, True],
            trigger_draws=[0.1, 0.2],
            amount_draws=[0.3, 0.4],
        ),
    )

    assert snapshot.policyholder_id == 33
    assert snapshot.previous_wealth_sector == [120.0, 80.0]
    assert [decision.sector_index for decision in snapshot.decisions] == [0, 1]
    assert snapshot.decisions[0].insured is True
    assert snapshot.decisions[0].insurer_id == 13
    assert snapshot.decisions[0].premium == 11.0
    assert snapshot.decisions[0].damage == 4.0
    assert snapshot.decisions[1].insured is False
    assert snapshot.decisions[1].damage == 6.0


def test_vn_settlement_snapshot_builder_normalizes_previous_wealth_sector() -> None:
    snapshot = build_vn_settlement_snapshot_from_damage_result(
        policyholder_id=34,
        previous_wealth=200.0,
        previous_wealth_sector=[120.0],
        insurance_decisions=[
            VNInsuranceDecision(sector_index=0, insured=False),
            VNInsuranceDecision(sector_index=1, insured=False),
        ],
        damage_result=VNDamageRuleResult(
            damages=[4.0, 6.0],
            triggered=[True, True],
            trigger_draws=[0.1, 0.2],
            amount_draws=[0.3, 0.4],
        ),
    )
    policyholder = Policyholder(entity_id=34)

    result = apply_vn_settlement_snapshot(policyholder, [], snapshot)

    assert snapshot.previous_wealth_sector == [120.0, 120.0]
    assert result.end_wealth_sector_current == [116.0, 114.0]


def test_vn_damage_settlement_snapshot_applies_damage_rule_and_settlement() -> None:
    insurer = Insurer(
        entity_id=14,
        premiums_current_sector=[8.0, 9.0],
        reserves_current=[100.0, 200.0],
        policyholders_current_sector=[2.0, 3.0],
        claims_count_current=[0, 1],
        claims_sum_current=[0.0, 5.0],
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
        draws=VNDamageRuleDraws(trigger_draws=[0.6, 0.5], amount_draws=[1.5, 2.0]),
        insurance_decisions=[
            VNInsuranceDecision(sector_index=0, insured=True, insurer_id=14),
            VNInsuranceDecision(sector_index=1, insured=False),
        ],
        previous_wealth=1000.0,
        previous_wealth_sector=[600.0, 400.0],
    )

    application = apply_vn_damage_settlement_snapshot(policyholder, [insurer], snapshot)

    assert application.policyholder_id == 35
    assert application.damage_result.damages == [13.0, 0.0]
    assert application.settlement_result.paid_premium_current == [8.0, 0.0]
    assert application.settlement_result.end_wealth_current == 979.0
    assert policyholder.claim_sum_current == [13.0, 0.0]
    assert insurer.reserves_current == [95.0, 200.0]
    assert insurer.policyholders_current_sector == [3.0, 3.0]
    assert insurer.claims_count_current == [1, 1]
    assert insurer.claims_sum_current == [13.0, 5.0]


def test_vn_settlement_snapshots_reject_duplicate_or_unknown_targets() -> None:
    policyholders = [Policyholder(entity_id=40)]
    insurers = [Insurer(entity_id=50)]
    snapshot = VNSettlementSnapshot(
        policyholder_id=40,
        previous_wealth=10.0,
        decisions=[
            VNSectorSettlementDecision(sector_index=0, insured=False, damage=1.0),
            VNSectorSettlementDecision(sector_index=1, insured=False, damage=2.0),
        ],
    )

    with pytest.raises(ValueError, match="duplicate VN settlement snapshot"):
        apply_vn_settlement_snapshots(policyholders, insurers, [snapshot, snapshot])

    unknown_policyholder = VNSettlementSnapshot(
        policyholder_id=41,
        previous_wealth=10.0,
        decisions=snapshot.decisions,
    )
    with pytest.raises(ValueError, match="unknown policyholder"):
        apply_vn_settlement_snapshots(policyholders, insurers, [unknown_policyholder])

    unknown_insurer = VNSettlementSnapshot(
        policyholder_id=40,
        previous_wealth=10.0,
        decisions=[
            VNSectorSettlementDecision(sector_index=0, insured=True, insurer_id=51, damage=1.0),
            VNSectorSettlementDecision(sector_index=1, insured=False, damage=2.0),
        ],
    )
    with pytest.raises(ValueError, match="unknown insurer"):
        apply_vn_settlement_snapshots(policyholders, insurers, [unknown_insurer])


def test_vn_settlement_loader_validates_required_shape() -> None:
    snapshots = load_vn_settlement_snapshots_from_mapping(
        [
            {
                "policyholder_id": 60,
                "previous_wealth": 25.0,
                "previous_wealth_sector": [10.0, 15.0],
                "decisions": [
                    {"sector_index": 0, "insured": True, "insurer_id": 70, "premium": 3.0, "damage": 1.0},
                    {"sector_index": 1, "insured": False, "damage": 2.0},
                ],
            }
        ]
    )

    assert snapshots[0].policyholder_id == 60
    assert snapshots[0].previous_wealth_sector == [10.0, 15.0]
    assert snapshots[0].decisions[0].sector_index == 0
    assert snapshots[0].decisions[0].insured is True
    assert snapshots[0].decisions[1].insurer_id is None

    with pytest.raises(ValueError, match="exactly one decision"):
        load_vn_settlement_snapshots_from_mapping(
            [
                {
                    "policyholder_id": 60,
                    "previous_wealth": 25.0,
                    "decisions": [
                        {"sector_index": 0, "insured": False, "damage": 1.0},
                        {"sector_index": 0, "insured": False, "damage": 2.0},
                    ],
                }
            ]
        )


def test_vn_insurance_decision_loader_validates_required_shape() -> None:
    decisions = load_vn_insurance_decisions_from_mapping(
        [
            {"sector_index": 0, "insured": True, "insurer_id": 70, "premium": 3.0},
            {"sector_index": 1, "insured": False},
        ]
    )

    assert decisions[0].sector_index == 0
    assert decisions[0].insured is True
    assert decisions[0].insurer_id == 70
    assert decisions[0].premium == 3.0
    assert decisions[1].insured is False

    with pytest.raises(ValueError, match="require exactly one decision"):
        load_vn_insurance_decisions_from_mapping(
            [
                {"sector_index": 0, "insured": False},
                {"sector_index": 0, "insured": False},
            ]
        )


def test_vn_damage_settlement_loader_reads_explicit_snapshot() -> None:
    snapshots = load_vn_damage_settlement_snapshots_from_mapping(
        [
            {
                "policyholder_id": 80,
                "previous_wealth": 300.0,
                "previous_wealth_sector": [180.0],
                "damage_thresholds": [0.7, 0.4],
                "change_shock": True,
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
                    {"sector_index": 0, "insured": True, "insurer_id": 90, "premium": 3.0},
                    {"sector_index": 1, "insured": False},
                ],
            }
        ]
    )

    assert snapshots[0].policyholder_id == 80
    assert snapshots[0].previous_wealth_sector == [180.0, 180.0]
    assert snapshots[0].damage_thresholds == [0.7, 0.4]
    assert snapshots[0].change_shock is True
    assert snapshots[0].parameters.damage_factor_shock == [7.0, 8.0]
    assert snapshots[0].draws.amount_draws == [0.3, 0.4]
    assert snapshots[0].insurance_decisions[0].insurer_id == 90
