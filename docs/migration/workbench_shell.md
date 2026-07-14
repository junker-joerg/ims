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
- `/api/run-control/queue` beschreibt lesend vorhandene lokale Run-Control-Queue-Eintraege, ohne die Queue zu initialisieren oder zu schreiben.
- `POST /api/run-control/queue` merkt einen per Dry-Run validierten Run-Control-Request in einer expliziten SQLite-Queue vor, ohne Ausfuehrung.
- `/api/run-control/queue/action-plan` leitet lesend naechste Queue-Schritte ab, ohne Queue, Metadaten oder Simulation zu schreiben.
- `/api/run-control/queue/{queue_id}` liefert einen einzelnen Queue-Eintrag lesend per ID.
- `/api/run-control/request-contract` beschreibt lesend den Run-Control-Request-Vertrag, ohne Request-Body, Upload oder Schreiben.
- `/api/run-control/dry-run-contract` beschreibt den Run-Control-Dry-Run-Vertrag fuer eine HTTP-Pruefung ohne Schreiben oder Ausfuehrung.
- `/api/run-control/dry-run` prueft ein Run-Control-Request-DTO gegen Request-Vertrag und Preflight, ohne Queue, Metadaten oder Simulation zu schreiben.
- `/api/run-control/preflight/{run_id}` prueft den ausgewaehlten Run lesend gegen die gesperrte Run-Control-Grenze.
- `/api/core-validation/overview` beschreibt lesend den IMS-Kernvalidierungsueberblick, Legacy-Abdeckung und den Execution-Summary-Vertrag, ohne einen Runner zu starten.
- `/api/core-validation/carryover-probe-contract` beschreibt lesend den API-Vertrag fuer spaeter bereits berechnete Carryover-Probe-Payloads, ohne Payload-Upload oder Probe-Start.
- `/api/run-control/adapter-result-contract` beschreibt lesend den API-Vertrag fuer spaeter bereits lokal gepruefte Adapter-Resultate, ohne Payload-Upload, HTTP-Validierung oder Adapterstart.
- `/api/run-control/adapter-start-contract` beschreibt lesend den API-Startvertrag fuer einen spaeteren kontrollierten Adapterstart, ohne Start-Payload, POST-Start, UI-Button, Queue-Worker oder Simulation.
- `/api/run-control/core-diagnostics-bridge` buendelt lesend Queue-Aktionsplan und Kernvalidierungsueberblick, ohne Queue, Metadaten, Runner oder Simulation zu schreiben.
- Die Workbench buendelt Health, Version, Capabilities und Metadatenquelle in einer kleinen lesenden Betriebsdiagnose.
- Die Workbench zeigt die Metadaten-Konsistenz als kleine Diagnose ohne Reparaturpfade.
- Die Workbench zeigt die aktuelle Szenario-/Run-Auswahl in einer kompakten, rein lesenden Auswahlzusammenfassung.
- Die Workbench zeigt Szenario-Metadaten zusaetzlich in einer scanbaren, rein lesenden Uebersicht.
- Die Szenario-Uebersicht enthaelt clientseitige Filter fuer Suche, Status, Quelle und Umfang.
- Die Workbench zeigt Run-Metadaten zusaetzlich in einer scanbaren, rein lesenden Uebersicht.
- Die Run-Uebersicht enthaelt clientseitige Filter fuer Suche, Status, Szenario und Quelle.
- Die Workbench zeigt ein kompaktes Run-Control-Statusband sowie eine Uebersicht fuer vorhandene Queue-Metadaten und gesperrte Ausfuehrungsgrenzen.
- Die Workbench zeigt einen read-only Kernvalidierungsueberblick mit Execution-Summary-Vertrag, ohne Summary-Upload, Formular oder Laufstart.
- Die Workbench zeigt den Carryover-Probe-Vertrag als read-only Karte, ohne Probe-Upload, Probe-Start oder Ausfuehrungsadapter.
- Die Workbench zeigt den Adapter-Resultat-Vertrag als read-only Karte, ohne Resultat-Upload, HTTP-Validierung, Dateiauswahl oder Adapterstart.
- Der Adapter-Startvertrag ist nur ein API-DTO-Vertrag; die Workbench zeigt noch keinen Startbutton.
- `ims.api.metadata_repository` bereitet eine lokale SQLite-Ablage fuer diese Metadaten vor.
- `ims.api.metadata_import` kann lokale JSON-Metadaten kontrolliert in diese Ablage importieren.
- `ims.api.metadata_import_cli` macht diesen Importpfad lokal pruefbar, als Preview zusammenfassbar, als Dry-Run vorab vergleichbar, als Snapshot lesbar und im Importformat exportierbar, ohne HTTP- oder UI-Schreibpfade zu oeffnen.
- `ims.api.metadata_write_contracts` beschreibt die vorbereiteten lokalen Schreibgrenzen, ohne selbst zu schreiben.
- `ims.api.core_validation_carryover_probe_contract` beschreibt den read-only API-Vertrag fuer vorab berechnete Carryover-Probe-Ergebnisse, ohne den Probe zu starten.
- `ims.api.run_control_contracts` beschreibt die spaetere Run-Steuerungsgrenze, ohne Ausfuehrung zu erlauben.
- `ims.api.run_control_requests` validiert lokale Run-Control-Request-DTOs, ohne Ausfuehrung zu erlauben.
- `ims.api.run_control_queue` speichert validierte Run-Control-Requests lokal in einer expliziten SQLite-Queue, ohne Ausfuehrung zu erlauben.
- `ims.api.run_control_preflight` prueft vorhandene Run-Metadaten lokal gegen diese gesperrte Steuerungsgrenze, ohne Ausfuehrung zu erlauben.
- `ims.api.workbench_diagnostics` prueft lokale Startbedingungen als CLI-Diagnose, ohne einen Server dauerhaft zu starten.
- `ims.api.workbench_start_plan` beschreibt den lokalen Start aus Defaults oder Konfiguration, startet aber keinen Server.
- `ims.api.workbench_readiness` buendelt lokale v1-Bereitschaft aus Diagnose, Metadatenquelle, CLI-Grenzen, Run-Control-Preflight und optionaler Run-Control-Queue-Diagnose, ohne den Server zu starten.
- `ims.api.workbench_portable_readiness` prueft die heutige Repo-Struktur oder eine spaetere portable Workbench-Ordnerstruktur, ohne Dateien zu erzeugen.
- `ims.api.workbench_build_snapshot` fasst vorhandene lokale Build-Artefakte zusammen, ohne Dateien zu kopieren oder ein ZIP zu erzeugen.
- `ims.api.workbench_artifact_manifest` beschreibt Ein- und Ausschlusspfade fuer ein spaeteres portables Artefakt, ohne Dateien zu kopieren oder ein ZIP zu erzeugen.
- `ims.api.workbench_bundle_plan` plant ein spaeteres lokales Workbench-Bundle auf Basis des Artefaktmanifests, ohne Dateien zu kopieren oder ein ZIP zu erzeugen.
- `ims.api.workbench_bundle_build` erzeugt nur bei explizitem `--out` ein lokales ZIP aus dem Bundle-Plan.
- `ims.api.workbench_bundle_smoke` prueft ein erzeugtes ZIP auf erwartete Eintraege, Ausschluesse, stabile Metadaten und lesbare Payloads.
- `ims.api.workbench_portable_staging` staged ein geprueftes ZIP in eine portable Zielstruktur.
- `ims.api.workbench_portable_staging_smoke` prueft eine gestagte portable Zielstruktur und ihre Startskriptgrenzen rein lesend.
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
- Der lokale Schreibvertrag ist rein beschreibend. Er oeffnet keinen HTTP- oder UI-Schreibpfad und erzeugt keine SQLite-Datei.
- Der lokale Run-Control-Vertrag ist rein beschreibend. Er startet keinen Lauf und schaltet keine API- oder UI-Steuerung frei.
- Der Run-Control-Dry-Run-Vertrag erlaubt nur den kontrollierten HTTP-Pruefpfad `POST /api/run-control/dry-run`. Dieser Request-Body muss dem Run-Control-Request-DTO entsprechen und `execution_enabled=false` setzen; Queue-Schreiben, Metadatenschreiben, Upload, PUT und Ausfuehrung bleiben gesperrt.
- Die lokale Run-Control-Queue schreibt nur ueber explizite CLI-Befehle mit `--db`. Sie startet keine Simulation, keinen Worker und keinen Scheduler.
- Der lokale Run-Control-Preflight ist rein lesend. Er prueft Run- und Szenario-Metadaten, startet aber keine Simulation und schreibt keine Metadaten.
- Die lokale Startdiagnose schreibt keine Metadaten, startet keine Simulation und erzeugt keine SQLite-Datei fuer fehlende explizite DB-Pfade.
- Der lokale Startplan ist rein beschreibend. Er gibt empfohlene Kommandos und aufgeloeste Pfade aus, startet aber keinen Server und erzeugt keine Dateien.
- Die lokale Readiness-Pruefung ist rein beschreibend. Sie startet keinen Server, baut kein Frontend, schreibt keine Metadaten und startet keine Simulation. Bei expliziter SQLite-Quelle bezieht sie die Run-Control-Queue-Diagnose als eigenen Bereitschaftsbereich ein, ohne die Queue zu initialisieren.
- Die lokale portable Strukturpruefung ist rein beschreibend. Sie erkennt Repo- und portable Zielstruktur, erzeugt aber keine fehlenden Ordner, keine SQLite-Datei und kein Release-Artefakt.
- Der lokale Build-Snapshot ist rein beschreibend. Er zaehlt vorhandene Frontend-Dist-Dateien und prueft lokale App-/Skriptpfade, kopiert aber keine Dateien und erzeugt kein ZIP.
- Das lokale Artefaktmanifest ist rein beschreibend. Es listet geplante Einschlusspfade und ausgeschlossene lokale Daten/Caches, kopiert aber keine Dateien und erzeugt kein ZIP.
- Der lokale Bundle-Trockenlauf ist rein beschreibend. Er nutzt das Artefaktmanifest als Dateiliste und Checksummengrundlage, kopiert aber keine Dateien und erzeugt kein ZIP.
- Der lokale ZIP-Build schreibt nur in einen expliziten `--out`-Pfad. Er startet keine Simulation und ist kein Installer, kein Release-Tag und kein fachlicher Gleichheitsnachweis.
- Die lokale CLI-Uebersicht ist rein beschreibend. Sie startet keinen Adapter, liest keinen Snapshot, importiert keine Metadaten und erzeugt keine SQLite-Datei.
- Die Frontend-Detailansicht ist rein lesend und nutzt nur die Detail-Endpunkte.
- Die Auswahlzusammenfassung ist rein lesend und fuehrt keine Start-, Schreib-, Import- oder Editieraktion aus.
- Die Szenario-Uebersicht ist rein lesend und enthaelt keine Start-, Upload- oder Editierkontrollen.
- Die Szenariofilter arbeiten nur auf bereits gelesenen Metadaten im Browser und oeffnen keinen API- oder Schreibpfad.
- Die Run-Uebersicht ist rein lesend und enthaelt keine Start- oder Editierkontrollen.
- Die Runfilter arbeiten nur auf bereits gelesenen Metadaten im Browser und oeffnen keinen API- oder Schreibpfad.
- Das Run-Control-Statusband ist rein lesend. Es fasst Queue, Preflight, Request-Vertrag, Dry-Run-Vertrag, Schreibpfade und Ausfuehrungsgrenze aus den bereits gelesenen Antworten zusammen und oeffnet keinen eigenen API-, Start- oder Schreibpfad.
- Die Run-Control-Uebersicht nutzt `/api/run-control/queue` lesend und zeigt vorhandene Queue-Eintraege, clientseitige Queue-Filter, Hinweise und gesperrte Ausfuehrungsgrenzen. Queue-Schreiben ist nur ueber den getrennten Vormerkpfad nach erfolgreichem Dry-Run und mit expliziter SQLite-Quelle erlaubt; es startet keinen Lauf und enthaelt keinen Startbutton.
- Die Run-Control-Request-Vertragskarte ist rein lesend. Sie nutzt `/api/run-control/request-contract`, zeigt Pflichtfelder, optionale Felder, verbotene Felder und ein Beispiel-DTO, validiert aber keinen Browser-Request und oeffnet keinen Upload- oder Schreibpfad.
- Die Run-Control-Dry-Run-Karte zeigt den Vertrag und kann fuer den ausgewaehlten Run `POST /api/run-control/dry-run` als reine Pruefung ausloesen. Nach einem passenden Dry-Run kann sie denselben Request ueber `POST /api/run-control/queue` in einer expliziten SQLite-Queue vormerken. Diese Vormerkung schreibt nur Queue-Metadaten, startet keine Simulation und enthaelt keinen Upload, Editor oder Startbutton.
- Die Run-Control-Aktionsplankarte nutzt `/api/run-control/queue/action-plan` und zeigt fuer vorhandene Queue-Eintraege nur `run_preflight`, `await_execution_release`, `resolve_blockers` oder `inspect_queue_status`. Sie schreibt nicht und startet keinen Adapter.
- Die Run-Control-Preflight-Karte ist rein lesend. Sie nutzt `/api/run-control/preflight/{run_id}` fuer den aktuell ausgewaehlten Run, zeigt Run-/Szenario-Bezug, Hinweise und gesperrte Ausfuehrungsgrenzen, startet aber keinen Lauf und schreibt keine Metadaten.
- Die Kernvalidierungsuebersicht ist rein lesend. Sie nutzt `/api/core-validation/overview`, zeigt Periodenplaene, Legacy-Referenzen und den Execution-Summary-Vertrag, startet aber keinen expliziten Periodenrunner und nimmt keine Summary-Datei entgegen.
- Die Carryover-Probe-Vertragskarte ist rein lesend. Sie nutzt `/api/core-validation/carryover-probe-contract`, beschreibt nur vorab berechnete `explicit_transition_carryover_probe`-Payloads, nimmt keinen Payload entgegen und startet keinen Probe.
- Die Adapter-Resultat-Vertragskarte ist rein lesend. Sie nutzt `/api/run-control/adapter-result-contract`, beschreibt nur vorab lokal gepruefte `controlled_execution_adapter`-Resultate, nimmt keinen Payload entgegen, validiert kein Resultat ueber HTTP und startet keinen Adapter.
- Der Adapter-Startvertrag ist rein lesend. Er nutzt `/api/run-control/adapter-start-contract`, beschreibt nur den spaeteren Startrequest, nimmt keinen Payload entgegen, validiert keinen Start-Payload ueber HTTP und stellt keinen `POST /api/run-control/adapter-start` bereit.
- Die Run-Control-Kernblick-Bruecke ist rein lesend. Sie nutzt `/api/run-control/core-diagnostics-bridge`, kombiniert nur vorhandene Queue-Aktionsplan- und Kernvalidierungssignale, schreibt nicht, startet keinen Runner und enthaelt keinen Startbutton.
- Die Metadatenquellen-Anzeige ist reine Betriebsdiagnose und oeffnet keine Persistenz- oder Ausfuehrungspfade.
- Die Betriebsdiagnose buendelt vorhandene Statusendpunkte, startet aber keine Laeufe und schreibt keine Daten.
- Die Metadaten-Konsistenzdiagnose ist rein lesend und repariert, importiert oder schreibt keine Metadaten.
- Die Importvorschau ist rein informativ und enthaelt keinen Upload, Editor oder Browser-Schreibpfad.
- Noch keine Schreibendpunkte fuer Szenario- oder Run-Metadaten.

