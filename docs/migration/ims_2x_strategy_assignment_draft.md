# IMS 2.x: Strategiezuordnungsentwurf und reine Validierung

Stand: 2026-09-02
Entwurf: `ims.strategy-assignment-draft.v1`
Validierung: `ims.strategy-assignment-draft-validation.v1`

## Einordnung

PR108 gibt einer kuenftigen Strategieauswahl erstmals ein konkretes,
versioniertes Austauschformat. Der Entwurf kann einzelne VU und VN mit einer
Katalogstrategie, ihrer zeitlichen Gueltigkeit und vorhandenen
Strategieparametern beschreiben. Er ist noch keine wirksame
Szenariokonfiguration.

Die API liest den Formatvertrag und prueft eingereichte JSON-Daten nur im
Speicher. Sie speichert nichts und ruft keine Regel auf.

## C-zu-Python-Mapping

| Historischer Ursprung | Python-Ziel | Bedeutung |
| --- | --- | --- |
| `IMSDATA.C`, `ACTION.st` | `StrategyAssignmentDraftEntry` | eine Strategie und Zeitangaben je einzelnem Akteur |
| `IMSDATA.C`, `vkrvu` und `vkrvn` | `strategy_id` plus Katalogpruefung | historische Regelbindung ueber stabile IMS-2.x-ID |
| `IMS.E`, `Vuauini`, `Vnauini` | `target_id` mit Vdefmd6-Grenzen | bekannte 25 VU und 200 VN |
| `IMS.E`, `Vdefmd6` | `base_model = "Vdefmd6"` | explizite Herkunft des ersten Entwurfsformats |
| vorhandene `*RuleParameters` | `parameter_schema` und `parameter_values` | belegte Parameterfelder ohne neue Defaults |
| vorhandene `*_parameters_from_mapping` | reine Loaderpruefung | bestehende Typ- und Stichprobengrenzen |

## JSON-Form

Der Dokumentkopf bindet den Entwurf an drei Versionen und seine erste
Basispopulation:

```json
{
  "schema_version": "ims.strategy-assignment-draft.v1",
  "catalog_schema_version": "ims.strategy-catalog.v1",
  "assignment_contract_schema_version": "ims.strategy-assignment-contract.v1",
  "base_model": "Vdefmd6",
  "scope": "partial_actor_assignments",
  "draft_id": "beispiel",
  "label": "Beispielentwurf",
  "assignments": []
}
```

Ein echter Entwurf muss mindestens eine Zuordnung enthalten. Das versionierte
Beispiel unter `tests/fixtures/strategy_assignment_draft_v1.json` ist
synthetisch. Seine Werte belegen nur Parser und Struktur; sie sind weder eine
historische Rekonstruktion noch eine fachliche Empfehlung.

Jede Zuordnung enthaelt:

- `actor_type` und `target_id` fuer genau ein VU oder VN;
- eine zum Akteur passende `strategy_id` aus dem Katalog;
- `activation_period`, `active_through_run` und `logical_time`;
- das exakt zur Strategie passende `parameter_schema`;
- alle Parameterfelder als Zweiervektoren fuer `legacy_sector_1` und
  `legacy_sector_2`.

Unbekannte Felder, implizite Defaults und Mehrfachzuordnungen desselben
Akteurs werden abgewiesen. Die Vdefmd6-Zielgrenzen sind VU 1-25 und VN 1-200.
`Vrvn01` muss `parameter_schema` und `parameter_values` jeweils mit `null`
angeben, weil seine expliziten Zufallsziehungen Laufdaten und keine
Strategieparameter sind.

## Pruefgrenze

`GET /api/strategies/assignment-draft-contract` beschreibt Form,
Zielgrenzen und gesperrte Funktionen. Ein
`POST /api/strategies/assignment-draft-validation` liefert einen
maschinenlesbaren Bericht. Ein fachlich ungueltiger, aber syntaktisch
lesbarer Entwurf ergibt HTTP 200 mit `valid = false`; unlesbares JSON ergibt
HTTP 400.

Der POST ist keine Schreiboperation. Jeder Bericht setzt
`writes_performed`, `snapshots_created`, `execution_performed` und
`simulation_performed` auf `false`. Weder SQLite noch andere Dateien werden
veraendert.

## Bewusst offene Punkte

- Die Teilmenge besitzt noch keine Merge- oder Ueberschreibungssemantik.
- Es gibt keine Gruppenbearbeitung und keine unterschiedlichen Strategien je
  historische Sektorposition.
- Die zwei Positionen werden nicht als Kfz oder Sach-Haftpflicht bezeichnet.
- Es gibt keinen geplanten Strategiewechsel und keine zusaetzlichen Sparten.
- Der Entwurf wird nicht in vorhandene Regel-Snapshots uebersetzt.
- Es gibt keine Workbench-Eingabe, Speicherung, Ausfuehrung oder Simulation.
- Die Validierung behauptet keine historische Vollgleichheit.

## Anschluss

PR109 kann den Entwurf in der Workbench erfassbar und gegen den neuen
Endpunkt pruefbar machen, weiterhin ohne Speicherung oder Ausfuehrung. Die
spaetere Snapshot-Uebersetzung bleibt ein eigener, fachlich rueckgebundener
Schritt.
