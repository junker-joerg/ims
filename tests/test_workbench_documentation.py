from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
README = REPO_ROOT / "README.md"
WORKBENCH_DOC = REPO_ROOT / "docs" / "migration" / "workbench_shell.md"
RUN_CONTROL_PLAN = REPO_ROOT / "docs" / "migration" / "workbench_run_control_plan.md"
PACKAGING_PLAN = REPO_ROOT / "docs" / "migration" / "workbench_packaging_plan.md"
DEMO_CHECKLIST = REPO_ROOT / "docs" / "migration" / "workbench_demo_checklist.md"
LEGACY_BACKLOG = REPO_ROOT / "docs" / "plans" / "legacy_file_family_validation_backlog.md"
CHECK_SCRIPT = REPO_ROOT / "scripts" / "workbench" / "check-workbench.cmd"
START_SCRIPT = REPO_ROOT / "scripts" / "workbench" / "start-workbench.cmd"
SCRIPT_README = REPO_ROOT / "scripts" / "workbench" / "README.md"


def test_readme_documents_local_workbench_start_commands():
    readme = README.read_text(encoding="utf-8")

    assert "python -m ims.api.workbench_diagnostics --frontend-dist frontend/dist" in readme
    assert "python -m ims.api.workbench_start_plan --config .\\workbench.local.json" in readme
    assert "python -m ims.api.workbench_readiness --frontend-dist frontend/dist" in readme
    assert "python -m ims.api.workbench_portable_readiness --root . --layout repo" in readme
    assert "erwartete Dateien und Ordner den richtigen Pfadtyp haben" in readme
    assert "python -m ims.api.workbench_build_snapshot --root . --frontend-dist frontend/dist" in readme
    assert "python -m ims.api.workbench_artifact_manifest --root . --frontend-dist frontend/dist" in readme
    assert "SHA-256-Pruefsummen" in readme
    assert "python -m ims.api.workbench_bundle_plan --root . --frontend-dist frontend/dist" in readme
    assert "ohne Dateien zu kopieren oder ein Archiv zu erzeugen" in readme
    assert "python -m ims.api.workbench_bundle_build --root . --frontend-dist frontend/dist --out .\\dist\\ims-workbench-local.zip" in readme
    assert "New-Item -ItemType Directory .\\dist -Force" in readme
    assert "fehlende Output-Parents nicht automatisch" in readme
    assert "Lokaler Release-Ablauf fuer ein ZIP-Artefakt" in readme
    assert "python -m ims.api.workbench_bundle_smoke --zip-path .\\dist\\ims-workbench-local.zip" in readme
    assert "python -m ims.api.workbench_portable_staging --zip-path .\\dist\\ims-workbench-local.zip --out .\\ims-workbench" in readme
    assert "python -m ims.api.workbench_portable_staging_smoke --root .\\ims-workbench" in readme
    assert "python -m ims.api.workbench_portable_readiness --root .\\ims-workbench --layout portable" in readme
    assert "tatsaechlich erzeugten ZIP-Inhalt" in readme
    assert "explizit gestagte portable Zielstruktur" in readme
    assert "fehlenden oder leeren Zielordner" in readme
    assert "ueberschreibt keine lokalen Nutzerdaten" in readme
    assert "Staging-Smoke prueft danach die gestagte Backend-/Frontend-Struktur" in readme
    assert "Backend-Importfaehigkeit" in readme
    assert "aus dem gestagten Workbench-Root" in readme
    assert "lokaler Bereitstellungscheck" in readme
    assert "kein Installer, kein Release-Tag und kein fachlicher Gleichheitsnachweis" in readme
    assert "nicht unter eingeschlossenen Quellbaeumen wie `python_port` oder `frontend/dist`" in readme
    assert "`zip_sha256`-Pruefsumme bei identischem Inhalt reproduzierbar" in readme
    assert "python -m ims.api.workbench_cli_overview" in readme
    assert "Kurzstart fuer die lokale Browser-Workbench" in readme
    assert "Start und Diagnose" in readme
    assert "Vertraege und Run-Control-Grenzen" in readme
    assert "Metadaten-CLI" in readme
    assert "python -m ims.api.metadata_write_contracts" in readme
    assert "python -m ims.api.metadata_write_contracts check .\\metadata_import.json" in readme
    assert "python -m ims.api.run_control_contracts" in readme
    assert "python -m ims.api.run_control_dry_run_contract" in readme
    assert "python -m ims.api.core_validation_carryover_probe_contract" in readme
    assert "python -m ims.api.controlled_execution_adapter_contract" in readme
    assert "python -m ims.api.controlled_execution_adapter --fixture" in readme
    assert "python -m ims.api.run_control_adapter_result_contract" in readme
    assert "python -m ims.api.run_control_adapter_result_contract check" in readme
    assert "python -m ims.api.run_control_adapter_result_api_contract" in readme
    assert "python -m ims.api.run_control_adapter_start_contract" in readme
    assert "python -m ims.api.run_control_execution_result_store persist" in readme
    assert "GET /api/run-control/dry-run-contract" in readme
    assert "GET /api/core-validation/carryover-probe-contract" in readme
    assert "GET /api/run-control/adapter-result-contract" in readme
    assert "GET /api/run-control/adapter-start-contract" in readme
    assert "POST /api/run-control/dry-run" in readme
    assert "POST /api/run-control/queue" in readme
    assert "GET /api/run-control/queue/action-plan" in readme
    assert "GET /api/run-control/core-diagnostics-bridge" in readme
    assert "Run-Control-Kernblick-Bruecke" in readme
    assert "Lokaler Demo-Smoke fuer die Browser-Workbench" in readme
    assert "Dry-Run pruefen -> Queue vormerken -> Run-Control-Aktionsplan ansehen" in readme
    assert "baseline-python-tests" in readme
    assert "agrsich-reference-window" in readme
    assert "Browser-/Screenshot-Smoke nutzt stabile UI-Anker" in readme
    assert "run-control-core-bridge" in readme
    assert "carryover-probe-contract" in readme
    assert "api_starts_probe=false" in readme
    assert "api_starts_adapter = false" in readme
    assert "kein Ausfuehrungsadapter, keine Fachvalidierung" in readme
    assert "python -m ims.api.run_control_requests check .\\run_control_request.json" in readme
    assert "python -m ims.api.run_control_queue enqueue .\\run_control_request.json --db .\\.ims_workbench\\metadata.sqlite" in readme
    assert "python -m ims.api.run_control_queue_diagnostics --db .\\.ims_workbench\\metadata.sqlite" in readme
    assert "python -m ims.api.run_control_queue_action_plan --db .\\.ims_workbench\\metadata.sqlite" in readme
    assert "run_preflight`, `await_execution_release`, `resolve_blockers` oder `inspect_queue_status`" in readme
    assert "Statuswerte, Szenario-Referenzen und Ausfuehrungsflags" in readme
    assert "Queue-only-Datenbank" in readme
    assert "fehlende Szenario-/Run-Metadatentabellen werden als Warnung gemeldet" in readme
    assert "Rollback-Journal-Datenbanken bleiben normale `mode=ro`-Reads" in readme
    assert "`immutable=1` wird nur fuer sidecar-freie WAL-Dateien genutzt" in readme
    assert "python -m ims.api.run_control_preflight --run-id baseline-python-tests" in readme
    assert "python -m ims.api.metadata_import_cli export" in readme
    assert "python -m ims.api.metadata_import_cli export --db .\\.ims_workbench\\metadata.sqlite --out .\\metadata_export.json" in readme
    assert "python -m ims.api.metadata_import_cli roundtrip" in readme
    assert "python -m ims.api.metadata_import_cli roundtrip --db .\\.ims_workbench\\metadata.sqlite" in readme
    assert "python -m ims.api.metadata_import_cli dry-run .\\metadata_import.json" in readme
    assert "python -m ims.api.metadata_import_cli dry-run .\\metadata_import.json --db .\\.ims_workbench\\metadata.sqlite" in readme
    assert "python -m ims.api.metadata_import_cli import .\\metadata_import.json --db .\\.ims_workbench\\metadata.sqlite" in readme
    assert "Backup und Restore lokaler Workbench-Metadaten" in readme
    assert ".ims_workbench\\metadata.sqlite" in readme
    assert "WAL-/SHM-Dateien" in readme
    assert "keine automatische Backup-Funktion, keine SQLite-Migration und keine Simulation" in readme
    assert "Update und Rollback lokaler Workbench-Versionen" in readme
    assert "neben der bisherigen Version in einen eigenen Ordner" in readme
    assert "explizitem neuem Anwendungspfad und explizitem bestehendem Metadatenpfad" in readme
    assert "workbench_readiness --db <alter-metadata-pfad>" in readme
    assert "PYTHONPATH` auf den neuen `python_port`-Pfad" in readme
    assert "explizite Installation aus dem neuen Checkout" in readme
    assert "workbench_portable_readiness" in readme
    assert "keinen automatischen Updater, keine In-place-Aktualisierung" in readme
    assert "python -m uvicorn ims.api.app:app --app-dir python_port --host 127.0.0.1 --port 8000" in readme
    assert "npm.cmd run build" in readme
    assert "Lokaler Workbench-v1 Abschlussstatus" in readme
    assert "Die lokale Workbench-v1 ist als Modernisierungs-Meilenstein abgeschlossen" in readme
    assert "kein Release-Tag, keine Fachvalidierung" in readme
    assert "expliziten Importbericht und Run-Control-Preflight" in readme
    assert "keine HTTP-/UI-Schreibpfade" in readme
    assert "docs/migration/workbench_run_control_plan.md" in readme
    assert "docs/plans/run_control_adapter_result_plan.md" in readme
    assert "docs/plans/run_control_adapter_result_view_plan.md" in readme
    assert "docs/migration/run_control_adapter_result_api_contract.md" in readme
    assert "docs/migration/run_control_adapter_start_contract.md" in readme
    assert "docs/migration/run_control_execution_result_store.md" in readme
    assert "docs/migration/workbench_packaging_plan.md" in readme
    assert "als lokaler ZIP-/Staging-Abschlussstatus konsolidiert" in readme
    assert "docs/migration/workbench_demo_checklist.md" in readme
    assert "Startbefehle, UI-Reihenfolge, erwartete Demo-Signale" in readme
    assert "scripts\\workbench\\check-workbench.cmd" in readme
    assert "scripts\\workbench\\start-workbench.cmd" in readme


