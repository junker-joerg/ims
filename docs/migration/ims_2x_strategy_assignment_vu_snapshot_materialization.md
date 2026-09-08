# PR121: VU-Snapshots materialisieren

Stand: PR121, 2026-09-08

## Ergebnis

PR121 fuehrt die atomare Materialisierung fuer alle zehn katalogisierten
VU-Strategien ein. Ein vollstaendig gueltiger PR120-Eingang wird in die acht
bereits vorhandenen Snapshottypen uebersetzt. Die Materialisierung erzeugt nur
In-Memory-Dataclasses und startet weder eine Regel noch einen Runner.

## C-zu-Python-Zuordnung

| Historische Aktion | Snapshottyp | Vorhandener Loader |
| --- | --- | --- |
| `Vrvu01` | `VURandomUniformRuleSnapshot` | `vu_random_uniform_rule_snapshot_from_mapping` |
| `Vrvu02` | `VURandomNormalRuleSnapshot` | `vu_random_normal_rule_snapshot_from_mapping` |
| `Vrvu03` | `VUReserveMarkupRuleSnapshot` | `vu_reserve_markup_rule_snapshot_from_mapping` |
| `Vrvu04` | `VUNetSwitcherMarkupRuleSnapshot` | `vu_net_switcher_markup_rule_snapshot_from_mapping` |
| `Vrvu05` | `VUMarketShareMarkupRuleSnapshot` | `vu_market_share_markup_rule_snapshot_from_mapping` |
| `Vrvu06` | `VUExpectedClaimRuleSnapshot` | `vu_expected_claim_rule_snapshot_from_mapping` |
| `Vrvu07-09` | `VUForeignInfoRuleSnapshot` | `vu_foreign_info_rule_snapshot_from_mapping` |
| `Vrvu10` | `VUFreeLinearRuleSnapshot` | `vu_free_linear_rule_snapshot_from_mapping` |

Die Aktionen stammen aus `IMS.E`. Snapshottypen und Loader liegen unveraendert
in `python_port/ims/model/vu_rules.py`. PR121 fuegt keinen Rechenkern und keine
fachliche Regel hinzu.

## Materialisierungsfolge

`materialize_strategy_assignment_vu_snapshots` fuehrt folgende Schritte aus:

1. `validate_strategy_assignment_vu_snapshot_state` prueft die gesamte
   PR120-Anfrage.
2. `translate_strategy_assignment_draft` liefert den PR110-Bauplan und die
   typisierten Parameter.
3. Die offenen Snapshotfelder werden aus dem bereits geprueften PR119-Kontext
   eingesetzt.
4. Der je Strategie dokumentierte VU-Snapshotloader erzeugt die Dataclass.
5. Das Ergebnis wird gegen den erwarteten Snapshottyp geprueft.

Die Zustandswerte aus PR120 werden nicht erneut in den Snapshot eingesetzt.
Sie belegen nur, dass die entsprechenden Kontextwerte aus demselben
eingereichten Perioden- und VU-Zustand stammen. Damit bleibt der Kontext die
einzige Materialisierungsquelle.

## Atomare Fehlerbehandlung

Ist die PR120-Anfrage ungueltig, bleiben
`snapshot_loader_invocation_count = 0` und `snapshots = []`. Schlaegt spaeter
ein einzelner Loader oder die Typpruefung fehl, werden alle bereits erzeugten
Zwischenergebnisse verworfen. Es gibt keine teilweise verwertbare
Ergebnisliste; `partial_results_returned = false`.

Der Bericht unterscheidet Eingabefehler, Loaderfehler und Typabweichungen und
nennt den Pfad des betroffenen Kontexteintrags. Die Eingabe selbst wird nicht
veraendert.

## API

`GET /api/strategies/assignment-vu-snapshot-materialization-contract`
enthaelt weiterhin den read-only PR118-Bestand. Das neue Feld `operation`
beschreibt zusaetzlich die PR121-Materialisierung, ihre PR120-Vorbedingung und
die geschlossenen Ausfuehrungsgrenzen.

`POST /api/strategies/assignment-vu-snapshot-materialization` akzeptiert die
unveraenderte PR120-Anfrage und liefert entweder die vollstaendige geordnete
Snapshotliste oder keine Snapshots. Ungueltiges JSON wird mit Status 400
beantwortet; fachliche Vertrags- und Loaderfehler erscheinen als
strukturierter Bericht mit Status 200.

## Schutzgrenze

Die Materialisierung konsumiert die geprueften Kontextwerte nur fuer den Bau
der In-Memory-Snapshots. Der Zustandsbeleg wird nicht konsumiert oder
gespeichert. Keine Funktion `apply_vu_*`, kein Runner und keine Simulation
wird aufgerufen. `execution_ready = false`, `writes_performed = false` und
`persistence_performed = false` bleiben fest.

Die expliziten Ziehungen werden nicht gegen einen historischen Seed oder
Draw-Plan geprueft. PR121 behauptet weder historische RNG-Gleichheit noch
historische Vollgleichheit.

## Naechster Schritt

PR122 soll die vollstaendig materialisierten VU-Snapshots in der Workbench
rein lesend anzeigen. Speicherung, Regelanwendung, Runner und Simulation
bleiben auch dort gesperrt.
