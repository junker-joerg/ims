from pathlib import Path
import struct


ROOT = Path(__file__).resolve().parent.parent
PLAN = ROOT / "docs/plans/ims_2x_pr151_results_workbench_plan.md"
MAPPING = ROOT / "docs/migration/ims_2x_hundred_period_results_workbench.md"
HANDBOOK = ROOT / "docs/handbook/management_seminar_guide.md"


def test_pr151_documents_source_download_and_unresolved_chain_creation():
    text = " ".join((PLAN.read_text(encoding="utf-8") + " " +
                     MAPPING.read_text(encoding="utf-8")).split())
    for phrase in (
        "ESS.C:71-75", "IMSDATA.C:14", "100 Perioden", "If-Match",
        "Fuenf-Perioden-Nachweis", "fluechtig", "keine neue", "PR150-ZIP",
        "incomming/", "historische",
    ):
        assert phrase in text
    for index, name in (("docs/plans/README.md", PLAN.name),
                        ("docs/migration/README.md", MAPPING.name)):
        assert name in (ROOT / index).read_text(encoding="utf-8")


def test_pr151_handbook_screenshots_are_wide_and_narrow():
    text = HANDBOOK.read_text(encoding="utf-8")
    for shape, width in (("wide", 1000), ("narrow", 300)):
        name = f"windows_hundred_period_results_pr151_{shape}_2026-09-16.png"
        image = ROOT / "docs/handbook/images" / name
        assert image.is_file()
        data = image.read_bytes()
        assert data[:8] == b"\x89PNG\r\n\x1a\n"
        actual_width, height = struct.unpack(">II", data[16:24])
        assert actual_width >= width
        assert height >= 700
        assert name in text


def test_pr151_workbench_has_explicit_start_comparison_and_digest_bound_download():
    app = (ROOT / "frontend/src/main.tsx").read_text(encoding="utf-8")
    results = (ROOT / "frontend/src/HundredPeriodResults.tsx").read_text(
        encoding="utf-8"
    )
    assert 'data-testid="strategy-results-tab"' in app
    for marker in (
        'data-testid="hundred-run-confirm"',
        'data-testid="hundred-run-start"',
        'data-testid="hundred-result"',
        'data-testid="hundred-download"',
        '"If-Match"',
        "baseline_result_digest",
    ):
        assert marker in results
