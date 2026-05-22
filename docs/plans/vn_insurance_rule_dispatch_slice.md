# Slice-Plan: VN-Versicherungsregel-Dispatch

## Ziel

Explizite Snapshots fuer die portierten VN-Versicherungsregelkerne `Vrvn01` bis
`Vrvn06` laden, anwenden und im VN-Periodenrunner diagnostisch ausgeben.

## Nicht-Ziele

- keine automatische Scheduler-Regelwahl
- keine automatische Kopplung an Schaden- und Abrechnungssnapshots
- keine Vollsimulation
- keine historische RNG-Gleichheitsbehauptung

## Umsetzung

- `VNInsuranceRuleKind`, `VNInsuranceRuleSnapshot` und
  `VNInsuranceRuleApplication` ergaenzen
- Mapping-Loader fuer Dispatch-Snapshots ergaenzen
- Dispatch-Funktion fuer alle portierten VN-Versicherungsregeln ergaenzen
- Scenario-Loader um `vn_insurance_rule_snapshots` erweitern
- VN-Periodenrunner um `insurance_rule_applications` und mehrperiodige
  Zaehldiagnose erweitern

## Validierung

- Unit-Tests fuer Dispatch und Loader
- Runner-Test fuer explizite Versicherungsregel-Snapshots
- Runner-Test fuer mehrperiodige Zaehldiagnose
- voller Pytest-Lauf vor PR und nach Merge
