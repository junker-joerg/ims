import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
PLAN = REPO_ROOT / "docs" / "plans" / "ims_2x_strategy_assignment_draft_plan.md"
MIGRATION = REPO_ROOT / "docs" / "migration" / "ims_2x_strategy_assignment_draft.md"
FIXTURE = REPO_ROOT / "tests" / "fixtures" / "strategy_assignment_draft_v1.json"


def test_pr108_plan_freezes_validation_only_scope_and_next_step() -> None:
    text = PLAN.read_text(encoding="utf-8")

    assert "PR108" in text
    assert "ims.strategy-assignment-draft.v1" in text
    assert "Vdefmd6" in text
    assert "25 VU und 200 VN" in text
    assert "keine Regel-Snapshots" in text
    assert "kein Runner- oder Simulationsstart" in text
    assert "keine historische Vollgleichheitsbehauptung" in text
    assert "PR109" in text


def test_pr108_mapping_documents_origin_format_and_closed_boundaries() -> None:
    text = MIGRATION.read_text(encoding="utf-8")

    assert "`IMSDATA.C`, `ACTION.st`" in text
    assert "`IMS.E`, `Vuauini`, `Vnauini`" in text
    assert "`legacy_sector_1`" in text
    assert "`legacy_sector_2`" in text
    assert "`Vrvn01`" in text
    assert "keine Schreiboperation" in text
    assert "historische Rekonstruktion" in text
    assert "fachliche Empfehlung" in text
    assert "historische Vollgleichheit" in text


def test_pr108_example_is_versioned_synthetic_and_documents_are_indexed() -> None:
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
    plan_index = (REPO_ROOT / "docs" / "plans" / "README.md").read_text(encoding="utf-8")
    migration_index = (REPO_ROOT / "docs" / "migration" / "README.md").read_text(encoding="utf-8")
    strategy_index = (REPO_ROOT / "docs" / "strategy" / "README.md").read_text(encoding="utf-8")

    assert fixture["schema_version"] == "ims.strategy-assignment-draft.v1"
    assert fixture["draft_id"] == "synthetic-pr108-example"
    assert "ims_2x_strategy_assignment_draft_plan.md" in plan_index
    assert "ims_2x_strategy_assignment_draft.md" in migration_index
    assert "PR108 Strategiezuordnungsentwurf" in strategy_index
