from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN = (
    ROOT
    / "docs"
    / "plans"
    / "ims_2x_strategy_assignment_snapshot_context_plan.md"
)
MIGRATION = (
    ROOT
    / "docs"
    / "migration"
    / "ims_2x_strategy_assignment_snapshot_context.md"
)


def test_pr112_plan_keeps_context_validation_non_executing() -> None:
    text = PLAN.read_text(encoding="utf-8")

    assert "PR112" in text
    assert "IMSDATA.C" in text
    assert "IMS.E" in text
    assert "18 offenen Feldnamen" in text
    assert "keine Verwendung der gelieferten Kontextwerte" in text
    assert "kein Aufruf eines Snapshot-Loaders" in text
    assert "keine Snapshot-Materialisierung" in text
    assert "kein Simulationsstart" in text
    assert "keine historische RNG- oder Vollgleichheitsbehauptung" in text
    assert "PR113" in text


def test_pr112_migration_documents_sources_nulls_and_validation_boundary() -> None:
    text = MIGRATION.read_text(encoding="utf-8")

    assert "unresolved_snapshot_fields" in text
    assert "Zufallsziehungen" in text
    assert "Periodenfinanzierung" in text
    assert "Vorperiode" in text
    assert "keine automatische" in text
    assert "explicitly_open_value_count" in text
    assert "snapshot_materialization_ready" in text
    assert "regelabhaengigen VN-Ziehungs-" in text
    assert "Markt- und Historienstrukturen" in text
    assert "keine Behauptung" in text


def test_pr112_documents_are_indexed() -> None:
    plans_index = (ROOT / "docs" / "plans" / "README.md").read_text(
        encoding="utf-8"
    )
    migration_index = (ROOT / "docs" / "migration" / "README.md").read_text(
        encoding="utf-8"
    )
    strategy_index = (ROOT / "docs" / "strategy" / "README.md").read_text(
        encoding="utf-8"
    )

    assert "ims_2x_strategy_assignment_snapshot_context_plan.md" in plans_index
    assert "ims_2x_strategy_assignment_snapshot_context.md" in migration_index
    assert "PR112 Snapshot-Kontextvertrag" in strategy_index
