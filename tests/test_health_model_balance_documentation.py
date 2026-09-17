from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
MIGRATION = ROOT / "docs" / "migration" / "ims_2x_deterministic_health_case.md"
PLAN = ROOT / "docs" / "plans" / "ims_2x_pr169_health_balance_and_simulation_plan.md"
ROADMAP = ROOT / "docs" / "plans" / "ims_2x_all_lines_management_lab_roadmap.md"


def test_pr169_documents_source_limits_calculation_and_full_health_ui_path() -> None:
    migration = MIGRATION.read_text(encoding="utf-8")
    plan = PLAN.read_text(encoding="utf-8")
    roadmap = ROADMAP.read_text(encoding="utf-8")
    normalized = " ".join((migration + plan).lower().split())
    for phrase in (
        "IMSDATA.C", "IMS.E", "KV", "explizite Szenariowerte",
        "offene Leistungsverpflichtung", "Periode 2", "kein zweiter Aufwand",
        "PR169a", "PR169b", "PR169c", "PR169d", "PR170",
        "100 IMS-Modellperioden", "keine historische Vollgleichheit",
    ):
        assert phrase.lower() in normalized
    assert "bedienbare 100-Perioden-Kranken-Simulation nach PR169d" in plan
    assert roadmap.index("| PR169 |") < roadmap.index("| PR169a |") < roadmap.index("| PR170 |")
    assert "ims_2x_pr169_health_balance_and_simulation_plan.md" in roadmap
    assert MIGRATION.name in (ROOT / "docs" / "migration" / "README.md").read_text(
        encoding="utf-8"
    )
    assert PLAN.name in (ROOT / "docs" / "plans" / "README.md").read_text(
        encoding="utf-8"
    )
