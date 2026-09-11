# PR134: Periodenketten-Eingang atomar validieren

Stand: 2026-09-11
Umsetzungsstand: PR134 umgesetzt

## Ziel

PR134 fuehrt einen versionierten JSON-Eingang fuer eine vollstaendige lokale
Periodenkette ein und prueft ihn zustandslos als Ganzes. Der Schnitt nimmt
zwei bis 100 Perioden an. Entweder ist der gesamte Eingang gueltig oder es
wird ausschliesslich ein Fehlerbericht geliefert.

Der PR loest keine Kandidaten aus der SQLite-Ablage auf, baut keine Kette,
ruft keinen Carryover und keinen Runner auf und startet keine Simulation.

## Historischer und technischer Bezug

| Quelle | Belegte Aussage | Folge fuer PR134 |
| --- | --- | --- |
| `IMSDATA.C:14` | `SIMLAENGE = 100` | `max_periods` liegt zwischen 2 und 100 |
| `ESS.C:71-75` | Start bei Periode 1, Fortschaltung um eins | Kandidaten reichen geordnet und lueckenlos von 1 bis `max_periods` |
| PR127-Kandidatenvertrag | Kandidaten-ID wird aus dem SHA-256-Digest abgeleitet | jede Referenz muss eine formal passende ID-/Digest-Paarung besitzen |
| PR133-Kettenvertrag | Carryover ist je Nachbaruebergang explizit | genau `max_periods - 1` Uebergaenge `t -> t+1` mit zwei booleschen Opt-ins |

PR134 portiert keine neue historische C-Funktion. Er ersetzt einen Teil der
frueher impliziten Laufvorbereitung durch eine pruefbare Eingangsgrenze.

## Versionierter Eingang

`ims.strategy-execution-period-chain-input.v1` enthaelt:

- die Ketten-, Kandidaten- und Basismodellversion;
- `run_index` und `max_periods`;
- genau eine Referenz aus `candidate_id`, `content_digest` und `period` je
  lokaler Periode;
- genau einen Uebergang je Nachbarperiodenpaar mit getrennten VU- und
  VN-Carryover-Schaltern.

Unbekannte und fehlende Felder, falsche Versionen, Periodenluecken,
Vertauschungen, doppelte Identitaeten, unpassende ID-/Digest-Paare sowie
nicht benachbarte Uebergaenge machen den gesamten Eingang ungueltig.

## Atomare Schutzgrenze

Die Validierung ist rein und deterministisch. Sie veraendert den Eingang
nicht und liefert nie eine Teilkette. Eine formell passende Kandidaten-ID
beweist dabei nur, dass sie aus dem angegebenen Digest abgeleitet ist.

Bewusst noch nicht geprueft werden:

- ob der Kandidat in der freigegebenen SQLite-Ablage existiert;
- ob sein gespeicherter Inhalt weiterhin denselben Digest besitzt;
- ob Kandidatenkontext, `run_index`, `max_periods` und Periode
  uebereinstimmen;
- ob benachbarte Kandidaten dieselben VU-/VN-Akteure enthalten.

## API

- `GET /api/strategies/execution-period-chain-validation-contract` beschreibt
  Schema, Reihenfolge und geschlossene Laufzeitgrenzen.
- `POST /api/strategies/execution-period-chain-validation` prueft genau einen
  vollstaendigen Eingang und liefert einen strukturierten Bericht.

Der POST-Endpunkt speichert nichts. Ein unlesbares JSON wird mit HTTP 400
abgewiesen; ein lesbares, aber ungueltiges Dokument erhaelt einen vollstaendigen
Fehlerbericht ohne Teilannahme.

## Restplanung

- **PR134 (umgesetzt):** Ketteneingang versionieren und zustandslos atomar
  validieren.
- **PR135 (naechster Schritt):** alle Referenzen serverseitig aus der
  Kandidatenablage aufloesen, gespeicherte Digests erneut pruefen und
  Kandidatenkontexte atomar gegeneinander abgleichen; weiterhin ohne
  Persistenz, Carryover oder Runner.
- **PR136+:** erst nach erfolgreicher Aufloesung den kanonischen Kettenbau und
  Digest, die unveraenderliche Ablage, eine isolierte Zwei-Perioden-Probe und
  den kontrollierten Ausbau bis 100 Perioden in getrennten PRs freigeben.

## Schutzgrenzen

- keine neue oder geaenderte Fachlogik;
- kein Kandidaten- oder Kettenbau und keine Persistenz;
- kein Carryover-Aufruf, Runnerstart oder UI-Startpfad;
- keine Ergebnisdateien und kein Legacy-Vergleich;
- keine historische RNG- oder Vollgleichheitsbehauptung;
- `incomming/` bleibt unversioniert.