def test_workbench_doc_groups_local_cli_boundaries():
    doc = WORKBENCH_DOC.read_text(encoding="utf-8")

    assert "## Lokale CLI-Grenzen" in doc
    assert "## Lokale Konfiguration" in doc
    assert "## Lokale Workbench-v1 Ablauf" in doc
    assert "## Lokaler Workbench-v1 Abschlussstatus" in doc
    assert "python -m ims.api.workbench_diagnostics --frontend-dist frontend/dist" in doc
    assert "python -m ims.api.workbench_diagnostics --config .\\workbench.local.json" in doc
    assert "python -m ims.api.workbench_start_plan --config .\\workbench.local.json" in doc
    assert "python -m ims.api.workbench_readiness --frontend-dist frontend/dist" in doc
    assert "python -m ims.api.workbench_portable_readiness --root . --layout repo" in doc
    assert "python -m ims.api.workbench_portable_readiness --root .\\ims-workbench --layout portable" in doc
    assert "python -m ims.api.workbench_build_snapshot --root . --frontend-dist frontend/dist" in doc
    assert "python -m ims.api.workbench_artifact_manifest --root . --frontend-dist frontend/dist" in doc
    assert "python -m ims.api.workbench_bundle_plan --root . --frontend-dist frontend/dist" in doc
    assert "python -m ims.api.workbench_bundle_build --root . --frontend-dist frontend/dist --out .\\dist\\ims-workbench-local.zip" in doc
    assert "New-Item -ItemType Directory .\\dist -Force" in doc
    assert "python -m ims.api.workbench_bundle_smoke --zip-path .\\dist\\ims-workbench-local.zip" in doc
    assert "python -m ims.api.workbench_portable_staging --zip-path .\\dist\\ims-workbench-local.zip --out .\\ims-workbench" in doc
    assert "python -m ims.api.workbench_portable_staging_smoke --root .\\ims-workbench" in doc
    assert "python -m ims.api.workbench_cli_overview" in doc
    assert "python -m ims.api.metadata_write_contracts" in doc
    assert "python -m ims.api.metadata_write_contracts check .\\metadata_import.json" in doc
    assert "python -m ims.api.run_control_contracts" in doc
    assert "python -m ims.api.run_control_dry_run_contract" in doc
    assert "python -m ims.api.core_validation_carryover_probe_contract" in doc
    assert "python -m ims.api.controlled_execution_adapter_contract" in doc
    assert "python -m ims.api.controlled_execution_adapter --fixture" in doc
    assert "python -m ims.api.run_control_adapter_result_contract" in doc
    assert "python -m ims.api.run_control_adapter_result_contract check" in doc
    assert "python -m ims.api.run_control_adapter_result_api_contract" in doc
    assert "python -m ims.api.run_control_adapter_start_contract" in doc
    assert "python -m ims.api.run_control_execution_result_store persist" in doc
    assert "GET /api/run-control/dry-run-contract" in doc
    assert "GET /api/core-validation/carryover-probe-contract" in doc
    assert "GET /api/run-control/adapter-result-contract" in doc
    assert "GET /api/run-control/adapter-start-contract" in doc
    assert "POST /api/run-control/dry-run" in doc
    assert "POST /api/run-control/queue" in doc
    assert "GET /api/run-control/queue/action-plan" in doc
    assert "GET /api/core-validation/overview" in doc
    assert "GET /api/run-control/core-diagnostics-bridge" in doc
    assert "Run-Control-Kernblick-Bruecke" in doc
    assert "Kernvalidierungsueberblick" in doc
    assert "Carryover-Probe-Vertrag" in doc
    assert "ohne Probe-Upload, Probe-Start oder Ausfuehrungsadapter" in doc
    assert "Execution-Summary-Vertrag" in doc
    assert "keinen expliziten Periodenrunner" in doc
    assert "python -m ims.api.run_control_requests check .\\run_control_request.json" in doc
    assert "python -m ims.api.run_control_queue enqueue .\\run_control_request.json --db .\\.ims_workbench\\metadata.sqlite" in doc
    assert "python -m ims.api.run_control_queue_diagnostics --db .\\.ims_workbench\\metadata.sqlite" in doc
    assert "python -m ims.api.run_control_queue_action_plan --db .\\.ims_workbench\\metadata.sqlite" in doc
    assert "fehlende Szenario-Referenzen" in doc
    assert "python -m ims.api.run_control_preflight --run-id baseline-python-tests" in doc
    assert "python -m ims.api.metadata_import_cli check .\\metadata_import.json" in doc
    assert "python -m ims.api.metadata_import_cli preview .\\metadata_import.json" in doc
    assert "python -m ims.api.metadata_import_cli snapshot --db .\\.ims_workbench\\metadata.sqlite" in doc
    assert "python -m ims.api.metadata_import_cli export --db .\\.ims_workbench\\metadata.sqlite --out .\\metadata_export.json" in doc
    assert "python -m ims.api.metadata_import_cli roundtrip --db .\\.ims_workbench\\metadata.sqlite" in doc
    assert "python -m ims.api.metadata_import_cli dry-run .\\metadata_import.json --db .\\.ims_workbench\\metadata.sqlite" in doc
    assert "python -m ims.api.metadata_import_cli import .\\metadata_import.json --db .\\.ims_workbench\\metadata.sqlite" in doc
    assert "Start und Diagnose:" in doc
    assert "Vertraege und Grenzen:" in doc
    assert "Metadaten:" in doc


