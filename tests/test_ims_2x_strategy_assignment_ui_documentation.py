from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
PLAN = REPO_ROOT / "docs" / "plans" / "ims_2x_strategy_assignment_ui_plan.md"
MIGRATION = REPO_ROOT / "docs" / "migration" / "ims_2x_strategy_assignment_ui.md"


def test_pr107_plan_preserves_read_only_scope_and_next_step() -> None:
    text = PLAN.read_text(encoding="utf-8")

    assert "PR107" in text
    assert "ims.strategy-assignment-contract.v1" in text
    assert "GET /api/strategies/assignment-contract" in text
    assert "keine konkreten Parameterwerte" in text
    assert "kein Schreiben, kein Runner-Start und keine Simulation" in text
    assert "keine historische Vollgleichheitsbehauptung" in text
    assert "PR108" in text
    assert "Entwurfsformat" in text


def test_pr107_migration_maps_historical_sources_to_workbench() -> None:
    text = MIGRATION.read_text(encoding="utf-8")

    assert "IMSDATA.C" in text
    assert "ACTION.st" in text
    assert "IMS.E" in text
    assert "Vdefmd6" in text
    assert "source_profiles" in text
    assert "parameter_schemas" in text
    assert "achtzehn VU-/VN-Bereiche" in text
    assert "dreizehn vorhandenen Dataclass-/Loaderformen" in text
    assert "Vrvn01" in text
    assert "Kfz" in text
    assert "Sach-Haftpflicht" in text
    assert "historische Vollgleichheit" in text


def test_pr107_documentation_is_indexed() -> None:
    plan_index = (REPO_ROOT / "docs" / "plans" / "README.md").read_text(encoding="utf-8")
    migration_index = (REPO_ROOT / "docs" / "migration" / "README.md").read_text(encoding="utf-8")
    strategy_index = (REPO_ROOT / "docs" / "strategy" / "README.md").read_text(encoding="utf-8")

    assert "ims_2x_strategy_assignment_ui_plan.md" in plan_index
    assert "ims_2x_strategy_assignment_ui.md" in migration_index
    assert "ims_2x_strategy_assignment_ui.md" in strategy_index