## Lokale Workbench-v1 Ablauf

Der lokale v1-Ablauf ist kurz und reproduzierbar:

```powershell
python -m pip install -e .\python_port[dev]
cd frontend
npm.cmd install
npm.cmd run build
cd ..
python -m ims.api.workbench_diagnostics --frontend-dist frontend/dist
python -m ims.api.workbench_readiness --frontend-dist frontend/dist
python -m ims.api.workbench_portable_readiness --root . --layout repo
python -m ims.api.workbench_build_snapshot --root . --frontend-dist frontend/dist
python -m ims.api.workbench_artifact_manifest --root . --frontend-dist frontend/dist
python -m ims.api.workbench_bundle_plan --root . --frontend-dist frontend/dist
python -m uvicorn ims.api.app:app --app-dir python_port --host 127.0.0.1 --port 8000
```

Danach ist die Workbench unter `http://127.0.0.1:8000/` erreichbar. Diagnose und Readiness sind lokale Vorabpruefungen; sie starten keinen Server, bauen kein Frontend, schreiben keine Metadaten und starten keine Simulation.

Die lokale Bedienreihenfolge fuer v1 ist:

1. Frontend-Abhaengigkeiten installieren und bauen.
2. Startdiagnose ausfuehren.
3. Readiness-Pruefung ausfuehren.
4. Backend lokal starten.
5. Workbench im Browser oeffnen.

Erste lokale Windows-Skripte kapseln diese Bedienung fuer den Packaging-Block:

```powershell
scripts\workbench\check-workbench.cmd
scripts\workbench\start-workbench.cmd
```

`check-workbench.cmd` prueft das vorhandene `frontend/dist`, Startdiagnose und Readiness. Es startet keinen dauerhaften Server, schreibt keine Metadaten und startet keine Simulation. `start-workbench.cmd` startet nur den lokalen Backend-Server auf `127.0.0.1:8000`; es fuehrt keinen Import, keine Queue-Schreiboperation und keinen Run aus.

## Lokaler Workbench-v1 Abschlussstatus

Die lokale Workbench-v1 ist als rein lokale Browser-Workbench und Modernisierungs-Meilenstein abgeschlossen. Dieser Abschluss ist kein Release-Tag, keine Fachvalidierung und keine historische Vollgleichheitsbehauptung. Sie liefert Backend-Health und Version, statische Frontend-Auslieferung, lesende Szenario- und Run-Metadaten, Detailansichten, Filter, Auswahlzusammenfassung, Betriebsdiagnose, Metadatenquelle, Konsistenzdiagnose und Readiness.

