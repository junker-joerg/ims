# PR118: VU-Snapshot-Materialisierungsbestand

## Ergebnis

PR118 beschreibt die spaetere VU-Snapshot-Materialisierung als eigenen,
versionierten read-only Vertrag. Er deckt alle zehn katalogisierten
VU-Strategien ab: neun Vdefmd6-Regeln und die historisch vorhandene, dort
nicht gruppierte Regel `Vrvu10`.

Der Vertrag zaehlt acht bestehende Snapshottypen und acht Collections.
`Vrvu07`, `Vrvu08` und `Vrvu09` teilen sich bewusst
`VUForeignInfoRuleSnapshot`; `dumping`, `average` und `attack` waehlen darin
unterschiedliche BAV-Fremdinformationsvektoren.

## C-zu-Python-Zuordnung

| Altcode | Python-Snapshot | Offene Besonderheit |
| --- | --- | --- |
| `IMS.E`, `act Vrvu01` | `VURandomUniformRuleSnapshot` | vier explizite Gleichverteilungsziehungen |
| `IMS.E`, `act Vrvu02` | `VURandomNormalRuleSnapshot` | vier explizite Normalziehungen |
| `IMS.E`, `act Vrvu03` | `VUReserveMarkupRuleSnapshot` | zwei Reserveschwellen; historischer Schockzweig vergleicht gegen null |
| `IMS.E`, `act Vrvu04` | `VUNetSwitcherMarkupRuleSnapshot` | zwei Nettowechslerschwellen und zwei Vorperiodenbestaende; Regel erst ab Periode 3 |
| `IMS.E`, `act Vrvu05` | `VUMarketShareMarkupRuleSnapshot` | zwei Marktanteilsschwellen und Zahl aktiver VN |
| `IMS.E`, `act Vrvu06` | `VUExpectedClaimRuleSnapshot` | Schadenanzahl und Schadensumme aus dem VU-Zustand |
| `IMS.E`, `act Vrvu07-09` | `VUForeignInfoRuleSnapshot` | BAV-Vektoren `Pm/Wm`, `Dp/Dw` oder `Mp/Mw` |
| `IMS.E`, `act Vrvu10` | `VUFreeLinearRuleSnapshot` | freie lineare Regel ausserhalb der Vdefmd6-Gruppen |

Alle Typen stammen aus `python_port/ims/model/vu_rules.py`. Die Zuordnung zu
Loader und Collection stammt unveraendert aus dem PR110-Vertrag in
`assignment_snapshot_translation.py`.

## Offene Snapshotfelder

Gemeinsam offen sind `interest_rate` und `change_shock`. Hinzu kommen je nach
Regel `random_draws`, `normal_draws`, `reserve_thresholds`,
`net_switcher_thresholds`, `previous_policyholders_sector`,
`market_share_thresholds` oder `active_policyholder_count`.

Der heutige Python-Code besitzt an mehreren Stellen technische Defaults oder
Runner-Fallbacks. Dazu gehoeren Zins `0.0`, Schockstatus `false`,
Nullschwellen, RNG-Ziehungen aus dem Laufkontext, VU-Vorperiodenbestaende und
die aktive VN-Zahl aus dem BAV-Zustand. PR118 dokumentiert diese Pfade nur.
Sie sind keine Freigabe, sie bei einer spaeteren Materialisierung still als
fachliche Defaults zu verwenden.

## Zustaende ausserhalb des Snapshots

Die Regelkerne lesen ausserdem den aktuellen Periodenindex sowie
VU-Praemien, Werbung und Reserven. `Vrvu04` und `Vrvu05` benoetigen
VN-Bestaende, `Vrvu06` Schadenanzahlen und Schadensummen, und `Vrvu07` bis
`Vrvu09` die zuvor gebildeten BAV-Fremdinformationen. Diese Werte werden im
Vertrag getrennt von den Snapshotfeldern ausgewiesen, damit ein Folge-PR
nicht versehentlich Loaderdaten und Runnerzustand vermischt.

## API und Schutzgrenze

`GET /api/strategies/assignment-vu-snapshot-materialization-contract` liefert
Ziele, offene Felder, Zustandsabhaengigkeiten und die aktuelle Grenzlage.
Andere HTTP-Methoden sind nicht zugelassen.

PR118 definiert noch kein VU-Eingabeformat, validiert keine Werte und ruft
keinen Snapshotloader auf. Er speichert nichts, koppelt keinen Runner an und
startet keine Simulation. Es wird weder historische RNG-Gleichheit noch
historische Vollgleichheit behauptet.

## Offene Punkte

- fachliche Quelle und Gueltigkeitsbereich der drei Schwellenwertfamilien;
- explizite Ziehungen gegen kontrollierte moderne RNG-Quelle;
- verbindliche Herkunft von Vorperiodenbestand und aktiver VN-Zahl;
- Eingabeform fuer Periode 1, Periode 2 bei `Vrvu04` und aktive Regelperioden;
- Behandlung von `Vrvu10` ausserhalb des Vdefmd6-Profils.

## Naechster Schritt

Ein Folge-PR kann daraus einen kleinen VU-Eingabe- und Validierungsvertrag
ableiten. Vor einer Materialisierung muessen insbesondere die
Schwellenwertquellen und die nicht zu uebernehmenden Loader-Fallbacks
fachlich festgelegt sein.
