from ims.analysis.aggregates import AggregateSnapshot, collect_basic_aggregates
from ims.engine.context import SimulationContext
from ims.io.scenario_loader import load_scenario
from ims.model.entities import BAV, Insurer, Policyholder


def test_collect_basic_aggregates_from_minimal_fixture() -> None:
    scenario = load_scenario("tests/fixtures/minimal_scenario.json")

    snapshot = collect_basic_aggregates(
        scenario.context,
        scenario.bav,
        scenario.insurers,
        scenario.policyholders,
    )

    assert snapshot == AggregateSnapshot(
        period=0,
        logtime=0,
        active_insurers=1,
        active_policyholders=1,
        assigned_policyholders=1,
        unassigned_policyholders=0,
    )


def test_collect_basic_aggregates_with_inactive_and_unassigned_entities() -> None:
    context = SimulationContext(period=2, logtime=7, max_periods=12, run_index=1, rng_seed=123)
    bav = BAV(entity_id=100, name="Basis-BAV")
    insurers = [
        Insurer(entity_id=200, name="Aktive VU", active=True),
        Insurer(entity_id=201, name="Inaktive VU", active=False),
    ]
    policyholders = [
        Policyholder(entity_id=300, name="Aktiver zugeordnet", active=True, insurer_id=200),
        Policyholder(entity_id=301, name="Inaktiver zugeordnet", active=False, insurer_id=200),
        Policyholder(entity_id=302, name="Aktiver unzugeordnet", active=True, insurer_id=None),
    ]

    snapshot = collect_basic_aggregates(context, bav, insurers, policyholders)

    assert snapshot == AggregateSnapshot(
        period=2,
        logtime=7,
        active_insurers=1,
        active_policyholders=2,
        assigned_policyholders=2,
        unassigned_policyholders=1,
    )
