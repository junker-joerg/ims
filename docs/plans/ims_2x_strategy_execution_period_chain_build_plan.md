# PR136: Kanonische fluechtige Periodenkette bauen

Stand: 2026-09-11
Umsetzungsstand: PR136 umgesetzt

## Ziel

PR136 baut aus einem vollstaendig erfolgreichen PR135-Speicher- und
Kontextabgleich eine kanonische, unveraenderliche Periodenkette im Speicher.
Die Kette erhaelt einen reproduzierbaren SHA-256-Gesamtdigest und eine daraus
abgeleitete ID. Sie wird weder gespeichert noch ausgefuehrt.

## Historischer und technischer Bezug

| Quelle | Belegte Aussage | Folge fuer PR136 |
| --- | --- | --- |
| `IMSDATA.C:14` | `SIMLAENGE = 100` | der bereits validierte lokale Horizont 1 bis hoechstens 100 wird unveraendert uebernommen |
| `ESS.C:71-75` | Lauf beginnt bei Periode 1 und schreitet um eins fort | Kandidaten und Uebergaenge bleiben lueckenlos und streng geordnet |
| PR133-Vertrag | Kandidaten, Horizont und Uebergaenge sind getrennte Kettenabschnitte | PR136 materialisiert genau diese bereits festgelegten Abschnitte |
| PR135-Aufloesung | Kandidateninhalt, Digest, Kontext und Akteursidentitaeten sind serverseitig geprueft | nur ein vollstaendig erfolgreicher Bericht darf eine Kette erzeugen |

PR136 portiert keine neue historische C-Funktion und ergaenzt keine VU-/VN-
Fachlogik.

## Kanonischer Inhalt

Der Gesamtdigest wird ueber ASCII-JSON mit sortierten Schluesseln, kompakten
Trennzeichen und gesperrten nicht-endlichen Zahlen gebildet. Die Digestbasis
enthaelt:

- Kettenschema und Basismodell;
- ersten und letzten Zeitraum, Periodenzahl, Laufindex und Maximalhorizont;
- ausschliesslich serverseitig bestaetigte Kandidaten-ID, Kandidatendigest und
  Periode;
- die expliziten, bereits validierten Uebergangsflags;
- den versionierten Nachweis der PR135-Aufloesung;
- die weiterhin geschlossenen Ausfuehrungsgrenzen.

`chain_id` und `content_digest` sind Identitaetsfelder und daher nicht Teil
ihrer eigenen Digestbasis. Datenbankpfad, Speicherzeitpunkte, vollstaendige
Kandidatenpayloads und spaetere Ergebnisprovenienz werden nicht aufgenommen.

## Atomare Reihenfolge

1. Vollstaendigen Eingang erneut durch PR135 validieren und aufloesen.
2. Bei jedem PR135-Problem ohne Teilkette abbrechen.
3. Kandidatenreferenzen aus den neu verifizierten Speicherergebnissen bilden.
4. Horizont, Uebergaenge, Aufloesungsnachweis und Grenzen kanonisch anordnen.
5. Gesamtdigest berechnen und stabile Ketten-ID daraus ableiten.
6. Vollstaendige Kette ausschliesslich in der Antwort zurueckgeben.

## API

- `GET /api/strategies/execution-period-chain-build-contract` beschreibt
  Digestbasis, Identitaet und geschlossene Grenzen.
- `POST /api/strategies/execution-period-chain-build` nimmt denselben
  versionierten Eingang wie PR134/PR135 an.

Die Kandidatenablage kommt allein aus der serverseitigen Workbench-
Konfiguration. Freie Datenbank-, Fixture- oder Ausgabepfade bleiben verboten.

## Validierung

- deterministischer Kettenbau aus zwei real gespeicherten Kandidaten;
- unabhaengige Nachrechnung des Gesamtdigests und der Ketten-ID;
- Digest-Aenderung bei fachlich explizit veraendertem Uebergangsflag;
- atomare Blockade bei ungueltigem Eingang, fehlendem oder manipuliertem
  Kandidaten;
- keine Teilkette und kein Digest bei gescheiterter Aufloesung;
- unveraenderte SQLite-Datei sowie keine Carryover-, Runner- oder
  Simulationsaufrufe;
- gleiche Grenzen in FastAPI und Starlette-Fallback.

## Restplanung

- **PR136 (umgesetzt):** kanonische fluechtige Kette und Gesamtdigest.
- **PR137 (umgesetzt):** explizit freigegebene, unveraenderliche und
  idempotente Kettenablage mit erneuter Digestpruefung; weiterhin ohne
  Carryover oder Runner.
- **PR138 (naechster Schritt):** read-only Freigabecheck der gespeicherten
  Kettenidentitaet.
- **PR139+:** isolierte Zwei-Perioden-Wirkungsprobe, atomarer Fehlerstopp und
  danach kontrollierter Ausbau bis zum 100-Perioden-Lauf in getrennten PRs.

## Schutzgrenzen

- keine neue oder geaenderte Fachlogik;
- keine Kettenpersistenz und keine Aenderung gespeicherter Kandidaten;
- kein Carryover-Aufruf, Runnerstart, UI-Start oder Ergebnisexport;
- kein Legacy-Vergleich und keine historische RNG- oder
  Vollgleichheitsbehauptung;
- `incomming/` bleibt unversioniert.
