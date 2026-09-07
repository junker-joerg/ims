# IMS 2.x: Regelabhaengige VN-Kontextvalidierung

Stand: PR115, 2026-09-07

## Fachliche Einordnung

PR112 konnte verschachtelte VN-Werte nur als allgemeines JSON pruefen. PR114
hat ihre neun konkreten Formen und die Verwendung in `Vrvn01` bis `Vrvn06`
festgelegt. PR115 setzt diese Beschreibung als reine Validierung um.

Der neue Bericht beantwortet nur die Frage: Sind der Entwurf und seine
Einperiodenwerte streng genug bestimmt, damit ein spaeterer Schritt die
vorhandenen Snapshotloader ohne still ergaenzte Fachwerte aufrufen koennte?
Er erzeugt selbst keinen Snapshot.

## Atomare Grundgrenze

`validate_strategy_assignment_snapshot_materialization_input` ruft zuerst den
unveraenderten PR112-Validator auf. Ist Entwurf, Bauplanbindung, Periode,
Eintragsmenge oder offene Feldmenge dort ungueltig, endet PR115 mit
`base_context_valid = false`. Kein verschachtelter Loader wird dann
aufgerufen.

Bei gueltiger Grundform werden alle VN-Eintraege geprueft. Fehler koennen fuer
mehrere Eintraege gesammelt werden, es gibt aber keine Teilfreigabe und keine
Teilresultate. `materialization_input_valid` wird nur bei einem fehlerfreien
Gesamtbericht `true`.

## Periode 1

Alle sechs historischen VN-Regeln verwenden in `IMS.E` in Periode 1 die
gespeicherten Startwerte fuer Versicherungsstatus und Versicherer beider
Risiken. PR115 verlangt deshalb genau zwei Objekte in `initial_decisions`:

- genau einmal `sector_index = 0` und einmal `sector_index = 1`;
- `insured` als echter boolescher Wert;
- positive `insurer_id` genau bei versicherten Entscheidungen;
- optionale, endliche und nicht negative Praemie.

Andere gemeinsame Snapshotfelder werden in Periode 1 vom vorhandenen
VN-Dispatch nicht konsumiert und daher in PR115 nicht fachlich umgedeutet.

## Perioden ab 2

| Regel | Streng gepruefter Eingang | Bedingung |
| --- | --- | --- |
| `Vrvn01` | zwei VU-Wahlziehungen, eindeutige aktive VU | aktive Liste nicht leer |
| `Vrvn02` | je zwei Status- und VU-Wahlziehungen, eindeutige aktive VU, Schockstatus | aktive Liste nicht leer |
| `Vrvn03` | zwei Schadenwahrscheinlichkeiten, nicht leere eindeutige VU-Werbebloecke | zwei Fallback-Ziehungen, sobald ein Sektor keine positive Werbung besitzt |
| `Vrvn04` | zwei Schadenwahrscheinlichkeiten, eindeutige Historie, aktive VU | Historie liegt vor der Kontextperiode; Fallback-Ziehungen und aktive VU bei fehlender versicherter Sektorhistorie |
| `Vrvn05` | Marktindikator, nicht leere eindeutige VU-Praemien, Informationskosten, zwei Ziehungslisten | Normal- oder Schockstichprobengroesse ist positiv und durch Draws gedeckt |
| `Vrvn06` | Marktindikator, nicht leere eindeutige VU-Praemien, Informationskosten | keine Wahlziehungen werden geprueft oder benoetigt |

Ziehungen muessen endliche Zahlen in `[0.0, 1.0)` sein. Werbe- und
Praemienvektoren enthalten exakt zwei endliche, nicht negative Werte. Aktive
VU-Listen sowie VU-Eingangslisten werden nicht still dedupliziert.

## Vorhandene Loader bleiben massgeblich

Nach der strengeren Formpruefung ruft PR115 den in PR114 dokumentierten
Loader fuer den jeweiligen verschachtelten Wert auf. Dadurch bleibt die
Verbindung zu `VNInsuranceDecision`, den regelabhaengigen Draw-Dataclasses,
`VNPreferenceInsurerInput`, `VNSearchInsuranceHistoryEntry` und
`VNSampleSearchInsurerInput` pruefbar.

Die geladenen Objekte werden nur innerhalb desselben Validierungsaufrufs fuer
Fallback- und Stichprobenbedingungen betrachtet. Sie werden nicht im Bericht
aufbewahrt, nicht in `VNInsuranceRuleSnapshot` eingesetzt und nicht an einen
Regelkern weitergegeben.

## Ursprung im Altcode und Abweichungsgrenze

- `IMS.E:2185`, `Vrvn01`: Pflichtversicherung und aktive Zufallsauswahl;
- `IMS.E:2406`, `Vrvn02`: Status- und Auswahlziehungen;
- `IMS.E:2627`, `Vrvn03`: Werbung und Zufallsfallback;
- `IMS.E:2948`, `Vrvn04`: fruehere versicherte Praemien und Fallback;
- `IMS.E:3229`, `Vrvn05`: `g0/g1`-Stichproben und Informationskosten;
- `IMS.E:3521`, `Vrvn06`: Praemieninformation aller aktiven VU.

PR115 prueft moderne explizite Eingaben. Er rekonstruiert weder die
historische Modulo-RNG-Folge noch die damalige Reihenfolge gleichzeitiger
Subjekte. Die bekannte `Vrvn03`-Nenner-Eigenheit bleibt unveraendert in der
Regeldokumentation festgehalten; hier wird keine neue Fachlogik eingefuehrt.

## API und Bericht

`GET /api/strategies/assignment-snapshot-materialization-validation-contract`
beschreibt Reihenfolge, Umfang und Grenzen. `POST
/api/strategies/assignment-snapshot-materialization-validation` nimmt das
unveraenderte Paar aus `draft` und `context` entgegen.

Der Bericht nennt Grundstatus, Periode, erwartete und gueltige VN-Eintraege,
erfolgreich gepruefte verschachtelte Werte, Loaderaufrufe und alle Fehler mit
Stufe und JSON-Pfad. Er setzt stets:

- `context_values_consumed = false`;
- `nested_loader_results_retained = false`;
- `snapshot_loader_invocation_performed = false`;
- `snapshot_materialization_ready = false`;
- `snapshots_created = false`;
- `execution_performed = false`;
- `simulation_performed = false`.

Es erfolgen keine Speicherung, keine Runner-Kopplung und keine historische
RNG- oder Vollgleichheitsbehauptung.

## Naechster Schritt

PR116 kann den gueltigen Gesamteingang atomar in vorhandene Snapshot-
Dataclasses uebertragen. Auch dieser Schritt soll zunaechst weder speichern
noch einen Runner oder eine Simulation starten.
