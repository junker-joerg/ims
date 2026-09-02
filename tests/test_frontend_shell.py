import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
FRONTEND_DIR = REPO_ROOT / "frontend"


def test_frontend_workbench_entrypoints_are_declared():
    package_json = json.loads((FRONTEND_DIR / "package.json").read_text(encoding="utf-8"))

    assert package_json["scripts"]["build"] == "tsc -b && vite build --configLoader runner"
    assert package_json["dependencies"]["react"]
    assert package_json["dependencies"]["react-dom"]
    assert package_json["devDependencies"]["vite"]


def test_frontend_lockfile_is_committed_for_repeatable_builds():
    lockfile = json.loads((FRONTEND_DIR / "package-lock.json").read_text(encoding="utf-8"))

    assert lockfile["name"] == "ims-workbench-frontend"
    assert lockfile["lockfileVersion"] == 3


def test_frontend_shell_sources_exist():
    assert (FRONTEND_DIR / "index.html").is_file()
    assert (FRONTEND_DIR / "src" / "main.tsx").is_file()
    assert (FRONTEND_DIR / "src" / "styles.css").is_file()


def test_frontend_shell_declares_detail_metadata_contract():
    source = (FRONTEND_DIR / "src" / "main.tsx").read_text(encoding="utf-8")

    assert "/api/scenarios/${encodeURIComponent(selectedScenarioId)}" in source
    assert "/api/runs/${encodeURIComponent(selectedRunId)}" in source
    assert "Metadaten-Detail" in source
    assert "Detaildaten nicht erreichbar" in source


def test_frontend_shell_declares_readonly_import_preview():
    source = (FRONTEND_DIR / "src" / "main.tsx").read_text(encoding="utf-8")

    assert "Importvorschau" in source
    assert "schema_version" in source
    assert "execution_enabled" in source
    assert "Preview lokal per CLI ohne Schreiben" in source
    assert "Snapshot lokal per CLI ohne Browser-Export" in source
    assert "Startdiagnose lokal per CLI ohne Serverstart" in source
    assert "Startplan lokal per CLI nur beschreibend" in source
    assert "Readiness lokal per CLI ohne Serverstart" in source
    assert "CLI-Uebersicht lokal per CLI ohne Seiteneffekte" in source
    assert "Schreibvertrag lokal per CLI nur beschreibend" in source
    assert "Schreibvertragspruefung lokal per CLI ohne Import" in source
    assert "Run-Control-Vertrag lokal per CLI ohne Ausfuehrung" in source
    assert "Run-Control-Preflight lokal per CLI ohne Ausfuehrung" in source
    assert "Export lokal per CLI nur mit explizitem Zielpfad" in source
    assert "Roundtrip lokal per CLI ohne Schreiben" in source
    assert "Browser schreibt keine Metadaten" in source
    assert 'type="file"' not in source


def test_frontend_shell_declares_metadata_source_status():
    source = (FRONTEND_DIR / "src" / "main.tsx").read_text(encoding="utf-8")

    assert "/api/metadata/source" in source
    assert "Metadatenquelle" in source
    assert "storage_kind" in source
    assert "writes_enabled" in source


def test_frontend_shell_declares_readonly_strategy_catalog():
    source = (FRONTEND_DIR / "src" / "main.tsx").read_text(encoding="utf-8")
    styles = (FRONTEND_DIR / "src" / "styles.css").read_text(encoding="utf-8")

    assert 'fetch("/api/strategies/catalog")' in source
    assert 'id="strategies"' in source
    assert 'data-testid="strategy-catalog"' in source
    assert "Strategiekatalog" in source
    assert "Nur lesen" in source
    assert "Historische Vollgleichheit" in source
    assert "historical_action" in source
    assert "source_chapter" in source
    assert "historical_rule_class" in source
    assert "included_in_vdefmd6" in source
    assert "parameterized" in source
    assert "parameter_capabilities" in source
    assert "test_status" in source
    assert "strategy-catalog-panel" in styles
    assert "strategy-table-row" in styles
    assert "strategyCatalog.selection_enabled" in source
    assert "strategyCatalog.parameter_editing_enabled" in source
    assert "strategyCatalog.simulation_performed" in source
    assert 'fetch("/api/strategies/catalog", {' not in source


