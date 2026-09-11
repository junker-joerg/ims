# PR133: Periodenketten- und Carryover-Vertrag

Stand: 2026-09-11
Umsetzungsstand: PR133 umgesetzt

## Ziel

PR133 versioniert die Grenze fuer eine spaetere kontrollierte Folge von zwei
bis 100 lokalen Perioden. Der Vertrag legt Periodenordnung,
Kandidatenreferenzen, Vorperiodenherkunft, Carryover-Opt-ins, Provenienz und
Stopbedingungen fest.

Der Vertrag baut, speichert oder startet keine Periodenkette. PR134 hat
inzwischen die getrennte zustandslose Eingangsvalidierung ergaenzt. Es wird
weiterhin keine VU-/VN-Regel geaendert und keine Simulation ausgefuehrt.

## Historischer Bezug

| Altcode | Aussage | Vertragsfolge |
| --- | --- | --- |
| `IMSDATA.C:14` | `SIMLAENGE = 100` | hoechstens 100 lokale Perioden je Lauf |
| `IMSDATA.C:202-216` | VU-Ziel-, Ergebnis- und Folgevektoren sind periodenindiziert | jeder Kettenschritt benennt seine lokale Periode explizit |
| `IMSDATA.C:252-287` | VN-Risiko- und Vermoegenswerte sind periodenindiziert | Vorperiodenwerte brauchen eine belegte Herkunft |
| `ESS.C:71-75` | `period` beginnt bei 1 und wird nach dem Periodenabschluss erhoeht | nur lueckenlose Nachbarperioden `t -> t+1` |

Historische Ergebniszeilen oberhalb 100 bleiben Zeilen aus getrennten
Wiederholungslaeufen. Der Vertrag deutet sie nicht in einen historischen
300- oder 500-Periodenlauf um.

## Periodenkette

Eine spaetere Kette muss:

- bei lokaler Periode 1 beginnen;
- zwei bis hoechstens 100 Perioden enthalten;
- strikt steigend und lueckenlos sein;
- denselben `run_index` und `max_periods` verwenden;
- je Periode genau einen unveraenderlich gespeicherten PR127-Kandidaten ueber
  `candidate_id`, Volldigest und Periode referenzieren;
- vor dem ersten Start als Ganzes geprueft werden.

Der Vertrag verweist fuer die inzwischen vorhandene Kettenvalidierung auf das
eigene Tor PR134.

## Vorperiodenherkunft

Carryover darf ausschliesslich aus dem erfolgreichen, unmittelbar vorherigen
In-Memory-Ergebnis derselben Kette stammen. Nicht zulaessig sind:

- der zusammengefasste gespeicherte PR131-Wirkungsnachweis;
- eine historische Referenzzeile;
- ein konstruiertes oder still ergaenztes Vorperiodenergebnis;
- ein Ergebnis einer anderen Kette oder einer nicht benachbarten Periode.

Ein spaeterer Ausfuehrungsnachweis muss Quell- und Zielkandidat, deren Digests,
den Ergebnisdigest der Vorperiode und den Digest des effektiven
Folgeperiodeneingangs festhalten.

## Carryover-Grenze

Carryover bleibt standardmaessig aus und verlangt je Uebergang getrennte
Opt-ins fuer VU und VN. Der Vertrag referenziert nur die vorhandenen
Bausteine:

- `ims.engine.vu_rule_runner.apply_vu_foreign_info_carryover`;
- `ims.engine.vn_rule_runner.apply_vn_state_carryover`.

Die Feldgruppen werden direkt aus der vorhandenen
`explicit_period_transition_diagnostics` uebernommen. Bei gemeinsamem Opt-in
gilt die schon im expliziten Mehrperiodenrunner vorhandene Reihenfolge VU vor
VN. Ziel ist immer eine isolierte Kopie des Kandidaten fuer `t+1`; gespeicherte
Kandidaten bleiben unveraendert.

Vor einer spaeteren Ausfuehrung muessen die Akteurs-IDs der Nachbarperioden
identisch sein. Ein fehlender Akteur, verdeckter Fallback oder pauschales
Fortschreiben aller Felder ist nicht zulaessig.

## Stopgrenzen

- Die gesamte Kette wird vor der ersten Periode atomar geprueft.
- Digestfehler, Periodenluecken und fehlende Akteure blockieren den Start.
- Der erste fehlgeschlagene Periodenschritt stoppt die Kette.
- Spaetere Perioden werden danach nicht mehr ausgefuehrt.
- Ein Teilergebnis darf nicht als erfolgreiche Gesamtkette gelten.

## Read-only API

`GET /api/strategies/execution-period-chain-contract` liefert den
versionierten Vertrag und verweist auf die getrennten PR134-Endpunkte fuer
Validierungsvertrag und Eingangspruefung. Andere HTTP-Methoden sind gesperrt.
Der Vertragsendpunkt nimmt keinen Kettenentwurf an und ruft weder Carryover
noch Runner auf.

## Restplanung

- **PR133 (umgesetzt):** Periodenketten-, Vorperioden- und Carryover-Grenze
  versionieren und read-only bereitstellen.
- **PR134 (umgesetzt):** einen versionierten Ketteneingang fuer Perioden 1
  bis maximal 100 zustandslos und atomar validieren.
- **PR135 (umgesetzt):** Kandidatenreferenzen serverseitig aufloesen, Digests
  erneut pruefen und Kandidatenkontexte sowie Akteursidentitaeten atomar
  abgleichen.
- **PR136 (umgesetzt):** kanonische fluechtige Kette und Gesamtdigest bilden.
- **PR137 (naechster Schritt):** unveraenderliche idempotente Ablage.
- **PR138+:** kleine Zwei-Perioden-Wirkungsprobe und spaeter den
  kontrollierten Ausbau bis 100 Perioden jeweils getrennt freigeben.

## Schutzgrenzen

- keine neue oder geaenderte Fachlogik;
- kein Kettenbau und keine Kettenpersistenz;
- kein Carryover-Aufruf und kein Runnerstart;
- kein neuer UI-Startpfad;
- keine Ergebnisdateien und kein Legacy-Vergleich;
- keine historische RNG- oder Vollgleichheitsbehauptung;
- `incomming/` bleibt unversioniert.
