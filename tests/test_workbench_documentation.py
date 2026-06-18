from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
README = REPO_ROOT / "README.md"
WORKBENCH_DOC = REPO_ROOT / "docs" / "migration" / "workbench_shell.md"
RUN_CONTROL_PLAN = REPO_ROOT / "docs" / "migration" / "workbench_run_control_plan.md"
PACKAGING_PLAN = REPO_ROOT / "docs" / "migration" / "workbench_packaging_plan.md"
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
    assert "python -m ims.api.run_control_requests check .\\run_control_request.json" in readme
    assert "python -m ims.api.run_control_queue enqueue .\\run_control_request.json --db .\\.ims_workbench\\metadata.sqlite" in readme
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
    assert "docs/migration/workbench_packaging_plan.md" in readme
    assert "als lokaler ZIP-/Staging-Abschlussstatus konsolidiert" in readme
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
    assert "python -m ims.api.run_control_requests check .\\run_control_request.json" in doc
    assert "python -m ims.api.run_control_queue enqueue .\\run_control_request.json --db .\\.ims_workbench\\metadata.sqlite" in doc
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
    assert "immutable=1" not in doc
    assert "Vollgleichheit" in doc
    assert "Keines dieser Kommandos startet eine Simulation" in doc
    assert "keine Konfigurationsdatei automatisch" in doc
    assert "relativ zum Speicherort der Konfigurationsdatei" in doc
    assert "Der Startplan startet keinen Server" in doc
    assert "## v1-Bereitschaftspruefung" in doc
    assert "Die Readiness-Pruefung startet keinen Server" in doc
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
    assert "Request-DTO enthaelt `run_id`, `scenario_id`, optional `metadata_db`, `requested_by`, `created_at`" in doc
    assert "Die Queue speichert `queue_id`, Request-Daten, Status und Ausfuehrungsgrenzen" in doc
    assert "Kein Queue-Befehl startet eine Simulation" in doc
    assert "Der Run-Control-Preflight ist ebenfalls rein lokal und lesend" in doc
    assert "schaltet keinen UI-Startbutton frei" in doc
    assert "keine Fachvalidierung und keine historische Vollgleichheitsbehauptung" in doc
    assert "Run-Felds `execution_enabled` mit dem Wert `false`" in doc
    assert "execution_enabled=true" in doc
    assert "0 reviewbare PRs" in doc
    assert "Die lokale Bedienreihenfolge fuer v1 ist" in doc
    assert "Die lokale Workbench-v1 ist als rein lokale Browser-Workbench und Modernisierungs-Meilenstein abgeschlossen" in doc
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
    assert "33-50+" in plan
    assert "Realistische Mitte: ca. `44` PRs" in plan
    assert "Packaging und Bereitstellung" in plan
    assert "Fachvalidierung und historische Vollgleichheit" in plan
    assert "Phase 1: Rein lokale Run-Control-Requests" in plan
    assert "Phase 6: Haertung, Doku, Smoke-/E2E-Pruefung" in plan
    assert "PR 1: Run-Control-Plan und Roadmap" in plan
    assert "PR 2: Run-Control-Request-DTO und lokale Validierung" in plan
    assert "PR 3: Run-Control-Queue/Repository in SQLite, ohne Ausfuehrung" in plan
    assert "keinen Worker, Scheduler oder Simulationslauf starten" in plan
    assert "PR 13-15: Haertung, Doku, Smoke-/E2E-Checks und Abschluss" in plan
    assert "3-5 Puffer-PRs" in plan
    assert "execution_enabled=false" in plan
    assert "`execution_enabled` bleibt bis zur expliziten Ausfuehrungsfreigabe `false`" in plan
    assert "Keine Fachlogikaenderung" in plan
    assert "Keine Simulation starten" in plan
    assert "Keine neuen HTTP-Endpunkte" in plan
    assert "Kein Packaging in diesem PR" in plan
    assert "Keine historische Vollgleichheitsbehauptung" in plan


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
    assert "18-36+" in plan
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