def test_frontend_shell_declares_readonly_strategy_assignment_views():
    source = (FRONTEND_DIR / "src" / "main.tsx").read_text(encoding="utf-8")
    styles = (FRONTEND_DIR / "src" / "styles.css").read_text(encoding="utf-8")

    assert 'fetch("/api/strategies/assignment-contract")' in source
    assert 'data-testid="strategy-assignment-profiles"' in source
    assert 'data-testid="strategy-parameter-schemas"' in source
    assert 'aria-label="Strategieansichten"' in source
    assert "Zuordnungen" in source
    assert "Parameterschemata" in source
    assert "source_profiles" in source
    assert "parameter_schemas" in source
    assert "assignment_targets" in source
    assert "sector_contract" in source
    assert "parameter_values_exposed" in source
    assert "shortStrategyFingerprint" in source
    assert "Quellwerte geschuetzt" in source
    assert "Vrvn01: Pflichtversicherung" in source
    assert "keine neuen Fachgrenzen" in source
    assert "strategyAssignmentContract.assignment_editing_enabled" in source
    assert "strategyAssignmentContract.parameter_editing_enabled" in source
    assert "strategyAssignmentContract.writes_enabled" in source
    assert "strategyAssignmentContract.execution_enabled" in source
    assert "strategyAssignmentContract.simulation_performed" in source
    assert 'fetch("/api/strategies/assignment-contract", {' not in source
    assert "strategy-workbench-tabs" in styles
    assert "strategy-profile-table" in styles
    assert "strategy-schema-list" in styles
    assert "strategy-schema-field-row" in styles


def test_frontend_shell_declares_readonly_operations_diagnosis():
    source = (FRONTEND_DIR / "src" / "main.tsx").read_text(encoding="utf-8")

    assert "Betriebsdiagnose" in source
    assert "/api/health" in source
    assert "/api/version" in source
    assert "/api/metadata/source" in source
    assert "/api/metadata/capabilities" in source
    assert "lokal per CLI" in source
    assert 'type="file"' not in source


def test_frontend_shell_declares_readonly_metadata_consistency_diagnosis():
    source = (FRONTEND_DIR / "src" / "main.tsx").read_text(encoding="utf-8")

    assert "Metadaten-Konsistenz" in source
    assert "/api/metadata/consistency" in source
    assert "runs_with_missing_scenario" in source
    assert "runs_with_execution_enabled" in source
    assert "Schreibpfade" in source
    assert "Simulation" in source
    assert "issue_count" in source
    assert "repair" not in source


def test_frontend_shell_declares_readonly_run_overview():
    source = (FRONTEND_DIR / "src" / "main.tsx").read_text(encoding="utf-8")

    assert "const selectRun = (run: RunMetadata)" in source
    assert "setSelectedRunId(run.id)" in source
    assert "setSelectedScenarioId(run.scenario_id)" in source
    assert "Run-Uebersicht" in source
    assert "run-overview-row" in source
    assert "period_window" in source
    assert "scenario_id" in source
    assert "execution_enabled" in source
    assert "gesperrt" in source
    assert "startRun" not in source


