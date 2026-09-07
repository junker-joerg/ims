from pathlib import Path


ROOT = Path(__file__).parents[1]
PLAN = (
    ROOT
    / "docs"
    / "plans"
    / "ims_2x_strategy_assignment_vu_snapshot_materialization_contract_plan.md"
)
MIGRATION = (
    ROOT
    / "docs"
    / "migration"
    / "ims_2x_strategy_assignment_vu_snapshot_materialization_contract.md"
)


def test_pr118_documentation_records_origin_scope_and_closed_boundaries() -> None:
    plan = PLAN.read_text(encoding="utf-8")
    migration = MIGRATION.read_text(encoding="utf-8")

    for source_symbol in ("Vrvu01", "Vrvu04", "Vrvu07", "Vrvu10"):
        assert source_symbol in plan
        assert source_symbol in migration
    assert "IMS.E" in plan
    assert "acht bestehende Snapshottypen" in migration
    assert "kein VU-Eingabeformat" in migration
    assert "keinen Snapshotloader" in migration
    assert "Simulation" in plan
    assert "historische Vollgleichheit" in migration
    assert "/api/strategies/assignment-vu-snapshot-materialization-contract" in migration


def test_pr118_documentation_is_linked_from_strategy_and_document_indexes() -> None:
    plan_index = (ROOT / "docs" / "plans" / "README.md").read_text(encoding="utf-8")
    migration_index = (ROOT / "docs" / "migration" / "README.md").read_text(encoding="utf-8")
    strategy_index = (ROOT / "docs" / "strategy" / "README.md").read_text(encoding="utf-8")

    assert PLAN.name in plan_index
    assert MIGRATION.name in migration_index
    assert MIGRATION.name in strategy_index
