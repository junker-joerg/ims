from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def test_pr169b_documents_source_mapping_and_staged_delivery() -> None:
    migration = (ROOT / "docs/migration/ims_2x_health_period_chain.md").read_text(encoding="utf-8")
    plan = (ROOT / "docs/plans/ims_2x_pr169_health_balance_and_simulation_plan.md").read_text(encoding="utf-8")
    roadmap = (ROOT / "docs/plans/ims_2x_all_lines_management_lab_roadmap.md").read_text(encoding="utf-8")
    normalized = " ".join(migration.replace("*", "").split())

    for phrase in (
        "IMSDATA.C", "IMS.E", "ims.health-period-chain-input.v1",
        "1, 2, 5, 10, 25, 50 und 100 Perioden", "Abgang",
        "Neugeschaeft", "null Ergebniszeilen", "1 MB", "PR169c",
        "PR169d", "keine API-Freigabe", "historische Vollgleichheit",
    ):
        assert phrase in normalized
    assert "## PR169b: fluechtige Periodenkette" in plan
    assert "| PR169b | Kontrollierte Kranken-Periodenkette bis 100 | umgesetzt:" in roadmap
    assert "PR170 hat die vier explizit eingegebenen Sparten" in roadmap
    assert "| PR169b | Kontrollierte Kranken-Periodenkette bis 100 | umgesetzt:" in roadmap
    assert "ims_2x_health_period_chain.md" in (
        ROOT / "docs/migration/README.md"
    ).read_text(encoding="utf-8")
