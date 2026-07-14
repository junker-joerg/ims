# Fuenfter fachlicher Regressionstest

## Zweck

Dieser Stand ergaenzt PR 42 als weiteren schmalen fachlichen Regressionstest
auf dem Weg zu einer spaeter benutzbaren, kontrollierten Simulation. Der Slice
prueft die VN-Regel `sample_search` / Vrvn05 ueber explizite Snapshots und ihre
Kopplung an den vorhandenen VN-Schaden-/Settlement-Runner.

Der Test bleibt bewusst kleiner als ein historischer Modellvergleich: Er nutzt
keine neuen historischen Referenzdateien, startet keine Simulation und leitet
keine automatische historische Regelwahl ab.

## Test-Schnitt

| Bereich | Wert |
| --- | --- |
| Test | `tests/test_fifth_fachlicher_vn_sample_search_regression.py` |
| Regelart | `sample_search` |
| Historischer Bezug | `IMS.E`, `act Vrvn05` |
| Kontrollpfad 1 | `apply_vn_insurance_rule_snapshots` |
| Kontrollpfad 2 | `run_vn_settlement_period_from_mapping` |
| Policyholder | `21` |
| Versicherer | `11` und `12` |
| Periode | `5` |

Der Test nutzt ausschliesslich explizite Snapshot-Eingaben. Die
Stichprobenziehung wird ueber `insurer_choice_draws_by_sector` festgelegt; es
wird kein RNG-Pfad und kein Scheduler gestartet.

## Gepruefte fachliche Signale

Der Regressionstest prueft:

- `rule_kind = SAMPLE_SEARCH`;
- `chosen_insurer_ids = [12, None]`;
- `selected_insurer_ids = [12, 11]`;
- `selected_premiums = [4.0, 5.0]`;
- `sampled_insurer_ids = [[11, 12], [11]]`;
- `used_insurer_choice_draws_by_sector = [[0.0, 0.99], [0.0]]`;
- `information_cost = 3.0`;
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

Nach PR 42 bleiben fuer eine reviewbare und stabile benutzbare Demo-Simulation
voraussichtlich noch 5 bis 7 PRs. Der naechste groessere Schritt sollte deshalb
den expliziten Ausfuehrungsfreigabeplan fuer Run-Control vorbereiten, weiterhin
ohne sofortigen UI-Startbutton und ohne historische Vollgleichheitsbehauptung.
