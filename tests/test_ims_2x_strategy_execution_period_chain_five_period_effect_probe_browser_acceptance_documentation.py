from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PLAN = (
    ROOT
    / "docs"
    / "plans"
    / "ims_2x_strategy_execution_period_chain_five_period_effect_probe_browser_acceptance_plan.md"
)
MIGRATION = (
    ROOT
    / "docs"
    / "migration"
    / "ims_2x_strategy_execution_period_chain_five_period_effect_probe_browser_acceptance.md"
)
HANDBOOK = ROOT / "docs" / "handbook" / "operation.md"
IMAGE_DIR = ROOT / "docs" / "handbook" / "images"


def _png_size(path: Path) -> tuple[int, int]:
    payload = path.read_bytes()
    assert payload[:8] == b"\x89PNG\r\n\x1a\n"
    assert payload[12:16] == b"IHDR"
    return (
        int.from_bytes(payload[16:20], "big"),
        int.from_bytes(payload[20:24], "big"),
    )


def test_pr146_plan_and_mapping_define_browser_acceptance_boundaries() -> None:
    plan = PLAN.read_text(encoding="utf-8")
    migration = MIGRATION.read_text(encoding="utf-8")
    normalized = " ".join((plan + migration).split())

    assert "PR146 umgesetzt" in plan
    assert "1440 x 1000" in normalized
    assert "390 x 844" in normalized
    assert "Ohne ausdrueckliche Checkbox" in plan
    assert "Runnerfehler in Periode 4" in normalized
    assert "ohne weitere Runner-, Carryover- oder Schreibaufrufe" in normalized
    assert "PR146 portiert keine C-Regel" in normalized
    assert "PR147 (naechster Schritt)" in plan
    assert "keine historische RNG- oder Vollgleichheitsbehauptung" in normalized
    assert "`incomming/` bleibt unversioniert" in plan


def test_pr146_handbook_uses_readable_wide_and_narrow_browser_images() -> None:
    expected = {
        "windows_strategy_five_period_effect_probe_pr146_wide_2026-09-16.png": (
            1440,
            1000,
        ),
        "windows_strategy_five_period_effect_probe_pr146_narrow_2026-09-16.png": (
            390,
            844,
        ),
    }
    handbook = HANDBOOK.read_text(encoding="utf-8")
    normalized = " ".join(handbook.split())

    for filename, dimensions in expected.items():
        path = IMAGE_DIR / filename
        assert _png_size(path) == dimensions
        assert f"images/{filename}" in handbook
    assert handbook.count("aufgenommen am 2026-09-16") == 2
    assert "Fuenf Perioden starten" in handbook
    assert "Prefix 1-2 exakt bestaetigt" in normalized
    assert "vier Uebergaenge" in normalized


def test_pr146_sources_are_indexed() -> None:
    plans_index = (ROOT / "docs" / "plans" / "README.md").read_text(
        encoding="utf-8"
    )
    migration_index = (ROOT / "docs" / "migration" / "README.md").read_text(
        encoding="utf-8"
    )
    strategy_index = (ROOT / "docs" / "strategy" / "README.md").read_text(
        encoding="utf-8"
    )

    assert PLAN.name in plans_index
    assert MIGRATION.name in migration_index
    assert MIGRATION.name in strategy_index
