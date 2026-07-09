# Plan: IMS-Kern-Fachlogik nach Workbench-v1

## Ziel

Dieser Plan markiert den Ruecksprung vom abgeschlossenen lokalen
Workbench-Ausbau in die eigentliche IMS-Fachlogik. Er beschreibt den naechsten
reviewbaren Kernblock, ohne bereits eine neue Simulation, einen Scheduler oder
eine historische Vollgleichheit zu behaupten.

## Ausgangsstand

Die Workbench-v1 stellt lokale Metadaten, Run-Control-Grenzen, Diagnose,
Readiness und eine rein lesende Browser-Oberflaeche bereit. Dieser Rahmen ist
nuetzlich, aber nicht der fachliche IMS-Kern.

Der portierte Kern enthaelt bereits belastbare Ausschnitte:

- `python_port/ims/model/entities.py` fuer kleine BAV-, VU- und VN-Zustandscontainer.
- `python_port/ims/engine/context.py` und `python_port/ims/engine/scheduler.py` fuer
  explizite Kontext- und Scheduling-Grundlagen.
- `python_port/ims/engine/rng.py` fuer kontrollierte Zufallsquellen.
- BAV-/Agrsich-Bausteine in `python_port/ims/model/bav_service.py`,
  `python_port/ims/model/agrsich_service.py`, `python_port/ims/model/agrsich_export.py`
  und `python_port/ims/model/agrsich_writer.py`.
- VU- und VN-Regel-Slices in `python_port/ims/model/vu_rules.py`,
  `python_port/ims/model/vn_rules.py`, `python_port/ims/model/vn_insurance_rules.py`
  und `python_port/ims/model/vn_damage_rules.py`.
- explizite Mehrperioden-Adapter in `python_port/ims/engine/explicit_period_runner.py`
  und `python_port/ims/engine/explicit_period_plan.py`.
- Legacy-orientierte Referenzen und Vergleichsfixtures unter `tests/fixtures/` und
  `tests/references/legacy_agrsich/`.

`legacy_c/` ist in diesem Stand nur ein Platzhalter. Der naechste Kernschritt
darf deshalb keine nicht vorhandene C-Quelle als gelesen behaupten. Belastbare
Referenzpunkte sind die vorhandenen Portierungsplaene, Python-Slices,
Legacy-DAT-Referenzen und Vergleichstests.

## Bisheriger groesserer Kernblock

Der erste fachliche Block nach der Workbench hat die vorhandenen expliziten
VU/VN-Periodenlaeufe in Richtung validierbarer Kernlauf verdichtet:

1. bestehenden expliziten Periodenplan und Runner inventarisieren;
2. die heute unterstuetzten Snapshot-Familien und Carryover-Flags als stabile
   Eingabegrenze dokumentieren;
3. eine kleine, deterministische Kernlauf-Diagnose aus vorhandenen Planfixtures
   ableiten;
4. die Ausgabe auf Periodenfolge, globale Perioden, VU-Regelanwendungen,
   VN-Versicherungsregeln, VN-Schaden-/Settlement-Anwendungen und Legacy-Targets
   beschraenken;
5. keine neuen Fachregeln einfuehren, bevor diese Diagnose die vorhandenen
   Referenzfenster nachvollziehbar beschreibt.

Der passende PR-Titel waere:

`Ergaenze IMS-Kernlauf-Diagnose fuer explizite Periodenplaene`

Dieser Block ist umgesetzt. Der aktuelle Stand trennt weiterhin:

- read-only Plan- und Bundle-Diagnosen, die keine Runner starten;
- echte explizite Mehrperiodenlaeufe, die nur ueber explizite Snapshots und
  Tests/gezielte Aufrufe laufen;
- `build_explicit_multi_period_execution_summary` als stabile Beschreibung eines
  bereits ausgefuehrten expliziten Mehrperiodenergebnisses.

## Aktueller groesserer Kernblock

Der aktuelle groessere Schritt ordnet die Execution-Summary-Vertraege und die
vorhandenen expliziten VU/VN-Periodenplaene in den IMS-Kernvalidierungsueberblick
und die lokale Demo-Grenze ein, ohne dort einen Lauf zu starten. Ziel ist eine
gemeinsame, read-only Sprache fuer:

1. geplante Periodenstruktur aus `explicit_period_diagnostics`;
2. historische Referenzabdeckung aus `legacy_validation_overview` und Coverage;
3. vorhandene Execution-Summary-Felder als erwarteter Ergebnisvertrag fuer
   spaetere kontrollierte Ausfuehrungsadapter;
4. klare Blocker, wenn nur Plan-Diagnosen vorliegen und keine ausgefuehrte
   Summary vorhanden ist;
5. weiterhin keine Simulation, keine automatische historische Regelwahl und
   keine Vollgleichheitsbehauptung.

