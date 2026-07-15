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

PR 25 ergaenzt den Demo-/Doku-Smoke fuer diese read-only Carryover/Kern-Sicht.
Der Smoke liest den Carryover-Probe-Vertrag neben Dry-Run, Queue,
Aktionsplan und Run-Control-Kernblick-Bruecke und prueft weiter
`api_starts_probe = false`, `api_accepts_probe_payload = false`,
`execution_performed = false` und `simulation_performed = false`.

PR 26 legt den ersten echten fachlichen Test-Slice als Plan fest:
`docs/plans/first_fachlicher_slice_test_plan.md` waehlt den
VN-Policyholder-State-Carryover aus
`tests/fixtures/replay_vn_policyholder_transition_plan.json`. Der geplante
Regressionstest soll Versicherer `11` und Policyholder `21` von globaler
Periode `21` nach `22` pruefen, mit `apply_vn_state_carryover` und
`probe_explicit_transition_carryover(..., apply_vn=True)` als bestehendem
portierten Pfad. Dieser Plan fuehrt noch keinen neuen Testpfad ein und startet
keine Simulation.

PR 27 fuehrt diesen Slice als eigenen fachlichen Regressionstest aus:
`tests/test_first_fachlicher_vn_carryover_regression.py` prueft den
VN-Carryover von Versicherer `11` und Policyholder `21` aus globaler Periode
`21` nach `22` ueber den vorhandenen Probe-/Carryover-Pfad. Der Test bleibt
ohne Simulation, ohne Scheduler-Start, ohne API-/UI-/Run-Control-Pfad und ohne
historische Vollgleichheitsbehauptung.

PR 28 schaerft diesen ersten fachlichen Regressionstest. Die Assertions binden
die VN-Source-Field-Vertraege direkt an die bestehenden Konstanten
`VN_CARRYOVER_INSURER_SOURCE_FIELDS` und
`VN_CARRYOVER_POLICYHOLDER_SOURCE_FIELDS`; die Migrationsnotiz
`docs/migration/first_fachlicher_regressionstest.md` dokumentiert Zweck,
Grenzen und offene Folgearbeit.

PR 29 legt den zweiten schmalen fachlichen Slice fest:
`docs/plans/second_fachlicher_slice_test_plan.md` waehlt eine
VN-Regelwirkung ueber explizite `best_info`-Snapshots. Der geplante Test soll
Policyholder `21`, Versicherer `11/12`, Periode `5`, die erwartete
Versicherungsentscheidung `[12, None]` und `information_cost = 4.0` pruefen.
VU-Carryover bleibt ein spaeterer eigener Slice, weil dafuer ein eigenes
explizites Fixture konservativer ist.

PR 30 setzt diesen zweiten fachlichen Slice um:
`tests/test_second_fachlicher_vn_rule_snapshot_regression.py` prueft die reine
`best_info`-Snapshot-Wirkung und eine Runner-Grenze ueber
`run_vn_settlement_period_from_mapping`. Die Migrationsnotiz
`docs/migration/second_fachlicher_regressionstest.md` grenzt den Test weiter
von Simulation, UI-/Run-Control-Startpfad und historischer Vollgleichheit ab.

PR 31 legt den dritten schmalen fachlichen Slice fest:
`docs/plans/third_fachlicher_slice_test_plan.md` waehlt ein
VU-Carryover-Fixture fuer Versicherer `10` von lokaler Periode `2` nach `3`.
Der geplante Test soll `carryovers[0].insurer_ids = [10]`,
`foreign_info.insurer.dp = [51.0, 52.0]` und
`policyholders_prev_sector = [30.0, 80.0]` pruefen.

PR 32 setzt diesen dritten fachlichen Slice um:
`tests/test_third_fachlicher_vu_carryover_regression.py` prueft den
VU-Carryover, die weitergerollte Frmdinf-Basis und die Vrvu04-
Nettowechslerbasis. Die Migrationsnotiz
`docs/migration/third_fachlicher_regressionstest.md` grenzt den Test weiter von
Simulation, UI-/Run-Control-Startpfad und historischer Vollgleichheit ab.

