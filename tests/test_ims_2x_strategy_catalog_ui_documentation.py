from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
PLAN = REPO_ROOT / "docs" / "plans" / "ims_2x_strategy_catalog_ui_plan.md"
MIGRATION = REPO_ROOT / "docs" / "migration" / "ims_2x_strategy_catalog_ui.md"


def test_pr105_plan_keeps_strategy_catalog_read_only() -> None:
    normalized = PLAN.read_text(encoding="utf-8")

    assert "PR105" in normalized
    assert "GET /api/strategies/catalog" in normalized
    assert "sechzehn Regeln" in normalized
    assert "acht Familien" in normalized
    assert "keine Strategieauswahl" in normalized
    assert "keine Simulation" in normalized
    assert "keine historische Vollgleichheitsbehauptung" in normalized
    assert "PR106" in normalized


def test_pr105_mapping_names_historical_and_modern_boundaries() -> None:
    normalized = MIGRATION.read_text(encoding="utf-8")

    assert "`IMS.E`: `Vrvu01` bis `Vrvu10`" in normalized
    assert "`IMS.E`: `Vrvn01` bis `Vrvn06`" in normalized
    assert "`Vdefmd6`: historische Regelklassen" in normalized
    assert "`Vrvu10`" in normalized
    assert "`simulation_performed = false`" in normalized
    assert "`historical_full_equality_claim = false`" in normalized


def test_pr105_documents_are_linked_from_indexes() -> None:
    plans_index = (REPO_ROOT / "docs" / "plans" / "README.md").read_text(encoding="utf-8")
    migration_index = (REPO_ROOT / "docs" / "migration" / "README.md").read_text(encoding="utf-8")
    strategy_index = (REPO_ROOT / "docs" / "strategy" / "README.md").read_text(encoding="utf-8")

    assert "ims_2x_strategy_catalog_ui_plan.md" in plans_index
    assert "ims_2x_strategy_catalog_ui.md" in migration_index
    assert "PR105 Strategiekatalog in der Workbench" in strategy_index
