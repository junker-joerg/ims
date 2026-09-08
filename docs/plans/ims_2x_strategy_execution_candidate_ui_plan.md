# PR128: Gespeicherte Ausfuehrungskandidaten read-only anzeigen

Stand: 2026-09-08

## Ziel

PR128 macht die in PR127 unveraenderlich gespeicherten Einperioden-
Ausfuehrungskandidaten in der Strategie-Workbench auffindbar und fachlich
einordenbar. Angezeigt werden Reife, Herkunft, SHA-256-Digest und
Speicherstatus.

Die Ansicht darf keine Kandidaten erzeugen, speichern, freigeben oder
ausfuehren. Sie fuehrt keine neue Fachlogik ein und startet keine Simulation.

## Historischer Bezug

Die historischen Aktionen `Vrvu01` bis `Vrvu10` und `Vrvn01` bis `Vrvn06`
aus `IMS.E` arbeiteten auf einem gemeinsamen Laufzustand. PR126 hat daraus
keine neue Regel abgeleitet, sondern einen modernen, kanonischen
Einperiodenzustand vorbereitet. PR127 hat diesen Zustand technisch
identifizierbar und unveraenderlich abgelegt.

PR128 beobachtet ausschliesslich diese moderne Ablage. Ein Digest belegt
Inhaltsidentitaet, aber weder historische RNG-Gleichheit noch fachliche
Vollgleichheit mit einem historischen Lauf.

## Read-only Uebersicht

`GET /api/strategies/execution-candidates` liest die konfigurierte
Workbench-SQLite-Datei ohne Tabellenanlage oder Schreibzugriff. Jeder
gefundene Datensatz wird mit der bestehenden PR127-Pruefung erneut gegen
seinen Kandidateninhalt und die relationalen Metadaten verifiziert.

Die Uebersicht liefert je Kandidat:

- Kandidaten-, Entwurfs- und Marktprofilidentitaet;
- Periode sowie VU-, VN- und Snapshotzahlen;
- Anzahl der Quelldokumente und Vertragsversionen;
- vollstaendigen Kandidatendigest und gekuerzten Profildigest fuer die UI;
- unveraenderlichen Speicherstatus und Speicherzeitpunkt;
- belegte Kandidatenreife sowie die weiterhin gesperrte Run-Control-Grenze.

Eine fehlende SQLite-Konfiguration und eine noch nicht angelegte
Kandidatentabelle werden als leere read-only Zustaende angezeigt. Ein
Integritaetsfehler wird nicht ausgeblendet, sondern als Konflikt gemeldet.

## Workbench-Schnitt

Der Strategiebereich erhaelt den neunten Tab `Kandidaten`. Die Liste ist nach
Speicherzeitpunkt sortiert; ein ausgewaehlter Kandidat zeigt:

- Eingang, Marktprofil und Speicherintegritaet als belegte Reifestufen;
- die ab PR129 verfuegbare, weiterhin read-only Run-Control-Pruefgrenze;
- Herkunft, Akteurs- und Snapshotumfang;
- SHA-256-Digest und Zeitpunkt der unveraenderlichen Ablage.

Die einzige Aktion ist das erneute Lesen der Uebersicht. Es gibt keinen
Speicher-, Freigabe- oder Startbutton.

## Validierung

- Unit-Tests fuer leere und gefuellte read-only Uebersichten;
- erneute Digest- und Metadatenpruefung aller gelisteten Kandidaten;
- API-Tests fuer Memory-, SQLite- und Konfliktzustand;
- statischer Workbench-Grenztest fuer GET-only, Sperrhinweise und UI-Felder;
- Frontend-Produktionsbuild und Browser-Smoke auf breitem und schmalem
  Viewport;
- Gesamtsuite ohne neuen Simulationsstart.

## Schutzgrenzen

- keine neue oder geaenderte VU-/VN-Fachregel;
- keine Kandidatenerzeugung und keine Speicheroperation aus dieser Ansicht;
- kein Run-Control-Eintrag, keine Freigabe und kein Runneraufruf;
- kein Scheduler, Carryover, Export oder Simulation;
- keine historische RNG- oder Vollgleichheitsbehauptung;
- `incomming/` bleibt unversioniert.

## Restplanung

- **PR129 (umgesetzt):** Run-Control-Resolver und Freigabecheck fuer
  Kandidaten-ID plus erneut geprueften Digest anbinden; Start bleibt
  gesperrt.
- **PR130:** kontrollierte Einperioden-Wirkungsprobe auf isolierter Kopie im
  Backend ausfuehren.
- **PR131:** manuellen Workbench-Start und read-only Ergebnisansicht an die
  vorhandene Freigabe-, Idempotenz- und Verlaufskette anbinden.
- **PR132:** Browser-Smoke, Fehlerpfade und Handbuch-Screenshots fuer den eng
  benannten Einperiodenpfad abschliessen.

Nach PR129 verbleiben drei kleine PRs bis zur kontrolliert bedienbaren
Einperioden-Wirkungsprobe. Mehrperiodenlauf und Regulierungssimulation bleiben
eigene spaetere Ausbaubloecke.

## Naechster Schritt

PR130 fuehrt einen erneut verifizierten Kandidaten erstmals kontrolliert auf
einer isolierten Kopie fuer genau eine Periode aus. Dateien, Legacy-Vergleich
und Carryover bleiben gesperrt.
