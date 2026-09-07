from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN = (
    ROOT
    / "docs"
    / "plans"
    / "ims_2x_strategy_assignment_snapshot_materialization_validation_plan.md"
)
MIGRATION = (
    ROOT
    / "docs"
    / "migration"
    / "ims_2x_strategy_assignment_snapshot_materialization_validation.md"
)


def test_pr115_plan_keeps_snapshot_creation_and_execution_closed() -> None:
    text = PLAN.read_text(encoding="utf-8")

    assert "PR115" in text
    assert "IMS.E" in text
    assert "Vrvn01" in text
    assert "Vrvn06" in text
    assert "keine Teilfreigabe" in text
    assert "kein Aufruf von `vn_insurance_rule_snapshot_from_mapping`" in text
    assert "keine Snapshot-Materialisierung" in text
    assert "kein Simulationsstart" in text
    assert "keine historische RNG- oder Vollgleichheitsbehauptung" in text
    assert "PR116" in text


def test_pr115_migration_documents_period_and_nested_validation() -> None:
    text = MIGRATION.read_text(encoding="utf-8")

    assert "base_context_valid = false" in text
    assert "initial_decisions" in text
    assert "Fallback-Ziehungen" in text
    assert "Historie liegt vor der Kontextperiode" in text
    assert "Schockstichprobengroesse" in text
    assert "nested_loader_results_retained = false" in text
    assert "snapshot_loader_invocation_performed = false" in text
    assert "keine Runner-Kopplung" in text
    assert "keine historische" in text


def test_pr115_documents_are_indexed() -> None:
    plans_index = (ROOT / "docs" / "plans" / "README.md").read_text(
        encoding="utf-8"
    )
    migration_index = (ROOT / "docs" / "migration" / "README.md").read_text(
        encoding="utf-8"
    )
    strategy_index = (ROOT / "docs" / "strategy" / "README.md").read_text(
        encoding="utf-8"
    )

    assert (
        "ims_2x_strategy_assignment_snapshot_materialization_validation_plan.md"
        in plans_index
    )
    assert (
        "ims_2x_strategy_assignment_snapshot_materialization_validation.md"
        in migration_index
    )
    assert "PR115 Materialisierungseingang validieren" in strategy_index
