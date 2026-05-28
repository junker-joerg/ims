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
- `/api/metadata/consistency` beschreibt lesend einfache Konsistenzkennzahlen der aktuellen Szenario- und Run-Metadaten.
- Die Workbench buendelt Health, Version, Capabilities und Metadatenquelle in einer kleinen lesenden Betriebsdiagnose.
- Die Workbench zeigt die Metadaten-Konsistenz als kleine Diagnose ohne Reparaturpfade.
- Die Workbench zeigt Szenario-Metadaten zusaetzlich in einer scanbaren, rein lesenden Uebersicht.
- Die Szenario-Uebersicht enthaelt clientseitige Filter fuer Suche, Status, Quelle und Umfang.
- Die Workbench zeigt Run-Metadaten zusaetzlich in einer scanbaren, rein lesenden Uebersicht.
- Die Run-Uebersicht enthaelt clientseitige Filter fuer Suche, Status, Szenario und Quelle.
- `ims.api.metadata_repository` bereitet eine lokale SQLite-Ablage fuer diese Metadaten vor.
- `ims.api.metadata_import` kann lokale JSON-Metadaten kontrolliert in diese Ablage importieren.
- `ims.api.metadata_import_cli` macht diesen Importpfad lokal pruefbar, als Preview zusammenfassbar und als Snapshot lesend exportierbar, ohne HTTP- oder UI-Schreibpfade zu oeffnen.
- `ims.api.workbench_diagnostics` prueft lokale Startbedingungen als CLI-Diagnose, ohne einen Server dauerhaft zu starten.
- `ims.api.workbench_start_plan` beschreibt den lokalen Start aus Defaults oder Konfiguration, startet aber keinen Server.
- `ims.api.workbench_cli_overview` listet lokale Workbench-CLI-Befehle und ihre Grenzen, fuehrt aber keinen davon aus.
- Die gebaute Vite-Anwendung aus `frontend/dist` wird lokal ueber `/` und `/assets` ausgeliefert.
- `frontend/` enthaelt eine Vite/React/TypeScript-Oberflaeche mit einer ruhigen Dashboard-Ansicht, die Listen- und Detailmetadaten liest.
- `python_port[dev]` enthaelt die Web-Testabhaengigkeiten, damit die Standardtests die API-Tests ohne separate manuelle Web-Installation sammeln koennen.

## Grenzen

- Keine Steuerung echter Fachlogiklaeufe.
- Keine Aenderung am Simulationskern.
- Keine neue historische Validierungsbehauptung.
- Keine Behauptung historischer Vollgleichheit.
- SQLite wird aktuell nur als lesende, deterministisch geseedete Repository-Schicht an der API genutzt.
- Interne Repository-Schreibmethoden sind vorbereitet und validiert, aber nicht als API- oder UI-Schreibpfade freigeschaltet.
- Der lokale Importpfad ist eine Python-Adapterfunktion, kein HTTP- oder UI-Schreibpfad.
- Der lokale CLI-Adapter schreibt nur im `import`-Modus und nur, wenn ein SQLite-Zielpfad explizit angegeben wird.
- Der lokale CLI-Preview-Modus schreibt keine Metadaten und nutzt `IMS_METADATA_DB` nicht als implizites Ziel.
- Der lokale CLI-Snapshot-Modus liest nur Metadaten und nutzt `IMS_METADATA_DB` nicht als implizite Quelle. Explizite SQLite-Snapshots werden read-only geoeffnet und beruecksichtigen den aktuellen WAL-Zustand.
- Die lokale Startdiagnose schreibt keine Metadaten, startet keine Simulation und erzeugt keine SQLite-Datei fuer fehlende explizite DB-Pfade.
- Der lokale Startplan ist rein beschreibend. Er gibt empfohlene Kommandos und aufgeloeste Pfade aus, startet aber keinen Server und erzeugt keine Dateien.
- Die lokale CLI-Uebersicht ist rein beschreibend. Sie startet keinen Adapter, liest keinen Snapshot, importiert keine Metadaten und erzeugt keine SQLite-Datei.
- Die Frontend-Detailansicht ist rein lesend und nutzt nur die Detail-Endpunkte.
- Die Szenario-Uebersicht ist rein lesend und enthaelt keine Start-, Upload- oder Editierkontrollen.
- Die Szenariofilter arbeiten nur auf bereits gelesenen Metadaten im Browser und oeffnen keinen API- oder Schreibpfad.
- Die Run-Uebersicht ist rein lesend und enthaelt keine Start- oder Editierkontrollen.
- Die Runfilter arbeiten nur auf bereits gelesenen Metadaten im Browser und oeffnen keinen API- oder Schreibpfad.
- Die Metadatenquellen-Anzeige ist reine Betriebsdiagnose und oeffnet keine Persistenz- oder Ausfuehrungspfade.
- Die Betriebsdiagnose buendelt vorhandene Statusendpunkte, startet aber keine Laeufe und schreibt keine Daten.
- Die Metadaten-Konsistenzdiagnose ist rein lesend und repariert, importiert oder schreibt keine Metadaten.
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

