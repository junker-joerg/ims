# Expliziter VU/VN-Periodenplan

## Ziel

Der explizite VU/VN-Periodenplan erzeugt gemeinsame VU/VN-Periodenszenarien aus
einem Basissnapshot plus expliziten Periodenupdates. Er reduziert Duplikation in
kontrollierten Mehrperiodenlaeufen und nutzt den vorhandenen kombinierten
Periodenrunner.

## Ursprung im Altcode

Der fachliche Anschluss bleibt bei den bereits portierten VU-Regelwirkungen aus
den `Vrvu*`-Slices und den VN-Periodenwirkungen aus `Vrvn01` bis `Vrvn06`. Der
Plan beschreibt explizite Python-Eingaben fuer diese portierten Kernpfade; er
portiert keinen historischen PlanVU-/PlanVN-Scheduler.

## Python-Abbildung

- `ExplicitPeriodPlan` beschreibt Metadaten, Basissnapshot und Carryover-Flags.
- `ExplicitPeriodPlanUpdate` beschreibt Periode, optionale
  `logtime`-/`max_periods`-Overrides, Laufindex, RNG-Seed, Entity-Updates und
  explizite VU/VN-Snapshotlisten.
- Periodenupdates koennen nun auch `vn_insurance_rule_snapshots` enthalten; sie
  werden wie die anderen Snapshotlisten in das erzeugte Fixture durchgereicht.
- Fehlen `insurance_decisions` in einem VN-Schaden-/Abrechnungs-Snapshot, kann
  der kombinierte Runner die Entscheidungen aus einem passenden
  `vn_insurance_rule_snapshots`-Eintrag derselben Periode beziehen.
- `build_explicit_period_fixture_from_plan` erzeugt daraus das Objekt-Fixture
  mit `periods`.
- `python -m ims.engine.explicit_period_diagnostics <plan.json>` liest dieselbe
  Planstruktur als Diagnose. Die Ausgabe enthaelt Periodenfolge, globale
  Perioden, Snapshot-Familien, erwartete Regelanwendungsgrenzen und
  Legacy-Bezuege, fuehrt aber keinen Periodenrunner aus und schreibt keine
  Dateien.
- `run_explicit_multi_period_from_plan_fixture` fuehrt das erzeugte Fixture ueber
  den kombinierten expliziten VU/VN-Runner aus.
- Optional koennen `legacy_targets` und `legacy_report_name` gesetzt werden. Sie
  werden an den kombinierten Runner weitergereicht; relative Legacy-Pfade werden
  am Plan-Fixture-Verzeichnis aufgeloest.

## Annahmen und Grenzen

- Alle VU-Regelparameter, VN-Versicherungsregel-Snapshots und
  VN-Schadenziehungen muessen explizit im Plan oder im Basissnapshot vorliegen.
  VN-Versicherungsentscheidungen koennen direkt am Schaden-/Abrechnungs-
  Snapshot stehen oder aus einem passenden VN-Versicherungsregel-Snapshot
  stammen.
- Fehlen `logtime` oder `max_periods` im Periodenupdate, bleibt der
  Basissnapshot massgeblich.
- Carryover-Flags muessen JSON-Booleans sein.
- Entity-Updates duerfen nur vorhandene `entity_id`-Werte des Basissnapshots
  ueberschreiben.
- Der Plan trifft keine Aussage ueber historische Vollgleichheit.