Die lokalen CLI-Adapter decken Startdiagnose, Startplan, Readiness, CLI-Uebersicht, Metadaten-Check, Preview, Dry-Run, Export, Roundtrip, Snapshot, expliziten Importbericht, Schreibvertrag, Schreibvertragspruefung, Run-Control-Vertrag, Run-Control-Request-Check, Run-Control-Queue, Run-Control-Queue-Diagnose und Run-Control-Preflight ab. Diese Werkzeuge bleiben lokal und starten keine Simulation. Nur `metadata_import_cli import --db` schreibt Metadaten, `run_control_queue init/enqueue --db` schreibt Queue-Metadaten in eine explizite SQLite-Datei und `metadata_import_cli export --out` schreibt nur in den expliziten JSON-Zielpfad. `run_control_queue list/show --db` und `run_control_queue_diagnostics --db` oeffnen die Queue-Datenbank read-only; die Diagnose prueft Queue-Schema, Statuswerte, Szenario-Referenzen und Ausfuehrungsflags, ohne Metadaten zu schreiben oder eine Simulation zu starten.

Die lokale Demo-Faehigkeit ist in `docs/migration/workbench_demo_checklist.md` als kurze Vorfuehr-Checkliste konsolidiert. Sie beschreibt Startbefehle, UI-Reihenfolge, erwartete Demo-Signale und die Grenze, dass der Browser-Demo-Pfad nur Dry-Run, Queue-Vormerkung und Aktionsplan zeigt.

Nicht enthalten sind weiterhin Fachlogikaenderungen, echte Run-Ausfuehrung, neue HTTP-Endpunkte, HTTP- oder UI-Schreibpfade, Browser-Upload, Browser-Download, funktionaler Run-Start, Szenario-Editor, SQLite-Migration und historische Vollgleichheitsbehauptung.

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

## Auswahlzusammenfassung

Die Workbench buendelt die aktuell ausgewaehlte Szenario-/Run-Kombination in einer kompakten Auswahlzusammenfassung. Sie nutzt nur bereits geladene Listen, zur aktuellen Auswahl passende Detaildaten, Capabilities und die Metadatenquelle. Sichtbar sind ausgewaehltes Szenario, ausgewaehlter Run, Periodenfenster, Metadatenquelle, Schreibgrenze, Ausfuehrungsgrenze und ein Hinweis, ob die Auswahl durch aktive Filter gerade nicht in den Listen sichtbar ist.

Die Auswahlzusammenfassung ist rein lesend. Sie startet keine Simulation, schreibt keine Metadaten, oeffnet keinen Import und ersetzt keinen Szenario-Editor.

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

## Backup und Restore lokaler Metadaten

Die lokale Workbench speichert aktuell nur Workbench-Metadaten in einer expliziten SQLite-Ablage wie `.ims_workbench/metadata.sqlite`. Diese Datei ist lokale Betriebsablage, keine Fachlogikdatenbank und kein historischer Gleichheitsnachweis.

Fuer ein konservatives Backup gilt:

- Workbench vor einem Datei-Backup stoppen.
- `metadata.sqlite` sichern.
- Falls SQLite-WAL aktiv ist, vorhandene `metadata.sqlite-wal` und `metadata.sqlite-shm` bewusst mit behandeln oder vorher einen stabilen Shutdown-/Checkpoint-Pfad nutzen.
- Optional zusaetzlich ein explizites JSON-Bundle erzeugen:

```powershell
python -m ims.api.metadata_import_cli export --db .\.ims_workbench\metadata.sqlite --out .\metadata_export.json
```

Vor und nach einem Restore koennen vorhandene lokale Lesechecks genutzt werden:

```powershell
python -m ims.api.metadata_import_cli snapshot --db .\.ims_workbench\metadata.sqlite
python -m ims.api.metadata_import_cli roundtrip --db .\.ims_workbench\metadata.sqlite
python -m ims.api.workbench_readiness --frontend-dist frontend/dist --db .\.ims_workbench\metadata.sqlite
```

Ein Restore ist aktuell manuell und explizit: Workbench stoppen, bestehende Metadatenquelle sichern oder ersetzen, wiederhergestellte Datei pruefen und erst danach die Workbench neu starten. Es gibt keine automatische Backup-Funktion, keine SQLite-Migration, keinen Updater, keinen HTTP- oder UI-Schreibpfad und keine Simulation. Backup und Restore enthalten keine Fachlogikdaten, keine Simulationsergebnisse und keine historische Vollgleichheitsbehauptung.

## Update und Rollback lokaler Workbench-Versionen

Lokale Workbench-Versionen werden bis auf Weiteres manuell aktualisiert. Eine neue Version soll neben der bisherigen Version in einen eigenen Ordner gelegt werden, nicht direkt ueber eine bestehende Installation. Die Anwendung und die lokalen Metadaten bleiben getrennt: Repo- oder ZIP-Inhalt, `python_port`, `frontend/dist` und Startskripte gehoeren zur Anwendung; `.ims_workbench` enthaelt die lokale Metadatenablage.

Ein konservativer Update-Test trennt alte Datenquelle und neue Anwendung
explizit. Die Werte sind Beispielpfade; wichtig ist, dass `$metadataDb` auf die
bestehende Metadatenquelle zeigt und `$newRoot` auf die neue Workbench-Version:

```powershell
$oldRoot = "C:\ims-workbench-old"
$newRoot = "C:\ims-workbench-new"
$metadataDb = Join-Path $oldRoot ".ims_workbench\metadata.sqlite"
$exportPath = Join-Path $oldRoot "metadata_export.json"

python -m ims.api.metadata_import_cli export --db $metadataDb --out $exportPath
python -m ims.api.workbench_portable_readiness --root $newRoot --layout portable
python -m ims.api.workbench_readiness --frontend-dist (Join-Path $newRoot "app\frontend\dist") --db $metadataDb
python -m ims.api.metadata_import_cli roundtrip --db $metadataDb
```

Die Befehle muessen im Kontext der neuen portablen Workbench-Version ausgefuehrt
werden, damit neuer Backend-/Adaptercode, neues Frontend und bestehende
Metadatenquelle gemeinsam geprueft werden.

Fuer einen Repo-Checkout statt eines portablen Zielordners wird in den neuen
Checkout gewechselt und dessen `python_port` explizit auf `PYTHONPATH` gesetzt,
damit `python -m ...` die neue Version nutzt:

```powershell
Push-Location $newRoot
$env:PYTHONPATH = Join-Path $newRoot "python_port"
python -m ims.api.workbench_portable_readiness --root . --layout repo
python -m ims.api.workbench_readiness --frontend-dist frontend/dist --db $metadataDb
Pop-Location
```

`Push-Location` allein setzt den Python-Modulkontext nicht. Alternativ kann die
neue Version aus `$newRoot\python_port` in die verwendete virtuelle Umgebung
installiert werden. Wichtig ist, dass der Check keinen alten editable install
aus einer bisherigen Workbench-Version nutzt.

Die neue Version wird damit gegen die bestehende Metadatenquelle geprueft. Sie
legt keine frische `.ims_workbench` als Ersatz an und migriert die SQLite-Datei
nicht automatisch.

Rollback heisst: neue Workbench stoppen, alte Version wieder starten und bei Bedarf die zuvor gesicherte Metadatenquelle zuruecklegen. Es gibt keinen automatischen Updater, keine In-place-Aktualisierung, keine automatische SQLite-Migration, keinen Installer, keinen HTTP- oder UI-Schreibpfad und keine Simulation. Update und Rollback enthalten keine Fachlogikdaten, keine Simulationsergebnisse und keine historische Vollgleichheitsbehauptung.

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
- Die Auswahlzusammenfassung muss die aktive Szenario-/Run-Kombination, Filterhinweise und gesperrte Grenzen rein lesend deklarieren.
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
- `workbench_readiness`
- `workbench_portable_readiness`
- `workbench_build_snapshot`
- `workbench_artifact_manifest`
- `metadata_import_cli check`
- `metadata_import_cli preview`
- `metadata_import_cli snapshot`
- `metadata_import_cli export`
- `metadata_import_cli roundtrip`
- `metadata_import_cli dry-run`
- `run_control_contracts`
- `run_control_preflight`
- `metadata_import_cli import --db`

Die Uebersicht fuehrt diese Befehle nicht aus. Sie startet keinen Server, liest keinen Snapshot, importiert keine Metadaten, erzeugt keine SQLite-Datei und startet keine Simulation. Nur der bereits bestehende Importpfad `metadata_import_cli import --db` und der explizite Datei-Export `metadata_import_cli export --out` sind als schreibende Befehle markiert; alle anderen aufgefuehrten Kommandos bleiben lesend oder rein beschreibend.

Die Restplanung in dieser Uebersicht ist bewusst grob: erwartet bleiben derzeit 0 reviewbare PRs bis zur lokalen Workbench-v1 fuer Backend und Frontend. Die lokale Workbench-v1 ist abgeschlossen; Fachvalidierung und historische Vollgleichheit bleiben separate spaetere Bloecke.

## v1-Bereitschaftspruefung

