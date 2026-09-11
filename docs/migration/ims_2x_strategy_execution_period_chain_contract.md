# PR133: Periodenkette und Carryover versionieren

Stand: 2026-09-11

## Einordnung

Nach der in PR132 abgenommenen Einperioden-Wirkungsprobe beschreibt PR133 den
naechsten Architekturvertrag. Er verbindet noch keine Kandidaten zu einem
Lauf, sondern macht vorab fest, welche Periodenfolge und welche Herkunft fuer
eine spaetere Mehrperiodenausfuehrung zulaessig sein werden.

## C-zu-Python-Mapping

| Historischer Ursprung | Python-Ziel | Bedeutung |
| --- | --- | --- |
| `IMSDATA.C`, `SIMLAENGE = 100` | `historical_horizon` | harte Grenze von 100 lokalen Perioden |
| `ESS.C`, Fortschaltung `period++` nach `Fini` | `period_sequence_policy` | lueckenlose Nachbarperioden ab Periode 1 |
| periodenindizierte VU-/VN-Zustandsvektoren in `IMSDATA.C` | `previous_period_result_policy` und `provenance_policy` | Vorperiodenzustand muss aus dem echten vorherigen Kettenergebnis stammen |
| bereits portierte VU-/VN-Fortschreibung | `carryover_definitions` | nur bekannte Funktionen und Feldgruppen, keine neue Carryover-Regel |

PR133 portiert keine weitere C-Funktion. Er ersetzt den frueher impliziten,
gemeinsam veraenderlichen Laufzustand durch eine explizite Vertrags- und
Herkunftsgrenze.

## Umsetzung

`ims.strategies.execution_period_chain_contract` liefert:

- die Vertragsversion `ims.strategy-execution-period-chain-contract.v1`;
- die vorgesehene Kettenversion `ims.strategy-execution-period-chain.v1`;
- sechs Pflichtabschnitte fuer Identitaet, Horizont, Kandidaten,
  Uebergaenge, Provenienz und Ausfuehrungsgrenzen;
- drei Carryover-Definitionen fuer VU, VN-Versicherer und
  VN-Versicherungsnehmer;
- die vorhandene VU-vor-VN-Anwendungsreihenfolge;
- atomare Stopbedingungen und geschlossene Laufzeitgrenzen;
- die in PR134 ergaenzten Validierungsendpunkte;
- aktivierte PR134-Validierung, PR135-Kandidatenaufloesung sowie
  PR136-Kettenbau und -Digest;
- aktivierte PR137-Kettenablage, PR138-Freigabepruefung und fluechtige
  PR139-Zwei-Perioden-Wirkungsprobe;
- `next_gate = PR140`.

Der read-only Hauptvertrag liegt unter
`GET /api/strategies/execution-period-chain-contract`. Fuer PR138 verweist er
zusaetzlich auf `GET /api/run-control/strategy-period-chain-contract` und
`POST /api/run-control/strategy-period-chain-release-check`.

## Bewusste Grenzen

Der Vertrag akzeptiert weder gespeicherte PR131-Ergebniszusammenfassungen
noch historische Referenzzeilen als Vorperiodenobjekt. Die vorhandenen
Carryover-Funktionen benoetigen echte `VUForeignInfoPeriodRunResult`- und
`VNSettlementPeriodRunResult`-Objekte. Diese duerfen nicht nachtraeglich aus
unvollstaendigen Daten erfunden werden.

Validierung, Kandidatenaufloesung, Kettenbau, Persistenz und der read-only
Freigabecheck sind inzwischen getrennt aktiviert. Carryover,
Mehrperiodenrunner, UI-Start und Ergebnisdateien bleiben `false`. Es wurde
keine Simulation gestartet und keine historische Gleichheit behauptet.

## Validierung

Unit- und API-Tests sichern:

- den 100-Perioden-Horizont und die lueckenlose lokale Folge;
- die exakten vorhandenen Carryover-Feldgruppen und Funktionsanker;
- die Herkunft aus dem unmittelbar vorherigen echten Ergebnis;
- Digest-, Akteurs- und Fehlerstopgrenzen;
- den reinen GET-Endpunkt und gesperrte Schreibmethoden;
- ausbleibende Carryover- und Runneraufrufe beim Lesen des Vertrags.

## Naechster Schritt

PR135 loest die formal gueltigen Kandidatenreferenzen serverseitig auf,
prueft ihre gespeicherten Digests erneut und gleicht Kandidatenkontexte sowie
Akteursidentitaeten atomar ab. PR136 bildet daraus inzwischen eine kanonische
fluechtige Kette und ihren Gesamtdigest. PR137 speichert sie inzwischen
unveraenderlich. PR138 prueft inzwischen die gespeicherte Freigabeidentitaet
read-only. PR139 erprobt inzwischen genau zwei Perioden fluechtig. PR140
soll den dauerhaften Start kontrollieren; groessere Horizonte bleiben
gesperrt.
