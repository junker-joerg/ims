# Plan: Vrvu04-Carryover-Periodenfenster

## Ziel

Der kontrollierte VU-Carryover soll die Vrvu04-/Mark-Up-II-Basis fuer
Nettowechsler periodisch weiterrollen. Bei Carryover wird die neue
`policyholders_prev_sector`-Basis aus den zuletzt bekannten aktuellen
Versicherungsnehmerzahlen gebildet.

## Ursprung

- `IMS.E`, `act Vrvu04`
- Nettowechsler je Sparte: `Vn(t-1) - Vn(t-2)`

## Umsetzung

- `apply_vu_foreign_info_carryover` setzt `policyholders_prev_sector` aus
  `previous.policyholders_current_sector`.
- Fehlt der sektorisierte aktuelle Zaehler, wird der skalare
  `previous.policyholders_current` auf beide Sparten gespiegelt.
- Tests sichern, dass Vrvu04 ohne explizite Snapshot-Basis nach Carryover keine
  wiederholten Nettowechsler aus einer alten Vorvorperiode berechnet.

## Grenzen

- Keine automatische historische VU-Regelwahl.
- Keine breitere Zustandsfortschreibung ausserhalb des bestehenden VU-Carryovers.
- Keine Aussage ueber historische Vollgleichheit.
