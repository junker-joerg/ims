from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
MIGRATION = ROOT / "docs" / "migration" / "ims_2x_life_v3_contract.md"
PLAN = ROOT / "docs" / "plans" / "ims_2x_pr160_life_flow_valuation_contract_plan.md"


def test_pr160_documents_historical_boundary_timing_and_deferred_execution() -> None:
    migration = MIGRATION.read_text(encoding="utf-8")
    plan = PLAN.read_text(encoding="utf-8")
    normalized = " ".join((migration + plan).lower().split())
    for phrase in (
        "IMSDATA.C", "IMS.E", "kein", "v1/v2", "Todesfallleistung",
        "Neuvertraege", "Kapitalbewegungen", "ROUND_HALF_EVEN",
        "Mortalitaet", "nicht als vollstaendige v3-Eingabe", "PR161", "PR164",
        "PR165", "PR166-167",
        "Solvency-II", "historische Vollgleichheit",
    ):
        assert phrase.lower() in normalized
    assert "ims_2x_life_v3_contract.md" in (
        ROOT / "docs" / "migration" / "README.md"
    ).read_text(encoding="utf-8")
    assert "ims_2x_pr160_life_flow_valuation_contract_plan.md" in (
        ROOT / "docs" / "plans" / "README.md"
    ).read_text(encoding="utf-8")
