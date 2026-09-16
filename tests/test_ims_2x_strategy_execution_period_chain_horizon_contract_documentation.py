from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PLAN = (
    ROOT
    / "docs"
    / "plans"
    / "ims_2x_strategy_execution_period_chain_horizon_contract_plan.md"
)
MIGRATION = (
    ROOT
    / "docs"
    / "migration"
    / "ims_2x_strategy_execution_period_chain_horizon_contract.md"
)


def test_pr147_mapping_and_plan_keep_release_closed() -> None:
    plan = PLAN.read_text(encoding="utf-8")
    migration = MIGRATION.read_text(encoding="utf-8")
    normalized = " ".join((plan + migration).split())

    assert "PR147 umgesetzt; PR148 naechster Schritt" in plan
    assert "`ESS.C:71-75`" in normalized
    assert "`IMSDATA.C:14`" in normalized
    assert "`SIMLAENGE = 100`" in normalized
    assert "10, 25, 50 und 100" in normalized
    assert "1.024 MiB" in plan
    assert "256 MiB" in plan
    assert "1.800 s" in plan
    assert "ein isolierbarer Worker" in plan
    assert "kanonisches JSON bytegleich" in normalized
    assert "kein Teilergebnis" in normalized
    assert "PR148 implementiert und misst" in plan
    assert "PR149 uebertraegt" in plan
    assert "`incomming/` bleibt unversioniert" in plan
    assert "keine historische RNG- oder Vollgleichheitsbehauptung" in normalized


def test_pr147_sources_are_indexed() -> None:
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
