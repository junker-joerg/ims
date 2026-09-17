from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PLAN = ROOT / "docs" / "plans" / "ims_2x_pr159_deterministic_life_case_plan.md"
MIGRATION = ROOT / "docs" / "migration" / "ims_2x_deterministic_life_case.md"


def test_pr159_documents_model_choice_historical_limit_and_deferred_scope() -> None:
    plan = PLAN.read_text(encoding="utf-8")
    migration = MIGRATION.read_text(encoding="utf-8")
    for phrase in (
        "IMSDATA.C", "IMS.E", "ROUND_HALF_EVEN", "opening_guarantee_liability",
        "premium_liability_allocation", "PR170", "keine historische Vollgleichheitsbehauptung",
        "Das ist keine dauerhafte Ausschlussliste", "PR160-167",
    ):
        assert phrase.lower() in (plan + migration).lower()
    assert "PR161 Tod und Kapital umgesetzt, PR162 Neugeschaeft naechster Schritt" in (
        ROOT / "docs" / "plans" / "ims_2x_all_lines_management_lab_roadmap.md"
    ).read_text(encoding="utf-8")
    assert "ims_2x_deterministic_life_case.md" in (
        ROOT / "docs" / "migration" / "README.md"
    ).read_text(encoding="utf-8")
