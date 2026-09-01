from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
PLAN = REPO_ROOT / "docs" / "plans" / "user_installation_handbook_plan.md"
PLANS_README = REPO_ROOT / "docs" / "plans" / "README.md"


def test_hb1_inventories_existing_handbook_sources() -> None:
    plan = PLAN.read_text(encoding="utf-8")

    assert "Planungsschnitt: HB1" in plan
    assert "workbench_demo_checklist.md" in plan
    assert "workbench_shell.md" in plan
    assert "workbench_release_checklist.md" in plan
    assert "workbench_metadata_recovery.md" in plan
    assert "windows_release_gate.md" in plan
    assert "scripts/workbench/README.md" in plan


def test_hb3_separates_platform_evidence_from_plans() -> None:
    plan = PLAN.read_text(encoding="utf-8")
    normalized = " ".join(plan.split())

    assert "Windows | `verified_windows_hb3`" in plan
    assert "Linux | `not_verified`" in plan
    assert "iOS/Juno | `feasibility_open`" in plan
    assert "Browser-Client" in plan
    assert "Lokale Juno-Ausfuehrung" in plan
    assert "nicht als unterstuetzte Installation bezeichnet" in normalized


def test_hb3_keeps_target_structure_and_updates_remaining_slices() -> None:
    plan = PLAN.read_text(encoding="utf-8")

    for chapter in (
        "quickstart_windows.md",
        "installation_windows.md",
        "operation.md",
        "results_and_validation.md",
        "data_and_updates.md",
        "troubleshooting.md",
        "installation_linux.md",
        "installation_ios_juno.md",
    ):
        assert chapter in plan
    for slice_name in range(2, 7):
        assert f"HB{slice_name}" in plan
    assert "3 Handbuch-Schnitte" in plan
    assert "580-1.320 LoC" in plan


def test_hb1_keeps_user_docs_and_migration_docs_separate() -> None:
    plan = PLAN.read_text(encoding="utf-8")
    normalized = " ".join(plan.split())

    assert "nicht primaer an Entwickler" in normalized
    assert "docs/handbook/" in plan
    assert "docs/migration/" in plan
    assert "Benutzerbefehle und Entwickler-/Releasebefehle bleiben getrennt" in plan
    assert "`incomming/` bleibt unversioniert" in plan
    assert "keine Simulation" in plan
    assert "keine neue Fachlogik" in plan
    assert "keine historische Vollgleichheitsbehauptung" in normalized


def test_plans_index_lists_hb1_through_hb3() -> None:
    readme = PLANS_README.read_text(encoding="utf-8")

    assert PLAN.is_file()
    assert "user_installation_handbook_plan.md" in readme
    assert "HB1" in readme
    assert "HB2" in readme
    assert "HB3" in readme
