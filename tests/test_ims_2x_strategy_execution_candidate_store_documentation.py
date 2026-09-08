from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs" / "plans" / "ims_2x_strategy_execution_candidate_store_plan.md"
MIGRATION = (
    ROOT
    / "docs"
    / "migration"
    / "ims_2x_strategy_execution_candidate_store.md"
)


def test_pr127_plan_documents_release_integrity_and_boundaries() -> None:
    text = PLAN.read_text(encoding="utf-8")

    assert "PR127" in text
    assert "expliziter Freigabe" in text
    assert "serverseitig erneut" in text
    assert "vor dem Schreiben" in text
    assert "zweite Digest-Pruefung" in text
    assert "reinem `INSERT`" in text
    assert "idempotent" in text
    assert "PR128" in text
    assert "kein Runner" in text
    assert "keine Simulation" in text
    assert "keine historische RNG- oder Vollgleichheitsbehauptung" in text
    assert "`incomming/` bleibt unversioniert" in text


def test_pr127_mapping_names_origin_implementation_and_open_work() -> None:
    text = MIGRATION.read_text(encoding="utf-8")

    assert "`Vrvu01` bis `Vrvu10`" in text
    assert "`Vrvn01` bis `Vrvn06`" in text
    assert "`ims.api.strategy_execution_candidate_store`" in text
    assert "keine historische Speichersemantik" in text
    assert "keinen Update- oder Delete-Pfad" in text
    assert "PR128" in text
    assert "PR129" in text
    assert "PR130" in text


def test_pr127_is_linked_from_plan_migration_and_strategy_indexes() -> None:
    plan_index = (ROOT / "docs" / "plans" / "README.md").read_text(
        encoding="utf-8"
    )
    migration_index = (ROOT / "docs" / "migration" / "README.md").read_text(
        encoding="utf-8"
    )
    strategy_index = (ROOT / "docs" / "strategy" / "README.md").read_text(
        encoding="utf-8"
    )

    assert "ims_2x_strategy_execution_candidate_store_plan.md" in plan_index
    assert "ims_2x_strategy_execution_candidate_store.md" in migration_index
    assert "ims_2x_strategy_execution_candidate_store.md" in strategy_index
