# PR135: Periodenkandidaten serverseitig aufloesen

Stand: 2026-09-11
Umsetzungsstand: PR135 umgesetzt

## Ziel

PR135 nimmt einen vollstaendig gueltigen PR134-Ketteneingang und loest alle
Kandidatenreferenzen aus der serverseitig konfigurierten SQLite-Ablage auf.
Jeder gespeicherte Kandidateninhalt wird erneut gegen seinen SHA-256-Digest
und seine ID geprueft. Danach werden Laufkontext und Akteursidentitaeten ueber
die gesamte Kette abgeglichen.

Der Schnitt liefert Kandidatenzusammenfassungen nur bei vollstaendigem Erfolg.
Er baut oder speichert keine Periodenkette und ruft weder Carryover noch
Runner auf.

## Historischer und technischer Bezug

| Quelle | Belegte Aussage | Folge fuer PR135 |
| --- | --- | --- |
| `IMSDATA.C:14` | `SIMLAENGE = 100` | jeder Kandidatenhorizont muss dem validierten Laufhorizont bis hoechstens 100 entsprechen |
| `IMSDATA.C:186-216` | VU-Zustaende sind periodenindiziert | Kandidatenperiode und `simulation_context.period` muessen der Kettenperiode entsprechen |
| `IMSDATA.C:252-287` | VN-Zustaende sind periodenindiziert | dieselbe Periodenidentitaet gilt fuer VN-Zustaende |
| `ESS.C:71-75` | Lauf beginnt bei Periode 1 und schreitet um eins fort | PR135 uebernimmt nur den zuvor validierten lueckenlosen PR134-Eingang |
| PR127-Kandidatenablage | gespeicherter Inhalt wird beim Lesen neu gehasht | nur read-only erneut verifizierte Kandidaten werden akzeptiert |

PR135 portiert keine neue C-Funktion und ergaenzt keine VU-/VN-Fachlogik.

## Verbindlicher Kontext

Massgeblich sind je Kandidat:

- `identity.period`;
- `market_ground_state.simulation_context.period`;
- `market_ground_state.simulation_context.run_index`;
- `market_ground_state.simulation_context.max_periods`.

Periode, Laufindex und Horizont muessen mit dem Ketteneingang uebereinstimmen.
Zusaetzlich muessen BAV-ID sowie die Mengen der VU- und VN-IDs in jeder
Periode mit Periode 1 identisch sein. Das ist eine Anschlussbedingung fuer die
bereits vorhandenen Carryover-Funktionen, noch kein Carryover-Aufruf.

Profil-ID und Profildigest duerfen sich zwischen Periodenkandidaten
unterscheiden. Eine Gleichheit waere durch den historischen Ablauf nicht
belegt und wird deshalb nicht gefordert.

## Atomare Pruefreihenfolge

1. Vollstaendigen PR134-Eingang zustandslos validieren.
2. Jeden Kandidaten ausschliesslich per ID aus der konfigurierten SQLite-Datei
   lesen.
3. Kandidateninhalt neu hashen und gespeicherte ID sowie Metadaten pruefen.
4. Referenz-ID, Referenzdigest und Referenzperiode abgleichen.
5. Periode, Laufindex und Horizont aller Kandidaten pruefen.
6. BAV-, VU- und VN-Identitaeten kettenweit abgleichen.
7. Zusammenfassungen nur ausgeben, wenn alle Pruefungen erfolgreich sind.

Ein Fehler laesst den gesamten Bericht auf `blocked` stehen. Bereits gelesene
Kandidaten werden nicht als Teilkette zurueckgegeben.

## API

- `GET /api/strategies/execution-period-chain-resolution-contract` beschreibt
  Quellen, Pruefreihenfolge und geschlossene Grenzen.
- `POST /api/strategies/execution-period-chain-resolution` nimmt genau den
  PR134-Eingang an.

Ein Datenbank- oder Dateipfad im Request ist nicht erlaubt. Ohne explizit
konfigurierte Workbench-SQLite-Datei bleibt der Endpunkt gesperrt.

## Restplanung

- **PR135 (umgesetzt):** Kandidaten aufloesen, Digests erneut pruefen und
  Kontexte sowie Akteursidentitaeten atomar abgleichen.
- **PR136 (umgesetzt):** aus einem erfolgreichen PR135-Bericht eine
  kanonische fluechtige Periodenkette mit reproduzierbarem Gesamtdigest bauen;
  weiterhin ohne Speicherung, Carryover oder Runner.
- **PR137 (naechster Schritt):** unveraenderliche idempotente Kettenablage.
- **PR138+:** isolierte Zwei-Perioden-Probe,
  Fehlerstopp und spaeter den kontrollierten Ausbau bis 100 Perioden in
  getrennten PRs freigeben.

## Schutzgrenzen

- keine neue oder geaenderte Fachlogik;
- kein Kettenbau, kein Kettendigest und keine Kettenpersistenz;
- keine freien Datenbank-, Fixture- oder Ausgabepfade;
- kein Carryover-Aufruf, Runnerstart oder UI-Startpfad;
- keine Ergebnisdateien und kein Legacy-Vergleich;
- keine historische RNG- oder Vollgleichheitsbehauptung;
- `incomming/` bleibt unversioniert.
