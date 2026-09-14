# PR142: Vertrag fuer den begrenzten Kettenrunner

Stand: 2026-09-14
Umsetzungsstand: PR142 umgesetzt

## Ziel

PR142 legt die Ausfuehrungsgrenze fuer eine spaetere Periodenkette mit zwei
bis hoechstens fuenf Perioden fest. Der bereits in PR139 bis PR141 belegte
Zwei-Perioden-Pfad bleibt unveraendert. Fuer drei bis fuenf Perioden wird in
diesem Schritt weder eine Kette gebaut noch ein Runner freigegeben.

Der Vertrag beantwortet vor der Implementierung:

- welche Kettenhorizonte die erste begrenzte Stufe umfasst;
- was vor dem ersten Runneraufruf vollstaendig geprueft sein muss;
- in welcher Reihenfolge Periodenschritt und Carryover spaeter erfolgen;
- wie ein Fehler ohne Teilresultat endet;
- welche Projektion des Prefixes 1-2 exakt stabil bleiben muss;
- welche Metadaten wegen des groesseren Gesamthorizonts nicht zum
  Prefixvergleich gehoeren.

## Historischer Bezug

| Quelle | Belegte Semantik | Grenze fuer PR142 |
| --- | --- | --- |
| `ESS.C:73-75` | aeussere Periodenschleife und Aufruf der logischen Zeitschritte | nur Ablaufreihenfolge, keine neue Scheduler-Portierung |
| `IMSDATA.C:14` | `SIMLAENGE = 100` | fuenf Perioden sind eine moderne Zwischenstufe, kein historischer Zielhorizont |
| PR139 | isolierte Ausfuehrung von Periode 1 und 2 | bleibt die einzige fluechtige Mehrperiodenausfuehrung |
| PR140/PR141 | dauerhafte Bedienung und Browserabnahme fuer genau zwei Perioden | Endpunkt, Ergebnis und UI bleiben unveraendert |

PR142 portiert keine C-Regel. Der historische Code belegt den periodischen
Ablauf und die 100-Perioden-Obergrenze, aber keinen besonderen
Fuenf-Perioden-Modus.

## Vertragsentscheidung

Der neue read-only Vertrag liegt unter:

`GET /api/run-control/strategy-period-chain-bounded-runner-contract`

Er setzt:

- `minimum_period_count = 2`;
- `maximum_period_count = 5`;
- lokale Perioden ab 1, lueckenlos und streng aufsteigend;
- denselben `run_index` und `max_periods` fuer alle Kandidaten;
- vollstaendige Kandidatenaufloesung, Digest- und Akteurspruefung vor dem
  ersten Runner;
- isolierte Kandidatenkopien ohne Mutation der gespeicherten Quellen;
- ausschliesslich die gespeicherten VU-/VN-Carryover-Flags;
- atomaren Abbruch beim ersten Fehler ohne spaetere Perioden und ohne
  Teilresultat.

Freigegeben bleibt nur der vorhandene Horizont 2. Die Periodenzahlen 3, 4 und
5 sind vertraglich beschrieben, aber noch nicht ausfuehrbar. Ein neuer POST-
Endpunkt wird nicht angelegt.

## Exakter Prefix 1-2

Eine Fuenf-Perioden-Kette besitzt notwendigerweise eine andere Ketten-ID,
einen anderen Gesamtdigest und einen anderen Horizont als eine
Zwei-Perioden-Kette. Auch `max_periods` im Kandidatenkontext ist verschieden.
Die vollstaendigen gespeicherten Objekte koennen deshalb nicht bytegleich
sein.

Exakt stabil bleiben muss stattdessen eine versionierte fachliche Projektion:

1. Periodenwirkung der Periode 1;
2. Carryover-Wirkung des Uebergangs 1 nach 2;
3. Periodenwirkung der Periode 2.

Die Projektion umfasst Perioden, globale Perioden, Regelaufrufzaehler,
Vorher-/Nachher-Zustaende, geaenderte Akteurs-IDs und den In-Memory-
Exportzaehler sowie alle fachlichen Carryover-Felder. Sie schliesst nur
Horizont- und Speicherumschlag aus: Ketten-ID, Kettendigest, `max_periods`,
Gesamtperiodenzahl, Freigabe- und Ergebnisidentitaet.

Die kanonische JSON-Darstellung dieser Projektion muss spaeter bytegleich
sein; eine numerische Toleranz ist nicht zulaessig. Schon die erste Differenz
blockiert die Freigabe des groesseren Horizonts.

## Umsetzung

- neuer versionierter Vertrag in
  `ims.strategies.execution_period_chain_bounded_runner_contract`;
- read-only API-Endpunkt in FastAPI- und Starlette-Fallback;
- Verweis aus dem bestehenden Periodenkettenvertrag;
- Unit-, API- und Dokumentationstests fuer Horizont, Reihenfolge,
  Prefixprojektion und gesperrte Grenzen;
- Fortschreibung der Planungs- und Migrationsindizes.

## Validierung

Die Tests muessen belegen:

- genau die Horizontgrenze 2 bis 5;
- den weiterhin allein freigegebenen Zwei-Perioden-Pfad;
- die vollstaendige Liste der fachlichen Prefixfelder;
- den Ausschluss ausschliesslich horizontabhaengiger Umschlagfelder;
- `bounded_runner_enabled = false` und keinen POST-Endpunkt;
- keinerlei Schreiben, Runner-, Carryover- oder Simulationsausfuehrung;
- unveraendertes Bestehen der PR139-bis-PR141-Regressionstests.

## Restplanung

- **PR142 (umgesetzt):** read-only Vertrag fuer zwei bis fuenf Perioden und
  exakte kanonische Prefixprojektion 1-2.
- **PR143 (umgesetzt):** eine vollstaendige Fuenf-Perioden-Kette
  serverseitig gebaut und atomar validiert; weiterhin ohne Runner.
- **PR144 (umgesetzt):** die gepruefte Fuenf-Perioden-Kette fluechtig
  auf isolierten Kandidatenkopien ausfuehren und den Prefixnachweis
  tatsaechlich berechnen.
- **PR145 (naechster Schritt):** kontrollierten Start, Idempotenz und
  Ergebnisablage anschliessen.
- **PR146:** Browserabnahme getrennt anschliessen.

## Schutzgrenzen

- keine neue oder geaenderte VU-/VN-Fachlogik;
- kein neuer Runneraufruf und kein Start-Endpunkt;
- keine Speicherung und keine fachlichen Ausgabedateien;
- kein Legacy-Vergleich und keine historische RNG- oder
  Vollgleichheitsbehauptung;
- `incomming/` bleibt unversioniert und wird nicht gelesen.
