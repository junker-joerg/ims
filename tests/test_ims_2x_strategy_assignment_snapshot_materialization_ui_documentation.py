from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN = (
    ROOT
    / "docs"
    / "plans"
    / "ims_2x_strategy_assignment_snapshot_materialization_ui_plan.md"
)
MIGRATION = (
    ROOT
    / "docs"
    / "migration"
    / "ims_2x_strategy_assignment_snapshot_materialization_ui.md"
)
FRONTEND = ROOT / "frontend" / "src" / "main.tsx"


def test_pr117_plan_keeps_preview_transient_and_execution_closed() -> None:
    text = PLAN.read_text(encoding="utf-8")

    assert "PR117" in text
    assert "IMS.E" in text
    assert "siebten Strategie-Tab `VN-Snapshots`" in text
    assert "keine Bearbeitung eines bereits materialisierten Snapshots" in text
    assert "keine Speicherung" in text
    assert "keine Run-Control-, Runner- oder Simulationskopplung" in text
    assert "keine historische RNG- oder Vollgleichheitsbehauptung" in text
    assert "PR118" in text


def test_pr117_migration_documents_period_and_lifetime_boundaries() -> None:
    text = MIGRATION.read_text(encoding="utf-8")

    assert "POST /api/strategies/assignment-snapshot-materialization" in text
    assert "Periode 1" in text
    assert "initial_decisions" in text
    assert "fluechtigen React-Zustand" in text
    assert "partial_results_returned = false" in text
    assert "persistence_performed = false" in text
    assert "runner_invoked = false" in text
    assert "simulation_performed = false" in text


def test_pr117_frontend_exposes_readonly_materialized_snapshot_preview() -> None:
    source = FRONTEND.read_text(encoding="utf-8")

    assert 'data-testid="strategy-snapshot-materialization-preview"' in source
    assert "/api/strategies/assignment-snapshot-materialization-contract" in source
    assert "strategySnapshotMaterializationContract?.operation.materialization_endpoint" in source
    assert "VN-Snapshots anzeigen" in source
    assert "Typisierte Eingabevorschau fuer eine VN-Regelperiode" in source
    assert "Strategieparameter" in source
    assert "Ziehungen und Auswahl" in source
    assert "Markt und Historie" in source
    assert "Schock und Kosten" in source
    assert "persistence_performed" in source
    assert "runner_invoked" in source
    assert "simulation_performed" in source
    assert "localStorage" not in source


def test_pr117_documents_are_indexed() -> None:
    plans_index = (ROOT / "docs" / "plans" / "README.md").read_text(
        encoding="utf-8"
    )
    migration_index = (ROOT / "docs" / "migration" / "README.md").read_text(
        encoding="utf-8"
    )
    strategy_index = (ROOT / "docs" / "strategy" / "README.md").read_text(
        encoding="utf-8"
    )

    assert "ims_2x_strategy_assignment_snapshot_materialization_ui_plan.md" in plans_index
    assert "ims_2x_strategy_assignment_snapshot_materialization_ui.md" in migration_index
    assert "PR117 VN-Snapshots in der Workbench" in strategy_index
