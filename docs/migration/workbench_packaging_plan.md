# Workbench Packaging- und Bereitstellungsplan

Dieses Dokument plant den Packaging- und Bereitstellungsblock nach der abgeschlossenen lokalen Workbench-v1. Es ist ein Planungsstand, keine Implementierung: Es erzeugt kein Release-Artefakt, installiert nichts, startet keine Simulation, oeffnet keine Schreibpfade, aendert keine Fachlogik und behauptet keine historische Vollgleichheit.

## Ausgangspunkt

Die lokale Workbench-v1 ist als Browser-Workbench abgeschlossen. Sie liefert Backend-Health und Version, statische Frontend-Auslieferung, lesende Szenario- und Run-Metadaten, Detailansichten, Filter, Auswahlzusammenfassung, Betriebsdiagnose, Metadatenquelle, Konsistenzdiagnose, Readiness und lokale CLI-Adapter.

Der aktuelle lokale Start bleibt entwicklungsnah:

```powershell
python -m pip install -e .\python_port[dev]
cd frontend
npm.cmd install
npm.cmd run build
cd ..
python -m ims.api.workbench_readiness --frontend-dist frontend/dist
python -m uvicorn ims.api.app:app --app-dir python_port --host 127.0.0.1 --port 8000
```

Dieser Ablauf ist fuer Entwicklung und Validierung ausreichend, aber noch kein portables Bereitstellungsformat fuer Anwender.

## Zielbild

Ziel ist eine kleine lokale, portable IMS Workbench, die ohne Projektwissen gestartet werden kann. Die Bereitstellung soll weiterhin lokal, transparent und kontrollierbar bleiben:

- ein reproduzierbar gebautes Frontend in einem festen Artefaktpfad,
- ein Python-Backend mit klarer Startgrenze,
- eine lokale Datenablage fuer Workbench-Metadaten,
- explizite Startskripte oder Launcher fuer Windows,
- eine ZIP- oder Ordnerstruktur, die kopiert und lokal gestartet werden kann,
- klare Update-, Backup- und Restore-Hinweise.

Die Bereitstellung bleibt von Fachvalidierung und historischer Vollgleichheit getrennt. Ein lauffaehiges Paket ist kein fachlicher Gleichheitsnachweis.

## Portable Ordnerstruktur

Ein spaeteres portables Artefakt sollte eine kleine, vorhersehbare Struktur verwenden:

```text
ims-workbench/
  README.txt
  start-workbench.cmd
  check-workbench.cmd
  python/
  app/
    python_port/
    frontend/
      dist/
  data/
    .ims_workbench/
      metadata.sqlite
  logs/
```

Diese Struktur ist ein Zielbild. In diesem Plan-PR wird sie nicht erzeugt.

## Lokale Datenablage

Die lokale Workbench-Datenablage bleibt auf Workbench-Metadaten beschraenkt. Die bevorzugte lokale Ablage ist:

```text
.ims_workbench/
  metadata.sqlite
```

Spaetere Backup- und Restore-Schritte sollen diese Datei explizit behandeln. Ein Backup darf keine Fachlogikdaten, keine Legacy-Vollvalidierungsbehauptung und keine versteckten Simulationsergebnisse implizieren.

SQLite-WAL-/SHM-Dateien koennen je nach Betrieb vorhanden sein. Packaging- und Backup-Schritte muessen entweder einen stabilen Checkpoint/Shutdown-Pfad dokumentieren oder diese Dateien bewusst behandeln. Lesende Diagnosepfade duerfen weiterhin keine Datenbankdateien implizit erzeugen.

## Startskripte und Launcher

Erste lokale Windows-Skripte sind unter `scripts/workbench/` vorbereitet:

