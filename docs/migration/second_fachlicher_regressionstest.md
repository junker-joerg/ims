# Zweiter fachlicher Regressionstest

## Zweck

Dieser Stand setzt den unter
`docs/plans/second_fachlicher_slice_test_plan.md` geplanten zweiten fachlichen
Regressionstest um. Der Slice prueft eine VN-Versicherungsregelwirkung ueber
explizite `best_info`-Snapshots und bleibt bewusst kleiner als ein historischer
Modellvergleich.

## Test-Schnitt

| Bereich | Wert |
| --- | --- |
| Test | `tests/test_second_fachlicher_vn_rule_snapshot_regression.py` |
| Regelart | `best_info` |
| Kontrollpfad 1 | `apply_vn_insurance_rule_snapshots` |
| Kontrollpfad 2 | `run_vn_settlement_period_from_mapping` |
| Policyholder | `21` |
| Versicherer | `11` und `12` |
| Periode | `5` |

Der Test nutzt ausschliesslich explizite Snapshot-Eingaben. Er startet keinen
Scheduler, keine Simulation, keinen HTTP-Endpunkt, keine Workbench-UI und keinen
Run-Control-Pfad.

## Gepruefte fachliche Signale

Der Regressionstest prueft:

- `rule_kind = BEST_INFO`;
- `chosen_insurer_ids = [12, None]`;
- `selected_insurer_ids = [12, 11]`;
- `selected_premiums = [4.0, 5.0]`;
- `considered_insurer_ids = [[11, 12], [11, 12]]`;
- `information_cost = 4.0`;
- Uebernahme derselben Snapshot-Entscheidung in den VN-Periodenlauf;
- Schaden-/Settlement-Grenze mit `damages = [9.0, 0.0]`;
- `chosen_insurer_sector_current = [12, None]`;
- `paid_premium_current = [4.0, 0.0]`;
- `end_wealth_current = 83.0` nach einmaligem Abzug der gemeinsamen
  `information_cost = 4.0`.

## Grenzen

Der Test ist ein fachlicher Regressionstest fuer einen expliziten
Zwischenzustand. Er ist kein historischer Vollgleichheitsnachweis, kein Abgleich
eines kompletten IMS/ESS-Laufs und kein Nachweis fuer alle VN-Regeln.

Nicht enthalten:

- keine Simulation;
- kein Scheduler-Start;
- kein API-/UI-/Run-Control-Startpfad;
- keine neue Fachregel;
- keine automatische historische Regelwahl;
- keine unbelegte sektorale Aufteilung der gemeinsamen Informationskosten;
- kein Vergleich gegen eine historische DAT-Vollausgabe.

## Offene Folgearbeit

Der naechste fachliche Anschluss sollte entweder einen weiteren VN-Regel-
Snapshot-Slice oder ein eigenes VU-Carryover-Fixture planen. Ein spaeterer
Teilgleichheitsnachweis braucht weiterhin eigene historische Referenzfenster
und darf nicht aus diesem Test allein abgeleitet werden.
