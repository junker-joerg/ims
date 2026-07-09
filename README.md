# ims

Dieses Repository enthält das Arbeitsgerüst für eine schrittweise, PR-basierte und semantisch konservative Migration von IMS.
Weitere Hinweise stehen unter `docs/migration/README.md`.

## Lokale Workbench

Die lokale Workbench-v1 ist unter `docs/migration/workbench_shell.md` beschrieben. Sie laeuft zuerst lokal im Browser und bleibt bewusst von der Fachlogik getrennt.

Kurzstart fuer die lokale Browser-Workbench:

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

Danach ist die Workbench lokal unter `http://127.0.0.1:8000/` erreichbar. Die aktuelle Workbench ist weiterhin rein lesend: keine Simulation, kein Browser-Upload und keine HTTP-/UI-Schreibpfade.

Alternativ stehen erste lokale Windows-Skripte bereit:

```powershell
scripts\workbench\check-workbench.cmd
scripts\workbench\start-workbench.cmd
```

Die Skripte setzen ein gebautes `frontend/dist` voraus. Das Check-Skript fuehrt Diagnose und Readiness aus, startet aber keinen dauerhaften Server. Das Start-Skript startet nur den lokalen Backend-Server.

Lokaler Workbench-v1 Abschlussstatus:

Die lokale Workbench-v1 ist als Modernisierungs-Meilenstein abgeschlossen. Dieser Abschluss ist kein Release-Tag, keine Fachvalidierung und keine historische Vollgleichheitsbehauptung.

- Backend-Health und Version sind lokal verfuegbar.
- Das gebaute Frontend wird statisch ausgeliefert.
- Szenario- und Run-Metadaten sind lesend als Listen, Details, Filter und Auswahlzusammenfassung verfuegbar.
- Betriebsdiagnose, Metadatenquelle, Konsistenzdiagnose, Readiness und lokale CLI-Grenzen sind dokumentiert und getestet.
- Lokale CLI-Adapter decken Diagnose, Import-Check, Preview, Dry-Run, Export, Roundtrip, Snapshot, expliziten Importbericht und Run-Control-Preflight ab.
- Keine Fachlogikaenderung, keine Simulation, keine HTTP-/UI-Schreibpfade und keine historische Vollgleichheitsbehauptung.

Die spaetere Run-Steuerung und Gesamtplanung bis zum vollstaendigen Abschluss sind unter `docs/migration/workbench_run_control_plan.md` beschrieben. Der separate Packaging- und Bereitstellungsblock ist unter `docs/migration/workbench_packaging_plan.md` als lokaler ZIP-/Staging-Abschlussstatus konsolidiert. Diese Plaene und Checks starten keine Simulation.

Die lokale Demo-Checkliste fuer eine kurze Vorfuehrung steht unter `docs/migration/workbench_demo_checklist.md`. Sie benennt Startbefehle, UI-Reihenfolge, erwartete Demo-Signale und klare Grenzen: Queue-Metadaten duerfen nur in eine explizite SQLite-Datei vorgemerkt werden; Simulation, Ausfuehrungsadapter und fachlicher Gleichheitsnachweis bleiben ausgeschlossen.

Der Anschluss zur eigentlichen IMS-Kern-Fachlogik nach Workbench-v1 ist unter
`docs/plans/ims_core_fachlogik_resume_plan.md` geplant. Dieser Plan benennt den
naechsten fachlichen Diagnoseblock fuer vorhandene explizite VU/VN-Periodenplaene,
ohne neue Fachlogik, HTTP-Schreibpfade oder Ausfuehrung freizuschalten.
Die spaetere rein lesende Verbindung zwischen Run-Control-Aktionsplan und
Kernlauf-Diagnosen ist unter
`docs/plans/run_control_core_diagnostics_bridge_plan.md` geplant. Der
read-only Endpunkt `GET /api/run-control/core-diagnostics-bridge` buendelt
Queue-Aktionsplan und Kernvalidierungsueberblick, bleibt aber ohne Schreibpfad,
ohne UI-Startpfad, ohne Runner-Start und ohne automatische Fachlogik.
Als erster rein lesender Kernblick kann
`python -m ims.engine.explicit_period_diagnostics tests/fixtures/replay_vu14_period_plan.json`
die vorhandene Planstruktur diagnostizieren, ohne Simulation, Runner-Start oder
Ausgabedateien.