def test_frontend_shell_declares_readonly_run_control_overview():
    source = (FRONTEND_DIR / "src" / "main.tsx").read_text(encoding="utf-8")
    styles = (FRONTEND_DIR / "src" / "styles.css").read_text(encoding="utf-8")

    assert "Run-Control-Statusband" in source
    assert "runControlBoundaryRows" in source
    assert "runControlPreflightBoundaryStatus" in source
    assert 'runControlPreflight?.status === "error"' in source
    assert "runControlPreflight?.issues.length" in source
    assert "run-control-boundary-panel" in source
    assert "run-control-boundary-grid" in styles
    assert "run-control-boundary-row" in styles
    assert "filterRunControlQueueEntries" in source
    assert "/api/run-control/queue" in source
    assert "/api/run-control/queue/${encodeURIComponent(selectedQueueId)}" in source
    assert "Run-Control-Uebersicht" in source
    assert "Run-Control-Queue-Detail" in source
    assert "Run-Control-Queue-Hinweise" in source
    assert "Run-Control-Queuefilter" in source
    assert "Run-Control-Queuesuche" in source
    assert "Run-Control-Statusfilter" in source
    assert "Run-Control-Szenariofilter" in source
    assert "Queue-Detail" in source
    assert "Queue vormerken" in source
    assert "Run-Control-Queue-Vormerkung" in source
    assert "Run-Control-Aktionsplan" in source
    assert "Run-Control-Ausfuehrungsflow" in source
    assert "Run-Control-Ergebnisanzeige" in source
    assert "Run-Control-Kernblick-Bruecke" in source
    assert "runControlActionPlan" in source
    assert "runControlExecutionFlowRows" in source
    assert "runControlExecutionResultRows" in source
    assert "runControlAdapterStartContract" in source
    assert "runControlExecutionResult" in source
    assert "runControlCoreBridge" in source
    assert "runControlCoreBridgeRows" in source
    assert "Adapter-Resultat-Vertrag" in source
    assert "adapterResultContractRows" in source
    assert "runControlAdapterResultContract" in source
    assert "/api/run-control/adapter-result-contract" in source
    assert "/api/run-control/adapter-start-contract" in source
    assert "/api/run-control/execution-result/${encodeURIComponent(selectedQueueId)}" in source
    assert "/api/run-control/execution-history/${encodeURIComponent(selectedQueueId)}" in source
    assert 'data-testid="adapter-result-contract"' in source
    assert 'data-testid="run-control-execution-flow"' in source
    assert 'data-testid="run-control-execution-result"' in source
    assert "selectedBridgeAction" in source
    assert "selectedQueueAction" in source
    assert "/api/run-control/queue/action-plan" in source
    assert "/api/run-control/core-diagnostics-bridge" in source
    assert "runControlQueueEnqueueResult" in source
    assert "enqueueRunControlQueue" in source
    assert "canEnqueueRunControlQueue" in source
    assert "runControlQueue" in source
    assert "selectedQueueId" in source
    assert "setSelectedQueueId(entry.queue_id)" in source
    assert "filteredQueueEntries.map" in source
    assert "queueActionLabel" in source
    assert "Preflight lokal" in source
    assert "Freigabe abwarten" in source
    assert "Ergebnis pruefen" in source
    assert "Blocker klaeren" in source
    assert "Status pruefen" in source
    assert "run_preflight" in source
    assert "await_execution_release" in source
    assert "resolve_blockers" in source
    assert "inspect_persisted_result" in source
    assert "inspect_queue_status" in source
    assert "inspect_core_validation_overview" in source
    assert "await_precomputed_execution_summary" in source
    assert "resolve_core_validation_blockers" in source
    assert "run-control-panel" in styles
    assert "run-control-filterbar" in styles
    assert "run-control-filter-count" in styles
    assert "run-control-table" in styles
    assert "run-control-detail-grid" in styles
    assert "run-control-issues" in styles
    assert "run-control-queue-enqueue-grid" in styles
    assert "run-control-queue-enqueue-row" in styles
    assert "run-control-action-plan-panel" in styles
    assert "run-control-action-plan-grid" in styles
    assert "run-control-action-plan-row" in styles
    assert "run-control-execution-flow-panel" in styles
    assert "run-control-execution-flow-steps" in styles
    assert "run-control-execution-flow-grid" in styles
    assert "run-control-execution-flow-row" in styles
    assert "run-control-execution-result-panel" in styles
    assert "run-control-execution-result-grid" in styles
    assert "run-control-execution-result-row" in styles
    assert "run-control-core-bridge-panel" in styles
    assert "run-control-core-bridge-grid" in styles
    assert "run-control-core-bridge-row" in styles
    assert "adapter-result-contract-panel" in styles
    assert "adapter-result-contract-grid" in styles
    assert "adapter-result-contract-row" in styles
    assert "Queue-Status" in source
    assert "Queue-Eintraege" in source
    assert "Naechster Schritt" in source
    assert "Keine Queue-Eintraege fuer diesen Filter" in source
    assert "Angelegt von" in source
    assert "Keine Run-Control-Queue-Eintraege" in source
    assert "writes_enabled" in source
    assert "execution_performed" in source
    assert "startRun" not in source
    assert 'type="file"' not in source


