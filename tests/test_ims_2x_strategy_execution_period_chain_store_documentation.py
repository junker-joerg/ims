from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PLAN = (
    ROOT
    / "docs"
    / "plans"
    / "ims_2x_strategy_execution_period_chain_store_plan.md"
)
MIGRATION = (
    ROOT
    / "docs"
    / "migration"
    / "ims_2x_strategy_execution_period_chain_store.md"
)


def test_pr137_plan_and_mapping_define_immutable_store_boundary() -> None:
    plan = PLAN.read_text(encoding="utf-8")
    migration = MIGRATION.read_text(encoding="utf-8")
    normalized = " ".join((plan + migration).split())

    assert "PR137 umgesetzt" in plan
    assert "`SIMLAENGE = 100`" in normalized
    assert "`explicit_storage_release = true`" in normalized
    assert "idempotenten Replay" in normalized
    assert "serverseitig" in normalized
    assert "vor und nach" in normalized
    assert "keine historische RNG- oder Vollgleichheitsbehauptung" in normalized
    assert "`incomming/` bleibt unversioniert" in plan
    assert "PR138" in normalized


def test_pr137_sources_are_indexed() -> None:
    plans_index = (ROOT / "docs" / "plans" / "README.md").read_text(
        encoding="utf-8"
    )
    migration_index = (ROOT / "docs" / "migration" / "README.md").read_text(
        encoding="utf-8"
    )
    strategy_index = (ROOT / "docs" / "strategy" / "README.md").read_text(
        encoding="utf-8"
    )

    assert PLAN.name in plans_index
    assert MIGRATION.name in migration_index
    assert MIGRATION.name in strategy_index
