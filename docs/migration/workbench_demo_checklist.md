# Lokale Workbench-Demo-Checkliste

Diese Checkliste beschreibt den aktuellen lokalen Demo-Schnitt der IMS Workbench. Sie ist eine Vorfuehr- und Bediennotiz, kein Release-Tag, keine Fachvalidierung, keine Simulation und keine historische Vollgleichheitsbehauptung.

## Demo-Ziel

Die Demo zeigt, dass die lokale Browser-Workbench einen Run-Control-Wunsch kontrolliert vorbereiten kann:

1. vorhandene Szenario- und Run-Metadaten lesen
2. Run-Control-Grenzen sichtbar machen
3. HTTP-Dry-Run fuer `baseline-python-tests` pruefen
4. Queue-Vormerkung in einer expliziten SQLite-Metadatenquelle schreiben
5. Run-Control-Aktionsplan lesen und `run_preflight` als naechsten sicheren Schritt anzeigen
6. Run-Control-Ausfuehrungsflow als gesperrte Statussicht anzeigen
7. Run-Control-Ergebnisanzeige als read-only Ergebnisblick anzeigen

Die Demo zeigt keine fachliche Ausfuehrung. `execution_enabled` und `execution_performed` bleiben `false`.

## Lokaler Start

Vor der Demo muss das Frontend gebaut sein:

```powershell
cd C:\Users\mjkoe\Documents\Codex\ims
npm.cmd run build --prefix .\frontend
```

Fuer die Demo wird eine explizite lokale SQLite-Metadatenquelle gesetzt. Das erlaubt nur die Queue-Vormerkung als Metadaten-Schreibpfad:

```powershell
$env:IMS_METADATA_DB = ".\.ims_workbench\demo-metadata.sqlite"
$env:IMS_FRONTEND_DIST = ".\frontend\dist"
python -m uvicorn ims.api.app:app --app-dir python_port --host 127.0.0.1 --port 8000
```

Danach ist die Workbench lokal unter `http://127.0.0.1:8000/` erreichbar.

## Demo-Ablauf in der UI

1. Dashboard oeffnen und Metadatenquelle pruefen: erwarteter Hinweis `SQLite-Datei`.
2. Auswahl pruefen: erwarteter Run `baseline-python-tests`, erwartetes Szenario `agrsich-reference-window`.
3. Run-Control-Statusband lesen: Queue, Preflight, Request-Vertrag, Dry-Run, Adapter-Resultat-Vertrag, Queue-Vormerkung und Aktionsplan sind getrennt sichtbar.
4. `Dry-Run pruefen` klicken.
5. Erwartung nach Dry-Run: Request akzeptiert, Preflight ok, Szenario passt, Schreibpfade gesperrt, Ausfuehrung gesperrt.
6. `Queue vormerken` klicken.
7. Erwartung nach Queue-Vormerkung: Status `vorgemerkt`, Queue-ID `baseline-python-tests`, Schreibpfad `Queue geschrieben`, Ausfuehrung gesperrt.
8. Run-Control-Aktionsplan lesen.
9. Erwartung im Aktionsplan: `Naechste Aktion = run_preflight`, Blocker `keine`, Schreibpfade gesperrt, Ausfuehrung gesperrt.
10. Run-Control-Ausfuehrungsflow lesen.
11. Erwartung im Flow: `Preflight -> explizite Freigabe -> Ausfuehren` ist sichtbar, `api_starts_adapter = false`, `ui_start_enabled = false`, `queue_worker_enabled = false`.
12. Run-Control-Ergebnisanzeige lesen.
13. Erwartung in der Ergebnisanzeige: kein Upload, kein Startpfad, bei fehlendem persistiertem Ergebnis `kein persistiertes Ergebnis`, Schreibpfade gesperrt, Ausfuehrung gesperrt.
14. Run-Control-Kernblick-Bruecke lesen.
15. Erwartung in der Bruecke: `Brueckenaktion = resolve_core_validation_blockers`, Summary-Schritt `await_precomputed_execution_summary`, Schreibpfade gesperrt, Ausfuehrung gesperrt.
16. Carryover-Probe-Vertrag lesen.
17. Erwartung im Vertrag: `api_starts_probe = false`, `api_accepts_probe_payload = false`, `ui_enabled = false`, `simulation_performed = false`.
18. Adapter-Resultat-Vertrag lesen.
19. Erwartung im Vertrag: `api_starts_adapter = false`, `api_accepts_result_payload = false`, `api_validates_result_payload = false`, `ui_enabled = false`, `simulation_performed = false`.

