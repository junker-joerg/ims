# Lokale Workbench-Demo-Checkliste

Diese Checkliste beschreibt den aktuellen lokalen Demo-Schnitt der IMS Workbench. Sie ist eine Vorfuehr- und Bediennotiz, kein Release-Tag, keine Fachvalidierung, keine Simulation und keine historische Vollgleichheitsbehauptung.

## Demo-Ziel

Die Demo zeigt, dass die lokale Browser-Workbench einen Run-Control-Wunsch kontrolliert vorbereiten kann:

1. vorhandene Szenario- und Run-Metadaten lesen
2. Run-Control-Grenzen sichtbar machen
3. HTTP-Dry-Run fuer `baseline-python-tests` pruefen
4. Queue-Vormerkung in einer expliziten SQLite-Metadatenquelle schreiben
5. Run-Control-Aktionsplan lesen und `run_preflight` als naechsten sicheren Schritt anzeigen

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
3. Run-Control-Statusband lesen: Queue, Preflight, Request-Vertrag, Dry-Run, Queue-Vormerkung und Aktionsplan sind getrennt sichtbar.
4. `Dry-Run pruefen` klicken.
5. Erwartung nach Dry-Run: Request akzeptiert, Preflight ok, Szenario passt, Schreibpfade gesperrt, Ausfuehrung gesperrt.
6. `Queue vormerken` klicken.
7. Erwartung nach Queue-Vormerkung: Status `vorgemerkt`, Queue-ID `baseline-python-tests`, Schreibpfad `Queue geschrieben`, Ausfuehrung gesperrt.
8. Run-Control-Aktionsplan lesen.
9. Erwartung im Aktionsplan: `Naechste Aktion = run_preflight`, Blocker `keine`, Schreibpfade gesperrt, Ausfuehrung gesperrt.

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

Run-Control-Aktionsplan und Kernvalidierungsueberblick sind in dieser Demo noch
nebeneinanderliegende Lesesignale. Die spaetere Verbindung ist nur als
read-only Brueckenplan unter
`docs/plans/run_control_core_diagnostics_bridge_plan.md` dokumentiert und
schaltet keinen Startpfad frei.

## Was demo-faehig ist

- lokale Browser-Workbench mit gebautem Frontend
- Backend-Health, Version, Metadatenquelle und Betriebsdiagnose
- lesende Szenario- und Run-Uebersichten mit Details, Filtern und Auswahlzusammenfassung
- Konsistenzdiagnose fuer Workbench-Metadaten
- Run-Control-Request-Vertrag, Dry-Run-Vertrag und Preflight-Anzeige
- kontrollierter HTTP-Dry-Run ohne Schreiben
- kontrollierte Queue-Vormerkung in expliziter SQLite-Datei
- lesender Run-Control-Aktionsplan mit `run_preflight`
- lesender Kernvalidierungsueberblick fuer vorhandene VU/VN-Periodenplaene und Legacy-Abdeckung
- Browser-/Screenshot-Smoke ueber stabile UI-Anker

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

Der Demo-Screenshot belegt nur Bedienbarkeit und sichtbare Grenzen. Er belegt keine historischen Fachwerte und ersetzt keine spaetere Alt-/Neu-Fachvalidierung.

## Schnelle Pruefung vor der Demo

```powershell
python -m pytest -q tests/test_workbench_demo_smoke.py tests/test_frontend_shell.py tests/test_workbench_documentation.py
npm.cmd run build --prefix .\frontend
```

Diese Pruefung startet keine Simulation. Der Browser-Durchlauf wird separat lokal durchgefuehrt, damit der sichtbare UI-Zustand geprueft werden kann.