Die lokale Readiness-Pruefung buendelt die bestehenden lokalen Grenzen:

```powershell
python -m ims.api.workbench_readiness --frontend-dist frontend/dist
```

Optional koennen eine explizite SQLite-Metadatenquelle und eine Run-ID fuer den Run-Control-Preflight angegeben werden:

```powershell
python -m ims.api.workbench_readiness --frontend-dist frontend/dist --db .\.ims_workbench\metadata.sqlite --run-id baseline-python-tests
```

Die Ausgabe enthaelt `mode = "workbench_readiness"`, Einzelstatus fuer Backend, Frontend, Metadaten, CLI, Run-Control und Run-Control-Queue, eine `checks`-Liste, `issues`, `writes_enabled = false` und `execution_enabled = false`. Eine fehlende oder unlesbare explizite SQLite-Metadatenquelle setzt `metadata_ready = false`; eine unbekannte Run-ID bleibt dagegen ein Run-Control-Hinweis. Eine nicht initialisierte Queue bleibt zulaessig, unlesbare Queue-Schemas oder aktivierte Ausfuehrungsflags setzen `run_control_queue_ready = false`.

Die Readiness-Pruefung startet keinen Server, baut kein Frontend, erzeugt keine SQLite-Datei, schreibt keine Metadaten, oeffnet keinen HTTP-Endpunkt und startet keine Simulation. Sie ist eine lokale Betriebs- und Härtungspruefung fuer die Workbench-v1, keine Fachvalidierung und keine historische Vollgleichheitsbehauptung.

## Portable Strukturpruefung

Der lokale portable Readiness-Check prueft, ob die fuer den Packaging-Block erwartete Struktur vorhanden ist. Fuer die heutige Repo-Struktur:

```powershell
python -m ims.api.workbench_portable_readiness --root . --layout repo
```

Fuer eine spaetere portable Ordnerstruktur:

```powershell
python -m ims.api.workbench_portable_readiness --root .\ims-workbench --layout portable
```

Die Ausgabe enthaelt `mode = "workbench_portable_readiness"`, den erkannten oder expliziten Layouttyp, Einzelchecks fuer `python_port`, `frontend_dist`, `start_script`, `check_script`, optionale lokale Daten-/Logordner, den erwarteten und tatsaechlichen Pfadtyp, `writes_enabled = false` und `execution_enabled = false`. Der Check erzeugt keine fehlenden Ordner, keine SQLite-Datei, kein ZIP, keinen Installer, oeffnet keinen Schreibpfad und startet keine Simulation.

## Build-Snapshot

Der lokale Build-Snapshot fasst die vorhandenen lokalen Artefakte zusammen:

```powershell
python -m ims.api.workbench_build_snapshot --root . --frontend-dist frontend/dist
```

Die Ausgabe enthaelt `mode = "workbench_build_snapshot"`, den Root-Pfad, den Frontend-Dist-Pfad, `frontend_index_available`, Anzahl und Groesse der vorhandenen Frontend-Dist-Dateien, Verfuegbarkeit von `python_port`, Start-/Check-Skripten, eine Liste bewusst ausgeschlossener lokaler Pfade, `writes_enabled = false` und `execution_enabled = false`.

Der Build-Snapshot baut kein Frontend, kopiert keine Dateien, erzeugt kein Artefaktmanifest, kein ZIP, keinen Installer, keine SQLite-Datei, startet keinen Server und startet keine Simulation. Er ist eine Vorstufe fuer spaetere Artefaktmanifest- und ZIP-Schritte, keine Bereitstellung selbst.

## Artefaktmanifest

Das lokale Artefaktmanifest beschreibt, welche vorhandenen Pfade spaeter in ein portables Workbench-Artefakt aufgenommen werden sollen und welche lokalen Pfade ausgeschlossen bleiben:

```powershell
python -m ims.api.workbench_artifact_manifest --root . --frontend-dist frontend/dist
```

Die Ausgabe enthaelt `mode = "workbench_artifact_manifest"`, `included_paths`, `excluded_paths`, `missing_required_paths`, `files`, `file_count`, `total_bytes`, `writes_enabled = false` und `execution_enabled = false`. Die `files`-Liste ist deterministisch nach relativen Pfaden sortiert und enthaelt pro Datei relativen Pfad, Quellpfad, Groesse und SHA-256-Pruefsumme.

Eingeschlossen werden unter anderem `python_port`, `frontend/dist`, die lokalen Start-/Check-Skripte, die Skript-Doku, README und Workbench-/Packaging-Doku. Ausgeschlossen bleiben lokale Daten und Caches wie `.git`, `.ims_workbench`, `logs`, `frontend/node_modules`, `frontend/.npm-cache`, Python-/Test-Caches und lokale SQLite-Dateien.

Das Artefaktmanifest schreibt keine Datei, kopiert keine Dateien, erzeugt kein ZIP, keinen Installer, keine SQLite-Datei, oeffnet keinen Schreibpfad und startet keine Simulation. Es ist nur die naechste pruefbare Grenze vor spaeteren ZIP-/Release-Schritten; die Checksummen dienen diesen spaeteren Smoke- und Release-Pruefungen.

## Bundle-Trockenlauf

Der lokale Bundle-Trockenlauf beschreibt auf Basis des Artefaktmanifests, welche Dateien in ein spaeteres Workbench-Bundle eingehen wuerden:

```powershell
python -m ims.api.workbench_bundle_plan --root . --frontend-dist frontend/dist
```

Die Ausgabe enthaelt `mode = "workbench_bundle_plan"`, den Root-Pfad, den Frontend-Dist-Pfad, `recommended_bundle_name`, `files`, `file_count`, `total_bytes`, `excluded_paths`, `writes_performed = false`, `archive_created = false` und `execution_performed = false`. Die `files`-Liste uebernimmt relative Pfade, Quellpfade, Groessen, SHA-256-Pruefsummen und Gruppen aus dem Artefaktmanifest.

Der Bundle-Trockenlauf schreibt keine Datei, kopiert keine Dateien, erzeugt kein ZIP, keinen Installer, keine SQLite-Datei, oeffnet keinen Schreibpfad und startet keine Simulation. Er ist ein pruefbarer Packaging-Zwischenschritt vor einer spaeteren expliziten ZIP-Erzeugung.

## Lokaler ZIP-Build

Der lokale ZIP-Build erzeugt aus dem Bundle-Plan ein explizit angegebenes ZIP:

```powershell
New-Item -ItemType Directory .\dist -Force
python -m ims.api.workbench_bundle_build --root . --frontend-dist frontend/dist --out .\dist\ims-workbench-local.zip
```

Der Ausgabeordner wird bewusst vorher angelegt; fehlende
Output-Parent-Verzeichnisse lehnt der ZIP-Build ab, statt sie implizit zu
erzeugen.

Die Ausgabe enthaelt `mode = "workbench_bundle_build"`, den Root-Pfad, den Frontend-Dist-Pfad, `out_path`, `entries`, `file_count`, `total_bytes`, `zip_bytes`, `zip_sha256`, `writes_performed = true`, `archive_created = true` und `execution_performed = false`.

Der ZIP-Build schreibt ausschliesslich den expliziten ZIP-Zielpfad. Er kopiert keine Dateien ausserhalb dieses Archivs, erzeugt keine SQLite-Datei, oeffnet keinen HTTP- oder UI-Schreibpfad und startet keine Simulation. Bei Bundle-Plan-Fehlern, fehlendem Ausgabeordner, nicht-`.zip`-Ziel, Ausgabe in ausgeschlossenen Pfaden oder Ausgabe unter eingeschlossenen Quellbaeumen wie `python_port` oder `frontend/dist` wird kein ZIP erzeugt. ZIP-Eintraege nutzen stabile Zeitstempel und Dateirechte, damit `zip_sha256` fuer identische Inhalte reproduzierbar bleibt. Das ZIP ist ein lokales Bereitstellungsartefakt, kein Installer, kein Release-Tag und keine Fachvalidierung oder historische Vollgleichheitsbehauptung.

Ein automatisierter ZIP-Smoke prueft fuer erzeugte lokale Bundles erwartete Workbench-Dateien, ausgeschlossene lokale Daten und Caches sowie stabile ZIP-Metadaten. Dieser Smoke startet keine Simulation und ist kein Installer- oder Release-Test.

## Lokale Release-Bereitstellung

Der lokale Release-Ablauf fuer ein ZIP-Artefakt buendelt die vorhandenen
Packaging-Grenzen in einer festen Reihenfolge:

```powershell
npm.cmd run build
New-Item -ItemType Directory .\dist -Force
python -m ims.api.workbench_bundle_build --root . --frontend-dist frontend/dist --out .\dist\ims-workbench-local.zip
python -m ims.api.workbench_bundle_smoke --zip-path .\dist\ims-workbench-local.zip
python -m ims.api.workbench_portable_staging --zip-path .\dist\ims-workbench-local.zip --out .\ims-workbench
python -m ims.api.workbench_portable_staging_smoke --root .\ims-workbench
python -m ims.api.workbench_portable_readiness --root .\ims-workbench --layout portable
```

