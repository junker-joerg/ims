# Plan: Erster fachlicher VN-Carryover-Slice-Test

## Ziel

Dieser PR 26 legt den ersten bewusst fachlichen Test-Slice nach der
demo-nahen read-only Carryover/Kern-Sicht fest. Der Schnitt bleibt ein
Plan-PR: Er startet keine Simulation, fuehrt keinen neuen Runner ein und
behauptet keine historische Vollgleichheit.

Der naechste echte Test soll den bereits vorhandenen engen
Carryover-Probe-Schnitt zu einem kleinen fachlichen Regressionstest
verdichten:

`VN-Policyholder-State-Carryover von globaler Periode 21 nach 22`

## Entscheidung fuer den ersten Slice

Der erste Slice soll das Fixture
`tests/fixtures/replay_vn_policyholder_transition_plan.json` nutzen.

Gruende:

- Es enthaelt eine belegte VN-Policyholder-Subjektmenge und loest die fruehere
  Diagnosegrenze `explicit_period_transition_no_policyholders`.
- Es nutzt explizite Eingabewerte statt historisch rekonstruierter
  Vorperiodenergebnisse.
- Es passt direkt zu dem vorhandenen portierten Baustein
  `apply_vn_state_carryover` aus
  `python_port/ims/engine/vn_rule_runner.py`.
- Es wird bereits durch `ims.engine.explicit_transition_carryover_probe`
  kontrolliert in-memory ansprechbar, ohne API, UI, Run-Control oder Overview
  zu starten.

Die VU-Planfixtures `replay_vu14_period_plan.json` und
`replay_vusk1_period_plan.json` bleiben fuer diesen PR nur Kontext. Sie belegen
weiter Versicherer-Zeitfenster und Legacy-Bezuege, liefern aber keine
VN-Policyholder-Subjektmenge fuer den ersten fachlichen Carryover-Test.

## Beteiligte Subjekte und Zustandsvektoren

Der Slice ist bewusst klein:

| Bereich | Wert |
| --- | --- |
| Fixture | `tests/fixtures/replay_vn_policyholder_transition_plan.json` |
| Vorperiode | lokale Periode `1`, globale Periode `21` |
| Zielperiode | lokale Periode `2`, globale Periode `22` |
| Versicherer | `entity_id = 11` |
| VN/Policyholder | `entity_id = 21` |
| geplanter Carryover | `carry_forward_vn_state = true` |
| portierter Baustein | `apply_vn_state_carryover` |
| Kontrolladapter | `probe_explicit_transition_carryover(..., apply_vn=True)` |

Zu pruefende Zustandsfelder fuer den ersten echten Regressionstest:

- `carried_insurer_ids = [11]`;
- `carried_policyholder_ids = [21]`;
- `from_global_period = 21`;
- `to_global_period = 22`;
- `vn_carryover_planned = true`;
- `vn_carryover_executed = true`;
- `diagnostic_candidate_ids_match = true`;
- `previous_result_source = "explicit_fixture_snapshot"`;
- `carried_insurer_state["11"]["premiums_current"] = 101.0`;
- `carried_policyholder_state["21"]["end_wealth_current"] = 999.0`.

Diese Werte sind Zwischenzustaende eines expliziten Fixtures. Sie sind kein historischer Gleichheitsnachweis und kein historischer Vollgleichheitsnachweis gegen einen vollstaendigen IMS/ESS-Lauf.

## Ursprung und Mapping

| Ursprung / Referenz | Python-Ziel |
| --- | --- |
| Explizites VN-Transition-Fixture | `tests/fixtures/replay_vn_policyholder_transition_plan.json` |
| Periodenuebergangsdiagnose | `python_port/ims/engine/explicit_period_transition_diagnostics.py` |
| Carryover-Probe | `python_port/ims/engine/explicit_transition_carryover_probe.py` |
| VN-State-Carryover | `python_port/ims/engine/vn_rule_runner.py::apply_vn_state_carryover` |
| VN-/VU-Zustandscontainer | `python_port/ims/model/entities.py` |

