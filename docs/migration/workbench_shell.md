# IMS Workbench Shell

Dieser Schritt eroeffnet den Modernisierungsblock fuer eine kleine lokale IMS Workbench. Er trennt bewusst Backend/API, Frontend/UI und die bereits abgegrenzte Python-Fachlogik.

## Inhalt

- `ims.api.app` stellt eine kleine FastAPI-Shell bereit.
- `/api/health` meldet den lokalen Backend-Status.
- `/api/version` meldet Name und Version der Workbench-Shell.
- `/api/scenarios` liefert lokale Szenario-Metadaten als versionierte, statische Adapterdaten.
- `/api/runs` liefert lokale Run-Metadaten als versionierte, statische Adapterdaten.
- `ims.api.metadata_repository` bereitet eine lokale SQLite-Ablage fuer diese Metadaten vor.
- Die gebaute Vite-Anwendung aus `frontend/dist` wird lokal ueber `/` und `/assets` ausgeliefert.
- `frontend/` enthaelt eine Vite/React/TypeScript-Oberflaeche mit einer ruhigen Dashboard-Ansicht, die diese Metadaten liest.
- `python_port[dev]` enthaelt die Web-Testabhaengigkeiten, damit die Standardtests die API-Tests ohne separate manuelle Web-Installation sammeln koennen.

## Grenzen

- Keine Steuerung echter Fachlogiklaeufe.
- Keine Aenderung am Simulationskern.
- Keine neue historische Validierungsbehauptung.
- SQLite wird aktuell nur als lesende, deterministisch geseedete Repository-Schicht vorbereitet.
- Noch keine Schreibendpunkte fuer Szenario- oder Run-Metadaten.

## Metadatenmodell

Die Workbench-Metadaten sind beschreibende DTOs an der API-Grenze. Jede Antwort enthaelt:

- `schema_version` fuer die stabile Antwortform.
- `generated_at` als deterministischen Erzeugungszeitpunkt der statischen Metadaten.
- `items` mit Szenario- oder Run-Eintraegen.

Szenario-Eintraege enthalten ID, Anzeigename, Status, fachlichen Umfang, Quelle, Validierungszusammenfassung, Aktualisierungszeitpunkt und Notiz. Run-Eintraege enthalten zusaetzlich das zugehoerige Szenario, ein Periodenfenster und `execution_enabled`. Dieses Feld bleibt aktuell immer `false`, weil die Workbench noch keine echten Laeufe startet.

## SQLite-Vorbereitung

Die SQLite-Schicht definiert Tabellen fuer Szenarien und Runs und seedet sie deterministisch aus den statischen Metadaten. Die API liest dieselbe DTO-Form aus dem Repository wie zuvor aus den statischen Objekten.

Ohne weitere Konfiguration verwendet die Backend-Shell eine in-memory-Datenbank. Fuer lokale Dateiablage kann `IMS_METADATA_DB` gesetzt werden:

```powershell
$env:IMS_METADATA_DB = ".ims_workbench\metadata.sqlite"
python -m uvicorn ims.api.app:app --app-dir python_port --host 127.0.0.1 --port 8000
```

Auch mit Dateiablage bleibt dieser Schritt lesend aus Sicht der API: Es gibt keine UI-Schreibpfade und keine Endpunkte zum Anlegen oder Veraendern von Metadaten.

## Lokaler Start

```powershell
python -m pip install -e .\python_port[dev]
cd frontend
npm.cmd install
npm.cmd run build
cd ..
python -m uvicorn ims.api.app:app --app-dir python_port --host 127.0.0.1 --port 8000
```

Danach ist die Workbench unter `http://localhost:8000/` erreichbar.

## Anschluss

Der naechste Modernisierungsschritt kann kontrollierte Metadaten-Schreibpfade entwerfen. Dabei sollte die bestehende DTO-Grenze erhalten bleiben, ohne den Fachlogikkern direkt mit UI-Zustaenden zu vermischen.
