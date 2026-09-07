# IMS 2.x: Atomare VN-Snapshot-Materialisierung

Stand: PR116, 2026-09-07

## Fachliche Einordnung

PR110 hat gueltige Strategieentwuerfe auf vorhandene Snapshottypen abgebildet.
PR112 bis PR115 haben die noch offenen Einperiodenwerte beschrieben und
regelabhaengig geprueft. PR116 schliesst erstmals diese beiden Seiten zu
vollstaendigen `VNInsuranceRuleSnapshot`-Objekten zusammen.

Das ist noch keine Regelausfuehrung. Ein Snapshot ist hier nur ein
vollstaendig typisierter Eingabestand fuer genau eine VN-Regel und eine
Periode.

## Ablauf und Atomaritaet

`materialize_strategy_assignment_snapshots` ruft zuerst unveraendert die
PR115-Validierung auf. Ist sie nicht vollstaendig gueltig, werden weder
verschachtelte Werte erneut geladen noch Snapshot-Loader aufgerufen.

Bei gueltigem Eingang werden die VN-Bauplaene erneut deterministisch aus dem
Entwurf uebersetzt und ueber Akteurstyp und Ziel-ID ihren Kontexteintraegen
zugeordnet. Pro Eintrag entsteht lokal ein Payload aus:

- `policyholder_id` und `rule_kind` aus dem PR110-Zielvertrag;
- dem bereits belegten Parameterblock aus dem Strategieentwurf;
- den fuer die Kontextperiode konsumierten PR114-Feldern.

Verschachtelte Werte werden dabei mit ihren vorhandenen Loadern in
`VNInsuranceDecision`, Draw-, Werbe-, Historien- oder Praemienobjekte
ueberfuehrt. Danach wird ausschliesslich der bereits vorhandene Loader
`vn_insurance_rule_snapshot_from_mapping` aufgerufen.

Die Snapshots bleiben waehrend des gesamten Vorgangs lokal. Schlaegt ein
spaeter Loader trotz erfolgreicher Vorvalidierung fehl, enthaelt der Bericht
keine Snapshots. Es gibt keine teilweise verwertbare Ergebnisliste.

## Periodengrenze

In Periode 1 wird ausschliesslich `initial_decisions` aus dem Kontext
materialisiert. Die anderen offenen Felder werden vom historischen
Startzweig nicht konsumiert und daher auch nicht in den Snapshot uebernommen.
Die Snapshot-Dataclass behaelt fuer sie ihre vorhandenen neutralen Werte.

Ab Periode 2 werden je Regel genau die belegten Werte uebernommen:

| Regel | Materialisierte Kontextwerte |
| --- | --- |
| `Vrvn01` | Auswahlziehungen und aktive VU |
| `Vrvn02` | Status-/Auswahlziehungen, aktive VU und Schockstatus |
| `Vrvn03` | Schadenwahrscheinlichkeiten, Werbung, Schockstatus und bedingte Fallback-Ziehungen |
| `Vrvn04` | Schadenwerte, Historie, aktive VU, Schock und bedingte Fallbacks |
| `Vrvn05` | Stichprobenziehungen, VU-Praemien, Marktindikator, Schockstatus und Stichprobenkosten |
| `Vrvn06` | VU-Praemien, Marktindikator, Schockstatus und Vollinformationskosten |

Es werden keine fehlenden Werte hergeleitet und keine Zufallszahlen erzeugt.

## Bericht und API

`POST /api/strategies/assignment-snapshot-materialization` nimmt weiterhin
das gemeinsame Objekt aus `draft` und `context` entgegen. Der Bericht nennt:

- Gueltigkeit des PR115-Eingangs;
- Periode und erwartete Snapshotzahl;
- Aufrufzahlen der verschachtelten und eigentlichen Snapshot-Loader;
- Fehler mit Stufe und JSON-Pfad;
- bei Gesamterfolg die typisierten VN-Snapshots samt Strategie- und
  Collection-Zuordnung.

`GET /api/strategies/assignment-snapshot-materialization-contract` bleibt
read-only. Der Vertrag weist jetzt die verfuegbare Materialisierung und ihre
weiterhin geschlossenen Ausfuehrungsgrenzen aus.

## Ursprung und Abweichungsgrenze

- `IMS.E:2185`, `Vrvn01`;
- `IMS.E:2406`, `Vrvn02`;
- `IMS.E:2627`, `Vrvn03`;
- `IMS.E:2948`, `Vrvn04`;
- `IMS.E:3229`, `Vrvn05`;
- `IMS.E:3521`, `Vrvn06`.

PR116 bildet nur explizit gelieferte moderne Eingaben auf die bereits
portierten Snapshot-Dataclasses ab. Er rekonstruiert keine historische
RNG-Bibliothek und behauptet weder gleiche Zufallsfolgen noch historische
Vollgleichheit.

## Geschlossene Grenzen

Der Bericht setzt stets:

- `partial_results_returned = false`;
- `writes_performed = false`;
- `persistence_performed = false`;
- `execution_ready = false`;
- `execution_performed = false`;
- `runner_invoked = false`;
- `simulation_performed = false`.

Weder `apply_vn_insurance_rule_snapshot` noch ein Runner oder eine Simulation
wird aufgerufen.

## Naechster Schritt

PR117 kann die materialisierten In-Memory-Snapshots als lesbare Vorschau in
der Workbench anzeigen. Speicherung und Ausfuehrung bleiben getrennte
spaetere Entscheidungen.
