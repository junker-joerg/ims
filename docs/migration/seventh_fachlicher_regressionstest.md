# Siebter fachlicher Regressionstest

## Zweck

Dieser Stand setzt PR 52 als weiteren schmalen fachlichen Regressionstest um.
Der Slice prueft die VN-Regel `preference` / Vrvn03 ueber explizite Snapshots
und ihre Kopplung an den vorhandenen VN-Schaden-/Settlement-Runner.

Der Test bleibt bewusst kleiner als ein historischer Modellvergleich: Er nutzt
keine neuen historischen Referenzdateien, startet keine Simulation und leitet
keine automatische historische Regelwahl ab.

## Test-Schnitt

| Bereich | Wert |
| --- | --- |
| Test | `tests/test_seventh_fachlicher_vn_preference_regression.py` |
| Regelart | `preference` |
| Historischer Bezug | `IMS.E`, `act Vrvn03` |
| Kontrollpfad 1 | `apply_vn_insurance_rule_snapshots` |
| Kontrollpfad 2 | `run_vn_settlement_period_from_mapping` |
| Policyholder | `21` |
| Versicherer | `11` und `12` |
| Periode | `5` |

Der Test nutzt ausschliesslich explizite Snapshot-Eingaben. Die VU-Werbewerte
waehlen in Sparte `0` Versicherer `12` und in Sparte `1` diagnostisch
Versicherer `11`; der Versicherungsstatus versichert nur Sparte `0`.

## Gepruefte fachliche Signale

Der Regressionstest prueft:

- `rule_kind = PREFERENCE`;
- `chosen_insurer_ids = [12, None]`;
- `selected_insurer_ids = [12, 11]`;
- `preference_scores = [{11: 0.1, 12: 0.9}, {11: 0.9, 12: 0.1}]`;
- `used_fallback = [False, False]`;
- `fallback_insurer_choice_draws is None`;
- Uebernahme derselben Snapshot-Entscheidung in den VN-Periodenlauf;
- Schaden-/Settlement-Grenze mit `damages = [9.0, 0.0]`;
- `chosen_insurer_sector_current = [12, None]`;
- `paid_premium_current = [4.0, 0.0]`;
- `claim_sum_current = [9.0, 0.0]`;
- `end_wealth_current = 87.0`;
- Reserven- und Policyholder-Aktualisierung beim gewaehlten Versicherer `12`.

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
- keine Uebernahme weiterer historischer Referenzdateien;
- kein Vergleich gegen eine historische DAT-Vollausgabe.

## Offene Folgearbeit

Nach PR 52 ist der siebte fachliche Slice umgesetzt. Der naechste geplante
Fachschnitt ist PR 53: Vrvn02 / `random` mit expliziten Draws und
Seed-/Draw-Grenze als schmaler Regressionstest.
