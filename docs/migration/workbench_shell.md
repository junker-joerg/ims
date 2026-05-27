# IMS Workbench Shell

Dieser Schritt eroeffnet den Modernisierungsblock fuer eine kleine lokale IMS Workbench. Er trennt bewusst Backend/API, Frontend/UI und die bereits abgegrenzte Python-Fachlogik.

## Inhalt

- `ims.api.app` stellt eine kleine FastAPI-Shell bereit.
- `/api/health` meldet den lokalen Backend-Status.
- `/api/version` meldet Name und Version der Workbench-Shell.
- Die gebaute Vite-Anwendung aus `frontend/dist` wird lokal ueber `/` und `/assets` ausgeliefert.
- `frontend/` enthaelt eine Vite/React/TypeScript-Oberflaeche mit einer ruhigen Dashboard-Ansicht.

## Grenzen

- Keine Steuerung echter Fachlogiklaeufe.
- Keine Aenderung am Simulationskern.
- Keine neue historische Validierungsbehauptung.
- Noch keine SQLite-Persistenz fuer Szenario- oder Run-Metadaten.

## Lokaler Start

```powershell
python -m pip install -e .\python_port[web]
npm.cmd install --prefix frontend
npm.cmd run build --prefix frontend
python -m uvicorn ims.api.app:app --app-dir python_port --host 127.0.0.1 --port 8000
```

Danach ist die Workbench unter `http://localhost:8000/` erreichbar.

## Anschluss

Der naechste Modernisierungsschritt sollte die API-Grenzen fuer Szenario- und Run-Metadaten entwerfen, ohne den Fachlogikkern direkt mit UI-Zustaenden zu vermischen. SQLite kann dabei vorbereitet werden, sobald die Metadatenformen stabil genug sind.