Die Uebersicht kann clientseitig nach Anzeigename oder ID suchen und nach Status, Quelle sowie fachlichem Umfang filtern. Die Filter verwenden ausschliesslich die bereits gelesenen Szenario-Metadaten aus `/api/scenarios`; es gibt dafuer keinen neuen API-Endpunkt und keinen Schreibpfad. Wenn kein Treffer uebrig bleibt, zeigt die Workbench einen knappen leeren Zustand.

Die Ausfuehrungsgrenze kommt aus `/api/metadata/capabilities` und bleibt als gesperrt sichtbar. Die Uebersicht bietet keine Start-Schaltflaeche, keinen Editor, keinen Upload und keinen Schreibpfad.

## Run-Uebersicht

Die Workbench zeigt die vorhandenen Run-Metadaten in einer kompakten Uebersicht. Sie nutzt weiterhin nur die bestehenden Listen- und Detaildaten aus `/api/runs` und `/api/runs/{run_id}` sowie bereits geladene Szenario-Metadaten fuer Anzeigenamen. Sichtbar sind Run-Anzeigename, Status, Szenario-Bezug, Periodenfenster, Quelle und die Ausfuehrungsgrenze.

Die Uebersicht kann clientseitig nach Anzeigename oder ID suchen und nach Status, Szenario sowie Quelle filtern. Die Filter verwenden ausschliesslich die bereits gelesenen Run-Metadaten aus `/api/runs` und Szenario-Anzeigenamen aus `/api/scenarios`; es gibt dafuer keinen neuen API-Endpunkt und keinen Schreibpfad. Wenn kein Treffer uebrig bleibt, zeigt die Workbench einen knappen leeren Zustand.

Wenn ein Run ausgewaehlt wird, setzt die Workbench auch das zugehoerige Szenario aus `scenario_id` als Auswahl. Dadurch bleibt die lesende Detailansicht konsistent, auch wenn die Metadaten Runs aus mehreren Szenarien enthalten.

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

## Metadaten-Konsistenz

`/api/metadata/consistency` liefert eine stabile, rein lesende Diagnoseform fuer die aktuell geladenen Szenario- und Run-Metadaten. Der Endpunkt nutzt die bestehenden Repository-Listen und Capabilities und startet keine Simulation.

Die Antwort enthaelt:

- Anzahl Szenarien und Runs.
- Anzahl Runs mit bekannter Szenario-Referenz.
- Run-IDs mit fehlender Szenario-Referenz.
- Run-IDs mit `execution_enabled = true`.
- Status der Schreib- und Simulationsgrenzen.
- `issue_count` und einen einfachen Status `ok` oder `warning`.