Der Ablauf prueft den tatsaechlich erzeugten ZIP-Inhalt und staged ihn danach
explizit in eine portable Zielstruktur unter `.\ims-workbench`. Eine portable
Readiness mit `app\frontend\dist` ist erst nach diesem Staging-Schritt sinnvoll;
Repo-Checks nutzen weiterhin `frontend/dist`. Das portable Staging erwartet
einen fehlenden oder leeren Zielordner und ueberschreibt keine lokalen
Nutzerdaten wie `metadata.sqlite`, WAL-/SHM-Dateien oder Logs. Der
Staging-Smoke liest die gestagte portable Zielstruktur, prueft zentrale
Backend-Module, deren Importfaehigkeit aus dem gestagten Workbench-Root ueber `app\python_port`,
`app\frontend\dist` und die portablen Startskripte, schreibt nichts und startet
keine Simulation. Das ZIP bleibt ein lokales
Bereitstellungsartefakt: Es ist kein Installer, kein automatischer Updater,
keine SQLite-Migration, keine Fachvalidierung und keine historische
Vollgleichheitsbehauptung.

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

`ims.api.metadata_write_contracts` beschreibt diese Grenze als lokalen Vertrag. Der Vertrag erlaubt fuer spaetere lokale Adapter nur Szenario- und Run-Metadaten, einschliesslich des im Importformat erforderlichen Run-Felds `execution_enabled` mit dem Wert `false`. `execution_enabled=true`, Simulation, Fachlogikdaten, HTTP-Schreibendpunkte, UI-Schreibworkflows und historische Vollgleichheitsbehauptungen bleiben verboten. Als aktuell einziger lokaler Schreibweg ist der explizite Import `metadata_import_cli import --db` genannt.

Der Vertrag ist selbst kein Schreibpfad. `python -m ims.api.metadata_write_contracts` gibt nur JSON aus, startet keinen Server, erzeugt keine SQLite-Datei, migriert keine Datenbank und schreibt keine Metadaten. Mit `python -m ims.api.metadata_write_contracts check .\metadata_import.json` kann eine lokale Importdatei zusaetzlich gegen diesen Vertrag geprueft werden. Diese Schreibvertragspruefung schreibt nicht, importiert nicht und lehnt `execution_enabled=true` sowie Fachlogik- oder Simulationsergebnisfelder ab.

## Run-Steuerungsgrenze

`ims.api.run_control_contracts` beschreibt den naechsten vorbereiteten Vertrag fuer spaetere Run-Steuerung:

```powershell
python -m ims.api.run_control_contracts
python -m ims.api.run_control_dry_run_contract
python -m ims.api.controlled_execution_adapter_contract
python -m ims.api.controlled_execution_adapter --fixture tests\fixtures\replay_vn_policyholder_transition_plan.json --explicit-execution-release
python -m ims.api.run_control_adapter_result_contract
python -m ims.api.run_control_adapter_result_contract check .\adapter_result.json
python -m ims.api.run_control_adapter_result_api_contract
python -m ims.api.run_control_adapter_start_contract
```

Die Ausgabe enthaelt `mode = "run_control_contract"`, `schema_version`, gesperrte HTTP-, UI- und Ausfuehrungsgrenzen, zukuenftig erwartbare Eingaben wie `run_id`, `scenario_id`, `metadata_db`, `requested_by`, `created_at` und `execution_enabled` sowie verbotene Grenzen wie Simulation, Fachlogikmutation, Browser-Upload, HTTP-Schreibendpunkt und historische Vollgleichheitsbehauptung.

Der Run-Control-Vertrag ist rein beschreibend. Er startet keinen Lauf, schreibt keine Metadaten, erzeugt keine SQLite-Datei, oeffnet keinen HTTP-Endpunkt und schaltet keinen UI-Startbutton frei. `execution_enabled` und `execution_performed` bleiben `false`.

Der Run-Control-Dry-Run-Vertrag enthaelt `mode = "run_control_dry_run_contract"`, `expected_inputs`, `required_preconditions`, `forbidden_boundaries`, `http_enabled = true`, `writes_enabled = false`, `execution_enabled = false`, `writes_performed = false` und `execution_performed = false`. Er gibt nur den kontrollierten HTTP-Pruefpfad frei; Queue-Schreiben, Metadatenschreiben und Ausfuehrung bleiben gesperrt.

Der kontrollierte Ausfuehrungsadapter-Vertrag enthaelt
`mode = "controlled_execution_adapter_contract"`, erwartete lokale
Fixture-Eingaben, die Felder des spaeteren
`explicit_multi_period_execution_summary` und die Grenzen
`runner_start_enabled = false`, `writes_enabled = false` und
`execution_performed = false`. Er hat in diesem Stand keinen HTTP-Endpunkt,
keinen UI-Startpfad und keinen Queue-Worker.

Der lokale kontrollierte Ausfuehrungsadapter enthaelt
`mode = "controlled_execution_adapter"` und startet nur mit
`--explicit-execution-release`. Er akzeptiert `periods`-Fixtures und
Planfixtures mit `base_snapshot` plus `period_updates`, gibt ausschliesslich den
`explicit_multi_period_execution_summary`-Vertrag zurueck und nimmt keinen freien `--output-dir` an.

Der Run-Control-Adapter-Resultat-Vertrag enthaelt
`mode = "run_control_adapter_result_contract"` und prueft nur ein bereits lokal
erzeugtes `controlled_execution_adapter`-JSON. Der lokale Check liefert
`mode = "run_control_adapter_result_validation"`, startet keinen Adapter,
schreibt keine Metadaten und akzeptiert keinen Browser-Upload.

Der Run-Control-Adapter-Resultat-API-Vertrag enthaelt
`mode = "run_control_adapter_result_api_contract"` und wird nur ueber
`GET /api/run-control/adapter-result-contract` lesend bereitgestellt. Er
beschreibt die spaetere Anzeigegrenze fuer vorab lokal gepruefte
Adapter-Resultate, akzeptiert aber keinen Payload, validiert kein Resultat ueber
HTTP, startet keinen Adapter und schaltet keine UI-Karte frei.

Der Run-Control-Adapter-Startvertrag enthaelt
`mode = "run_control_adapter_start_contract"` und wird nur ueber
`GET /api/run-control/adapter-start-contract` lesend bereitgestellt. Er
beschreibt den spaeteren Startrequest fuer
`POST /api/run-control/adapter-start`, akzeptiert in diesem Stand aber keinen
Start-Payload, validiert keinen Start-Payload ueber HTTP, startet keinen
Adapter und schaltet keinen UI-Startbutton frei.

Ein lokaler Request-Check kann eine spaetere Steuerungsanfrage als DTO validieren:

```powershell
python -m ims.api.run_control_requests check .\run_control_request.json
```

Das Request-DTO enthaelt `run_id`, `scenario_id`, optional `metadata_db`, `requested_by`, `created_at` und das Pflichtfeld `execution_enabled` mit dem Wert `false`. Der Check lehnt `execution_enabled=true`, Fachlogikdaten, Simulationsergebnisfelder und unbekannte Felder ab. Er schreibt keine Metadaten, erzeugt keine SQLite-Datei, oeffnet keinen HTTP-Endpunkt und startet keine Simulation.

Der HTTP-Lesekontrakt fuer dieses DTO ist:

```text
GET /api/run-control/request-contract
GET /api/run-control/dry-run-contract
POST /api/run-control/dry-run
POST /api/run-control/queue
GET /api/run-control/queue/action-plan
GET /api/core-validation/overview
GET /api/core-validation/carryover-probe-contract
GET /api/run-control/adapter-result-contract
GET /api/run-control/adapter-start-contract
GET /api/run-control/core-diagnostics-bridge
```

Die Antwort enthaelt `mode = "run_control_request_contract"`, `schema_version`, `accepted_fields`, `required_fields`, `optional_fields`, `forbidden_fields`, `example_request`, `writes_enabled = false`, `execution_enabled = false` und `execution_performed = false`. Der Endpunkt akzeptiert keinen Request-Body, prueft keinen Browser-Upload, schreibt keine Queue und startet keine Ausfuehrung. Die Frontend-Request-Vertragskarte zeigt diese Felder nur als lokale Orientierung.

Der Dry-Run-Vertragsendpunkt liefert die Form mit `mode = "run_control_dry_run_contract"`, erwarteten Eingaben, Vorbedingungen und verbotenen Grenzen. Der zugehoerige `POST /api/run-control/dry-run` akzeptiert nur das bestehende Run-Control-Request-DTO, lehnt `execution_enabled=true`, unbekannte Felder und fachliche Ergebnisdaten ab, kombiniert den Request mit dem vorhandenen Preflight und liefert `mode = "run_control_dry_run"`. Er schreibt keine Queue oder Metadaten, erzeugt keine SQLite-Datei und startet keine Simulation. Die Frontend-Dry-Run-Karte zeigt Vertrag und letztes Pruefergebnis fuer die aktuelle Run-Auswahl.

