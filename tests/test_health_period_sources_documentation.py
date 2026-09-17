from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def test_health_source_contract_is_mapped_and_not_pretending_to_run() -> None:
    document = (ROOT / "docs/migration/ims_2x_health_period_sources.md").read_text(encoding="utf-8")
    plan = (ROOT / "docs/plans/ims_2x_pr169_health_balance_and_simulation_plan.md").read_text(encoding="utf-8")
    roadmap = (ROOT / "docs/plans/ims_2x_all_lines_management_lab_roadmap.md").read_text(encoding="utf-8")

    normalized = " ".join(document.split())
    for phrase in (
        "IMSDATA.C", "IMS.E", "ims.health-period-sources-input.v1",
        "Neugeschaeft", "Abgang", "exogenous", "Periodenende",
        "keine historische Vollgleichheitsbehauptung", "PR169b",
    ):
        assert phrase in normalized
    assert "## PR169a: Quellen- und Bestandsvertrag" in plan
    assert "| PR169a | Kranken-Bestands- und Quellenvertrag | umgesetzt:" in roadmap
    assert "| PR169b | Kontrollierte Kranken-Periodenkette bis 100 |" in roadmap