Die Workbench stellt diese Werte als kompakte Diagnose dar. Warnungen sind Hinweise auf Metadatenform oder Betriebsgrenzen; sie oeffnen keinen Reparaturdialog, keinen Import, keinen Editor und keinen Schreibpfad.

## Smoke-Tests

Die Workbench-Shell ist mit kleinen Smoke-Tests abgesichert:

- API-Health muss erreichbar sein.
- Version, Metadatenquelle und Capabilities muessen gemeinsam lesbar sein.
- Die Metadaten-Konsistenz muss lesbar sein und fuer Seed-Daten keine offenen Hinweise melden.
- Szenario- und Run-Listen muessen lesbar sein.
- Szenario- und Run-Details muessen fuer IDs aus den Listen lesbar sein.
- Fehlende Metadaten-IDs muessen die stabile `metadata_not_found`-Fehlerform liefern.
- Eine gebaute Frontend-Struktur aus `index.html` und `/assets` muss statisch ausgeliefert werden.
- Die Frontend-Shell muss die Detail-, Importvorschau- und Betriebsdiagnose-Vertraege im Quelltext enthalten.
- Die Szenario-Uebersicht muss Szenario-Daten weiterhin lesend darstellen und die globale Ausfuehrungsgrenze als gesperrt behandeln.
- Die Szenariofilter muessen als clientseitige, lesende Filter in der Frontend-Shell deklariert sein.
- Die Run-Uebersicht muss Run-Daten weiterhin lesend darstellen und `execution_enabled` als gesperrte Grenze behandeln.
- Die Runfilter muessen als clientseitige, lesende Filter in der Frontend-Shell deklariert sein.

Das ist bewusst kein vollstaendiger Browser-End-to-End-Test. Interaktion, Layout und echte Browserereignisse werden weiterhin lokal ueber die Vorschau geprueft; der automatisierte Smoke-Test bleibt ohne zusaetzliche Browser-Testabhaengigkeiten.

## Betriebsdiagnose

Die Workbench zeigt eine kompakte Betriebsdiagnose aus bestehenden Endpunkten:

- `/api/health` fuer Backend-Status und gebautes Frontend.
- `/api/version` fuer Name und Version der Workbench-Shell.
- `/api/metadata/source` fuer die aktuelle Metadatenquelle.
- `/api/metadata/capabilities` fuer gesperrte Schreib- und Ausfuehrungsgrenzen.

Diese Diagnose ist rein lesend. Sie bestaetigt, dass Schreibpfade, Simulation und Browser-Import weiter gesperrt sind, und verweist fuer den Import nur auf den lokalen CLI-Adapter. Sie ist kein Editor, kein Upload-Workflow und kein Startpunkt fuer echte Simulationen.

## Lokale Startdiagnose

Der lokale Diagnoseadapter prueft Startbedingungen, ohne einen Server dauerhaft zu starten:

```powershell
python -m ims.api.workbench_diagnostics
```

Optional kann ein expliziter SQLite-Metadatenpfad geprueft werden:

```powershell
python -m ims.api.workbench_diagnostics --db .\.ims_workbench\metadata.sqlite
```

Alternativ kann die Diagnose eine explizite lokale Konfigurationsdatei lesen:

```powershell
python -m ims.api.workbench_diagnostics --config .\workbench.local.json
```

Die Ausgabe ist eine stabile JSON-Zeile mit `status`, `mode = "diagnostics"`, Importierbarkeit der API, verfuegbaren Web-Abhaengigkeiten, Frontend-Build-Status, Metadatenquelle, gesperrten Schreib- und Ausfuehrungsgrenzen sowie `issues`. Die Web-Abhaengigkeiten umfassen die lokale ASGI-Startbasis inklusive `uvicorn`, weil das dokumentierte Startkommando darueber laeuft. Fehlende Frontend-Builds oder fehlende explizite SQLite-Dateien werden als Diagnosehinweise gemeldet. Der Adapter initialisiert keine Datenbank, migriert keine Metadaten, oeffnet keinen HTTP-Endpunkt und startet keine Simulation.

