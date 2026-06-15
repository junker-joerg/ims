# Workbench Run-Control Plan nach v1

Dieses Dokument plant den naechsten Modernisierungsblock nach der abgeschlossenen lokalen Workbench-v1. Es ist ein Planungsstand, keine Implementierung: Es startet keine Simulation, oeffnet keine Schreibpfade, aendert keine Fachlogik und behauptet keine historische Vollgleichheit.

## Ausgangspunkt nach Workbench-v1

Die lokale Workbench-v1 ist als rein lokale Browser-Workbench abgeschlossen. Sie stellt Backend-Health und Version, statische Frontend-Auslieferung, lesende Szenario- und Run-Metadaten, Detailansichten, Filter, Auswahlzusammenfassung, Betriebsdiagnose, Metadatenquelle, Konsistenzdiagnose und Readiness bereit.

Die lokalen CLI-Adapter decken Diagnose, Startplan, CLI-Uebersicht, Metadaten-Check, Preview, Dry-Run, Export, Roundtrip, Snapshot, expliziten Importbericht, Schreibvertrag, Schreibvertragspruefung, Run-Control-Vertrag und Run-Control-Preflight ab. Diese Werkzeuge bleiben lokal. Nur der explizite Metadatenimport mit `--db` schreibt Metadaten in eine angegebene SQLite-Datei; keine dieser Grenzen startet eine Simulation.

## Zielbild

Das Zielbild bleibt eine kleine portable IMS Workbench fuer lokale Nutzung im Browser. UI, Backend/API, Metadatenhaltung, spaetere Ausfuehrungsadapter und Python-Fachlogik bleiben sauber getrennt. Die Workbench soll spaeter kontrolliert Run-Anfragen vorbereiten, anzeigen, validieren und nach separater Freigabe an einen eng abgegrenzten Ausfuehrungsadapter uebergeben koennen.

Bis zu dieser separaten Freigabe bleibt `execution_enabled` auf `false`. Es gibt keinen funktionalen Startbutton, keine stille Fachlogikmutation und keine historische Vollgleichheitsbehauptung.

## Gesamtplanung bis wirklich alles fertig

Die Restplanung bis zum vollstaendigen Abschluss inklusive Workbench-Ausbau, Fachvalidierung, historischer Vollgleichheit und Packaging/Bereitstellung bleibt bewusst grob:

- Erwartet: ca. `33-50+` reviewbare PRs.
- Realistische Mitte: ca. `44` PRs.
- Optimistisch: ca. `33-38` PRs.
- Realistisch: ca. `40-48` PRs.
- Mit schwieriger Fachvalidierung oder Packaging-Fallen: `50+` PRs.

Geplante Bloecke:

| Block | Erwarteter Umfang | Inhalt |
| --- | ---: | --- |
| Workbench nach v1 vollstaendig nutzbarer machen | ca. `12-20` PRs | kontrollierte Run-Steuerung, lokale Schreibpfade, UI-Vorbereitung, spaeterer Ausfuehrungsadapter, Haertung, Doku und E2E-Smokes |
| Fachvalidierung und historische Vollgleichheit | ca. `10-18` PRs | weitere Legacy-Referenzen, zusaetzliche Alt-/Neu-Vergleichspfade, Mehrperioden-Replays, Abweichungsanalyse, Modellkorrekturen und Abschlussbericht |
| Packaging und Bereitstellung | ca. `8-14` PRs | lokale Startbarkeit, portable Ordnerstruktur, Startskripte/Launcher, reproduzierbarer Build, ZIP-/Release-Artefakte, Installations-, Update- und Backup-Doku |
| Integrations- und Abschlussreserve | ca. `3-5` PRs | Review-Fixes, CI- und Windows-Pfadhaertung, finale Doku-Konsolidierung und Meilensteinabschluss |

Diese Planung ist keine Zusage auf historische Vollgleichheit. Fachvalidierung und historische Vollgleichheit bleiben eigene spaetere Bloecke mit separaten Referenzfenstern, Vergleichspfaden und Abschlusskriterien.

