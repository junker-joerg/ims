from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN = (
    ROOT
    / "docs"
    / "plans"
    / "ims_2x_strategy_assignment_snapshot_materialization_plan.md"
)
MIGRATION = (
    ROOT
    / "docs"
    / "migration"
    / "ims_2x_strategy_assignment_snapshot_materialization.md"
)


def test_pr116_plan_documents_atomic_scope_and_closed_execution() -> None:
    text = PLAN.read_text(encoding="utf-8")

    assert "PR116" in text
    assert "IMS.E" in text
    assert "Vrvn01" in text
    assert "Vrvn06" in text
    assert "PR115-Fehler verhindern jeden Snapshot-Loader-Aufruf" in text
    assert "partial_results_returned = false" in text
    assert "kein Aufruf von `apply_vn_insurance_rule_snapshot`" in text
    assert "kein Simulationsstart" in text
    assert "keine historische RNG- oder Vollgleichheitsbehauptung" in text
    assert "PR117" in text


def test_pr116_migration_maps_periods_and_existing_snapshot_loader() -> None:
    text = MIGRATION.read_text(encoding="utf-8")

    assert "VNInsuranceRuleSnapshot" in text
    assert "vn_insurance_rule_snapshot_from_mapping" in text
    assert "In Periode 1 wird ausschliesslich `initial_decisions`" in text
    assert "Ab Periode 2" in text
    assert "keine teilweise verwertbare Ergebnisliste" in text
    assert "writes_performed = false" in text
    assert "execution_ready = false" in text
    assert "keine historische" in text


def test_pr116_documents_are_indexed() -> None:
    plans_index = (ROOT / "docs" / "plans" / "README.md").read_text(
        encoding="utf-8"
    )
    migration_index = (ROOT / "docs" / "migration" / "README.md").read_text(
        encoding="utf-8"
    )
    strategy_index = (ROOT / "docs" / "strategy" / "README.md").read_text(
        encoding="utf-8"
    )

    assert "ims_2x_strategy_assignment_snapshot_materialization_plan.md" in (
        plans_index
    )
    assert "ims_2x_strategy_assignment_snapshot_materialization.md" in (
        migration_index
    )
    assert "PR116 VN-Snapshots materialisieren" in strategy_index
