from pathlib import Path


ROOT = Path(__file__).parents[1]
PLAN = (
    ROOT
    / "docs"
    / "plans"
    / "ims_2x_strategy_assignment_vu_snapshot_materialization_validation_plan.md"
)
MIGRATION = (
    ROOT
    / "docs"
    / "migration"
    / "ims_2x_strategy_assignment_vu_snapshot_materialization_validation.md"
)


def test_pr119_documentation_records_sources_policies_and_boundaries() -> None:
    plan = PLAN.read_text(encoding="utf-8")
    migration = MIGRATION.read_text(encoding="utf-8")

    for source in ("A1[1]", "A1[2]", "A1[3]", "aspiration_sector_1/2"):
        assert source in migration
    assert "[0.0, 1.0)" in plan
    assert "reject-loader-and-runner-fallbacks-v1" in migration
    assert "threshold_values_cross_checked_against_actor_state = false" in migration
    assert "Kein VU-Snapshotloader" in migration
    assert "Simulation bleiben gesperrt" in migration
    assert "Vollgleichheit" in migration


def test_pr119_documentation_is_linked_from_all_strategy_indexes() -> None:
    plan_index = (ROOT / "docs" / "plans" / "README.md").read_text(encoding="utf-8")
    migration_index = (ROOT / "docs" / "migration" / "README.md").read_text(encoding="utf-8")
    strategy_index = (ROOT / "docs" / "strategy" / "README.md").read_text(encoding="utf-8")

    assert PLAN.name in plan_index
    assert MIGRATION.name in migration_index
    assert MIGRATION.name in strategy_index