def test_workbench_doc_keeps_modernization_boundaries_conservative():
    doc = WORKBENCH_DOC.read_text(encoding="utf-8")

    assert "uvicorn" in doc
    assert "Rollback-Journal-Datenbanken werden dabei als normale `mode=ro`-Quelle gelesen" in doc
    assert "`immutable=1` bleibt auf sidecar-freie WAL-Dateien beschraenkt" in doc
    assert "Rollback-Journal-Dateien bleiben `mode=ro`, sidecar-freie WAL-Dateien nutzen `immutable=1`" in doc
    assert "Vollgleichheit" in doc
    assert "Keines dieser Kommandos startet eine Simulation" in doc
    assert "keine Konfigurationsdatei automatisch" in doc
    assert "relativ zum Speicherort der Konfigurationsdatei" in doc
    assert "Der Startplan startet keinen Server" in doc
    assert "## v1-Bereitschaftspruefung" in doc
    assert "Die Readiness-Pruefung startet keinen Server" in doc
    assert "Run-Control-Queue-Diagnose als eigenen Bereitschaftsbereich" in doc
    assert "run_control_queue_ready = false" in doc
    assert "Die lokale portable Strukturpruefung ist rein beschreibend" in doc
    assert "Der Check erzeugt keine fehlenden Ordner" in doc
    assert "erwarteten und tatsaechlichen Pfadtyp" in doc
    assert "Der lokale Build-Snapshot ist rein beschreibend" in doc
    assert "Der Build-Snapshot baut kein Frontend" in doc
    assert "Das lokale Artefaktmanifest ist rein beschreibend" in doc
    assert "Ausgeschlossen bleiben lokale Daten und Caches" in doc
    assert "deterministisch nach relativen Pfaden sortiert" in doc
    assert "SHA-256-Pruefsumme" in doc
    assert "Der lokale Bundle-Trockenlauf ist rein beschreibend" in doc
    assert "archive_created = false" in doc
    assert "Er ist ein pruefbarer Packaging-Zwischenschritt" in doc
    assert "## Lokaler ZIP-Build" in doc
    assert "writes_performed = true" in doc
    assert "archive_created = true" in doc
    assert "schreibt ausschliesslich den expliziten ZIP-Zielpfad" in doc
    assert "fehlende" in doc
    assert "Output-Parent-Verzeichnisse lehnt der ZIP-Build ab" in doc
    assert "Ausgabe unter eingeschlossenen Quellbaeumen wie `python_port` oder `frontend/dist`" in doc
    assert "ZIP-Eintraege nutzen stabile Zeitstempel und Dateirechte" in doc
    assert "`zip_sha256` fuer identische Inhalte reproduzierbar bleibt" in doc
    assert "automatisierter ZIP-Smoke prueft fuer erzeugte lokale Bundles" in doc
    assert "Dieser Smoke startet keine Simulation" in doc
    assert "## Lokale Release-Bereitstellung" in doc
    assert "Der lokale Release-Ablauf fuer ein ZIP-Artefakt" in doc
    assert "prueft den tatsaechlich erzeugten ZIP-Inhalt" in doc
    assert "explizit in eine portable Zielstruktur unter `.\\ims-workbench`" in doc
    assert "fehlenden oder leeren Zielordner" in doc
    assert "ueberschreibt keine lokalen" in doc
    assert "erst nach" in doc
    assert "diesem Staging-Schritt" in doc
    assert "Staging-Smoke liest die gestagte portable Zielstruktur" in doc
    assert "Backend-Module" in doc
    assert "Importfaehigkeit aus dem gestagten Workbench-Root ueber `app\\python_port`" in doc
    assert "app\\frontend\\dist" in doc
    assert "writes_enabled = false" in doc
    assert "execution_enabled = false" in doc
    assert "Die Uebersicht fuehrt diese Befehle nicht aus" in doc
    assert "Die Szenariofilter arbeiten nur auf bereits gelesenen Metadaten" in doc
    assert "Die Runfilter arbeiten nur auf bereits gelesenen Metadaten" in doc
    assert "Die Auswahlzusammenfassung ist rein lesend" in doc
    assert "zur aktuellen Auswahl passende Detaildaten" in doc
    assert "Der lokale Schreibvertrag ist rein beschreibend" in doc
    assert "Diese Schreibvertragspruefung schreibt nicht" in doc
    assert "Der Export startet keine Simulation" in doc
    assert "gleiche aufgeloeste `--db`- und `--out`-Pfade" in doc
    assert "Hardlink- oder Datei-Alias" in doc
    assert "dieselbe Dateiidentitaet" in doc
    assert "Der Roundtrip schreibt keine Exportdatei" in doc
    assert "Der Dry-Run schreibt keine Metadaten" in doc
    assert "Importbericht" in doc
    assert "writes_performed = true" in doc
    assert "execution_performed = false" in doc
    assert "## Run-Steuerungsgrenze" in doc
    assert "Der Run-Control-Vertrag ist rein beschreibend" in doc
    assert "Der Run-Control-Dry-Run-Vertrag erlaubt nur den kontrollierten HTTP-Pruefpfad" in doc
    assert 'mode = "run_control_dry_run_contract"' in doc
    assert 'mode = "controlled_execution_adapter_contract"' in doc
    assert 'mode = "controlled_execution_adapter"' in doc
    assert 'mode = "run_control_adapter_result_contract"' in doc
    assert 'mode = "run_control_adapter_result_validation"' in doc
    assert 'mode = "run_control_adapter_result_api_contract"' in doc
    assert 'mode = "run_control_adapter_start_contract"' in doc
    assert 'mode = "run_control_execution_result_store_persist"' in doc
    assert "runner_start_enabled = false" in doc
    assert "--explicit-execution-release" in doc
    assert "keinen freien `--output-dir`" in doc
    assert "read-only Adapter-Resultat" in doc
    assert "bereits lokal erzeugtes" in doc
    assert "keinen Adapterstart aus Run-Control" in doc
    assert "akzeptiert keinen Browser-Upload" in doc
    assert "run_control_adapter_result_view_plan.md" in doc
    assert "read-only API-/UI-Anzeige" in doc
    assert "Dateiauswahl, Startbutton und Adapterstart gesperrt" in doc
    assert "api_accepts_result_payload = false" in doc
    assert "api_validates_result_payload = false" in doc
    assert "api_starts_adapter = false" in doc
    assert "Request-DTO enthaelt `run_id`, `scenario_id`, optional `metadata_db`, `requested_by`, `created_at`" in doc
    assert "Die Queue speichert `queue_id`, Request-Daten, Status und Ausfuehrungsgrenzen" in doc
    assert "`planned`, `blocked`, `validated` und `result_persisted`" in doc
    assert 'mode = "run_control_queue_action_plan"' in doc
    assert "`run_preflight`, `await_execution_release`, `resolve_blockers`, `inspect_persisted_result` oder `inspect_queue_status`" in doc
    assert "Der lokale Ergebnisstore schreibt nur mit `--explicit-persistence-release`" in doc
    assert "Queue-only-Datenbank bleibt als Queue lesbar" in doc
    assert "fehlende Szenario-/Run-Metadatentabellen werden als Diagnosewarnung und Aktionsplan-Blocker gemeldet" in doc
    assert "Kein Queue-Befehl startet eine Simulation" in doc
    assert "GET /api/run-control/queue" in doc
    assert "POST /api/run-control/queue" in doc
    assert "GET /api/run-control/queue/action-plan" in doc
    assert "Der lokale Demo-Smoke fuer die Browser-Workbench" in doc
    assert "Dry-Run pruefen -> Queue vormerken -> Run-Control-Aktionsplan ansehen" in doc
    assert "Run-Control-Kernblick-Bruecke lesen" in doc
    assert "Adapter-Resultat-Vertrag lesen" in doc
    assert "POST /api/run-control/dry-run`, danach `POST /api/run-control/queue`" in doc
    assert "run-control-demo-dry-run-button" in doc
    assert "run-control-demo-action-plan" in doc
    assert "run-control-core-bridge" in doc
    assert "Dieser Demo-Smoke startet keine Simulation" in doc
    assert "GET /api/run-control/queue/{queue_id}" in doc
    assert "metadata_not_found" in doc
    assert "Run-Control-Uebersicht" in doc
    assert "Queue-Schreiben ist nur ueber den getrennten Vormerkpfad" in doc
    assert "Ohne explizite SQLite-Quelle bleibt der Endpunkt blockiert" in doc
    assert "Die Run-Control-Aktionsplankarte nutzt `/api/run-control/queue/action-plan`" in doc
    assert "Die Run-Control-Kernblick-Bruecke ist rein lesend" in doc
    assert "`/api/run-control/core-diagnostics-bridge`" in doc
    assert "enthaelt keinen Startbutton" in doc
    assert "run_preflight`, `await_execution_release`, `resolve_blockers` oder `inspect_queue_status" in doc
    assert "Der Run-Control-Preflight ist ebenfalls rein lokal und lesend" in doc
    assert "schaltet keinen UI-Startbutton frei" in doc
    assert "keine Fachvalidierung und keine historische Vollgleichheitsbehauptung" in doc
    assert "Run-Felds `execution_enabled` mit dem Wert `false`" in doc
    assert "execution_enabled=true" in doc
    assert "0 reviewbare PRs" in doc
    assert "Die lokale Bedienreihenfolge fuer v1 ist" in doc
    assert "Die lokale Workbench-v1 ist als rein lokale Browser-Workbench und Modernisierungs-Meilenstein abgeschlossen" in doc
    assert "docs/migration/workbench_demo_checklist.md" in doc
    assert "Startbefehle, UI-Reihenfolge, erwartete Demo-Signale" in doc
    assert "Nicht enthalten sind weiterhin Fachlogikaenderungen" in doc
    assert "## Backup und Restore lokaler Metadaten" in doc
    assert "metadata.sqlite-wal" in doc
    assert "metadata.sqlite-shm" in doc
    assert "python -m ims.api.metadata_import_cli export --db .\\.ims_workbench\\metadata.sqlite --out .\\metadata_export.json" in doc
    assert "python -m ims.api.metadata_import_cli snapshot --db .\\.ims_workbench\\metadata.sqlite" in doc
    assert "python -m ims.api.workbench_readiness --frontend-dist frontend/dist --db .\\.ims_workbench\\metadata.sqlite" in doc
    assert "keine automatische Backup-Funktion" in doc
    assert "keine SQLite-Migration" in doc
    assert "keine Fachlogikdaten, keine Simulationsergebnisse" in doc
    assert "## Update und Rollback lokaler Workbench-Versionen" in doc
    assert "neben der bisherigen Version in einen eigenen Ordner" in doc
    assert '$oldRoot = "C:\\ims-workbench-old"' in doc
    assert '$newRoot = "C:\\ims-workbench-new"' in doc
    assert '$metadataDb = Join-Path $oldRoot ".ims_workbench\\metadata.sqlite"' in doc
    assert "python -m ims.api.workbench_portable_readiness --root $newRoot --layout portable" in doc
    assert 'python -m ims.api.workbench_readiness --frontend-dist (Join-Path $newRoot "app\\frontend\\dist") --db $metadataDb' in doc
    assert "python -m ims.api.metadata_import_cli roundtrip --db $metadataDb" in doc
    assert "im Kontext der neuen portablen Workbench-Version" in doc
    assert "Push-Location $newRoot" in doc
    assert '$env:PYTHONPATH = Join-Path $newRoot "python_port"' in doc
    assert "python -m ims.api.workbench_portable_readiness --root . --layout repo" in doc
    assert "python -m ims.api.workbench_readiness --frontend-dist frontend/dist --db $metadataDb" in doc
    assert "Pop-Location" in doc
    assert "`Push-Location` allein setzt den Python-Modulkontext nicht" in doc
    assert "keinen alten editable install" in doc
    assert "gegen die bestehende Metadatenquelle geprueft" in doc
    assert "keine frische `.ims_workbench` als Ersatz" in doc
    assert "Rollback heisst" in doc
    assert "keinen automatischen Updater" in doc
    assert "keine In-place-Aktualisierung" in doc
    assert "## Spaetere Bloecke" in doc
    assert "kontrollierte echte Run-Steuerung" in doc
    assert "eigene reviewbare Plaene und PRs" in doc
    assert "docs/migration/workbench_packaging_plan.md" in doc
    assert "Packaging- und Bereitstellungsblock ist separat" in doc
    assert "ZIP-/Staging-Grenzen" in doc
    assert "scripts\\workbench\\check-workbench.cmd" in doc
    assert "scripts\\workbench\\start-workbench.cmd" in doc


