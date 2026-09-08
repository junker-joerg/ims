from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN = (
    ROOT
    / "docs"
    / "plans"
    / "ims_2x_strategy_execution_candidate_validation_plan.md"
)
MIGRATION = (
    ROOT
    / "docs"
    / "migration"
    / "ims_2x_strategy_execution_candidate_validation.md"
)


def test_pr125_documentation_records_shared_sources_and_vn_process_boundary() -> None:
    plan = PLAN.read_text(encoding="utf-8")
    migration = MIGRATION.read_text(encoding="utf-8")
    combined = f"{plan}\n{migration}"

    assert "PR125" in combined
    assert "genau einen Strategieentwurf" in plan
    assert "genau einen\nSnapshotkontext" in plan
    assert "`damage_settlement_snapshots`" in plan
    assert "`insurance_decisions`" in plan
    assert "`information_cost`" in plan
    assert "Reine `settlement_snapshots` bleiben gesperrt" in plan
    assert "`scenario_profile_resolved = false`" in migration
    assert "keine Snapshotloader" in plan
    assert "keine Simulation" in plan
    assert "historische RNG- oder Vollgleichheitsbehauptung" in plan


def test_pr125_documentation_is_indexed_and_names_pr126() -> None:
    plan_index = (ROOT / "docs" / "plans" / "README.md").read_text(
        encoding="utf-8"
    )
    migration_index = (ROOT / "docs" / "migration" / "README.md").read_text(
        encoding="utf-8"
    )
    strategy_index = (ROOT / "docs" / "strategy" / "README.md").read_text(
        encoding="utf-8"
    )

    assert PLAN.name in plan_index
    assert MIGRATION.name in migration_index
    assert MIGRATION.name in strategy_index
    assert "PR126" in PLAN.read_text(encoding="utf-8")