`legacy_c/` enthaelt in diesem Stand keine belastbar gelesene historische
C-Quelle fuer diesen Slice. Der Plan behauptet deshalb keinen direkten
C-Funktionsabgleich. Die belastbaren Referenzen sind die vorhandenen
Portierungsbausteine, das explizite Fixture und die bestehenden
Legacy-Agrsich-Referenzfenster.

## Naechste PRs

Der Weg zum ersten echten fachlichen Test ist klein geblieben:

1. PR 26: diesen Slice als fachlichen Testplan festlegen und die Grenzen
   dokumentieren (erledigt).
2. PR 27: den VN-Carryover-Slice als eigenen Regressionstest mit klarer
   erwarteter Ergebnisform ausfuehren. Dabei darf nur der vorhandene
   Probe-/Carryover-Pfad genutzt werden; keine Simulation und keine neue
   Fachregel (erledigt:
   `tests/test_first_fachlicher_vn_carryover_regression.py`).
3. PR 28: die Assertions und Dokumentation so schaerfen, dass der Slice als
   erster fachlicher Regressionstest zaehlbar ist, weiterhin ohne
   Vollgleichheitsbehauptung.

## Umgesetzter Regressionstest in PR 27

`tests/test_first_fachlicher_vn_carryover_regression.py` fuehrt den Slice
ueber `probe_explicit_transition_carryover(..., apply_vn=True)` aus und prueft
die fachlichen Zwischenzustaende fuer Versicherer `11`, Policyholder `21` und
globale Perioden `21 -> 22`.

Der Test bleibt ein enger Regressionstest auf explizite Fixture-Zustaende. Er
startet keine Simulation, nutzt keinen Scheduler, oeffnet keinen API-/UI- oder
Run-Control-Pfad und behauptet keine historische Vollgleichheit.

## Testgrenzen fuer PR 27

Der naechste Code-PR darf:

- `probe_explicit_transition_carryover` mit `apply_vn=True` fuer genau dieses
  Fixture nutzen;
- die oben genannten Zwischenzustaende als fachliche Regression pruefen;
- die bestehende Diagnosegrenze
  `diagnostic_candidate_ids_match = true` als Konsistenzsignal verwenden;
- weiter `writes_performed = false`, `execution_performed = false`,
  `simulation_performed = false` und
  `automatic_historical_rule_selection_performed = false` verlangen.

Der naechste Code-PR darf nicht:

- eine Simulation oder einen Scheduler starten;
- aus API, UI, Overview oder Run-Control heraus ausfuehren;
- ein historisches Vorperiodenergebnis erfinden;
- eine automatische historische Regelwahl ableiten;
- eine neue Fachregel einfuehren;
- neue VU-/VN-Fachlogik einfuehren;
- eine historische Vollgleichheit behaupten.

Kurzgrenze: keine neue Fachregel und keine historische Vollgleichheit behaupten.

## Offene Punkte

- Der Slice prueft zunaechst nur explizite Fixture-Zwischenzustaende, keine
  historische DAT-Vollgleichheit.
- Ein spaeterer Teilgleichheitsnachweis braucht eigene Legacy-Bezuege oder
  belastbar erklaerte Vergleichsfenster.
- VU-Carryover und weitere VN-Regelwirkungen bleiben separate Folge-PRs.

## Definition von fertig fuer diesen PR

- Der erste fachliche Slice ist eindeutig ausgewaehlt.
- Beteiligte Subjekte, Perioden, Zustandsfelder und Python-Bausteine sind
  benannt.
- Die naechsten zwei PRs bis zum ersten fachlichen Regressionstest sind
  abgegrenzt.
- Dokumentationstests sichern Plan, Grenzen und Nicht-Ziele.
- Es wurde keine Simulation gestartet und keine neue Fachlogik eingefuehrt.