def test_workbench_run_control_plan_documents_next_modernization_block():
    plan = RUN_CONTROL_PLAN.read_text(encoding="utf-8")

    assert RUN_CONTROL_PLAN.is_file()
    assert "Workbench Run-Control Plan nach v1" in plan
    assert "14-28+" in plan
    assert "Packaging und Bereitstellung | ca. `0` geplante PRs" in plan
    assert "Vorhandene lokale Run-Control-Bausteine" in plan
    assert "Run-Control-Vertrag" in plan
    assert "Run-Control-Dry-Run-Vertrag" in plan
    assert "Run-Control-Request-Check" in plan
    assert "Run-Control-Queue" in plan
    assert "Run-Control-Queue-Aktionsplan" in plan
    assert "python -m ims.api.run_control_queue_action_plan --db .\\.ims_workbench\\metadata.sqlite" in plan
    assert "writes_performed = false" in plan
    assert "Run-Control-Preflight" in plan
    assert "Packaging und Bereitstellung" in plan
    assert "Fachvalidierung und historische Vollgleichheit" in plan
    assert "Phase 1: Rein lokale Run-Control-Requests" in plan
    assert "Phase 6: Haertung, Doku, Smoke-/E2E-Pruefung" in plan
    assert "PR 1: Run-Control-Dashboard/lesende Queue-Anzeige im Frontend" in plan
    assert "PR 2: API-Leseendpunkte fuer Queue/Requests, noch ohne Schreibpfad" in plan
    assert "PR 3: Kontrollierter HTTP-Dry-Run als Pruefpfad" in plan
    assert "Erledigt" in plan
    assert "PR 4: Kontrollierte lokale Queue-Schreibpfade ueber API nur nach erfolgreichem Dry-Run" in plan
    assert "PR 5: Run-Control-Aktionsplan per API/UI sichtbar machen" in plan
    assert "PR 6: Lokaler Demo-Smoke fuer Dry-Run, Queue-Vormerkung und Aktionsplan" in plan
    assert "PR 7: Lokale Demo-Checkliste mit Startbefehlen, UI-Reihenfolge und Grenzen ohne Simulation" in plan
    assert "PR 8: Read-only Run-Control-Brueckenplan zu Kernlauf-Diagnosen" in plan
    assert "docs/plans/run_control_execution_release_plan.md" in plan
    assert "PR 9: Ausfuehrungsfreigabeplan fuer Run-Control dokumentieren" in plan
    assert "PR 10: API-Startvertrag fuer den kontrollierten Adapter hart gegated" in plan
    assert "python_port/ims/api/run_control_adapter_start_contract.py" in plan
    assert "GET /api/run-control/adapter-start-contract" in plan
    assert "PR 11: Queue-/Status-/Resultat-Persistenz" in plan
    assert "python_port/ims/api/run_control_execution_result_store.py" in plan
    assert "result_persisted" in plan
    assert "PR 12+: UI-Flow, Ergebnisanzeige" in plan
    assert "keinen Worker, Scheduler oder Simulationslauf starten" in plan
    assert "docs/plans/run_control_core_diagnostics_bridge_plan.md" in plan
    assert 'mode = "run_control_core_diagnostics_bridge"' in plan
    assert "Run-Control-Kernblick-Bruecke" in plan
    assert "GET /api/core-validation/overview" in plan
    assert "GET /api/run-control/core-diagnostics-bridge" in plan
    assert "inspect_core_validation_overview" in plan
    assert "await_precomputed_execution_summary" in plan
    assert "resolve_core_validation_blockers" in plan
    assert "Rollback-Journal-Datenbanken werden mit `mode=ro` gelesen" in plan
    assert "`immutable=1` ist nur fuer sidecar-freie WAL-Dateien zulaessig" in plan
    assert "Haertung, Doku, Smoke-/E2E-Checks" in plan
    assert "Review-Fixes, CI- und Windows-Pfadhaertung" in plan
    assert "execution_enabled=false" in plan
    assert "`execution_enabled` bleibt bis zur expliziten Ausfuehrungsfreigabe `false`" in plan
    assert "Die Ausfuehrungsfreigabe ist in PR 43 nur geplant" in plan
    assert "kein API-Pfad setzt" in plan
    assert "Keine Fachlogikaenderung" in plan
    assert "Keine Simulation starten" in plan
    assert "Keine weiteren HTTP-Schreibendpunkte ausser der kontrollierten Queue-Vormerkung" in plan
    assert "Kein HTTP-Schreibpfad ausser Queue-Metadaten nach erfolgreichem Dry-Run" in plan
    assert "Demo-Smoke: Browser-Ablauf Dry-Run pruefen, Queue vormerken, Run-Control-Aktionsplan ansehen und Run-Control-Kernblick-Bruecke lesen" in plan
    assert "Kein Packaging in diesem PR" in plan
    assert "Keine historische Vollgleichheitsbehauptung" in plan