- `check-workbench.cmd` prueft `frontend/dist`, Startdiagnose und Readiness.
- `start-workbench.cmd` startet nur den lokalen Backend-Server auf `127.0.0.1:8000`.
- `README.md` beschreibt diese lokale Grenze.
- `python -m ims.api.workbench_portable_readiness --root . --layout repo` prueft die heutige Repo-Struktur.
- `python -m ims.api.workbench_portable_readiness --root .\ims-workbench --layout portable` prueft eine spaetere portable Zielstruktur.
- `python -m ims.api.workbench_build_snapshot --root . --frontend-dist frontend/dist` fasst vorhandene lokale Build-Artefakte zusammen.
- `python -m ims.api.workbench_artifact_manifest --root . --frontend-dist frontend/dist` beschreibt Ein- und Ausschlusspfade sowie Datei-Groessen und SHA-256-Pruefsummen fuer ein spaeteres Artefakt.
- `python -m ims.api.workbench_bundle_plan --root . --frontend-dist frontend/dist` plant ein spaeteres Bundle auf Basis des Manifests, ohne Dateien zu kopieren oder ein ZIP zu erzeugen.
- `python -m ims.api.workbench_bundle_build --root . --frontend-dist frontend/dist --out .\dist\ims-workbench-local.zip` erzeugt ein explizites lokales ZIP aus dem Bundle-Plan.

Diese Skripte kapseln nur lokale Betriebsablaeufe:

- Voraussetzungen pruefen,
- Readiness ausfuehren,
- Backend lokal starten,
- Browser-URL anzeigen oder optional oeffnen,
- Logdateien in einen lokalen `logs/`-Ordner schreiben.

Nicht erlaubt in diesem Block:

- Simulation starten,
- Run-Control ausfuehren,
- Fachlogik mutieren,
- HTTP- oder UI-Schreibpfade oeffnen,
- Szenarien im Browser editieren,
- historische Vollgleichheit behaupten.

## Reproduzierbarer Build

Ein spaeterer Build-Schritt soll mindestens pruefen:

- Python-Abhaengigkeiten fuer Backend/API und Tests,
- Frontend-Abhaengigkeiten und `npm.cmd run build`,
- Vorhandensein von `frontend/dist`,
- `python -m ims.api.workbench_readiness --frontend-dist frontend/dist`,
- lokale statische Auslieferung ueber das Backend.

Der Build darf keine lokale SQLite-Datei erzeugen, keine Simulation starten und keine Metadaten importieren, ausser ein spaeterer Schritt verlangt einen expliziten Testpfad.

## ZIP- und Release-Artefakte

Ein spaeteres ZIP-Artefakt sollte erst nach einem eigenen reviewbaren Schritt entstehen. Erwartete Artefaktregeln:

- nur explizit gebaute Dateien aufnehmen,
- keine lokalen Caches aufnehmen,
- keine `frontend/node_modules/`,
- keine `frontend/dist` versionieren, sondern reproduzierbar bauen und dann ins Artefakt kopieren,
- keine privaten lokalen Datenbanken oder Nutzerdaten aufnehmen,
- Checksummen oder Manifest fuer Artefaktinhalt pruefen,
- den ZIP-Zielpfad nicht unter eingeschlossenen Quellbaeumen wie `python_port` oder `frontend/dist` erlauben,
- ZIP-Eintraege mit stabilen Zeitstempeln und Dateirechten schreiben, damit die ZIP-Pruefsumme bei identischem Inhalt reproduzierbar bleibt.

Das ZIP ist ein Bereitstellungsartefakt, kein Installer und kein fachlicher Validierungsbericht.

## Backup und Restore lokaler Metadaten

Die lokale Workbench-Datenablage enthaelt aktuell nur Workbench-Metadaten. Ein Backup fuer diese Metadaten behandelt ausschliesslich die explizite SQLite-Ablage und optionale exportierte JSON-Bundles:

- `metadata.sqlite` ist die lokale Metadatenquelle.
- `metadata.sqlite-wal` und `metadata.sqlite-shm` koennen bei SQLite-WAL-Betrieb vorhanden sein und muessen bei einem Datei-Backup bewusst behandelt werden.
- `python -m ims.api.metadata_import_cli snapshot --db .\.ims_workbench\metadata.sqlite` liest die Metadatenquelle als Diagnose, schreibt aber kein Backup.
- `python -m ims.api.metadata_import_cli export --db .\.ims_workbench\metadata.sqlite --out .\metadata_export.json` erzeugt ein explizites JSON-Bundle im Importformat.
- `python -m ims.api.metadata_import_cli roundtrip --db .\.ims_workbench\metadata.sqlite` prueft die Lesbarkeit und Importvertragsnaehe, schreibt aber nicht.
- `python -m ims.api.workbench_readiness --frontend-dist frontend/dist --db .\.ims_workbench\metadata.sqlite` prueft eine wiederhergestellte Metadatenquelle vor der lokalen Nutzung.

