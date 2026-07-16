from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
PLAN = REPO_ROOT / "docs" / "plans" / "ims_core_fachlogik_resume_plan.md"
RUN_CONTROL_CORE_BRIDGE_PLAN = (
    REPO_ROOT / "docs" / "plans" / "run_control_core_diagnostics_bridge_plan.md"
)
RUN_CONTROL_EXECUTION_RELEASE_PLAN = (
    REPO_ROOT / "docs" / "plans" / "run_control_execution_release_plan.md"
)
EXPLICIT_PERIOD_TRANSITION_PLAN = (
    REPO_ROOT / "docs" / "plans" / "explicit_period_transition_slice.md"
)
EXPLICIT_TRANSITION_CARRYOVER_PLAN = (
    REPO_ROOT / "docs" / "plans" / "explicit_transition_carryover_code_slice.md"
)
FIRST_FACHLICHER_SLICE_TEST_PLAN = (
    REPO_ROOT / "docs" / "plans" / "first_fachlicher_slice_test_plan.md"
)
FIRST_FACHLICHER_REGRESSION_DOC = (
    REPO_ROOT / "docs" / "migration" / "first_fachlicher_regressionstest.md"
)
SECOND_FACHLICHER_SLICE_TEST_PLAN = (
    REPO_ROOT / "docs" / "plans" / "second_fachlicher_slice_test_plan.md"
)
SECOND_FACHLICHER_REGRESSION_DOC = (
    REPO_ROOT / "docs" / "migration" / "second_fachlicher_regressionstest.md"
)
THIRD_FACHLICHER_SLICE_TEST_PLAN = (
    REPO_ROOT / "docs" / "plans" / "third_fachlicher_slice_test_plan.md"
)
THIRD_FACHLICHER_REGRESSION_DOC = (
    REPO_ROOT / "docs" / "migration" / "third_fachlicher_regressionstest.md"
)
FOURTH_FACHLICHER_REGRESSION_DOC = (
    REPO_ROOT / "docs" / "migration" / "fourth_fachlicher_regressionstest.md"
)
FIFTH_FACHLICHER_REGRESSION_DOC = (
    REPO_ROOT / "docs" / "migration" / "fifth_fachlicher_regressionstest.md"
)
SIXTH_FACHLICHER_SLICE_TEST_PLAN = (
    REPO_ROOT / "docs" / "plans" / "sixth_fachlicher_slice_test_plan.md"
)
SIXTH_FACHLICHER_REGRESSION_DOC = (
    REPO_ROOT / "docs" / "migration" / "sixth_fachlicher_regressionstest.md"
)
SEVENTH_FACHLICHER_REGRESSION_DOC = (
    REPO_ROOT / "docs" / "migration" / "seventh_fachlicher_regressionstest.md"
)
PRODUCTION_READINESS_PLAN = (
    REPO_ROOT / "docs" / "plans" / "production_readiness_pr_plan.md"
)
CONTROLLED_EXECUTION_ADAPTER_PLAN = (
    REPO_ROOT / "docs" / "plans" / "controlled_execution_adapter_plan.md"
)
CONTROLLED_EXECUTION_ADAPTER_CONTRACT_DOC = (
    REPO_ROOT / "docs" / "migration" / "controlled_execution_adapter_contract.md"
)
CONTROLLED_EXECUTION_ADAPTER_DOC = (
    REPO_ROOT / "docs" / "migration" / "controlled_execution_adapter.md"
)
RUN_CONTROL_ADAPTER_RESULT_PLAN = (
    REPO_ROOT / "docs" / "plans" / "run_control_adapter_result_plan.md"
)
RUN_CONTROL_ADAPTER_RESULT_VIEW_PLAN = (
    REPO_ROOT / "docs" / "plans" / "run_control_adapter_result_view_plan.md"
)
RUN_CONTROL_ADAPTER_RESULT_CONTRACT_DOC = (
    REPO_ROOT / "docs" / "migration" / "run_control_adapter_result_contract.md"
)
RUN_CONTROL_ADAPTER_RESULT_API_CONTRACT_DOC = (
    REPO_ROOT / "docs" / "migration" / "run_control_adapter_result_api_contract.md"
)
RUN_CONTROL_ADAPTER_START_CONTRACT_DOC = (
    REPO_ROOT / "docs" / "migration" / "run_control_adapter_start_contract.md"
)
RUN_CONTROL_EXECUTION_RESULT_STORE_DOC = (
    REPO_ROOT / "docs" / "migration" / "run_control_execution_result_store.md"
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
    assert "ims.engine.explicit_period_transition_diagnostics" in plan
    assert "explicit_period_transition_no_policyholders" in plan
    assert "replay_vn_policyholder_transition_plan.json" in plan
    assert "docs/plans/explicit_transition_carryover_code_slice.md" in plan
    assert "apply_vu_foreign_info_carryover" in plan
    assert "apply_vn_state_carryover" in plan
    assert "ims.engine.explicit_transition_carryover_probe" in plan
    assert "explicit_transition_carryover_probe_contract" in plan
    assert "GET /api/core-validation/carryover-probe-contract" in plan
    assert "Carryover-Probe-Vertrag" in plan
    assert "ohne Probe-Upload, Probe-Start" in plan
    assert "Demo-/Doku-Smoke fuer die read-only Carryover/Kern-Sicht ist umgesetzt" in plan
    assert "carryover-probe-contract" in plan
    assert "0 PRs bis zur demo-nahen read-only Carryover/Kern-Sicht" in plan
    assert "first_fachlicher_slice_test_plan.md" in plan
    assert "Versicherer `11` und Policyholder `21`" in plan
    assert "globale Perioden `21 -> 22`" in plan
    assert "tests/test_first_fachlicher_vn_carryover_regression.py" in plan
    assert "erster fachlicher VN-Carryover-Slice-Test ist als Regressionstest umgesetzt" in plan
    assert "0 PRs bis zum ersten ausgefuehrten fachlichen Regressionstest" in plan
    assert "first_fachlicher_regressionstest.md" in plan
    assert "0 PRs bis zur geschaerften Einordnung" in plan
    assert "second_fachlicher_slice_test_plan.md" in plan
    assert "VN-Regelwirkung ueber explizite `best_info`-Snapshots" in plan
    assert "Policyholder `21`, Versicherer `11/12`, Periode `5`" in plan
    assert "Versicherungsentscheidung `[12, None]`" in plan
    assert "information_cost = 4.0" in plan
    assert "tests/test_second_fachlicher_vn_rule_snapshot_regression.py" in plan
    assert "second_fachlicher_regressionstest.md" in plan
    assert "zweiter fachlicher VN-Regel-Snapshot-Slice ist als Regressionstest" in plan
    assert "0 PRs bis zum zweiten ausgefuehrten fachlichen Regressionstest" in plan
    assert "third_fachlicher_slice_test_plan.md" in plan
    assert "VU-Carryover-Fixture fuer Versicherer `10`" in plan
    assert "lokaler Periode `2` nach `3`" in plan
    assert "foreign_info.insurer.dp = [51.0, 52.0]" in plan
    assert "policyholders_prev_sector = [30.0, 80.0]" in plan
    assert "tests/test_third_fachlicher_vu_carryover_regression.py" in plan
    assert "third_fachlicher_regressionstest.md" in plan
    assert "dritter fachlicher VU-Carryover-Fixture-Slice ist als Regressionstest" in plan
    assert "0 PRs bis zum dritten ausgefuehrten fachlichen Regressionstest" in plan
    assert "controlled_execution_adapter_plan.md" in plan
    assert "Ausfuehrungsadapter-Vertrag" in plan
    assert "execution_performed = false" in plan
    assert "python_port/ims/api/controlled_execution_adapter_contract.py" in plan
    assert "tests/test_api_controlled_execution_adapter_contract.py" in plan
    assert "docs/migration/controlled_execution_adapter_contract.md" in plan
    assert "python_port/ims/api/controlled_execution_adapter.py" in plan
    assert "tests/test_api_controlled_execution_adapter.py" in plan
    assert "docs/migration/controlled_execution_adapter.md" in plan
    assert "docs/plans/run_control_adapter_result_plan.md" in plan
    assert "read-only Adapter-Resultat fuer Run-Control" in plan
    assert "python_port/ims/api/run_control_adapter_result_contract.py" in plan
    assert "tests/test_api_run_control_adapter_result_contract.py" in plan
    assert "docs/migration/run_control_adapter_result_contract.md" in plan
    assert "docs/plans/run_control_adapter_result_view_plan.md" in plan
    assert "python_port/ims/api/run_control_adapter_result_api_contract.py" in plan
    assert "tests/test_api_run_control_adapter_result_api_contract.py" in plan
    assert "docs/migration/run_control_adapter_result_api_contract.md" in plan
    assert "0 PRs bis zu einem read-only Ausfuehrungsadapter-Vertrag" in plan
    assert "0 PRs bis zu einem lokalen expliziten Adapter ohne API-/UI-Startpfad" in plan
    assert "0 PRs bis zur Entscheidung fuer ein read-only Adapter-Resultat" in plan
    assert "0 PRs bis zu einem read-only Adapter-Resultat-Vertrag" in plan
    assert "read-only API-Vertrag fuer Adapter-Resultate ist umgesetzt" in plan
    assert "gesperrte UI-Karte fuer Adapter-Resultat-Vertrag ist umgesetzt" in plan
    assert "tests/test_fourth_fachlicher_vn_best_info_carryover_regression.py" in plan
    assert "docs/migration/fourth_fachlicher_regressionstest.md" in plan
    assert "vierter fachlicher VN-`best_info`-/Carryover-Slice" in plan
    assert "0 PRs bis zum vierten ausgefuehrten fachlichen Regressionstest" in plan
    assert "tests/test_fifth_fachlicher_vn_sample_search_regression.py" in plan
    assert "docs/migration/fifth_fachlicher_regressionstest.md" in plan
    assert "fuenfter fachlicher VN-`sample_search`-/Settlement-Slice" in plan
    assert "0 PRs bis zum fuenften ausgefuehrten fachlichen Regressionstest" in plan
    assert "docs/plans/run_control_execution_release_plan.md" in plan
    assert "Run-Control-Ausfuehrungsfreigabeplan ist dokumentiert" in plan
    assert "python_port/ims/api/run_control_adapter_start_contract.py" in plan
    assert "tests/test_api_run_control_adapter_start_contract.py" in plan
    assert "docs/migration/run_control_adapter_start_contract.md" in plan
    assert "GET /api/run-control/adapter-start-contract" in plan
    assert "API-Startvertrag fuer den kontrollierten Adapter ist hart gegated umgesetzt" in plan
    assert "python_port/ims/api/run_control_execution_result_store.py" in plan
    assert "tests/test_api_run_control_execution_result_store.py" in plan
    assert "docs/migration/run_control_execution_result_store.md" in plan
    assert "Queue-/Status-/Resultat-Persistenz fuer freigegebene Ausfuehrung ist lokal" in plan
    assert "docs/migration/run_control_execution_flow_ui.md" in plan
    assert "Run-Control-Ausfuehrungsflow in der Workbench ist umgesetzt" in plan
    assert "docs/migration/run_control_execution_result_view.md" in plan
    assert "Run-Control-Ergebnisanzeige fuer persistierte Adapterresultate ist umgesetzt" in plan
    assert "PR 48 Demo-Smoke und Doku fuer den benutzbaren Ablauf ist umgesetzt" in plan
    assert "PR 49 Packaging-/Startskript-Haertung fuer die lokale Auslieferung ist" in plan
    assert "PR 50 legt die Produktionsreife-Roadmap fest" in plan
    assert "Vrvn04 / `search_history` als Plan fuer PR 51" in plan
    assert "sechster fachlicher VN-`search_history`-/Vrvn04-Slice ist" in plan
    assert "0 PRs bis zum sechsten ausgefuehrten fachlichen Regressionstest" in plan
    assert "siebter fachlicher VN-`preference`-/Vrvn03-Slice ist" in plan
    assert "0 PRs bis zum siebten ausgefuehrten fachlichen Regressionstest" in plan
    assert "vorgeschlagener naechster Schritt ist PR 53" in plan
    assert "VN-`random`-/Vrvn02-Slice mit expliziten Draws" in plan
    assert "Run-Control-Ergebnisanzeige fuer persistierte Adapterresultate anbinden" in plan
    assert "Queue-/Status-/Resultat-Persistenz" in plan
    assert "0 weitere Pflicht-PRs bis zu einer startbar verpackten kontrollierten Demo" in plan
    assert "16-22" in plan
    assert "Produktionsreife mit validiertem Altdaten-Korpus und laufender UI" in plan
    assert "automatic_historical_rule_selection_performed` auf `false`" in plan


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


def test_production_readiness_plan_scopes_remaining_prs() -> None:
    plan = PRODUCTION_READINESS_PLAN.read_text(encoding="utf-8")

    assert PRODUCTION_READINESS_PLAN.is_file()
    assert "Plan: PRs bis zur Produktionsreife" in plan
    assert "validiertem Altdaten-Korpus" in plan
    assert "laufender UI" in plan
    assert "PR 50: sechsten fachlichen Slice waehlen" in plan
    assert "PR 51: sechsten fachlichen Regressionstest fuer Vrvn04" in plan
    assert "Phase A: Fachliche Slice-Abdeckung erweitern" in plan
    assert "Phase B: Altdaten-Validierung verdichten" in plan
    assert "Phase C: Kontrollierte Ausfuehrung und UI" in plan
    assert "Phase D: Freigabehaertung" in plan
    assert "16-22" in plan
    assert "keine aktuelle Behauptung historischer Vollgleichheit" in plan
    assert "keine automatische historische Regelwahl" in plan
    assert "keinen UI-Startpfad frei" in plan


def test_sixth_fachlicher_slice_plan_selects_vrvn04_search_history() -> None:
    plan = SIXTH_FACHLICHER_SLICE_TEST_PLAN.read_text(encoding="utf-8")

    assert SIXTH_FACHLICHER_SLICE_TEST_PLAN.is_file()
    assert "Sechster fachlicher Slice-Test" in plan
    assert "Vrvn04" in plan
    assert "`search_history`" in plan
    assert "tests/test_sixth_fachlicher_vn_search_history_regression.py" in plan
    assert "docs/migration/sixth_fachlicher_regressionstest.md" in plan
    assert "apply_vn_search_insurance_rule" in plan
    assert "apply_vn_insurance_rule_snapshots" in plan
    assert "run_vn_settlement_period_from_mapping" in plan
    assert "chosen_insurer_ids = [12, None]" in plan
    assert "selected_insurer_ids = [12, 11]" in plan
    assert "damages = [9.0, 0.0]" in plan
    assert "end_wealth_current = 87.0" in plan
    assert "Keine Simulation" in plan
    assert "Keine historische Vollgleichheitsbehauptung" in plan


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


def test_run_control_execution_release_plan_scopes_release_chain() -> None:
    plan = RUN_CONTROL_EXECUTION_RELEASE_PLAN.read_text(encoding="utf-8")

    assert RUN_CONTROL_EXECUTION_RELEASE_PLAN.is_file()
    assert "Run-Control-Ausfuehrungsfreigabe" in plan
    assert "Dieser PR 43" in plan
    assert "controlled_execution_adapter" in plan
    assert "`--explicit-execution-release`" in plan
    assert "Execution release" in plan
    assert "Adapter start" in plan
    assert "Result persistence" in plan
    assert "Queue-Eintrag existiert" in plan
    assert "explicit_execution_release = true" in plan
    assert "api_starts_adapter" in plan
    assert "kein sofortiger UI-Startbutton" in plan
    assert "kein Queue-Worker" in plan
    assert "kein Scheduler-Start" in plan
    assert "kein Browser-Upload" in plan
    assert "keine automatische historische Regelwahl" in plan
    assert "keine neue Fachlogik" in plan
    assert "Umsetzung in PR 44" in plan
    assert "python_port/ims/api/run_control_adapter_start_contract.py" in plan
    assert "GET /api/run-control/adapter-start-contract" in plan
    assert 'planned_start_endpoint = "/api/run-control/adapter-start"' in plan
    assert "api_accepts_start_payload = false" in plan
    assert "api_starts_adapter = false" in plan
    assert "POST /api/run-control/adapter-start" in plan
    assert "PR 44: API-Startvertrag" in plan
    assert "Umsetzung in PR 45" in plan
    assert "python_port/ims/api/run_control_execution_result_store.py" in plan
    assert "run_control_execution_results" in plan
    assert "result_persisted" in plan
    assert "inspect_persisted_result" in plan
    assert "Run-Control-Ausfuehrungsflow in der Workbench anzeigen" in plan
    assert "GET /api/run-control/execution-result/{queue_id}" in plan
    assert "Run-Control-Ergebnisanzeige" in plan
    assert "PR 48: Demo-Smoke und Doku" in plan
    assert "## Umsetzung in PR 48" in plan
    assert "tests/test_workbench_demo_smoke.py" in plan
    assert "nach PR 49 0 weitere Pflicht-PRs" in plan
    assert "## Umsetzung in PR 49" in plan
    assert "IMS_WORKBENCH_HOST" in plan
    assert "PR 50 schreibt die Produktionsreife-Roadmap fest" in plan
    assert "Vrvn04 / `search_history` als Plan fuer" in plan
    assert "PR 51 setzt diesen sechsten fachlichen" in plan
    assert "groessere Umsetzungsschritt war PR 52" in plan
    assert "PR 52 ist erledigt" in plan
    assert "naechste fachliche Schritt" in plan
    assert "Vrvn02 / `random` mit expliziten Draws" in plan
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
    assert "ims.engine.explicit_period_transition_diagnostics" in plan
    assert "writes_performed = false" in plan
    assert "execution_performed = false" in plan
    assert "simulation_performed = false" in plan
    assert "automatic_historical_rule_selection_performed = false" in plan
    assert "keine neue Fachlogik" in plan
    assert "keine Simulation und kein Scheduler-Start" in plan
    assert "keine Uebernahme von `VU014PR1.DAT`" in plan
    assert "keine historische Vollgleichheitsbehauptung" in plan


def test_explicit_transition_carryover_code_plan_keeps_code_slice_narrow() -> None:
    plan = EXPLICIT_TRANSITION_CARRYOVER_PLAN.read_text(encoding="utf-8")

    assert EXPLICIT_TRANSITION_CARRYOVER_PLAN.is_file()
    assert "Enger Carryover-Code-Slice fuer explizite Periodenuebergaenge" in plan
    assert "Dieser PR 20" in plan
    assert "apply_vu_foreign_info_carryover" in plan
    assert "python_port/ims/engine/vu_rule_runner.py" in plan
    assert "apply_vn_state_carryover" in plan
    assert "python_port/ims/engine/vn_rule_runner.py" in plan
    assert "diagnose_explicit_period_transitions" in plan
    assert "python_port/ims/engine/explicit_period_transition_diagnostics.py" in plan
    assert "tests/fixtures/replay_vu14_period_plan.json" in plan
    assert "tests/fixtures/replay_vusk1_period_plan.json" in plan
    assert "tests/fixtures/replay_vn_policyholder_transition_plan.json" in plan
    assert "`VUForeignInfoPeriodRunResult`" in plan
    assert "`VNSettlementPeriodRunResult`" in plan
    assert 'mode = "explicit_transition_carryover_probe"' in plan
    assert "python_port/ims/engine/explicit_transition_carryover_probe.py" in plan
    assert "diagnostic_candidate_ids_match = true" in plan
    assert "writes_performed = false" in plan
    assert "execution_performed = false" in plan
    assert "simulation_performed = false" in plan
    assert "automatic_historical_rule_selection_performed = false" in plan
    assert "kein historisches Vorperioden-Ergebnis erfinden" in plan
    assert "keine automatische historische Regelableitung" in plan
    assert "keine Simulation und kein Scheduler-Start" in plan
    assert "keine Uebernahme von `VU014PR1.DAT`" in plan
    assert "keine historische Vollgleichheitsbehauptung" in plan


def test_first_fachlicher_slice_plan_selects_vn_carryover_regression() -> None:
    plan = FIRST_FACHLICHER_SLICE_TEST_PLAN.read_text(encoding="utf-8")

    assert FIRST_FACHLICHER_SLICE_TEST_PLAN.is_file()
    assert "Erster fachlicher VN-Carryover-Slice-Test" in plan
    assert "Dieser PR 26" in plan
    assert "tests/fixtures/replay_vn_policyholder_transition_plan.json" in plan
    assert "VN-Policyholder-State-Carryover von globaler Periode 21 nach 22" in plan
    assert "entity_id = 11" in plan
    assert "entity_id = 21" in plan
    assert "`apply_vn_state_carryover`" in plan
    assert "`probe_explicit_transition_carryover(..., apply_vn=True)`" in plan
    assert "carried_insurer_ids = [11]" in plan
    assert "carried_policyholder_ids = [21]" in plan
    assert "diagnostic_candidate_ids_match = true" in plan
    assert 'previous_result_source = "explicit_fixture_snapshot"' in plan
    assert 'carried_policyholder_state["21"]["end_wealth_current"] = 999.0' in plan
    assert "kein historischer Gleichheitsnachweis" in plan
    assert "`legacy_c/` enthaelt in diesem Stand keine belastbar gelesene historische" in plan
    assert "PR 27: den VN-Carryover-Slice als eigenen Regressionstest" in plan
    assert "tests/test_first_fachlicher_vn_carryover_regression.py" in plan
    assert "Umgesetzter Regressionstest in PR 27" in plan
    assert "docs/migration/first_fachlicher_regressionstest.md" in plan
    assert "PR 28: die Assertions und Dokumentation" in plan
    assert "PR 28 ordnet diesen Test" in plan
    assert "writes_performed = false" in plan
    assert "execution_performed = false" in plan
    assert "simulation_performed = false" in plan
    assert "automatic_historical_rule_selection_performed = false" in plan
    assert "keine Simulation" in plan
    assert "keine neue Fachregel" in plan
    assert "keine historische Vollgleichheit behaupten" in plan


def test_first_fachlicher_regression_doc_scopes_first_test() -> None:
    doc = FIRST_FACHLICHER_REGRESSION_DOC.read_text(encoding="utf-8")

    assert FIRST_FACHLICHER_REGRESSION_DOC.is_file()
    assert "Erster fachlicher Regressionstest" in doc
    assert "tests/test_first_fachlicher_vn_carryover_regression.py" in doc
    assert "tests/fixtures/replay_vn_policyholder_transition_plan.json" in doc
    assert "`probe_explicit_transition_carryover(..., apply_vn=True)`" in doc
    assert "`apply_vn_state_carryover`" in doc
    assert "Versicherer | `11`" in doc
    assert "Policyholder | `21`" in doc
    assert "globale Periode `21 -> 22`" in doc
    assert "carried_insurer_ids = [11]" in doc
    assert "carried_policyholder_ids = [21]" in doc
    assert "VN_CARRYOVER_INSURER_SOURCE_FIELDS" in doc
    assert "VN_CARRYOVER_POLICYHOLDER_SOURCE_FIELDS" in doc
    assert "writes_performed = false" in doc
    assert "execution_performed = false" in doc
    assert "simulation_performed = false" in doc
    assert "automatic_historical_rule_selection_performed = false" in doc
    assert "kein historischer Vollgleichheitsnachweis" in doc
    assert "kein API-/UI-/Run-Control-Startpfad" in doc
    assert "keine neue Fachregel" in doc
    assert "second_fachlicher_slice_test_plan.md" in doc
    assert "VN-Regelwirkung ueber" in doc


def test_second_fachlicher_slice_plan_selects_vn_rule_snapshot_regression() -> None:
    plan = SECOND_FACHLICHER_SLICE_TEST_PLAN.read_text(encoding="utf-8")

    assert SECOND_FACHLICHER_SLICE_TEST_PLAN.is_file()
    assert "Zweiter fachlicher VN-Regel-Snapshot-Slice" in plan
    assert "Dieser PR 29" in plan
    assert "VN-Regelwirkung ueber explizite Snapshots" in plan
    assert "Regelart `best_info`" in plan
    assert "Policyholder `21`" in plan
    assert "aktive Versicherer `11` und `12`" in plan
    assert "Periode `5`" in plan
    assert "erwartete Versicherungsentscheidung `[12, None]`" in plan
    assert "information_cost = 4.0" in plan
    assert "python_port/ims/model/vn_insurance_rules.py::apply_vn_insurance_rule_snapshots" in plan
    assert "python_port/ims/engine/vn_rule_runner.py::run_vn_settlement_period_from_mapping" in plan
    assert "tests/test_vn_insurance_rules.py::test_vn_insurance_rule_dispatch_applies_mixed_rule_snapshots" in plan
    assert "tests/test_vn_rule_runner.py::test_vn_rule_runner_applies_explicit_insurance_rule_snapshots" in plan
    assert "VU-Carryover bleibt fachlich naheliegend" in plan
    assert "PR 30 setzt den geplanten Slice als eigenen Regressionstest um" in plan
    assert "tests/test_second_fachlicher_vn_rule_snapshot_regression.py" in plan
    assert "docs/migration/second_fachlicher_regressionstest.md" in plan
    assert "PR 30: geplanten `best_info`-VN-Regel-Snapshot-Slice als Regressionstest" in plan
    assert "umsetzen und dokumentieren (erledigt)" in plan
    assert "validiert die fachliche Ausfuehrung" in plan
    assert "keine Simulation" in plan
    assert "kein Scheduler-Start" in plan
    assert "kein API-/UI-/Run-Control-Startpfad" in plan
    assert "keine neue Fachregel" in plan
    assert "keine historische Vollgleichheitsbehauptung" in plan


def test_second_fachlicher_regression_doc_scopes_second_test() -> None:
    doc = SECOND_FACHLICHER_REGRESSION_DOC.read_text(encoding="utf-8")

    assert SECOND_FACHLICHER_REGRESSION_DOC.is_file()
    assert "Zweiter fachlicher Regressionstest" in doc
    assert "tests/test_second_fachlicher_vn_rule_snapshot_regression.py" in doc
    assert "`best_info`" in doc
    assert "`apply_vn_insurance_rule_snapshots`" in doc
    assert "`run_vn_settlement_period_from_mapping`" in doc
    assert "Policyholder | `21`" in doc
    assert "Versicherer | `11` und `12`" in doc
    assert "Periode | `5`" in doc
    assert "chosen_insurer_ids = [12, None]" in doc
    assert "selected_insurer_ids = [12, 11]" in doc
    assert "information_cost = 4.0" in doc
    assert "chosen_insurer_sector_current = [12, None]" in doc
    assert "end_wealth_current = 87.0" in doc
    assert "kein historischer Vollgleichheitsnachweis" in doc
    assert "kein API-/UI-/Run-Control-Startpfad" in doc
    assert "keine neue Fachregel" in doc


def test_third_fachlicher_slice_plan_selects_vu_carryover_fixture() -> None:
    plan = THIRD_FACHLICHER_SLICE_TEST_PLAN.read_text(encoding="utf-8")

    assert THIRD_FACHLICHER_SLICE_TEST_PLAN.is_file()
    assert "Dritter fachlicher VU-Carryover-Fixture-Slice" in plan
    assert "Dieser PR 31" in plan
    assert "VU-Carryover ueber explizite Mehrperioden-Fixture-Grenze" in plan
    assert "Versicherer `10`" in plan
    assert "lokale Perioden `2 -> 3`" in plan
    assert "carry_forward_insurer_state = true" in plan
    assert "insurer_ids = [10]" in plan
    assert "foreign_info.insurer.dp = [51.0, 52.0]" in plan
    assert "policyholders_prev_sector = [30.0, 80.0]" in plan
    assert "python_port/ims/engine/vu_rule_runner.py::apply_vu_foreign_info_carryover" in plan
    assert "run_vu_foreign_info_multi_period_from_mappings" in plan
    assert "test_vu_rule_multi_period_runner_can_carry_current_insurer_state_forward" in plan
    assert "test_vu_rule_multi_period_carryover_advances_net_switcher_previous_basis" in plan
    assert "docs/plans/vu_net_switcher_carryover_window_slice.md" in plan
    assert "docs/migration/vu_foreign_info_period_runner.md" in plan
    assert "PR 32 setzt den geplanten Slice als eigenen Regressionstest um" in plan
    assert "tests/test_third_fachlicher_vu_carryover_regression.py" in plan
    assert "docs/migration/third_fachlicher_regressionstest.md" in plan
    assert "umsetzen und dokumentieren (erledigt)" in plan
    assert "validiert die fachliche Ausfuehrung" in plan
    assert "net_switcher_values" in plan
    assert "keine Simulation" in plan
    assert "kein Scheduler-Start" in plan
    assert "kein API-/UI-/Run-Control-Startpfad" in plan
    assert "keine neue Fachregel" in plan
    assert "keine historische Vollgleichheitsbehauptung" in plan


def test_third_fachlicher_regression_doc_scopes_third_test() -> None:
    doc = THIRD_FACHLICHER_REGRESSION_DOC.read_text(encoding="utf-8")

    assert THIRD_FACHLICHER_REGRESSION_DOC.is_file()
    assert "Dritter fachlicher Regressionstest" in doc
    assert "tests/test_third_fachlicher_vu_carryover_regression.py" in doc
    assert "`run_vu_foreign_info_multi_period_from_mappings`" in doc
    assert "`apply_vu_foreign_info_carryover`" in doc
    assert "Versicherer | `10`" in doc
    assert "lokale Perioden `2 -> 3`" in doc
    assert "Globale Perioden | `14 -> 15`" in doc
    assert "carryovers[0].insurer_ids = [10]" in doc
    assert "foreign_info.insurer.dp = [51.0, 52.0]" in doc
    assert "policyholders_prev_sector = [30.0, 80.0]" in doc
    assert "net_switcher_values = [0.0, 0.0]" in doc
    assert "kein historischer Vollgleichheitsnachweis" in doc
    assert "kein API-/UI-/Run-Control-Startpfad" in doc
    assert "keine neue Fachregel" in doc


def test_fourth_fachlicher_regression_doc_scopes_fourth_test() -> None:
    doc = FOURTH_FACHLICHER_REGRESSION_DOC.read_text(encoding="utf-8")

    assert FOURTH_FACHLICHER_REGRESSION_DOC.is_file()
    assert "Vierter fachlicher Regressionstest" in doc
    assert "tests/test_fourth_fachlicher_vn_best_info_carryover_regression.py" in doc
    assert "`run_vn_settlement_multi_period_from_mappings`" in doc
    assert "`apply_vn_state_carryover`" in doc
    assert "Regelart | `best_info`" in doc
    assert "Policyholder | `21`" in doc
    assert "Versicherer | `11` und `12`" in doc
    assert "lokale Perioden `5 -> 6`" in doc
    assert "Globale Perioden | `5 -> 6`" in doc
    assert "carryovers[0].insurer_ids = [11, 12]" in doc
    assert "carryovers[0].policyholder_ids = [21]" in doc
    assert "chosen_insurer_ids = [12, None]" in doc
    assert "information_cost = 4.0" in doc
    assert "damages = [9.0, 0.0]" in doc
    assert "end_wealth_current = 87.0" in doc
    assert "kein historischer Vollgleichheitsnachweis" in doc
    assert "kein API-/UI-/Run-Control-Startpfad" in doc
    assert "keine neue Fachregel" in doc


def test_fifth_fachlicher_regression_doc_scopes_fifth_test() -> None:
    doc = FIFTH_FACHLICHER_REGRESSION_DOC.read_text(encoding="utf-8")

    assert FIFTH_FACHLICHER_REGRESSION_DOC.is_file()
    assert "Fuenfter fachlicher Regressionstest" in doc
    assert "tests/test_fifth_fachlicher_vn_sample_search_regression.py" in doc
    assert "Regelart | `sample_search`" in doc
    assert "Historischer Bezug | `IMS.E`, `act Vrvn05`" in doc
    assert "`apply_vn_insurance_rule_snapshots`" in doc
    assert "`run_vn_settlement_period_from_mapping`" in doc
    assert "Policyholder | `21`" in doc
    assert "Versicherer | `11` und `12`" in doc
    assert "sampled_insurer_ids = [[11, 12], [11]]" in doc
    assert "used_insurer_choice_draws_by_sector = [[0.0, 0.99], [0.0]]" in doc
    assert "information_cost = 3.0" in doc
    assert "damages = [9.0, 0.0]" in doc
    assert "end_wealth_current = 87.0" in doc
    assert "kein historischer Vollgleichheitsnachweis" in doc
    assert "kein API-/UI-/Run-Control-Startpfad" in doc
    assert "keine neue Fachregel" in doc
    assert "noch 5 bis 7 PRs" in doc


def test_sixth_fachlicher_regression_doc_scopes_sixth_test() -> None:
    doc = SIXTH_FACHLICHER_REGRESSION_DOC.read_text(encoding="utf-8")

    assert SIXTH_FACHLICHER_REGRESSION_DOC.is_file()
    assert "Sechster fachlicher Regressionstest" in doc
    assert "tests/test_sixth_fachlicher_vn_search_history_regression.py" in doc
    assert "Regelart | `search_history`" in doc
    assert "Historischer Bezug | `IMS.E`, `act Vrvn04`" in doc
    assert "`apply_vn_insurance_rule_snapshots`" in doc
    assert "`run_vn_settlement_period_from_mapping`" in doc
    assert "Policyholder | `21`" in doc
    assert "Versicherer | `11` und `12`" in doc
    assert "selected_history_periods = [4, 4]" in doc
    assert "used_fallback = [False, False]" in doc
    assert "damages = [9.0, 0.0]" in doc
    assert "end_wealth_current = 87.0" in doc
    assert "kein historischer Vollgleichheitsnachweis" in doc
    assert "kein API-/UI-/Run-Control-Startpfad" in doc
    assert "keine neue Fachregel" in doc
    assert "Fachschnitt ist PR 52" in doc


def test_seventh_fachlicher_regression_doc_scopes_seventh_test() -> None:
    doc = SEVENTH_FACHLICHER_REGRESSION_DOC.read_text(encoding="utf-8")

    assert SEVENTH_FACHLICHER_REGRESSION_DOC.is_file()
    assert "Siebter fachlicher Regressionstest" in doc
    assert "tests/test_seventh_fachlicher_vn_preference_regression.py" in doc
    assert "Regelart | `preference`" in doc
    assert "Historischer Bezug | `IMS.E`, `act Vrvn03`" in doc
    assert "`apply_vn_insurance_rule_snapshots`" in doc
    assert "`run_vn_settlement_period_from_mapping`" in doc
    assert "Policyholder | `21`" in doc
    assert "Versicherer | `11` und `12`" in doc
    assert "preference_scores = [{11: 0.1, 12: 0.9}, {11: 0.9, 12: 0.1}]" in doc
    assert "used_fallback = [False, False]" in doc
    assert "damages = [9.0, 0.0]" in doc
    assert "end_wealth_current = 87.0" in doc
    assert "kein historischer Vollgleichheitsnachweis" in doc
    assert "kein API-/UI-/Run-Control-Startpfad" in doc
    assert "keine neue Fachregel" in doc
    assert "Fachschnitt ist PR 53" in doc


def test_controlled_execution_adapter_plan_keeps_adapter_gated() -> None:
    plan = CONTROLLED_EXECUTION_ADAPTER_PLAN.read_text(encoding="utf-8")

    assert CONTROLLED_EXECUTION_ADAPTER_PLAN.is_file()
    assert "Kontrollierter Ausfuehrungsadapter nach drei Fach-Slices" in plan
    assert "Dieser PR 33" in plan
    assert "Gewaehlt wird ein schmaler Ausfuehrungsadapterplan" in plan
    assert "Drei fachliche Regressionstests" in plan
    assert "kein API-/UI-Startpfad im ersten Adapter-PR" in plan
    assert "nur explizite VU/VN-Periodenfixtures" in plan
    assert "keine Queue-Ausfuehrung und kein Worker" in plan
    assert "build_explicit_multi_period_execution_summary" in plan
    assert "python_port/ims/api/run_control_queue_action_plan.py" in plan
    assert "python_port/ims/api/run_control_core_diagnostics_bridge.py" in plan
    assert "docs/plans/run_control_core_diagnostics_bridge_plan.md" in plan
    assert "docs/migration/workbench_run_control_plan.md" in plan
    assert "PR 34 bereitet den Ausfuehrungsadapter-Vertrag als read-only DTO vor" in plan
    assert "python_port/ims/api/controlled_execution_adapter_contract.py" in plan
    assert "tests/test_api_controlled_execution_adapter_contract.py" in plan
    assert "docs/migration/controlled_execution_adapter_contract.md" in plan
    assert "execution_performed = false" in plan
    assert "runner_start_enabled = false" in plan
    assert "keinen Runner-Start" in plan
    assert "keine Simulation" in plan
    assert "kein HTTP-/UI-Startpfad" in plan
    assert "kein Queue-Worker" in plan
    assert "keine neue Fachregel" in plan
    assert "keine historische Vollgleichheitsbehauptung" in plan
    assert "PR 34: read-only Ausfuehrungsadapter-Vertrag als DTO und Vertragstest" in plan
    assert "umsetzen und dokumentieren (erledigt)" in plan
    assert "stabile JSON-Form des read-only Vertrags" in plan
    assert "PR 35 setzt danach einen lokalen, explizit aufgerufenen Adapter um" in plan
    assert "python_port/ims/api/controlled_execution_adapter.py" in plan
    assert "tests/test_api_controlled_execution_adapter.py" in plan
    assert "docs/migration/controlled_execution_adapter.md" in plan
    assert "--explicit-execution-release" in plan
    assert "ohne API-/UI-Startpfad (erledigt)" in plan
    assert "PR 36: entscheiden, ob Run-Control zunaechst nur ein read-only" in plan
    assert "docs/plans/run_control_adapter_result_plan.md" in plan
    assert "PR 37: read-only Adapter-Resultat-DTO oder Vertrag vorbereiten" in plan
    assert "python_port/ims/api/run_control_adapter_result_contract.py" in plan
    assert "tests/test_api_run_control_adapter_result_contract.py" in plan
    assert "docs/migration/run_control_adapter_result_contract.md" in plan
    assert "docs/plans/run_control_adapter_result_view_plan.md" in plan
    assert "PR 38 kann danach optional eine rein lesende API-/UI-Anzeige" in plan
    assert "PR 39 stellt den read-only API-Vertrag fuer Adapter-Resultate bereit" in plan
    assert "python_port/ims/api/run_control_adapter_result_api_contract.py" in plan
    assert "docs/migration/run_control_adapter_result_api_contract.md" in plan
    assert "PR 40 zeigt die gesperrte UI-Karte `Adapter-Resultat-Vertrag`" in plan
    assert "PR 41 setzt danach wieder einen schmalen fachlichen VN-Slice um" in plan
    assert "PR 42 setzt einen weiteren schmalen fachlichen VN-Slice um" in plan
    assert "PR 43 bereitet den expliziten Run-Control-Ausfuehrungsfreigabeplan" in plan
    assert "PR 44 stellt den hart gegateten API-Startvertrag" in plan
    assert "python_port/ims/api/run_control_adapter_start_contract.py" in plan
    assert "GET /api/run-control/adapter-start-contract" in plan
    assert "PR 45 setzt die lokale Queue-/Status-/Resultat-Persistenz" in plan
    assert "python_port/ims/api/run_control_execution_result_store.py" in plan
    assert "PR 46 zeigt den UI-Flow" in plan
    assert "PR 47 bindet die read-only Ergebnisanzeige" in plan
    assert "PR 48 sichert den benutzbaren Ablauf als Demo-Smoke" in plan
    assert "PR 49 haertet die Packaging-/Startskriptgrenze" in plan


def test_run_control_adapter_result_plan_keeps_result_readonly() -> None:
    plan = RUN_CONTROL_ADAPTER_RESULT_PLAN.read_text(encoding="utf-8")

    assert RUN_CONTROL_ADAPTER_RESULT_PLAN.is_file()
    assert "Read-only Adapter-Resultat fuer Run-Control" in plan
    assert "Dieser PR 36 entscheidet den naechsten groesseren Schritt" in plan
    assert "nicht sofort eine Run-Control-Ausfuehrung" in plan
    assert "bereits lokal erzeugtes `controlled_execution_adapter`-JSON" in plan
    assert "expected Summary: `explicit_multi_period_execution_summary`" not in plan
    assert "expected_summary" not in plan
    assert "PR 37 soll nur ein read-only Resultat-DTO oder einen Vertrag vorbereiten" in plan
    assert "PR 37 ist umgesetzt" in plan
    assert "python_port/ims/api/run_control_adapter_result_contract.py" in plan
    assert "tests/test_api_run_control_adapter_result_contract.py" in plan
    assert "kein Start von `ims.api.controlled_execution_adapter` aus Run-Control" in plan
    assert "kein Runner-Start aus Run-Control" in plan
    assert "kein Browser-Upload" in plan
    assert "kein API-/UI-Startpfad" in plan
    assert "keine neue Fachregel" in plan
    assert "keine historische Vollgleichheitsbehauptung" in plan


def test_run_control_adapter_result_contract_doc_scopes_readonly_validation() -> None:
    doc = RUN_CONTROL_ADAPTER_RESULT_CONTRACT_DOC.read_text(encoding="utf-8")

    assert RUN_CONTROL_ADAPTER_RESULT_CONTRACT_DOC.is_file()
    assert "Run-Control Adapter-Resultat-Vertrag" in doc
    assert "Dieser PR 37 ergaenzt nur den read-only Vertrag" in doc
    assert "python_port/ims/api/run_control_adapter_result_contract.py" in doc
    assert "tests/test_api_run_control_adapter_result_contract.py" in doc
    assert "`mode = \"run_control_adapter_result_contract\"`" in doc
    assert "`expected_result_mode = \"controlled_execution_adapter\"`" in doc
    assert "`expected_summary_mode = \"explicit_multi_period_execution_summary\"`" in doc
    assert "`adapter_start_allowed = false`" in doc
    assert "`api_accepts_upload = false`" in doc
    assert "python -m ims.api.run_control_adapter_result_contract check" in doc
    assert "Der Check schreibt keine Metadaten" in doc
    assert "kein Start von `ims.api.controlled_execution_adapter` aus Run-Control" in doc
    assert "kein Browser-Upload" in doc
    assert "keine neue Fachregel" in doc
    assert "keine historische Vollgleichheitsbehauptung" in doc


def test_run_control_adapter_result_api_contract_doc_scopes_readonly_endpoint() -> None:
    doc = RUN_CONTROL_ADAPTER_RESULT_API_CONTRACT_DOC.read_text(encoding="utf-8")

    assert RUN_CONTROL_ADAPTER_RESULT_API_CONTRACT_DOC.is_file()
    assert "Run-Control Adapter-Resultat-API-Vertrag" in doc
    assert "Dieser PR 39" in doc
    assert "GET /api/run-control/adapter-result-contract" in doc
    assert "python_port/ims/api/run_control_adapter_result_api_contract.py" in doc
    assert "tests/test_api_run_control_adapter_result_api_contract.py" in doc
    assert "`mode = \"run_control_adapter_result_api_contract\"`" in doc
    assert "`api_accepts_result_payload = false`" in doc
    assert "`api_validates_result_payload = false`" in doc
    assert "`api_starts_adapter = false`" in doc
    assert "kein HTTP-Payload-Check fuer Adapter-Resultate" in doc
    assert "kein Start von `ims.api.controlled_execution_adapter`" in doc
    assert "keine historische Vollgleichheitsbehauptung" in doc


def test_run_control_adapter_start_contract_doc_scopes_hard_gate() -> None:
    doc = RUN_CONTROL_ADAPTER_START_CONTRACT_DOC.read_text(encoding="utf-8")

    assert RUN_CONTROL_ADAPTER_START_CONTRACT_DOC.is_file()
    assert "Run-Control Adapter-Startvertrag" in doc
    assert "Dieser PR 44" in doc
    assert "GET /api/run-control/adapter-start-contract" in doc
    assert "python_port/ims/api/run_control_adapter_start_contract.py" in doc
    assert "tests/test_api_run_control_adapter_start_contract.py" in doc
    assert "`mode = \"run_control_adapter_start_contract\"`" in doc
    assert "`planned_start_endpoint = \"/api/run-control/adapter-start\"`" in doc
    assert "`api_accepts_start_payload = false`" in doc
    assert "`api_validates_start_payload = false`" in doc
    assert "`api_starts_adapter = false`" in doc
    assert "`ui_start_enabled = false`" in doc
    assert "`queue_worker_enabled = false`" in doc
    assert "kein POST-Startendpunkt" in doc
    assert "kein Start von `ims.api.controlled_execution_adapter`" in doc
    assert "keine historische Vollgleichheitsbehauptung" in doc


def test_run_control_execution_result_store_doc_scopes_persistence_boundary() -> None:
    doc = RUN_CONTROL_EXECUTION_RESULT_STORE_DOC.read_text(encoding="utf-8")

    assert RUN_CONTROL_EXECUTION_RESULT_STORE_DOC.is_file()
    assert "Run-Control Ergebnis-Persistenzgrenze" in doc
    assert "Dieser PR 45" in doc
    assert "python -m ims.api.run_control_execution_result_store persist" in doc
    assert "python_port/ims/api/run_control_execution_result_store.py" in doc
    assert "tests/test_api_run_control_execution_result_store.py" in doc
    assert "run_control_execution_results" in doc
    assert "result_persisted" in doc
    assert "inspect_persisted_result" in doc
    assert "`execution_performed` bleibt `false`" in doc
    assert "`--explicit-persistence-release`" in doc
    assert "kein Start von `ims.api.controlled_execution_adapter`" in doc
    assert "keine historische Vollgleichheitsbehauptung" in doc


def test_run_control_adapter_result_view_plan_scopes_next_step() -> None:
    plan = RUN_CONTROL_ADAPTER_RESULT_VIEW_PLAN.read_text(encoding="utf-8")

    assert RUN_CONTROL_ADAPTER_RESULT_VIEW_PLAN.is_file()
    assert "Read-only Anzeige fuer Adapter-Resultate" in plan
    assert "Dieser Plan schlaegt den naechsten Schritt" in plan
    assert "Vorschlag fuer PR 38" in plan
    assert "rein lesende API-/UI-Anzeige" in plan
    assert "bereits lokal erzeugte Adapterresultate" in plan
    assert "run_control_adapter_result_contract.py" in plan
    assert "kein Browser-Upload" in plan
    assert "kein Dateipicker" in plan
    assert "kein Startbutton" in plan
    assert "kein Start von `ims.api.controlled_execution_adapter`" in plan
    assert "PR 39: optional read-only API-Vertrag oder Endpunkt" in plan
    assert "python_port/ims/api/run_control_adapter_result_api_contract.py" in plan
    assert "tests/test_api_run_control_adapter_result_api_contract.py" in plan
    assert "docs/migration/run_control_adapter_result_api_contract.md" in plan
    assert "PR 40: optional UI-Karte" in plan
    assert "`Adapter-Resultat-Vertrag` in `frontend/src/main.tsx`" in plan
    assert "PR 41: danach wieder einen schmalen fachlichen VN-Slice" in plan
    assert "PR 42: weiteren schmalen fachlichen VN-Slice" in plan
    assert "PR 43: danach den expliziten Run-Control-Ausfuehrungsfreigabeplan" in plan
    assert "docs/plans/run_control_execution_release_plan.md" in plan
    assert "PR 44: danach API-Startvertrag" in plan
    assert "GET /api/run-control/adapter-start-contract" in plan
    assert "PR 45: danach Queue-/Status-/Resultat-Persistenz" in plan
    assert "python_port/ims/api/run_control_execution_result_store.py" in plan
    assert "PR 46: danach UI-Flow" in plan
    assert "PR 47: danach Ergebnisanzeige" in plan
    assert "PR 48: danach Demo-Smoke und Doku fuer den benutzbaren Ablauf absichern" in plan
    assert "PR 49: danach Packaging-/Startskript-Haertung" in plan
    assert "keine historische Vollgleichheitsbehauptung" in plan


def test_controlled_execution_adapter_contract_doc_scopes_contract() -> None:
    doc = CONTROLLED_EXECUTION_ADAPTER_CONTRACT_DOC.read_text(encoding="utf-8")

    assert CONTROLLED_EXECUTION_ADAPTER_CONTRACT_DOC.is_file()
    assert "Kontrollierter Ausfuehrungsadapter-Vertrag" in doc
    assert "Dieser PR 34 ergaenzt nur den read-only Vertrag" in doc
    assert "python_port/ims/api/controlled_execution_adapter_contract.py" in doc
    assert "tests/test_api_controlled_execution_adapter_contract.py" in doc
    assert "`mode = \"controlled_execution_adapter_contract\"`" in doc
    assert "`adapter_mode = \"explicit_multi_period_fixture_adapter\"`" in doc
    assert "`expected_summary_mode = \"explicit_multi_period_execution_summary\"`" in doc
    assert "`fixture_path`" in doc
    assert "`execution_enabled=true` aus Queue-Metadaten" in doc
    assert "`runner_start_enabled = false`" in doc
    assert "`writes_enabled = false`" in doc
    assert "`execution_performed = false`" in doc
    assert "kein API-/UI-Startpfad" in doc
    assert "keine neue Fachlogik" in doc
    assert "keine historische Vollgleichheitsbehauptung" in doc


def test_controlled_execution_adapter_doc_scopes_local_adapter() -> None:
    doc = CONTROLLED_EXECUTION_ADAPTER_DOC.read_text(encoding="utf-8")

    assert CONTROLLED_EXECUTION_ADAPTER_DOC.is_file()
    assert "Kontrollierter lokaler Ausfuehrungsadapter" in doc
    assert "Dieser PR 35 setzt den ersten lokalen Ausfuehrungsadapter um" in doc
    assert "python_port/ims/api/controlled_execution_adapter.py" in doc
    assert "tests/test_api_controlled_execution_adapter.py" in doc
    assert "run_explicit_multi_period_from_fixture" in doc
    assert "run_explicit_multi_period_from_plan_fixture" in doc
    assert "build_explicit_multi_period_execution_summary" in doc
    assert "--explicit-execution-release" in doc
    assert "`--output-dir` ist bewusst kein" in doc
    assert "kein HTTP-Endpunkt" in doc
    assert "kein UI-Startpfad" in doc
    assert "kein Queue-Worker" in doc
    assert "keine neue Fachlogik" in doc
    assert "keine historische Vollgleichheitsbehauptung" in doc


def test_plan_indexes_reference_ims_core_resume_plan() -> None:
    plans_readme = PLANS_README.read_text(encoding="utf-8")
    readme = README.read_text(encoding="utf-8")

    assert "ims_core_fachlogik_resume_plan.md" in plans_readme
    assert "IMS-Kern-Fachlogik nach Workbench-v1" in plans_readme
    assert "run_control_core_diagnostics_bridge_plan.md" in plans_readme
    assert "Run-Control-Aktionsplan und Kernlauf-Diagnosen" in plans_readme
    assert "explicit_period_transition_slice.md" in plans_readme
    assert "Periodenuebergangs- und Carryover-Grenze" in plans_readme
    assert "explicit_transition_carryover_code_slice.md" in plans_readme
    assert "bestehenden portierten Carryover-Bausteinen" in plans_readme
    assert "first_fachlicher_slice_test_plan.md" in plans_readme
    assert "ersten fachlichen VN-Carryover-Slice-Test" in plans_readme
    assert "second_fachlicher_slice_test_plan.md" in plans_readme
    assert "fachlichen Slice als VN-Regelwirkung" in plans_readme
    assert "third_fachlicher_slice_test_plan.md" in plans_readme
    assert "fachlichen Slice als VU-Carryover-Fixture" in plans_readme
    assert "production_readiness_pr_plan.md" in plans_readme
    assert "Produktionsreife" in plans_readme
    assert "sixth_fachlicher_slice_test_plan.md" in plans_readme
    assert "Vrvn04 / `search_history`" in plans_readme
    assert "sixth_fachlicher_regressionstest.md" in plans_readme
    assert "PR-51-Einordnung des" in plans_readme
    assert "seventh_fachlicher_regressionstest.md" in plans_readme
    assert "PR-52-Einordnung des" in plans_readme
    assert "controlled_execution_adapter_plan.md" in plans_readme
    assert "PR-33 bis PR-35-Plan" in plans_readme
    assert "schmalen Ausfuehrungsadapter" in plans_readme
    assert "run_control_adapter_result_plan.md" in plans_readme
    assert "PR-36-Entscheidung" in plans_readme
    assert "PR-37-Vertrag" in plans_readme
    assert "run_control_adapter_result_view_plan.md" in plans_readme
    assert "Vorschlag fuer PR 38" in plans_readme
    assert "run_control_adapter_result_api_contract.md" in plans_readme
    assert "GET /api/run-control/adapter-result-contract" in plans_readme
    assert "fourth_fachlicher_regressionstest.md" in plans_readme
    assert "PR-41-Einordnung des" in plans_readme
    assert "fifth_fachlicher_regressionstest.md" in plans_readme
    assert "PR-42-Einordnung des" in plans_readme
    assert "run_control_execution_release_plan.md" in plans_readme
    assert "PR-43-Plan fuer die explizite" in plans_readme
    assert "run_control_adapter_start_contract.md" in plans_readme
    assert "GET /api/run-control/adapter-start-contract" in plans_readme
    assert "run_control_execution_result_store.md" in plans_readme
    assert "result_persisted" in plans_readme
    assert "docs/plans/ims_core_fachlogik_resume_plan.md" in readme
    assert "docs/plans/run_control_core_diagnostics_bridge_plan.md" in readme
    assert "docs/plans/explicit_period_transition_slice.md" in readme
    assert "docs/plans/explicit_transition_carryover_code_slice.md" in readme
    assert "docs/plans/first_fachlicher_slice_test_plan.md" in readme
    assert "docs/migration/first_fachlicher_regressionstest.md" in readme
    assert "docs/plans/second_fachlicher_slice_test_plan.md" in readme
    assert "docs/migration/second_fachlicher_regressionstest.md" in readme
    assert "docs/plans/third_fachlicher_slice_test_plan.md" in readme
    assert "docs/migration/third_fachlicher_regressionstest.md" in readme
    assert "docs/plans/controlled_execution_adapter_plan.md" in readme
    assert "docs/migration/controlled_execution_adapter_contract.md" in readme
    assert "docs/migration/controlled_execution_adapter.md" in readme
    assert "docs/plans/run_control_adapter_result_plan.md" in readme
    assert "docs/plans/run_control_adapter_result_view_plan.md" in readme
    assert "docs/plans/run_control_execution_release_plan.md" in readme
    assert "docs/plans/production_readiness_pr_plan.md" in readme
    assert "docs/plans/sixth_fachlicher_slice_test_plan.md" in readme
    assert "PR 50 waehlt als naechsten" in readme
    assert "tests/test_sixth_fachlicher_vn_search_history_regression.py" in readme
    assert "docs/migration/sixth_fachlicher_regressionstest.md" in readme
    assert "tests/test_seventh_fachlicher_vn_preference_regression.py" in readme
    assert "docs/migration/seventh_fachlicher_regressionstest.md" in readme
    assert "docs/migration/run_control_adapter_result_contract.md" in readme
    assert "docs/migration/run_control_adapter_result_api_contract.md" in readme
    assert "docs/migration/run_control_adapter_start_contract.md" in readme
    assert "docs/migration/run_control_execution_result_store.md" in readme
    assert "docs/migration/fourth_fachlicher_regressionstest.md" in readme
    assert "docs/migration/fifth_fachlicher_regressionstest.md" in readme
    assert "docs/migration/sixth_fachlicher_regressionstest.md" in readme
    assert "docs/migration/seventh_fachlicher_regressionstest.md" in readme
    assert "tests/test_first_fachlicher_vn_carryover_regression.py" in readme
    assert "tests/test_second_fachlicher_vn_rule_snapshot_regression.py" in readme
    assert "tests/test_third_fachlicher_vu_carryover_regression.py" in readme
    assert "tests/test_fourth_fachlicher_vn_best_info_carryover_regression.py" in readme
    assert "tests/test_fifth_fachlicher_vn_sample_search_regression.py" in readme
    assert "tests/test_sixth_fachlicher_vn_search_history_regression.py" in readme
    assert "tests/test_seventh_fachlicher_vn_preference_regression.py" in readme
    assert "python_port/ims/api/controlled_execution_adapter_contract.py" in readme
    assert "python_port/ims/api/controlled_execution_adapter.py" in readme
    assert "python_port/ims/api/run_control_adapter_result_contract.py" in readme
    assert "python_port/ims/api/run_control_adapter_result_api_contract.py" in readme
    assert "python_port/ims/api/run_control_adapter_start_contract.py" in readme
    assert "python_port/ims/api/run_control_execution_result_store.py" in readme
    assert "python -m ims.api.controlled_execution_adapter_contract" in readme
    assert "python -m ims.api.controlled_execution_adapter --fixture" in readme
    assert "python -m ims.api.run_control_adapter_result_contract" in readme
    assert "python -m ims.api.run_control_adapter_result_api_contract" in readme
    assert "python -m ims.api.run_control_adapter_start_contract" in readme
    assert "python -m ims.api.run_control_execution_result_store persist" in readme
    assert "python -m ims.engine.explicit_transition_carryover_probe --apply-vn" in readme
    assert "python -m ims.engine.explicit_period_transition_diagnostics" in readme
    assert "explicit_transition_carryover_probe_contract" in readme
    assert "GET /api/core-validation/carryover-probe-contract" in readme
    assert "GET /api/run-control/adapter-result-contract" in readme
    assert "GET /api/run-control/adapter-start-contract" in readme
    assert "Carryover-Probe-Vertrag" in readme
    assert "0 PRs bis zur" in readme
    assert "3+ fachliche" in readme
    assert "einem breiteren fachlichen Anschluss" in readme
    assert "Versicherer `11` und Policyholder `21`" in readme
    assert "globaler Periode `21` nach `22`" in readme
    assert "zweiter" in readme
    assert "schmaler Slice geplant" in readme
    assert "VN-Regelwirkung ueber explizite `best_info`-Snapshots" in readme
    assert "Policyholder `21`, Versicherer `11/12` und Periode `5`" in readme
    assert "zweite fachliche Regressionstest" in readme
    assert "Uebernahme in den VN-Periodenlauf" in readme
    assert "dritte fachliche Slice" in readme
    assert "VU-Carryover fuer" in readme
    assert "Versicherer `10` von lokaler Periode `2` nach `3`" in readme
    assert "dritte fachliche Regressionstest" in readme
    assert "Vrvu04-Nettowechslerbasis" in readme
    assert "vierte fachliche Regressionstest" in readme
    assert "VN-`best_info`-Entscheidung" in readme
    assert "Periode `5` in den vorhandenen VN-State-Carryover" in readme
    assert "fuenfte fachliche Regressionstest" in readme
    assert "VN-`sample_search`-/Vrvn05-Entscheidung" in readme
    assert "sechste fachliche Regressionstest" in readme
    assert "VN-`search_history`-/Vrvn04-Entscheidung" in readme
    assert "Historienauswahl aus Periode `4`" in readme
    assert "siebte fachliche Regressionstest" in readme
    assert "VN-`preference`-/Vrvn03-Entscheidung" in readme
    assert "Praeferenzscores aus aktiver VU-Werbung" in readme
    assert "grob noch 5 bis 7 PRs" in readme
    assert "Run-Control-Ausfuehrungsfreigabeplan" in readme
    assert "keinen API-Startpfad, keinen UI-Startbutton" in readme
    assert "grob noch 4 bis 6 reviewbare PRs" in readme
    assert "hart gegatete API-Startvertrag" in readme
    assert "PR-44-Schnitt" in readme
    assert "grob noch 3 bis 5 reviewbare PRs" in readme
    assert "lokale Ergebnis-Persistenzgrenze" in readme
    assert "result_persisted" in readme
    assert "grob noch 2 bis 4 reviewbare PRs" in readme
    assert "Run-Control-Ausfuehrungsflow" in readme
    assert "Run-Control-Ergebnisanzeige" in readme
    assert "grob noch 0 bis 2 reviewbare PRs" in readme
    assert "kontrollierter Ausfuehrungsadapter-Vertrag" in readme
    assert "bereits lokal erzeugtes Adapterergebnis als read-only" in readme
    assert "vorab erzeugtes `controlled_execution_adapter`-JSON" in readme
    assert "--explicit-execution-release" in readme
    assert "explicit_multi_period_execution_summary" in readme
    assert "runner_start_enabled" in readme
    assert "execution_performed" in readme
    assert "rein lesende Verbindung zwischen Run-Control-Aktionsplan" in readme
    assert "replay_vu14_period_plan.json" in readme
    assert "replay_vn_policyholder_transition_plan.json" in readme
    assert "explizites Opt-in" in readme