Start und Diagnose:

Optional kann die Diagnose eine explizite lokale Konfigurationsdatei lesen:

```powershell
python -m ims.api.workbench_diagnostics --config .\workbench.local.json
```

Ein rein beschreibender Startplan kann dieselben lokalen Werte als JSON zusammenfassen, ohne den Server zu starten:

```powershell
python -m ims.api.workbench_start_plan --config .\workbench.local.json
```

Eine lokale v1-Bereitschaftspruefung buendelt Diagnose, Metadatenquelle, CLI-Grenzen, Run-Control-Preflight und bei expliziter SQLite-Quelle die Run-Control-Queue-Diagnose, ohne den Server zu starten:

```powershell
python -m ims.api.workbench_readiness --frontend-dist frontend/dist
```

Eine lokale Strukturpruefung prueft die heutige Repo-Struktur oder eine spaetere portable Workbench-Ordnerstruktur, ohne Dateien zu erzeugen:

```powershell
python -m ims.api.workbench_portable_readiness --root . --layout repo
```

Die Strukturpruefung validiert dabei auch, ob erwartete Dateien und Ordner den richtigen Pfadtyp haben.

Ein lokaler Build-Snapshot fasst vorhandene Frontend-/Backend-Artefakte zusammen, ohne Dateien zu kopieren oder ein ZIP zu erzeugen:

```powershell
python -m ims.api.workbench_build_snapshot --root . --frontend-dist frontend/dist
```

Ein lokales Artefaktmanifest beschreibt Ein- und Ausschlusspfade fuer ein spaeteres portables Artefakt, erzeugt aber noch kein ZIP:

```powershell
python -m ims.api.workbench_artifact_manifest --root . --frontend-dist frontend/dist
```

Das Manifest enthaelt fuer eingeschlossene Dateien relative Pfade, Groesse und SHA-256-Pruefsummen.

Ein lokaler Bundle-Trockenlauf nutzt dieses Manifest und beschreibt ein spaeteres ZIP-Bundle, ohne Dateien zu kopieren oder ein Archiv zu erzeugen:

```powershell
python -m ims.api.workbench_bundle_plan --root . --frontend-dist frontend/dist
```

Ein expliziter lokaler ZIP-Build kann daraus ein ZIP in einen angegebenen Zielpfad schreiben. Der Ausgabeordner wird vorher explizit angelegt, weil der ZIP-Build fehlende Output-Parents nicht automatisch erzeugt:

```powershell
New-Item -ItemType Directory .\dist -Force
python -m ims.api.workbench_bundle_build --root . --frontend-dist frontend/dist --out .\dist\ims-workbench-local.zip
```

Dieses ZIP ist ein lokales Bereitstellungsartefakt, kein Installer, kein Release-Tag und kein fachlicher Gleichheitsnachweis.
Der ZIP-Zielpfad darf nicht unter eingeschlossenen Quellbaeumen wie `python_port` oder `frontend/dist` liegen. ZIP-Eintraege werden mit stabilen Metadaten geschrieben, damit die `zip_sha256`-Pruefsumme bei identischem Inhalt reproduzierbar bleibt.

Lokaler Release-Ablauf fuer ein ZIP-Artefakt:

```powershell
npm.cmd run build
New-Item -ItemType Directory .\dist -Force
python -m ims.api.workbench_bundle_build --root . --frontend-dist frontend/dist --out .\dist\ims-workbench-local.zip
python -m ims.api.workbench_bundle_smoke --zip-path .\dist\ims-workbench-local.zip
python -m ims.api.workbench_portable_staging --zip-path .\dist\ims-workbench-local.zip --out .\ims-workbench
python -m ims.api.workbench_portable_staging_smoke --root .\ims-workbench
python -m ims.api.workbench_portable_readiness --root .\ims-workbench --layout portable
```

Dieser Ablauf ist ein lokaler Bereitstellungscheck fuer den tatsaechlich erzeugten ZIP-Inhalt und eine daraus explizit gestagte portable Zielstruktur unter `.\ims-workbench`. Portable Readiness mit `app\frontend\dist` ist erst nach diesem Staging-Schritt sinnvoll. Der Ablauf startet keine Simulation, oeffnet keinen HTTP- oder UI-Schreibpfad, installiert nichts automatisch und migriert keine SQLite-Datenbank.
Der ZIP-Smoke prueft erwartete Eintraege, ausgeschlossene lokale Daten, stabile ZIP-Metadaten sowie die Lesbarkeit der ZIP-Payloads inklusive CRC-Pruefung.
Das portable Staging erwartet einen fehlenden oder leeren Zielordner und ueberschreibt keine lokalen Nutzerdaten wie `metadata.sqlite`, WAL-/SHM-Dateien oder Logs. Der Staging-Smoke prueft danach die gestagte Backend-/Frontend-Struktur, die Backend-Importfaehigkeit aus dem gestagten Workbench-Root fuer die Check-/Startskriptgrenze und die portablen Startskriptgrenzen rein lesend.

Eine lokale CLI-Uebersicht listet die vorhandenen Befehle und ihre Grenzen, ohne Import, Snapshot oder Serverstart auszufuehren:

```powershell
python -m ims.api.workbench_cli_overview
```

Vertraege und Run-Control-Grenzen:

Ein lokaler Schreibvertrag beschreibt die vorbereiteten Metadaten-Schreibgrenzen, ohne einen Schreibpfad zu oeffnen:

```powershell
python -m ims.api.metadata_write_contracts
python -m ims.api.metadata_write_contracts check .\metadata_import.json
```

Ein lokaler Run-Control-Vertrag beschreibt die spaetere Steuerungsgrenze, ohne einen Lauf zu starten:

```powershell
python -m ims.api.run_control_contracts
python -m ims.api.run_control_dry_run_contract
```

Der Dry-Run-Vertrag beschreibt den kontrollierten HTTP-Pruefpfad. Die Workbench-API stellt ihn ueber `GET /api/run-control/dry-run-contract` bereit; `POST /api/run-control/dry-run` akzeptiert nur das Run-Control-Request-DTO mit `execution_enabled=false`, kombiniert es mit dem vorhandenen Preflight und schreibt keine Queue oder Metadaten. Es gibt keinen PUT, keinen Browser-Upload, keinen Schreibpfad und keine Simulation.

Ein lokaler Run-Control-Request-Check validiert eine spaetere Steuerungsanfrage als DTO, ohne sie zu speichern oder auszufuehren:

```powershell
python -m ims.api.run_control_requests check .\run_control_request.json
```

Die Workbench-API stellt denselben Request-Vertrag lesend bereit:

```text
GET /api/run-control/request-contract
```

Der Endpunkt gibt Pflichtfelder, optionale Felder, verbotene Felder und ein Beispiel-DTO zurueck. Er akzeptiert keinen Request-Body, validiert keinen Browser-Upload, schreibt keine Metadaten und startet keine Ausfuehrung.

Eine lokale Run-Control-Queue kann solche Requests in einer expliziten SQLite-Datei vormerken, ohne Ausfuehrung, Worker oder Scheduler zu starten:

