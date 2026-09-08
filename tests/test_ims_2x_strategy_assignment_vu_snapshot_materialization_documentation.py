from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN = (
    ROOT
    / "docs"
    / "plans"
    / "ims_2x_strategy_assignment_vu_snapshot_materialization_plan.md"
)
MIGRATION = (
    ROOT
    / "docs"
    / "migration"
    / "ims_2x_strategy_assignment_vu_snapshot_materialization.md"
)


def test_pr121_plan_documents_atomic_scope_and_closed_execution() -> None:
    text = PLAN.read_text(encoding="utf-8")

    assert "PR121" in text
    assert "PR120-Fehler verhindern jeden Snapshot-Loader-Aufruf" in text
    assert "partial_results_returned = false" in text
    assert "keine VU-Regelausfuehrung" in text
    assert "keine Speicherung" in text
    assert "keine historische RNG- oder Vollgleichheitsbehauptung" in text
    assert "PR122" in text


def test_pr121_migration_maps_all_historical_actions_and_loaders() -> None:
    text = MIGRATION.read_text(encoding="utf-8")

    for action in (
        "Vrvu01",
        "Vrvu02",
        "Vrvu03",
        "Vrvu04",
        "Vrvu05",
        "Vrvu06",
        "Vrvu07-09",
        "Vrvu10",
    ):
        assert action in text
    for loader in (
        "vu_random_uniform_rule_snapshot_from_mapping",
        "vu_random_normal_rule_snapshot_from_mapping",
        "vu_reserve_markup_rule_snapshot_from_mapping",
        "vu_net_switcher_markup_rule_snapshot_from_mapping",
        "vu_market_share_markup_rule_snapshot_from_mapping",
        "vu_expected_claim_rule_snapshot_from_mapping",
        "vu_foreign_info_rule_snapshot_from_mapping",
        "vu_free_linear_rule_snapshot_from_mapping",
    ):
        assert loader in text
    assert "keine teilweise verwertbare" in text
    assert "execution_ready = false" in text
    assert "historische Vollgleichheit" in text


def test_pr121_documents_are_indexed() -> None:
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
    assert "PR121 VU-Snapshots materialisieren" in strategy_index
