from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN = (
    ROOT
    / "docs"
    / "plans"
    / "ims_2x_strategy_execution_candidate_effect_probe_plan.md"
)
MIGRATION = (
    ROOT
    / "docs"
    / "migration"
    / "ims_2x_strategy_execution_candidate_effect_probe.md"
)


def test_pr130_plan_documents_isolated_one_period_execution_and_boundaries() -> None:
    text = PLAN.read_text(encoding="utf-8")

    assert "PR130" in text
    assert "`Vrvu01` bis `Vrvu10`" in text
    assert "`Vrvn01` bis `Vrvn06`" in text
    assert "`run_loaded_explicit_period` genau einmal" in text
    assert "`output_dir=None`" in text
    assert "`explicit_effect_probe_execution = true`" in text
    assert "insurance_decisions: null" in text
    assert "keine Entscheidung ergaenzt" in text
    assert "nicht gespeichert" in text
    assert "kein Carryover" in text
    assert "keine historische RNG- oder Vollgleichheitsbehauptung" in text
    assert "`incomming/` bleibt unversioniert" in text
    assert "PR131 (umgesetzt)" in text
    assert "PR132" in text
    assert "ein kleiner PR" in text


def test_pr130_mapping_names_backend_api_result_and_limits() -> None:
    text = MIGRATION.read_text(encoding="utf-8")

    assert "`ims.api.strategy_execution_candidate_effect_probe`" in text
    assert "`ims.engine.explicit_period_runner.run_loaded_explicit_period`" in text
    assert "`state_before`" in text
    assert "`state_after`" in text
    assert "GET /api/run-control/strategy-candidate-effect-probe-contract" in text
    assert "POST /api/run-control/strategy-candidate-effect-probe" in text
    assert "`execution_performed = true`" in text
    assert "`simulation_performed` bleibt `false`" in text
    assert "keine dauerhafte Idempotenz" in text


def test_pr130_is_linked_from_plan_migration_and_strategy_indexes() -> None:
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
