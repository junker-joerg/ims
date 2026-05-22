# Slice-Plan: VN-Regeldispatch im expliziten Periodenplan

## Ziel

Der explizite VU/VN-Periodenplan soll die portierten VN-Versicherungsregel-
Snapshots aus `Vrvn01` bis `Vrvn06` direkt durchreichen koennen. Der kombinierte
Runner soll diese Anwendungen separat diagnostizieren.

## Umsetzung

- `vn_insurance_rule_snapshots` in die unterstuetzten Periodenplan-Snapshotlisten
  aufnehmen
- `ExplicitMultiPeriodRunResult` um
  `total_vn_insurance_rule_applications` erweitern
- Tests fuer Plan-Fixture-Aufbau, Plan-Ausfuehrung und kombinierten Runner
  ergaenzen

## Grenzen

- Keine automatische Kopplung von Versicherungsentscheidungen an Schaden- oder
  Abrechnungssnapshots
- Keine historische Scheduler-Regelwahl
- Keine Vollsimulation und keine Behauptung historischer Vollgleichheit
