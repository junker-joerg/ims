from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
PLAN = REPO_ROOT / "docs" / "plans" / "ims_core_fachlogik_resume_plan.md"
RUN_CONTROL_CORE_BRIDGE_PLAN = (
    REPO_ROOT / "docs" / "plans" / "run_control_core_diagnostics_bridge_plan.md"
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
    assert "0 PRs bis zu einem read-only Ausfuehrungsadapter-Vertrag" in plan
    assert "0 PRs bis zu einem lokalen expliziten Adapter ohne API-/UI-Startpfad" in plan
    assert "0 PRs bis zur Entscheidung fuer ein read-only Adapter-Resultat" in plan
    assert "0 PRs bis zu einem read-only Adapter-Resultat-Vertrag" in plan
    assert "vorgeschlagener naechster Schritt ist PR 38" in plan
    assert "read-only API-/UI-Anzeige fuer Adapter-Resultate planen" in plan
    assert "danach 1-2 PRs fuer optionalen read-only API-Vertrag/Endpunkt und UI-Karte" in plan
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
    assert "PR 40: optional UI-Karte" in plan
    assert "PR 41+: danach wieder einen schmalen fachlichen" in plan
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
    assert "controlled_execution_adapter_plan.md" in plans_readme
    assert "PR-33 bis PR-35-Plan" in plans_readme
    assert "schmalen Ausfuehrungsadapter" in plans_readme
    assert "run_control_adapter_result_plan.md" in plans_readme
    assert "PR-36-Entscheidung" in plans_readme
    assert "PR-37-Vertrag" in plans_readme
    assert "run_control_adapter_result_view_plan.md" in plans_readme
    assert "Vorschlag fuer PR 38" in plans_readme
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
    assert "docs/migration/run_control_adapter_result_contract.md" in readme
    assert "tests/test_first_fachlicher_vn_carryover_regression.py" in readme
    assert "tests/test_second_fachlicher_vn_rule_snapshot_regression.py" in readme
    assert "tests/test_third_fachlicher_vu_carryover_regression.py" in readme
    assert "python_port/ims/api/controlled_execution_adapter_contract.py" in readme
    assert "python_port/ims/api/controlled_execution_adapter.py" in readme
    assert "python_port/ims/api/run_control_adapter_result_contract.py" in readme
    assert "python -m ims.api.controlled_execution_adapter_contract" in readme
    assert "python -m ims.api.controlled_execution_adapter --fixture" in readme
    assert "python -m ims.api.run_control_adapter_result_contract" in readme
    assert "python -m ims.engine.explicit_transition_carryover_probe --apply-vn" in readme
    assert "python -m ims.engine.explicit_period_transition_diagnostics" in readme
    assert "explicit_transition_carryover_probe_contract" in readme
    assert "GET /api/core-validation/carryover-probe-contract" in readme
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