def test_workbench_demo_checklist_documents_local_demo_scope():
    checklist = DEMO_CHECKLIST.read_text(encoding="utf-8")

    assert DEMO_CHECKLIST.is_file()
    assert "Lokale Workbench-Demo-Checkliste" in checklist
    assert "kein Release-Tag, keine Fachvalidierung, keine Simulation" in checklist
    assert "baseline-python-tests" in checklist
    assert "agrsich-reference-window" in checklist
    assert "Dry-Run pruefen" in checklist
    assert "Queue vormerken" in checklist
    assert "Naechste Aktion = run_preflight" in checklist
    assert "execution_enabled" in checklist
    assert "execution_performed" in checklist
    assert "Was demo-faehig ist" in checklist
    assert "Optionaler lesender Kernblick" in checklist
    assert "python -m ims.engine.explicit_period_diagnostics tests/fixtures/replay_vu14_period_plan.json" in checklist
    assert "python -m ims.engine.explicit_period_diagnostics_bundle tests/fixtures/replay_vu14_period_plan.json tests/fixtures/replay_vusk1_period_plan.json" in checklist
    assert "python -m ims.engine.core_validation_overview --legacy-fixture tests/fixtures/legacy_validation_bundle.json" in checklist
    assert "2 Planfixtures, 8 Perioden" in checklist
    assert "19 Referenzen, 6300 abgedeckte Zeilen" in checklist
    assert "execution_summary_next_action = await_precomputed_execution_summary" in checklist
    assert "overview_starts_runner = false" in checklist
    assert "Kernvalidierungsueberblick" in checklist
    assert "Carryover-Probe-Vertrag" in checklist
    assert "Adapter-Resultat-Vertrag" in checklist
    assert "Probe-Payload annehmen" in checklist
    assert "keinen Probe starten" in checklist
    assert "keinen Ausfuehrungsadapter" in checklist
    assert "Run-Control-Kernblick-Bruecke" in checklist
    assert "GET /api/run-control/core-diagnostics-bridge" in checklist
    assert "Run-Control-Aktionsplan" in checklist
    assert "gemeinsame Lesesicht" in checklist
    assert "Brueckenaktion = resolve_core_validation_blockers" in checklist
    assert "Summary-Schritt `await_precomputed_execution_summary`" in checklist
    assert "api_starts_probe = false" in checklist
    assert "api_accepts_probe_payload = false" in checklist
    assert "ui_enabled = false" in checklist
    assert "simulation_performed = false" in checklist
    assert "api_starts_adapter = false" in checklist
    assert "api_accepts_result_payload = false" in checklist
    assert "api_validates_result_payload = false" in checklist
    assert "docs/plans/run_control_core_diagnostics_bridge_plan.md" in checklist
    assert "schaltet keinen Startpfad frei" in checklist
    assert "lesender Carryover-Probe-Vertrag fuer vorab berechnete Probe-Payloads" in checklist
    assert "lesender Adapter-Resultat-Vertrag fuer vorab lokal gepruefte Adapter-Resultate" in checklist
    assert "lesende Run-Control-Kernblick-Bruecke ohne Startpfad" in checklist
    assert "run-control-core-bridge" in checklist
    assert "carryover-probe-contract" in checklist
    assert "adapter-result-contract" in checklist
    assert "Was noch nicht demo-faehig ist" in checklist
    assert "echte Simulation oder Periodenrunner-Ausfuehrung" in checklist
    assert "vorab berechnete Execution-Summary als UI-Eingabe" in checklist
    assert "Ausfuehrungsadapter hinter `run_preflight`" in checklist
    assert "fachlicher Gleichheitsnachweis" in checklist
    assert "gesperrte Carryover-Probe-Vertragskarte" in checklist
    assert "gesperrte Adapter-Resultat-Vertragskarte" in checklist
    assert "python -m pytest -q tests/test_workbench_demo_smoke.py tests/test_frontend_shell.py tests/test_workbench_documentation.py" in checklist
    assert "npm.cmd run build --prefix .\\frontend" in checklist