PR 33 legt den naechsten groesseren Schritt fest:
`docs/plans/controlled_execution_adapter_plan.md` waehlt nach drei fachlichen
Regressionstests einen schmalen kontrollierten Ausfuehrungsadapter-Vertrag als
naechsten Schnitt. Dieser Plan startet noch keinen Runner und haelt API, UI,
Queue, Preflight, Aktionsplan und Kernblick-Bruecke weiter auf
`execution_performed = false`.

PR 34 setzt diesen Vertrag als read-only DTO um:
`python_port/ims/api/controlled_execution_adapter_contract.py` beschreibt
Fixture-Eingaben, Preconditions, verbotene Grenzen und die erwarteten Felder des
`explicit_multi_period_execution_summary`-Vertrags. Der zugehoerige Test
`tests/test_api_controlled_execution_adapter_contract.py` prueft die JSON-Form,
die Schreibfreiheit und die Argumentablehnung; die Migrationsnotiz
`docs/migration/controlled_execution_adapter_contract.md` ordnet den Schnitt ein.
Auch dieser Stand startet keinen Runner und haelt `execution_performed = false`.

PR 35 setzt den lokalen Adapter um:
`python_port/ims/api/controlled_execution_adapter.py` fuehrt nur explizit
freigegebene Fixture-Laeufe aus, akzeptiert keinen freien Output-Pfad und gibt
das Ergebnis als `explicit_multi_period_execution_summary` zurueck. Der Test
`tests/test_api_controlled_execution_adapter.py` prueft Freigabepflicht,
Fixture-Arten, Schreibfreiheit und CLI-Grenzen; die Migrationsnotiz
`docs/migration/controlled_execution_adapter.md` grenzt den Schnitt von API, UI,
Queue, Simulation und Vollgleichheit ab.

PR 36 entscheidet den naechsten Anschluss:
`docs/plans/run_control_adapter_result_plan.md` waehlt ein read-only
Adapter-Resultat fuer Run-Control als naechsten Schnitt. Run-Control soll
zunaechst nur ein bereits lokal erzeugtes `controlled_execution_adapter`-JSON
einordnen oder dessen Ergebnisform beschreiben duerfen. Es gibt weiterhin
keinen Adapterstart, keinen Browser-Upload, keinen Queue-Worker, keinen
Startbutton und keine historische Vollgleichheitsbehauptung.

PR 37 setzt diesen Vertrag um:
`python_port/ims/api/run_control_adapter_result_contract.py` beschreibt die
erwartete `controlled_execution_adapter`-Resultatform und prueft bereits
erzeugte JSON-Dateien read-only. Der Test
`tests/test_api_run_control_adapter_result_contract.py` belegt Vertrag,
Validator und CLI-Schreibfreiheit; die Migrationsnotiz
`docs/migration/run_control_adapter_result_contract.md` dokumentiert die
Grenzen.

PR 38 hat die naechste read-only Anzeigegrenze geplant:
`docs/plans/run_control_adapter_result_view_plan.md` legt eine rein lesende
API-/UI-Anzeigeplanung fuer bereits lokal erzeugte Adapterresultate fest.

PR 39 setzt den ersten API-Schnitt dafuer um:
`python_port/ims/api/run_control_adapter_result_api_contract.py` stellt
`GET /api/run-control/adapter-result-contract` als read-only Vertrag bereit.
Der Endpunkt bleibt ohne Payload-Upload, ohne HTTP-Validierung eines
Adapter-Resultats, ohne UI-Startbutton und ohne Adapterstart aus Run-Control.

PR 40 zeigt diesen Vertrag als gesperrte UI-Karte:
`frontend/src/main.tsx` laedt `GET /api/run-control/adapter-result-contract`
und stellt `Adapter-Resultat-Vertrag` nur lesend dar. Die Karte bleibt ohne
Upload, Dateiauswahl, Startbutton, HTTP-Resultatvalidierung und Adapterstart.