def test_frontend_shell_declares_readonly_run_control_request_contract():
    source = (FRONTEND_DIR / "src" / "main.tsx").read_text(encoding="utf-8")
    styles = (FRONTEND_DIR / "src" / "styles.css").read_text(encoding="utf-8")

    assert "/api/run-control/request-contract" in source
    assert "Run-Control-Request-Vertrag" in source
    assert "runControlRequestContract" in source
    assert "required_fields" in source
    assert "optional_fields" in source
    assert "forbidden_fields" in source
    assert "example_request" in source
    assert "Beispiel run_id" in source
    assert "example_request.run_id" in source
    assert "Beispiel scenario_id" in source
    assert "example_request.scenario_id" in source
    assert "Beispiel metadata_db" in source
    assert "example_request.metadata_db" in source
    assert "Beispiel requested_by" in source
    assert "example_request.requested_by" in source
    assert "Beispiel created_at" in source
    assert "example_request.created_at" in source
    assert "Beispiel execution_enabled" in source
    assert "example_request.execution_enabled" in source
    assert "Run-Control-Request-Vertrag per API nur lesend" in source
    assert "run-control-request-panel" in styles
    assert "run-control-request-grid" in styles
    assert "run-control-request-row" in styles
    assert "writes_enabled" in source
    assert "execution_performed" in source
    assert "startRun" not in source
    assert 'type="file"' not in source


def test_frontend_shell_declares_readonly_run_control_preflight():
    source = (FRONTEND_DIR / "src" / "main.tsx").read_text(encoding="utf-8")
    styles = (FRONTEND_DIR / "src" / "styles.css").read_text(encoding="utf-8")

    assert "yesNoLoading" in source
    assert "/api/run-control/preflight/${encodeURIComponent(selectedRunId)}" in source
    assert "Run-Control-Preflight" in source
    assert "runControlPreflight" in source
    assert "setRunControlPreflight" in source
    assert "run_found" in source
    assert "scenario_found" in source
    assert "execution_allowed" in source
    assert "writes_performed" in source
    assert "execution_performed" in source
    assert "Run-Control-Preflight nicht erreichbar" in source
    assert "run-control-preflight-panel" in styles
    assert "run-control-preflight-grid" in styles
    assert "run-control-preflight-row" in styles
    assert "startRun" not in source
    assert 'type="file"' not in source


def test_frontend_shell_declares_readonly_core_validation_overview():
    source = (FRONTEND_DIR / "src" / "main.tsx").read_text(encoding="utf-8")
    styles = (FRONTEND_DIR / "src" / "styles.css").read_text(encoding="utf-8")

    assert "/api/core-validation/overview" in source
    assert "Kernvalidierungsueberblick" in source
    assert "coreValidation" in source
    assert "execution_summary_contract" in source
    assert "Execution-Summary-Vertrag" in source
    assert "overview_starts_runner" in source
    assert "Summary-Felder" in source
    assert "core-validation-panel" in styles
    assert "core-validation-summary" in styles
    assert "core-validation-contract" in styles
    assert "startRun" not in source
    assert "uploadAdapter" not in source
    assert 'type="file"' not in source


