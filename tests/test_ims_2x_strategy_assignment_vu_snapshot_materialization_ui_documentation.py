from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN = (
    ROOT
    / "docs"
    / "plans"
    / "ims_2x_strategy_assignment_vu_snapshot_materialization_ui_plan.md"
)
MIGRATION = (
    ROOT
    / "docs"
    / "migration"
    / "ims_2x_strategy_assignment_vu_snapshot_materialization_ui.md"
)
FRONTEND = ROOT / "frontend" / "src" / "main.tsx"


def test_pr122_plan_keeps_vu_preview_transient_and_execution_closed() -> None:
    text = PLAN.read_text(encoding="utf-8")

    assert "PR122" in text
    assert "achter Strategie-Tab `VU-Snapshots`" in text
    assert "vorbereitete Eingaben fuer VU-Regeln" in text
    assert "keine Speicherung oder Browser-Persistenz" in text
    assert "keine Run-Control-, Runner- oder Simulationskopplung" in text
    assert "keine historische RNG- oder Vollgleichheitsbehauptung" in text
    assert "PR123" in text


def test_pr122_migration_documents_provenance_and_atomic_boundaries() -> None:
    text = MIGRATION.read_text(encoding="utf-8")

    assert "POST /api/strategies/assignment-vu-snapshot-materialization" in text
    assert "interest_rate" in text
    assert "active_policyholder_count" in text
    assert "policyholders_t_minus_2" in text
    assert "nicht automatisch aus dem Kontext kopiert" in text
    assert "state_provenance_validated = true" in text
    assert "state_values_consumed = false" in text
    assert "partial_results_returned = false" in text
    assert "runner_invoked = false" in text
    assert "simulation_performed = false" in text


def test_pr122_frontend_exposes_readonly_vu_snapshot_preview() -> None:
    source = FRONTEND.read_text(encoding="utf-8")

    assert 'strategyWorkbenchView === "vu-snapshots"' in source
    assert 'data-testid="strategy-vu-snapshot-materialization-preview"' in source
    assert "/api/strategies/assignment-vu-snapshot-materialization-validation-contract" in source
    assert "/api/strategies/assignment-vu-snapshot-state-contract" in source
    assert "/api/strategies/assignment-vu-snapshot-materialization-contract" in source
    assert "strategyVUMaterializationContract?.operation.materialization_endpoint" in source
    assert "Getrennten VU-Zustandsbeleg erfassen" in source
    assert "VU-Snapshots anzeigen" in source
    assert "Herkunftsabgleich" in source
    assert "Ziehungsherkunft" in source
    assert "state_provenance_validated" in source
    assert "state_values_consumed" in source
    assert "partial_results_returned" in source
    assert "persistence_performed" in source
    assert "runner_invoked" in source
    assert "simulation_performed" in source
    assert "localStorage" not in source


def test_pr122_documents_are_indexed() -> None:
    plans_index = (ROOT / "docs" / "plans" / "README.md").read_text(
        encoding="utf-8"
    )
    migration_index = (ROOT / "docs" / "migration" / "README.md").read_text(
        encoding="utf-8"
    )
    strategy_index = (ROOT / "docs" / "strategy" / "README.md").read_text(
        encoding="utf-8"
    )

    assert "ims_2x_strategy_assignment_vu_snapshot_materialization_ui_plan.md" in plans_index
    assert "ims_2x_strategy_assignment_vu_snapshot_materialization_ui.md" in migration_index
    assert "PR122 VU-Snapshots in der Workbench" in strategy_index
