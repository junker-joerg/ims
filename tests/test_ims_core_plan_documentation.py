from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
PLAN = REPO_ROOT / "docs" / "plans" / "ims_core_fachlogik_resume_plan.md"
PLANS_README = REPO_ROOT / "docs" / "plans" / "README.md"
README = REPO_ROOT / "README.md"


def test_ims_core_resume_plan_marks_workbench_to_core_transition() -> None:
    plan = PLAN.read_text(encoding="utf-8")

    assert "Ruecksprung vom abgeschlossenen lokalen" in plan
    assert "Workbench-Ausbau in die eigentliche IMS-Fachlogik" in plan
    assert "nicht der fachliche IMS-Kern" in plan
    assert "python_port/ims/model/entities.py" in plan
    assert "python_port/ims/engine/explicit_period_runner.py" in plan
    assert "tests/references/legacy_agrsich/" in plan
    assert "`legacy_c/` ist in diesem Stand nur ein Platzhalter" in plan


def test_ims_core_resume_plan_names_next_reviewable_core_block() -> None:
    plan = PLAN.read_text(encoding="utf-8")

    assert "Ergaenze IMS-Kernlauf-Diagnose fuer explizite Periodenplaene" in plan
    assert "Plane Execution-Summary-Vertrag im IMS-Kernvalidierungsueberblick" in plan
    assert "python -m ims.model.legacy_validation_overview tests/fixtures/legacy_validation_bundle.json" in plan
    assert "bestehenden expliziten Periodenplan und Runner inventarisieren" in plan
    assert "deterministische Kernlauf-Diagnose" in plan
    assert "legacy_compare_default" in plan
    assert "keine Reportartefakte" in plan
    assert "keine neuen Fachregeln" in plan
    assert "Periodenfolge" in plan
    assert "Legacy-Targets" in plan
    assert "build_explicit_multi_period_execution_summary" in plan
    assert "Execution-Summary-Vertraege" in plan
    assert "vorhandenen expliziten VU/VN-Periodenplaene" in plan
    assert "2 Planfixtures, 8 Perioden" in plan
    assert "19 Legacy-Referenzen, 6300 abgedeckte Zeilen" in plan
    assert "`/api/core-validation/overview`" in plan
    assert "Kernvalidierungsueberblick" in plan
    assert "docs/migration/workbench_demo_checklist.md" in plan
    assert "ohne Runner-Start" in plan
    assert "ohne Simulation oder automatische historische Regelwahl" in plan


def test_ims_core_resume_plan_keeps_boundaries_conservative() -> None:
    plan = PLAN.read_text(encoding="utf-8")

    assert "keine Fachlogikaenderung in diesem Plan-PR" in plan
    assert "keine Simulation starten" in plan
    assert "kein neuer HTTP-Endpunkt" in plan
    assert "kein HTTP- oder UI-Schreibpfad" in plan
    assert "kein funktionaler Run-Start" in plan
    assert "kein Start eines expliziten Periodenrunners aus dem Kernvalidierungsueberblick" in plan
    assert "keine historische Vollgleichheitsbehauptung" in plan
    assert "keine Behauptung, dass nicht vorhandene `legacy_c/`-Quellen gelesen wurden" in plan


def test_plan_indexes_reference_ims_core_resume_plan() -> None:
    plans_readme = PLANS_README.read_text(encoding="utf-8")
    readme = README.read_text(encoding="utf-8")

    assert "ims_core_fachlogik_resume_plan.md" in plans_readme
    assert "IMS-Kern-Fachlogik nach Workbench-v1" in plans_readme
    assert "docs/plans/ims_core_fachlogik_resume_plan.md" in readme