Der Queue-Vormerkendpunkt `POST /api/run-control/queue` akzeptiert dasselbe Request-DTO nur bei expliziter SQLite-Metadatenquelle. Vor dem Schreiben fuehrt er denselben Dry-Run aus; fehlgeschlagener Preflight, Szenario-Abweichungen, `execution_enabled=true` oder unbekannte Felder werden vor dem ersten Queue-Schreibzugriff abgelehnt. Bei Erfolg liefert er `mode = "run_control_queue_enqueue"`, den geschriebenen Queue-Eintrag, `writes_performed = true`, `execution_enabled = false` und `execution_performed = false`. Ohne explizite SQLite-Quelle bleibt der Endpunkt blockiert und erzeugt keine `.ims_workbench`-Datei.

Der Aktionsplan-Endpunkt `GET /api/run-control/queue/action-plan` liest dieselbe explizite SQLite-Quelle wie die Queue-Uebersicht. Optional kann `queue_id` als Query-Parameter gesetzt werden. Die Antwort liefert `mode = "run_control_queue_action_plan"`, `actions`, `issues`, `writes_performed = false` und `execution_performed = false`. Pro Queue-Eintrag bleiben `execution_allowed`, `writes_performed` und `execution_performed` `false`; sichtbar werden nur die naechsten sicheren Hinweise `run_preflight`, `await_execution_release`, `resolve_blockers` oder `inspect_queue_status`.

Der Bruecken-Endpunkt `GET /api/run-control/core-diagnostics-bridge` kombiniert
denselben Aktionsplan mit `GET /api/core-validation/overview`. Optional kann
`queue_id` als Query-Parameter gesetzt werden. Die Antwort liefert `mode =
"run_control_core_diagnostics_bridge"`, Queue-Bezug, Perioden- und
Legacy-Zaehler, `bridge_next_action`, `blocked_by`, `writes_performed = false`
und `execution_performed = false`. Der Endpunkt startet keinen Preflight, keinen
Periodenrunner, keine Simulation und keinen Ausfuehrungsadapter.

Der Carryover-Probe-Vertragsendpunkt
`GET /api/core-validation/carryover-probe-contract` beschreibt, welche bereits
berechneten `explicit_transition_carryover_probe`-Payloads spaeter zur
Kernvalidierung passen. Die Antwort liefert
`mode = "core_validation_carryover_probe_api_contract"`,
`precomputed_probe_required = true`, `api_accepts_probe_payload = false`,
`api_starts_probe = false`, `writes_performed = false` und
`execution_performed = false`. Der Endpunkt akzeptiert keinen Request-Body,
liest keine Probe-Datei, startet keinen Probe, schreibt nichts und behauptet
keine historische Vollgleichheit.

Der Adapter-Resultat-Vertragsendpunkt
`GET /api/run-control/adapter-result-contract` beschreibt, welche bereits lokal
geprueften `controlled_execution_adapter`-Resultate spaeter angezeigt werden
duerfen. Die Antwort liefert
`mode = "run_control_adapter_result_api_contract"`,
`api_accepts_result_payload = false`, `api_validates_result_payload = false`,
`api_starts_adapter = false`, `writes_performed = false` und
`execution_performed = false`. Der Endpunkt akzeptiert keinen Request-Body,
liest keine Adapter-Datei, startet keinen Adapter, schreibt nichts und
behauptet keine historische Vollgleichheit.

Der Adapter-Start-Vertragsendpunkt
`GET /api/run-control/adapter-start-contract` beschreibt, welche spaeteren
Request-Felder und Preconditions fuer einen freigegebenen Adapterstart
erforderlich waeren. Die Antwort liefert
`mode = "run_control_adapter_start_contract"`,
`planned_start_endpoint = "/api/run-control/adapter-start"`,
`api_accepts_start_payload = false`, `api_validates_start_payload = false`,
`api_starts_adapter = false`, `ui_start_enabled = false`,
`queue_worker_enabled = false`, `writes_performed = false` und
`execution_performed = false`. `POST /api/run-control/adapter-start` existiert
in diesem Stand nicht.

Der kontrollierte Ausfuehrungsadapter-Vertrag bleibt dagegen ein lokaler
CLI-/DTO-Vertrag. Der lokale Adapter ist ebenfalls nicht Teil der
HTTP-Lesekontrakte und schaltet keinen Startbutton frei.

Der naechste geplante Run-Control-Anschluss ist nur ein read-only Adapter-Resultat. `docs/plans/run_control_adapter_result_plan.md` legt fest,
dass Run-Control hoechstens ein bereits lokal erzeugtes
`controlled_execution_adapter`-JSON einordnen darf. Es gibt weiterhin keinen Adapterstart aus Run-Control, keinen Browser-Upload, keinen Queue-Worker und keinen UI-Startpfad.
Der vorgeschlagene Folgeschritt `docs/plans/run_control_adapter_result_view_plan.md`
plant nur eine read-only API-/UI-Anzeige fuer Adapter-Resultate. Auch dort
bleiben Browser-Upload, Dateiauswahl, Startbutton und Adapterstart gesperrt.

Der lokale Demo-Smoke fuer die Browser-Workbench ist die bewusst kleine Bedienfolge `Dry-Run pruefen -> Queue vormerken -> Run-Control-Aktionsplan ansehen -> Run-Control-Kernblick-Bruecke lesen -> Carryover-Probe-Vertrag lesen -> Adapter-Resultat-Vertrag lesen`. Als stabile Demo-Daten dienen `baseline-python-tests` und `agrsich-reference-window`. Die API-Sequenz ist `POST /api/run-control/dry-run`, danach `POST /api/run-control/queue`, anschliessend `GET /api/run-control/queue/action-plan`, `GET /api/run-control/core-diagnostics-bridge`, `GET /api/core-validation/carryover-probe-contract` und `GET /api/run-control/adapter-result-contract`, jeweils optional mit `queue_id`, wo der Endpunkt dies unterstuetzt. Dabei schreibt nur die Queue-Vormerkung in eine explizite SQLite-Metadatenquelle; Dry-Run, Aktionsplan, Bruecke, Carryover-Probe-Vertrag und Adapter-Resultat-Vertrag bleiben lesend. Erwartet sind `execution_enabled = false`, `execution_performed = false`, ein Queue-Aktionshinweis `run_preflight`, ein Brueckenhinweis `resolve_core_validation_blockers`, `api_starts_probe = false` und `api_starts_adapter = false`. Dieser Demo-Smoke startet keine Simulation, aktiviert keinen Ausfuehrungsadapter, aendert keine Fachlogik und behauptet keine historische Vollgleichheit.

Fuer den echten Browser-/Screenshot-Smoke stellt die Frontend-Schale stabile `data-testid`-Anker bereit: `run-control-demo-dry-run-button`, `run-control-demo-queue-button`, `run-control-demo-dry-run-result`, `run-control-demo-queue-result`, `run-control-demo-action-plan`, `run-control-core-bridge`, `carryover-probe-contract` und `adapter-result-contract`. Der Screenshot-Smoke prueft Sichtbarkeit und Bedienfolge in der lokalen Workbench. Er prueft keine historischen Fachwerte und ersetzt keine spaetere Fachvalidierung.

`ims.api.run_control_queue` kann validierte Requests lokal vormerken:

```powershell
python -m ims.api.run_control_queue init --db .\.ims_workbench\metadata.sqlite
python -m ims.api.run_control_queue enqueue .\run_control_request.json --db .\.ims_workbench\metadata.sqlite
python -m ims.api.run_control_queue list --db .\.ims_workbench\metadata.sqlite
python -m ims.api.run_control_queue_diagnostics --db .\.ims_workbench\metadata.sqlite
python -m ims.api.run_control_queue_action_plan --db .\.ims_workbench\metadata.sqlite
```

Die Queue speichert `queue_id`, Request-Daten, Status und Ausfuehrungsgrenzen. Erlaubte Statuswerte sind `planned`, `blocked` und `validated`. `init` und `enqueue` schreiben nur in den expliziten SQLite-Pfad; `list`, `show`, `run_control_queue_diagnostics` und `run_control_queue_action_plan` lesen eine bestehende Queue read-only. Wenn keine WAL-/SHM-Sidecars vorhanden sind, erzeugen diese Lesezugriffe keine neuen Sidecars. Rollback-Journal-Datenbanken werden dabei als normale `mode=ro`-Quelle gelesen; `immutable=1` bleibt auf sidecar-freie WAL-Dateien beschraenkt. Sind Live-WAL-Sidecars vollstaendig vorhanden, werden sie beruecksichtigt, statt aktuelle Queue-Daten still zu ignorieren. Unvollstaendige Sidecar-Zustaende, etwa `-wal` ohne `-shm`, werden vor dem Lesen abgelehnt, damit kein fehlender Sidecar neu aufgebaut wird. Die Diagnose meldet fehlende Szenario-Referenzen, unerwartete Ausfuehrungsflags, bereits gesetztes `execution_performed` und unbekannte Statuswerte als Issues. Der Aktionsplan gibt `mode = "run_control_queue_action_plan"`, `metadata_source`, `queue_count`, `actions`, `issues`, `writes_performed = false` und `execution_performed = false` aus. Pro Queue-Eintrag bleiben `execution_allowed`, `writes_performed` und `execution_performed` `false`; empfohlen werden nur `run_preflight`, `await_execution_release`, `resolve_blockers` oder `inspect_queue_status`. Er nutzt Queue-Diagnose und Preflight als lesende Hinweise, startet aber keine Ausfuehrung und oeffnet keine Schreibpfade. Eine nur mit `run_control_queue init --db` angelegte Queue-only-Datenbank bleibt als Queue lesbar; fehlende Szenario-/Run-Metadatentabellen werden als Diagnosewarnung und Aktionsplan-Blocker gemeldet. Kein Queue-Befehl startet eine Simulation, einen Worker, einen Scheduler, einen HTTP-Endpunkt oder einen UI-Schreibpfad. `execution_enabled` und `execution_performed` bleiben fuer normale Queue-Eintraege `false`.

