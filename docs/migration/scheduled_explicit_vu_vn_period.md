# Geplanter expliziter VU/VN-Periodenschritt

## Ziel

Dieser Slice verbindet den technischen Scheduler mit dem bereits portierten
expliziten VU/VN-Periodenrunner. Ein einzelnes geplantes Event fuehrt die
kontrollierte Reihenfolge aus: zuerst VU-Regeln, danach VN-Versicherungsregel,
VN-Schaden und VN-Abrechnung.

## Ursprung im Altcode

Der fachliche Anschluss bleibt bei den bereits portierten VU-Regelkernen
`Vrvu*` und den VN-Regelpfaden `Vrvn01` bis `Vrvn06`. Historisch wuerde die
Auswahl und zeitliche Einordnung ueber PlanVU-/PlanVN-Umfelder laufen; dieser
Slice portiert diese historische Scheduler-Semantik noch nicht.

## Python-Abbildung

- `ScheduledExplicitPeriodResult` haelt das geplante Event und das Ergebnis des
  expliziten Periodenrunners zusammen.
- `run_scheduled_explicit_vu_vn_period_from_mapping` laedt ein In-Memory-
  Szenario, plant ein einzelnes `explicit_vu_vn_period`-Event und fuehrt danach
  `run_loaded_explicit_period` aus.
- Das Event nutzt `context.period` und `context.logtime` aus dem geladenen
  Szenario. Die fachliche Wirkung bleibt vollstaendig im expliziten Runner.
- Der Pfad kann VN-Schaden-/Abrechnungs-Snapshots ohne direkte
  `insurance_decisions` aus passenden `vn_insurance_rule_snapshots` speisen.

## Annahmen und Grenzen

- Der Baustein ist ein kontrollierter Orchestrierungsanschluss, keine
  historische Vollsimulation.
- Es wird genau ein explizites VU/VN-Periodenereignis geplant.
- Keine automatische historische Regelwahl, kein Dialog- oder UI-Pfad.
- Keine Behauptung historischer Vollgleichheit.
