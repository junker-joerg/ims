# Workbench Run-Control Plan nach v1

Dieses Dokument plant den naechsten Modernisierungsblock nach der abgeschlossenen lokalen Workbench-v1. Es ist ein Planungsstand, keine Implementierung: Es startet keine Simulation, oeffnet keine Schreibpfade, aendert keine Fachlogik und behauptet keine historische Vollgleichheit.

## Ausgangspunkt nach Workbench-v1

Die lokale Workbench-v1 ist als rein lokale Browser-Workbench abgeschlossen. Sie stellt Backend-Health und Version, statische Frontend-Auslieferung, lesende Szenario- und Run-Metadaten, Detailansichten, Filter, Auswahlzusammenfassung, Betriebsdiagnose, Metadatenquelle, Konsistenzdiagnose und Readiness bereit.

Die lokalen CLI-Adapter decken Diagnose, Startplan, CLI-Uebersicht, Metadaten-Check, Preview, Dry-Run, Export, Roundtrip, Snapshot, expliziten Importbericht, Schreibvertrag, Schreibvertragspruefung, Run-Control-Vertrag, Run-Control-Request-Check, Run-Control-Queue und Run-Control-Preflight ab. Diese Werkzeuge bleiben lokal. Nur der explizite Metadatenimport mit `--db` und die explizite lokale Run-Control-Queue schreiben Metadaten in eine angegebene SQLite-Datei; keine dieser Grenzen startet eine Simulation.

Vorhandene lokale Run-Control-Bausteine sind:

- Run-Control-Vertrag (`ims.api.run_control_contracts`), rein beschreibend.
- Run-Control-Dry-Run-Vertrag (`ims.api.run_control_dry_run_contract`), gesperrt und rein beschreibend.
- Run-Control-Request-Check (`ims.api.run_control_requests`), lokal validierend.
- Run-Control-Queue (`ims.api.run_control_queue`), explizit lokal und ohne Ausfuehrung.
- Run-Control-Queue-Aktionsplan (`ims.api.run_control_queue_action_plan`), lokal lesend und ohne Ausfuehrung.
- Run-Control-Preflight (`ims.api.run_control_preflight`), lesend und ohne Ausfuehrung.
- Workbench-Readiness und CLI-Uebersicht, die diese Grenzen sichtbar machen.

## Zielbild

Das Zielbild bleibt eine kleine portable IMS Workbench fuer lokale Nutzung im Browser. UI, Backend/API, Metadatenhaltung, spaetere Ausfuehrungsadapter und Python-Fachlogik bleiben sauber getrennt. Die Workbench soll spaeter kontrolliert Run-Anfragen vorbereiten, anzeigen, validieren und nach separater Freigabe an einen eng abgegrenzten Ausfuehrungsadapter uebergeben koennen.

Bis zu dieser separaten Freigabe bleibt `execution_enabled` auf `false`. Es gibt keinen funktionalen Startbutton, keine stille Fachlogikmutation und keine historische Vollgleichheitsbehauptung.

## Gesamtplanung bis wirklich alles fertig

Die Restplanung bis zum vollstaendigen Abschluss inklusive weiterem Workbench-Ausbau, Fachvalidierung und historischer Vollgleichheit bleibt bewusst grob. Der Packaging-/Bereitstellungsblock fuer die lokale Workbench-v1 ist bereits konsolidiert; offen bleiben dort nur Review-Fixes oder spaeter explizit beauftragte Release-Automatisierung.

- Erwartet: grob ca. `14-28+` reviewbare PRs.
- Workbench-Ausbau nach v1: ca. `3-7` PRs.
- Fachvalidierung/historische Vollgleichheit: ca. `10-18` PRs.
- Integrations-/Review-Reserve: ca. `1-3` PRs.

Geplante Bloecke:

| Block | Erwarteter Umfang | Inhalt |
| --- | ---: | --- |
| Workbench nach v1 vollstaendig nutzbarer machen | ca. `3-7` PRs | lokale Aktionsplaene, lesende Queue-/Run-Control-Anzeigen, gesperrte Dry-Run-Vertraege, spaeterer Ausfuehrungsadapter nur nach Freigabe, Haertung, Doku und E2E-Smokes |
| Fachvalidierung und historische Vollgleichheit | ca. `10-18` PRs | weitere Legacy-Referenzen, zusaetzliche Alt-/Neu-Vergleichspfade, Mehrperioden-Replays, Abweichungsanalyse, Modellkorrekturen und Abschlussbericht |
| Packaging und Bereitstellung | ca. `0` geplante PRs | lokale Startbarkeit, portable Ordnerstruktur, Startskripte/Launcher, reproduzierbarer Build, ZIP-/Staging-Grenzen, Installations-, Update- und Backup-Doku sind fuer v1 konsolidiert; offen nur Review-Fixes oder spaeter explizite Release-Automatisierung |
| Integrations- und Abschlussreserve | ca. `1-3` PRs | Review-Fixes, CI- und Windows-Pfadhaertung, finale Doku-Konsolidierung und Meilensteinabschluss |

Diese Planung ist keine Zusage auf historische Vollgleichheit. Fachvalidierung und historische Vollgleichheit bleiben eigene spaetere Bloecke mit separaten Referenzfenstern, Vergleichspfaden und Abschlusskriterien.

## Run-Control-Phasen

Phase 1: Rein lokale Run-Control-Requests als DTO und CLI, ohne Ausfuehrung.

Phase 2: Persistierte Run-Control-Metadaten oder Queue in SQLite, weiterhin ohne Fachlogiklauf.

Phase 3: HTTP-Vertrag fuer Run-Control-Requests, zunaechst gesperrt oder als Dry-Run, ohne echte Ausfuehrung.

Phase 4: UI-Bedienflaeche fuer geplante Run-Control-Pfade, ohne funktionalen Start.

Phase 5: Kontrollierter Adapter zur spaeteren Simulationsausfuehrung, erst nach separater expliziter Freigabe und mit enger Fachlogikgrenze.

Phase 6: Haertung, Doku, Smoke-/E2E-Pruefung und Abschlusskonsolidierung.

## Erwartete PR-Roadmap fuer den Workbench-Ausbau

1. PR 1: Run-Control-Dashboard/lesende Queue-Anzeige im Frontend mit clientseitigen Filtern, Hinweisen und lokalen Schrittlabels.
2. PR 2: API-Leseendpunkte fuer Queue/Requests, noch ohne Schreibpfad. Queue-Reads sind vorhanden; der Request-Vertrag wird als GET-Contract sichtbar.
3. PR 3: Kontrollierter HTTP-Dry-Run-Vertrag, weiterhin gesperrt und ohne Request-Body.
4. PR 4: UI-Preflight-Ansicht fuer ausgewaehlten Run per GET-only Leseendpunkt.
5. PR 5: Kontrollierte lokale Queue-Schreibpfade ueber API nur nach separater Freigabe.
6. PR 6+: Ausfuehrungsadapter erst nach expliziter fachlicher Freigabe.
7. Weitere PRs: Haertung, Doku, Smoke-/E2E-Checks, Review-Fixes und Grenzkorrekturen.

## API- und DTO-Grenzen

Run-Control-DTOs sollen nur Metadaten und Absichten beschreiben. Erwartbare Felder sind `run_id`, `scenario_id`, `metadata_db`, `requested_by`, `created_at`, `execution_enabled=false`, Status, Quelle und Validierungs-/Preflight-Ergebnis. Fachlogikdaten, Simulationsergebnisse und Legacy-Vergleichsdaten gehoeren nicht in diese DTOs.

HTTP-Vertraege duerfen erst eingefuehrt werden, wenn ihre Schreib- und Ausfuehrungsgrenzen testbar sind. Zunaechst muessen sie gesperrt oder reine Dry-Run-Vertraege bleiben. Fehlerformen sollen stabil, knapp und maschinenlesbar sein.

## Repository- und SQLite-Grenzen

SQLite bleibt die lokale Metadatenablage. Run-Control-Metadaten oder Queue-Eintraege duerfen nur ueber klar benannte Repository-Methoden geschrieben werden. Die lokale Queue darf validierte Requests vormerken, aber keinen Worker, Scheduler oder Simulationslauf starten.

Lesende Diagnose-, Snapshot-, Export-, Roundtrip- und Preflight-Pfade duerfen keine Datenbankdateien erzeugen. Schreibpfade muessen einen expliziten Zielpfad verlangen und duerfen keine Ausfuehrung starten. Fuer SQLite-Read-only-Zugriffe bleibt die WAL-Grenze explizit: Rollback-Journal-Datenbanken werden mit `mode=ro` gelesen, vollstaendige Live-WAL-Sidecars werden beruecksichtigt, unvollstaendige Sidecars werden abgelehnt und `immutable=1` ist nur fuer sidecar-freie WAL-Dateien zulaessig.

