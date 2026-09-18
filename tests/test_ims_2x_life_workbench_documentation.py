from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PLAN = ROOT / "docs/plans/ims_2x_pr167_life_workbench_plan.md"
MAPPING = ROOT / "docs/migration/ims_2x_life_workbench.md"
HANDBOOK = ROOT / "docs/handbook/management_seminar_guide.md"


def test_pr167_documents_origin_boundaries_and_remaining_ui_gap() -> None:
    text = PLAN.read_text(encoding="utf-8") + MAPPING.read_text(encoding="utf-8")
    for phrase in (
        "IMSDATA.C", "IMS.E", "ESS.C", "PR166", "Zwei-Perioden",
        "Baseline", "Variante", "Digest", "historische",
        "Browser-Download", "Screenshots", "PR168",
    ):
        assert phrase in text
    assert PLAN.name in (ROOT / "docs/plans/README.md").read_text(encoding="utf-8")
    assert MAPPING.name in (ROOT / "docs/migration/README.md").read_text(encoding="utf-8")


def test_pr167_handbook_and_workbench_offer_guided_life_path() -> None:
    handbook = HANDBOOK.read_text(encoding="utf-8")
    component = (ROOT / "frontend/src/LifeWorkbench.tsx").read_text(encoding="utf-8")
    app = (ROOT / "frontend/src/main.tsx").read_text(encoding="utf-8")
    for marker in (
        "Einen Lebensfall im Seminar vergleichen", "Todesfall",
        "Neugeschaeft", "Beide Faelle berechnen", "SQLite",
    ):
        assert marker in handbook
    for marker in (
        'data-testid="life-workbench"', 'data-testid="life-results"',
        '"/api/accounting/life-period-chain"',
        'explicit_storage_release: true', '"If-Match"',
        "Todesfall A2 in Periode 1", "historyReady",
    ):
        assert marker in component
    assert 'id="life"' in component
    assert "<LifeWorkbench onReady={setLifeReady} />" in app