PR 41 kehrt danach bewusst zu einem schmalen fachlichen Slice zurueck:
`tests/test_fourth_fachlicher_vn_best_info_carryover_regression.py` prueft die
bereits belegte VN-`best_info`-Entscheidung fuer Policyholder `21` und
Versicherer `11/12` zusammen mit dem vorhandenen VN-State-Carryover von
Periode `5` nach `6`. Die zweite Periode enthaelt keine neuen VN-Regel-,
Schaden- oder Settlement-Snapshots; die Migrationsnotiz
`docs/migration/fourth_fachlicher_regressionstest.md` grenzt den Slice von
Simulation, API-/UI-/Run-Control-Startpfad und historischer Vollgleichheit ab.

PR 42 verbreitert die VN-Regelabdeckung noch einmal schmal:
`tests/test_fifth_fachlicher_vn_sample_search_regression.py` prueft
`sample_search` / Vrvn05 ueber explizite Snapshots, feste
`insurer_choice_draws_by_sector`, Stichprobendiagnose und die Uebernahme in den
VN-Schaden-/Settlement-Runner. Die Migrationsnotiz
`docs/migration/fifth_fachlicher_regressionstest.md` dokumentiert Ursprung,
Mapping, Grenzen und die Schaetzung von noch 5 bis 7 reviewbaren PRs bis zu
einer benutzbaren kontrollierten Demo-Simulation.

PR 43 bereitet die explizite Run-Control-Ausfuehrungsfreigabe als Plan vor:
`docs/plans/run_control_execution_release_plan.md` beschreibt die Freigabekette
von Dry-Run, Queue, Action-Plan, expliziter Ausfuehrungsfreigabe, spaeterem
Adapterstart und Ergebnisablage. Der Schnitt bleibt ohne neuen API-Startpfad,
ohne UI-Startbutton, ohne Queue-Worker, ohne Simulation und ohne
Vollgleichheitsbehauptung.

PR 44 stellt den hart gegateten API-Startvertrag bereit:
`python_port/ims/api/run_control_adapter_start_contract.py` und
`GET /api/run-control/adapter-start-contract` beschreiben nur den spaeteren
Startrequest, Preconditions und verbotene Grenzen. `POST /api/run-control/adapter-start`
existiert noch nicht; `api_starts_adapter`,
`ui_start_enabled`, `queue_worker_enabled`, `writes_enabled` und
`execution_enabled` bleiben `false`.

PR 45 stellt die lokale Queue-/Status-/Resultat-Persistenzgrenze bereit:
`python_port/ims/api/run_control_execution_result_store.py` speichert nur ein
vorab validiertes Adapter-Resultat in eine explizite SQLite-Quelle, setzt den
Queue-Status `result_persisted` und laesst `execution_performed` fuer die Queue
weiter `false`. Der Schnitt startet keinen Adapter, keinen Worker und keine
Simulation.

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
17. Demo-/Doku-Smoke fuer die read-only Carryover/Kern-Sicht ergaenzen. Der
    Demo-Smoke liest `GET /api/core-validation/carryover-probe-contract`,
    prueft die gesperrten Probe-Grenzen und nutzt `carryover-probe-contract`
    als stabilen UI-Anker.
18. Ersten fachlichen VN-Carryover-Slice-Test planen. Der Plan
    `docs/plans/first_fachlicher_slice_test_plan.md` fixiert
    `replay_vn_policyholder_transition_plan.json`, Versicherer `11`,
    Policyholder `21`, globale Perioden `21 -> 22` und die erwarteten
    Zwischenzustaende fuer den naechsten Regressionstest.
19. Geplanten VN-Carryover-Slice als Regressionstest ausfuehren. Dieser Schnitt
    ist umgesetzt:
    `tests/test_first_fachlicher_vn_carryover_regression.py` prueft
    `carried_insurer_ids = [11]`, `carried_policyholder_ids = [21]`,
    `diagnostic_candidate_ids_match = true` und die gesperrten
    Ausfuehrungs-/Simulationsflags.
