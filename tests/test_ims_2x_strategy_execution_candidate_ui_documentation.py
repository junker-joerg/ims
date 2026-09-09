from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs" / "plans" / "ims_2x_strategy_execution_candidate_ui_plan.md"
MIGRATION = ROOT / "docs" / "migration" / "ims_2x_strategy_execution_candidate_ui.md"


def test_pr128_plan_documents_read_only_candidate_observation() -> None:
    text = PLAN.read_text(encoding="utf-8")

    assert "PR128" in text
    assert "Kandidatenreife" in text
    assert "GET /api/strategies/execution-candidates" in text
    assert "ohne Tabellenanlage oder Schreibzugriff" in text
    assert "keinen" in text
    assert "Speicher-, Freigabe- oder Startbutton" in text
    assert "PR129" in text
    assert "zwei kleine PRs" in text
    assert "keine historische RNG- oder Vollgleichheitsbehauptung" in text
    assert "`incomming/` bleibt unversioniert" in text


def test_pr128_mapping_names_origin_ui_and_boundaries() -> None:
    text = MIGRATION.read_text(encoding="utf-8")

    assert "`Vrvu01` bis `Vrvu10`" in text
    assert "`Vrvn01` bis `Vrvn06`" in text
    assert "`ims.api.strategy_execution_candidate_store`" in text
    assert "Tab `Kandidaten`" in text
    assert "keine historische UI-" in text
    assert "keinen POST-, Speicher-, Freigabe- oder" in text
    assert "PR129" in text
    assert "PR130" in text


def test_pr128_is_linked_from_plan_migration_and_strategy_indexes() -> None:
    plan_index = (ROOT / "docs" / "plans" / "README.md").read_text(encoding="utf-8")
    migration_index = (ROOT / "docs" / "migration" / "README.md").read_text(encoding="utf-8")
    strategy_index = (ROOT / "docs" / "strategy" / "README.md").read_text(encoding="utf-8")

    assert "ims_2x_strategy_execution_candidate_ui_plan.md" in plan_index
    assert "ims_2x_strategy_execution_candidate_ui.md" in migration_index
    assert "ims_2x_strategy_execution_candidate_ui.md" in strategy_index
