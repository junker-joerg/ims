from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PLAN = (
    ROOT
    / "docs"
    / "plans"
    / "ims_2x_strategy_execution_period_chain_five_period_effect_probe_start_plan.md"
)
MIGRATION = (
    ROOT
    / "docs"
    / "migration"
    / "ims_2x_strategy_execution_period_chain_five_period_effect_probe_start.md"
)


def test_pr145_plan_and_mapping_define_persistent_five_period_start() -> None:
    plan = PLAN.read_text(encoding="utf-8")
    migration = MIGRATION.read_text(encoding="utf-8")
    normalized = " ".join((plan + migration).split())

    assert "Status: umgesetzt" in plan
    assert "`ESS.C:73-75`" in normalized
    assert "`IMSDATA.C:14`" in normalized
    assert "unveraenderten PR144-Request" in normalized
    assert "vollstaendigen Startrequest" in normalized
    assert "kanonische Kettenkopie" in normalized
    assert "vollstaendige Wirkungsergebnis" in normalized
    assert "hoechstens ein erfolgreiches Ergebnis" in normalized
    assert "kein Teilresultat" in normalized
    assert "keine neue Fachlogik" in normalized
    assert "keine historische RNG- oder Vollgleichheitsbehauptung" in normalized
    assert "`incomming/` bleibt unversioniert" in plan
    assert "PR146" in normalized


def test_pr145_sources_are_indexed() -> None:
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
