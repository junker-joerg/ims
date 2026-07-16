# Achter fachlicher Regressionstest

## Zweck

Dieser Stand setzt PR 53 als weiteren schmalen fachlichen Regressionstest um.
Der Slice prueft die VN-Regel `random` / Vrvn02 ueber explizite Draw-Snapshots
und ihre Kopplung an den vorhandenen VN-Schaden-/Settlement-Runner.

Der Test bleibt bewusst kleiner als ein historischer Modellvergleich: Er nutzt
keine neuen historischen Referenzdateien, startet keine Simulation und leitet
keine automatische historische Regelwahl ab.

## Test-Schnitt

| Bereich | Wert |
| --- | --- |
| Test | `tests/test_eighth_fachlicher_vn_random_regression.py` |
| Regelart | `random` |
| Historischer Bezug | `IMS.E`, `act Vrvn02` |
| Kontrollpfad 1 | `apply_vn_insurance_rule_snapshots` |
| Kontrollpfad 2 | `run_vn_settlement_period_from_mapping` |
| Policyholder | `21` |
| Versicherer | `11` und `12` |
| Periode | `5` |

Der Test nutzt ausschliesslich explizite Snapshot-Draws:

- `status_draws = [0.5, 0.1]`;
- `insurer_choice_draws = [0.75, 0.0]`.

Der Szenariokontext enthaelt zwar einen `rng_seed`, aber die Vrvn02-Entscheidung
und die Schadenhoehen in diesem Slice kommen aus expliziten Draw-Feldern. Damit
ist die Seed-/Draw-Grenze dokumentiert: reproduzierbare Draw-Eingaben ja,
historische RNG-Folge oder Modulo-Gleichheit nein.

## Gepruefte fachliche Signale

Der Regressionstest prueft:

- `rule_kind = RANDOM`;
- `chosen_insurer_ids = [12, None]`;
- `selected_insurer_ids = [12, 11]`;
- `status_draws = [0.5, 0.1]`;
- `insurer_choice_draws = [0.75, 0.0]`;
- aktive VU-Auswahl auch fuer die unversicherte Sparte `1`;
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
- kein Vergleich gegen eine historische DAT-Vollausgabe;
- keine historische RNG- oder Modulo-Gleichheitsbehauptung.

## Offene Folgearbeit

Nach PR 53 ist der achte fachliche Slice umgesetzt. Der naechste geplante
Fachschnitt ist PR 54: VN-Schaden-/Settlement-Pfad aus `Vrvn01` bis `Vrvn03`
breiter gegen vorhandene explizite Fixtures pruefen.