20. Ersten fachlichen Regressionstest schaerfen und einordnen. Dieser Schnitt
    ist umgesetzt: `docs/migration/first_fachlicher_regressionstest.md`
    dokumentiert den belegten VN-Carryover-Zwischenzustand und grenzt ihn von
    historischer Vollgleichheit ab.
21. Zweiten fachlichen Slice waehlen. Dieser Schnitt ist umgesetzt:
    `docs/plans/second_fachlicher_slice_test_plan.md` plant die
    VN-Regelwirkung ueber explizite `best_info`-Snapshots als naechsten
    Regressionstest, weiterhin ohne Simulation, Runner-Start aus einer UI oder
    historische Vollgleichheitsbehauptung.
22. Geplanten zweiten fachlichen Slice als Regressionstest ausfuehren. Dieser
    Schnitt ist umgesetzt:
    `tests/test_second_fachlicher_vn_rule_snapshot_regression.py` prueft
    `chosen_insurer_ids = [12, None]`, `selected_insurer_ids = [12, 11]`,
    `information_cost = 4.0` und die Uebernahme in den VN-Periodenlauf.
23. Dritten fachlichen Slice waehlen. Dieser Schnitt ist umgesetzt:
    `docs/plans/third_fachlicher_slice_test_plan.md` plant ein
    VU-Carryover-Fixture als naechsten Regressionstest, weiterhin ohne
    Simulation, API-/UI-/Run-Control-Startpfad oder historische
    Vollgleichheitsbehauptung.
24. Geplanten dritten fachlichen Slice als Regressionstest ausfuehren. Dieser
    Schnitt ist umgesetzt:
    `tests/test_third_fachlicher_vu_carryover_regression.py` prueft
    `carryovers[0].insurer_ids = [10]`, `foreign_info.insurer.dp = [51.0, 52.0]`,
    `policyholders_prev_sector = [30.0, 80.0]` und
    `net_switcher_values = [0.0, 0.0]`.
25. Schmalen Ausfuehrungsadapter-Vertrag planen. Dieser Schnitt ist umgesetzt:
    `docs/plans/controlled_execution_adapter_plan.md` beschreibt den ersten
    Adapter nur als Vertrag und Grenze, ohne Runner-Start, API-/UI-Startpfad,
    Queue-Worker oder historische Vollgleichheitsbehauptung.
26. Read-only Ausfuehrungsadapter-Vertrag als DTO und Vertragstest vorbereiten.
    Dieser Schnitt ist umgesetzt:
    `python_port/ims/api/controlled_execution_adapter_contract.py`,
    `tests/test_api_controlled_execution_adapter_contract.py` und
    `docs/migration/controlled_execution_adapter_contract.md` validieren den
    Vertrag ohne Runner-Start.
27. Lokalen kontrollierten Ausfuehrungsadapter umsetzen. Dieser Schnitt ist
    umgesetzt: `python_port/ims/api/controlled_execution_adapter.py`,
    `tests/test_api_controlled_execution_adapter.py` und
    `docs/migration/controlled_execution_adapter.md` fuehren den Adapter nur
    mit explizitem Freigabeflag und ohne Output-Pfad ein.
28. Read-only Adapter-Resultat fuer Run-Control planen. Dieser Schnitt ist
    umgesetzt: `docs/plans/run_control_adapter_result_plan.md` entscheidet,
    dass Run-Control zunaechst nur ein bereits lokal erzeugtes Adapterergebnis
    einordnen darf, ohne Adapterstart.
29. Read-only Adapter-Resultat-Vertrag fuer Run-Control umsetzen. Dieser
    Schnitt ist umgesetzt:
    `python_port/ims/api/run_control_adapter_result_contract.py`,
    `tests/test_api_run_control_adapter_result_contract.py` und
    `docs/migration/run_control_adapter_result_contract.md` validieren ein
    bereits erzeugtes Adapterresultat ohne Adapterstart.
