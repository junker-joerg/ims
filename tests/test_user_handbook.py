from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
HANDBOOK_ROOT = REPO_ROOT / "docs" / "handbook"


def _read(filename: str) -> str:
    return (HANDBOOK_ROOT / filename).read_text(encoding="utf-8")


def test_handbook_index_defines_scope_navigation_and_platform_status() -> None:
    index = _read("README.md")

    assert "Handbuchstand: HB2" in index
    assert "[Workbench bedienen](operation.md)" in index
    assert "[Ergebnisse und historische Validierung verstehen]" in index
    assert "[Technische Quellen und Nachweise]" in index
    assert "`Dashboard`" in index
    assert "`Szenarien`" in index
    assert "`Validierung`" in index
    assert "`Runs`" in index
    assert "verified_local_workbench_path" in index
    assert "not_verified" in index
    assert "feasibility_open" in index


def test_operation_follows_visible_controlled_ui_path() -> None:
    operation = _read("operation.md")
    normalized = " ".join(operation.split())

    for label in (
        "Szenario-Uebersicht",
        "Run-Uebersicht",
        "Kernvalidierungsueberblick",
        "Dry-Run pruefen",
        "Queue vormerken",
        "Run-Control-Aktionsplan",
        "Freigabe pruefen",
        "Adapter starten",
        "Run-Control-Ergebnisanzeige",
        "Ergebnis neu laden",
    ):
        assert label in operation
    assert "Preflight -> explizite Freigabe -> Ausfuehren" in normalized
    assert "keinen automatischen Worker und keine historische Simulation" in normalized
    assert "keinen Browser-Upload" in normalized
    assert "`Neuer Lauf` gehoert in HB2 nicht zum freigegebenen" in normalized


def test_results_explain_current_status_without_full_equality_claim() -> None:
    results = _read("results_and_validation.md")
    normalized = " ".join(results.split())

    assert "12/15" in results
    assert "4.800/6.300" in results
    assert "3/15" in results
    assert "1.500/6.300" in results
    assert "3.917" in results
    assert "881" in results
    assert "13.367" in results
    assert "1.335" in results
    assert "fuenf getrennte 100-Perioden-Laeufe" in normalized
    assert "kein historischer 500-Perioden-Lauf" in normalized
    assert "nicht als Vollgleichheitsnachweis" in normalized


def test_technical_reference_links_only_existing_sources() -> None:
    reference = _read("technical_reference.md")
    normalized = " ".join(reference.split())

    expected_paths = (
        "docs/migration/workbench_shell.md",
        "docs/migration/workbench_demo_checklist.md",
        "docs/migration/windows_release_gate.md",
        "docs/migration/production_release_corpus_report.md",
        "docs/migration/historical_500_period_vn_class_delivery.md",
        "docs/plans/user_installation_handbook_plan.md",
        "scripts/workbench/README.md",
    )
    for path in expected_paths:
        assert (REPO_ROOT / path).is_file(), path
    assert "Linux bleibt bis HB4 `not_verified`" in normalized
    assert "iOS/Juno bleibt bis HB5 `feasibility_open`" in normalized


def test_handbook_plan_records_hb2_and_remaining_slices() -> None:
    plan = (REPO_ROOT / "docs/plans/user_installation_handbook_plan.md").read_text(
        encoding="utf-8"
    )
    normalized = " ".join(plan.split())

    assert "Umsetzungsstand: HB2" in plan
    assert "HB2: Benutzerhandbuch-Grundgeruest und Bedienpfad (umgesetzt)" in plan
    assert "Nach HB2 bleiben **4 Handbuch-Schnitte**" in normalized
    assert "HB3 bis HB6" in plan
    assert "840-1.860 LoC" in plan
