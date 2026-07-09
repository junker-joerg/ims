# Plan: Enger Carryover-Code-Slice fuer explizite Periodenuebergaenge

## Ziel

Dieser PR 20 bereitet den naechsten echten Code-Schnitt nach den rein lesenden
Carryover-Kandidatenlisten vor. Der Schnitt soll keine historische Regelwirkung
ableiten, keine Simulation starten und keinen neuen Runner-Startpfad
freischalten. Er grenzt nur ab, wie vorhandene portierte Carryover-Bausteine in
einem spaeteren kleinen Code-PR kontrolliert geprueft werden duerfen.

Der spaetere Code darf ausschliesslich auf bereits vorhandene Bausteine
aufsetzen:

- `apply_vu_foreign_info_carryover` aus
  `python_port/ims/engine/vu_rule_runner.py`;
- `apply_vn_state_carryover` aus
  `python_port/ims/engine/vn_rule_runner.py`;
- `diagnose_explicit_period_transitions` aus
  `python_port/ims/engine/explicit_period_transition_diagnostics.py` als
  nicht ausfuehrende Eingabe- und Grenzdiagnose.

## Belegbare Eingabegrenze

Die vorhandenen Fixtures bleiben die einzige Eingabe fuer diesen Anschluss:

- `tests/fixtures/replay_vu14_period_plan.json`
  - VU-Planfixture mit Versicherer `14` und Legacy-Fenster `VU14L1.DAT`;
  - Carryover-Kandidaten nur fuer gemeinsame Versicherer-IDs.
- `tests/fixtures/replay_vusk1_period_plan.json`
  - VU-Planfixture mit Versicherer `77` und Legacy-Fenster `VUSK1L4.DAT`;
  - weiteres Versicherer-Zeitfenster, aber keine neue Aggregatstufe.
- `tests/fixtures/replay_vn_policyholder_transition_plan.json`
  - minimales VN-Anschlussfixture mit Versicherer `11` und Policyholder `21`;
  - belegt VN-Subjektmenge und loest die reine Diagnosegrenze
    `explicit_period_transition_no_policyholders`.

Diese Fixtures enthalten explizite Eingabewerte. Sie sind keine historische
Vollsimulation und keine automatische Rekonstruktion historischer VU-/VN-Regeln.

## Vorgeschlagener Code-Schnitt

Der naechste Code-PR soll einen kleinen, getrennten Carryover-Probe vorbereiten.
Geeigneter Arbeitstitel:

`Pruefe explizite Carryover-Bausteine fuer Periodenuebergaenge`

Der Probe darf:

1. ein einzelnes explizites Periodenplan-Fixture laden;
2. dieselbe Perioden- und Subjektgrenze wie
   `explicit_period_transition_diagnostics` pruefen;
3. nur bei explizitem Opt-in einen bestehenden Carryover-Baustein auf zwei
   geladene Nachbarperioden anwenden;
4. die gemeldeten `insurer_ids`, `policyholder_ids`, Quell-/Zielperioden und
   globalen Perioden mit der Uebergangsdiagnose vergleichen;
5. die mutierten Felder als Carryover-Probe ausweisen, ohne daraus
   historische Gleichheit oder automatische Regelwirkung abzuleiten.

Der Probe darf nicht aus `core_validation_overview`, der Workbench-UI,
Run-Control oder einem HTTP-Endpunkt heraus gestartet werden.

## Wichtige Fachgrenze

Die VU- und VN-Carryover-Funktionen erwarten ein echtes Vorperioden-Ergebnis:

- `apply_vu_foreign_info_carryover` erwartet ein
  `VUForeignInfoPeriodRunResult`.
- `apply_vn_state_carryover` erwartet ein `VNSettlementPeriodRunResult`.

Der naechste Code-PR darf deshalb kein historisches Vorperioden-Ergebnis
erfinden. Wenn ein Fixture nur explizite Eingabewerte liefert, muss der Probe
das offen melden oder mit einem separat und gezielt erzeugten portierten
Periodenergebnis arbeiten. Diese Erzeugung bleibt weiterhin ein kontrollierter
Testpfad und ist keine Vollsimulation.

Kurzregel: kein historisches Vorperioden-Ergebnis erfinden.

## Erwarteter Ergebnisvertrag

Ein spaeterer Probe-Result sollte mindestens diese Felder berichten:

- `mode = "explicit_transition_carryover_probe"`;
- `plan_path`;
- `from_period`, `to_period`, `from_global_period`, `to_global_period`;
- `vu_carryover_requested`, `vn_carryover_requested`;
- `vu_carryover_executed`, `vn_carryover_executed`;
- `carried_insurer_ids`, `carried_policyholder_ids`;
- `source_fields`, getrennt fuer VU-Insurer, VN-Insurer und VN-Policyholder;
- `diagnostic_candidate_ids_match = true`;
- `writes_performed = false` fuer Dateisystem/HTTP/UI;
- `execution_performed = false` fuer Simulation/Runner-Startpfade;
- `simulation_performed = false`;
- `automatic_historical_rule_selection_performed = false`.

Lokale Objektmutationen innerhalb eines gezielten Unit-Tests duerfen als
Carryover-Probe sichtbar sein. Sie duerfen nicht als Schreibpfad, Simulation
oder historische Vollgleichheit beschrieben werden.

## Tests fuer den naechsten Code-PR

Der Code-PR sollte klein bleiben und mindestens pruefen:

- ohne explizites Opt-in wird kein Carryover ausgefuehrt;
- bei VU-Opt-in werden nur gemeinsame Versicherer-IDs aus der
  Uebergangsdiagnose getragen;
- bei VN-Opt-in werden gemeinsame Versicherer- und Policyholder-IDs getragen;
- Quell- und Zielperioden sowie globale Perioden stimmen mit der bestehenden
  Uebergangsdiagnose ueberein;
- fehlendes oder nicht belegbares Vorperioden-Ergebnis bleibt ein Blocker und
  wird nicht still gefuellt;
- `writes_performed`, `simulation_performed` und
  `automatic_historical_rule_selection_performed` bleiben `false`.

## Nicht-Ziele

- keine neue VU-/VN-Fachregel;
- keine automatische historische Regelableitung;
- keine Simulation und kein Scheduler-Start;
- kein Start aus API, UI, Overview oder Run-Control;
- kein neuer HTTP-Schreibpfad;
- keine Uebernahme von `VU014PR1.DAT`;
- keine historische Vollgleichheitsbehauptung;
- keine Behauptung, dass nicht vorhandene `legacy_c/`-Quellen gelesen wurden.

## Definition von fertig fuer diesen Plan-PR

- Der Carryover-Code-Schnitt ist als eigener Plan dokumentiert.
- Die vorhandenen portierten Carryover-Bausteine und ihre Eingabegrenzen sind
  benannt.
- Die Rest-PR-Planung verweist auf diesen Plan.
- Dokumentationstests sichern die konservativen Grenzen.
- Es wurde keine Simulation gestartet und kein historisches Ergebnis erfunden.
