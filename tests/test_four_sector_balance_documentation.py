from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def test_pr170_documents_four_sector_mapping_and_browser_boundary() -> None:
    migration = (ROOT / "docs/migration/four_sector_model_balance.md").read_text(encoding="utf-8")
    roadmap = (ROOT / "docs/plans/ims_2x_all_lines_management_lab_roadmap.md").read_text(encoding="utf-8")
    handbook = (ROOT / "docs/handbook/management_seminar_guide.md").read_text(encoding="utf-8")
    for phrase in (
        "IMSDATA.C", "ims.four-sector-balance-input.v1", "motor",
        "property_liability", "life", "health", "scenario_id", "variant_id",
        "keine Teilzeilen", "Solvency II", "historische Vollgleichheit",
    ):
        assert phrase in migration
    assert "four_sector_model_balance.md" in (ROOT / "docs/migration/README.md").read_text(encoding="utf-8")
    assert "PR170a hat die vier geprueften Eingaben" in roadmap
    assert "Vier Sparten zu einer Versichererbilanz verbinden" in handbook
