from ims.engine.context import SimulationContext
from ims.engine.vn_rule_runner import VNSettlementPeriodRunResult, run_vn_settlement_period
from ims.model.entities import Insurer, Policyholder
from ims.model.vn_rules import VNSectorSettlementDecision, VNSettlementSnapshot


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


def test_vn_rule_runner_allows_empty_snapshot_list() -> None:
    result = run_vn_settlement_period(
        SimulationContext(period=2, max_periods=3),
        [Insurer(entity_id=10)],
        [Policyholder(entity_id=20)],
    )

    assert result.period == 2
    assert result.total_settlement_applications == 0
    assert result.settlement_applications == []