Der erste UI-/Demo-Anschluss ist umgesetzt: `/api/core-validation/overview` und
die Workbench-Karte `Kernvalidierungsueberblick` zeigen Plananzahl,
Periodenachsen, Legacy-Abdeckung und Execution-Summary-Vertrag lesend. Die
lokale Demo-Checkliste dokumentiert den aktuellen Diagnosebefund:
2 Planfixtures, 8 Perioden, globale Perioden `1, 2, 3, 4, 101, 102, 103, 104`,
19 Legacy-Referenzen, 6300 abgedeckte Zeilen und `execution_performed = false`.

Der passende PR-Titel waere:

`Plane Execution-Summary-Vertrag im IMS-Kernvalidierungsueberblick`

## Naechster fachlicher Slice

Nach der read-only Run-Control-Bruecke ist der naechste groessere Schritt wieder
ein schmaler Kern-Fachlogik-Slice. PR 16 plant diesen Anschluss unter
`docs/plans/explicit_period_transition_slice.md`: Zuerst werden die vorhandenen
VU-Periodenfixtures `replay_vu14_period_plan.json` und
`replay_vusk1_period_plan.json` als Periodenuebergangs- und Carryover-Grenze
kartiert. Der Plan bleibt ohne neue Fachlogik, ohne Runner-Start, ohne
Simulation, ohne automatische historische Regelwahl und ohne
Vollgleichheitsbehauptung.

PR 17 setzt diesen Anschluss als read-only
`ims.engine.explicit_period_transition_diagnostics` um. Die Diagnose beschreibt
benachbarte Uebergaenge aus den Planfixtures, meldet die fehlende
VN-Policyholder-Abdeckung als Hinweis
`explicit_period_transition_no_policyholders` und setzt `writes_performed`,
`execution_performed`, `simulation_performed` sowie
`automatic_historical_rule_selection_performed` auf `false`.

PR 18 ergaenzt das minimale Anschlussfixture
`tests/fixtures/replay_vn_policyholder_transition_plan.json`. Es belegt eine
VN-Policyholder-Subjektmenge fuer die Uebergangsdiagnose, ohne den Runner zu
starten oder eine historische Regelentscheidung abzuleiten.

PR 19 ergaenzt rein lesende Carryover-Kandidatenlisten in der
Uebergangsdiagnose. PR 20 plant den ersten echten Carryover-Code-Schnitt unter
`docs/plans/explicit_transition_carryover_code_slice.md`: Der spaetere Code darf
nur `apply_vu_foreign_info_carryover` und `apply_vn_state_carryover` als
vorhandene portierte Bausteine nutzen, muss explizites Opt-in verlangen und darf
keine historische Regelwirkung oder Vollgleichheit ableiten.

PR 21 setzt diesen Schnitt als `ims.engine.explicit_transition_carryover_probe`
um. Der Probe nutzt explizite Fixture-Snapshots als Quelle, fuehrt Carryover nur
bei `--apply-vu` oder `--apply-vn` in-memory aus und bleibt ohne API-/UI-,
Overview- oder Run-Control-Anbindung.

PR 22 ordnet den Probe als
`explicit_transition_carryover_probe_contract` im
`ims_core_validation_overview` ein. Der Overview beschreibt nur die erwarteten
Felder eines spaeter bereitgestellten Probe-Payloads und startet keinen Probe
aus dem Overview heraus.

PR 23 stellt denselben Vertrag ueber
`GET /api/core-validation/carryover-probe-contract` read-only bereit. Der
Endpunkt beschreibt vorab berechnete Probe-Payloads, akzeptiert aber keinen
Payload und startet keinen Probe.

PR 24 zeigt diesen Vertrag in der Workbench als read-only Karte
`Carryover-Probe-Vertrag`. Die Karte nutzt nur
`GET /api/core-validation/carryover-probe-contract`, nimmt keinen Payload
entgegen, startet keinen Probe, aktiviert keinen Ausfuehrungsadapter und leitet
keine automatische historische Regelwahl ab.

## Vorgeschlagene PR-Reihenfolge

1. Kernlauf-Diagnose fuer vorhandene explizite Periodenplaene, nur lesend und
   ohne neue Fachregel. Der Befehl
   `python -m ims.engine.explicit_period_diagnostics tests/fixtures/replay_vu14_period_plan.json`
   liest Planstruktur, Periodenfolge, globale Perioden, Snapshot-Familien,
   erwartete Regelanwendungsgrenzen und Legacy-Bezuege, startet aber keinen
   Runner und schreibt keine Ausgaben. Dieser Schritt ist umgesetzt.
