from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
README = REPO_ROOT / "README.md"
WORKBENCH_DOC = REPO_ROOT / "docs" / "migration" / "workbench_shell.md"


def test_readme_documents_local_workbench_start_commands():
    readme = README.read_text(encoding="utf-8")

    assert "python -m ims.api.workbench_diagnostics --frontend-dist frontend/dist" in readme
    assert "python -m ims.api.workbench_start_plan --config .\\workbench.local.json" in readme
    assert "python -m ims.api.workbench_readiness --frontend-dist frontend/dist" in readme
    assert "python -m ims.api.workbench_cli_overview" in readme
    assert "Kurzstart fuer die lokale Browser-Workbench" in readme
    assert "Start und Diagnose" in readme
    assert "Vertraege und Run-Control-Grenzen" in readme
    assert "Metadaten-CLI" in readme
    assert "python -m ims.api.metadata_write_contracts" in readme
    assert "python -m ims.api.metadata_write_contracts check .\\metadata_import.json" in readme
    assert "python -m ims.api.run_control_contracts" in readme
    assert "python -m ims.api.run_control_preflight --run-id baseline-python-tests" in readme
    assert "python -m ims.api.metadata_import_cli export" in readme
    assert "python -m ims.api.metadata_import_cli export --db .\\.ims_workbench\\metadata.sqlite --out .\\metadata_export.json" in readme
    assert "python -m ims.api.metadata_import_cli roundtrip" in readme
    assert "python -m ims.api.metadata_import_cli roundtrip --db .\\.ims_workbench\\metadata.sqlite" in readme
    assert "python -m ims.api.metadata_import_cli dry-run .\\metadata_import.json" in readme
    assert "python -m ims.api.metadata_import_cli dry-run .\\metadata_import.json --db .\\.ims_workbench\\metadata.sqlite" in readme
    assert "python -m ims.api.metadata_import_cli import .\\metadata_import.json --db .\\.ims_workbench\\metadata.sqlite" in readme
    assert "python -m uvicorn ims.api.app:app --app-dir python_port --host 127.0.0.1 --port 8000" in readme
    assert "npm.cmd run build" in readme
    assert "Lokaler Workbench-v1 Abschlussstatus" in readme
    assert "expliziten Importbericht und Run-Control-Preflight" in readme
    assert "keine HTTP-/UI-Schreibpfade" in readme


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
    assert "python -m ims.api.workbench_cli_overview" in doc
    assert "python -m ims.api.metadata_write_contracts" in doc
    assert "python -m ims.api.metadata_write_contracts check .\\metadata_import.json" in doc
    assert "python -m ims.api.run_control_contracts" in doc
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
    assert "Der Run-Control-Preflight ist ebenfalls rein lokal und lesend" in doc
    assert "schaltet keinen UI-Startbutton frei" in doc
    assert "keine Fachvalidierung und keine historische Vollgleichheitsbehauptung" in doc
    assert "Run-Felds `execution_enabled` mit dem Wert `false`" in doc
    assert "execution_enabled=true" in doc
    assert "0-1 reviewbare PRs" in doc
    assert "Die lokale Bedienreihenfolge fuer v1 ist" in doc
    assert "Die lokale Workbench-v1 ist als rein lokale Browser-Workbench konsolidiert" in doc
    assert "Nicht enthalten sind weiterhin Fachlogikaenderungen" in doc
