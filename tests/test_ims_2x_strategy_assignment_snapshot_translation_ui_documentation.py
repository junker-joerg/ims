from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN = (
    ROOT
    / "docs"
    / "plans"
    / "ims_2x_strategy_assignment_snapshot_translation_ui_plan.md"
)
MIGRATION = (
    ROOT
    / "docs"
    / "migration"
    / "ims_2x_strategy_assignment_snapshot_translation_ui.md"
)


def test_pr111_plan_keeps_preview_read_only_and_execution_closed() -> None:
    text = PLAN.read_text(encoding="utf-8")

    assert "PR111" in text
    assert "IMSDATA.C" in text
    assert "IMS.E" in text
    assert "fuenfter Strategie-Tab `Bauplaene`" in text
    assert "keine Snapshot-Materialisierung" in text
    assert "keine Run-Control-, Runner- oder Simulationskopplung" in text
    assert "keine historische Vollgleichheitsbehauptung" in text
    assert "PR112" in text


def test_pr111_migration_documents_user_flow_and_visible_boundaries() -> None:
    text = MIGRATION.read_text(encoding="utf-8")

    assert "ACTION.st" in text
    assert "POST /api/strategies/assignment-snapshot-translation" in text
    assert "Bauplaene anzeigen" in text
    assert "React-Zustand" in text
    assert "Zufallsziehungen" in text
    assert "Zinssatz der Periode" in text
    assert "Defaults: nein" in text
    assert "Snapshots:" in text
    assert "keine Simulation" in text


def test_pr111_documents_are_indexed() -> None:
    plans_index = (ROOT / "docs" / "plans" / "README.md").read_text(
        encoding="utf-8"
    )
    migration_index = (ROOT / "docs" / "migration" / "README.md").read_text(
        encoding="utf-8"
    )
    strategy_index = (ROOT / "docs" / "strategy" / "README.md").read_text(
        encoding="utf-8"
    )

    assert "ims_2x_strategy_assignment_snapshot_translation_ui_plan.md" in plans_index
    assert "ims_2x_strategy_assignment_snapshot_translation_ui.md" in migration_index
    assert "PR111 Snapshot-Bauplaene in der Workbench" in strategy_index
