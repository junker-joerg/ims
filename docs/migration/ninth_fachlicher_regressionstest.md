# Neunter fachlicher Regressionstest

## Zweck

Dieser Stand setzt PR 54 als breiteren, aber weiterhin schmalen fachlichen
Regressionstest um. Der Slice prueft den gemeinsamen VN-Schaden-/Settlement-Pfad
fuer explizite Entscheidungen aus `Vrvn01` bis `Vrvn03`.

Der Test bleibt bewusst kleiner als ein historischer Modellvergleich: Er nutzt
keine neuen historischen Referenzdateien, startet keine Simulation und leitet
keine automatische historische Regelwahl ab.

## Test-Schnitt

| Bereich | Wert |
| --- | --- |
| Test | `tests/test_ninth_fachlicher_vn_damage_settlement_breadth.py` |
| Regelarten | `compulsory`, `random`, `preference` |
| Historischer Bezug | `IMS.E`, `act Vrvn01` bis `act Vrvn03` |
| Kontrollpfad | `run_vn_settlement_period_from_mapping` |
| Policyholder | `21`, `22`, `23` |
| Versicherer | `11` und `12` |
| Periode | `5` |

Der Test nutzt ausschliesslich explizite In-Memory-Snapshots. Die
`vn_damage_settlement_snapshots` enthalten keine eigenen
`insurance_decisions`; der Runner muss sie aus den drei
`vn_insurance_rule_snapshots` aufloesen.

## Gepruefte fachliche Signale

Der Regressionstest prueft:

- `rule_kind = [COMPULSORY, RANDOM, PREFERENCE]`;
- aufgeloeste Versichererentscheidungen `[[12, 11], [12, None], [12, None]]`;
- `total_damage_settlement_applications = 3`;
- `total_settlement_applications = 3`;
- Schaden-/Settlement-Grenze fuer Pflichtversicherung mit
  `damages = [9.0, 16.0]`, `paid_premium_current = [4.0, 5.0]` und
  `end_wealth_current = 66.0`;
- Sektorvermoegen aus `previous_wealth_sector = [120.0, 80.0]` mit
  `end_wealth_sector_current = [107.0, 59.0]`;
- Schaden-/Settlement-Grenze fuer `random` und `preference` jeweils mit
  `damages = [9.0, 0.0]` und `end_wealth_current = 87.0`;
- kumulierte Versichererfortschreibung:
  - Versicherer `11`: `reserves_current = [30.0, 39.0]`,
    `policyholders_current_sector = [0.0, 2.0]`,
    `claims_count_current = [0, 1]`,
    `claims_sum_current = [0.0, 16.0]`;
  - Versicherer `12`: `reserves_current = [25.0, 60.0]`,
    `policyholders_current_sector = [4.0, 2.0]`,
    `claims_count_current = [3, 0]`,
    `claims_sum_current = [27.0, 0.0]`.

## Grenzen

Der Test ist ein fachlicher Regressionstest fuer explizite Zwischenzustaende.
Er ist kein historischer Vollgleichheitsnachweis, kein Abgleich eines kompletten
IMS/ESS-Laufs und kein Nachweis fuer alle VN-Regeln.

Nicht enthalten:

- keine Simulation;
- kein Scheduler-Start;
- kein API-/UI-/Run-Control-Startpfad;
- keine neue Fachregel;
- keine automatische historische Regelwahl;
- keine Uebernahme weiterer historischer Referenzdateien;
- kein Vergleich gegen eine historische DAT-Vollausgabe.

## Offene Folgearbeit

Nach PR 54 ist der VN-Schaden-/Settlement-Pfad fuer `Vrvn01` bis `Vrvn03`
breiter gegen explizite Fixtures abgesichert. Der naechste geplante Fachschnitt
ist PR 55: VU-Regelbreite, vorzugsweise ein expliziter VU-Random- oder
VU-Markup-Slice mit Draw-/Carryover-Grenze.
