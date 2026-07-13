# Erster fachlicher Regressionstest

## Zweck

Dieser Stand ordnet den ersten fachlichen Regressionstest der IMS-Migration ein.
Er ist bewusst klein: Er prueft den VN-State-Carryover eines expliziten
Fixture-Uebergangs und behauptet keine historische Vollgleichheit.

## Test-Schnitt

| Bereich | Wert |
| --- | --- |
| Test | `tests/test_first_fachlicher_vn_carryover_regression.py` |
| Fixture | `tests/fixtures/replay_vn_policyholder_transition_plan.json` |
| Kontrollpfad | `probe_explicit_transition_carryover(..., apply_vn=True)` |
| Portierter Baustein | `apply_vn_state_carryover` |
| Versicherer | `11` |
| Policyholder | `21` |
| Uebergang | globale Periode `21 -> 22` |

Der Test nutzt ausschliesslich vorhandene portierte Bausteine und explizite
Fixture-Zustaende. Er startet keinen Scheduler, keine Simulation, keinen
HTTP-Endpunkt, keine Workbench-UI und keinen Run-Control-Pfad.

## Gepruefte fachliche Signale

Der Regressionstest prueft:

- `carried_insurer_ids = [11]`;
- `carried_policyholder_ids = [21]`;
- `from_global_period = 21`;
- `to_global_period = 22`;
- `vn_carryover_planned = true`;
- `vn_carryover_executed = true`;
- `diagnostic_candidate_ids_match = true`;
- `previous_result_source = "explicit_fixture_snapshot"`;
- die VN-Source-Field-Vertraege aus
  `VN_CARRYOVER_INSURER_SOURCE_FIELDS` und
  `VN_CARRYOVER_POLICYHOLDER_SOURCE_FIELDS`;
- `carried_insurer_state["11"]["premiums_current"] = 101.0`;
- `carried_policyholder_state["21"]["end_wealth_current"] = 999.0`;
- `writes_performed = false`;
- `execution_performed = false`;
- `simulation_performed = false`;
- `automatic_historical_rule_selection_performed = false`.

## Grenzen

Der Test ist ein fachlicher Regressionstest fuer einen expliziten
Zwischenzustand. Er ist kein historischer Vollgleichheitsnachweis, kein
Abgleich eines kompletten IMS/ESS-Laufs und kein Nachweis fuer alle VN-Regeln.

Nicht enthalten:

- keine Simulation;
- kein Scheduler-Start;
- kein API-/UI-/Run-Control-Startpfad;
- keine neue Fachregel;
- keine automatische historische Regelwahl;
- kein historisches Vorperiodenergebnis, das nicht im Fixture belegt ist;
- kein Vergleich gegen eine historische DAT-Vollausgabe.

## Offene Folgearbeit

Der naechste fachliche Anschluss ist nun unter
`docs/plans/second_fachlicher_slice_test_plan.md` als VN-Regelwirkung ueber
explizite `best_info`-Snapshots geplant. Ein spaeterer Teilgleichheitsnachweis
braucht weiterhin eigene historische Referenzfenster und darf nicht aus diesem
Test allein abgeleitet werden.
