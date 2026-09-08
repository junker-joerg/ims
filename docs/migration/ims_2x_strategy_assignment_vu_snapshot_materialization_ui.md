# IMS 2.x: Materialisierte VU-Snapshots in der Workbench

Stand: PR122, 2026-09-08

## Ergebnis

PR122 ergaenzt die Strategie-Workbench um den Tab `VU-Snapshots`. Die Ansicht
ruft den bestehenden Endpunkt
`POST /api/strategies/assignment-vu-snapshot-materialization` auf und zeigt
nur dessen vollstaendige PR121-Ergebnisliste. Die zehn VU-Strategien werden
weiterhin auf acht vorhandene Snapshottypen abgebildet.

Ein Snapshot ist eine typisierte Eingabe fuer einen einzelnen VU-Regelaufruf.
Er ist noch kein berechneter VU-Zustand und kein Simulationsresultat.

## Zustands- und Herkunftsbeleg

Vor der Vorschau erfasst der Anwender einen getrennten PR120-Zustandsbeleg.
Die Workbench laedt dafuer die vorhandenen read-only Vertraege fuer:

- den PR119-Materialisierungseingang;
- den PR120-Zustandsbeleg;
- die PR121-Materialisierung.

Der gemeinsame Periodenzustand enthaelt `interest_rate`, `change_shock` und
`active_policyholder_count`. Fuer `Vrvu03`, `Vrvu04` und `Vrvu05` werden die
beiden dreistelligen Anspruchsprofile erfasst. `Vrvu04` verlangt zusaetzlich
`policyholders_t_minus_2`. Andere VU-Regeln besitzen absichtlich einen leeren
regelabhaengigen Werteblock.

Diese Werte werden nicht automatisch aus dem Kontext kopiert. PR120 vergleicht
beide Eingaben exakt. PR121 verwendet nach erfolgreichem Vergleich nur die
Kontextwerte fuer den Snapshot und meldet `state_values_consumed = false`.

## Vorschau

Nach vollstaendigem Erfolg zeigt die Workbench je VU:

- Strategie und gegebenenfalls `rule_kind`;
- Snapshottyp und Zielsammlung;
- typisierte Strategieparameter;
- explizite Gleich- oder Normalverteilungsziehungen, soweit vorhanden;
- Schwellen, Marktbestand und Vorperiodenbestand, soweit regelrelevant;
- Zinssatz und Schockstatus der Periode.

Verschachtelte Parameter und Vektoren werden lesbar aufgegliedert. Die
Vorschau bleibt im fluechtigen React-Zustand. Eine Aenderung an Entwurf,
Kontext oder Zustandsbeleg verwirft sie unmittelbar.

## Fehler- und Atomaritaetsgrenze

Fehler des PR119-Eingangs, des PR120-Herkunftsabgleichs oder eines
Snapshotloaders werden mit Pfad und Meldung angezeigt. PR121 gibt in jedem
Fehlerfall keine Snapshotliste frei; die Workbench zeigt deshalb niemals ein
veraltetes oder teilweises Ergebnis.

Die erfolgreiche Ansicht macht folgende Grenzen sichtbar:

- `state_provenance_validated = true`;
- `context_values_consumed = true`;
- `state_values_consumed = false`;
- `partial_results_returned = false`;
- `persistence_performed = false`;
- `execution_ready = false`;
- `runner_invoked = false`;
- `simulation_performed = false`.

## Ursprung und Aussagegrenze

Die Snapshottypen und Loader liegen in `python_port/ims/model/vu_rules.py` und
bilden die bereits portierten Ausschnitte aus `IMS.E`, `Vrvu01` bis `Vrvu10`,
ab. PR122 veraendert weder diese Regeln noch ihre Parameter oder
Zustandsuebergaenge.

Der Zustandsbeleg wird lokal eingegeben. Er authentifiziert keinen
historischen Lauf. Die Ziehungen werden nicht gegen einen Seed oder Draw-Plan
geprueft. Die Ansicht behauptet daher weder historische RNG-Gleichheit noch
historische Vollgleichheit.

## Naechster Schritt

PR123 plant den spaeteren kontrollierten Ausfuehrungsanschluss der gemeinsam
vorbereiteten VU- und VN-Snapshots. Dieser Folge-PR soll noch keine
Runner-Anbindung oder Simulation implementieren.