## Lokaler Startplan

Der lokale Startplan fasst dieselben Konfigurationswerte beschreibend zusammen und gibt ein empfohlenes Startkommando sowie ein passendes Diagnosekommando als JSON aus:

```powershell
python -m ims.api.workbench_start_plan
```

Mit expliziter Konfigurationsdatei:

```powershell
python -m ims.api.workbench_start_plan --config .\workbench.local.json
```

Die Ausgabe enthaelt `status`, `mode = "start_plan"`, `host`, `port`, `frontend_dist`, `metadata_db`, `recommended_command`, `diagnostics_command`, gesperrte Schreib- und Ausfuehrungsgrenzen sowie `issues`. Fehlende `frontend_dist`-Werte in der Konfigurationsdatei verwenden denselben repo-relativen Default wie die Startdiagnose. Explizite relative `frontend_dist`- und `metadata_db`-Pfade werden relativ zur Konfigurationsdatei aufgeloest.

Der Startplan startet keinen Server, erzeugt keine Konfigurationsdatei, initialisiert keine SQLite-Datei, migriert keine Metadaten, oeffnet keinen HTTP-Endpunkt und startet keine Simulation. Er ist eine lesende Orientierung fuer lokale Startwerkzeuge und Betriebssupport, nicht der eigentliche Workbench-Start.

## Lokale CLI-Uebersicht

Die lokale CLI-Uebersicht buendelt die vorhandenen Workbench-Befehle und ihre Grenzen in einer stabilen JSON-Form:

```powershell
python -m ims.api.workbench_cli_overview
```

Die Ausgabe enthaelt `status`, `mode = "cli_overview"`, `commands`, `boundaries` und `rest_plan`. Aufgefuehrt werden:

- `workbench_diagnostics`
- `workbench_start_plan`
- `metadata_import_cli check`
- `metadata_import_cli preview`
- `metadata_import_cli snapshot`
- `metadata_import_cli import --db`

Die Uebersicht fuehrt diese Befehle nicht aus. Sie startet keinen Server, liest keinen Snapshot, importiert keine Metadaten, erzeugt keine SQLite-Datei und startet keine Simulation. Nur der bereits bestehende Importpfad `metadata_import_cli import --db` ist als schreibender Befehl markiert; alle anderen aufgefuehrten Kommandos bleiben lesend oder rein beschreibend.

Die Restplanung in dieser Uebersicht ist bewusst grob: erwartet bleiben derzeit etwa 12-18 reviewbare PRs bis zur lokalen Workbench-v1 fuer Backend und Frontend. Naechste Bloecke sind lokale Start-/Konfigurationsnutzung, lesende Szenario-/Run-Arbeitsflaechen, kontrollierte lokale Schreibpfade, eine spaetere Run-Steuerungsgrenze ohne echte Simulation sowie v1-Haertung mit Doku und Smoke-/Preview-Checks. Fachvalidierung und historische Vollgleichheit bleiben separate spaetere Bloecke.

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

## Lokaler Start

Der lokale Standardablauf ist bewusst kurz und reproduzierbar:

```powershell
python -m pip install -e .\python_port[dev]
cd frontend
npm.cmd install
npm.cmd run build
cd ..
python -m ims.api.workbench_diagnostics --frontend-dist frontend/dist
python -m ims.api.workbench_start_plan
python -m uvicorn ims.api.app:app --app-dir python_port --host 127.0.0.1 --port 8000
```

Danach ist die Workbench unter `http://127.0.0.1:8000/` erreichbar. Optional kann vor dem Start eine explizite Metadatenquelle fuer die Diagnose angegeben werden:

```powershell
python -m ims.api.workbench_diagnostics --frontend-dist frontend/dist --db .\.ims_workbench\metadata.sqlite
```

