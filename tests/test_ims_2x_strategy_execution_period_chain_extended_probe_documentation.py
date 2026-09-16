from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PLAN = ROOT / "docs/plans/ims_2x_strategy_execution_period_chain_extended_probe_plan.md"
MAPPING = (
    ROOT / "docs/migration/ims_2x_strategy_execution_period_chain_extended_probe.md"
)


def test_pr148_documents_historical_boundary_measurement_and_open_points():
    plan = PLAN.read_text(encoding="utf-8")
    mapping = MAPPING.read_text(encoding="utf-8")
    normalized = " ".join((plan + mapping).split())
    for phrase in (
        "ESS.C:71-75",
        "IMSDATA.C:14",
        "SIMLAENGE = 100",
        "10, 25 und 50",
        "100-Perioden-Grenze",
        "Peak-RSS",
        "fluechtige",
        "kanonisches JSON",
        "keine historische",
    ):
        assert phrase in normalized
    assert "PR149" in mapping
    assert "36,5 MB" in mapping
    assert "kein Teilergebnis" in normalized
    for index in (
        "docs/plans/README.md",
        "docs/migration/README.md",
        "docs/strategy/README.md",
    ):
        text = (ROOT / index).read_text(encoding="utf-8")
        assert MAPPING.name in text or PLAN.name in text