def test_legacy_file_family_backlog_updates_remaining_pr_plan():
    backlog = LEGACY_BACKLOG.read_text(encoding="utf-8")

    assert LEGACY_BACKLOG.is_file()
    assert "Keine Uebernahme von `VU014PR1.DAT`" in backlog
    assert "schmalen fachlichen VU-/VN-Regel- oder Carryover-Slice" in backlog
    assert "Periodenuebergangs-/Carryover-Grenze" in backlog
    assert "PR 12: Read-only Brueckenplan" in backlog
    assert "ohne neuen Endpunkt, Schreibpfad oder Runner-Start (erledigt)" in backlog
    assert "PR 13: Optional eine rein lesende API-Anbindung" in backlog
    assert "(erledigt)" in backlog
    assert "PR 14: Optional eine rein lesende UI-Karte" in backlog
    assert "PR 15: Bruecken-Demo-/Screenshot-Smoke" in backlog
    assert "visueller Beleg fuer die neue Karte gebraucht wird (erledigt)" in backlog
    assert "PR 16: Naechsten schmalen fachlichen VU-/VN-Regel- oder Carryover-Slice" in backlog
    assert "docs/plans/explicit_period_transition_slice.md" in backlog
    assert "Periodenuebergangs-/Carryover-Grenze fuer `VU14L1.DAT` und `VUSK1L4.DAT`" in backlog
    assert "noch ohne neue Fachlogik" in backlog
    assert "PR 17: Explizite Periodenuebergangs-/Carryover-Diagnose" in backlog
    assert "historische Regelwahl (erledigt)" in backlog
    assert "PR 18: Kleines VN-Policyholder- oder Carryover-Anschlussfixture planen" in backlog
    assert "replay_vn_policyholder_transition_plan.json" in backlog
    assert "explicit_period_transition_no_policyholders" in backlog
    assert "PR 19: Engen Carryover-Code-Slice" in backlog
    assert "Carryover-Kandidatenlisten in der" in backlog
    assert "keine Carryover-Ausfuehrung" in backlog
    assert "PR 20: Echten Carryover-Code-Slice separat planen" in backlog
    assert "docs/plans/explicit_transition_carryover_code_slice.md" in backlog
    assert "PR 21: Den geplanten engen Carryover-Probe als Code-/Test-Schritt umsetzen" in backlog
    assert "ims.engine.explicit_transition_carryover_probe" in backlog
    assert "(dieser Schnitt:" in backlog
    assert "erledigt" in backlog
    assert "Aktuelle PR-Zaehlung" in backlog
    assert "0 PRs bis zur demo-nahen read-only Carryover/Kern-Sicht" in backlog
    assert "3+" in backlog
    assert "Der erste echte fachliche Regressionstest ist nach PR 28 ausgefuehrt und" in backlog
    assert "Bis zur geschaerften Einordnung dieses ersten fachlichen Regressionstests" in backlog
    assert "bleiben nach PR 28 noch 0 PRs" in backlog
    assert "PR 22: Carryover-Probe im Kernvalidierungsueberblick" in backlog
    assert "explicit_transition_carryover_probe_contract" in backlog
    assert "PR 23: Read-only API-Vertrag" in backlog
    assert "GET /api/core-validation/carryover-probe-contract" in backlog
    assert "PR 24: UI-Karte" in backlog
    assert "`Carryover-Probe-Vertrag` in der Workbench" in backlog
    assert "PR 25: Demo-/Doku-Smoke" in backlog
    assert "`carryover-probe-contract` im Demo-Smoke" in backlog
    assert "PR 26: Ersten fachlichen VN-Carryover-Slice-Test planen" in backlog
    assert "docs/plans/first_fachlicher_slice_test_plan.md" in backlog
    assert "PR 27: Den geplanten VN-Carryover-Slice als fachlichen Regressionstest" in backlog
    assert "tests/test_first_fachlicher_vn_carryover_regression.py" in backlog
    assert "erledigt" in backlog
    assert "PR 28: Assertions und Dokumentation fuer den ersten fachlichen" in backlog
    assert "docs/migration/first_fachlicher_regressionstest.md" in backlog
    assert "PR 29: Zweiten schmalen fachlichen Slice" in backlog
    assert "second_fachlicher_slice_test_plan.md" in backlog
    assert "VN-Regelwirkung ueber explizite `best_info`-Snapshots" in backlog
    assert "Policyholder `21`" in backlog
    assert "Versicherer `11/12` und Periode `5`" in backlog
    assert "keine API-/UI-/Run-Control-Anbindung" in backlog
    assert "PR 30: Geplanten VN-Regel-Snapshot-Slice" in backlog
    assert "tests/test_second_fachlicher_vn_rule_snapshot_regression.py" in backlog
    assert "docs/migration/second_fachlicher_regressionstest.md" in backlog
    assert "Bis zum zweiten ausgefuehrten fachlichen Regressionstest" in backlog
    assert "bleiben nach PR 30" in backlog
    assert "noch 0 PRs" in backlog
    assert "PR 31: Optional weiteren VN-Regel-Snapshot" in backlog
    assert "VU-Carryover-Fixture geplant" in backlog
    assert "third_fachlicher_slice_test_plan.md" in backlog
    assert "tests/test_third_fachlicher_vu_carryover_regression.py" in backlog
    assert "docs/migration/third_fachlicher_regressionstest.md" in backlog
    assert "Bis zum dritten ausgefuehrten fachlichen Regressionstest" in backlog
    assert "bleiben nach PR 32" in backlog
    assert "noch 0 PRs" in backlog
    assert "PR 32: Geplanten VU-Carryover-Fixture-Slice" in backlog
    assert "PR 33: Danach entscheiden" in backlog
    assert "Ausfuehrungsadapter-Vertrag geplant" in backlog
    assert "controlled_execution_adapter_plan.md" in backlog
    assert "Bis zu einem read-only Ausfuehrungsadapter-Vertrag" in backlog
    assert "bleiben nach PR 34 noch 0 PRs" in backlog
    assert "PR 34: Read-only Ausfuehrungsadapter-Vertrag" in backlog
    assert "tests/test_api_controlled_execution_adapter_contract.py" in backlog
    assert "docs/migration/controlled_execution_adapter_contract.md" in backlog
    assert "PR 35: Optional lokalen Adapter" in backlog
    assert "tests/test_api_controlled_execution_adapter.py" in backlog
    assert "docs/migration/controlled_execution_adapter.md" in backlog
    assert "Bis zu einem lokalen expliziten Adapter" in backlog
    assert "bleiben nach PR 35 noch 0 PRs" in backlog
    assert "PR 36: Entscheiden" in backlog
    assert "run_control_adapter_result_plan.md" in backlog
    assert "run_control_adapter_result_view_plan.md" in backlog
    assert "read-only Adapter-Resultat" in backlog
    assert "Bis zur Entscheidung fuer ein read-only Adapter-Resultat" in backlog
    assert "bleiben nach PR 36 noch" in backlog
    assert "PR 37: Read-only Adapter-Resultat-DTO" in backlog
    assert "tests/test_api_run_control_adapter_result_contract.py" in backlog
    assert "docs/migration/run_control_adapter_result_contract.md" in backlog
    assert "Bis zu einem read-only Adapter-Resultat-Vertrag" in backlog
    assert "bleiben nach PR 37 noch 0 PRs" in backlog
    assert "PR 38: Read-only API-/UI-Anzeige" in backlog
    assert "PR 39: Optional read-only API-Vertrag" in backlog
    assert "tests/test_api_run_control_adapter_result_api_contract.py" in backlog
    assert "docs/migration/run_control_adapter_result_api_contract.md" in backlog
    assert "Die gesperrte UI-Karte fuer den Adapter-Resultat-Vertrag ist nach PR 40 umgesetzt" in backlog
    assert "PR 40: Optional UI-Karte" in backlog
    assert "frontend/src/main.tsx" in backlog
    assert "tests/test_frontend_shell.py" in backlog
    assert "Der vierte fachliche VN-Slice ist nach PR 41 umgesetzt" in backlog
    assert "PR 41: `best_info`-Wirkung plus VN-State-Carryover" in backlog
    assert "tests/test_fourth_fachlicher_vn_best_info_carryover_regression.py" in backlog
    assert "docs/migration/fourth_fachlicher_regressionstest.md" in backlog
    assert "Der fuenfte fachliche VN-Slice ist nach PR 42 umgesetzt" in backlog
    assert "PR 42: `sample_search` / Vrvn05 plus Schaden-/Settlement-Runner-Grenze" in backlog
    assert "tests/test_fifth_fachlicher_vn_sample_search_regression.py" in backlog
    assert "docs/migration/fifth_fachlicher_regressionstest.md" in backlog
    assert "PR 43: Expliziten Run-Control-Ausfuehrungsfreigabeplan" in backlog
    assert "docs/plans/run_control_execution_release_plan.md" in backlog
    assert "PR 44: API-Startvertrag fuer den kontrollierten Adapter hart gegated" in backlog
    assert "tests/test_api_run_control_adapter_start_contract.py" in backlog
    assert "docs/migration/run_control_adapter_start_contract.md" in backlog
    assert "PR 45: Queue-/Status-/Resultat-Persistenz" in backlog
    assert "tests/test_api_run_control_execution_result_store.py" in backlog
    assert "docs/migration/run_control_execution_result_store.md" in backlog
    assert "PR 46: UI-Flow" in backlog
    assert "PR 48: Demo-Smoke und Doku fuer den benutzbaren Ablauf" in backlog
    assert "Zaehlschnitt nach PR 45: grob 2 bis 4 reviewbare PRs" in backlog
    assert "weiterhin ohne Vollgleichheitsbehauptung" in backlog


