from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN = (
    ROOT
    / "docs"
    / "plans"
    / "ims_2x_strategy_execution_candidate_run_control_plan.md"
)
MIGRATION = (
    ROOT
    / "docs"
    / "migration"
    / "ims_2x_strategy_execution_candidate_run_control.md"
)


def test_pr129_plan_documents_identity_recheck_and_closed_start_boundary() -> None:
    text = PLAN.read_text(encoding="utf-8")

    assert "PR129" in text
    assert "`Vrvu01` bis `Vrvu10`" in text
    assert "`Vrvn01` bis `Vrvn06`" in text
    assert "Kandidaten-ID" in text
    assert "erwarteten SHA-256-Digest" in text
    assert "vollstaendigen erwarteten Digest" in text
    assert "noch keine\nAuthentisierung" in text
    assert "keinen\nQueue-Eintrag" in text
    assert "keine Simulation" in text
    assert "keine historische RNG- oder Vollgleichheitsbehauptung" in text
    assert "`incomming/` bleibt unversioniert" in text
    assert "PR130" in text
    assert "zwei kleine PRs" in text


def test_pr129_mapping_names_implementation_api_and_limits() -> None:
    text = MIGRATION.read_text(encoding="utf-8")

    assert "`ims.api.strategy_execution_candidate_run_control`" in text
    assert "`StrategyExecutionCandidateRunControlRequest`" in text
    assert "`check_strategy_execution_candidate_run_control_release`" in text
    assert "GET /api/run-control/strategy-candidate-contract" in text
    assert "POST /api/run-control/strategy-candidate-release-check" in text
    assert "keine Benutzeridentitaet" in text
    assert "keine Starterlaubnis" in text
    assert "PR130" in text


def test_pr129_is_linked_from_plan_migration_and_strategy_indexes() -> None:
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
