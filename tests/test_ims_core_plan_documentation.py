from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
PLAN = REPO_ROOT / "docs" / "plans" / "ims_core_fachlogik_resume_plan.md"
RUN_CONTROL_CORE_BRIDGE_PLAN = (
    REPO_ROOT / "docs" / "plans" / "run_control_core_diagnostics_bridge_plan.md"
)
EXPLICIT_PERIOD_TRANSITION_PLAN = (
    REPO_ROOT / "docs" / "plans" / "explicit_period_transition_slice.md"
)
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
    assert "GET /api/run-control/core-diagnostics-bridge" in plan
    assert "Kernvalidierungsueberblick" in plan
    assert "docs/migration/workbench_demo_checklist.md" in plan
    assert "docs/plans/run_control_core_diagnostics_bridge_plan.md" in plan
    assert "docs/plans/explicit_period_transition_slice.md" in plan
    assert "ohne Runner-Start" in plan
    assert "ohne Simulation oder automatische historische Regelwahl" in plan
    assert "Periodenuebergangs- und Carryover-Grenze" in plan


def test_ims_core_resume_plan_keeps_boundaries_conservative() -> None:
    plan = PLAN.read_text(encoding="utf-8")

    assert "keine Fachlogikaenderung in diesem Plan-PR" in plan
    assert "keine Simulation starten" in plan
    assert "kein neuer HTTP-Schreibendpunkt" in plan
    assert "kein HTTP- oder UI-Schreibpfad" in plan
    assert "kein funktionaler Run-Start" in plan
    assert "kein Start eines expliziten Periodenrunners aus dem Kernvalidierungsueberblick" in plan
    assert "keine historische Vollgleichheitsbehauptung" in plan
    assert "keine Behauptung, dass nicht vorhandene `legacy_c/`-Quellen gelesen wurden" in plan


def test_run_control_core_bridge_plan_keeps_readonly_boundaries() -> None:
    plan = RUN_CONTROL_CORE_BRIDGE_PLAN.read_text(encoding="utf-8")

    assert RUN_CONTROL_CORE_BRIDGE_PLAN.is_file()
    assert "Read-only Run-Control-Anbindung an Kernlauf-Diagnosen" in plan
    assert "GET /api/run-control/queue/action-plan" in plan
    assert "GET /api/core-validation/overview" in plan
    assert "python -m ims.engine.explicit_period_diagnostics_bundle" in plan
    assert "python -m ims.engine.core_validation_overview --legacy-fixture" in plan
    assert "build_explicit_multi_period_execution_summary" in plan
    assert "2 Planfixtures" in plan
    assert "8 Perioden" in plan
    assert "19 Legacy-Referenzen" in plan
    assert "6300 abgedeckte Zeilen" in plan
    assert 'mode = "run_control_core_diagnostics_bridge"' in plan
    assert "writes_performed = false" in plan
    assert "execution_performed = false" in plan
    assert "inspect_core_validation_overview" in plan
    assert "await_precomputed_execution_summary" in plan
    assert "resolve_core_validation_blockers" in plan
    assert "kein neuer HTTP-Schreibpfad" in plan
    assert "kein Start eines expliziten Periodenrunners" in plan
    assert "keine Simulation" in plan
    assert "keine neue Fachlogik" in plan
    assert "keine historische Vollgleichheitsbehauptung" in plan


def test_explicit_period_transition_plan_selects_next_narrow_slice() -> None:
    plan = EXPLICIT_PERIOD_TRANSITION_PLAN.read_text(encoding="utf-8")

    assert EXPLICIT_PERIOD_TRANSITION_PLAN.is_file()
    assert "Expliziter Periodenuebergang aus vorhandenen Planfixtures" in plan
    assert "Dieser PR 16" in plan
    assert "tests/fixtures/replay_vu14_period_plan.json" in plan
    assert "tests/fixtures/replay_vusk1_period_plan.json" in plan
    assert "VU14L1.DAT" in plan
    assert "VUSK1L4.DAT" in plan
    assert "globale Perioden `1` bis `4`" in plan
    assert "globale Perioden `101` bis `104`" in plan
    assert "keine VN-Policyholder" in plan
    assert "`legacy_c/` enthaelt in diesem Stand keine lesbare historische C-Quelle" in plan
    assert "docs/migration/agrsich_replay_plan.md" in plan
    assert "docs/migration/explicit_vu_vn_period_runner.md" in plan
    assert 'mode = "explicit_period_transition_diagnostics"' in plan
    assert "writes_performed = false" in plan
    assert "execution_performed = false" in plan
    assert "simulation_performed = false" in plan
    assert "automatic_historical_rule_selection_performed = false" in plan
    assert "keine neue Fachlogik" in plan
    assert "keine Simulation und kein Scheduler-Start" in plan
    assert "keine Uebernahme von `VU014PR1.DAT`" in plan
    assert "keine historische Vollgleichheitsbehauptung" in plan


def test_plan_indexes_reference_ims_core_resume_plan() -> None:
    plans_readme = PLANS_README.read_text(encoding="utf-8")
    readme = README.read_text(encoding="utf-8")

    assert "ims_core_fachlogik_resume_plan.md" in plans_readme
    assert "IMS-Kern-Fachlogik nach Workbench-v1" in plans_readme
    assert "run_control_core_diagnostics_bridge_plan.md" in plans_readme
    assert "Run-Control-Aktionsplan und Kernlauf-Diagnosen" in plans_readme
    assert "explicit_period_transition_slice.md" in plans_readme
    assert "Periodenuebergangs- und Carryover-Grenze" in plans_readme
    assert "docs/plans/ims_core_fachlogik_resume_plan.md" in readme
    assert "docs/plans/run_control_core_diagnostics_bridge_plan.md" in readme
    assert "docs/plans/explicit_period_transition_slice.md" in readme
    assert "rein lesende Verbindung zwischen Run-Control-Aktionsplan" in readme
    assert "replay_vu14_period_plan.json" in readme
