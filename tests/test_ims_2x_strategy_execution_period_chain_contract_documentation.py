from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PLAN = (
    ROOT
    / "docs"
    / "plans"
    / "ims_2x_strategy_execution_period_chain_contract_plan.md"
)
MIGRATION = (
    ROOT
    / "docs"
    / "migration"
    / "ims_2x_strategy_execution_period_chain_contract.md"
)


def test_pr133_plan_and_mapping_define_period_chain_boundaries() -> None:
    plan = PLAN.read_text(encoding="utf-8")
    migration = MIGRATION.read_text(encoding="utf-8")
    normalized = " ".join((plan + migration).split())

    assert "PR133 umgesetzt" in plan
    assert "`SIMLAENGE = 100`" in normalized
    assert "zwei bis hoechstens 100 Perioden" in normalized
    assert "lueckenlos" in normalized
    assert "apply_vu_foreign_info_carryover" in normalized
    assert "apply_vn_state_carryover" in normalized
    assert "PR131-Wirkungsnachweis" in normalized
    assert "kein Carryover-Aufruf und kein Runnerstart" in plan
    assert "keine historische RNG- oder Vollgleichheitsbehauptung" in plan
    assert "`incomming/` bleibt unversioniert" in plan
    assert "PR134" in normalized


def test_pr133_sources_are_indexed() -> None:
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
