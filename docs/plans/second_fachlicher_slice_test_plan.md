# Plan: Zweiter fachlicher VN-Regel-Snapshot-Slice

## Zweck

Dieser PR 29 legt den zweiten schmalen fachlichen Regressionstest der
IMS-Migration fest. Nach dem VN-Carryover-Slice wird als naechster kleiner
Fachlogik-Schnitt eine VN-Regelwirkung ueber explizite Snapshots gewaehlt.

Der urspruengliche Schnitt war ein Plan-PR: Er fuehrte noch keinen neuen
Regressionstest ein, startete keinen Runner und behauptete keine historische
Vollgleichheit. PR 30 setzt diesen Plan als gezielten Regressionstest um.

## Auswahl

Gewaehlter Slice:

- VN-Versicherungsregelwirkung ueber explizite Snapshots;
- Regelart `best_info`;
- Policyholder `21`;
- aktive Versicherer `11` und `12`;
- Periode `5`;
- erwartete Versicherungsentscheidung `[12, None]`;
- erwartete Informationskosten `information_cost = 4.0`.

Technische Anker:

- `python_port/ims/model/vn_insurance_rules.py::apply_vn_insurance_rule_snapshots`;
- `python_port/ims/engine/vn_rule_runner.py::run_vn_settlement_period_from_mapping`;
- `tests/test_vn_insurance_rules.py::test_vn_insurance_rule_dispatch_applies_mixed_rule_snapshots`;
- `tests/test_vn_rule_runner.py::test_vn_rule_runner_applies_explicit_insurance_rule_snapshots`.

Der spaetere Regressionstest soll zuerst die reine
`apply_vn_insurance_rule_snapshots`-Wirkung absichern. Eine Runner-Grenze kann
zusaetzlich pruefen, dass `run_vn_settlement_period_from_mapping` dieselbe
Snapshot-Entscheidung in den Periodenlauf uebernimmt. Beide Pfade sind bereits
portierte Bausteine; es wird keine neue Fachregel eingefuehrt.

## Warum nicht VU-Carryover in diesem Schnitt

VU-Carryover bleibt fachlich naheliegend, ist fuer diesen PR aber weniger
schmal. Die aktuell versionierten VU-Planfixtures belegen vor allem
Periodenuebergaenge und Legacy-Zielbezug; ein belastbarer VU-Carryover-
Regressionstest braucht ein eigenes, explizit dokumentiertes Fixture oder einen
separat eingeordneten Test-local Plan. Damit bleibt VU-Carryover ein spaeterer
eigener Slice.

Die VN-Regelwirkung ueber explizite Snapshots ist dagegen schon als
portierter, deterministischer Pfad vorhanden und kann ohne neue historische
DAT-Behauptung getestet werden.

## Umsetzung in PR 30

PR 30 setzt den geplanten Slice als eigenen Regressionstest um:

- `tests/test_second_fachlicher_vn_rule_snapshot_regression.py`;
- expliziter `best_info`-Snapshot fuer Policyholder `21`;
- Erwartung `chosen_insurer_ids = [12, None]`;
- Erwartung `information_cost = 4.0`;
- Runner-Grenztest, der die Snapshot-Entscheidung ueber
  `run_vn_settlement_period_from_mapping` nachweist;
- Dokumentation der Grenzen in
  `docs/migration/second_fachlicher_regressionstest.md`.

## Grenzen

- keine Simulation;
- kein Scheduler-Start;
- kein API-/UI-/Run-Control-Startpfad;
- keine neue Fachregel;
- keine automatische historische Regelwahl;
- keine Uebernahme weiterer historischer Referenzdateien;
- keine historische Vollgleichheitsbehauptung;
- keine Behauptung, dass dieser Slice alle VN-Regeln oder das historische
  Gesamtmodell abdeckt.

## Folgeplanung

- PR 30: geplanten `best_info`-VN-Regel-Snapshot-Slice als Regressionstest
  umsetzen und dokumentieren (erledigt).
- PR 31: optional weiteren VN-Regel-Snapshot oder VU-Carryover-Fixture planen,
  falls der Review mehr Breite vor einer Run-Control-Planung verlangt.
- PR 32+: spaetere Run-Control- oder Ausfuehrungsadapterplaene erst nach
  separater fachlicher Freigabe; weiterhin ohne Vollgleichheitsbehauptung.

## Validierung dieses Plan-PRs

Der urspruengliche Plan-PR wurde nur ueber Dokumentationstests validiert. PR 30
validiert die fachliche Ausfuehrung zusaetzlich ueber
`tests/test_second_fachlicher_vn_rule_snapshot_regression.py`.
