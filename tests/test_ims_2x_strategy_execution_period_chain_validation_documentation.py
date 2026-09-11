from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PLAN = (
    ROOT
    / "docs"
    / "plans"
    / "ims_2x_strategy_execution_period_chain_validation_plan.md"
)
MIGRATION = (
    ROOT
    / "docs"
    / "migration"
    / "ims_2x_strategy_execution_period_chain_validation.md"
)


def test_pr134_plan_and_mapping_define_atomic_validation_boundary() -> None:
    plan = PLAN.read_text(encoding="utf-8")
    migration = MIGRATION.read_text(encoding="utf-8")
    normalized = " ".join((plan + migration).split())

    assert "PR134 umgesetzt" in plan
    assert "`SIMLAENGE = 100`" in normalized
    assert "1..max_periods" in normalized
    assert "candidate_id" in normalized
    assert "content_digest" in normalized
    assert "Teil" in normalized
    assert "keine neue oder geaenderte Fachlogik" in plan
    assert "keine historische RNG- oder Vollgleichheitsbehauptung" in plan
    assert "`incomming/` bleibt unversioniert" in plan
    assert "PR135" in normalized


def test_pr134_sources_are_indexed() -> None:
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
