# IMS 2.x: Einperioden-Kontext fuer Snapshot-Bauplaene

Stand: PR112, 2026-09-02

## Fachliche Einordnung

Ein Strategieentwurf legt fest, welcher VU oder VN wann welcher Regel folgt
und welche Strategieparameter gelten. Fuer einen konkreten Regelaufruf fehlen
danach weiterhin periodenspezifische Informationen: Zufallsziehungen,
Zinssatz, Schockstatus, Marktwerte und benoetigte Vorperiodenzustaende.

PR112 beschreibt diese Informationen als expliziten Kontext zu genau einer
Periode. Er rekonstruiert weder einen historischen Lauf noch entscheidet er,
aus welcher kuenftigen Quelle die Werte stammen.

## Format und Bindung

Eine Validierungsanfrage besteht aus zwei getrennten Dokumenten:

- `draft`: unveraenderter PR108-Strategieentwurf;
- `context`: Dokument vom Typ
  `ims.strategy-assignment-snapshot-context.v1`.

Der Kontext nennt `draft_id`, `period` und je Entwurfszuordnung einen Eintrag
mit `actor_type`, `target_id`, `strategy_id` und `values`. Der Validator
uebersetzt den Entwurf erneut mit PR110 und erwartet fuer jeden Bauplan exakt
dessen `unresolved_snapshot_fields`. Dadurch entsteht kein paralleles,
handgepflegtes Strategie-zu-Snapshot-Mapping.

## Kontextquellen

| Kategorie | Felder | Noch offene Herkunft |
| --- | --- | --- |
| Ziehungen | `random_draws`, `normal_draws`, `draws` | kontrollierte moderne RNG-Policy oder explizites Testszenario |
| Periodenfinanzierung | `interest_rate`, Informationskosten | Szenario- oder Periodenparameter |
| Schock | `change_shock` | expliziter Perioden-/Regulierungsschock |
| Strategiezustand | Reserve-, Wechsler- und Marktanteilsschwellen | Szenario oder belegter Ausgangszustand |
| Markt | aktive Akteure, Schadenwerte, VU-Inputs, Marktindikator | aktueller Markt- und Aggregatzustand |
| Vorperiode | vorherige VN-Zahlen, Anfangsentscheidungen, Historie | kontrollierter Carryover |

Die Tabelle ist eine Herkunftsklassifikation, keine automatische
Quellenauswahl. Insbesondere erzeugt PR112 keine Zufallszahlen und leitet
keinen Markt- oder Vorperiodenwert ab.

## Validierungsumfang

Der Validator prueft:

- Vertragsversion, Basismodell und Einperioden-Scope;
- positive Periodennummer;
- identische `draft_id`;
- genau einen Kontexteintrag je Entwurfsziel;
- passende Strategie-ID und exakte offene Feldmenge;
- eindeutige JSON-Wertformen der vorhandenen Snapshotoberflaechen.

Zwei- und Vierervektoren werden in ihrer belegten Laenge geprueft. Zinssatz,
Marktindikator und Kosten muessen endliche Zahlen sein, Schockstatus ein
echter boolescher Wert und aktive VU positive Ganzzahlen. Der Validator
normalisiert keine Eingabe.

Verschachtelte `draws`, `initial_decisions`, `insurer_inputs` und `history`
werden bewusst noch nicht regelabhaengig interpretiert. Diese Semantik ist
vor einer Materialisierung separat zu belegen.

## Offen bleibende Werte

Mehrere aktuelle Snapshotfelder sind nullable. Ein explizites `null` ist bei
diesen Feldern ein gueltiger Ausdruck fuer `noch offen`. Der Bericht zaehlt
diese Werte als `explicitly_open_value_count` und setzt
`all_context_values_supplied` auf `false`. Es wird kein technischer
Loader-Default eingesetzt.

Auch bei vollstaendig gelieferten Werten bleibt
`snapshot_materialization_ready` immer `false`: PR112 prueft nur die
Vertragsform und verbraucht keinen Wert.

## API und Grenzen

`GET /api/strategies/assignment-snapshot-context-contract` liefert
Felddefinitionen, Quellenkategorien und geschlossene Grenzen. `POST
/api/strategies/assignment-snapshot-context-validation` validiert das Paar
aus Entwurf und Kontext zustandslos.

Beide Endpunkte schreiben nichts. Sie rufen keine Snapshot-Loader auf,
erzeugen keine Snapshots, verbinden nichts mit Run-Control oder Runner und
starten keine Simulation. Aus der Strukturpruefung folgt keine Behauptung
historischer RNG- oder Vollgleichheit.

## Naechster Schritt

PR113 kann den Vertrag als lokalen Kontextentwurf in der Workbench sichtbar
und pruefbar machen. Vor einer spaeteren Snapshot-Materialisierung muessen die
regelabhaengigen VN-Ziehungs-, Markt- und Historienstrukturen enger an ihre
vorhandenen Loader und Zustandsdataclasses gebunden werden.