Der lokale Queue-Aktionsplan ist ein rein lesender Adapter zwischen Queue-Diagnose und Preflight:

```powershell
python -m ims.api.run_control_queue_action_plan --db .\.ims_workbench\metadata.sqlite
python -m ims.api.run_control_queue_action_plan --db .\.ims_workbench\metadata.sqlite --queue-id <id>
```

Er erzeugt stabile JSON-Felder fuer `status`, `mode = "run_control_queue_action_plan"`, `db_path`, `metadata_source`, optional `queue_id`, `queue_count`, `actions`, `issues`, `writes_performed = false` und `execution_performed = false`. Pro Queue-Eintrag werden `queue_id`, `run_id`, `scenario_id`, `queue_status`, `next_action`, `next_action_label`, `blocked_by`, `execution_allowed = false`, `writes_performed = false` und `execution_performed = false` sichtbar. `planned` ohne Blocker fuehrt nur zu `run_preflight`, `validated` ohne Blocker zu `await_execution_release`, `blocked` oder Diagnose-/Preflight-Hinweise zu `resolve_blockers`; unbekannte Statuswerte bleiben ein `inspect_queue_status`-Hinweis. Queue-only-Datenbanken und nicht initialisierte Queues bleiben stabile Hinweise statt Abstuerze.

## Sicherheitsgrenzen

- `execution_enabled` bleibt bis zur expliziten Ausfuehrungsfreigabe `false`.
- `execution_performed` bleibt in Plan-, Diagnose-, Dry-Run- und Preflight-Pfaden `false`.
- Kein Startbutton mit echter Funktion.
- Keine stille Fachlogikmutation.
- Keine Simulation im Plan-PR.
- Kein Packaging im Plan-PR, nur Planung.
- Keine historische Vollgleichheitsbehauptung.

## UI-Grenzen

Die UI darf geplante Run-Control-Metadaten spaeter anzeigen, filtern und als Preflight-Ergebnis erklaeren. Sie darf in den naechsten Schritten keinen Upload, keinen Editor, keinen Browser-Download, keinen HTTP-Schreibpfad und keinen funktionalen Run-Start bereitstellen.

UI-Texte sollen operational, knapp und ruhig bleiben. Die Workbench bleibt ein Werkzeug, keine Marketing-Oberflaeche.

## Teststrategie

Die Run-Control-Schritte brauchen Tests auf mehreren Ebenen:

- DTO- und Vertragsform: Pflichtfelder, verbotene Felder, stabile Fehlerformen.
- Repository/SQLite: explizite Schreibpfade, atomare Grenzen, keine implizite Datei-Erzeugung.
- CLI/Dry-Run/Preflight: stabile JSON-Formen, `writes_performed = false`, `execution_performed = false`.
- HTTP-Vertraege: zunaechst gesperrt oder Dry-Run, keine echte Ausfuehrung.
- Frontend: rein lesende Anzeige, kein Startbutton mit Funktion, keine Schreibcontrols.
- Doku-Smokes: keine Fachlogikaenderung, keine historische Vollgleichheitsbehauptung, Packaging/Bereitstellung als eigener spaeterer Block.

## Nicht-Ziele dieses Plan-PRs

- Keine Fachlogikaenderung.
- Keine Simulation starten.
- Keine neuen HTTP-Schreibendpunkte.
- Kein HTTP-Schreibpfad.
- Kein Browser-Upload.
- Kein Browser-Download.
- Keine UI-Schreibpfade.
- Kein funktionaler Run-Start.
- Kein Szenario-Editor.
- Keine SQLite-Migration.
- Kein Packaging in diesem PR.
- Keine historische Vollgleichheitsbehauptung.

## Spaetere separate Bloecke

Fachvalidierung und historische Vollgleichheit bleiben eigene spaetere Bloecke von ca. `10-18` PRs. Packaging und Bereitstellung sind fuer die lokale Workbench-v1 mit ca. `0` geplanten PRs konsolidiert; weitere Packaging-Arbeit waere ein separater spaeterer Auftrag, etwa fuer Release-Automatisierung. Keiner dieser Bloecke darf als Nebeneffekt der Run-Control-Planung umgesetzt oder behauptet werden.
