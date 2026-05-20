import pytest

from ims.model.entities import Insurer, Policyholder
from ims.model.vn_rules import (
    VNSectorSettlementDecision,
    VNSettlementSnapshot,
    apply_vn_settlement_snapshot,
    apply_vn_settlement_snapshots,
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
