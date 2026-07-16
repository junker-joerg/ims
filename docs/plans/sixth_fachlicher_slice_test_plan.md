# Plan: Sechster fachlicher Slice-Test

## Ziel

PR 50 waehlt den sechsten fachlichen Regressionstest nach den bereits
umgesetzten VN-`best_info`-, VN-`sample_search`- und Carryover-Slices. Der
naechste kleine Fachschnitt soll die VN-Suchversicherungsregel
`search_history` / Vrvn04 ueber explizite Snapshots pruefen.

Dieser PR plant den Test nur. Die Umsetzung des Tests folgt separat in PR 51.

## Ursprung und bestehende Bausteine

- Historischer Bezug: `IMS.E`, `act Vrvn04` als Suchversicherungsregel.
- Python-Regelkern:
  `python_port/ims/model/vn_insurance_rules.py::apply_vn_search_insurance_rule`.
- Snapshot-/Dispatch-Pfad:
  `load_vn_insurance_rule_snapshots_from_mapping` und
  `apply_vn_insurance_rule_snapshots`.
- Runner-Grenze:
  `python_port/ims/engine/vn_rule_runner.py::run_vn_settlement_period_from_mapping`.
- Bestehende Unit-Abdeckung:
  `tests/test_vn_insurance_rules.py::test_vn_search_insurance_decisions_feed_damage_settlement_path`.

## Gewaehlter Regressionstest fuer PR 51

Der geplante Test soll analog zum fuenften fachlichen Slice aufgebaut werden:

- Testdatei:
  `tests/test_sixth_fachlicher_vn_search_history_regression.py`;
- Regelart: `search_history`;
- Policyholder: `21`;
- Versicherer: `11` und `12`;
- Periode: `5`;
- Kontrollpfad 1: `apply_vn_insurance_rule_snapshots`;
- Kontrollpfad 2: `run_vn_settlement_period_from_mapping`;
- Historie:
  - Sparte 0: fruehere versicherte Entscheidung bei Versicherer `12` mit
    Praemie `4.0`;
  - Sparte 1: fruehere versicherte Entscheidung bei Versicherer `11` mit
    Praemie `5.0`;
- Erwartete Entscheidung:
  - `chosen_insurer_ids = [12, None]`;
  - `selected_insurer_ids = [12, 11]`;
  - `selected_history_periods` belegt die verwendeten Historienperioden;
  - keine Fallback-Ziehung fuer den normalen Suchpfad;
  - Schaden-/Settlement-Grenze mit `damages = [9.0, 0.0]`,
    `paid_premium_current = [4.0, 0.0]` und `end_wealth_current = 87.0`.

## Warum dieser Slice

Vrvn04 ist der konservativste Anschluss nach Vrvn05:

- Der Regelkern ist bereits portiert und unit-getestet.
- Die erwarteten Fachsignale sind aus vorhandenen Tests ableitbar.
- Der Slice nutzt explizite Historieneintraege statt historischer
  Scheduler-Rekonstruktion.
- Er erweitert die VN-Regelbreite, ohne neue Fachlogik oder neue Altdaten zu
  uebernehmen.

## Grenzen

- Keine Simulation.
- Kein Scheduler-Start.
- Kein API-/UI-/Run-Control-Startpfad.
- Keine neue Fachregel.
- Keine automatische historische Regelwahl.
- Keine Uebernahme weiterer historischer Referenzdateien.
- Kein Vergleich gegen eine historische DAT-Vollausgabe.
- Keine historische Vollgleichheitsbehauptung.

## Produktionsreife-Bezug

Dieser Slice ist ein Baustein der Produktionsreife-Roadmap in
`docs/plans/production_readiness_pr_plan.md`: Er verbreitert die fachliche
VN-Regelabdeckung, ersetzt aber keinen Altdaten-Gesamtvergleich und keinen
Abschlussbericht.
