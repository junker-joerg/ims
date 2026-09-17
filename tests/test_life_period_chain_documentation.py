from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PLAN = ROOT / "docs" / "plans" / "ims_2x_pr165_life_period_chain_plan.md"
MIGRATION = ROOT / "docs" / "migration" / "ims_2x_life_period_chain.md"


def test_pr165_documents_sources_carryover_budget_and_next_step() -> None:
    plan = PLAN.read_text(encoding="utf-8")
    migration = MIGRATION.read_text(encoding="utf-8")
    normalized = " ".join((plan + migration).lower().split())
    for phrase in (
        "IMSDATA.C", "IMS.E", "PR163", "PR164", "PR166", "PR167",
        "death_benefit_if_death", "maturity_benefit_if_due",
        "opening_backing_assets", "Carryover", "Prefix",
        "100 Perioden", "10.000", "Abbruch", "atomar",
        "Nichtleben", "keine historische Vollgleichheit",
    ):
        assert phrase.lower() in normalized
    assert PLAN.name in (ROOT / "docs" / "plans" / "README.md").read_text(encoding="utf-8")
    assert MIGRATION.name in (ROOT / "docs" / "migration" / "README.md").read_text(encoding="utf-8")
    roadmap = (ROOT / "docs" / "plans" / "ims_2x_all_lines_management_lab_roadmap.md").read_text(encoding="utf-8")
    assert "PR166 Lebens-Ergebnisdienst umgesetzt, PR167 Workbench naechster Schritt" in roadmap
