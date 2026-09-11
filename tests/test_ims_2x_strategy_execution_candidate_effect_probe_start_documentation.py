from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN = (
    ROOT
    / "docs"
    / "plans"
    / "ims_2x_strategy_execution_candidate_effect_probe_start_plan.md"
)
MIGRATION = (
    ROOT
    / "docs"
    / "migration"
    / "ims_2x_strategy_execution_candidate_effect_probe_start.md"
)


def test_pr131_plan_documents_controlled_start_and_persistence_boundaries() -> None:
    text = PLAN.read_text(encoding="utf-8")

    assert "PR131" in text
    assert "`Vrvu01` bis `Vrvu10`" in text
    assert "`Vrvn01` bis `Vrvn06`" in text
    assert "`BEGIN IMMEDIATE`" in text
    assert "hoechstens ein erfolgreiches Ergebnis" in text
    assert "neue manuelle Freigabe" in text
    assert "Idempotenzschluessel erlaubt" in text.replace("\n", " ")
    assert "kein automatischer Retry" in text
    assert "keine historische RNG- oder Vollgleichheitsbehauptung" in text
    assert "`incomming/` bleibt unversioniert" in text
    assert "PR132" in text
    assert "Nach PR132 ist die Einperioden-Wirkungsprobe" in text
    assert "PR133" in text


def test_pr131_mapping_names_api_ui_storage_and_limits() -> None:
    text = MIGRATION.read_text(encoding="utf-8")

    assert "`ims.api.strategy_execution_candidate_effect_probe_start`" in text
    assert "strategy_execution_candidate_effect_probe_attempts" in text
    assert "strategy_execution_candidate_effect_probe_results" in text
    assert "POST /api/run-control/strategy-candidate-effect-probe-start" in text
    assert "result/{candidate_id}" in text
    assert "history/{candidate_id}" in text
    assert "unveraendert" in text
    assert "kein Carryover" in text
    assert "keine historische RNG- oder Vollgleichheitsbehauptung" in text


def test_pr131_is_linked_from_plan_migration_and_strategy_indexes() -> None:
    plan_index = (ROOT / "docs" / "plans" / "README.md").read_text(
        encoding="utf-8"
    )
    migration_index = (ROOT / "docs" / "migration" / "README.md").read_text(
        encoding="utf-8"
    )
    strategy_index = (ROOT / "docs" / "strategy" / "README.md").read_text(
        encoding="utf-8"
    )

    assert PLAN.name in plan_index
    assert MIGRATION.name in migration_index
    assert MIGRATION.name in strategy_index
