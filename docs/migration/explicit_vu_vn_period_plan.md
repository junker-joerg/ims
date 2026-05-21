# Expliziter VU/VN-Periodenplan

## Ziel

Der explizite VU/VN-Periodenplan erzeugt gemeinsame VU/VN-Periodenszenarien aus
einem Basissnapshot plus expliziten Periodenupdates. Er reduziert Duplikation in
kontrollierten Mehrperiodenlaeufen und nutzt den vorhandenen kombinierten
Periodenrunner.

## Ursprung im Altcode

Der fachliche Anschluss bleibt bei den bereits portierten VU-Regelwirkungen aus
den `Vrvu*`-Slices und den VN-Periodenwirkungen aus `Vrvn01` bis `Vrvn03`. Der
Plan beschreibt explizite Python-Eingaben fuer diese portierten Kernpfade; er
portiert keinen historischen PlanVU-/PlanVN-Scheduler.

## Python-Abbildung

- `ExplicitPeriodPlan` beschreibt Metadaten, Basissnapshot und Carryover-Flags.
- `ExplicitPeriodPlanUpdate` beschreibt Periode, optionale
  `logtime`-/`max_periods`-Overrides, Laufindex, RNG-Seed, Entity-Updates und
  explizite VU/VN-Snapshotlisten.
- `build_explicit_period_fixture_from_plan` erzeugt daraus das Objekt-Fixture
  mit `periods`.
- `run_explicit_multi_period_from_plan_fixture` fuehrt das erzeugte Fixture ueber
  den kombinierten expliziten VU/VN-Runner aus.
- Optional koennen `legacy_targets` und `legacy_report_name` gesetzt werden. Sie
  werden an den kombinierten Runner weitergereicht; relative Legacy-Pfade werden
  am Plan-Fixture-Verzeichnis aufgeloest.

## Annahmen und Grenzen

- Alle VU-Regelparameter, VN-Schadenziehungen und VN-Versicherungsentscheidungen
  muessen explizit im Plan oder im Basissnapshot vorliegen.
- Fehlen `logtime` oder `max_periods` im Periodenupdate, bleibt der
  Basissnapshot massgeblich.
- Carryover-Flags muessen JSON-Booleans sein.
- Entity-Updates duerfen nur vorhandene `entity_id`-Werte des Basissnapshots
  ueberschreiben.
- Der Plan trifft keine Aussage ueber historische Vollgleichheit.
