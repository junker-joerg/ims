from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PLAN = (
    ROOT
    / "docs"
    / "plans"
    / "ims_2x_strategy_execution_period_chain_resolution_plan.md"
)
MIGRATION = (
    ROOT
    / "docs"
    / "migration"
    / "ims_2x_strategy_execution_period_chain_resolution.md"
)


def test_pr135_plan_and_mapping_define_atomic_resolution_boundary() -> None:
    plan = PLAN.read_text(encoding="utf-8")
    migration = MIGRATION.read_text(encoding="utf-8")
    normalized = " ".join((plan + migration).split())

    assert "PR135 umgesetzt" in plan
    assert "`SIMLAENGE = 100`" in normalized
    assert "simulation_context.period" in normalized
    assert "simulation_context.run_index" in normalized
    assert "simulation_context.max_periods" in normalized
    assert "BAV-, VU- und VN-Identitaeten" in normalized
    assert "keine neue oder geaenderte Fachlogik" in plan
    assert "keine historische RNG- oder Vollgleichheitsbehauptung" in plan
    assert "`incomming/` bleibt unversioniert" in plan
    assert "PR136" in normalized


def test_pr135_sources_are_indexed() -> None:
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