def test_workbench_packaging_plan_documents_portable_delivery_block():
    plan = PACKAGING_PLAN.read_text(encoding="utf-8")

    assert PACKAGING_PLAN.is_file()
    assert "Workbench Packaging- und Bereitstellungsplan" in plan
    assert "## Abschlussstatus" in plan
    assert "Packaging-/Bereitstellungsblock ist fuer die lokale Workbench-v1 abgeschlossen" in plan
    assert "Der lokale ZIP-/Staging-Ablauf ist als manuelle, pruefbare Bereitstellungsgrenze vorbereitet" in plan
    assert "portable IMS Workbench" in plan
    assert "start-workbench.cmd" in plan
    assert "check-workbench.cmd" in plan
    assert ".ims_workbench/" in plan
    assert "metadata.sqlite" in plan
    assert "ZIP- und Release-Artefakte" in plan
    assert "Backup und Restore lokaler Metadaten" in plan
    assert "metadata.sqlite-wal" in plan
    assert "metadata.sqlite-shm" in plan
    assert "snapshot --db .\\.ims_workbench\\metadata.sqlite" in plan
    assert "export --db .\\.ims_workbench\\metadata.sqlite --out .\\metadata_export.json" in plan
    assert "roundtrip --db .\\.ims_workbench\\metadata.sqlite" in plan
    assert "workbench_readiness --frontend-dist frontend/dist --db .\\.ims_workbench\\metadata.sqlite" in plan
    assert "keine automatische Backup-Funktion" in plan
    assert "keine SQLite-Migration" in plan
    assert "keine Fachlogikdaten, keine Simulationsergebnisse" in plan
    assert "Update und Rollback lokaler Workbench-Versionen" in plan
    assert "neben der bisherigen Version in einen eigenen" in plan
    assert '$oldRoot = "C:\\ims-workbench-old"' in plan
    assert '$newRoot = "C:\\ims-workbench-new"' in plan
    assert '$metadataDb = Join-Path $oldRoot ".ims_workbench\\metadata.sqlite"' in plan
    assert "python -m ims.api.workbench_portable_readiness --root $newRoot --layout portable" in plan
    assert 'python -m ims.api.workbench_readiness --frontend-dist (Join-Path $newRoot "app\\frontend\\dist") --db $metadataDb' in plan
    assert "python -m ims.api.metadata_import_cli roundtrip --db $metadataDb" in plan
    assert "im Kontext der neuen portablen Workbench-Version" in plan
    assert "Push-Location $newRoot" in plan
    assert '$env:PYTHONPATH = Join-Path $newRoot "python_port"' in plan
    assert "python -m ims.api.workbench_portable_readiness --root . --layout repo" in plan
    assert "python -m ims.api.workbench_readiness --frontend-dist frontend/dist --db $metadataDb" in plan
    assert "Pop-Location" in plan
    assert "Push-Location` allein" in plan
    assert "alten" in plan
    assert "Backend-/Adaptercode" in plan
    assert "Der neue" in plan
    assert "Anwendungspfad und der bestehende Metadatenpfad" in plan
    assert "Rollback heisst" in plan
    assert "kein fachlicher" in plan
    assert "Gleichheitsnachweis und keine historische Vollgleichheitsbehauptung" in plan
    assert "0` PRs, abgesehen von Review-Fixes" in plan
    assert "14-28+" in plan
    assert "Fachvalidierung und historische Vollgleichheit" in plan
    assert "Packaging und Bereitstellung" in plan
    assert "Lokale Startskripte fuer Windows, ohne Installer: vorbereitet" in plan
    assert "Readiness-Check fuer portable Ordnerstruktur: vorbereitet" in plan
    assert "Build-Snapshot fuer Frontend- und Backend-Artefakte: vorbereitet" in plan
    assert "Artefaktmanifest, Checksummen und Ausschluss lokaler Caches/Nutzerdaten: vorbereitet" in plan
    assert "Bundle-Trockenlauf auf Basis des Artefaktmanifests: vorbereitet" in plan
    assert "ZIP-Erzeugung als expliziter lokaler Build-Schritt: vorbereitet" in plan
    assert "ZIP-Smoke-Test ohne Simulation: vorbereitet" in plan
    assert "Backup-/Restore-Doku fuer lokale Metadaten: vorbereitet" in plan
    assert "Update-/Rollback-Doku fuer lokale Workbench-Versionen: vorbereitet" in plan
    assert "Release-Checkliste fuer lokale ZIP-Artefakte" in plan
    assert "Konsolidierter lokaler Release-Ablauf" in plan
    assert "Der lokale Release-Ablauf fuer ein ZIP-Artefakt" in plan
    assert "python -m ims.api.workbench_bundle_smoke --zip-path .\\dist\\ims-workbench-local.zip" in plan
    assert "python -m ims.api.workbench_portable_staging --zip-path .\\dist\\ims-workbench-local.zip --out .\\ims-workbench" in plan
    assert "python -m ims.api.workbench_portable_staging_smoke --root .\\ims-workbench" in plan
    assert "python -m ims.api.workbench_portable_readiness --root .\\ims-workbench --layout portable" in plan
    assert "Repo-Build: `npm.cmd run build`" in plan
    assert "ZIP-Artefakt: expliziter Zielpfad" in plan
    assert "staged sie erst ueber den expliziten" in plan
    assert "Portable Zielstruktur: erst nach separatem" in plan
    assert "Readiness `app\\frontend\\dist`" in plan
    assert "Portables Staging fuer ZIP-Artefakte" in plan
    assert "Repo-Layout-Eintraege wie" in plan
    assert "noch kein fertig gestagter portabler" in plan
    assert "Quelle ist entweder ein geprueftes Repo-Layout-ZIP" in plan
    assert "Ziel ist ein explizit angegebener, neuer oder leerer Staging-Ordner" in plan
    assert "ims-workbench/app/python_port" in plan
    assert "ims-workbench/app/frontend/dist" in plan
    assert "ims-workbench/start-workbench.cmd" in plan
    assert "ims-workbench/check-workbench.cmd" in plan
    assert "ims-workbench/data/.ims_workbench" in plan
    assert "ims-workbench/logs" in plan
    assert "Lokale Nutzerdaten werden nicht ueberschrieben" in plan
    assert "Staging, ZIP-Build und ZIP-Smoke bleiben getrennte Grenzen" in plan
    assert "kopiert nur die definierten Workbench-Anwendungsartefakte" in plan
    assert "Frontend wurde gebaut: `npm.cmd run build`" in plan
    assert "New-Item -ItemType Directory .\\dist -Force" in plan
    assert "workbench_bundle_build --root . --frontend-dist frontend/dist --out .\\dist\\ims-workbench-local.zip" in plan
    assert "ZIP-Build erzeugt den Output-Parent nicht automatisch" in plan
    assert "fehlender" in plan
    assert "Ausgabeordner bleibt ein Fehler" in plan
    assert "ZIP-Zielpfad liegt nicht unter eingeschlossenen Quellbaeumen" in plan
    assert "Bundle-Plan und ZIP-Smoke" in plan
    assert "konsolidierte lokale Release-Ablauf prueft das ZIP selbst" in plan
    assert "staged es" in plan
    assert "fehlenden oder leeren Zielordner" in plan
    assert "workbench_portable_readiness --layout portable" in plan
    assert "app\\frontend\\dist" in plan
    assert "Repo-Side-by-Side-Checks setzen `PYTHONPATH`" in plan
    assert "Bestehende Metadatenquelle wird explizit als `--db` uebergeben" in plan
    assert "Backup oder JSON-Export der Metadatenquelle" in plan
    assert "Rollback-Pfad ist vorbereitet" in plan
    assert "workbench_portable_readiness --root . --layout repo" in plan
    assert "workbench_portable_readiness --root .\\ims-workbench --layout portable" in plan
    assert "workbench_build_snapshot --root . --frontend-dist frontend/dist" in plan
    assert "workbench_artifact_manifest --root . --frontend-dist frontend/dist" in plan
    assert "workbench_bundle_plan --root . --frontend-dist frontend/dist" in plan
    assert "workbench_bundle_build --root . --frontend-dist frontend/dist --out .\\dist\\ims-workbench-local.zip" in plan
    assert "portable Strukturpruefung fuer Repo- und Zielstruktur" in plan
    assert "Build-Snapshots fuer vorhandene Frontend-/Backend-Artefakte" in plan
    assert "Artefaktmanifest fuer Ein- und Ausschlusspfade inklusive Groessen und SHA-256-Pruefsummen" in plan
    assert "Bundle-Trockenlauf auf Basis des Artefaktmanifests, ohne ZIP-Erzeugung" in plan
    assert "ZIP-Inhaltspruefung fuer explizit erzeugte lokale Bundles" in plan
    assert "ZIP-Smoke-Test fuer erwartete Workbench-Dateien, Ausschluesse und stabile ZIP-Metadaten" in plan
    assert "Backup-/Restore-Doku fuer `metadata.sqlite`, WAL-/SHM-Grenzen, Snapshot, Export, Roundtrip und Readiness" in plan
    assert "Update-/Rollback-Doku fuer parallele Versionstests, Datenablage-Trennung, Readiness, Roundtrip und manuellen Rollback" in plan
    assert "Lokale Release-Bereitstellung: konsolidiert" in plan
    assert "Portables Staging fuer ZIP-Artefakte: vorbereitet" in plan
    assert "Staging-Smoke fuer portable Zielstruktur und Startskriptgrenzen: vorbereitet" in plan
    assert "Staging-Smoke fuer zentrale Backend-Module" in plan
    assert "Backend-Importfaehigkeit" in plan
    assert "Importfaehigkeit aus dem gestagten Workbench-Root" in plan
    assert "Abschlusskonsolidierung: erledigt" in plan
    assert "0` geplanten PRs" in plan
    assert "portables Staging aus einem geprueften ZIP in eine leere Zielstruktur" in plan
    assert "nicht unter eingeschlossenen Quellbaeumen wie `python_port` oder `frontend/dist`" in plan
    assert "stabilen Zeitstempeln und Dateirechten" in plan
    assert "reproduzierbare ZIP-Pruefsummen bei identischem Inhalt" in plan
    assert "Ablehnung von ZIP-Zielpfaden unter eingeschlossenen Quellbaeumen" in plan
    assert "Keine Fachlogikaenderung" in plan
    assert "Keine Simulation starten" in plan
    assert "Keine neuen HTTP-Endpunkte" in plan
    assert "Kein HTTP-Schreibpfad" in plan
    assert "Kein Browser-Upload" in plan
    assert "Kein Browser-Download" in plan
    assert "Keine UI-Schreibpfade" in plan
    assert "Kein Installer" in plan
    assert "Kein ZIP- oder Release-Artefakt in diesem PR" in plan
    assert "Keine historische Vollgleichheitsbehauptung" in plan
    assert "lauffaehiges Paket ist kein fachlicher Gleichheitsnachweis" in plan


