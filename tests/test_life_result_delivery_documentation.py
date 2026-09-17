from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PLAN = ROOT / "docs" / "plans" / "ims_2x_pr166_life_result_delivery_plan.md"
MIGRATION = ROOT / "docs" / "migration" / "ims_2x_life_result_delivery.md"


def test_pr166_documents_scope_limits_and_next_step() -> None:
    plan = PLAN.read_text(encoding="utf-8")
    migration = MIGRATION.read_text(encoding="utf-8")
    normalized = " ".join((plan + migration).lower().split())
    for phrase in (
        "IMSDATA.C", "IMS.E", "PR163-165", "PR167", "SQLite",
        "Idempotenz", "Digest", "If-Match", "XLSX", "20 Sekunden",
        "46 Sekunden", "100x100", "Backup-/Restore", "keine historische Vollgleichheit",
    ):
        assert phrase.lower() in normalized
    assert PLAN.name in (ROOT / "docs" / "plans" / "README.md").read_text(encoding="utf-8")
    assert MIGRATION.name in (ROOT / "docs" / "migration" / "README.md").read_text(encoding="utf-8")
    roadmap = (ROOT / "docs" / "plans" / "ims_2x_all_lines_management_lab_roadmap.md").read_text(encoding="utf-8")
    assert "PR166 Lebens-Ergebnisdienst umgesetzt, PR167 Workbench naechster Schritt" in roadmap
