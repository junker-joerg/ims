# IMS 2.x: Materialisierte VN-Snapshots in der Workbench

Stand: PR117, 2026-09-07

## Fachliche Einordnung

PR117 zeigt erstmals, welche vollstaendig typisierten Eingaben aus einem
lokalen Strategieentwurf und seinem Einperiodenkontext entstehen. Die
angezeigten Objekte sind Eingaben fuer die sechs portierten VN-Regeln, noch
keine Ergebnisse einer Regel oder Simulation.

Der neue Tab ruft ausschliesslich
`POST /api/strategies/assignment-snapshot-materialization` auf. Dieser
PR116-Endpunkt fuehrt vor jedem Loaderaufruf die strengere PR115-Pruefung aus
und veroeffentlicht keine Teilresultate.

## Workbench-Ablauf

Im Tab `Kontext` bleibt die allgemeine PR112-Pruefung erhalten. Nach ihrem
Erfolg kann der Anwender mit `VN-Snapshots anzeigen` die ausdrueckliche
PR116-Materialisierung anfordern. Schlaegt die strengere regelabhaengige
Pruefung fehl, zeigt die Workbench die Fehlerpfade und erzeugt keine
Vorschau.

Bei vollstaendigem Erfolg wechselt die Workbench in den Tab `VN-Snapshots`.
Die Darstellung nennt Periode, Entwurf, Snapshot- und Loaderzahlen. Jeder VN
ist nach Strategie und `rule_kind` identifizierbar. Verschachtelte Parameter,
Ziehungen, Entscheidungen, Marktwerte und Historien werden mit fachlichen
Feldnamen lesbar aufgegliedert.

## Periodengrenze

Fuer Periode 1 wird nur `initial_decisions` angezeigt. Die neutralen Werte
der anderen Dataclass-Felder sind keine gelieferten historischen oder
modernen Eingaben und bleiben deshalb verborgen.

Ab Periode 2 zeigt die Workbench je Regel genau die in PR114 bis PR116
belegten Pflicht- und Bedingungsfelder. Ein `null` bei einem bedingten Feld
wird als nicht benoetigt oder nicht belegt kenntlich gemacht und nicht durch
einen UI-Default ersetzt.

## Lebensdauer der Vorschau

Die Vorschau liegt nur im fluechtigen React-Zustand des aktuellen
Browserfensters. Jede Aenderung an Entwurf, Bauplanbindung, Periode oder
Kontextwert verwirft sie. Es gibt keine Speicher-, Export- oder
Wiederherstellungsfunktion.

Der PR116-Bericht belegt in der Ansicht weiterhin:

- `partial_results_returned = false`;
- `persistence_performed = false`;
- `execution_ready = false`;
- `runner_invoked = false`;
- `execution_performed = false`;
- `simulation_performed = false`.

## Ursprung und Abweichungsgrenze

- `IMS.E:2185`, `Vrvn01`;
- `IMS.E:2406`, `Vrvn02`;
- `IMS.E:2627`, `Vrvn03`;
- `IMS.E:2948`, `Vrvn04`;
- `IMS.E:3229`, `Vrvn05`;
- `IMS.E:3521`, `Vrvn06`.

PR117 veraendert weder diese historische Fachlogik noch die portierten
Snapshot-Loader. Er erzeugt keine Zufallszahlen und behauptet keine
historische RNG- oder Vollgleichheit.

## Naechster Schritt

PR118 kann die VU-Seite als eigenen read-only Materialisierungsvertrag
inventarisieren. Eine Kopplung an Speicherung, Run-Control, Runner oder
Simulation ist damit noch nicht freigegeben.
