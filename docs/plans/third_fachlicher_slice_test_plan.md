# Plan: Dritter fachlicher VU-Carryover-Fixture-Slice

## Zweck

Dieser PR 31 legt den dritten schmalen fachlichen Regressionstest der
IMS-Migration fest. Nach dem VN-Carryover-Slice und dem
VN-`best_info`-Regel-Snapshot-Slice wird als naechster kleiner Fachlogik-
Schnitt ein VU-Carryover-Fixture gewaehlt.

Der Schnitt bleibt ein Plan-PR: Er fuehrt noch keinen neuen Regressionstest ein,
startet keine Simulation und behauptet keine historische Vollgleichheit.

## Auswahl

Gewaehlter Slice:

- VU-Carryover ueber explizite Mehrperioden-Fixture-Grenze;
- Versicherer `10`;
- lokale Perioden `2 -> 3`;
- `carry_forward_insurer_state = true`;
- erwarteter Carryover `insurer_ids = [10]`;
- erwartete weitergerollte Frmdinf-Basis `foreign_info.insurer.dp = [51.0, 52.0]`;
- erwartete Vrvu04-Nettowechslerbasis
  `policyholders_prev_sector = [30.0, 80.0]`.

Technische Anker:

- `python_port/ims/engine/vu_rule_runner.py::apply_vu_foreign_info_carryover`;
- `python_port/ims/engine/vu_rule_runner.py::run_vu_foreign_info_multi_period_from_mappings`;
- `tests/test_vu_rule_runner.py::test_vu_rule_multi_period_runner_can_carry_current_insurer_state_forward`;
- `tests/test_vu_rule_runner.py::test_vu_rule_multi_period_carryover_advances_net_switcher_previous_basis`;
- `docs/plans/vu_net_switcher_carryover_window_slice.md`;
- `docs/migration/vu_foreign_info_period_runner.md`.

Der spaetere Regressionstest soll den vorhandenen portierten Carryover-Pfad
gezielt absichern. Er darf keine neue VU-Regelentscheidung einfuehren und keine
automatische historische Regelwahl ableiten.

## Warum VU-Carryover jetzt

Die letzten beiden fachlichen Slices lagen auf VN-Seite. Ein VU-Carryover-
Fixture bringt Breite in den Kern, ohne die Ausfuehrungsgrenze zu vergroessern:
Der vorhandene Code rollt nur klar benannte Versichererzustandsfelder und die
Vrvu04-Nettowechslerbasis weiter. Damit bleibt der Schnitt enger als eine
breitere Run-Control- oder Simulation-Anbindung.

Ein weiterer VN-Regel-Snapshot bleibt moeglich, bringt aber weniger neue
Abdeckung, solange die VU-Perioden-/Carryover-Seite noch nicht als eigener
fachlicher Regressionstest eingeordnet ist.

## Erwarteter naechster PR

PR 32 soll den geplanten Slice als eigenen Regressionstest umsetzen:

- neues explizites Zwei-Perioden-Fixture oder testlokales Fixture fuer
  Versicherer `10`;
- Erwartung `carryovers[0].insurer_ids = [10]`;
- Erwartung `foreign_info.insurer.dp = [51.0, 52.0]` in der zweiten Periode;
- Erwartung `policyholders_prev_sector = [30.0, 80.0]`;
- optionaler Vrvu04-Grenztest mit Nettowechslerwerten `net_switcher_values =
  [0.0, 0.0]`;
- Dokumentation der Grenzen in `docs/migration/`.

## Grenzen

- keine Simulation;
- kein Scheduler-Start;
- kein API-/UI-/Run-Control-Startpfad;
- keine neue Fachregel;
- keine automatische historische Regelwahl;
- keine Uebernahme weiterer historischer Referenzdateien;
- kein Vergleich gegen eine historische DAT-Vollausgabe;
- keine historische Vollgleichheitsbehauptung.

## Folgeplanung

- PR 32: geplanten VU-Carryover-Fixture-Slice als dritten fachlichen
  Regressionstest umsetzen und dokumentieren.
- PR 33: danach entscheiden, ob ein weiterer VN-/VU-Regel-Snapshot oder ein
  schmaler Ausfuehrungsadapterplan fachlich sinnvoller ist.
- PR 34+: Run-Control- oder Ausfuehrungsadapterplaene erst nach separater
  fachlicher Freigabe; weiterhin ohne Vollgleichheitsbehauptung.

## Validierung dieses Plan-PRs

Dieser Plan wird nur ueber Dokumentationstests validiert. Die fachliche
Ausfuehrung des Slices folgt in einem separaten PR.
