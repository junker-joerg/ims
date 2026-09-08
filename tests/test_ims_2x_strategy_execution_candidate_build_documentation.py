from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs" / "plans" / "ims_2x_strategy_execution_candidate_build_plan.md"
MIGRATION = (
    ROOT
    / "docs"
    / "migration"
    / "ims_2x_strategy_execution_candidate_build.md"
)


def test_pr126_documentation_records_sources_digest_and_boundaries() -> None:
    plan = PLAN.read_text(encoding="utf-8")
    migration = MIGRATION.read_text(encoding="utf-8")
    combined = f"{plan}\n{migration}"

    assert "PR126" in combined
    assert "`IMS.E`" in combined
    assert "`Vrvu01` bis `Vrvu10`" in combined
    assert "`Vrvn01` bis `Vrvn06`" in combined
    assert "`LoadedScenario`" in combined
    assert "synthetic-joint-single-period-v1" in migration
    assert "SHA-256" in migration
    assert "candidate_id" in migration
    assert "content_digest" in migration
    assert "keine VU-, VN-, Schaden- oder Abrechnungsregel geaendert" in migration
    assert "keine Kandidatenablage" in plan
    assert "keine Simulation" in plan
    assert "keine historische RNG- oder Vollgleichheitsbehauptung" in plan


def test_pr126_documentation_is_indexed_and_names_pr127() -> None:
    plan_index = (ROOT / "docs" / "plans" / "README.md").read_text(
        encoding="utf-8"
    )
    migration_index = (ROOT / "docs" / "migration" / "README.md").read_text(
        encoding="utf-8"
    )
    strategy_index = (ROOT / "docs" / "strategy" / "README.md").read_text(
        encoding="utf-8"
    )
    connection_plan = (
        ROOT
        / "docs"
        / "plans"
        / "ims_2x_strategy_execution_connection_plan.md"
    ).read_text(encoding="utf-8")

    assert PLAN.name in plan_index
    assert MIGRATION.name in migration_index
    assert MIGRATION.name in strategy_index
    assert "PR126 (umgesetzt)" in connection_plan
    assert "drei kleine PRs" in connection_plan
    assert "PR127" in PLAN.read_text(encoding="utf-8")