## Run-Control-Phasen

Phase 1: Rein lokale Run-Control-Requests als DTO und CLI, ohne Ausfuehrung.

Phase 2: Persistierte Run-Control-Metadaten oder Queue in SQLite, weiterhin ohne Fachlogiklauf.

Phase 3: HTTP-Vertrag fuer Run-Control-Requests, zunaechst gesperrt oder als Dry-Run, ohne echte Ausfuehrung.

Phase 4: UI-Bedienflaeche fuer geplante Run-Control-Pfade, ohne funktionalen Start.

Phase 5: Kontrollierter Adapter zur spaeteren Simulationsausfuehrung, erst nach separater expliziter Freigabe und mit enger Fachlogikgrenze.

Phase 6: Haertung, Doku, Smoke-/E2E-Pruefung und Abschlusskonsolidierung.

## Erwartete PR-Roadmap fuer den Workbench-Ausbau

1. PR 1: Run-Control-Plan und Roadmap.
2. PR 2: Run-Control-Request-DTO und lokale Validierung. Dieser Schritt fuehrt nur ein lokales Request-Format und einen Check ein; er startet keine Ausfuehrung.
3. PR 3: Run-Control-Queue/Repository in SQLite, ohne Ausfuehrung. Dieser Schritt speichert nur validierte Request-Metadaten in einer expliziten lokalen Queue.
4. PR 4: CLI-Dry-Run fuer Run-Control-Requests.
5. PR 5: Gesperrte HTTP-Vertraege fuer Run-Control.
6. PR 6: Metadaten-Schreibpfade kontrolliert vorbereiten.
7. PR 7: UI-Anzeige fuer geplante Run-Control-Requests.
8. PR 8: UI-Dry-Run/Preflight-Ansicht ohne Start.
9. PR 9: Ausfuehrungsadapter-Plan und Fachlogikgrenze.
10. PR 10-12: Kontrollierte Adapterimplementierung nur nach expliziter Freigabe.
11. PR 13-15: Haertung, Doku, Smoke-/E2E-Checks und Abschluss.
12. Zusaetzlich 3-5 Puffer-PRs fuer Review-Fixes, CI-Haertung und Grenzkorrekturen.

## API- und DTO-Grenzen

Run-Control-DTOs sollen nur Metadaten und Absichten beschreiben. Erwartbare Felder sind `run_id`, `scenario_id`, `metadata_db`, `requested_by`, `created_at`, `execution_enabled=false`, Status, Quelle und Validierungs-/Preflight-Ergebnis. Fachlogikdaten, Simulationsergebnisse und Legacy-Vergleichsdaten gehoeren nicht in diese DTOs.

HTTP-Vertraege duerfen erst eingefuehrt werden, wenn ihre Schreib- und Ausfuehrungsgrenzen testbar sind. Zunaechst muessen sie gesperrt oder reine Dry-Run-Vertraege bleiben. Fehlerformen sollen stabil, knapp und maschinenlesbar sein.

## Repository- und SQLite-Grenzen

SQLite bleibt die lokale Metadatenablage. Run-Control-Metadaten oder Queue-Eintraege duerfen nur ueber klar benannte Repository-Methoden geschrieben werden. Die lokale Queue darf validierte Requests vormerken, aber keinen Worker, Scheduler oder Simulationslauf starten.

Lesende Diagnose-, Snapshot-, Export-, Roundtrip- und Preflight-Pfade duerfen keine Datenbankdateien erzeugen. Schreibpfade muessen einen expliziten Zielpfad verlangen und duerfen keine Ausfuehrung starten.

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
- Keine neuen HTTP-Endpunkte.
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

Fachvalidierung und historische Vollgleichheit bleiben eigene spaetere Bloecke von ca. `10-18` PRs. Packaging und Bereitstellung bleiben ein eigener Block von ca. `8-14` PRs. Beide duerfen nicht als Nebeneffekt der Run-Control-Planung umgesetzt oder behauptet werden.
