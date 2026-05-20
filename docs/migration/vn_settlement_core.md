# VN-Abrechnungskern aus Vrvn01 bis Vrvn03

Dieser Slice portiert den deterministischen Abrechnungsteil der historischen
Versicherungsnehmerregeln. Er verarbeitet explizite Entscheidungen und
Schadenrealisationen je Sparte und schreibt daraus VN- und VU-Snapshots fort.

## Ursprung im Altcode

- `IMS.E`, `act Vrvn01`
- `IMS.E`, `act Vrvn02`
- `IMS.E`, `act Vrvn03`

Die drei Regeln unterscheiden sich in der vorgeschalteten Wahl- und
Zufallslogik. Danach folgt ein weitgehend gleicher Abrechnungsblock:

- bei Fremdversicherung werden Reserven um Praemie erhoeht und um Schaden
  reduziert
- bei positivem Schaden werden Schadenanzahl und Schadensumme des Versicherers
  fortgeschrieben
- die Versichertenzahl des Versicherers steigt je versichertem Risiko
- beim VN werden Versicherer, Versicherungsstatus, gezahlte Praemie,
  Eigen-/Fremdschaden und kumuliertes Vermoegen geschrieben

## Python-Abbildung

Der neue Kern liegt in `python_port/ims/model/vn_rules.py`.
Der kleine Periodeneinstieg liegt in `python_port/ims/engine/vn_rule_runner.py`.

Wichtige Typen und Funktionen:

- `VNSectorSettlementDecision`
- `VNSettlementSnapshot`
- `VNSettlementResult`
- `VNSettlementApplication`
- `apply_vn_settlement_snapshot`
- `apply_vn_settlement_snapshots`
- `load_vn_settlement_snapshots_from_mapping`
- `run_vn_settlement_period`

Szenarien koennen optional `vn_settlement_snapshots` enthalten. Der
Szenario-Loader prueft dabei frueh:

- unbekannte VN-Ziele
- unbekannte VU-Referenzen in versicherten Entscheidungen
- doppelte VN-Ziele

## Annahmen und Grenzen

- Dieser Slice portiert nur die Abrechnung nach bereits getroffener Entscheidung.
- Versichererwahl, Praeferenzwahl, Pflichtversicherung, Schadenziehung und
  Aenderungsschocklogik bleiben bewusst ausserhalb dieses PRs.
- Praemien werden entweder explizit im Snapshot angegeben oder aus dem aktuellen
  VU-Sektor-Snapshot gelesen.
- Das historische `Vm` ist skalar. Die Python-Sektorvermoegen werden nur als
  explizite, reportingfreundliche Snapshot-Fortschreibung gefuehrt und nicht als
  historische Vollgleichheit behauptet.
- Keine Scheduler-Kopplung, keine Vollsimulation, keine automatische
  historische Regelauswahl.
