# PR142: Begrenzten Kettenrunner vertraglich festlegen

Stand: 2026-09-14

## Einordnung

PR142 fuegt einen versionierten read-only Vertrag fuer die erste
Horizonterweiterung von zwei auf hoechstens fuenf Perioden hinzu. Er
implementiert keine Fuenf-Perioden-Ausfuehrung. Der vorhandene
Zwei-Perioden-Pfad aus PR139 bis PR141 bleibt unveraendert und weiterhin der
einzige freigegebene Mehrperiodenpfad.

## C-zu-Python-Mapping

| Historischer Ursprung | Python-Ziel | Fachliche Entsprechung |
| --- | --- | --- |
| Periodenschleife in `ESS.C:73-75` | `STRATEGY_EXECUTION_BOUNDED_RUNNER_STEPS` | Perioden werden spaeter streng aufsteigend und genau einmal ausgefuehrt |
| `SIMLAENGE = 100` in `IMSDATA.C:14` | `BOUNDED_RUNNER_MAXIMUM_PERIODS = 5` | moderne, absichtlich kleinere Freigabestufe unterhalb der historischen Obergrenze |
| vorhandener expliziter Periodenschritt | `run_loaded_explicit_period` als benannte spaetere Quelle | VU-Regeln, VN-Regeln und Aggregation bleiben unveraendert |
| vorhandener Vorperiodenzustand | gespeicherte VU-/VN-Carryover-Flags | Carryover bleibt explizit und wirkt nur auf eine isolierte Kopie der Folgeperiode |

Der Vertrag portiert weder Scheduler- noch VU-/VN-Regellogik. Fuenf Perioden
sind kein historischer Sondermodus.

## Neuer Vertrag

`ims.strategy-execution-period-chain-bounded-runner-contract.v1` beschreibt:

- einen lueckenlosen lokalen Horizont von 2 bis 5;
- den weiterhin freigegebenen Horizont 2;
- die noch gesperrten Horizonte 3, 4 und 5;
- Aufloesung und vollstaendige Pruefung aller Kandidaten vor Periode 1;
- isolierte Kandidatenkopien und autoritative Uebergangsflags;
- Abbruch nach dem ersten Fehler ohne Teilresultat;
- die exakte fachliche Prefixprojektion fuer Periode 1, Uebergang 1 nach 2
  und Periode 2.

Der Vertrag wird read-only unter
`GET /api/run-control/strategy-period-chain-bounded-runner-contract`
ausgeliefert. Fuer diese URL gibt es keinen POST-, PUT- oder DELETE-Pfad.

## Prefixgrenze

Der Vergleich verwendet nicht das gesamte Kettenobjekt: Ketten-ID,
Gesamtdigest, `max_periods`, Gesamtperiodenzahl sowie Freigabe- und
Ergebnisidentitaet muessen sich bei einem groesseren Horizont unterscheiden
duerfen.

Verglichen werden alle fachlichen Felder aus:

- `period_effects[period=1]`;
- `transition_effects[from_period=1,to_period=2]`;
- `period_effects[period=2]`.

Die kanonische JSON-Projektion muss spaeter fachlich und byteweise exakt mit
dem gespeicherten PR140-Ergebnis uebereinstimmen. Toleranzen und versteckte
Fallbacks sind ausgeschlossen. PR142 definiert diese Projektion; PR144 wird
den Vergleich erstmals nach einer echten Fuenf-Perioden-Wirkungsprobe
ausgefuehrt. PR145 hat Start und Ablage kontrolliert angeschlossen.

## Laufgrenzen

Nach PR145 meldet der fortgeschriebene Vertrag ausdruecklich:

- `bounded_runner_enabled = true` fuer genau fuenf Perioden;
- `five_period_candidate_validation_enabled = true`;
- `five_period_chain_build_enabled = true`;
- `five_period_execution_enabled = true`;
- `five_period_server_start_enabled = true`;
- `five_period_idempotency_persistence_enabled = true`;
- `five_period_result_persistence_enabled = true`;
- `five_period_immutable_chain_snapshot_persistence_enabled = true`;
- `five_period_ui_start_enabled = true` (seit PR146; nur exakt fuenf Perioden);
- `prefix_comparison_execution_enabled = true`;
- `simulation_performed = false`.

Der bestehende Zwei-Perioden-Endpunkt und dessen Ergebnisschema werden nicht
geaendert. Die neue Vertrags-URL ist nur eine maschinenlesbare
Freigabeplanung.

## Tests

Unit- und API-Tests pruefen Horizont, Schrittfolge, Prefixfelder,
Ausschlussfelder, Sperrflags und reine GET-Semantik. Die bestehenden
Zwei-Perioden-Tests bleiben die Regression fuer den aktuellen Prefix.

## Grenzen und naechster Schritt

PR142 schreibt keine Metadaten, startet keinen Runner und erzeugt keine
Ausgabedatei. `incomming/` wird nicht gelesen und bleibt unversioniert. Der
Vertrag behauptet weder historische RNG- noch Vollgleichheit.

PR143 hat die kanonische Fuenf-Perioden-Kette gebaut und atomar validiert.
PR144 hat die fluechtige Ausfuehrung und den hier definierten
Prefixvergleich angeschlossen. PR145 hat den kontrollierten Serverstart und
die unveraenderliche Ergebnisablage ergaenzt. PR146 darf Workbench- und
Browserabnahme anschliessen.
