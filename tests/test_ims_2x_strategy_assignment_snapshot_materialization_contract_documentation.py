from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN = (
    ROOT
    / "docs"
    / "plans"
    / "ims_2x_strategy_assignment_snapshot_materialization_contract_plan.md"
)
MIGRATION = (
    ROOT
    / "docs"
    / "migration"
    / "ims_2x_strategy_assignment_snapshot_materialization_contract.md"
)


def test_pr114_plan_keeps_materialization_and_execution_closed() -> None:
    text = PLAN.read_text(encoding="utf-8")

    assert "PR114" in text
    assert "IMS.E" in text
    assert "neun explizite Loaderformen" in text
    assert "keine Aenderung des generischen PR112-Kontextvalidators" in text
    assert "kein Aufruf von `vn_insurance_rule_snapshot_from_mapping`" in text
    assert "keine Snapshot-Materialisierung" in text
    assert "kein Simulationsstart" in text
    assert "keine historische RNG- oder Vollgleichheitsbehauptung" in text
    assert "PR115" in text
    assert "PR116" in text


def test_pr114_migration_documents_all_six_vn_rule_shapes() -> None:
    text = MIGRATION.read_text(encoding="utf-8")

    for rule_name in ("Vrvn01", "Vrvn02", "Vrvn03", "Vrvn04", "Vrvn05", "Vrvn06"):
        assert rule_name in text
    assert "initial_decisions" in text
    assert "Fallback-Ziehungen" in text
    assert "VU-Werbebloecke" in text
    assert "Suchhistorie" in text
    assert "Stichproben-Ziehungslisten" in text
    assert "context_validator_uses_nested_contract = false" in text
    assert "keine Runner-Kopplung" in text
    assert "historische Vollgleichheit" in text


def test_pr114_documents_are_indexed() -> None:
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
        "ims_2x_strategy_assignment_snapshot_materialization_contract_plan.md"
        in plans_index
    )
    assert (
        "ims_2x_strategy_assignment_snapshot_materialization_contract.md"
        in migration_index
    )
    assert "PR114 Materialisierungsvertrag" in strategy_index
