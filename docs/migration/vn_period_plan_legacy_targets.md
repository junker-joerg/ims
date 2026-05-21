# Legacy-Ziele im VN-Agrsich-Periodenplan

## Ziel

Der VN-Agrsich-Periodenplan kann nun dieselben Legacy-Ziele und
Validierungsreports nutzen wie der darunterliegende VN-Agrsich-Replay-Runner.
Damit lassen sich explizite VN-Periodenplaene direkt gegen historische
`IMSVNR*`- oder `IMSVU*`-Fenster pruefen, ohne vorher ein separates
Mehrperioden-Fixture auszuschreiben.

## Ursprung im Altcode

Der fachliche Anschluss bleibt bei den VN-Periodenwirkungen aus `Vrvn01` bis
`Vrvn03` und den historischen Agrsich-Ausgaben. Dieser Schritt fuegt keine neue
VN-Entscheidungs- oder Schedulerlogik hinzu, sondern reicht vorhandene
Validierungsziele in den bereits portierten VN-Agrsich-Replay-Pfad durch.

## Python-Abbildung

- `VNAgrsichReplayPlan` liest optionale `legacy_targets` und
  `legacy_report_name`.
- `build_vn_agrsich_replay_fixture_from_period_plan` bewahrt diese Angaben im
  erzeugten Replay-Fixture.
- `run_vn_agrsich_replay_from_period_plan_fixture` loest relative
  `legacy_path`-Werte relativ zum Plan-Fixture und uebergibt typisierte
  `VNAgrsichLegacyTarget`-Objekte an den Runner.
- Wenn ein Reportname gesetzt ist, schreibt der bestehende Runner die
  JSON-/CSV-Validierungsreports.

## Annahmen und Grenzen

- Periodenentscheidungen, Schadenziehungen und Versicherungsentscheidungen
  bleiben explizite Eingaben.
- Der Slice behauptet keine historische Vollgleichheit.
- Die Vollstaendigkeit der Legacy-Perioden wird vom bestehenden
  VN-Agrsich-Replay-Vergleich geprueft.
