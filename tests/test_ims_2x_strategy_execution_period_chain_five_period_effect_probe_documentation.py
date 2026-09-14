from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PLAN = (
    ROOT
    / "docs"
    / "plans"
    / "ims_2x_strategy_execution_period_chain_five_period_effect_probe_plan.md"
)
MIGRATION = (
    ROOT
    / "docs"
    / "migration"
    / "ims_2x_strategy_execution_period_chain_five_period_effect_probe.md"
)


def test_pr144_plan_and_mapping_define_ephemeral_five_period_probe() -> None:
    plan = PLAN.read_text(encoding="utf-8")
    migration = MIGRATION.read_text(encoding="utf-8")
    normalized = " ".join((plan + migration).split())

    assert "PR144 umgesetzt" in plan
    assert "`ESS.C:73-75`" in normalized
    assert "`SIMLAENGE = 100`" in normalized
    assert "genau fuenf" in normalized
    assert "vier Uebergaenge" in normalized
    assert "kanonisches ASCII-JSON bytegleich" in normalized
    assert "ohne numerische Toleranz" in normalized
    assert "Perioden 3 bis 5 nicht aufgerufen" in normalized
    assert "keine neue oder geaenderte VU-/VN-Fachlogik" in normalized
    assert "keine historische RNG- oder Vollgleichheitsbehauptung" in normalized
    assert "`incomming/` bleibt unversioniert" in plan
    assert "PR145 (naechster Schritt)" in plan


def test_pr144_sources_are_indexed() -> None:
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