def test_frontend_shell_declares_readonly_carryover_probe_contract_card():
    source = (FRONTEND_DIR / "src" / "main.tsx").read_text(encoding="utf-8")
    styles = (FRONTEND_DIR / "src" / "styles.css").read_text(encoding="utf-8")

    assert "/api/core-validation/carryover-probe-contract" in source
    assert "CoreValidationCarryoverProbeContract" in source
    assert "Carryover-Probe-Vertrag" in source
    assert 'data-testid="carryover-probe-contract"' in source
    assert "carryoverProbeContract" in source
    assert "precomputed_probe_required" in source
    assert "expected_probe_mode" in source
    assert "expected_contract_mode" in source
    assert "api_accepts_probe_payload" in source
    assert "api_starts_probe" in source
    assert "ui_enabled" in source
    assert "automatic_historical_rule_selection_performed" in source
    assert "Carryover-Probe-Grenzen" in source
    assert "carryover-probe-panel" in styles
    assert "startRun" not in source
    assert "startProbe" not in source
    assert "uploadProbe" not in source
    assert 'type="file"' not in source


def test_frontend_shell_declares_readonly_adapter_result_contract_card():
    source = (FRONTEND_DIR / "src" / "main.tsx").read_text(encoding="utf-8")
    styles = (FRONTEND_DIR / "src" / "styles.css").read_text(encoding="utf-8")

    assert "/api/run-control/adapter-result-contract" in source
    assert "RunControlAdapterResultApiContract" in source
    assert "Adapter-Resultat-Vertrag" in source
    assert "Adapter-Resultat-Grenzen" in source
    assert 'data-testid="adapter-result-contract"' in source
    assert "runControlAdapterResultContract" in source
    assert "adapterResultContractRows" in source
    assert "expected_result_mode" in source
    assert "expected_validation_mode" in source
    assert "expected_contract_mode" in source
    assert "api_accepts_result_payload" in source
    assert "api_validates_result_payload" in source
    assert "api_starts_adapter" in source
    assert "queue_worker_enabled" in source
    assert "simulation_performed" in source
    assert "automatic_historical_rule_selection_performed" in source
    assert "adapter-result-contract-panel" in styles
    assert "adapter-result-contract-grid" in styles
    assert "adapter-result-contract-row" in styles
    assert "startReleasedAdapter" in source
    assert "checkExecutionRelease" in source
    assert "uploadAdapter" not in source
    assert 'type="file"' not in source


def test_frontend_shell_declares_gated_run_control_execution_flow():
    source = (FRONTEND_DIR / "src" / "main.tsx").read_text(encoding="utf-8")
    styles = (FRONTEND_DIR / "src" / "styles.css").read_text(encoding="utf-8")

    assert "/api/run-control/adapter-start-contract" in source
    assert "RunControlAdapterStartContract" in source
    assert "Run-Control-Ausfuehrungsflow" in source
    assert 'aria-label="Preflight -> explizite Freigabe -> Ausfuehren"' in source
    assert 'data-testid="run-control-execution-flow"' in source
    assert "runControlExecutionFlowSteps" in source
    assert "runControlExecutionFlowRows" in source
    assert "planned_start_endpoint" in source
    assert "api_accepts_start_payload" in source
    assert "api_validates_start_payload" in source
    assert "api_starts_adapter" in source
    assert "ui_start_enabled" in source
    assert "queue_worker_enabled" in source
    assert "historical_full_equality_claimed" in source
    assert "result_persisted" in source
    assert "inspect_persisted_result" in source
    assert "Ausfuehren" in source
    assert "gesperrt" in source
    assert "run-control-execution-flow-panel" in styles
    assert "run-control-execution-flow-steps" in styles
    assert "run-control-execution-flow-step" in styles
    assert "run-control-execution-flow-grid" in styles
    assert "run-control-execution-flow-row" in styles
    assert "/api/run-control/adapter-release-check" in source
    assert "/api/run-control/adapter-start" in source
    assert "RunControlExecutionReleaseRequest" in source
    assert "createUiIdempotencyKey" in source
    assert "executionReleaseConfirmed" in source
    assert "canCheckExecutionRelease" in source
    assert "canStartAdapter" in source
    assert "startReleasedAdapter" in source
    assert 'data-testid="run-control-release-check-button"' in source
    assert 'data-testid="run-control-adapter-start-button"' in source
    assert "vu14-calculated-diagnostic" in source
    assert "carry_forward_vu_state: false" in source
    assert "carry_forward_vn_state: false" in source
    assert "run-control-execution-release" in styles
    assert "run-control-execution-confirmation" in styles
    assert 'type="file"' not in source