```powershell
python -m ims.api.run_control_queue init --db .\.ims_workbench\metadata.sqlite
python -m ims.api.run_control_queue enqueue .\run_control_request.json --db .\.ims_workbench\metadata.sqlite
python -m ims.api.run_control_queue list --db .\.ims_workbench\metadata.sqlite
python -m ims.api.run_control_queue_diagnostics --db .\.ims_workbench\metadata.sqlite
python -m ims.api.run_control_queue_action_plan --db .\.ims_workbench\metadata.sqlite
```

`init` und `enqueue` sind die expliziten lokalen Queue-Schreibbefehle. `list`, `show`, `run_control_queue_diagnostics` und `run_control_queue_action_plan` lesen die Queue-Datenbank read-only. Die Diagnose prueft Queue-Schema, Statuswerte, Szenario-Referenzen und Ausfuehrungsflags, ohne Metadaten zu schreiben oder eine Simulation zu starten. Der Aktionsplan fuehrt diese Diagnose mit dem lokalen Preflight zusammen und empfiehlt pro Queue-Eintrag nur den naechsten sicheren lokalen Schritt: `run_preflight`, `await_execution_release`, `resolve_blockers` oder `inspect_queue_status`. Eine Queue-only-Datenbank aus `run_control_queue init --db` bleibt diagnostizierbar und planbar; fehlende Szenario-/Run-Metadatentabellen werden als Warnung gemeldet.

Die Workbench-Oberflaeche zeigt vorhandene Queue-Eintraege rein lesend, filtert sie clientseitig und blendet nur lokale Schrittlabels wie Preflight, Freigabe abwarten, Blocker klaeren oder Status pruefen ein. Daraus entsteht kein Start-, Upload-, Editor-, HTTP-Schreib- oder Ausfuehrungspfad.

Read-only SQLite-Zugriffe behandeln lokale WAL-Grenzen bewusst: Rollback-Journal-Datenbanken bleiben normale `mode=ro`-Reads, vollstaendige `-wal`/`-shm`-Sidecars werden beruecksichtigt und `immutable=1` wird nur fuer sidecar-freie WAL-Dateien genutzt, damit lesende Queue- und Metadatenbefehle keine neuen Sidecars erzeugen.

`workbench_readiness --db <metadata.sqlite>` bezieht diese Queue-Diagnose als eigenen Bereitschaftsbereich ein. Eine nicht initialisierte Queue bleibt ein zulaessiger Hinweis; unlesbare Queue-Schemas oder aktivierte Ausfuehrungsflags werden als Queue-Bereitschaftsproblem gemeldet.

Ein lokaler Run-Control-Preflight prueft vorhandene Run-Metadaten gegen diese gesperrte Steuerungsgrenze, ohne einen Lauf zu starten:

```powershell
python -m ims.api.run_control_preflight --run-id baseline-python-tests
```

Die Workbench-UI laedt denselben Preflight fuer den ausgewaehlten Run ueber `GET /api/run-control/preflight/{run_id}`. Die Dry-Run-Karte kann fuer die aktuelle Auswahl `POST /api/run-control/dry-run` als reine Pruefung ausloesen und nach einem erfolgreichen Dry-Run ueber `POST /api/run-control/queue` eine Queue-Vormerkung in einer expliziten SQLite-Quelle schreiben. `GET /api/run-control/queue/action-plan` zeigt danach nur den naechsten sicheren Schritt wie `run_preflight`, `await_execution_release`, `resolve_blockers` oder `inspect_queue_status`. Diese Schritte zeigen Run-/Szenario-Bezug, Hinweise und gesperrte Ausfuehrungsgrenzen, ohne PUT, Upload, Editor oder Simulation. Ein kompaktes Run-Control-Statusband buendelt Queue, Preflight, Request-Vertrag, Dry-Run-Pruefung, Queue-Vormerkung und Aktionsplan.

Lokaler Demo-Smoke fuer die Browser-Workbench:

```text
Dry-Run pruefen -> Queue vormerken -> Run-Control-Aktionsplan ansehen
```

