from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def test_pr169c_documents_storage_integrity_export_and_remaining_ui_boundary() -> None:
    migration = (ROOT / "docs/migration/ims_2x_health_result_delivery.md").read_text(encoding="utf-8")
    plan = (ROOT / "docs/plans/ims_2x_pr169_health_balance_and_simulation_plan.md").read_text(encoding="utf-8")
    roadmap = (ROOT / "docs/plans/ims_2x_all_lines_management_lab_roadmap.md").read_text(encoding="utf-8")
    normalized = " ".join(migration.replace("*", "").split())

    for phrase in (
        "IMSDATA.C", "IMS.E", "ims.health-result-start.v1",
        "explizit konfigurierten SQLite-Pfad", "Idempotenzschluessel",
        "CSV", "JSON", "XLSX", "If-Match", "20 Sekunden",
        "keine neue Kranken-Fachregel", "historische Vollgleichheit", "PR169d",
    ):
        assert phrase in normalized
    assert "## PR169c: Ergebnisfreigabe und Export" in plan
    assert "| PR169c | Kranken-Ergebnisablage, API und CSV/JSON/XLSX | umgesetzt:" in roadmap
    assert "PR170 hat die vier explizit eingegebenen Sparten" in roadmap
    assert "| PR169c | Kranken-Ergebnisablage, API und CSV/JSON/XLSX | umgesetzt:" in roadmap
    assert "ims_2x_health_result_delivery.md" in (
        ROOT / "docs/migration/README.md"
    ).read_text(encoding="utf-8")
