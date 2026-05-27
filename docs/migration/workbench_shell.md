# IMS Workbench Shell

Dieser Schritt eroeffnet den Modernisierungsblock fuer eine kleine lokale IMS Workbench. Er trennt bewusst Backend/API, Frontend/UI und die bereits abgegrenzte Python-Fachlogik.

## Inhalt

- `ims.api.app` stellt eine kleine FastAPI-Shell bereit.
- `/api/health` meldet den lokalen Backend-Status.
- `/api/version` meldet Name und Version der Workbench-Shell.
- `/api/scenarios` liefert lokale Szenario-Metadaten als versionierte, statische Adapterdaten.
- `/api/runs` liefert lokale Run-Metadaten als versionierte, statische Adapterdaten.
- `/api/scenarios/{scenario_id}` und `/api/runs/{run_id}` liefern einzelne Metadatensaetze per ID.
- `/api/metadata/capabilities` beschreibt die aktuell gesperrten Schreib- und Ausfuehrungsgrenzen.
- `ims.api.metadata_repository` bereitet eine lokale SQLite-Ablage fuer diese Metadaten vor.
- `ims.api.metadata_import` kann lokale JSON-Metadaten kontrolliert in diese Ablage importieren.
- Die gebaute Vite-Anwendung aus `frontend/dist` wird lokal ueber `/` und `/assets` ausgeliefert.
- `frontend/` enthaelt eine Vite/React/TypeScript-Oberflaeche mit einer ruhigen Dashboard-Ansicht, die diese Metadaten liest.
- `python_port[dev]` enthaelt die Web-Testabhaengigkeiten, damit die Standardtests die API-Tests ohne separate manuelle Web-Installation sammeln koennen.

## Grenzen

- Keine Steuerung echter Fachlogiklaeufe.
- Keine Aenderung am Simulationskern.
- Keine neue historische Validierungsbehauptung.
- SQLite wird aktuell nur als lesende, deterministisch geseedete Repository-Schicht an der API genutzt.
- Interne Repository-Schreibmethoden sind vorbereitet und validiert, aber nicht als API- oder UI-Schreibpfade freigeschaltet.
- Der lokale Importpfad ist eine Python-Adapterfunktion, kein HTTP- oder UI-Schreibpfad.
- Noch keine Schreibendpunkte fuer Szenario- oder Run-Metadaten.

## Metadatenmodell

Die Workbench-Metadaten sind beschreibende DTOs an der API-Grenze. Jede Antwort enthaelt:

- `schema_version` fuer die stabile Antwortform.
- `generated_at` als deterministischen Erzeugungszeitpunkt der statischen Metadaten.
- `items` mit Szenario- oder Run-Eintraegen.

Szenario-Eintraege enthalten ID, Anzeigename, Status, fachlichen Umfang, Quelle, Validierungszusammenfassung, Aktualisierungszeitpunkt und Notiz. Run-Eintraege enthalten zusaetzlich das zugehoerige Szenario, ein Periodenfenster und `execution_enabled`. Dieses Feld bleibt aktuell immer `false`, weil die Workbench noch keine echten Laeufe startet.

Die Detail-Endpunkte geben dieselbe Einzelform zurueck, die auch in den Listen unter `items` steht. Nicht gefundene IDs liefern stabil:

```json
{
  "error": {
    "code": "metadata_not_found",
    "resource": "scenario",
    "id": "missing-scenario",
    "message": "scenario metadata not found"
  }
}
```

## SQLite-Vorbereitung

Die SQLite-Schicht definiert Tabellen fuer Szenarien und Runs und seedet sie deterministisch aus den statischen Metadaten. Das Seeding ist nicht-destruktiv: bestehende lokale Zeilen werden nicht durch Defaultwerte ueberschrieben. Die API liest dieselbe DTO-Form aus dem Repository wie zuvor aus den statischen Objekten.

Die Default-App baut die SQLite-Verbindung lazy beim ersten Metadatenzugriff auf. Ein reiner Import von `ims.api.app` darf dadurch keine konfigurierte `IMS_METADATA_DB` anlegen oder veraendern.

