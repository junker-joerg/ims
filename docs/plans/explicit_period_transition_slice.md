# Plan: Expliziter Periodenuebergang aus vorhandenen Planfixtures

## Ziel

Dieser PR 16 waehlt den naechsten fachlichen Slice nach der read-only
Run-Control-Bruecke. Der Slice soll keinen neuen Lauf starten und keine neue
VU-/VN-Regel ableiten. Er kartiert zuerst, welche Zwischenzustaende beim
Uebergang zwischen den bereits vorhandenen expliziten Periodenfixtures sichtbar
gemacht werden duerfen.

Der naechste Code-PR darf danach eine kleine, rein lokale Diagnose fuer
Periodenuebergaenge vorbereiten. Sie soll zeigen:

- Quell- und Zielperiode je Uebergang;
- lokale und globale Periodenachse;
- beteiligte VU/VN-Subjektmengen;
- ob ein vorhandener Carryover-Schritt geplant, ausgefuehrt oder bewusst nicht
  aktiviert ist;
- welche Felder als explizite Eingabe aus dem Fixture kommen und welche Felder
  aus einem vorhandenen Carryover stammen.

## Belegbare Fixture-Grenze

Die ersten belegbaren Eingaben sind:

- `tests/fixtures/replay_vu14_period_plan.json`
  - Legacy-Fenster: `VU14L1.DAT`, globale Perioden `1` bis `4`;
  - ein Versicherer: `entity_id = 14`, `rule_id = 14`, `rule_class = 1`;
  - keine VN-Policyholder.
- `tests/fixtures/replay_vusk1_period_plan.json`
  - Legacy-Fenster: `VUSK1L4.DAT`, globale Perioden `101` bis `104`;
  - ein Versicherer: `entity_id = 77`, `rule_id = 7`, `rule_class = 4`;
  - keine VN-Policyholder.

Diese Fixtures enthalten explizite Periodenupdates. Sie sind keine historische
Vollsimulation und liefern noch keine automatisch abgeleiteten Regelwerte.

## Altcode- und Migrationsspur

`legacy_c/` enthaelt in diesem Stand keine lesbare historische C-Quelle ausser
dem Platzhalter `.gitkeep`. Deshalb behauptet dieser Plan keine neu gelesene
C-Funktion.

Die fachliche Spur laeuft ueber bereits dokumentierte Migrationsschnitte:

- `docs/migration/agrsich_replay_plan.md` fuer deterministische
  Agrsich-Periodenplaene aus Startzustand plus expliziten Updates;
- `docs/migration/explicit_vu_vn_period_runner.md` fuer die vorhandene
  Reihenfolge VU-Regeln vor VN-Abrechnung im expliziten Runner;
- `docs/migration/period_plan_context_overrides.md` fuer `period`,
  `run_index`, `max_periods`, `logtime` und globale Perioden;
- vorhandene VU-Spuren zu `Vrvu*`-Slices, die nur dann herangezogen werden,
  wenn ein spaeterer PR eine einzelne Regelwirkung explizit belegt.

## Kandidat fuer den naechsten Code-PR

Der bevorzugte naechste Code-Schnitt ist eine kleine
`explicit_period_transition_diagnostics`-Diagnose oder eine entsprechende
Erweiterung der bestehenden Periodendiagnose. Sie soll die vorhandenen
Planfixtures lesen, aber keinen Runner, Scheduler, HTTP-Pfad oder UI-Startpfad
aktivieren.

Erwartete Ausgabegrenze:

- `mode = "explicit_period_transition_diagnostics"`;
- `transition_count`;
- `from_period`, `to_period`, `from_global_period`, `to_global_period`;
- `insurer_ids`, `policyholder_ids`;
- `vu_carryover_planned`, `vn_carryover_planned`;
- `writes_performed = false`;
- `execution_performed = false`;
- `simulation_performed = false`;
- `automatic_historical_rule_selection_performed = false`.

## Nicht-Ziele

- keine neue Fachlogik;
- keine neue automatische historische Regelwahl;
- keine Simulation und kein Scheduler-Start;
- kein Runner-Start aus API, UI oder Overview;
- kein neuer HTTP-Schreibpfad;
- keine Uebernahme von `VU014PR1.DAT`;
- keine historische Vollgleichheitsbehauptung;
- keine Behauptung, dass fehlende `legacy_c/`-Quellen gelesen wurden.

## Risiken und offene Punkte

- Die aktuellen Planfixtures enthalten keine VN-Policyholder. VN-Carryover muss
  deshalb erst mit einem separaten Fixture belegt werden, bevor VN-Zustand als
  abgedeckt gilt.
- VU14 und VUSK1 sind kleine Agrsich-Fenster. Sie belegen Periodenachsen und
  Versichererzustand, aber keine Vollmodellgleichheit.
- Explizite Periodenupdates koennen historische Werte nachbilden, sind aber noch
  keine aus Altlogik berechneten Regelentscheidungen.
- Carryover darf nur vorhandene portierte Carryover-Bausteine beschreiben. Er
  darf keine fehlenden Regelwerte auffuellen.

## Testgrenze fuer den naechsten Code-PR

Der naechste Code-PR soll mindestens pruefen:

- beide vorhandenen Planfixtures werden als Diagnoseeingaben akzeptiert;
- globale Perioden `1..4` und `101..104` bleiben getrennt sichtbar;
- `policyholder_ids` bleibt fuer diese Fixtures leer;
- keine Diagnose setzt `execution_performed`, `writes_performed`,
  `simulation_performed` oder
  `automatic_historical_rule_selection_performed` auf `true`;
- fehlerhafte oder nicht strikt steigende Periodenuebergaenge werden abgelehnt;
- offene VN-Abdeckung wird dokumentiert statt still als erledigt markiert.
