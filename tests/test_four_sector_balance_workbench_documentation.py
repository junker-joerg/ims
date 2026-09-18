from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def test_pr170a_documents_bounded_browser_path_and_screenshots() -> None:
    plan = (ROOT / "docs/plans/ims_2x_pr170a_four_sector_workbench.md").read_text(encoding="utf-8")
    guide = (ROOT / "docs/handbook/management_seminar_guide.md").read_text(encoding="utf-8")
    roadmap = (ROOT / "docs/plans/ims_2x_all_lines_management_lab_roadmap.md").read_text(encoding="utf-8")
    app = (ROOT / "frontend/src/main.tsx").read_text(encoding="utf-8")
    component = (ROOT / "frontend/src/FourSectorBalanceWorkbench.tsx").read_text(encoding="utf-8")
    for phrase in (
        "IMSDATA.C", "Baseline", "Variante", "Zwei-Perioden",
        "Szenario", "100-Perioden", "ohne neue Fachregel",
    ):
        assert phrase in (plan + guide + roadmap)
    for name in (
        "windows_four_sector_balance_pr170a_wide_2026-09-18.png",
        "windows_four_sector_balance_pr170a_narrow_2026-09-18.png",
    ):
        assert name in guide
        assert (ROOT / "docs/handbook/images" / name).is_file()
    assert "| PR170a | Vier-Sparten-Bilanz in der Workbench | umgesetzt:" in roadmap
    assert 'href="#four-sector-balance"' in app
    assert "<FourSectorBalanceWorkbench nonLife={nonLifeReady} life={lifeReady} health={healthReady}" in app
    assert "onReady={setFourSectorReady}" in app
    assert 'data-testid="four-sector-results"' in component
