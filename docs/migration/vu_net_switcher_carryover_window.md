# Vrvu04-Carryover-Periodenfenster

## Ziel

Dieser Slice korrigiert die kontrollierte Fortschreibung der Vrvu04-Basis im
VU-Mehrperiodenrunner. Wenn `carry_forward_insurer_state=True` aktiv ist, wird
die zweite Vorperiodenbasis fuer Nettowechsler nun aus den zuletzt bekannten
aktuellen Versicherungsnehmerzahlen gebildet.

## Ursprung im Altcode

- `IMS.E`, `act Vrvu04`
- Kommentar: `Verhaltensregel: Mark-Up II`
- Kernformel: Nettowechsler je Sparte als `Vn(t-1) - Vn(t-2)`

## Python-Abbildung

- `python_port/ims/engine/vu_rule_runner.py`
  - `apply_vu_foreign_info_carryover` setzt `policyholders_prev_sector` aus
    `previous.policyholders_current_sector`.
  - Falls der sektorisierte aktuelle Zaehler fehlt, wird
    `previous.policyholders_current` als konservativer Skalar-Fallback auf beide
    Sparten gespiegelt.

Damit verschiebt der Carryover das Zwei-Perioden-Fenster fuer Vrvu04 in die
Folgeperiode. Snapshots mit explizitem `previous_policyholders_sector` bleiben
weiterhin ein Override fuer gezielte Referenz- und Regressionstests.

## Validierung

- Mehrperioden-Test fuer sektorisierten Carryover: unveraenderte aktuelle
  Versicherungsnehmerzahlen erzeugen in der Folgeperiode `0.0` Nettowechsler.
- Mehrperioden-Test fuer Skalar-Fallback: fehlende sektorisierte aktuelle
  Zaehler werden aus `policyholders_current` gespiegelt.

## Grenzen

- Keine automatische historische VU-Regelwahl.
- Keine Vollsimulation.
- Keine Aussage ueber historische Vollgleichheit.
