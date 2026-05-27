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
- `/api/metadata/source` beschreibt lesend, ob die Metadatenquelle in-memory oder als SQLite-Datei konfiguriert ist.
- Die Workbench buendelt Health, Version, Capabilities und Metadatenquelle in einer kleinen lesenden Betriebsdiagnose.
- Die Workbench zeigt Szenario-Metadaten zusaetzlich in einer scanbaren, rein lesenden Uebersicht.
- Die Workbench zeigt Run-Metadaten zusaetzlich in einer scanbaren, rein lesenden Uebersicht.
- `ims.api.metadata_repository` bereitet eine lokale SQLite-Ablage fuer diese Metadaten vor.
- `ims.api.metadata_import` kann lokale JSON-Metadaten kontrolliert in diese Ablage importieren.
- `ims.api.metadata_import_cli` macht diesen Importpfad lokal pruefbar, ohne HTTP- oder UI-Schreibpfade zu oeffnen.
- Die gebaute Vite-Anwendung aus `frontend/dist` wird lokal ueber `/` und `/assets` ausgeliefert.
- `frontend/` enthaelt eine Vite/React/TypeScript-Oberflaeche mit einer ruhigen Dashboard-Ansicht, die Listen- und Detailmetadaten liest.
- `python_port[dev]` enthaelt die Web-Testabhaengigkeiten, damit die Standardtests die API-Tests ohne separate manuelle Web-Installation sammeln koennen.

## Grenzen

- Keine Steuerung echter Fachlogiklaeufe.
- Keine Aenderung am Simulationskern.
- Keine neue historische Validierungsbehauptung.
- SQLite wird aktuell nur als lesende, deterministisch geseedete Repository-Schicht an der API genutzt.
- Interne Repository-Schreibmethoden sind vorbereitet und validiert, aber nicht als API- oder UI-Schreibpfade freigeschaltet.
- Der lokale Importpfad ist eine Python-Adapterfunktion, kein HTTP- oder UI-Schreibpfad.
- Der lokale CLI-Adapter schreibt nur, wenn ein SQLite-Zielpfad explizit angegeben wird.
- Die Frontend-Detailansicht ist rein lesend und nutzt nur die Detail-Endpunkte.
- Die Szenario-Uebersicht ist rein lesend und enthaelt keine Start-, Upload- oder Editierkontrollen.
- Die Run-Uebersicht ist rein lesend und enthaelt keine Start- oder Editierkontrollen.
- Die Metadatenquellen-Anzeige ist reine Betriebsdiagnose und oeffnet keine Persistenz- oder Ausfuehrungspfade.
- Die Betriebsdiagnose buendelt vorhandene Statusendpunkte, startet aber keine Laeufe und schreibt keine Daten.
- Die Importvorschau ist rein informativ und enthaelt keinen Upload, Editor oder Browser-Schreibpfad.
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

Die Workbench nutzt diese Endpunkte fuer eine kompakte Detailansicht zu ausgewaehltem Szenario und Run. Fehler beim Detailabruf werden knapp angezeigt; daraus entsteht kein Editor- oder Start-Workflow.

## Szenario-Uebersicht

Die Workbench zeigt die vorhandenen Szenario-Metadaten in einer kompakten Uebersicht. Sie nutzt weiterhin nur die bestehenden Listen- und Detaildaten aus `/api/scenarios` und `/api/scenarios/{scenario_id}`. Sichtbar sind Szenario-Anzeigename, Status, fachlicher Umfang, Quelle, Validierungsumfang, Aktualisierungszeitpunkt und die globale Ausfuehrungsgrenze.

Die Ausfuehrungsgrenze kommt aus `/api/metadata/capabilities` und bleibt als gesperrt sichtbar. Die Uebersicht bietet keine Start-Schaltflaeche, keinen Editor, keinen Upload und keinen Schreibpfad.

## Run-Uebersicht

Die Workbench zeigt die vorhandenen Run-Metadaten in einer kompakten Uebersicht. Sie nutzt weiterhin nur die bestehenden Listen- und Detaildaten aus `/api/runs` und `/api/runs/{run_id}` sowie bereits geladene Szenario-Metadaten fuer Anzeigenamen. Sichtbar sind Run-Anzeigename, Status, Szenario-Bezug, Periodenfenster, Quelle und die Ausfuehrungsgrenze.

`execution_enabled` bleibt eine reine Grenze und wird als gesperrt angezeigt. Die Uebersicht bietet keine Start-Schaltflaeche, keinen Editor und keinen Schreibpfad.

## Metadatenquelle

`/api/metadata/source` liefert eine kleine, stabile Statusform fuer die lokale Metadatenquelle:

```json
{
  "schema_version": "ims.workbench.metadata.v1",
  "storage_kind": "memory",
  "configured": false,
  "injected": false,
  "writes_enabled": false,
  "execution_enabled": false
}
```

