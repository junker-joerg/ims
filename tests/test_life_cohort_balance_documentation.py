from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PLAN = ROOT / "docs" / "plans" / "ims_2x_pr162_life_cohort_new_business_plan.md"
MIGRATION = ROOT / "docs" / "migration" / "ims_2x_life_cohort_new_business.md"


def test_pr162_documents_historical_boundary_timing_and_next_steps() -> None:
    plan = PLAN.read_text(encoding="utf-8")
    migration = MIGRATION.read_text(encoding="utf-8")
    normalized = " ".join((plan + migration).lower().split())
    for phrase in (
        "IMSDATA.C", "IMS.E", "PR160", "PR161", "PR163", "PR165-167",
        "issue_period", "new_business_liability_allocation", "Folgeperiode",
        "ROUND_HALF_EVEN", "Kohortensummen", "atomar", "historische Vollgleichheit",
    ):
        assert phrase.lower() in normalized
    assert PLAN.name in (ROOT / "docs" / "plans" / "README.md").read_text(encoding="utf-8")
    assert MIGRATION.name in (ROOT / "docs" / "migration" / "README.md").read_text(encoding="utf-8")
    assert "PR163 Einzelpolicen umgesetzt, PR164 Annahmen naechster Schritt" in (
        ROOT / "docs" / "plans" / "ims_2x_all_lines_management_lab_roadmap.md"
    ).read_text(encoding="utf-8")
