# VN-Agrsich-Periodenplan

## Ziel

Der VN-Agrsich-Periodenplan macht wiederholbare VN-Replay-Laeufe aus einem
gemeinsamen Basissnapshot plus expliziten Periodenupdates moeglich. Damit koennen
kleine fachliche Mehrperioden-Slices fuer VN-Schaden, VN-Abrechnung und optionalen
VN-State-Carryover ohne duplizierte Vollsnapshots beschrieben werden.

## Ursprung im Altcode

Der fachliche Anschluss liegt bei den VN-Periodenwirkungen aus `Vrvn01` bis
`Vrvn06` sowie bei den historischen Agrsich-Ausgaben `IMSVNR*.DAT` und
`IMSVU*.DAT`. Dieser Slice portiert keinen historischen Scheduler, sondern
strukturiert explizite Python-Snapshots fuer den bereits portierten VN-Replay-Pfad.

## Python-Abbildung

- `VNAgrsichReplayPlan` beschreibt Metadaten, Startzustand, Carryover-Flag und
  Periodenupdates. Optional koennen `legacy_targets` und `legacy_report_name`
  gesetzt werden.
- `VNAgrsichReplayPeriodUpdate` beschreibt Periode, optionale
  `logtime`-/`max_periods`-Overrides, Laufindex, RNG-Seed, Entitaetsupdates und
  optionale VN-Snapshotlisten.
- Periodenupdates koennen `vn_insurance_rule_snapshots` enthalten. Diese werden
  in das erzeugte Replay-Fixture durchgereicht und koennen fehlende
  `insurance_decisions` passender Schaden-Abrechnungs-Snapshots speisen.
- `build_vn_agrsich_replay_fixture_from_period_plan` erzeugt daraus das bestehende
  VN-Agrsich-Replay-Fixture mit `periods`.
- `run_vn_agrsich_replay_from_period_plan_fixture` fuehrt den erzeugten
  Periodenlauf mit dem bestehenden VN-Agrsich-Runner aus. Relative
  Legacy-Pfade werden am Plan-Fixture-Verzeichnis aufgeloest und an den Runner
  weitergereicht.

## Annahmen und Grenzen

- Alle VN-Versicherungsregel-, Schadens- und Abrechnungsinformationen liegen
  weiterhin explizit im Plan oder im Basissnapshot vor.
- Das `carry_forward_vn_state`-Flag muss ein Boolean sein.
- Fehlen `logtime` oder `max_periods` im Periodenupdate, bleibt der
  Basissnapshot massgeblich.
- Entitaetsupdates duerfen nur vorhandene `entity_id`-Werte des Basissnapshots
  ueberschreiben.
- Legacy-Zielvergleiche und Validierungsreports bleiben im bestehenden
  VN-Agrsich-Replay-Pfad verdrahtet; der Periodenplan reicht die Angaben nur
  kontrolliert durch.