Wenn `IMS_METADATA_DB` gesetzt ist, meldet der Endpunkt `storage_kind = "sqlite"`, `configured = true` und den aufgeloesten Pfad. Wenn `create_app(metadata_repository=...)` ein Repository erhaelt, kommt die Quellenbeschreibung aus genau diesem Repository; fuer eine injizierte SQLite-Ablage wird deshalb ebenfalls `storage_kind = "sqlite"` mit `injected = true` gemeldet. Dadurch beschreibt die Diagnose die Datenquelle, aus der die API tatsaechlich liest.

Diese Antwort erzeugt beim reinen Import oder Quellenabruf keine SQLite-Datei. Die Workbench zeigt diese Information in der lokalen Ablage als reine Diagnose an. `writes_enabled` und `execution_enabled` bleiben dort bewusst `false`.

## Smoke-Tests

Die Workbench-Shell ist mit kleinen Smoke-Tests abgesichert:

- API-Health muss erreichbar sein.
- Version, Metadatenquelle und Capabilities muessen gemeinsam lesbar sein.
- Szenario- und Run-Listen muessen lesbar sein.
- Szenario- und Run-Details muessen fuer IDs aus den Listen lesbar sein.
- Fehlende Metadaten-IDs muessen die stabile `metadata_not_found`-Fehlerform liefern.
- Eine gebaute Frontend-Struktur aus `index.html` und `/assets` muss statisch ausgeliefert werden.
- Die Frontend-Shell muss die Detail-, Importvorschau- und Betriebsdiagnose-Vertraege im Quelltext enthalten.
- Die Szenario-Uebersicht muss Szenario-Daten weiterhin lesend darstellen und die globale Ausfuehrungsgrenze als gesperrt behandeln.
- Die Run-Uebersicht muss Run-Daten weiterhin lesend darstellen und `execution_enabled` als gesperrte Grenze behandeln.

Das ist bewusst kein vollstaendiger Browser-End-to-End-Test. Interaktion, Layout und echte Browserereignisse werden weiterhin lokal ueber die Vorschau geprueft; der automatisierte Smoke-Test bleibt ohne zusaetzliche Browser-Testabhaengigkeiten.

## Betriebsdiagnose

Die Workbench zeigt eine kompakte Betriebsdiagnose aus bestehenden Endpunkten:

- `/api/health` fuer Backend-Status und gebautes Frontend.
- `/api/version` fuer Name und Version der Workbench-Shell.
- `/api/metadata/source` fuer die aktuelle Metadatenquelle.
- `/api/metadata/capabilities` fuer gesperrte Schreib- und Ausfuehrungsgrenzen.

Diese Diagnose ist rein lesend. Sie bestaetigt, dass Schreibpfade, Simulation und Browser-Import weiter gesperrt sind, und verweist fuer den Import nur auf den lokalen CLI-Adapter. Sie ist kein Editor, kein Upload-Workflow und kein Startpunkt fuer echte Simulationen.

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

Die Workbench zeigt das erwartete Importformat als lesende Vorschau. Sie erklaert die Top-Level-Felder `schema_version`, `scenarios` und `runs`, verweist auf den Python-Adapter und haelt sichtbar fest, dass `execution_enabled` weiter `false` bleiben muss. Es gibt keinen File-Upload, keinen Browser-Editor und keinen HTTP-Schreibpfad.

Der lokale CLI-Adapter kann dieselbe Datei zuerst nur pruefen:

```powershell
python -m ims.api.metadata_import_cli check .\metadata_import.json
```

Ein Import schreibt nur in eine ausdruecklich angegebene SQLite-Datei:

```powershell
python -m ims.api.metadata_import_cli import .\metadata_import.json --db .\.ims_workbench\metadata.sqlite
```

Die Ausgabe ist eine knappe JSON-Statuszeile. Fehler liefern ebenfalls eine stabile JSON-Form mit `status = "error"` und einer kurzen Meldung. Der Adapter liest weder `IMS_METADATA_DB` als implizites Schreibziel noch oeffnet er einen HTTP-Endpunkt. Die API- und UI-Schreibpfade bleiben gesperrt.

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

Import-Bundles werden vor dem ersten Schreibzugriff vollstaendig gegen die Repository-Grenzen validiert. Wenn ein spaeterer Run-Eintrag ungueltig ist, bleiben vorher im Bundle enthaltene neue Szenarien deshalb ungeschrieben. Der lokale CLI-Check nutzt dieselbe Referenzvalidierung gegen die geseedeten Metadaten und die Szenarien aus der Importdatei, damit ein Check keine Datei akzeptiert, die der direkte Import wegen unbekannter `scenario_id` ablehnen wuerde.

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

Der naechste Modernisierungsschritt kann die lokale Metadatenablage sichtbarer machen, etwa durch eine lesende Anzeige der aktiven SQLite-Quelle und der Import-/Seed-Herkunft. Schreibende API- oder UI-Pfade sollten weiterhin separat und explizit entworfen werden. Dabei sollte die bestehende DTO-Grenze erhalten bleiben, ohne den Fachlogikkern direkt mit UI-Zustaenden zu vermischen.
