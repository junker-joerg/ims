# PR134: Periodenketten-Eingang validieren

Stand: 2026-09-11

## Einordnung

PR133 hat die Periodenfolge, Kandidatenreferenzen und Carryover-Grenzen
beschrieben. PR134 macht daraus erstmals einen maschinenpruefbaren Eingang,
ohne die referenzierten Kandidaten zu laden oder einen Laufzustand zu
erzeugen.

## C-zu-Python-Mapping

| Historischer Ursprung | Python-Ziel | Bedeutung |
| --- | --- | --- |
| `IMSDATA.C`, `SIMLAENGE = 100` | `max_periods`-Pruefung | hoechstens 100 lokale Perioden |
| `ESS.C`, `period = 1` und `period++` | Horizont- und Uebergangspruefung | vollstaendige Folge `1..max_periods` und nur `t -> t+1` |
| impliziter gemeinsamer Laufzustand | versionierter Ketteneingang und Fehlerbericht | Vorbereitung wird explizit, deterministisch und atomar pruefbar |

Es wird keine weitere C-Regel portiert und keine fachliche Wirkung
veraendert.

## Umsetzung

`ims.strategies.execution_period_chain_validation` liefert:

- `ims.strategy-execution-period-chain-input.v1`;
- `ims.strategy-execution-period-chain-validation.v1`;
- eine exakte Feld-, Versions- und Wertepruefung;
- eine lueckenlose Kandidatenfolge von Periode 1 bis `max_periods`;
- eindeutige Kandidaten-IDs und Digests samt formaler ID-/Digest-Identitaet;
- eine vollstaendige, geordnete Nachbaruebergangsfolge mit expliziten
  booleschen VU-/VN-Carryover-Schaltern;
- einen strukturierten atomaren Bericht ohne Teilkette.

Die zwei API-Endpunkte stellen Vertrag und Validierung fuer FastAPI und den
Starlette-Fallback gleich bereit. Das vorhandene PR133-Vertragsdokument weist
nun `period_chain_validation_enabled = true` und `next_gate = PR135` aus.

## Validierung

Unit- und API-Tests sichern:

- einen gueltigen deterministischen Eingang;
- unvollstaendige, ungeordnete und zu lange Horizonte;
- doppelte oder unpassende Kandidatenidentitaeten;
- fehlerhafte Uebergaenge und nicht boolesche Carryover-Schalter;
- atomare Ablehnung ohne Teilkette;
- gesperrte Kandidatenauflosung, Kettenbildung, Carryover- und Runneraufrufe;
- den read-only Vertragsendpunkt und gesperrte HTTP-Methoden.

## Bewusste Grenzen

PR134 prueft nur das eingereichte Dokument. Der Digest des gespeicherten
Kandidaten wird nicht neu berechnet, und der Kandidatenkontext wird nicht mit
`run_index`, `max_periods` oder Periode der Kette abgeglichen. Eine gueltige
Antwort ist deshalb eine Eingangsfreigabe, noch keine ausfuehrbare Kette.

Es wurden weder Carryover noch Runner oder Simulation gestartet. Aus dem
Schnitt folgt keine historische RNG- oder Vollgleichheitsbehauptung.

## Naechster Schritt

PR135 soll die Kandidatenreferenzen serverseitig aufloesen, ihre gespeicherten
Digests erneut pruefen und die Kontextgleichheit der gesamten Kette atomar
feststellen. Kettenpersistenz, Carryover und Ausfuehrung bleiben dort noch
gesperrt.
