# Strategieentwurf zu Regel-Snapshot-Bauplan

Stand: PR110, 2026-09-02

## Fachliche Einordnung

Im historischen Modell verweist `ACTION.st` auf eine VU- oder VN-Regel. Die
Parameter der in `IMS.E` definierten `Vrvu*`- und `Vrvn*`-Funktionen werden bei
der Initialisierung aus `Vuauini` beziehungsweise `Vnauini` an den einzelnen
Akteur gebunden. PR108 hat diese Bindung als validierbaren Entwurf abgebildet.

PR110 uebersetzt eine solche gueltige Bindung nun eindeutig auf die bereits
portierten Python-Snapshotformen. Der Schritt rekonstruiert dabei keinen
historischen Lauf und erzeugt keine neuen fachlichen Eingaben.

## Mapping

| Historische Regel | Strategie-ID | Vorhandener Snapshottyp | Variante |
| --- | --- | --- | --- |
| `Vrvu01` | `vu.vrvu01` | `VURandomUniformRuleSnapshot` | - |
| `Vrvu02` | `vu.vrvu02` | `VURandomNormalRuleSnapshot` | - |
| `Vrvu03` | `vu.vrvu03` | `VUReserveMarkupRuleSnapshot` | - |
| `Vrvu04` | `vu.vrvu04` | `VUNetSwitcherMarkupRuleSnapshot` | - |
| `Vrvu05` | `vu.vrvu05` | `VUMarketShareMarkupRuleSnapshot` | - |
| `Vrvu06` | `vu.vrvu06` | `VUExpectedClaimRuleSnapshot` | - |
| `Vrvu07` | `vu.vrvu07` | `VUForeignInfoRuleSnapshot` | `dumping` |
| `Vrvu08` | `vu.vrvu08` | `VUForeignInfoRuleSnapshot` | `average` |
| `Vrvu09` | `vu.vrvu09` | `VUForeignInfoRuleSnapshot` | `attack` |
| `Vrvu10` | `vu.vrvu10` | `VUFreeLinearRuleSnapshot` | - |
| `Vrvn01` | `vn.vrvn01` | `VNInsuranceRuleSnapshot` | `compulsory` |
| `Vrvn02` | `vn.vrvn02` | `VNInsuranceRuleSnapshot` | `random` |
| `Vrvn03` | `vn.vrvn03` | `VNInsuranceRuleSnapshot` | `preference` |
| `Vrvn04` | `vn.vrvn04` | `VNInsuranceRuleSnapshot` | `search_history` |
| `Vrvn05` | `vn.vrvn05` | `VNInsuranceRuleSnapshot` | `sample_search` |
| `Vrvn06` | `vn.vrvn06` | `VNInsuranceRuleSnapshot` | `best_info` |

## Zweistufige Uebersetzung

Die erste Stufe ist in PR110 implementiert:

1. Den gesamten Entwurf mit dem PR108-Vertrag validieren.
2. Die Parameterwerte mit dem bereits vorhandenen Regelparameterloader in die
   vorhandene Parameter-Dataclass ueberfuehren.
3. Ziel-ID, gemeinsame Regelvariante und Parameter als partielles
   `snapshot_payload` ausgeben.
4. Alle uebrigen Felder des realen Snapshottyps als
   `unresolved_snapshot_fields` ausweisen.

Die zweite Stufe bleibt bewusst offen. Sie muss periodenspezifisch unter
anderem Draws, `change_shock`, Zinssatz, Schwellen, aktive VU,
Informationskosten, Marktwerte und benoetigte Vorperiodenzustaende liefern.
Welche Werte fuer eine konkrete Periode gelten, ist aus einem Strategieentwurf
allein nicht ableitbar.

## Warum noch kein Snapshot-Loader aufgerufen wird

Mehrere bestehende Snapshot-Loader besitzen technische Fallbackwerte, etwa
`0.0` fuer Zinssatz oder VU-Schwellen und `False` fuer `change_shock`. Diese
Defaults sind fuer explizite Tests und alte Aufrufer nuetzlich, belegen aber
nicht den fachlich richtigen Wert eines neuen Strategieentwurfs. PR110 ruft
diese Loader daher nicht auf und meldet die Felder stattdessen als offen.

Das Ergebnis ist ein deterministischer Bauplan fuer einen vorhandenen
Snapshottyp, kein ausfuehrbarer Snapshot. `snapshots_created`,
`execution_performed` und `simulation_performed` bleiben `false`.

## API

`GET /api/strategies/assignment-snapshot-translation-contract` liefert das
vollstaendige Mapping und die geschlossenen Grenzen. `POST
/api/strategies/assignment-snapshot-translation` akzeptiert einen
PR108-Entwurf und liefert die Bauplaene nur bei vollstaendig erfolgreicher
Validierung. Ein fehlerhafter Entwurf wird nicht teilweise uebersetzt.

Beide Endpunkte sind zustandslos. Sie schreiben weder Workbench-Metadaten noch
Dateien und sind nicht mit Run-Control, Runner oder Simulation verbunden.

## Offene Punkte

- expliziter Vertrag fuer Perioden- und Marktinput je Snapshotfamilie;
- Entscheidung, welche Werte aus Szenario, Vdefmd6-Ausgangszustand oder
  kontrollierter moderner RNG-Policy stammen;
- Materialisierung erst bei vollstaendigem Kontext;
- spaetere, separat freizugebende Runner-Kopplung;
- keine Behauptung historischer RNG- oder Vollgleichheit.
