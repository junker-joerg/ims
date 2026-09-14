# PR143: Fuenf-Perioden-Kette kanonisch bauen

Stand: 2026-09-14

## Einordnung

PR143 ergaenzt einen spezialisierten serverseitigen Baupfad fuer genau fuenf
Perioden. Er kombiniert die vorhandene atomare Eingangsvalidierung,
Kandidatenaufloesung und kanonische Kettenbildung. Das Ergebnis bleibt
fluechtig und wird vor der Rueckgabe nochmals vollstaendig geprueft.

## C-zu-Python-Mapping

| Historischer Ursprung | Python-Ziel | Fachliche Entsprechung |
| --- | --- | --- |
| Periodenschleife in `ESS.C:73-75` | geordnete Periodenreferenzen 1 bis 5 | spaetere Ausfuehrungsreihenfolge wird vorbereitet, aber nicht ausgefuehrt |
| `SIMLAENGE = 100` in `IMSDATA.C:14` | `FIVE_PERIOD_CHAIN_PERIOD_COUNT = 5` | absichtlich kleine moderne Freigabestufe |
| historischer Vorperiodenzustand | vier explizite VU-/VN-Carryover-Uebergaenge | Uebergangsabsicht wird gespeichert, aber noch nicht angewendet |
| vorhandene Python-Kandidaten | PR134-/PR135-Pruefpfad | alle Digests, Kontexte und Akteursidentitaeten werden erneut geprueft |

Es wird keine historische Fachfunktion neu implementiert. Das Mapping
beschreibt nur die kontrollierte Orchestrierungsgrenze.

## Umsetzung

`build_strategy_execution_five_period_chain` verlangt einen bereits
versionierten Periodenketteneingang mit exakt fuenf Kandidaten und vier
Uebergaengen. Vor dem Bau werden alle Kandidaten aus der konfigurierten
SQLite-Ablage gelesen und gegen Referenz, gespeicherten Digest, Periode,
Laufindex, Horizont sowie BAV-/VU-/VN-Identitaeten geprueft.

Der vorhandene generische Kettenbauer erzeugt danach das kanonische
Kettenobjekt. PR143 prueft anschliessend erneut:

- Horizont 1 bis 5;
- Kandidatenperioden 1 bis 5;
- Uebergaenge 1->2 bis 4->5;
- SHA-256-Gesamtdigest;
- aus dem Digest abgeleitete Ketten-ID.

Nur die vollstaendig gepruefte Kette wird zurueckgegeben. Ein Fehler vor,
waehrend oder nach dem Bau ergibt `period_chain = null` und
`partial_chain_returned = false`.

## API-Grenze

Der Vertrag ist unter
`GET /api/strategies/execution-period-chain-five-period-build-contract`
lesbar. Der fluechtige Bau erfolgt ueber
`POST /api/strategies/execution-period-chain-five-period-build`.

Die Route ist in FastAPI und im Starlette-Fallback vorhanden. Sie verwendet
ausschliesslich die konfigurierte SQLite-Metadatenquelle und nimmt keinen
freien Datenbankpfad entgegen.

## Laufgrenzen

PR143 meldet ausdruecklich:

- `five_period_candidate_validation_enabled = true`;
- `five_period_chain_build_enabled = true`;
- `period_chain_persistence_enabled = false`;
- `runner_enabled = false`;
- `writes_enabled = false`;
- `execution_performed = false`;
- `simulation_performed = false`.

Der bestehende Zwei-Perioden-Pfad bleibt unveraendert. Der in PR142
definierte Prefixvergleich wird noch nicht berechnet, weil PR143 keine
Periode ausfuehrt.

## Tests und Grenzen

Unit- und API-Tests pruefen den deterministischen Fuenf-Perioden-Bau,
Manipulations- und Horizontfehler, atomare Unterdrueckung von Teilketten,
Read-only-Verhalten sowie beide Servervarianten.

Es gibt keine neue Fachlogik, keine Ausgabedatei, keinen historischen
Vergleich und keine Vollgleichheitsbehauptung. `incomming/` wird nicht
gelesen und bleibt unversioniert.

PR144 fuehrt die gepruefte Kette inzwischen fluechtig auf isolierten
Kandidatenkopien aus und weist den exakten Prefix 1-2 gegen ein gespeichertes
PR140-Ergebnis nach. PR145 darf kontrollierten Start, Idempotenz und
unveraenderliche Ergebnisablage anschliessen.