Der Demo-Smoke nutzt den bekannten Run `baseline-python-tests` und das Szenario `agrsich-reference-window`. Er prueft den HTTP-Dry-Run, schreibt danach nur die Queue-Vormerkung in eine explizite SQLite-Metadatenquelle und liest den Aktionsplan wieder aus. Erwartet bleiben `execution_enabled=false`, `execution_performed=false` und als naechster Schritt `run_preflight`. Der Ablauf ist eine lokale Bedien- und Integrationsprobe, keine Simulation, kein Ausfuehrungsadapter, keine Fachvalidierung und keine historische Vollgleichheitsbehauptung.

Der zugehoerige Browser-/Screenshot-Smoke nutzt stabile UI-Anker fuer Dry-Run-Schaltflaeche, Queue-Schaltflaeche, Queue-Ergebnis und Aktionsplankarte. Der Screenshot soll belegen, dass die lokale UI den Demo-Pfad sichtbar und bedienbar macht; er ist kein fachlicher Ergebnisnachweis.

Metadaten-CLI:

Ein lokaler Metadatenexport kann das bestehende Importformat reproduzierbar ausgeben. Ohne `--out` schreibt er nur nach stdout, mit `--out` nur in den expliziten Zielpfad:

```powershell
python -m ims.api.metadata_import_cli export
python -m ims.api.metadata_import_cli export --db .\.ims_workbench\metadata.sqlite --out .\metadata_export.json
```

Ein lokaler Roundtrip-Check prueft Export, Importformat und Schreibvertrag gemeinsam, ohne Dateien zu schreiben:

```powershell
python -m ims.api.metadata_import_cli roundtrip
python -m ims.api.metadata_import_cli roundtrip --db .\.ims_workbench\metadata.sqlite
```

Ein lokaler Import-Trockenlauf zeigt vor einem expliziten Import, welche Szenario- und Run-Metadaten neu waeren oder bestehende IDs ersetzen wuerden. Er schreibt nicht:

```powershell
python -m ims.api.metadata_import_cli dry-run .\metadata_import.json
python -m ims.api.metadata_import_cli dry-run .\metadata_import.json --db .\.ims_workbench\metadata.sqlite
```

Der explizite lokale Import schreibt nur in den angegebenen SQLite-Pfad und gibt danach einen kleinen Importbericht mit geschriebenen IDs und Konsistenzstatus aus:

```powershell
python -m ims.api.metadata_import_cli import .\metadata_import.json --db .\.ims_workbench\metadata.sqlite
```

Backup und Restore lokaler Workbench-Metadaten bleiben explizite Betriebsablaeufe. Die Doku beschreibt das Sichern von `.ims_workbench\metadata.sqlite`, den bewussten Umgang mit WAL-/SHM-Dateien sowie pruefende CLI-Kommandos wie `snapshot`, `roundtrip`, `export` und `workbench_readiness`. Es gibt keine automatische Backup-Funktion, keine SQLite-Migration und keine Simulation.

Update und Rollback lokaler Workbench-Versionen bleiben ebenfalls manuell. Eine neue Workbench-Version soll neben der bisherigen Version in einen eigenen Ordner gelegt werden. Die Checks sollen mit explizitem neuem Anwendungspfad und explizitem bestehendem Metadatenpfad laufen, etwa mit `workbench_portable_readiness`, `workbench_readiness --db <alter-metadata-pfad>` und optional `metadata_import_cli roundtrip --db <alter-metadata-pfad>`. Repo-Side-by-Side-Checks muessen ausserdem den Python-Kontext der neuen Version nutzen, etwa ueber `PYTHONPATH` auf den neuen `python_port`-Pfad oder eine explizite Installation aus dem neuen Checkout. Rollback heisst: neue Version stoppen, alte Version wieder starten und bei Bedarf die zuvor gesicherte Metadatenquelle zuruecklegen. Es gibt keinen automatischen Updater, keine In-place-Aktualisierung, keine automatische SQLite-Migration und keine historische Vollgleichheitsbehauptung.
