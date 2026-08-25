# Eingefrorene Workbench-Release-Checkliste

## Zweck und Stand

Diese Checkliste ist der technische Freigabevertrag `pr67-v1` fuer ein lokales
Workbench-ZIP. Sie gilt ab PR 67 und fasst die bereits vorhandenen Build-, ZIP-,
Staging- und Startgrenzen zusammen.

Die Checkliste ist kein Installervertrag, keine Simulation und kein Nachweis
historischer Vollgleichheit. Ein ZIP wird nur dann als lokal release-bereit
gemeldet, wenn jeder Pflichtcheck erfolgreich ist.

## Pflichtreihenfolge

1. Frontend im Checkout bauen:

   ```powershell
   npm.cmd run build --prefix .\frontend
   ```

2. Einen expliziten, leeren Arbeitsbereich fuer ZIP und Staging vorbereiten.
   Weder `dist` noch das portable Ziel werden versioniert.
3. ZIP erzeugen:

   ```powershell
   python -m ims.api.workbench_bundle_build --root . --frontend-dist frontend/dist --out <arbeitsbereich>\ims-workbench-local.zip
   ```

4. ZIP direkt pruefen:

   ```powershell
   python -m ims.api.workbench_bundle_smoke --zip-path <arbeitsbereich>\ims-workbench-local.zip
   ```

5. ZIP in einen fehlenden oder leeren portablen Zielordner stagen:

   ```powershell
   python -m ims.api.workbench_portable_staging --zip-path <arbeitsbereich>\ims-workbench-local.zip --out <arbeitsbereich>\ims-workbench
   ```

6. Staging und portable Pfade rein lesend pruefen:

   ```powershell
   python -m ims.api.workbench_portable_staging_smoke --root <arbeitsbereich>\ims-workbench
   python -m ims.api.workbench_portable_readiness --root <arbeitsbereich>\ims-workbench --layout portable
   ```

7. Eingefrorenen Sammelcheck ausfuehren:

   ```powershell
   python -m ims.api.workbench_release_smoke --repo-root . --zip-path <arbeitsbereich>\ims-workbench-local.zip --portable-root <arbeitsbereich>\ims-workbench
   ```

8. `check-workbench.cmd` aus dem portablen Root ausfuehren. Der Check darf
   keinen Server starten und keine fehlende Metadatendatenbank erzeugen.
9. `start-workbench.cmd` auf einem freien Loopback-Port starten und nur
   `GET /api/health` pruefen. Danach den Prozess kontrolliert beenden.

## Freigabegates

- `bundle_ready = true`: ZIP-Smoke ist ohne Issues erfolgreich.
- `portable_ready = true`: Staging-Smoke und portable Readiness sind gruen.
- `artifact_scripts_match_repo = true`: ZIP-Skripte entsprechen dem geprueften
  Checkout; unterschiedliche Zeilenenden werden kanonisch verglichen.
- `production_scripts_ready = true`: Repo-, ZIP- und portable Skripte erfuellen
  ihren Check- oder Startvertrag.
- `pr66_demo_adapter_separated = true`: kein Produktionsskript referenziert
  `run_control_browser_demo_smoke`, `controlled_smoke_adapter` oder
  `ims.api.controlled_execution_adapter`.
- `release_ready = true`: alle Pflichtgates sind erfuellt.
- `writes_performed = false`, `execution_performed = false` und
  `simulation_performed = false`: Der Sammelcheck selbst bleibt rein lesend.

## Lokale Nachweise

Der konkrete PR-Smoke dokumentiert mindestens:

- Frontend-Build erfolgreich;
- ZIP erstellt, CRC-geprueft und mit stabilen Metadaten gelesen;
- portable Struktur in einem neuen lokalen Ziel gestaged;
- Check-Skript erfolgreich;
- normaler Produktionsstart ueber `ims.api.app:app` auf Loopback erreichbar;
- Health-Endpunkt per GET erfolgreich;
- Prozess danach beendet;
- keine Run-Control-Aktion, kein Adapterstart und keine Simulation ausgeloest.

ZIP, Staging-Verzeichnis, lokale SQLite-Dateien und Logs bleiben unversionierte
Pruefarbeitsdaten.

## PR-67-Nachweis vom 2026-08-25

- Frontend-Build: erfolgreich, 1.578 transformierte Module.
- ZIP-Build: erfolgreich, 110 Dateien und nichtleere SHA-256-Pruefsumme.
- ZIP-Smoke: `status = ok`, stabile Metadaten, CRC lesbar, keine verbotenen
  Eintraege.
- Portables Staging: 106 gestagte Dateien einschliesslich der zwei generierten
  Skripte; Staging-Smoke und Readiness jeweils `status = ok`.
- Sammelcheck: `release_ready = true`,
  `artifact_scripts_match_repo = true`,
  `pr66_demo_adapter_separated = true`.
- Portables `check-workbench.cmd`: Diagnose und Readiness jeweils
  `status = ok`, ohne Metadatendatenbank.
- Portables `start-workbench.cmd`: normaler Start von `ims.api.app:app` auf
  `127.0.0.1:8127`; `GET /api/health` antwortete mit HTTP 200,
  `status = ok` und `frontend_available = true`; Prozess danach beendet.
- Es wurde keine Run-Control-Aktion, kein Adapter und keine Simulation
  gestartet.

## Grenzen

- Der PR-66-Fake-Adapter bleibt ausschliesslich in seiner isolierten
  Browser-Smoke-Testschale.
- Kein Browser-Upload, Queue-Worker oder automatischer Updater.
- Keine neue Fachlogik und keine automatische historische Regelwahl.
- Keine historische Vollgleichheitsbehauptung.
- Backup/Restore und Update/Rollback lokaler Metadaten folgen getrennt in
  PR 68.