30. Read-only Anzeige fuer Adapter-Resultate planen. Vorgeschlagen fuer den
    naechsten Schnitt und umgesetzt:
    `docs/plans/run_control_adapter_result_view_plan.md` soll API-/UI-Anzeige
    nur als gesperrte, lesende Grenze vorbereiten.
31. Read-only API-Vertrag fuer Adapter-Resultate bereitstellen. Dieser Schnitt
    ist umgesetzt:
    `python_port/ims/api/run_control_adapter_result_api_contract.py`,
    `tests/test_api_run_control_adapter_result_api_contract.py` und
    `docs/migration/run_control_adapter_result_api_contract.md` beschreiben
    `GET /api/run-control/adapter-result-contract` ohne Payload-Upload,
    HTTP-Validierung oder Adapterstart.
32. Gesperrte UI-Karte fuer Adapter-Resultat-Vertrag anzeigen. Dieser Schnitt
    ist umgesetzt: `frontend/src/main.tsx`, `frontend/src/styles.css` und
    `tests/test_frontend_shell.py` zeigen `Adapter-Resultat-Vertrag` ohne
    Upload, Dateiauswahl, Startbutton oder Adapterstart.
33. Vierten fachlichen VN-Slice als Regressionstest ausfuehren. Dieser Schnitt
    ist umgesetzt:
    `tests/test_fourth_fachlicher_vn_best_info_carryover_regression.py` prueft
    die `best_info`-Entscheidung `[12, None]`, `information_cost = 4.0`,
    `damages = [9.0, 0.0]`, `end_wealth_current = 87.0` und den
    weitergetragenen VN-Zustand in Periode `6` ohne neue VN-Snapshots.
34. Fuenften fachlichen VN-Slice als Regressionstest ausfuehren. Dieser
    Schnitt ist umgesetzt:
    `tests/test_fifth_fachlicher_vn_sample_search_regression.py` prueft
    `sample_search` / Vrvn05, `sampled_insurer_ids = [[11, 12], [11]]`,
    `information_cost = 3.0`, `damages = [9.0, 0.0]` und
    `end_wealth_current = 87.0`.
35. Run-Control-Ausfuehrungsfreigabe planen. Dieser Schnitt ist umgesetzt:
    `docs/plans/run_control_execution_release_plan.md` benennt Preconditions,
    verbotene Pfade und die PR-Reihenfolge bis zur benutzbaren kontrollierten
    Demo-Simulation.
36. API-Startvertrag fuer den kontrollierten Adapter hart gegated vorbereiten.
    Dieser Schnitt ist umgesetzt:
    `python_port/ims/api/run_control_adapter_start_contract.py`,
    `tests/test_api_run_control_adapter_start_contract.py` und
    `docs/migration/run_control_adapter_start_contract.md` beschreiben
    `GET /api/run-control/adapter-start-contract` ohne Start-Payload,
    POST-Startendpunkt, UI-Startbutton, Queue-Worker oder Simulation.
37. Queue-/Status-/Resultat-Persistenz fuer freigegebene Ausfuehrung
    vorbereiten. Dieser Schnitt ist umgesetzt:
    `python_port/ims/api/run_control_execution_result_store.py`,
    `tests/test_api_run_control_execution_result_store.py` und
    `docs/migration/run_control_execution_result_store.md` speichern nur vorab
    validierte Adapter-Resultate mit expliziter Persistenzfreigabe, weiterhin
    ohne Adapterstart, UI-Startbutton, Queue-Worker oder Simulation.
