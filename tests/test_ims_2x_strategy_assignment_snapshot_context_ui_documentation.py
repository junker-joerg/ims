from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN = (
    ROOT
    / "docs"
    / "plans"
    / "ims_2x_strategy_assignment_snapshot_context_ui_plan.md"
)
MIGRATION = (
    ROOT
    / "docs"
    / "migration"
    / "ims_2x_strategy_assignment_snapshot_context_ui.md"
)
FRONTEND = ROOT / "frontend" / "src" / "main.tsx"


def test_pr113_plan_keeps_context_local_and_execution_closed() -> None:
    text = PLAN.read_text(encoding="utf-8")

    assert "PR113" in text
    assert "IMSDATA.C" in text
    assert "IMS.E" in text
    assert "sechster Strategie-Tab `Kontext`" in text
    assert "keine vorbelegten Beispiel-, Default-" in text
    assert "keine Verwendung der gelieferten Kontextwerte" in text
    assert "kein Aufruf eines Snapshot-Loaders" in text
    assert "keine Snapshot-Materialisierung" in text
    assert "keine Run-Control-, Runner- oder Simulationskopplung" in text
    assert "keine historische RNG- oder Vollgleichheitsbehauptung" in text
    assert "PR114" in text


def test_pr113_migration_documents_field_errors_and_null_boundary() -> None:
    text = MIGRATION.read_text(encoding="utf-8")

    assert "ACTION.st" in text
    assert "unresolved_snapshot_fields" in text
    assert "fluechtiger React-Zustand" in text
    assert "Kontext anlegen" in text
    assert "context_value_missing" in text
    assert "context_value_shape_invalid" in text
    assert "bewusst als `null` markiert" in text
    assert "context_values_consumed = false" in text
    assert "snapshot_loader_invocation_performed = false" in text
    assert "kein materialisierbarer Snapshot" in text


def test_pr113_frontend_exposes_context_editor_and_existing_read_only_api() -> None:
    source = FRONTEND.read_text(encoding="utf-8")

    assert 'data-testid="strategy-snapshot-context-editor"' in source
    assert "/api/strategies/assignment-snapshot-context-contract" in source
    assert "strategySnapshotContextContract?.validation_endpoint" in source
    assert "Kontext anlegen" in source
    assert "Bewusst offen" in source
    assert "Kontext pruefen" in source
    assert "Werte verwendet:" in source
    assert "Loader:" in source
    assert "Keine Materialisierung" in source


def test_pr113_documents_are_indexed() -> None:
    plans_index = (ROOT / "docs" / "plans" / "README.md").read_text(
        encoding="utf-8"
    )
    migration_index = (ROOT / "docs" / "migration" / "README.md").read_text(
        encoding="utf-8"
    )
    strategy_index = (ROOT / "docs" / "strategy" / "README.md").read_text(
        encoding="utf-8"
    )

    assert "ims_2x_strategy_assignment_snapshot_context_ui_plan.md" in plans_index
    assert "ims_2x_strategy_assignment_snapshot_context_ui.md" in migration_index
    assert "PR113 Snapshot-Kontext in der Workbench" in strategy_index
