# Zehnter fachlicher Regressionstest: VU-Zufall-I mit Carryover

## Ziel

PR 55 verbreitert die VU-Regelabdeckung um einen schmalen, deterministischen
Mehrperiodenslice. Der Test bindet zwei explizite Draw-Vektoren fuer
`Vrvu01` / Zufall I und prueft getrennt, welche VU-Zustaende nur bei
explizitem Carryover-Opt-in in die Folgeperiode gelangen.

Der Schnitt fuegt keine Fachregel hinzu. Er fixiert das bereits portierte
Verhalten von `apply_vu_random_uniform_rule_snapshots` und
`apply_vu_foreign_info_carryover` im vorhandenen
`run_vu_foreign_info_multi_period_from_mappings`.

## Ursprung und Mapping

| Aspekt | Einordnung |
| --- | --- |
| Historischer Bezug | bestehendes Mapping zu `IMS.E`, `act Vrvu01` |
| Portierter Regelkern | `python_port/ims/model/vu_rules.py` |
| Expliziter Mehrperiodenpfad | `python_port/ims/engine/vu_rule_runner.py` |
| Regressionstest | `tests/test_tenth_fachlicher_vu_random_carryover_regression.py` |
| Versicherer | `10` |
| Lokale Perioden | `2 -> 3` |
| Globale Perioden | `14 -> 15` |

Die historische Herkunft ist aus den vorhandenen Mapping-Dokumenten
`vu_random_rule_kernels.md` und `vu_random_draw_basis.md` uebernommen. Dieser
PR behauptet nicht, eine im Repository nicht vorhandene vollstaendige
historische Quellbasis erneut gelesen zu haben.

## Belegte Zwischenzustaende

Der erste Snapshot verwendet
`random_draws = [0.1, 0.2, 0.3, 0.4]`. Daraus entstehen fuer Periode 2:

- `premiums_current_sector = [1.0, 4.0]`;
- `advertising_current_sector = [9.0, 16.0]`;
- `reserves_current = [52.5, 63.0]`.

Mit `carry_forward_insurer_state = true` werden diese Werte fuer Versicherer
`10` in die Vorperiodenbasis der Periode 3 geschrieben. Der zweite explizite
Snapshot verwendet unabhaengig davon
`random_draws = [0.5, 0.25, 0.75, 0.125]` und ergibt:

- `premiums_prev_sector = [1.0, 4.0]`;
- `advertising_prev_sector = [9.0, 16.0]`;
- `reserves_prev_sector = [52.5, 63.0]`;
- `premiums_current_sector = [5.0, 5.0]`;
- `advertising_current_sector = [22.5, 5.0]`;
- `reserves_current = [55.125, 66.15]`.

Der Kontrolltest laesst das Carryover-Opt-in weg. Dann bleibt
`carryovers = []`, die Fixture-Vorperiodenbasis der zweiten Periode bleibt
unveraendert und die Reserven enden bei `[52.5, 63.0]`.

## Draw- und Carryover-Grenze

- Beide Draw-Vektoren stehen explizit im Test; die unterschiedlichen
  `rng_seed`-Werte werden nicht zur historischen Draw-Herleitung verwendet.
- Der Python-RNG und insbesondere der historische IMS/ESS-RNG sind nicht
  Gegenstand dieses Tests.
- Carryover findet nur nach ausdruecklichem Opt-in statt und betrifft nur die
  bereits in `apply_vu_foreign_info_carryover` definierten VU-Zustandsfelder.
- Die VU-Regelart wird nicht automatisch aus historischen Daten gewaehlt.

## Validierung und Grenzen

Der Test ist ein Regressionstest fuer explizite Python-Snapshots. Er startet
keine Simulation, keinen Scheduler, keinen API-/UI-/Run-Control-Startpfad und
schreibt keine Ergebnisdateien. Die Parameter und Draws sind kontrollierte
Testwerte, keine aus einer historischen DAT-Datei abgeleitete Vollreferenz.

Damit ist dieser Slice kein historischer RNG-Nachweis und kein historischer
Vollgleichheitsnachweis. Offene Feld-, Scheduler- und RNG-Fragen werden in den
folgenden Altdaten-PRs nicht still aufgeloest.

## Naechster Schritt

PR 56 fixiert den Produktions-Altdatenkorpus: Er benennt gezielt, welche
historischen Referenzen fuer die erste Freigabe zaehlen und welche Kandidaten
weiter ausgeschlossen bleiben. `incomming/` bleibt dabei unversioniert und
wird nicht als Sammelimport behandelt.