Ein Restore bleibt zunaechst ein manueller, expliziter Betriebsablauf: Workbench stoppen, bestehende Metadatenquelle sichern oder ersetzen, wiederhergestellte Datei mit Readiness und Roundtrip pruefen, dann Workbench neu starten. Dieser Plan ergaenzt keine automatische Backup-Funktion, keine SQLite-Migration, keinen Updater, keine Simulation und keine Fachvalidierung. Ein Backup enthaelt keine Fachlogikdaten, keine Simulationsergebnisse und keine historische Vollgleichheitsbehauptung.

## Update und Rollback lokaler Workbench-Versionen

Update und Rollback bleiben zunaechst manuelle, lokale Betriebsablaeufe. Eine
neue Workbench-Version soll nicht direkt ueber eine bestehende Version kopiert
werden. Stattdessen wird sie neben der bisherigen Version in einen eigenen
Ordner entpackt oder ausgecheckt und erst nach lokalen Checks genutzt.

Die Trennung ist bewusst einfach:

- Anwendung: Repo- oder ZIP-Inhalt, `python_port`, `frontend/dist`,
  Startskripte und Doku.
- Lokale Daten: `.ims_workbench/metadata.sqlite` und je nach SQLite-Betrieb
  zugehoerige WAL-/SHM-Dateien.
- Diagnoseartefakte: explizite JSON-Exports, Snapshots und Logs.

Ein konservatives Update sieht so aus:

1. Bisherige Workbench-Version und lokale Metadaten unveraendert lassen.
2. Vor dem Test der neuen Version ein Backup oder JSON-Export der lokalen
   Metadaten erstellen.
3. Neue Workbench-Version in einen eigenen Ordner entpacken oder auschecken.
4. Alte Metadatenquelle und neue Anwendung mit expliziten Pfaden pruefen:

```powershell
$oldRoot = "C:\ims-workbench-old"
$newRoot = "C:\ims-workbench-new"
$metadataDb = Join-Path $oldRoot ".ims_workbench\metadata.sqlite"
$exportPath = Join-Path $oldRoot "metadata_export.json"

python -m ims.api.metadata_import_cli export --db $metadataDb --out $exportPath
python -m ims.api.workbench_portable_readiness --root $newRoot --layout portable
python -m ims.api.workbench_readiness --frontend-dist (Join-Path $newRoot "app\frontend\dist") --db $metadataDb
```

5. Optional die Metadatenquelle zusaetzlich pruefen:

```powershell
python -m ims.api.metadata_import_cli roundtrip --db $metadataDb
```

6. Neue Version erst starten, wenn die Checks erwartbar gruen sind.

Die Befehle muessen im Kontext der neuen portablen Workbench-Version laufen.
Bei einem neuen Repo-Checkout wird deshalb in den neuen Checkout gewechselt und
`--layout repo` relativ zu diesem Checkout verwendet:

```powershell
Push-Location $newRoot
python -m ims.api.workbench_portable_readiness --root . --layout repo
python -m ims.api.workbench_readiness --frontend-dist frontend/dist --db $metadataDb
Pop-Location
```

Der neue Anwendungspfad und der bestehende Metadatenpfad duerfen dabei nicht
implizit aus dem aktuellen Arbeitsverzeichnis geraten.

Rollback heisst entsprechend: neue Workbench stoppen, alte Version wieder
starten und bei Bedarf die zuvor gesicherte Metadatenquelle zuruecklegen. Der
Rollback ist kein Datenbank-Migrationsmechanismus und kein automatischer
Downgrade. Wenn eine spaetere Version jemals eine SQLite-Migration erfordert,
braucht diese Migration einen eigenen Plan, eigene Tests und eine separate
Freigabe.

