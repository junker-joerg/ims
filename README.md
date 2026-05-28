# ims

Dieses Repository enthält das Arbeitsgerüst für eine schrittweise, PR-basierte und semantisch konservative Migration von IMS.
Weitere Hinweise stehen unter `docs/migration/README.md`.

## Lokale Workbench

Eine erste lokale Backend-/Frontend-Shell ist unter `docs/migration/workbench_shell.md` beschrieben.

Kurzstart:

```powershell
python -m pip install -e .\python_port[dev]
cd frontend
npm.cmd install
npm.cmd run build
cd ..
python -m ims.api.workbench_diagnostics --frontend-dist frontend/dist
python -m uvicorn ims.api.app:app --app-dir python_port --host 127.0.0.1 --port 8000
```

Danach ist die Workbench lokal unter `http://127.0.0.1:8000/` erreichbar. Die aktuelle Workbench ist weiterhin rein lesend: keine Simulation, kein Browser-Upload und keine HTTP-/UI-Schreibpfade.

Optional kann die Diagnose eine explizite lokale Konfigurationsdatei lesen:

```powershell
python -m ims.api.workbench_diagnostics --config .\workbench.local.json
```

Ein rein beschreibender Startplan kann dieselben lokalen Werte als JSON zusammenfassen, ohne den Server zu starten:

```powershell
python -m ims.api.workbench_start_plan --config .\workbench.local.json
```

Eine lokale CLI-Uebersicht listet die vorhandenen Befehle und ihre Grenzen, ohne Import, Snapshot oder Serverstart auszufuehren:

```powershell
python -m ims.api.workbench_cli_overview
```

Ein lokaler Schreibvertrag beschreibt die vorbereiteten Metadaten-Schreibgrenzen, ohne einen Schreibpfad zu oeffnen:

```powershell
python -m ims.api.metadata_write_contracts
python -m ims.api.metadata_write_contracts check .\metadata_import.json
```

Ein lokaler Metadatenexport kann das bestehende Importformat reproduzierbar ausgeben. Ohne `--out` schreibt er nur nach stdout, mit `--out` nur in den expliziten Zielpfad:

```powershell
python -m ims.api.metadata_import_cli export
python -m ims.api.metadata_import_cli export --db .\.ims_workbench\metadata.sqlite --out .\metadata_export.json
```

Ein lokaler Roundtrip-Check prueft Export, Importformat und Schreibvertrag gemeinsam, ohne Dateien zu schreiben:

```powershell
python -m ims.api.metadata_import_cli roundtrip
python -m ims.api.metadata_import_cli roundtrip --db .\.ims_workbench\metadata.sqlite
```

Ein lokaler Import-Trockenlauf zeigt vor einem expliziten Import, welche Szenario- und Run-Metadaten neu waeren oder bestehende IDs ersetzen wuerden. Er schreibt nicht:

```powershell
python -m ims.api.metadata_import_cli dry-run .\metadata_import.json
python -m ims.api.metadata_import_cli dry-run .\metadata_import.json --db .\.ims_workbench\metadata.sqlite
```
