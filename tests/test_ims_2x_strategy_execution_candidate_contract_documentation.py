from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs" / "plans" / "ims_2x_strategy_execution_candidate_contract_plan.md"
MIGRATION = (
    ROOT
    / "docs"
    / "migration"
    / "ims_2x_strategy_execution_candidate_contract.md"
)


def test_pr124_documentation_records_sources_collections_and_boundaries() -> None:
    plan = PLAN.read_text(encoding="utf-8")
    migration = MIGRATION.read_text(encoding="utf-8")
    combined = f"{plan}\n{migration}"

    assert "PR124" in combined
    assert "IMS.E" in migration
    assert "`LoadedScenario`" in combined
    assert "`ims.engine.explicit_period_runner.run_loaded_explicit_period`" in plan
    assert "Acht VU-Regelsammlungen" in plan
    assert "`vn_insurance_rule_snapshots`" in migration
    assert "`vn_damage_settlement_snapshots`" in migration
    assert "`vn_settlement_snapshots`" in migration
    assert "keine Kandidatenvalidierung" in plan
    assert "keine Simulation" in plan
    assert "historische RNG- oder Vollgleichheitsbehauptung" in plan


def test_pr124_documentation_is_indexed_and_names_current_next_pr() -> None:
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
    assert "PR127" in PLAN.read_text(encoding="utf-8")
