from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PLAN = (
    ROOT
    / "docs"
    / "plans"
    / "ims_2x_strategy_execution_period_chain_bounded_runner_contract_plan.md"
)
MIGRATION = (
    ROOT
    / "docs"
    / "migration"
    / "ims_2x_strategy_execution_period_chain_bounded_runner_contract.md"
)


def test_pr142_plan_and_mapping_define_bounded_runner_contract() -> None:
    plan = PLAN.read_text(encoding="utf-8")
    migration = MIGRATION.read_text(encoding="utf-8")
    normalized = " ".join((plan + migration).split())

    assert "PR142 umgesetzt" in plan
    assert "`ESS.C:73-75`" in normalized
    assert "`SIMLAENGE = 100`" in normalized
    assert "zwei bis hoechstens fuenf Perioden" in normalized
    assert "kanonische JSON" in normalized
    assert "bytegleich" in normalized
    assert "keinen POST-, PUT- oder DELETE-Pfad" in normalized
    assert "keine neue oder geaenderte VU-/VN-Fachlogik" in normalized
    assert "keine historische RNG- oder Vollgleichheitsbehauptung" in normalized
    assert "`incomming/` bleibt unversioniert" in plan
    assert "PR143 (umgesetzt)" in plan
    assert "PR144 (umgesetzt)" in plan
    assert "PR145 (naechster Schritt)" in plan


def test_pr142_sources_are_indexed() -> None:
    plans_index = (ROOT / "docs" / "plans" / "README.md").read_text(
        encoding="utf-8"
    )
    migration_index = (ROOT / "docs" / "migration" / "README.md").read_text(
        encoding="utf-8"
    )
    strategy_index = (ROOT / "docs" / "strategy" / "README.md").read_text(
        encoding="utf-8"
    )

    assert PLAN.name in plans_index
    assert MIGRATION.name in migration_index
    assert MIGRATION.name in strategy_index
