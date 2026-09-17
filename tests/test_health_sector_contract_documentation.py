from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
MIGRATION = ROOT / "docs" / "migration" / "ims_2x_health_sector_contract.md"
PLAN = ROOT / "docs" / "plans" / "ims_2x_pr168_health_sector_contract_plan.md"


def test_pr168_documents_historical_boundary_benefit_timing_and_next_steps() -> None:
    migration = MIGRATION.read_text(encoding="utf-8")
    plan = PLAN.read_text(encoding="utf-8")
    normalized = " ".join((migration + plan).lower().split())
    for phrase in (
        "IMSDATA.C", "IMS.E", "KV", "nicht", "angefallene",
        "ausgezahlte", "Alterungsrueckstellung", "PR169", "PR170",
        "keine Simulation", "historische Vollgleichheit",
    ):
        assert phrase.lower() in normalized
    assert MIGRATION.name in (ROOT / "docs" / "migration" / "README.md").read_text(
        encoding="utf-8"
    )
    assert PLAN.name in (ROOT / "docs" / "plans" / "README.md").read_text(
        encoding="utf-8"
    )