def test_frontend_shell_declares_readonly_run_control_execution_result_card():
    source = (FRONTEND_DIR / "src" / "main.tsx").read_text(encoding="utf-8")
    styles = (FRONTEND_DIR / "src" / "styles.css").read_text(encoding="utf-8")

    assert "/api/run-control/execution-result/${encodeURIComponent(selectedQueueId)}" in source
    assert "/api/run-control/execution-history/${encodeURIComponent(selectedQueueId)}" in source
    assert "RunControlExecutionResult" in source
    assert "RunControlExecutionResultRecord" in source
    assert "RunControlExecutionHistory" in source
    assert "RunControlExecutionAttempt" in source
    assert "Run-Control-Ergebnisanzeige" in source
    assert "Persistiertes Run-Control-Ergebnis" in source
    assert 'data-testid="run-control-execution-result"' in source
    assert 'data-testid="run-control-execution-history"' in source
    assert 'data-testid="run-control-execution-result-refresh"' in source
    assert "runControlExecutionResultRows" in source
    assert "runControlExecutionHistoryRows" in source
    assert "runControlExecutionResultState" in source
    assert "runControlExecutionHistoryState" in source
    assert "setExecutionEvidenceRevision" in source
    assert "Ergebnis neu laden" in source
    assert "Automatische Wiederholung" in source
    assert "automatic_retry_enabled" in source
    assert "failure_message" in source
    assert "kein persistiertes Ergebnis" in source
    assert "adapter_execution_performed" in source
    assert "summary_mode" in source
    assert "persisted_at" in source
    assert "historical_full_equality_claimed" in source
    assert "run-control-execution-result-panel" in styles
    assert "run-control-execution-result-grid" in styles
    assert "run-control-execution-result-row" in styles
    assert "run-control-execution-result-refresh" in styles
    assert "retryExecution" not in source
    assert "/api/run-control/execution-retry" not in source
    assert "startRun" not in source
    assert "startAdapter" not in source
    assert "uploadAdapter" not in source
    assert 'type="file"' not in source


def test_frontend_shell_declares_controlled_run_control_dry_run_check():
    source = (FRONTEND_DIR / "src" / "main.tsx").read_text(encoding="utf-8")
    styles = (FRONTEND_DIR / "src" / "styles.css").read_text(encoding="utf-8")

    assert "/api/run-control/dry-run-contract" in source
    assert "/api/run-control/dry-run" in source
    assert "/api/run-control/queue" in source
    assert 'method: "POST"' in source
    assert "Run-Control-Dry-Run-Vertrag" in source
    assert "Run-Control-Dry-Run-Ergebnis" in source
    assert 'data-testid="run-control-demo-dry-run-panel"' in source
    assert 'data-testid="run-control-demo-dry-run-button"' in source
    assert 'data-testid="run-control-demo-queue-button"' in source
    assert 'data-testid="run-control-demo-dry-run-result"' in source
    assert 'data-testid="run-control-demo-queue-result"' in source
    assert 'data-testid="run-control-demo-action-plan"' in source
    assert 'data-testid="run-control-core-bridge"' in source
    assert "runControlDryRunContract" in source
    assert "runControlDryRunResult" in source
    assert "expected_inputs" in source
    assert "required_preconditions" in source
    assert "forbidden_boundaries" in source
    assert "http_enabled" in source
    assert "request_accepted" in source
    assert "preflight_passed" in source
    assert "scenario_matches_request" in source
    assert "dry_run_allowed" in source
    assert "writes_performed" in source
    assert "execution_performed" in source
    assert "Dry-Run pruefen" in source
    assert "Queue vormerken" in source
    assert "Run-Control-Dry-Run per API pruefend ohne Ausfuehrung" in source
    assert "run-control-dry-run-panel" in styles
    assert "run-control-dry-run-grid" in styles
    assert "run-control-dry-run-row" in styles
    assert "run-control-dry-run-result-grid" in styles
    assert "run-control-dry-run-result-row" in styles
    assert "startRun" not in source
    assert "submit" not in source
    assert 'type="file"' not in source


