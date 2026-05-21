# Plan: Globale Periodenfolge im VU-Runner

## Ziel

Dieser Slice richtet den expliziten VU-Mehrperiodenrunner an der bereits
verwendeten globalen Periodenlogik aus. Dadurch koennen Periodenplaene mit
`run_index` und `max_periods` denselben Zeitbegriff im VU-Runner, Agrsich-Replay
und expliziten VU/VN-Laeufen verwenden.

## Begrenzung

- Keine neue Regel- oder Schedulerlogik.
- Keine Aenderung der VU-Regelkerne.
- Keine Vollsimulation.

## Umsetzung

1. Globale Periode aus dem geladenen Kontext berechnen.
2. Mehrperiodenfolge anhand globaler Perioden validieren.
3. Lokale und globale Perioden in Carryover-Diagnosen ausweisen.
4. Tests fuer bestehende Mehrperiodenlaeufe und laufuebergreifende Perioden.

## Validierung

- Fokustests fuer `tests/test_vu_rule_runner.py`.
- Volltestlauf des Python-Ports.
