# Legacy-Ziele fuer VU-Agrsich-Replay

## Ziel

Der deterministische VU-Agrsich-Replay-Pfad kann nun mehrere Legacy-Ziele
vergleichen und optional Validierungsreports schreiben. Damit ist die VU-Seite
an denselben tabellenbasierten Validierungskorridor angeschlossen, den die VN-
und expliziten VU/VN-Pfade bereits nutzen.

## Ursprung im Altcode

Der fachliche Anschluss bleibt bei den historischen Agrsich-Ausgaben fuer VU-
und VN-Tabellen sowie den bereits portierten VU-Regelkernen. Dieser Slice
portiert keine neue Versichererentscheidung und keinen historischen Scheduler,
sondern erweitert den kontrollierten Vergleichspfad fuer erzeugte
Replay-Exports.

## Python-Abbildung

- `ReplayLegacyTarget` beschreibt Legacy-Datei, Exportdatei, Subjekttyp und
  Toleranz.
- `run_agrsich_replay_from_mapping` akzeptiert explizite `legacy_targets` und
  laedt zusaetzlich Fixture-Feld `legacy_targets`.
- Geschriebene Exporttabellen werden pro Dateiname zusammengefuehrt und mit den
  bestehenden Multi-Perioden-Komparatoren verglichen.
- `legacy_report_name` schreibt bei vorhandenem Vergleich die JSON-/CSV-
  Validierungsreports.
- `build_replay_fixture_from_period_plan` bewahrt `legacy_targets` und
  `legacy_report_name`; `run_agrsich_replay_from_period_plan_fixture` reicht den
  Reportnamen weiter.

## Annahmen und Grenzen

- `legacy_window` bleibt fuer bestehende VU-Fenster erhalten.
- Mehrzielige Legacy-Vergleiche pruefen die erzeugten Exporttabellen, behaupten
  aber keine historische Vollgleichheit.
- Periodenupdates, VU-Regel-Snapshots und Carryover bleiben explizite Eingaben.
