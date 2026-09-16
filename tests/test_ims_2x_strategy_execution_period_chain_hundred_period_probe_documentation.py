from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PLAN = ROOT / "docs/plans/ims_2x_strategy_execution_period_chain_hundred_period_probe_plan.md"
MAPPING = ROOT / "docs/migration/ims_2x_strategy_execution_period_chain_hundred_period_probe.md"


def test_pr149_documents_source_boundary_measurement_and_missing_user_path():
    plan = PLAN.read_text(encoding="utf-8")
    mapping = MAPPING.read_text(encoding="utf-8")
    combined = " ".join((plan + mapping).split())
    for phrase in (
        "ESS.C:71-75",
        "IMSDATA.C:14",
        "SIMLAENGE = 100",
        "v1-Eingang",
        "v2-Eingang",
        "99 kanonische Uebergaenge",
        "Periode 99",
        "44,2 MB",
        "kein Teilergebnis",
        "keinen historischen RNG- oder Vollgleichheitsnachweis",
    ):
        assert phrase in combined
    assert "PR150" in mapping
    assert "PR151" in mapping
    for index in (
        "docs/plans/README.md",
        "docs/migration/README.md",
        "docs/strategy/README.md",
    ):
        text = (ROOT / index).read_text(encoding="utf-8")
        assert MAPPING.name in text or PLAN.name in text
