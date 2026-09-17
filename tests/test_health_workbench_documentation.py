from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PLAN = ROOT / "docs/plans/ims_2x_pr169_health_balance_and_simulation_plan.md"
MAPPING = ROOT / "docs/migration/ims_2x_health_workbench.md"
GUIDE = ROOT / "docs/handbook/management_seminar_guide.md"


def test_pr169d_describes_semantics_and_next_boundary() -> None:
    text = PLAN.read_text(encoding="utf-8") + MAPPING.read_text(encoding="utf-8")
    for phrase in (
        "IMSDATA.C", "IMS.E", "PR169b", "PR169c", "PR170",
        "Baseline", "Variante", "100 Perioden", "Prefixe",
        "If-Match", "CSV/JSON/XLSX", "historischen",
    ):
        assert phrase in text
    assert "ims_2x_health_workbench.md" in (
        ROOT / "docs/migration/README.md"
    ).read_text(encoding="utf-8")


def test_handbook_shows_real_wide_and_narrow_health_path() -> None:
    guide = GUIDE.read_text(encoding="utf-8")
    assert "## Einen Krankenfall ueber 100 Perioden vergleichen" in guide
    assert "Leistungsanfall" in guide
    assert "1552,0000" in guide and "1492,0000" in guide
    for width, height, suffix in (
        (1440, 900, "wide_inputs"),
        (1440, 900, "wide_results"),
        (390, 844, "narrow_inputs"),
        (390, 844, "narrow_results"),
    ):
        filename = f"windows_health_workbench_pr169d_{suffix}_2026-09-17.png"
        path = GUIDE.parent / "images" / filename
        data = path.read_bytes()
        assert data[:8] == b"\x89PNG\r\n\x1a\n"
        assert int.from_bytes(data[16:20], "big") == width
        assert int.from_bytes(data[20:24], "big") == height
        assert f"images/{filename}" in guide
