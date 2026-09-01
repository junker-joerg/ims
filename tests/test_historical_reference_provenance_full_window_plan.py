from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
PLAN = (
    REPO_ROOT
    / "docs"
    / "plans"
    / "historical_reference_provenance_and_full_window_plan.md"
)
PLANS_README = REPO_ROOT / "docs" / "plans" / "README.md"
PRODUCTION_PLAN = REPO_ROOT / "docs" / "plans" / "production_readiness_pr_plan.md"
CORE_PLAN = REPO_ROOT / "docs" / "plans" / "ims_core_fachlogik_resume_plan.md"


def test_plan_separates_archive_family_from_historical_run() -> None:
    plan = PLAN.read_text(encoding="utf-8")
    normalized = " ".join(plan.split())

    assert "Planungsschnitt: PR 87" in plan
    assert "WVEMOD1.ZIP" in plan
    assert "WVEMOD2.ZIP" in plan
    assert "WVEMOD3.ZIP" in plan
    assert "VDEFMD5A.ZIP" in plan
    assert "same_run_proven" in plan
    assert "archive_family_only" in plan
    assert "mixed_reference_layers" in plan
    assert "contradictory_or_unresolved" in plan
    assert "beweist er weder denselben historischen Lauf" in normalized
    assert "Seed oder Laufparameter duerfen nicht zwischen" in plan


def test_plan_fixes_required_full_window_matrix() -> None:
    plan = PLAN.read_text(encoding="utf-8")
    normalized = plan.replace("\n", " ")

    assert "| 100 | `imsvu014.dat`, `imsvnsk1.dat` | 2 | 200 / je 1 |" in plan
    assert "| 300 | `imsvnr01.dat`, `imsvnr02.dat` | 2 | 600 / je 3 |" in plan
    assert "| Gesamt | 15 Exportidentitaeten / 19 Referenzziele | 15 | 6.300 |" in plan
    assert "| 11 | 5.500 / je 5 |" in plan
    assert "eine einzige 500-zeilige berechnete Tabelle" in plan
    assert "nicht als fuenf Aggregate oder Aggregatebenen" in normalized
    assert "fuenf getrennten modernen 100-Perioden-Laeufen" in normalized


def test_plan_orders_provenance_before_full_window_execution() -> None:
    plan = PLAN.read_text(encoding="utf-8")
    normalized = " ".join(plan.split())

    for pr_number in range(87, 103):
        assert f"PR {pr_number}" in plan
    assert plan.index("PR 88: read-only Archivmanifest") < plan.index(
        "PR 92: Ergebniszeilenvertrag"
    )
    assert "2/15 Tabellen und 200/6.300" in plan
    assert "Zielperioden vollstaendig geliefert" in plan
    assert "4/15 Tabellen und 800/6.300 Zielzeilen" in normalized
    assert "15/15 Tabellen und 6.300/6.300 Zielzeilen" in plan
    assert "Umsetzungsstand: PR 101" in plan
    assert "1 geplanter PR" in normalized
    assert "Verbleibende grobe Bruttoabschaetzung fuer PR 102" in plan
    assert "maximal 100 Perioden je Lauf" in normalized
    assert "`go_separate_reference_tests`" in plan


def test_plan_keeps_current_change_read_only_and_conservative() -> None:
    plan = PLAN.read_text(encoding="utf-8")

    assert "kein Import, kein Staging und keine Versionierung aus `incomming/`" in plan
    assert "keine Runner-, Scheduler-, Adapter-, Server- oder Simulationsausfuehrung" in plan
    assert "keine neue Fachlogik" in plan
    assert "keine historische Vollgleichheits- oder Produktionsfreigabebehauptung" in plan
    assert "110-350 LoC" in plan
    assert "unbekannten fachlichen Korrektur-PRs" in plan


def test_central_plans_and_index_reference_pr87_series() -> None:
    readme = PLANS_README.read_text(encoding="utf-8")
    production = PRODUCTION_PLAN.read_text(encoding="utf-8")
    core = CORE_PLAN.read_text(encoding="utf-8")

    assert PLAN.is_file()
    assert "historical_reference_provenance_and_full_window_plan.md" in readme
    assert "Nach PR 101 ist `1` PR" in production
    assert "PR 102" in production
    assert "Nach PR 101" in core
    assert "`1` geplanter PR" in core