## Optionaler lesender Kernblick

Nach dem Run-Control-Demo-Pfad kann die Demo den Kernvalidierungsueberblick als rein lesenden Fachlogik-Ausblick zeigen. Dieser Blick ist kein Start eines Kernlaufs.

Lokale Diagnosebefehle fuer denselben Stand:

```powershell
$env:PYTHONPATH = "python_port"
python -m ims.engine.explicit_period_diagnostics tests/fixtures/replay_vu14_period_plan.json
python -m ims.engine.explicit_period_diagnostics tests/fixtures/replay_vusk1_period_plan.json
python -m ims.engine.explicit_period_diagnostics_bundle tests/fixtures/replay_vu14_period_plan.json tests/fixtures/replay_vusk1_period_plan.json
python -m ims.engine.core_validation_overview --legacy-fixture tests/fixtures/legacy_validation_bundle.json tests/fixtures/replay_vu14_period_plan.json tests/fixtures/replay_vusk1_period_plan.json
```

Aktueller Diagnosebefund:

- `explicit_period_diagnostics_bundle`: Status `ok`, 2 Planfixtures, 8 Perioden, globale Perioden `1, 2, 3, 4, 101, 102, 103, 104`.
- Legacy-Bezug im Bundle: 2 Legacy-Ziele (`VU14L1.DAT`, `VUSK1L4.DAT`).
- `ims_core_validation_overview`: Status `warning`, weil die naechste Validierungsaktion weiter `await_historical_reference` bleibt.
- Legacy-Abdeckung im Ueberblick: 19 Referenzen, 6300 abgedeckte Zeilen und 6300 abgedeckte Perioden.
- Execution-Summary-Vertrag: `execution_summary_available = false`, `execution_summary_next_action = await_precomputed_execution_summary`.
- Grenzwerte: `overview_starts_runner = false`, `overview_accepts_summary_input = false`, `writes_performed = false`, `execution_performed = false`.

In der UI ist dieser Blick die Karte `Kernvalidierungsueberblick`. Sie darf Periodenplaene, Legacy-Abdeckung und den Execution-Summary-Vertrag anzeigen. Sie darf keine Summary-Datei annehmen, keinen Periodenrunner starten und keine Fachlogik ausfuehren.

Die Karte `Carryover-Probe-Vertrag` zeigt den read-only Vertrag fuer vorab
berechnete `explicit_transition_carryover_probe`-Payloads. Sie darf keinen
Probe-Payload annehmen, keinen Probe starten, keinen Ausfuehrungsadapter
aktivieren und keine automatische historische Regelwahl ableiten.

Die Karte `Adapter-Resultat-Vertrag` zeigt den read-only Vertrag fuer vorab
lokal gepruefte `controlled_execution_adapter`-Resultate. Sie darf keinen
Resultat-Payload annehmen, kein Resultat ueber HTTP validieren, keinen
Dateipicker anbieten, keinen Adapter starten und keine automatische historische
Regelwahl ableiten.

Die Karte `Run-Control-Kernblick-Bruecke` zeigt den Run-Control-Aktionsplan und
den Kernvalidierungsueberblick als gemeinsame Lesesicht. Sie darf nur
`GET /api/run-control/core-diagnostics-bridge` anzeigen, keinen Startpfad
freischalten, keinen Upload anbieten und keinen Ausfuehrungsadapter aktivieren.
Sie schaltet keinen Startpfad frei.
Der geplante Brueckenschnitt ist in `docs/plans/run_control_core_diagnostics_bridge_plan.md`
dokumentiert.