Die API bietet dazu eine rein lesende Uebersicht:

```text
GET /api/run-control/queue
```

Die Antwort enthaelt `mode = "run_control_queue_overview"`, `queue_count`, vorhandene `entries`, `issues`, `writes_enabled = false`, `execution_enabled = false` und `execution_performed = false`. Ohne explizite SQLite-Metadatenquelle meldet sie die Queue als nicht konfiguriert. Bei einer SQLite-Quelle ohne initialisierte Queue bleibt die Ausgabe ein lesender Hinweis; der Endpunkt legt keine Queue-Tabelle an und schreibt keine Datei.

Ein einzelner Eintrag kann lesend ueber `GET /api/run-control/queue/{queue_id}` geladen werden. Fehlende Eintraege liefern die stabile `metadata_not_found`-Fehlerform. Die Frontend-Run-Control-Uebersicht nutzt diese Endpunkte fuer Auswahl, Filter, lokale Schritt-Hinweise und Detailkarte und bleibt ohne Start-, Upload-, Editor- oder Schreibkontrollen. Die Schritt-Hinweise sind nur Anzeige: `planned` verweist auf lokalen Preflight, `validated` auf wartende Ausfuehrungsfreigabe, `blocked` auf Blockerklaerung und unbekannte Statuswerte auf Statuspruefung.

Ein lokaler Preflight kann vorhandene Run-Metadaten gegen diese Grenze pruefen:

```powershell
python -m ims.api.run_control_preflight --run-id baseline-python-tests
```

Optional kann eine explizite SQLite-Metadatenquelle read-only gelesen werden:

```powershell
python -m ims.api.run_control_preflight --run-id baseline-python-tests --db .\.ims_workbench\metadata.sqlite
```

Der Run-Control-Preflight ist ebenfalls rein lokal und lesend. Er meldet, ob Run- und Szenario-Metadaten gefunden wurden, welche Metadatenquelle gelesen wurde und warum Ausfuehrung weiter nicht erlaubt ist. Unbekannte Runs, fehlende Szenario-Referenzen oder `execution_enabled=true` werden als Issues ausgegeben. Der Preflight erzeugt keine SQLite-Datei, schreibt keine Metadaten, oeffnet keinen HTTP-Endpunkt und startet keine Simulation.

Die Workbench-API stellt denselben Preflight fuer die aktuelle UI-Auswahl read-only bereit:

```text
GET /api/run-control/preflight/{run_id}
```

Die Antwort enthaelt `mode = "run_control_preflight"`, `run_id`, `scenario_id`, `run_found`, `scenario_found`, `metadata_source`, `execution_enabled`, `execution_allowed = false`, `issues`, `writes_performed = false` und `execution_performed = false`. Die Frontend-Preflight-Karte laedt diesen Endpunkt bei Run-Auswahl, zeigt waehrend des Ladens neutrale Ladewerte statt negativer Pruefergebnisse und bleibt ohne Startbutton, Upload, Editor, POST/PUT oder Browser-Schreibpfad.

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

Start und Diagnose:

| Kommando | Zweck | Schreibverhalten |
| --- | --- | --- |
| `python -m ims.api.workbench_diagnostics --frontend-dist frontend/dist` | Startbedingungen pruefen | schreibt nicht |
| `python -m ims.api.workbench_diagnostics --config .\workbench.local.json` | Startbedingungen aus expliziter Konfiguration pruefen | schreibt nicht |
| `python -m ims.api.workbench_start_plan --config .\workbench.local.json` | Lokalen Start beschreibend zusammenfassen | schreibt nicht |
| `python -m ims.api.workbench_readiness --frontend-dist frontend/dist` | Lokale Workbench-v1-Bereitschaft buendeln | schreibt nicht |
| `python -m ims.api.workbench_portable_readiness --root . --layout repo` | Repo- oder portable Workbench-Struktur pruefen | schreibt nicht |
| `python -m ims.api.workbench_build_snapshot --root . --frontend-dist frontend/dist` | Vorhandene lokale Build-Artefakte zusammenfassen | schreibt nicht |
| `python -m ims.api.workbench_artifact_manifest --root . --frontend-dist frontend/dist` | Ein- und Ausschlusspfade fuer spaeteres Artefakt beschreiben | schreibt nicht |
| `python -m ims.api.workbench_bundle_plan --root . --frontend-dist frontend/dist` | Spaeteres Workbench-Bundle auf Basis des Manifests planen | schreibt nicht |
| `python -m ims.api.workbench_bundle_build --root . --frontend-dist frontend/dist --out .\dist\ims-workbench-local.zip` | Explizites lokales ZIP aus dem Bundle-Plan erzeugen | schreibt nur den expliziten ZIP-Zielpfad |
| `python -m ims.api.workbench_bundle_smoke --zip-path .\dist\ims-workbench-local.zip` | Explizit erzeugtes ZIP direkt pruefen | schreibt nicht |
| `python -m ims.api.workbench_portable_staging --zip-path .\dist\ims-workbench-local.zip --out .\ims-workbench` | Geprueftes ZIP in eine portable Zielstruktur stagen | schreibt nur in den expliziten leeren Zielordner |
| `python -m ims.api.workbench_portable_staging_smoke --root .\ims-workbench` | Gestagte portable Struktur und Startskriptgrenzen pruefen | schreibt nicht |
| `python -m ims.api.workbench_cli_overview` | Lokale Workbench-CLI-Befehle und Grenzen auflisten | schreibt nicht |

Vertraege und Grenzen:

| Kommando | Zweck | Schreibverhalten |
| --- | --- | --- |
| `python -m ims.api.metadata_write_contracts` | Vorbereitete Schreibgrenzen beschreibend ausgeben | schreibt nicht |
| `python -m ims.api.metadata_write_contracts check .\metadata_import.json` | Importdatei gegen den Schreibvertrag pruefen | schreibt nicht |
| `python -m ims.api.run_control_contracts` | Spaetere Run-Steuerungsgrenze ohne Ausfuehrung beschreiben | schreibt nicht |
| `python -m ims.api.controlled_execution_adapter_contract` | Spaeteren lokalen Ausfuehrungsadapter-Vertrag ohne Runner-Start beschreiben | schreibt nicht |
| `python -m ims.api.controlled_execution_adapter --fixture tests\fixtures\replay_vn_policyholder_transition_plan.json --explicit-execution-release` | Lokalen explizit freigegebenen Fixture-Adapter ohne Output-Pfad ausfuehren | schreibt nicht |
| `python -m ims.api.run_control_adapter_result_contract` | Run-Control-Adapter-Resultat-Vertrag beschreiben | schreibt nicht |
| `python -m ims.api.run_control_adapter_result_contract check .\adapter_result.json` | Bereits erzeugtes Adapter-Resultat read-only gegen den Vertrag pruefen | schreibt nicht |
| `python -m ims.api.run_control_adapter_result_api_contract` | API-Vertrag fuer vorab lokal gepruefte Adapter-Resultate beschreiben | schreibt nicht |
| `python -m ims.api.run_control_adapter_start_contract` | API-Startvertrag fuer spaetere Adapterstarts beschreiben | schreibt nicht |
| `python -m ims.api.core_validation_carryover_probe_contract` | API-Vertrag fuer vorab berechnete Carryover-Probe-Ergebnisse beschreiben | schreibt nicht |
| `python -m ims.api.run_control_requests check .\run_control_request.json` | Lokalen Run-Control-Request ohne Ausfuehrung validieren | schreibt nicht |
| `python -m ims.api.run_control_queue init --db .\.ims_workbench\metadata.sqlite` | Queue-Schema in expliziter SQLite-Datei anlegen | schreibt Queue-Metadaten |
| `python -m ims.api.run_control_queue enqueue .\run_control_request.json --db .\.ims_workbench\metadata.sqlite` | Validierten Request ohne Ausfuehrung vormerken | schreibt Queue-Metadaten |
| `python -m ims.api.run_control_queue list --db .\.ims_workbench\metadata.sqlite` | Queue read-only auflisten, neue Sidecars vermeiden und unvollstaendige Sidecars ablehnen | schreibt nicht |
| `python -m ims.api.run_control_queue_diagnostics --db .\.ims_workbench\metadata.sqlite` | Queue-Schema, Szenario-Referenzen, Statuswerte und Ausfuehrungsflags read-only diagnostizieren | schreibt nicht |
| `python -m ims.api.run_control_preflight --run-id baseline-python-tests` | Run-Metadaten lokal gegen die gesperrte Steuerungsgrenze pruefen | schreibt nicht |

