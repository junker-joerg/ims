# VN-Versicherungsregel-Dispatch

Dieser Slice verbindet die portierten VN-Versicherungsregelkerne `Vrvn01` bis
`Vrvn06` ueber explizite Snapshots mit dem bestehenden VN-Periodenrunner. Der
Dispatch erzeugt `VNInsuranceDecision`-Listen und Diagnosen, fuehrt aber noch
keine automatische Schaden- oder Abrechnungsanwendung aus.

## Ursprung im Altcode

- `IMS.E`, `act Vrvn01` bis `act Vrvn06`
- Historisch waehlt der Scheduler je VN eine Verhaltensregel und fuehrt danach
  Schadenserzeugung und Abrechnung im selben `act`-Block aus.

Im Python-Port bleiben diese Bestandteile weiterhin getrennt:

- Versicherungsentscheidung: `python_port/ims/model/vn_insurance_rules.py`
- Schadenerzeugung und Abrechnung: `python_port/ims/model/vn_rules.py`
- expliziter Periodenlauf: `python_port/ims/engine/vn_rule_runner.py`

## Python-Abbildung

Neue zentrale Typen:

- `VNInsuranceRuleKind`
- `VNInsuranceRuleSnapshot`
- `VNInsuranceRuleApplication`

Neue zentrale Funktionen:

- `vn_insurance_rule_snapshot_from_mapping`
- `load_vn_insurance_rule_snapshots_from_mapping`
- `apply_vn_insurance_rule_snapshot`
- `apply_vn_insurance_rule_snapshots`

Der Scenario-Loader akzeptiert nun optional `vn_insurance_rule_snapshots`.
Der VN-Periodenrunner wendet diese Snapshots an und gibt die Anwendungen in
`VNSettlementPeriodRunResult.insurance_rule_applications` aus. Mehrperiodige
Laeufe zaehlen diese Anwendungen ueber
`VNSettlementMultiPeriodRunResult.total_insurance_rule_applications`.

## Unterstuetzte Regelarten

- `compulsory`: Vrvn01 / Pflichtversicherung
- `random`: Vrvn02 / Zufallsversicherung
- `preference`: Vrvn03 / Praeferenzwahl
- `search_history`: Vrvn04 / Suche nach frueherer VN-Praemie
- `sample_search`: Vrvn05 / Stichprobensuche nach aktueller VU-Praemie
- `best_info`: Vrvn06 / beste Information ueber aktive aktuelle VU-Praemien

In Periode 1 verwendet der Dispatch fuer alle Regelarten explizite
`initial_decisions`. Fuer Vrvn02 ist das bewusst der Startperiodenpfad, da der
portierte Zufallsregel-Kern nur die Perioden nach der Startperiode abbildet.

## Validierung

Die Tests decken ab:

- Dispatch gemischter Regel-Snapshots
- Startperioden-Dispatch ueber explizite Initialentscheidungen
- kontrollierte Fehler fuer unvollstaendige Snapshots
- Scenario-Loader-Referenzvalidierung fuer unbekannte VN
- Scenario-Loader-Referenzvalidierung fuer unbekannte VU in
  `active_insurer_ids`, `initial_decisions`, `insurer_inputs` und
  Suchhistorien
- Anwendung und Zaehlen der Dispatch-Ergebnisse im VN-Periodenrunner

## Grenzen

- Der Dispatch erzeugt Entscheidungen, bucht sie aber nicht automatisch in
  `vn_damage_settlement_snapshots` ein.
- Informationskosten aus Vrvn05/Vrvn06 bleiben diagnostisch und werden noch
  nicht automatisch im Settlement-Vermoegenspfad verrechnet.
- Keine automatische historische Scheduler- oder Regelwahl.
- Keine Vollsimulation und keine Behauptung historischer Vollgleichheit.
