# Workbench Run-Control Plan nach v1

Dieses Dokument plant den naechsten Modernisierungsblock nach der abgeschlossenen lokalen Workbench-v1. Es ist ein Planungsstand, keine Implementierung: Es startet keine Simulation, oeffnet keine Schreibpfade, aendert keine Fachlogik und behauptet keine historische Vollgleichheit.

## Ausgangspunkt nach Workbench-v1

Die lokale Workbench-v1 ist als rein lokale Browser-Workbench abgeschlossen. Sie stellt Backend-Health und Version, statische Frontend-Auslieferung, lesende Szenario- und Run-Metadaten, Detailansichten, Filter, Auswahlzusammenfassung, Betriebsdiagnose, Metadatenquelle, Konsistenzdiagnose und Readiness bereit.

Die lokalen CLI-Adapter decken Diagnose, Startplan, CLI-Uebersicht, Metadaten-Check, Preview, Dry-Run, Export, Roundtrip, Snapshot, expliziten Importbericht, Schreibvertrag, Schreibvertragspruefung, Run-Control-Vertrag, Run-Control-Request-Check, Run-Control-Queue und Run-Control-Preflight ab. Diese Werkzeuge bleiben lokal. Nur der explizite Metadatenimport mit `--db` und die explizite lokale Run-Control-Queue schreiben Metadaten in eine angegebene SQLite-Datei; keine dieser Grenzen startet eine Simulation.

Vorhandene lokale Run-Control-Bausteine sind:

- Run-Control-Vertrag (`ims.api.run_control_contracts`), rein beschreibend.
- Run-Control-Dry-Run-Vertrag (`ims.api.run_control_dry_run_contract`) und HTTP-Pruefpfad (`POST /api/run-control/dry-run`), ohne Schreiben und ohne Ausfuehrung.
- Run-Control-Request-Check (`ims.api.run_control_requests`), lokal validierend.
- Run-Control-Queue (`ims.api.run_control_queue`) und API-Vormerkung (`POST /api/run-control/queue`), explizit lokal und ohne Ausfuehrung.
- Run-Control-Queue-Aktionsplan (`ims.api.run_control_queue_action_plan`), lokal lesend und ohne Ausfuehrung.
- Run-Control-Preflight (`ims.api.run_control_preflight`), lesend und ohne Ausfuehrung.
- Workbench-Readiness und CLI-Uebersicht, die diese Grenzen sichtbar machen.
- Read-only Brueckenplanung zu Kernlauf-Diagnosen in
  `docs/plans/run_control_core_diagnostics_bridge_plan.md`; sie verbindet noch
  keinen neuen Codepfad, sondern beschreibt nur die spaetere gemeinsame Lesesicht
  auf Queue-Aktionsplan und Kernvalidierungsueberblick.
- Expliziter Ausfuehrungsfreigabeplan in
  `docs/plans/run_control_execution_release_plan.md`; er beschreibt den
  spaeteren Uebergang von validierter Queue zu kontrolliertem Adapterstart,
  setzt ihn aber in PR 43 noch nicht um.

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
| Workbench nach v1 vollstaendig nutzbarer machen | ca. `0-1` PRs | lokale Aktionsplaene, lesende Queue-/Run-Control-Anzeigen, kontrollierte Dry-Run-Pruefung, Queue-Vormerkung, Demo-Smoke und Demo-Checkliste sind vorbereitet; offen bleiben nur Review-Fixes oder ein spaeterer Ausfuehrungsadapter nach Freigabe |
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

PR 43 konkretisiert die Phase-5-Freigabegrenze als Plan. Der Plan erlaubt noch
keinen Startbutton, keinen Queue-Worker und keinen Adapterstart aus Run-Control;
er beschreibt nur Preconditions, verbotene Pfade und die PR-Reihenfolge bis zur
benutzbaren kontrollierten Demo-Simulation.

## Erwartete PR-Roadmap fuer den Workbench-Ausbau

