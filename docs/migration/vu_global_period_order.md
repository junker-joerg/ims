# Globale Periodenfolge im VU-Mehrperiodenrunner

## Ziel

Der explizite VU-Mehrperiodenrunner nutzt fuer Periodenvalidierung,
Periodenergebnis und Carryover-Diagnose nun dieselbe globale Periodenlogik
wie Agrsich-Replay und explizite VU/VN-Laeufe:

`global_period = run_index * max_periods + period`

wenn `max_periods > 0`; andernfalls bleibt `period` die globale Periode.

## Ursprung im Altcode

Der Anschluss liegt bei der periodischen Fortschreibung der bereits portierten
VU-Regelkerne `Vrvu01` bis `Vrvu10` und der Agrsich-Auswertung. Dieser Slice
portiert keinen historischen Scheduler, sondern vereinheitlicht die belegte
Zeitachse der kontrollierten Python-Mehrperiodenlaeufe.

## Python-Abbildung

- `VUForeignInfoPeriodRunResult` enthaelt neben `context_period` nun
  `context_global_period`.
- `VUForeignInfoCarryover` dokumentiert lokale und globale Quell-/Zielperioden.
- `run_vu_foreign_info_multi_period_from_mappings` validiert strikt steigende
  globale Perioden; `processed_periods` und `processed_local_periods` bleiben
  lokale Periodenindizes, `processed_global_periods` enthaelt die validierte
  globale Reihenfolge.

## Annahmen und Grenzen

- Lokale Perioden bleiben in `context_period` und den Aggregat-Snapshots
  sichtbar.
- Die Aenderung fuehrt keine neue VU-Regelentscheidung ein.
- Keine Vollsimulation und keine Behauptung historischer Vollgleichheit.
