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
    assert "runControlQueue" in source
    assert "selectedQueueId" in source
    assert "setSelectedQueueId(entry.queue_id)" in source
    assert "filteredQueueEntries.map" in source
    assert "queueActionLabel" in source
    assert "Preflight lokal" in source
    assert "Freigabe abwarten" in source
    assert "Blocker klaeren" in source
    assert "Status pruefen" in source
    assert "run-control-panel" in styles
    assert "run-control-filterbar" in styles
    assert "run-control-filter-count" in styles
    assert "run-control-table" in styles
    assert "run-control-detail-grid" in styles
    assert "run-control-issues" in styles
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
