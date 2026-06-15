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
- Checksummen oder Manifest fuer Artefaktinhalt pruefen.

Das ZIP ist ein Bereitstellungsartefakt, kein Installer und kein fachlicher Validierungsbericht.

## Update und Backup

Update- und Backup-Doku soll spaeter getrennt beschrieben werden:

- welche Dateien zur Anwendung gehoeren,
- welche Dateien lokale Daten sind,
- wie `metadata.sqlite` gesichert wird,
- wie eine neue Workbench-Version neben einer alten Version getestet wird,
- wie ein Rollback ohne Datenverlust aussieht.

Bis dahin gibt es keine automatische Migration und keinen automatischen Updater.

## Erwartete PR-Roadmap

Der Packaging-/Bereitstellungsblock bleibt grob bei ca. `6-12` reviewbaren PRs nach diesem Schritt:

1. Packaging- und Bereitstellungsplan: erledigt.
2. Lokale Startskripte fuer Windows, ohne Installer: vorbereitet.
3. Readiness-Check fuer portable Ordnerstruktur: vorbereitet.
4. Build-Snapshot fuer Frontend- und Backend-Artefakte.
5. Artefaktmanifest und Ausschluss lokaler Caches/Nutzerdaten.
6. ZIP-Erzeugung als expliziter lokaler Build-Schritt.
7. ZIP-Smoke-Test ohne Simulation.
8. Backup-/Restore-Doku fuer lokale Metadaten.
9. Update-/Rollback-Doku.
10. Windows-Pfadhaertung und Leerzeichenpfade.
11. Release-Checkliste.
12. Abschlusskonsolidierung.
13. Puffer fuer Review-Fixes und CI-/Plattformhaertung.

## Gesamtplanung

Die grobe Gesamtplanung bis "wirklich alles fertig" bleibt:

- Workbench-Ausbau nach v1: ca. `9-17` PRs.
- Fachvalidierung und historische Vollgleichheit: ca. `10-18` PRs.
- Packaging und Bereitstellung: ca. `6-12` PRs.
- Integrations- und Review-Reserve: ca. `3-5` PRs.

Erwartet bleiben damit weiterhin grob ca. `28-45+` reviewbare PRs. Diese Zahl ist bewusst konservativ und kann durch Fachvalidierung oder Plattform-/Packaging-Fallen steigen.

## Teststrategie

Packaging-Schritte sollen jeweils kleine, automatisierte Checks ergaenzen:

- Doku-Smokes fuer Start-, Build- und Artefaktgrenzen,
- Tests gegen versehentlich versionierte Artefakte oder lokale Caches,
- Pfadtests fuer Windows und Leerzeichen,
- Readiness-Checks gegen explizite Artefaktpfade,
- portable Strukturpruefung fuer Repo- und Zielstruktur,
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