Die Diagnose ist ein Preflight fuer lokale Betriebsbedingungen. Sie ist kein Serverstart, kein Import und kein Schreibpfad.

## Lokale Konfiguration

Eine lokale JSON-Konfigurationsdatei kann zentrale Betriebswerte beschreibend buendeln. Sie wird nur gelesen, wenn sie explizit uebergeben wird; die Workbench erzeugt keine Konfigurationsdatei automatisch.

Beispiel:

```json
{
  "host": "127.0.0.1",
  "port": 8000,
  "frontend_dist": "frontend/dist",
  "metadata_db": ".ims_workbench/metadata.sqlite"
}
```

Ohne Datei gelten die Defaults `host = "127.0.0.1"`, `port = 8000`, `frontend_dist = "frontend/dist"` und `metadata_db = null`. Fehlt `frontend_dist` in einer explizit uebergebenen Konfigurationsdatei, nutzt die Diagnose denselben repo-relativen Frontend-Default wie ohne Konfiguration. Explizit gesetzte relative Pfade in `frontend_dist` und `metadata_db` werden relativ zum Speicherort der Konfigurationsdatei aufgeloest, damit der Diagnosebefehl auch aus einem anderen Arbeitsverzeichnis stabil bleibt.

Die Felder `host`, `port`, `frontend_dist` und `metadata_db` sind die gesamte aktuelle Konfigurationsflaeche; unbekannte Felder werden abgelehnt, damit Tippfehler nicht still ignoriert werden. `metadata_db` bleibt optional. Ein fehlender expliziter DB-Pfad wird als Diagnosehinweis gemeldet, aber nicht angelegt.

Die Konfigurationsdatei ersetzt die bestehenden Umgebungsvariablen nicht. `IMS_METADATA_DB` und `IMS_FRONTEND_DIST` bleiben fuer den eigentlichen Backend-Start verfuegbar. Die lokale Konfiguration bereitet zunaechst nur eine explizite, testbare Grenze fuer Diagnose und spaetere Startwerkzeuge vor.

## Lokale CLI-Grenzen

Die lokalen CLI-Kommandos sind absichtlich getrennt:

| Kommando | Zweck | Schreibverhalten |
| --- | --- | --- |
| `python -m ims.api.workbench_diagnostics --frontend-dist frontend/dist` | Startbedingungen pruefen | schreibt nicht |
| `python -m ims.api.workbench_diagnostics --config .\workbench.local.json` | Startbedingungen aus expliziter Konfiguration pruefen | schreibt nicht |
| `python -m ims.api.workbench_start_plan --config .\workbench.local.json` | Lokalen Start beschreibend zusammenfassen | schreibt nicht |
| `python -m ims.api.workbench_cli_overview` | Lokale Workbench-CLI-Befehle und Grenzen auflisten | schreibt nicht |
| `python -m ims.api.metadata_import_cli check .\metadata_import.json` | Importformat knapp validieren | schreibt nicht |
| `python -m ims.api.metadata_import_cli preview .\metadata_import.json` | Importdatei zusammenfassen und Konsistenzhinweise zeigen | schreibt nicht |
| `python -m ims.api.metadata_import_cli snapshot` | geseedete In-Memory-Metadaten als Diagnose lesen | schreibt nicht |
| `python -m ims.api.metadata_import_cli snapshot --db .\.ims_workbench\metadata.sqlite` | explizite SQLite-Metadaten read-only lesen | schreibt nicht |
| `python -m ims.api.metadata_import_cli import .\metadata_import.json --db .\.ims_workbench\metadata.sqlite` | validierte Metadaten lokal importieren | schreibt nur in den expliziten DB-Pfad |

Keines dieser Kommandos startet eine Simulation. Es gibt weiterhin keinen HTTP-Schreibpfad, keinen Browser-Upload und keinen Szenario-Editor.

## Lokaler Metadatenimport

