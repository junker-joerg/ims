# Geplanter expliziter VU/VN-Periodenschritt

## Ziel

Dieser Slice verbindet den technischen Scheduler mit dem bereits portierten
expliziten VU/VN-Periodenrunner. Geplante Events fuehren die kontrollierte
Reihenfolge aus: zuerst VU-Regeln, danach VN-Versicherungsregel, VN-Schaden und
VN-Abrechnung.

## Ursprung im Altcode

Der fachliche Anschluss bleibt bei den bereits portierten VU-Regelkernen
`Vrvu*` und den VN-Regelpfaden `Vrvn01` bis `Vrvn06`. Historisch wuerde die
Auswahl und zeitliche Einordnung ueber PlanVU-/PlanVN-Umfelder laufen; dieser
Slice portiert diese historische Scheduler-Semantik noch nicht.

## Python-Abbildung

- `ScheduledExplicitPeriodResult` haelt das geplante Event und das Ergebnis des
  expliziten Periodenrunners zusammen.
- `ScheduledExplicitMultiPeriodResult` haelt die geplanten Events und das
  Ergebnis des validierten expliziten Mehrperiodenrunners zusammen.
- `run_scheduled_explicit_vu_vn_period_from_mapping` laedt ein In-Memory-
  Szenario, plant ein einzelnes `explicit_vu_vn_period`-Event und fuehrt danach
  `run_loaded_explicit_period` aus.
- `run_scheduled_explicit_vu_vn_periods_from_mappings` plant fuer mehrere
  Periodenszenarien `explicit_vu_vn_period`-Events auf globaler Zeitachse und
  delegiert die fachliche Ausfuehrung an `run_explicit_multi_period_from_mappings`.
- `run_scheduled_explicit_vu_vn_periods_from_fixture` nutzt dieselbe
  Scheduler-Diagnose fuer gespeicherte JSON-Fixtures und delegiert die
  Ausfuehrung an `run_explicit_multi_period_from_fixture`, inklusive der dort
  vorhandenen Carryover- und Legacy-Ziel-Verarbeitung.
- `run_scheduled_explicit_vu_vn_periods_from_plan_fixture` erzeugt aus einem
  expliziten Periodenplan dasselbe Runner-Fixture fuer die Scheduler-Diagnose
  und delegiert die Ausfuehrung an `run_explicit_multi_period_from_plan_fixture`.
  Damit bleiben Plan-Overrides, Carryover und Legacy-Ziele im bestehenden
  Plan-Runner verankert.
- Das Event nutzt `context.period` und `context.logtime` aus dem geladenen
  Szenario. Mehrperiodige Events verwenden `run_index * max_periods + period`
  als Scheduler-Periode. Mapping-, Fixture- und Plan-Wrapper fuehren die
  expliziten Perioden in genau dieser geplanten Event-Reihenfolge aus. Die
  fachliche Wirkung bleibt vollstaendig im expliziten Runner.
- Der Pfad kann VN-Schaden-/Abrechnungs-Snapshots ohne direkte
  `insurance_decisions` aus passenden `vn_insurance_rule_snapshots` speisen.

## Annahmen und Grenzen

- Der Baustein ist ein kontrollierter Orchestrierungsanschluss, keine
  historische Vollsimulation.
- Es werden nur explizite VU/VN-Periodenereignisse geplant; die validierte
  Periodenfolge, Carryover und Legacy-Vergleiche bleiben im bestehenden
  expliziten Runner verankert.
- Keine automatische historische Regelwahl, kein Dialog- oder UI-Pfad.
- Keine Behauptung historischer Vollgleichheit.
