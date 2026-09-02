from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs" / "plans" / "ims_2x_strategy_assignment_draft_ui_plan.md"
MIGRATION = ROOT / "docs" / "migration" / "ims_2x_strategy_assignment_draft_ui.md"


def test_pr109_plan_keeps_editing_local_and_execution_closed() -> None:
    text = PLAN.read_text(encoding="utf-8")

    assert "PR109" in text
    assert "Vdefmd6" in text
    assert "POST /api/strategies/assignment-draft-validation" in text
    assert "keine Datei-, Browser- oder Datenbankspeicherung" in text
    assert "keine Uebersetzung in Regel-Snapshots" in text
    assert "keine Kopplung an Run-Control, Runner oder Simulation" in text
    assert "keine historische Vollgleichheitsbehauptung" in text
    assert "PR110" in text


def test_pr109_migration_maps_historical_fields_to_workbench() -> None:
    text = MIGRATION.read_text(encoding="utf-8")

    assert "IMSDATA.C" in text
    assert "ACTION.st" in text
    assert "IMS.E" in text
    assert "Vuauini" in text
    assert "Vnauini" in text
    assert "Position 1 und Position 2" in text
    assert "Browser-Neuladen verwirft den Entwurf" in text
    assert "weder Schreiben noch Snapshot-Erzeugung" in text
    assert "keine Simulation" in text


def test_pr109_documents_are_indexed() -> None:
    plans_index = (ROOT / "docs" / "plans" / "README.md").read_text(encoding="utf-8")
    migration_index = (ROOT / "docs" / "migration" / "README.md").read_text(encoding="utf-8")
    strategy_index = (ROOT / "docs" / "strategy" / "README.md").read_text(encoding="utf-8")

    assert "ims_2x_strategy_assignment_draft_ui_plan.md" in plans_index
    assert "ims_2x_strategy_assignment_draft_ui.md" in migration_index
    assert "PR109 Strategieentwurf in der Workbench" in strategy_index
