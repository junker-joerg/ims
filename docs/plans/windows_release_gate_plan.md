# Plan: Windows-Freigabegate fuer PR 70

## Ziel

PR 70 buendelt die bereits belegten technischen Pruefungen in einer
reproduzierbaren Windows-Kette. Dieselbe PowerShell-Datei soll lokal und in
GitHub Actions laufen. Der Schritt fuegt keine fachliche Logik hinzu und
veraendert die blockierte PR-69-Freigabeentscheidung nicht.

## Gate-Reihenfolge

1. gesamte Python-Testsuite ausfuehren;
2. Frontend mit dem gesperrten `package-lock.json` bauen;
3. PR-69-Korpusbericht rein lesend erzeugen;
4. genau den aktuellen konservativen Befund verlangen:
   19/19 Referenzen, 6.300 Perioden, 15 fehlende berechnete Exporte,
   `production_release_approved = false`;
5. Workbench-ZIP in einem neuen temporaeren Arbeitsbereich bauen;
6. ZIP pruefen und portabel stagen;
7. Staging-Smoke und portable Readiness ausfuehren;
8. eingefrorenen PR-67-Release-Smoke ausfuehren;
9. portables `check-workbench.cmd` ohne Serverstart ausfuehren;
10. den temporaeren Arbeitsbereich kontrolliert entfernen.

Pytest-Tempdaten und -Cache bleiben innerhalb dieses Arbeitsbereichs. Das Gate
haengt dadurch weder lokal noch in CI von globalen Windows-Temp- oder
Repo-Cache-Rechten ab.

## CI-Umgebung

- GitHub Actions auf `windows-latest`;
- GitHub-Actions-Version 6 mit Node-24-Laufzeit;
- Python 3.12;
- Node.js 22;
- Python-Installation aus `python_port[dev]`;
- Frontend-Abhaengigkeiten ueber `npm.cmd ci --prefix .\frontend`;
- Gate-Aufruf ueber `scripts\workbench\test-release-gate.ps1`.

## Fehlergrenzen

Das Gate bricht ab bei:

- fehlgeschlagenen Python-Tests oder Frontend-Build;
- unvollstaendiger Referenzabdeckung;
- einer unerwarteten fachlichen Freigabebehauptung;
- einer anderen Anzahl als 15 fehlenden Kernexporten im eingefrorenen
  PR-69-Stand;
- fehlerhaftem ZIP, Staging oder Release-Smoke;
- schreibendem oder simulationsausloesendem Bericht;
- fehlgeschlagenem portablen Checkskript.

Die Erwartung von 15 Blockern ist bewusst ein PR-69-Baselinevertrag. Sobald
berechnete Exporte kontrolliert aufgenommen werden, muss ein eigener PR diesen
Vertrag und die Freigabeentscheidung explizit aktualisieren.

## Grenzen

- kein Serverstart und kein Browser-Smoke;
- kein Adapter-, Runner- oder Queue-Start;
- keine Simulation als Produktlauf;
- keine SQLite-Datenbank oder Metadatenmigration;
- kein Zugriff auf `incomming/`;
- keine neue Fachlogik;
- keine automatische historische Regelwahl;
- keine historische Vollgleichheitsbehauptung;
- keine fachliche Produktionsfreigabe.

## Danach

Nach PR 70 ist die geplante technische Pflichtkette abgeschlossen. Weitere PRs
sind Review-Fixes, Plattformhaertung oder fachliche Abweichungsarbeit. Die
fachliche Produktionsfreigabe bleibt an die extern bereitgestellten 15
berechneten Kernexporte und deren separaten Vergleich gebunden.

PR 71 hat Herkunft, vorhandenen Runner-/Writer-Anschluss und Erzeugungsluecke
jeder dieser 15 Exportidentitaeten kartiert. PR 72 hat danach den read-only
100-Perioden-Erzeugungsvertrag fuer `imsvu014.dat` vorbereitet. PR 73 hat die
VU14-Quellenbindung und Periode 1 geschlossen. PR 74 hat die belegte
`Vdefmd6`-Population aus 25 VU und 200 VN aufgebaut. PR 75 hat danach die
wirksamen Aktionsslots und eine moderne Seed-Policy read-only gebunden. PR 76
hat die VU14-Vorschock-Regelprojektion klassifiziert; PR 77 kartiert als
naechstes den offenen VN-/Schaden-/Settlement-Pfad, weiterhin ohne vorgezogene
Vollgleichheitsbehauptung.