`ims.api.metadata_import` definiert einen kleinen Importpfad fuer lokale JSON-Dateien. Der Import schreibt nur in die SQLite-Metadatenablage und verwendet die bestehenden Repository-Upserts. Er startet keine Simulation und veraendert keine Fachlogik.

Die Workbench zeigt das erwartete Importformat als lesende Vorschau. Sie erklaert die Top-Level-Felder `schema_version`, `scenarios` und `runs`, verweist auf den Python-Adapter und haelt sichtbar fest, dass `execution_enabled` weiter `false` bleiben muss. Es gibt keinen File-Upload, keinen Browser-Editor und keinen HTTP-Schreibpfad.

Die Vorschau verweist zusaetzlich auf die lokale Startdiagnose. Diese bleibt ein CLI-Adapter und ist kein Browser-Export, kein Startbutton und kein Schreibpfad.

Der lokale CLI-Adapter kann dieselbe Datei zuerst nur pruefen:

```powershell
python -m ims.api.metadata_import_cli check .\metadata_import.json
```

Eine ausfuehrlichere lokale Vorschau liefert dieselben Grunddaten plus neue/bekannte IDs und Konsistenzhinweise, schreibt aber ebenfalls nicht:

```powershell
python -m ims.api.metadata_import_cli preview .\metadata_import.json
```

Ein lokaler Snapshot gibt die aktuell lesbaren Workbench-Metadaten als Diagnoseartefakt aus. Ohne `--db` nutzt der Befehl die geseedeten In-Memory-Metadaten:

```powershell
python -m ims.api.metadata_import_cli snapshot
```

Mit expliziter SQLite-Datei liest der Befehl nur diese Datei:

```powershell
python -m ims.api.metadata_import_cli snapshot --db .\.ims_workbench\metadata.sqlite
```

Der explizite Snapshot-Pfad oeffnet die SQLite-Datei read-only. Er initialisiert oder migriert keine Datenbank und schreibt keine Workbench-Metadaten. SQLite-WAL-/SHM-Dateien koennen bei einer Live-WAL-Datenbank vorhanden sein; sie bedeuten keinen Import- oder Snapshot-Schreibpfad. Fehlt die Datei oder ist sie keine lesbare Workbench-SQLite-Ablage, liefert der CLI-Adapter eine stabile JSON-Fehlerform.

Ein Import schreibt nur in eine ausdruecklich angegebene SQLite-Datei:

```powershell
python -m ims.api.metadata_import_cli import .\metadata_import.json --db .\.ims_workbench\metadata.sqlite
```

Die Ausgabe ist eine knappe JSON-Statuszeile. Fehler liefern ebenfalls eine stabile JSON-Form mit `status = "error"` und einer kurzen Meldung. Der Preview-Modus liefert zusaetzlich `existing_scenario_ids`, `existing_run_ids`, `new_scenario_ids`, `new_run_ids`, `runs_with_missing_scenario`, `runs_with_execution_enabled` und `writes_performed = false`. Der Snapshot-Modus liefert `source`, `scenarios`, `runs`, `consistency`, `writes_performed = false` und `execution_performed = false`. Er exportiert keine Fachlogikdaten, startet keine Simulation und nutzt eine read-only Verbindung fuer explizite Snapshot-Datenbanken, damit auch committed Live-WAL-Metadaten sichtbar bleiben. Der Adapter liest weder `IMS_METADATA_DB` als implizites Schreibziel noch oeffnet er einen HTTP-Endpunkt. Die API- und UI-Schreibpfade bleiben gesperrt.

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

## Anschluss

Der naechste Modernisierungsschritt kann die lokale Metadatenablage sichtbarer machen, etwa durch eine lesende Anzeige der aktiven SQLite-Quelle und der Import-/Seed-Herkunft. Schreibende API- oder UI-Pfade sollten weiterhin separat und explizit entworfen werden. Dabei sollte die bestehende DTO-Grenze erhalten bleiben, ohne den Fachlogikkern direkt mit UI-Zustaenden zu vermischen.
