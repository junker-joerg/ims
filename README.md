# ims

Dieses Repository enthält das Arbeitsgerüst für eine schrittweise, PR-basierte und semantisch konservative Migration von IMS.
Weitere Hinweise stehen unter `docs/migration/README.md`.

## Lokale Workbench

Die lokale Workbench-v1 ist unter `docs/migration/workbench_shell.md` beschrieben. Sie laeuft zuerst lokal im Browser und bleibt bewusst von der Fachlogik getrennt.

Kurzstart fuer die lokale Browser-Workbench:

```powershell
python -m pip install -e .\python_port[dev]
cd frontend
npm.cmd install
npm.cmd run build
cd ..
python -m ims.api.workbench_diagnostics --frontend-dist frontend/dist
python -m ims.api.workbench_readiness --frontend-dist frontend/dist
python -m uvicorn ims.api.app:app --app-dir python_port --host 127.0.0.1 --port 8000
```

Danach ist die Workbench lokal unter `http://127.0.0.1:8000/` erreichbar. Die aktuelle Workbench ist weiterhin rein lesend: keine Simulation, kein Browser-Upload und keine HTTP-/UI-Schreibpfade.

Alternativ stehen erste lokale Windows-Skripte bereit:

```powershell
scripts\workbench\check-workbench.cmd
scripts\workbench\start-workbench.cmd
```

Die Skripte setzen ein gebautes `frontend/dist` voraus. Das Check-Skript fuehrt Diagnose und Readiness aus, startet aber keinen dauerhaften Server. Das Start-Skript startet nur den lokalen Backend-Server.

Lokaler Workbench-v1 Abschlussstatus:

Die lokale Workbench-v1 ist als Modernisierungs-Meilenstein abgeschlossen. Dieser Abschluss ist kein Release-Tag, keine Fachvalidierung und keine historische Vollgleichheitsbehauptung.

- Backend-Health und Version sind lokal verfuegbar.
- Das gebaute Frontend wird statisch ausgeliefert.
- Szenario- und Run-Metadaten sind lesend als Listen, Details, Filter und Auswahlzusammenfassung verfuegbar.
- Betriebsdiagnose, Metadatenquelle, Konsistenzdiagnose, Readiness und lokale CLI-Grenzen sind dokumentiert und getestet.
- Lokale CLI-Adapter decken Diagnose, Import-Check, Preview, Dry-Run, Export, Roundtrip, Snapshot, expliziten Importbericht und Run-Control-Preflight ab.
- Keine Fachlogikaenderung, keine Simulation, keine HTTP-/UI-Schreibpfade und keine historische Vollgleichheitsbehauptung.

Die spaetere Run-Steuerung und Gesamtplanung bis zum vollstaendigen Abschluss sind unter `docs/migration/workbench_run_control_plan.md` beschrieben. Der separate Packaging- und Bereitstellungsblock ist unter `docs/migration/workbench_packaging_plan.md` geplant. Diese Plaene sind konzeptionell und starten keine Simulation.

Start und Diagnose:

Optional kann die Diagnose eine explizite lokale Konfigurationsdatei lesen:

```powershell
python -m ims.api.workbench_diagnostics --config .\workbench.local.json
```

Ein rein beschreibender Startplan kann dieselben lokalen Werte als JSON zusammenfassen, ohne den Server zu starten:

```powershell
python -m ims.api.workbench_start_plan --config .\workbench.local.json
```

Eine lokale v1-Bereitschaftspruefung buendelt Diagnose, Metadatenquelle, CLI-Grenzen und Run-Control-Preflight, ohne den Server zu starten:

```powershell
python -m ims.api.workbench_readiness --frontend-dist frontend/dist
```

Eine lokale CLI-Uebersicht listet die vorhandenen Befehle und ihre Grenzen, ohne Import, Snapshot oder Serverstart auszufuehren:

```powershell
python -m ims.api.workbench_cli_overview
```

Vertraege und Run-Control-Grenzen:

Ein lokaler Schreibvertrag beschreibt die vorbereiteten Metadaten-Schreibgrenzen, ohne einen Schreibpfad zu oeffnen:

```powershell
python -m ims.api.metadata_write_contracts
python -m ims.api.metadata_write_contracts check .\metadata_import.json
```

Ein lokaler Run-Control-Vertrag beschreibt die spaetere Steuerungsgrenze, ohne einen Lauf zu starten:

```powershell
python -m ims.api.run_control_contracts
```

Ein lokaler Run-Control-Request-Check validiert eine spaetere Steuerungsanfrage als DTO, ohne sie zu speichern oder auszufuehren:

```powershell
python -m ims.api.run_control_requests check .\run_control_request.json
```

Eine lokale Run-Control-Queue kann solche Requests in einer expliziten SQLite-Datei vormerken, ohne Ausfuehrung, Worker oder Scheduler zu starten:

```powershell
python -m ims.api.run_control_queue init --db .\.ims_workbench\metadata.sqlite
python -m ims.api.run_control_queue enqueue .\run_control_request.json --db .\.ims_workbench\metadata.sqlite
python -m ims.api.run_control_queue list --db .\.ims_workbench\metadata.sqlite
```

`init` und `enqueue` sind die expliziten lokalen Queue-Schreibbefehle. `list` und `show` lesen die Queue-Datenbank read-only, vermeiden neue WAL-/SHM-Sidecars und lehnen unvollstaendige Sidecar-Zustaende ab.

Ein lokaler Run-Control-Preflight prueft vorhandene Run-Metadaten gegen diese gesperrte Steuerungsgrenze, ohne einen Lauf zu starten:

```powershell
python -m ims.api.run_control_preflight --run-id baseline-python-tests
```

Metadaten-CLI:

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

Der explizite lokale Import schreibt nur in den angegebenen SQLite-Pfad und gibt danach einen kleinen Importbericht mit geschriebenen IDs und Konsistenzstatus aus:

```powershell
python -m ims.api.metadata_import_cli import .\metadata_import.json --db .\.ims_workbench\metadata.sqlite
```
