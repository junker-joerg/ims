# Expliziter VU/VN-Periodenrunner

## Ziel

Der explizite VU/VN-Periodenrunner fuehrt die bereits portierten VU-Regeln und
VN-Schaden-/Abrechnungsschritte in einem gemeinsamen geladenen Szenario aus.
Damit koennen kontrollierte Fachlogik-Slices abbilden, dass VU-Entscheidungen
innerhalb einer Periode vor der VN-Abrechnung auf die aktuellen Versichererwerte
wirken.

## Ursprung im Altcode

Der fachliche Anschluss liegt bei den VU-Regelwirkungen aus den portierten
`Vrvu*`-Slices und den VN-Periodenwirkungen aus `Vrvn01` bis `Vrvn06`. Dieser
Slice bildet nur die explizite Reihenfolge der bereits migrierten Kernlogik ab;
historische Scheduling-, Dialog- und Auswahlpfade bleiben ausserhalb.

## Python-Abbildung

- `ExplicitPeriodRunResult` fasst VU-Ergebnis, VN-Ergebnis und optionale
  Agrsich-Tabellen einer Periode zusammen.
- `run_loaded_explicit_period` wendet im geladenen Szenario zuerst
  `run_loaded_vu_foreign_info_period` und danach `run_loaded_vn_settlement_period`
  an.
- `run_explicit_multi_period_from_mappings` fuehrt mehrere explizite Perioden mit
  strikt steigender Periodenfolge aus.
- Das Mehrperiodenergebnis weist die lokale und globale Periodenfolge getrennt
  aus: `processed_local_periods` enthaelt `context.period`,
  `processed_global_periods` enthaelt die validierte globale Zeitachse.
- Optionale Flags `carry_forward_vu_state` und `carry_forward_vn_state` aktivieren
  die bereits vorhandenen kontrollierten Carryover-Bausteine.
- Das Mehrperiodenergebnis zaehlt VN-Versicherungsregelanwendungen separat als
  `total_vn_insurance_rule_applications`.
- `build_explicit_multi_period_execution_summary` erzeugt eine stabile
  maschinenlesbare Zusammenfassung eines ausgefuehrten expliziten
  Mehrperiodenlaufs. Sie berichtet lokale und globale Periodenachsen,
  VU-/VN-Anwendungszaehlungen, Carryover-Zaehler, Legacy-Vergleichsstatus und
  Schreibstatus, fuehrt aber keine fachliche Nachberechnung aus.
- Schaden-/Abrechnungs-Snapshots duerfen ihre `insurance_decisions` aus einem
  passenden `vn_insurance_rule_snapshots`-Eintrag derselben VN ableiten. Damit
  kann der explizite VU/VN-Lauf die portierten VN-Versicherungsregeln direkt in
  die anschliessende VN-Schadenabrechnung einspeisen.
- `ExplicitPeriodCarryover` weist lokale und globale Quell-/Zielperioden aus,
  damit Plaene mit `run_index * max_periods + period` dieselbe Zeitachse wie
  die VU- und Agrsich-Runner diagnostizieren.

## Annahmen und Grenzen

- Alle VU-Regelparameter, VN-Versicherungsregel-Snapshots und Schadenziehungen
  muessen als explizite Snapshots im Szenario vorliegen. VN-
  Versicherungsentscheidungen koennen entweder direkt am Schaden-/Abrechnungs-
  Snapshot stehen oder aus einem passenden VN-Versicherungsregel-Snapshot der
  Periode stammen.
- Bei gleichzeitig aktiviertem VU- und VN-Carryover werden beide bestehenden
  Carryover-Bausteine ausgefuehrt; der VN-Carryover enthaelt dabei auch
  Versicherer-Aktuellwerte nach der VN-Abrechnung.
- Der Runner ist kein Ersatz fuer einen historischen PlanVN-/PlanVU-Scheduler.
- Die globale Carryover-Diagnose fuehrt keine neue Fortschreibungslogik ein,
  sondern beschreibt nur den bereits validierten Zustandstransfer eindeutiger.
- Die Execution-Summary dokumentiert explizit, dass keine automatische
  historische Regelwahl und keine Vollsimulation ausgefuehrt wurden.