1. PR 1: Run-Control-Dashboard/lesende Queue-Anzeige im Frontend mit clientseitigen Filtern, Hinweisen und lokalen Schrittlabels.
2. PR 2: API-Leseendpunkte fuer Queue/Requests, noch ohne Schreibpfad. Queue-Reads sind vorhanden; der Request-Vertrag wird als GET-Contract sichtbar.
3. PR 3: Kontrollierter HTTP-Dry-Run als Pruefpfad mit Request-DTO und UI-Ergebnis, ohne Queue-Schreiben, Metadatenschreiben oder Ausfuehrung. Erledigt.
4. PR 4: Kontrollierte lokale Queue-Schreibpfade ueber API nur nach erfolgreichem Dry-Run und expliziter SQLite-Quelle. Erledigt.
5. PR 5: Run-Control-Aktionsplan per API/UI sichtbar machen, weiter ohne Ausfuehrungsadapter. Erledigt.
6. PR 6: Lokaler Demo-Smoke fuer Dry-Run, Queue-Vormerkung und Aktionsplan, ohne Ausfuehrungsadapter. Erledigt.
7. PR 7: Lokale Demo-Checkliste mit Startbefehlen, UI-Reihenfolge und Grenzen ohne Simulation. Erledigt.
8. PR 8: Read-only Run-Control-Brueckenplan zu Kernlauf-Diagnosen, ohne neuen
   Endpunkt, Schreibpfad oder Runner-Start.
9. PR 9: Ausfuehrungsfreigabeplan fuer Run-Control dokumentieren, weiterhin
   ohne UI-Startbutton, Queue-Worker oder Adapterstart. Erledigt:
   `docs/plans/run_control_execution_release_plan.md`.
10. PR 10: API-Startvertrag fuer den kontrollierten Adapter hart gegated als
    read-only Vertrag bereitstellen. Erledigt:
    `python_port/ims/api/run_control_adapter_start_contract.py`,
    `GET /api/run-control/adapter-start-contract` und
    `docs/migration/run_control_adapter_start_contract.md`; weiterhin ohne
    POST-Start, UI-Startbutton, Queue-Worker, Persistenz oder Simulation.
11. PR 11+: Persistenz, UI-Flow, Ergebnisanzeige und Demo-Smoke erst in
    separaten PRs.
12. Weitere PRs: Haertung, Doku, Smoke-/E2E-Checks, Review-Fixes und Grenzkorrekturen.

## API- und DTO-Grenzen

Run-Control-DTOs sollen nur Metadaten und Absichten beschreiben. Erwartbare Felder sind `run_id`, `scenario_id`, `metadata_db`, `requested_by`, `created_at`, `execution_enabled=false`, Status, Quelle und Validierungs-/Preflight-Ergebnis. Fachlogikdaten, Simulationsergebnisse und Legacy-Vergleichsdaten gehoeren nicht in diese DTOs.

HTTP-Vertraege duerfen erst eingefuehrt werden, wenn ihre Schreib- und Ausfuehrungsgrenzen testbar sind. Der erste freigegebene HTTP-Pfad bleibt ein reiner Dry-Run-Check: Er akzeptiert nur das Run-Control-Request-DTO, kombiniert es mit Preflight und schreibt keine Queue oder Metadaten. Der erste HTTP-Schreibpfad darf nur Queue-Metadaten in eine explizit konfigurierte SQLite-Quelle vormerken, nachdem derselbe Dry-Run bestanden wurde. Fehlerformen sollen stabil, knapp und maschinenlesbar sein.

## Repository- und SQLite-Grenzen

SQLite bleibt die lokale Metadatenablage. Run-Control-Metadaten oder Queue-Eintraege duerfen nur ueber klar benannte Repository-Methoden geschrieben werden. Die lokale Queue darf validierte Requests vormerken, aber keinen Worker, Scheduler oder Simulationslauf starten.

Lesende Diagnose-, Snapshot-, Export-, Roundtrip- und Preflight-Pfade duerfen keine Datenbankdateien erzeugen. Schreibpfade muessen einen expliziten Zielpfad verlangen und duerfen keine Ausfuehrung starten. Fuer SQLite-Read-only-Zugriffe bleibt die WAL-Grenze explizit: Rollback-Journal-Datenbanken werden mit `mode=ro` gelesen, vollstaendige Live-WAL-Sidecars werden beruecksichtigt, unvollstaendige Sidecars werden abgelehnt und `immutable=1` ist nur fuer sidecar-freie WAL-Dateien zulaessig.

Der lokale Queue-Aktionsplan ist ein rein lesender Adapter zwischen Queue-Diagnose und Preflight:

```powershell
python -m ims.api.run_control_queue_action_plan --db .\.ims_workbench\metadata.sqlite
python -m ims.api.run_control_queue_action_plan --db .\.ims_workbench\metadata.sqlite --queue-id <id>
```

