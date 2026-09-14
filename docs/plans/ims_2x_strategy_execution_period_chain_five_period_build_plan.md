# PR143: Kanonische Fuenf-Perioden-Kette bauen und validieren

Stand: 2026-09-14
Umsetzungsstand: PR143 umgesetzt

## Ziel

PR143 setzt die in PR142 beschriebene erste Horizonterweiterung als engen
Baupfad um. Genau fuenf gespeicherte Periodenkandidaten und vier explizite
Uebergaenge werden serverseitig erneut geprueft und zu einer fluechtigen,
kanonischen Kette zusammengesetzt.

Der Schritt fuehrt keine Periode aus. Er speichert weder Kette noch Ergebnis
und veraendert keine VU-, VN-, Scheduler- oder Zufallslogik.

## Historischer Bezug

| Quelle | Belegte Semantik | Grenze fuer PR143 |
| --- | --- | --- |
| `ESS.C:73-75` | periodischer Ablauf in streng aufsteigender Reihenfolge | belegt nur die Reihenfolge; kein Runner wird aufgerufen |
| `IMSDATA.C:14` | historischer Laufhorizont `SIMLAENGE = 100` | fuenf Perioden bleiben eine moderne, kleine Zwischenstufe |
| PR134 | atomare Eingangspruefung fuer lueckenlose Ketten | wird unveraendert wiederverwendet |
| PR135 | serverseitige Kandidatenaufloesung und erneute Digestpruefung | wird fuer alle fuenf Kandidaten vollstaendig ausgefuehrt |
| PR136 | kanonischer Kettenbau und Gesamtdigest | liefert das bestehende Kettenformat |
| PR142 | enger Horizontvertrag und Prefixgrenze 1-2 | PR143 oeffnet nur Bau und Validierung, nicht Ausfuehrung |

PR143 portiert keine neue C-Regel. Die Spezialisierung auf fuenf Perioden ist
eine kontrollierte Freigabestufe unterhalb des historischen 100er-Horizonts.

## Ablauf

Der spezialisierte Bau akzeptiert nur:

- `max_periods = 5`;
- Kandidatenreferenzen fuer die Perioden 1, 2, 3, 4 und 5;
- genau die Uebergaenge 1->2, 2->3, 3->4 und 4->5;
- einen gemeinsamen `run_index` und `max_periods = 5` in allen Kontexten;
- dieselben BAV-, VU- und VN-Identitaeten in allen Perioden;
- zu ID, Referenz und gespeichertem Inhalt passende SHA-256-Digests.

Erst danach wird der vorhandene kanonische Kettenbauer aufgerufen. Das
Ergebnis wird nochmals gegen Horizont, Kandidatenfolge, Uebergangsfolge,
Gesamtdigest und daraus abgeleitete Ketten-ID geprueft. Bei der ersten
Abweichung wird keine Teilkette zurueckgegeben.

## API

- `GET /api/strategies/execution-period-chain-five-period-build-contract`
- `POST /api/strategies/execution-period-chain-five-period-build`

Der POST verarbeitet Referenzen gegen die konfigurierte SQLite-Ablage. Er
schreibt nicht in die Ablage. Freie Datenbankpfade und eingebettete
Kandidateninhalte werden nicht akzeptiert.

## Kanonisches Ergebnis

Die vollstaendige fluechtige Kette enthaelt:

- Horizont 1 bis 5 mit Laufindex;
- fuenf geordnete Kandidatenreferenzen;
- vier geordnete Uebergaenge samt VU-/VN-Carryover-Schaltern;
- Herkunftsnachweis der erneuten Kandidatenpruefung;
- weiterhin geschlossene Ausfuehrungsgrenzen;
- SHA-256-Gesamtdigest und daraus abgeleitete Ketten-ID.

Speicherzeitpunkte, Datenbankpfad und vollstaendige Kandidateninhalte bleiben
wie im bestehenden Kettenformat aus der Identitaet ausgeschlossen.

## Validierung

Die Tests belegen:

- deterministisch identische Kette bei identischem Eingang;
- exakt fuenf Kandidaten und vier Uebergaenge;
- unabhaengige Neuberechnung von Gesamtdigest und Ketten-ID;
- Abbruch vor Kandidatenaufloesung bei anderem Horizont;
- atomaren Abbruch bei manipuliertem fuenften Kandidaten;
- Unterdrueckung einer nach dem Bau manipulierten Kette;
- unveraenderte SQLite-Datei und ausbleibende Runner-/Carryover-Aufrufe;
- gleiche API-Semantik in FastAPI und Starlette-Fallback.

## Restplanung

- **PR143 (umgesetzt):** exakt fuenf Kandidaten serverseitig pruefen und eine
  vollstaendige fluechtige Kette mit verifiziertem Gesamtdigest bauen.
- **PR144 (umgesetzt):** diese Kette auf isolierten Kandidatenkopien
  fluechtig ausfuehren und den exakten fachlichen Prefix 1-2 gegen ein
  gespeichertes Ergebnis des bestehenden Zwei-Perioden-Pfads pruefen.
- **PR145 (umgesetzt):** kontrollierten Serverstart, dauerhafte Idempotenz
  und unveraenderliche Ergebnisablage fuer fuenf Perioden angeschlossen.
- **PR146 (naechster Schritt):** Workbench- und Browserabnahme auf breitem
  und schmalem Viewport samt Fehlerpfaden und Handbuch-Screenshot.

## Schutzgrenzen

- keine neue Fachlogik und keine geaenderte Regel;
- kein Runner-, Carryover- oder Scheduleraufruf;
- keine Speicherung und keine Ausgabedatei;
- kein Legacy-Vergleich und keine historische RNG- oder
  Vollgleichheitsbehauptung;
- `incomming/` bleibt unversioniert und wird nicht gelesen.
