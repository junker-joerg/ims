# Sechster fachlicher Regressionstest

## Zweck

Dieser Stand setzt PR 51 als weiteren schmalen fachlichen Regressionstest um.
Der Slice prueft die VN-Regel `search_history` / Vrvn04 ueber explizite
Snapshots und ihre Kopplung an den vorhandenen VN-Schaden-/Settlement-Runner.

Der Test bleibt bewusst kleiner als ein historischer Modellvergleich: Er nutzt
keine neuen historischen Referenzdateien, startet keine Simulation und leitet
keine automatische historische Regelwahl ab.

## Test-Schnitt

| Bereich | Wert |
| --- | --- |
| Test | `tests/test_sixth_fachlicher_vn_search_history_regression.py` |
| Regelart | `search_history` |
| Historischer Bezug | `IMS.E`, `act Vrvn04` |
| Kontrollpfad 1 | `apply_vn_insurance_rule_snapshots` |
| Kontrollpfad 2 | `run_vn_settlement_period_from_mapping` |
| Policyholder | `21` |
| Versicherer | `11` und `12` |
| Periode | `5` |

Der Test nutzt ausschliesslich explizite Snapshot-Eingaben. Die Vrvn04-Historie
enthaelt je Sparte einen frueheren versicherten Eintrag aus Periode `4`; deshalb
wird kein Fallback-Draw und kein RNG-Pfad benoetigt.

## Gepruefte fachliche Signale

Der Regressionstest prueft:

- `rule_kind = SEARCH_HISTORY`;
- `chosen_insurer_ids = [12, None]`;
- `selected_insurer_ids = [12, 11]`;
- `selected_history_periods = [4, 4]`;
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

Nach PR 51 ist der sechste fachliche Slice umgesetzt. Der naechste geplante
Fachschnitt ist PR 52: Vrvn03 / `preference` als siebter fachlicher
Regressionstest oder, falls die Reviewgrenze es verlangt, zuerst als kleiner
Plan-Schnitt.