Er erzeugt stabile JSON-Felder fuer `status`, `mode = "run_control_queue_action_plan"`, `db_path`, `metadata_source`, optional `queue_id`, `queue_count`, `actions`, `issues`, `writes_performed = false` und `execution_performed = false`. Pro Queue-Eintrag werden `queue_id`, `run_id`, `scenario_id`, `queue_status`, `next_action`, `next_action_label`, `blocked_by`, `execution_allowed = false`, `writes_performed = false` und `execution_performed = false` sichtbar. `planned` ohne Blocker fuehrt nur zu `run_preflight`, `validated` ohne Blocker zu `await_execution_release`, `blocked` oder Diagnose-/Preflight-Hinweise zu `resolve_blockers`; unbekannte Statuswerte bleiben ein `inspect_queue_status`-Hinweis. Queue-only-Datenbanken und nicht initialisierte Queues bleiben stabile Hinweise statt Abstuerze.

Die Run-Control-Bruecke zu Kernlauf-Diagnosen darf diesen Aktionsplan nur mit
dem bestehenden `GET /api/core-validation/overview` zusammen anzeigen. Der
Brueckenmodus bleibt read-only:
`mode = "run_control_core_diagnostics_bridge"`,
`writes_performed = false`, `execution_performed = false`,
`inspect_core_validation_overview`, `await_precomputed_execution_summary` und
`resolve_core_validation_blockers` sind Hinweise, keine Ausfuehrung.
Der erste kleine Code-Schnitt war ein reines Python-DTO:
`ims.api.run_control_core_diagnostics_bridge.build_run_control_core_diagnostics_bridge`.
Der aktuelle API-Schnitt macht denselben Vertrag ueber
`GET /api/run-control/core-diagnostics-bridge` lesend verfuegbar. Die
Workbench-Karte `Run-Control-Kernblick-Bruecke` zeigt diese Antwort nur
lesend; sie ist kein Startpfad und kein Ausfuehrungsadapter.

## Sicherheitsgrenzen

- `execution_enabled` bleibt bis zur expliziten Ausfuehrungsfreigabe `false`.
- `execution_performed` bleibt in Plan-, Diagnose-, Dry-Run- und Preflight-Pfaden `false`.
- Eine Run-Control-Bruecke zu Kernlauf-Diagnosen bleibt read-only und darf
  keinen neuen Schreib- oder Ausfuehrungspfad oeffnen.
- Die Ausfuehrungsfreigabe ist in PR 43 nur geplant; kein API-Pfad setzt
  `api_starts_adapter = true`.
- Kein Startbutton mit echter Funktion.
- Keine stille Fachlogikmutation.
- Keine Simulation im Plan-PR.
- Kein Packaging im Plan-PR, nur Planung.
- Keine historische Vollgleichheitsbehauptung.

## UI-Grenzen

Die UI darf geplante Run-Control-Metadaten anzeigen, filtern und als Preflight-Ergebnis erklaeren. Sie darf nur die kontrollierte Queue-Vormerkung nach erfolgreichem Dry-Run und expliziter SQLite-Quelle ausloesen. Upload, Editor, Browser-Download und funktionaler Run-Start bleiben ausgeschlossen.

UI-Texte sollen operational, knapp und ruhig bleiben. Die Workbench bleibt ein Werkzeug, keine Marketing-Oberflaeche.

## Teststrategie

Die Run-Control-Schritte brauchen Tests auf mehreren Ebenen:

- DTO- und Vertragsform: Pflichtfelder, verbotene Felder, stabile Fehlerformen.
- Repository/SQLite: explizite Schreibpfade, atomare Grenzen, keine implizite Datei-Erzeugung.
- CLI/Dry-Run/Preflight: stabile JSON-Formen, `writes_performed = false`, `execution_performed = false`.
- HTTP-Vertraege: zunaechst gesperrt oder Dry-Run, keine echte Ausfuehrung.
- Frontend: rein lesende Anzeige, kein Startbutton mit Funktion, keine Schreibcontrols.
- Demo-Smoke: Browser-Ablauf Dry-Run pruefen, Queue vormerken, Run-Control-Aktionsplan ansehen und Run-Control-Kernblick-Bruecke lesen, mit stabilen UI-Ankern, Screenshot-Beleg und `execution_performed = false`.
- Doku-Smokes: keine Fachlogikaenderung, keine historische Vollgleichheitsbehauptung, Packaging/Bereitstellung als eigener spaeterer Block.

## Nicht-Ziele dieses Plan-PRs

- Keine Fachlogikaenderung.
- Keine Simulation starten.
- Keine weiteren HTTP-Schreibendpunkte ausser der kontrollierten Queue-Vormerkung.
- Kein HTTP-Schreibpfad ausser Queue-Metadaten nach erfolgreichem Dry-Run und expliziter SQLite-Quelle.
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
