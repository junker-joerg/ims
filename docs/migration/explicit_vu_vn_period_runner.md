# Expliziter VU/VN-Periodenrunner

## Ziel

Der explizite VU/VN-Periodenrunner fuehrt die bereits portierten VU-Regeln und
VN-Schaden-/Abrechnungsschritte in einem gemeinsamen geladenen Szenario aus.
Damit koennen kontrollierte Fachlogik-Slices abbilden, dass VU-Entscheidungen
innerhalb einer Periode vor der VN-Abrechnung auf die aktuellen Versichererwerte
wirken.

## Ursprung im Altcode

Der fachliche Anschluss liegt bei den VU-Regelwirkungen aus den portierten
`Vrvu*`-Slices und den VN-Periodenwirkungen aus `Vrvn01` bis `Vrvn03`. Dieser
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
- Optionale Flags `carry_forward_vu_state` und `carry_forward_vn_state` aktivieren
  die bereits vorhandenen kontrollierten Carryover-Bausteine.
- `ExplicitPeriodCarryover` weist lokale und globale Quell-/Zielperioden aus,
  damit Plaene mit `run_index * max_periods + period` dieselbe Zeitachse wie
  die VU- und Agrsich-Runner diagnostizieren.

## Annahmen und Grenzen

- Alle VU-Regelparameter, Schadenziehungen und VN-Versicherungsentscheidungen
  muessen als explizite Snapshots im Szenario vorliegen.
- Bei gleichzeitig aktiviertem VU- und VN-Carryover werden beide bestehenden
  Carryover-Bausteine ausgefuehrt; der VN-Carryover enthaelt dabei auch
  Versicherer-Aktuellwerte nach der VN-Abrechnung.
- Der Runner ist kein Ersatz fuer einen historischen PlanVN-/PlanVU-Scheduler.
- Die globale Carryover-Diagnose fuehrt keine neue Fortschreibungslogik ein,
  sondern beschreibt nur den bereits validierten Zustandstransfer eindeutiger.