def test_workbench_start_scripts_are_readonly_packaging_helpers():
    check_script = CHECK_SCRIPT.read_text(encoding="utf-8")
    start_script = START_SCRIPT.read_text(encoding="utf-8")
    script_readme = SCRIPT_README.read_text(encoding="utf-8")
    combined_scripts = f"{check_script}\n{start_script}".lower()

    assert CHECK_SCRIPT.is_file()
    assert START_SCRIPT.is_file()
    assert SCRIPT_README.is_file()
    assert "python -m ims.api.workbench_diagnostics --frontend-dist frontend/dist" in check_script
    assert "python -m ims.api.workbench_readiness --frontend-dist frontend/dist" in check_script
    assert "python -m uvicorn ims.api.app:app --app-dir python_port --host 127.0.0.1 --port 8000" in start_script
    assert "frontend\\dist\\index.html" in check_script
    assert "frontend\\dist\\index.html" in start_script
    assert "startet keinen dauerhaften Server" in script_readme
    assert "startet nur den lokalen Backend-Server" in script_readme

    forbidden_fragments = (
        "metadata_import_cli import",
        "run_control_queue enqueue",
        "run_control_queue init",
        "run_control_preflight --run-id",
        "run_control_requests check",
        "npm.cmd install",
        "npm.cmd run build",
        "sqlite3 ",
    )
    for fragment in forbidden_fragments:
        assert fragment not in combined_scripts