Die Karte `Run-Control-Ausfuehrungsflow` zeigt den Ablauf
`Preflight -> explizite Freigabe -> Ausfuehren` nur als Statussicht auf
Preflight, Aktionsplan, Adapter-Startvertrag und Queue-Ergebnisstatus. Sie
enthaelt keinen UI-Startbutton, keinen Queue-Worker und keinen Adapterstart.

Die Karte `Run-Control-Ergebnisanzeige` zeigt ein vorhandenes persistiertes
Adapterresultat ueber `GET /api/run-control/execution-result/{queue_id}` nur
lesend. Sie nimmt keinen Payload an, bietet keinen Dateipicker an, startet
keinen Adapter und schreibt keine Metadaten.

## Was demo-faehig ist

- lokale Browser-Workbench mit gebautem Frontend
- Backend-Health, Version, Metadatenquelle und Betriebsdiagnose
- lesende Szenario- und Run-Uebersichten mit Details, Filtern und Auswahlzusammenfassung
- Konsistenzdiagnose fuer Workbench-Metadaten
- Run-Control-Request-Vertrag, Dry-Run-Vertrag und Preflight-Anzeige
- kontrollierter HTTP-Dry-Run ohne Schreiben
- kontrollierte Queue-Vormerkung in expliziter SQLite-Datei
- lesender Run-Control-Aktionsplan mit `run_preflight`
- lesender Run-Control-Ausfuehrungsflow mit gesperrtem Ausfuehren-Schritt und stabilem UI-Anker `run-control-execution-flow`
- lesende Run-Control-Ergebnisanzeige fuer persistierte Adapterresultate mit stabilem UI-Anker `run-control-execution-result`
- lesender Kernvalidierungsueberblick fuer vorhandene VU/VN-Periodenplaene und Legacy-Abdeckung
- lesender Carryover-Probe-Vertrag fuer vorab berechnete Probe-Payloads ohne Upload oder Startpfad
- lesender Adapter-Resultat-Vertrag fuer vorab lokal gepruefte Adapter-Resultate ohne Upload, HTTP-Validierung oder Startpfad
- lesende Run-Control-Kernblick-Bruecke ohne Startpfad
- Browser-/Screenshot-Smoke ueber stabile UI-Anker einschliesslich `run-control-execution-flow`, `run-control-execution-result`, `run-control-core-bridge`, `carryover-probe-contract` und `adapter-result-contract`

## Was noch nicht demo-faehig ist

- echte Simulation oder Periodenrunner-Ausfuehrung
- vorab berechnete Execution-Summary als UI-Eingabe
- Ausfuehrungsadapter hinter `run_preflight`
- fachlicher Gleichheitsnachweis gegen historische IMS/ESS-Laeufe
- Szenario-Editor, Browser-Upload oder Browser-Download
- automatische SQLite-Migration, automatischer Updater oder Installer
- produktiver Release-Prozess

## Vorfuehrgrenzen

Die Queue-Vormerkung ist der einzige in der Demo erwartete UI-ausgeloeste Schreibvorgang. Sie schreibt nur Queue-Metadaten in die explizite SQLite-Datei. Sie startet keinen Worker, keinen Scheduler, keinen Simulationslauf und keine Fachlogikmutation.

Der Demo-Screenshot belegt nur Bedienbarkeit, sichtbare Grenzen, die gesperrte Ausfuehrungsflow-Karte, die read-only Ergebnisanzeige, die gesperrte Carryover-Probe-Vertragskarte und die gesperrte Adapter-Resultat-Vertragskarte. Er belegt keine historischen Fachwerte und ersetzt keine spaetere Alt-/Neu-Fachvalidierung.

## Schnelle Pruefung vor der Demo

```powershell
python -m pytest -q tests/test_workbench_demo_smoke.py tests/test_frontend_shell.py tests/test_workbench_documentation.py
npm.cmd run build --prefix .\frontend
```

Diese Pruefung startet keine Simulation. Der Browser-Durchlauf wird separat lokal durchgefuehrt, damit der sichtbare UI-Zustand geprueft werden kann.
