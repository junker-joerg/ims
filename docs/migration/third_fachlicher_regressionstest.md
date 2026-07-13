# Dritter fachlicher Regressionstest

## Zweck

Dieser Stand setzt den unter
`docs/plans/third_fachlicher_slice_test_plan.md` geplanten dritten fachlichen
Regressionstest um. Der Slice prueft einen kontrollierten VU-Carryover ueber
ein explizites Zwei-Perioden-Fixture und bleibt bewusst kleiner als ein
historischer Modellvergleich.

## Test-Schnitt

| Bereich | Wert |
| --- | --- |
| Test | `tests/test_third_fachlicher_vu_carryover_regression.py` |
| Kontrollpfad | `run_vu_foreign_info_multi_period_from_mappings` |
| Portierter Baustein | `apply_vu_foreign_info_carryover` |
| Versicherer | `10` |
| Uebergang | lokale Perioden `2 -> 3` |
| Globale Perioden | `14 -> 15` |

Der Test nutzt ausschliesslich explizite Fixture-Zustaende und den vorhandenen
VU-Mehrperiodenpfad mit `carry_forward_insurer_state=True`. Er startet keinen
Scheduler, keine Simulation, keinen HTTP-Endpunkt, keine Workbench-UI und keinen
Run-Control-Pfad.

## Gepruefte fachliche Signale

Der Regressionstest prueft:

- `carryovers[0].insurer_ids = [10]`;
- `from_period = 2`;
- `to_period = 3`;
- `from_global_period = 14`;
- `to_global_period = 15`;
- `foreign_info.insurer.dp = [51.0, 52.0]`;
- `foreign_info.insurer.dw = [4.0, 8.0]`;
- `foreign_info.insurer.mp = [51.0, 52.0]`;
- `premiums_current_sector = [26.5, 15.0]`;
- `advertising_current_sector = [3.4, 5.6]`;
- `reserves_current = [55.125, 66.15]`;
- `policyholders_current_sector = [30.0, 80.0]`;
- `policyholders_prev_sector = [30.0, 80.0]`;
- Vrvu04-Grenze `net_switcher_values = [0.0, 0.0]`, wenn die zweite Periode
  nur den Nettowechsler-Mark-Up-Snapshot nutzt.

## Grenzen

Der Test ist ein fachlicher Regressionstest fuer einen expliziten
Zwischenzustand. Er ist kein historischer Vollgleichheitsnachweis, kein Abgleich
eines kompletten IMS/ESS-Laufs und kein Nachweis fuer alle VU-Regeln.

Nicht enthalten:

- keine Simulation;
- kein Scheduler-Start;
- kein API-/UI-/Run-Control-Startpfad;
- keine neue Fachregel;
- keine automatische historische Regelwahl;
- keine Uebernahme weiterer historischer Referenzdateien;
- kein Vergleich gegen eine historische DAT-Vollausgabe.

## Offene Folgearbeit

Der naechste fachliche Anschluss sollte entscheiden, ob ein weiterer
VU-/VN-Regel-Snapshot mehr Fachbreite bringt oder ob zuerst ein schmaler
Ausfuehrungsadapterplan vorbereitet werden soll. Ein spaeterer
Teilgleichheitsnachweis braucht weiterhin eigene historische Referenzfenster
und darf nicht aus diesem Test allein abgeleitet werden.
