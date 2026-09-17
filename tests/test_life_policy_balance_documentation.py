from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PLAN = ROOT / "docs" / "plans" / "ims_2x_pr163_life_policy_maturity_plan.md"
MIGRATION = ROOT / "docs" / "migration" / "ims_2x_life_policy_maturity.md"


def test_pr163_documents_historical_boundary_semantics_and_next_steps() -> None:
    plan = PLAN.read_text(encoding="utf-8")
    migration = MIGRATION.read_text(encoding="utf-8")
    normalized = " ".join((plan + migration).lower().split())
    for phrase in (
        "IMSDATA.C", "IMS.E", "PR160", "PR162", "PR164", "PR165-167",
        "fully_enumerated_policies", "ROUND_HALF_EVEN", "0.0001",
        "hoechstens 100 aktive Policen", "maturity_benefits_paid",
        "Garantieuntergrenze", "atomar", "historische Vollgleichheit",
        "kein Runner", "keine Stichprobe",
    ):
        assert phrase.lower() in normalized
    assert PLAN.name in (ROOT / "docs" / "plans" / "README.md").read_text(encoding="utf-8")
    assert MIGRATION.name in (ROOT / "docs" / "migration" / "README.md").read_text(encoding="utf-8")
    roadmap = (ROOT / "docs" / "plans" / "ims_2x_all_lines_management_lab_roadmap.md").read_text(encoding="utf-8")
    assert "PR165 Lebensanschluss umgesetzt, PR166 Ergebnisablage naechster Schritt" in roadmap