2. Validierungsbericht fuer die vorhandenen Legacy-Agrsich-Referenzen
   vereinheitlichen, ohne Toleranzen still zu veraendern. Der lokale Befehl
   `python -m ims.model.legacy_validation_overview tests/fixtures/legacy_validation_bundle.json`
   fasst vorhandene Legacy-Agrsich-Validierungsfixtures als JSON zusammen,
   berichtet Tabellen, Perioden, Abweichungsachsen und die dokumentierte
   `legacy_compare_default`-Toleranz, startet aber keinen Runner und schreibt
   keine Reportartefakte. Dieser Schritt ist umgesetzt.
3. Diagnose-Buendel fuer mehrere vorhandene explizite Periodenplaene
   zusammenfassen. Der Befehl
   `python -m ims.engine.explicit_period_diagnostics_bundle tests/fixtures/replay_vu14_period_plan.json tests/fixtures/replay_vusk1_period_plan.json`
   aggregiert Planstatus, Perioden, globale Perioden, Snapshot-Familien und
   Legacy-Bezuege, ohne Runner oder Simulation zu starten. Dieser Schritt ist
   umgesetzt.
4. IMS-Kernvalidierungsueberblick aus Diagnose-Buendel,
   Legacy-Validierungsueberblick, Coverage-Matrix und Next-Family-Plan
   zusammenfuehren. Der Befehl
   `python -m ims.engine.core_validation_overview --legacy-fixture tests/fixtures/legacy_validation_bundle.json tests/fixtures/replay_vu14_period_plan.json tests/fixtures/replay_vusk1_period_plan.json`
   bleibt read-only und zeigt, welche weitere Validierung durch fehlende echte
   historische Referenzen blockiert ist.
5. Danach einen schmalen VU- oder VN-Regel-Slice aus den vorhandenen
   Plan-Dateien auswaehlen und mit explizitem Ursprung dokumentieren. Der erste
   Anschluss ist umgesetzt: `build_explicit_multi_period_execution_summary`
   beschreibt ausgefuehrte explizite VU/VN-Mehrperiodenlaeufe mit
   Periodenachsen, Anwendungszaehlungen, Carryover- und Legacy-Report-Status,
   ohne Simulation oder automatische historische Regelwahl zu behaupten.
6. Execution-Summary-Vertrag im `ims_core_validation_overview` planen
   (dieser Schnitt): read-only, ohne Runner-Start und ohne Ausfuehrung aus dem
   Overview heraus, aber mit expliziter Kennzeichnung, welche Ergebnisfelder ein
   spaeter kontrollierter Ausfuehrungsadapter liefern muss.
   Kurzgrenze: keine Ausfuehrung aus dem Overview heraus.
7. Read-only API-/UI-Anbindung fuer den Kernvalidierungsueberblick in die
   lokale Demo-Grenze einordnen, weiterhin ohne funktionalen Start. Dieser
   Anschluss ist umgesetzt: `/api/core-validation/overview`, die UI-Karte und
   `docs/migration/workbench_demo_checklist.md` zeigen die vorhandenen
   VU/VN-Periodenplaene diagnostisch.
8. Echte Run-Control-Anbindung an Kernlauf-Diagnosen erst als read-only
   Brueckenplan vorbereiten. Dieser Schnitt ist in
   `docs/plans/run_control_core_diagnostics_bridge_plan.md` dokumentiert:
   Queue-Aktionsplan und Kernvalidierungsueberblick duerfen spaeter nur
   gemeinsam gelesen werden; der read-only API-Schnitt
   `GET /api/run-control/core-diagnostics-bridge` schaltet keinen Schreibpfad,
   keinen UI-Startpfad und keinen Runner-Start frei.
9. Expliziten Periodenuebergang aus vorhandenen Planfixtures planen. Dieser
   Schnitt ist in `docs/plans/explicit_period_transition_slice.md`
   dokumentiert: `VU14L1.DAT` und `VUSK1L4.DAT` liefern belegbare
   Versicherer-Periodenfenster, aber noch keine VN-Policyholder und keine
   automatisch berechnete Regelwirkung.
10. Explizite Periodenuebergangsdiagnose umsetzen. Der Befehl
    `python -m ims.engine.explicit_period_transition_diagnostics tests/fixtures/replay_vu14_period_plan.json`
    beschreibt Uebergaenge, Subjektmengen, explizite Update-Felder und geplante
    Carryover-Flags, bleibt aber ohne Runner-Start, Simulation oder neue
    Fachlogik.
11. Minimales VN-Policyholder-Anschlussfixture ergaenzen. Das Fixture
    `tests/fixtures/replay_vn_policyholder_transition_plan.json` zeigt, dass
    `explicit_period_transition_no_policyholders` fuer eine belegte VN-
    Subjektmenge nicht mehr gemeldet wird; es bleibt ein explizites
    Eingabefixtures ohne Legacy-Vollgleichheitsbehauptung.
