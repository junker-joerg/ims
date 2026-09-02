from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN = (
    ROOT
    / "docs"
    / "plans"
    / "ims_2x_strategy_assignment_snapshot_translation_plan.md"
)
MIGRATION = (
    ROOT
    / "docs"
    / "migration"
    / "ims_2x_strategy_assignment_snapshot_translation.md"
)


def test_pr110_plan_keeps_materialization_and_execution_closed() -> None:
    text = PLAN.read_text(encoding="utf-8")

    assert "PR110" in text
    assert "IMSDATA.C" in text
    assert "IMS.E" in text
    assert "Alle zehn VU- und sechs VN-Katalogstrategien" in text
    assert "Snapshot-Loader werden nicht aufgerufen" in text
    assert "keine Materialisierung" in text
    assert "kein Simulationsstart" in text
    assert "keine historische Vollgleichheitsbehauptung" in text
    assert "PR111" in text


def test_pr110_migration_documents_mapping_and_unknown_context() -> None:
    text = MIGRATION.read_text(encoding="utf-8")

    assert "ACTION.st" in text
    assert "Vuauini" in text
    assert "Vnauini" in text
    assert "VURandomUniformRuleSnapshot" in text
    assert "VUForeignInfoRuleSnapshot" in text
    assert "VNInsuranceRuleSnapshot" in text
    assert "unresolved_snapshot_fields" in text
    assert "snapshots_created" in text
    assert "keine Behauptung historischer RNG- oder Vollgleichheit" in text


def test_pr110_documents_are_indexed() -> None:
    plans_index = (ROOT / "docs" / "plans" / "README.md").read_text(
        encoding="utf-8"
    )
    migration_index = (ROOT / "docs" / "migration" / "README.md").read_text(
        encoding="utf-8"
    )
    strategy_index = (ROOT / "docs" / "strategy" / "README.md").read_text(
        encoding="utf-8"
    )

    assert "ims_2x_strategy_assignment_snapshot_translation_plan.md" in plans_index
    assert "ims_2x_strategy_assignment_snapshot_translation.md" in migration_index
    assert "PR110 Snapshot-Bauplaene" in strategy_index
