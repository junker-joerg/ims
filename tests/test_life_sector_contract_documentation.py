from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
MIGRATION = ROOT / "docs" / "migration" / "ims_2x_life_sector_contract.md"
PLAN = ROOT / "docs" / "plans" / "ims_2x_pr158_life_sector_contract_plan.md"


def test_life_contract_documents_historical_limit_and_open_decisions() -> None:
    migration = MIGRATION.read_text(encoding="utf-8")
    plan = PLAN.read_text(encoding="utf-8")

    for phrase in (
        "IMSDATA.C", "IMS.E", "kein Beleg", "geschlossener homogener",
        "Garantieverpflichtung", "liability_release", "keine heute waehlbaren",
        "PR159", "kein Neugeschaeft",
    ):
        assert phrase.lower() in migration.lower()
    assert "keine historische Gleichheitsbehauptung" in plan
