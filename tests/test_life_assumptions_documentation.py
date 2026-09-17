from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PLAN = ROOT / "docs" / "plans" / "ims_2x_pr164_life_assumptions_plan.md"
MIGRATION = ROOT / "docs" / "migration" / "ims_2x_life_assumptions.md"


def test_pr164_documents_historical_boundary_sources_and_next_step() -> None:
    plan = PLAN.read_text(encoding="utf-8")
    migration = MIGRATION.read_text(encoding="utf-8")
    normalized = " ".join((plan + migration).lower().split())
    for phrase in (
        "IMSDATA.C", "IMS.E", "BAV.Zs", "PR160", "PR163", "PR165",
        "insurer_rule_on_opening_backing_assets",
        "exogenous_deterministic_rate_curve", "ROUND_HALF_EVEN",
        "ROUND_HALF_UP", "opening_backing_assets", "death_policy_ids",
        "lueckenlos", "atomar", "keine historische vollgleichheit",
        "keine RNG-Ziehung", "keinen Runner",
    ):
        assert phrase.lower() in normalized
    assert PLAN.name in (ROOT / "docs" / "plans" / "README.md").read_text(encoding="utf-8")
    assert MIGRATION.name in (ROOT / "docs" / "migration" / "README.md").read_text(encoding="utf-8")
    roadmap = (ROOT / "docs" / "plans" / "ims_2x_all_lines_management_lab_roadmap.md").read_text(encoding="utf-8")
    assert "PR167 Lebens-Workbench umgesetzt, PR168 Kranken-Vertrag naechster Schritt" in roadmap