Dieser Plan ergaenzt keinen automatischen Updater, keine In-place-Aktualisierung,
keine automatische SQLite-Migration, keinen Installer, keine Simulation und
keine Fachvalidierung. Ein lokales Update oder Rollback ist kein fachlicher
Gleichheitsnachweis und keine historische Vollgleichheitsbehauptung.

## Erwartete PR-Roadmap

Der Packaging-/Bereitstellungsblock bleibt grob bei ca. `1-3` reviewbaren PRs nach diesem Schritt:

1. Packaging- und Bereitstellungsplan: erledigt.
2. Lokale Startskripte fuer Windows, ohne Installer: vorbereitet.
3. Readiness-Check fuer portable Ordnerstruktur: vorbereitet.
4. Build-Snapshot fuer Frontend- und Backend-Artefakte: vorbereitet.
5. Artefaktmanifest, Checksummen und Ausschluss lokaler Caches/Nutzerdaten: vorbereitet.
6. Bundle-Trockenlauf auf Basis des Artefaktmanifests: vorbereitet.
7. ZIP-Erzeugung als expliziter lokaler Build-Schritt: vorbereitet.
8. ZIP-Smoke-Test ohne Simulation: vorbereitet.
9. Backup-/Restore-Doku fuer lokale Metadaten: vorbereitet.
10. Update-/Rollback-Doku fuer lokale Workbench-Versionen: vorbereitet.
11. Windows-Pfadhaertung und Leerzeichenpfade.
12. Release-Checkliste.
13. Abschlusskonsolidierung.
14. Puffer fuer Review-Fixes und CI-/Plattformhaertung.

## Gesamtplanung

Die grobe Gesamtplanung bis "wirklich alles fertig" bleibt:

- Workbench-Ausbau nach v1: ca. `8-15` PRs.
- Fachvalidierung und historische Vollgleichheit: ca. `10-18` PRs.
- Packaging und Bereitstellung: ca. `1-3` PRs.
- Integrations- und Review-Reserve: ca. `1-4` PRs.

Erwartet bleiben damit weiterhin grob ca. `20-40+` reviewbare PRs. Diese Zahl ist bewusst konservativ und kann durch Fachvalidierung oder Plattform-/Packaging-Fallen steigen.

## Teststrategie

Packaging-Schritte sollen jeweils kleine, automatisierte Checks ergaenzen:

- Doku-Smokes fuer Start-, Build- und Artefaktgrenzen,
- Tests gegen versehentlich versionierte Artefakte oder lokale Caches,
- Pfadtests fuer Windows und Leerzeichen,
- Readiness-Checks gegen explizite Artefaktpfade,
- portable Strukturpruefung fuer Repo- und Zielstruktur,
- Build-Snapshots fuer vorhandene Frontend-/Backend-Artefakte,
- Artefaktmanifest fuer Ein- und Ausschlusspfade inklusive Groessen und SHA-256-Pruefsummen,
- Bundle-Trockenlauf auf Basis des Artefaktmanifests, ohne ZIP-Erzeugung,
- ZIP-Inhaltspruefung fuer explizit erzeugte lokale Bundles,
- ZIP-Smoke-Test fuer erwartete Workbench-Dateien, Ausschluesse und stabile ZIP-Metadaten,
- Backup-/Restore-Doku fuer `metadata.sqlite`, WAL-/SHM-Grenzen, Snapshot, Export, Roundtrip und Readiness,
- Update-/Rollback-Doku fuer parallele Versionstests, Datenablage-Trennung, Readiness, Roundtrip und manuellen Rollback,
- reproduzierbare ZIP-Pruefsummen bei identischem Inhalt trotz unterschiedlicher lokaler Dateizeitstempel,
- Ablehnung von ZIP-Zielpfaden unter eingeschlossenen Quellbaeumen,
- Smoke-Start des Backend ohne Simulation,
- ZIP-Inhaltspruefung, sobald ZIP-Erzeugung umgesetzt wird.

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
- Kein Installer.
- Kein ZIP- oder Release-Artefakt in diesem PR.
- Keine automatische Update-Funktion.
- Keine historische Vollgleichheitsbehauptung.
