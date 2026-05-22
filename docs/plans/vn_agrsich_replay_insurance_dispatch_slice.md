# Slice-Plan: VN-Regeldispatch im Agrsich-Replay

## Ziel

Der VN-Agrsich-Replay-Pfad soll die portierten VN-Versicherungsregel-Snapshots
aus `Vrvn01` bis `Vrvn06` diagnostizieren und im Periodenplan durchreichen
koennen.

## Umsetzung

- `VNAgrsichReplayRunResult` um `total_insurance_rule_applications` erweitern
- VN-Agrsich-Replay-Test fuer Schaden-Abrechnung aus VN-Regeldispatch ergaenzen
- VN-Agrsich-Periodenplan um `vn_insurance_rule_snapshots` erweitern
- Periodenplan-Tests auf den neuen Dispatch-zu-Schaden-Pfad ausrichten

## Grenzen

- Keine historische Scheduler- oder Regelwahl
- Keine automatische Erzeugung von Schadensnapshots ohne explizite Parameter und
  Schwellen
- Keine Vollsimulation und keine Behauptung historischer Vollgleichheit