38. Run-Control-Ausfuehrungsflow in der Workbench anzeigen. Dieser Schnitt ist
    umgesetzt: `frontend/src/main.tsx`, `frontend/src/styles.css`,
    `tests/test_frontend_shell.py` und
    `docs/migration/run_control_execution_flow_ui.md` zeigen
    `Preflight -> explizite Freigabe -> Ausfuehren` nur als Statussicht,
    weiterhin ohne UI-Startbutton, Queue-Worker, Adapterstart oder Simulation.

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
- Demo-/Doku-Smoke fuer die read-only Carryover/Kern-Sicht ist umgesetzt;
- erster fachlicher VN-Carryover-Slice-Test ist geplant;
- erster fachlicher VN-Carryover-Slice-Test ist als Regressionstest umgesetzt;
- erster fachlicher Regressionstest ist dokumentiert und eingeordnet;
- 0 PRs bis zur demo-nahen read-only Carryover/Kern-Sicht;
- 0 PRs bis zum ersten ausgefuehrten fachlichen Regressionstest;
- 0 PRs bis zur geschaerften Einordnung dieses ersten fachlichen
  Regressionstests;
- zweiter fachlicher Slice ist als VN-Regelwirkung ueber explizite
  `best_info`-Snapshots geplant;
- zweiter fachlicher VN-Regel-Snapshot-Slice ist als Regressionstest
  umgesetzt und dokumentiert;
- 0 PRs bis zum zweiten ausgefuehrten fachlichen Regressionstest;
- dritter fachlicher Slice ist als VU-Carryover-Fixture geplant;
- dritter fachlicher VU-Carryover-Fixture-Slice ist als Regressionstest
  umgesetzt und dokumentiert;
- 0 PRs bis zum dritten ausgefuehrten fachlichen Regressionstest;
- Ausfuehrungsadapter-Vertrag ist als read-only DTO umgesetzt;
- 0 PRs bis zu einem read-only Ausfuehrungsadapter-Vertrag;
- lokaler kontrollierter Ausfuehrungsadapter ist umgesetzt;
- 0 PRs bis zu einem lokalen expliziten Adapter ohne API-/UI-Startpfad;
- read-only Adapter-Resultat fuer Run-Control ist geplant;
- 0 PRs bis zur Entscheidung fuer ein read-only Adapter-Resultat;
- read-only Adapter-Resultat-Vertrag ist umgesetzt;
- 0 PRs bis zu einem read-only Adapter-Resultat-Vertrag;
- read-only API-/UI-Anzeige fuer Adapter-Resultate ist geplant;
- read-only API-Vertrag fuer Adapter-Resultate ist umgesetzt;
- gesperrte UI-Karte fuer Adapter-Resultat-Vertrag ist umgesetzt;
- vierter fachlicher VN-`best_info`-/Carryover-Slice ist als Regressionstest
  umgesetzt und dokumentiert;
- 0 PRs bis zum vierten ausgefuehrten fachlichen Regressionstest;
- fuenfter fachlicher VN-`sample_search`-/Settlement-Slice ist als
  Regressionstest umgesetzt und dokumentiert;
- 0 PRs bis zum fuenften ausgefuehrten fachlichen Regressionstest;
- Run-Control-Ausfuehrungsfreigabeplan ist dokumentiert;
- API-Startvertrag fuer den kontrollierten Adapter ist hart gegated umgesetzt;
- Queue-/Status-/Resultat-Persistenz fuer freigegebene Ausfuehrung ist lokal
  vorbereitet;
- Run-Control-Ausfuehrungsflow in der Workbench ist umgesetzt;
- vorgeschlagener naechster Schritt ist PR 47:
  Ergebnisanzeige fuer freigegebene Adapterlaeufe anbinden,
  weiterhin ohne historische Vollgleichheitsbehauptung;
- danach grob 1 bis 3 reviewbare PRs bis zu einer benutzbaren kontrollierten
  Demo-Simulation;
- read-only Execution-Summary-Vertrag, Kernvalidierungsueberblick und
  Run-Control-Bruecke sind umgesetzt; offen bleiben nur spaetere echte
  Ausfuehrungsadapter nach separater Freigabe.

Damit bleiben grob ca. 6-16+ reviewbare PRs bis zu einem deutlich breiteren
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
