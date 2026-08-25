# Vierter fachlicher Regressionstest

## Zweck

Dieser Stand ergaenzt einen vierten schmalen fachlichen Regressionstest nach
der read-only Adapter-Resultat-UI. Der Slice verbindet die bereits belegte
VN-`best_info`-Regelwirkung mit dem vorhandenen VN-State-Carryover ueber zwei
explizite Perioden.

Der Test bleibt bewusst kleiner als ein historischer Modellvergleich: Er nutzt
keine neuen historischen Referenzdateien, startet keine Simulation und leitet
keine automatische historische Regelwahl ab.

## Test-Schnitt

| Bereich | Wert |
| --- | --- |
| Test | `tests/test_fourth_fachlicher_vn_best_info_carryover_regression.py` |
| Kontrollpfad | `run_vn_settlement_multi_period_from_mappings` |
| Portierter Baustein | `apply_vn_state_carryover` |
| Regelart | `best_info` |
| Policyholder | `21` |
| Versicherer | `11` und `12` |
| Uebergang | lokale Perioden `5 -> 6` |
| Globale Perioden | `5 -> 6` |

Die erste Periode nutzt einen expliziten `best_info`-Snapshot und einen
expliziten Schaden-/Settlement-Snapshot. Die zweite Periode enthaelt keine
neuen VN-Regel-, Schaden- oder Settlement-Snapshots. Damit prueft der Test, dass
der mutierte VN-Zustand aus Periode `5` ueber `carry_forward_vn_state=True` in
Periode `6` sichtbar bleibt.

## Gepruefte fachliche Signale

Der Regressionstest prueft:

- `total_insurance_rule_applications = 1`;
- `total_damage_settlement_applications = 1`;
- `total_settlement_applications = 1`;
- `carryovers[0].insurer_ids = [11, 12]`;
- `carryovers[0].policyholder_ids = [21]`;
- `chosen_insurer_ids = [12, None]`;
- `information_cost = 4.0`;
- `damages = [9.0, 0.0]`;
- `paid_premium_current = [4.0, 0.0]`;
- `claim_sum_current = [9.0, 0.0]`;
- `end_wealth_current = 83.0` nach einmaligem Abzug der gemeinsamen
  `information_cost = 4.0`;
- `end_wealth_sector_current = [87.0, 100.0]`, da der Altcode keine belastbare
  sektorale Verteilung der gemeinsamen Informationskosten vorgibt;
- keine neuen VN-Regel-, Schaden- oder Settlement-Anwendungen in Periode `6`;
- weitergetragener VN-Zustand in Periode `6` mit
  `chosen_insurer_sector_current = [12, None]`.

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
- keine Uebernahme weiterer historischer Referenzdateien;
- kein Vergleich gegen eine historische DAT-Vollausgabe.

## Offene Folgearbeit

Der naechste fachliche Anschluss sollte einen weiteren schmalen VU-/VN-Slice
mit eigenem belegtem Zwischenzustand waehlen. Naheliegend ist ein weiterer
expliziter VN-Regel-Snapshot oder ein enger Carryover-/Regelanschluss aus den
vorhandenen Planfixtures. Ein spaeterer Teilgleichheitsnachweis braucht
weiterhin eigene historische Referenzfenster und darf nicht aus diesem Test
allein abgeleitet werden.