12. Engen Carryover-Code-Slice planen. Dieser Schnitt steht in
    `docs/plans/explicit_transition_carryover_code_slice.md` und begrenzt den
    naechsten Code-PR auf einen expliziten Carryover-Probe mit vorhandenen
    portierten Carryover-Bausteinen, ohne Simulation, API-/UI-Startpfad oder
    historische Regelableitung.
13. Engen Carryover-Probe umsetzen. Der Befehl
    `python -m ims.engine.explicit_transition_carryover_probe --apply-vn tests/fixtures/replay_vn_policyholder_transition_plan.json`
    prueft vorhandene Carryover-Bausteine in-memory gegen die
    Uebergangsdiagnose, schreibt nichts und startet keine Simulation.
14. Carryover-Probe-Vertrag in den Kernvalidierungsueberblick einordnen. Der
    Overview meldet `carryover_probe_available = false`,
    `carryover_probe_next_action = "provide_precomputed_carryover_probe"` und
    `overview_starts_probe = false`.
15. Read-only API-Vertrag fuer Carryover-Probe-Ergebnisse vorbereiten. Der
    Endpunkt `GET /api/core-validation/carryover-probe-contract` liefert
    `mode = "core_validation_carryover_probe_api_contract"`, bleibt ohne
    Request-Body und startet keinen Probe.
16. Read-only UI-Karte fuer denselben Vertrag vorbereiten. Die Workbench zeigt
    `Carryover-Probe-Vertrag`, bleibt aber ohne Probe-Upload, Probe-Start,
    Runner-Start, Ausfuehrungsadapter und automatische historische Regelwahl.

## Aktualisierte PR-Restplanung

Nach dem lokalen Inventar der historischen Testdaten unter `incomming/` ist der
Referenzblocker fuer mehrere Dateifamilien nicht mehr grundsaetzlich offen. Die
Versicherer-SK1-Zeitfenster `VUSK1L1.DAT` bis `VUSK1L5.DAT` sind nun als
versionierte Legacy-Referenzfenster im Bundle abgedeckt; weitere lokale
Kandidaten bleiben noch nicht versionierte Referenzen.

Aktualisierte grobe Restplanung:

- 0-1 PRs fuer weitere Inventar-/Akzeptanzgrenzen der neuen lokalen Kandidaten;
- 2-4 PRs fuer `IMSVNR01.DAT` bis `IMSVNR06.DAT`;
- 2-5 PRs fuer Klassenaggregate `IMSVNVK*.DAT` und `IMSVUVK*.DAT`;
- Plan- und Diagnose-PR fuer den schmalen Periodenuebergangs-/Carryover-Slice
  aus vorhandenen Planfixtures sind umgesetzt;
- Plan fuer den engen Carryover-Code-Slice ist umgesetzt;
- enger Carryover-Probe ist umgesetzt;
- Carryover-Probe-Vertrag im Kernvalidierungsueberblick ist umgesetzt;
- Carryover-Probe-API-Vertrag ist umgesetzt;
- Carryover-Probe-Vertragskarte in der Workbench ist umgesetzt;
- 1 PR bis zur demo-nahen read-only Carryover/Kern-Sicht;
- danach 3+ PRs fuer anschliessende schmale VU-/VN-Regel- oder
  Carryover-Code-Slices und spaetere Ausfuehrungsadapterplaene;
- read-only Execution-Summary-Vertrag, Kernvalidierungsueberblick und
  Run-Control-Bruecke sind umgesetzt; offen bleiben nur spaetere echte
  Ausfuehrungsadapter nach separater Freigabe.

Damit bleiben grob ca. 7-17+ reviewbare PRs bis zu einem deutlich breiteren
historischen Validierungsstand. Diese Schaetzung ersetzt keine
Vollgleichheitspruefung.

## Grenzen

- keine Fachlogikaenderung in diesem Plan-PR;
- keine Simulation starten;
- kein neuer HTTP-Schreibendpunkt;
- kein HTTP- oder UI-Schreibpfad;
- kein Browser-Upload oder Browser-Download;
- kein funktionaler Run-Start;
- kein Start eines expliziten Periodenrunners aus dem Kernvalidierungsueberblick;
- kein Szenario-Editor;
- keine SQLite-Migration;
- keine historische Vollgleichheitsbehauptung;
- keine Behauptung, dass nicht vorhandene `legacy_c/`-Quellen gelesen wurden.

## Validierung fuer diesen Plan

Dieser Plan wird durch Dokumentationstests abgesichert. Sie pruefen, dass der
Uebergang zur Fachlogik die vorhandenen Kernmodule benennt, den naechsten
Kernblock klar begrenzt und die Nicht-Ziele beibehaelt.