Ohne weitere Konfiguration verwendet die Backend-Shell eine in-memory-Datenbank. Fuer lokale Dateiablage kann `IMS_METADATA_DB` gesetzt werden:

```powershell
$env:IMS_METADATA_DB = ".ims_workbench\metadata.sqlite"
python -m uvicorn ims.api.app:app --app-dir python_port --host 127.0.0.1 --port 8000
```

Auch mit Dateiablage bleibt dieser Schritt lesend aus Sicht der API: Es gibt keine UI-Schreibpfade und keine Endpunkte zum Anlegen oder Veraendern von Metadaten.

## Schreibgrenzen

Die Repository-Schicht kennt vorbereitete Upsert-Methoden fuer Szenario- und Run-Metadaten. Diese Methoden validieren die minimale Metadatenform und lehnen `execution_enabled = true` fuer Runs ab. Damit wird verhindert, dass Metadatenpflege versehentlich als Run-Steuerung verstanden wird.

Der Capabilities-Endpunkt meldet deshalb weiterhin:

- Szenario-Metadaten-Schreiben: vorbereitet, aber API-seitig deaktiviert.
- Run-Metadaten-Schreiben: vorbereitet, aber API-seitig deaktiviert.
- Simulation ausfuehren: deaktiviert.

## Lokaler Metadatenimport

`ims.api.metadata_import` definiert einen kleinen Importpfad fuer lokale JSON-Dateien. Der Import schreibt nur in die SQLite-Metadatenablage und verwendet die bestehenden Repository-Upserts. Er startet keine Simulation und veraendert keine Fachlogik.

Das Importformat ist bewusst nahe an der API-DTO-Form:

```json
{
  "schema_version": "ims.workbench.metadata.v1",
  "scenarios": [
    {
      "id": "local-imported-scenario",
      "display_name": "Lokal importiertes Szenario",
      "status": "draft",
      "domain_scope": "Metadaten",
      "source": {
        "kind": "fixture",
        "label": "Lokale Importdatei",
        "path": "local/metadata.json"
      },
      "validation": {
        "status": "planned",
        "scope": "keine Fachvalidierung",
        "claim": "Importiert nur Workbench-Metadaten."
      },
      "updated_at": "2026-05-27T00:00:00Z",
      "notes": "Lokaler Metadatenimport ohne Simulationssteuerung."
    }
  ],
  "runs": [
    {
      "id": "local-imported-run",
      "display_name": "Importierter Metadatenlauf",
      "scenario_id": "local-imported-scenario",
      "status": "planned",
      "source": {
        "kind": "fixture",
        "label": "Lokale Importdatei",
        "path": "local/metadata.json"
      },
      "validation": {
        "status": "planned",
        "scope": "keine Simulation",
        "claim": "Beschreibender Run-Metadatensatz."
      },
      "period_window": "keine Simulation",
      "execution_enabled": false,
      "updated_at": "2026-05-27T00:00:00Z"
    }
  ]
}
```

Der Import validiert:

- Pflichtfelder muessen vorhanden und nicht leer sein.
- `schema_version` muss zur aktuellen Metadatenform passen.
- Run-Eintraege duerfen nur auf vorhandene oder im selben Import enthaltene Szenarien verweisen.
- `execution_enabled` muss `false` bleiben.

Import-Bundles werden vor dem ersten Schreibzugriff vollstaendig gegen die Repository-Grenzen validiert. Wenn ein spaeterer Run-Eintrag ungueltig ist, bleiben vorher im Bundle enthaltene neue Szenarien deshalb ungeschrieben.

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

Der naechste Modernisierungsschritt kann entscheiden, ob zuerst ein kleiner Szenario-Metadaten-Editor oder ein expliziter HTTP-Schreibpfad fuer diese Importgrenze sinnvoller ist. Dabei sollte die bestehende DTO-Grenze erhalten bleiben, ohne den Fachlogikkern direkt mit UI-Zustaenden zu vermischen.
