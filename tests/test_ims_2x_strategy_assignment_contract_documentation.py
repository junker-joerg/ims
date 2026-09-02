from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
PLAN = REPO_ROOT / "docs" / "plans" / "ims_2x_strategy_assignment_contract_plan.md"
MIGRATION = REPO_ROOT / "docs" / "migration" / "ims_2x_strategy_assignment_contract.md"


def test_pr106_plan_freezes_scope_and_follow_up_sequence() -> None:
    normalized = PLAN.read_text(encoding="utf-8")

    assert "PR106" in normalized
    assert "dreizehn unterschiedliche Parameterschemata" in normalized
    assert "achtzehn aus `Vdefmd6` abgeleitete Quellprofile" in normalized
    assert "keine modernen Spartennamen" in normalized
    assert "kein Runner-Start und keine Simulation" in normalized
    assert "keine historische Vollgleichheitsbehauptung" in normalized
    assert "PR107" in normalized
    assert "PR108" in normalized


def test_pr106_mapping_documents_actor_parameter_and_sector_boundaries() -> None:
    normalized = MIGRATION.read_text(encoding="utf-8")

    assert "`IMSDATA.C`, `ACTION.st`" in normalized
    assert "`IMS.E`, `Vuauini` und `Vnauini`" in normalized
    assert "VU14 und VU15-16" in normalized
    assert "VN151-190 und VN191-200" in normalized
    assert "`Vrvn01` besitzt keinen eigenen Strategieparameterblock" in normalized
    assert "`legacy_sector_1` und `legacy_sector_2`" in normalized
    assert "weder unterschiedliche Strategien je Position" in normalized
    assert "Parameterwerte werden nicht ausgegeben" in normalized


def test_pr106_documents_are_linked_from_indexes() -> None:
    plans_index = (REPO_ROOT / "docs" / "plans" / "README.md").read_text(encoding="utf-8")
    migration_index = (REPO_ROOT / "docs" / "migration" / "README.md").read_text(encoding="utf-8")
    strategy_index = (REPO_ROOT / "docs" / "strategy" / "README.md").read_text(encoding="utf-8")

    assert "ims_2x_strategy_assignment_contract_plan.md" in plans_index
    assert "ims_2x_strategy_assignment_contract.md" in migration_index
    assert "PR106 Strategiezuordnungs- und Parametervertrag" in strategy_index
