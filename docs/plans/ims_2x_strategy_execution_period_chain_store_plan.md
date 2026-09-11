# PR137: Periodenkette unveraenderlich speichern

Stand: 2026-09-11
Umsetzungsstand: PR137 umgesetzt

## Ziel

PR137 speichert eine kanonische PR136-Periodenkette nur nach ausdruecklicher
Freigabe unveraenderlich und idempotent in der konfigurierten Workbench-
SQLite-Datei. Vor dem ersten Schreibzugriff wird die Kette serverseitig aus
dem vollstaendigen Eingang neu gebaut. ID und Volldigest muessen der Freigabe
entsprechen. Nach Insert oder exaktem Replay wird der gespeicherte Inhalt neu
gelesen, strukturell geprueft und erneut gehasht.

## Historischer und technischer Bezug

| Quelle | Belegte Aussage | Folge fuer PR137 |
| --- | --- | --- |
| `IMSDATA.C:14` | `SIMLAENGE = 100` | gespeicherter Horizont bleibt auf den PR133- bis PR136-Vertrag von 2 bis 100 lokalen Perioden begrenzt |
| `ESS.C:71-75` | Lauf beginnt bei Periode 1 und schreitet um eins fort | gespeicherte Kandidaten- und Uebergangsfolgen werden erneut als lueckenlos validiert |
| PR127-Kandidatenablage | explizite Freigabe, serverseitiger Neubau und exakter Replay sind bewaehrt | PR137 uebernimmt dasselbe kontrollierte Speichermuster fuer Ketten |
| PR136-Kettenbau | Ketten-ID folgt aus dem kanonischen Gesamtdigest | ID und Digest bilden gemeinsam die unveraenderliche Identitaet |

PR137 portiert keine neue C-Funktion und ergaenzt keine VU-/VN-Fachlogik.

## Speicherrequest

Der Request enthaelt exakt:

- seine versionierte Schemaversion;
- den vollstaendigen PR134-Ketteneingang;
- erwartete Ketten-ID und erwarteten Volldigest;
- einen ISO-8601-Speicherzeitpunkt mit Zeitzone;
- `explicit_storage_release = true`.

Browserseitig erzeugte Kettenpayloads, PR135-Berichte und freie Datenbank-
oder Ausgabepfade werden nicht akzeptiert.

## Atomare Reihenfolge

1. Requestform, Schemaversion, Freigabe, Digestidentitaet und Zeitstempel
   pruefen.
2. PR136-Kette samt vorheriger PR135-Aufloesung serverseitig neu bauen.
3. Neu gebaute ID und Volldigest mit der Freigabe vergleichen.
4. Kettenstruktur und Digest unmittelbar vor dem Schreiben pruefen.
5. Neue Identitaet insert-only speichern oder vorhandenen exakten Inhalt als
   idempotenten Replay behandeln.
6. Gespeicherten Inhalt und Metadaten erneut lesen, strukturell pruefen und
   den Digest neu berechnen.
7. Bei jeder Abweichung atomar abbrechen und vorhandene Daten nicht
   reparieren oder ueberschreiben.

## API

- `GET /api/strategies/execution-period-chain-store-contract` beschreibt
  Freigabe, Unveraenderlichkeit und Digestpruefungen.
- `POST /api/strategies/execution-period-chain-store` speichert oder bestaetigt
  einen exakten Replay.
- `GET /api/strategies/execution-period-chains/{chain_id}` liest eine Kette
  read-only und prueft sie erneut.

## Validierung

- Insert, read-only Abruf und Digestpruefung vor und nach dem Schreiben;
- exakter Replay ohne zweite Zeile und unter Beibehaltung des urspruenglichen
  Speicherzeitpunkts;
- Abbruch ohne Kettentabelle bei fehlender expliziter Freigabe oder falscher
  erwarteter Identitaet;
- Ablehnung manipulierter Payloads und Metadaten ohne Reparatur;
- keine Annahme browserseitiger Kettenpayloads oder freier Pfade;
- keine Carryover-, Runner- oder Simulationsaufrufe;
- gleiche API-Grenzen in FastAPI und Starlette-Fallback.

## Restplanung

- **PR137 (umgesetzt):** unveraenderliche idempotente Kettenablage.
- **PR138 (umgesetzt):** kontrollierter read-only Freigabecheck fuer
  gespeicherte Ketten-ID und erneut geprueften Volldigest; weiterhin ohne
  Carryover oder Runner.
- **PR139 (umgesetzt):** isolierte fluechtige Zwei-Perioden-Wirkungsprobe
  mit atomarem Fehlerstopp.
- **PR140 (naechster Schritt):** kontrollierter dauerhafter Start; danach
  Ausbau bis 100 Perioden in getrennten PRs.

## Schutzgrenzen

- keine neue oder geaenderte Fachlogik;
- keine Updates oder Reparaturen gespeicherter Ketten;
- kein Carryover-Aufruf, Runnerstart, UI-Start oder Ergebnisexport;
- kein Legacy-Vergleich und keine historische RNG- oder
  Vollgleichheitsbehauptung;
- `incomming/` bleibt unversioniert.