def test_frontend_shell_declares_readonly_scenario_overview():
    source = (FRONTEND_DIR / "src" / "main.tsx").read_text(encoding="utf-8")

    assert "Szenario-Uebersicht" in source
    assert "scenario-overview-row" in source
    assert "domain_scope" in source
    assert "updated_at" in source
    assert "validation.scope" in source
    assert "executionLabel" in source
    assert "startScenario" not in source


def test_frontend_shell_declares_readonly_scenario_filters():
    source = (FRONTEND_DIR / "src" / "main.tsx").read_text(encoding="utf-8")
    styles = (FRONTEND_DIR / "src" / "styles.css").read_text(encoding="utf-8")

    assert "filterScenarios" in source
    assert "Szenariofilter" in source
    assert "Szenariosuche" in source
    assert "Szenario-Statusfilter" in source
    assert "Szenario-Quellenfilter" in source
    assert "Szenario-Scopefilter" in source
    assert "filteredScenarios.map" in source
    assert "Keine Szenarien fuer diesen Filter" in source
    assert "scenario-filterbar" in styles
    assert "scenario-filter-count" in styles
    assert 'type="file"' not in source


def test_frontend_shell_declares_readonly_run_filters():
    source = (FRONTEND_DIR / "src" / "main.tsx").read_text(encoding="utf-8")
    styles = (FRONTEND_DIR / "src" / "styles.css").read_text(encoding="utf-8")

    assert "filterRuns" in source
    assert "Runfilter" in source
    assert "Runsuche" in source
    assert "Run-Statusfilter" in source
    assert "Run-Szenariofilter" in source
    assert "Run-Quellenfilter" in source
    assert "filteredRuns.map" in source
    assert "Keine Runs fuer diesen Filter" in source
    assert "selectRun(run)" in source
    assert "run-filterbar" in styles
    assert "run-filter-count" in styles
    assert "execution_enabled" in source
    assert 'type="file"' not in source


def test_frontend_shell_declares_readonly_selection_summary():
    source = (FRONTEND_DIR / "src" / "main.tsx").read_text(encoding="utf-8")
    styles = (FRONTEND_DIR / "src" / "styles.css").read_text(encoding="utf-8")

    assert "Auswahlzusammenfassung" in source
    assert "selectionRows" in source
    assert "scenarioDetail?.id === selectedScenarioId" in source
    assert "runDetail?.id === selectedRunId" in source
    assert "selectedScenarioHidden" in source
    assert "selectedRunHidden" in source
    assert "Auswahl durch Filter aktuell nicht in den Listen sichtbar" in source
    assert "Auswahl in den Listen sichtbar" in source
    assert "Periodenfenster" in source
    assert "Metadatenquelle" in source
    assert "Schreibpfade" in source
    assert "Ausfuehrung" in source
    assert "selection-summary-panel" in styles
    assert "selection-summary-grid" in styles
    assert "selection-summary-row" in styles
    assert "startRun" not in source
    assert "startScenario" not in source
    assert 'type="file"' not in source