Metadaten:

| Kommando | Zweck | Schreibverhalten |
| --- | --- | --- |
| `python -m ims.api.metadata_import_cli check .\metadata_import.json` | Importformat knapp validieren | schreibt nicht |
| `python -m ims.api.metadata_import_cli preview .\metadata_import.json` | Importdatei zusammenfassen und Konsistenzhinweise zeigen | schreibt nicht |
| `python -m ims.api.metadata_import_cli snapshot` | geseedete In-Memory-Metadaten als Diagnose lesen | schreibt nicht |
| `python -m ims.api.metadata_import_cli snapshot --db .\.ims_workbench\metadata.sqlite` | explizite SQLite-Metadaten read-only lesen | schreibt nicht |
| `python -m ims.api.metadata_import_cli export` | geseedete In-Memory-Metadaten im Importformat auf stdout ausgeben | schreibt nicht |
| `python -m ims.api.metadata_import_cli export --db .\.ims_workbench\metadata.sqlite --out .\metadata_export.json` | explizite SQLite-Metadaten im Importformat exportieren | schreibt nur in den expliziten Zielpfad |
| `python -m ims.api.metadata_import_cli roundtrip` | Seed-Metadaten exportieren und im Speicher gegen Importformat und Schreibvertrag pruefen | schreibt nicht |
| `python -m ims.api.metadata_import_cli roundtrip --db .\.ims_workbench\metadata.sqlite` | explizite SQLite-Metadaten read-only roundtrip-pruefen | schreibt nicht |
| `python -m ims.api.metadata_import_cli dry-run .\metadata_import.json` | Importwirkung gegen Seed-Metadaten pruefen | schreibt nicht |
| `python -m ims.api.metadata_import_cli dry-run .\metadata_import.json --db .\.ims_workbench\metadata.sqlite` | Importwirkung gegen eine explizite SQLite-Quelle pruefen | schreibt nicht |
| `python -m ims.api.metadata_import_cli import .\metadata_import.json --db .\.ims_workbench\metadata.sqlite` | validierte Metadaten lokal importieren und Importbericht ausgeben | schreibt nur in den expliziten DB-Pfad |

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

Der explizite Snapshot-Pfad oeffnet die SQLite-Datei read-only. Er initialisiert oder migriert keine Datenbank und schreibt keine Workbench-Metadaten. SQLite-WAL-/SHM-Dateien koennen bei einer Live-WAL-Datenbank vorhanden sein; sie bedeuten keinen Import- oder Snapshot-Schreibpfad. Fuer sidecar-freie Datenbanken gilt dieselbe Grenze wie bei der Queue: Rollback-Journal-Dateien bleiben `mode=ro`, sidecar-freie WAL-Dateien nutzen `immutable=1`, und unvollstaendige Sidecars werden abgelehnt. Fehlt die Datei oder ist sie keine lesbare Workbench-SQLite-Ablage, liefert der CLI-Adapter eine stabile JSON-Fehlerform.

Ein lokaler Export gibt die aktuell lesbaren Workbench-Metadaten im bestehenden Importformat aus. Ohne `--out` wird das JSON-Bundle auf stdout geschrieben und keine Datei erzeugt:

```powershell
python -m ims.api.metadata_import_cli export
```

Mit expliziter SQLite-Quelle und explizitem Zielpfad wird nur dieser Zielpfad geschrieben:

```powershell
python -m ims.api.metadata_import_cli export --db .\.ims_workbench\metadata.sqlite --out .\metadata_export.json
```

Der Export startet keine Simulation, erzeugt keine SQLite-Datei, oeffnet keinen HTTP-Endpunkt und ist kein Browser-Download. Fehlt eine explizite SQLite-Quelle, wird sie nicht angelegt. Der explizite Export-Zielpfad darf weder identisch mit der SQLite-Quelle sein noch ueber Hardlink- oder Datei-Alias auf dieselbe Datei zeigen; gleiche aufgeloeste `--db`- und `--out`-Pfade sowie dieselbe Dateiidentitaet werden abgelehnt, bevor geschrieben wird.

Ein lokaler Roundtrip-Check exportiert die aktuell lesbaren Metadaten im Speicher und prueft dieses Bundle direkt wieder gegen Importparser, Repository-Validierung und Schreibvertrag:

```powershell
python -m ims.api.metadata_import_cli roundtrip
```

Mit expliziter SQLite-Quelle wird diese read-only gelesen:

```powershell
python -m ims.api.metadata_import_cli roundtrip --db .\.ims_workbench\metadata.sqlite
```

Der Roundtrip schreibt keine Exportdatei, erzeugt keine SQLite-Datei, importiert keine Metadaten und startet keine Simulation. Er ist eine lokale Adapterpruefung fuer Metadatenformen, keine Fachvalidierung und keine historische Vollgleichheitsbehauptung.

Ein lokaler Import-Trockenlauf prueft eine Importdatei gegen Importparser, Schreibvertrag und optional gegen eine explizite SQLite-Metadatenquelle. Er zeigt, welche Szenario- und Run-IDs neu waeren und welche bestehenden IDs ersetzt wuerden:

```powershell
python -m ims.api.metadata_import_cli dry-run .\metadata_import.json
```

Mit expliziter SQLite-Quelle wird diese read-only fuer den Bestandsabgleich genutzt:

```powershell
python -m ims.api.metadata_import_cli dry-run .\metadata_import.json --db .\.ims_workbench\metadata.sqlite
```

Der Dry-Run schreibt keine Metadaten, erzeugt keine SQLite-Datei, importiert nichts und startet keine Simulation. Er ist eine lokale Vorabpruefung fuer kontrollierte Metadatenpflege, keine Fachvalidierung und keine historische Vollgleichheitsbehauptung.

Ein Import schreibt nur in eine ausdruecklich angegebene SQLite-Datei:

```powershell
python -m ims.api.metadata_import_cli import .\metadata_import.json --db .\.ims_workbench\metadata.sqlite
```

Nach einem erfolgreichen Import liefert der CLI-Adapter einen Importbericht mit `input_path`, `db_path`, geschriebenen Szenario- und Run-IDs, `consistency`, `writes_performed = true` und `execution_performed = false`. Der Bericht startet keine Simulation, ist keine Fachvalidierung und behauptet keine historische Vollgleichheit.

Die Ausgabe ist eine knappe JSON-Statuszeile. Fehler liefern ebenfalls eine stabile JSON-Form mit `status = "error"` und einer kurzen Meldung. Der Preview-Modus liefert zusaetzlich `existing_scenario_ids`, `existing_run_ids`, `new_scenario_ids`, `new_run_ids`, `runs_with_missing_scenario`, `runs_with_execution_enabled` und `writes_performed = false`. Der Snapshot-Modus liefert `source`, `scenarios`, `runs`, `consistency`, `writes_performed = false` und `execution_performed = false`. Der Export-Modus ohne `--out` liefert direkt `schema_version`, `scenarios` und `runs`; mit `--out` liefert er eine Statuszeile mit `mode = "export"`. Der Roundtrip-Modus liefert `source`, Zaehler und IDs sowie `import_valid = true`, `write_contract_valid = true`, `writes_performed = false` und `execution_performed = false`. Der Dry-Run-Modus liefert `source`, Zaehler, `new_scenario_ids`, `replaced_scenario_ids`, `new_run_ids`, `replaced_run_ids`, `issues`, `writes_performed = false` und `execution_performed = false`. Der Import-Modus liefert den Importbericht mit Konsistenzstatus nach dem Schreiben. Er exportiert keine Fachlogikdaten, startet keine Simulation und nutzt eine read-only Verbindung fuer explizite Snapshot-/Export-/Roundtrip-/Dry-Run-Datenbanken, damit auch committed Live-WAL-Metadaten sichtbar bleiben. Der Adapter liest weder `IMS_METADATA_DB` als implizites Schreibziel noch oeffnet er einen HTTP-Endpunkt. Die API- und UI-Schreibpfade bleiben gesperrt.

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

## Spaetere Bloecke

Nach der lokalen Workbench-v1 bleiben groessere Bloecke bewusst separat: kontrollierte echte Run-Steuerung, moegliche UI- oder HTTP-Schreibpfade, ein Szenario-Editor, SQLite-Migrationen sowie zusaetzliche Fachvalidierung und historische Vollgleichheit. Diese Themen sollen jeweils eigene reviewbare Plaene und PRs bekommen und duerfen nicht als stiller Nebeneffekt der lokalen Workbench-v1 verstanden werden.

Der Packaging- und Bereitstellungsblock ist separat unter `docs/migration/workbench_packaging_plan.md` konsolidiert. Dieser Stand beschreibt portable lokale Startbarkeit, Startskripte, Artefaktstruktur, ZIP-/Staging-Grenzen sowie Backup-/Update-Grenzen, erzeugt aber selbst kein Paket und startet keine Simulation.
