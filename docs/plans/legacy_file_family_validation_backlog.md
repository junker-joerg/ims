# Backlog weiterer Legacy-Dateifamilien

Diese Liste verhindert, dass einzelne gruene Agrsich-Slices als
Gesamtgleichheit des Modells missverstanden werden.

## Bereits angebunden

- Versicherer-Agrsich: `VU14L1.DAT`, `VUSK1L1.DAT` bis `VUSK1L5.DAT` als
  SK1-Zeitfenster auf derselben unterstuetzten Aggregatstufe
- VN-Agrsich: `IMSVNR01.DAT` bis `IMSVNR06.DAT`, `IMSVNSK1.DAT`,
  `IMSVNVK1.DAT` bis `IMSVNVK3.DAT`
- Versicherer-Klassenaggregate: `IMSVUVK1.DAT` bis `IMSVUVK3.DAT`

## Naheliegende naechste Kandidaten

- Schmale fachliche VU-/VN-Regel- oder Carryover-Slices aus vorhandenen
  Planfixtures, weil die naheliegenden Agrsich-Dateifamilien inzwischen
  versioniert und validiert sind.
- Parameterausgaben wie `VU014PR1.DAT` bleiben geparkt, bis eine belastbare
  Feldklaerung und eigene Parserentscheidung vorliegt.

## Neuer lokaler Kandidatenbestand

Unter `incomming/` liegt nun ein lokaler, nicht versionierter historischer
Kandidatenbestand. Details stehen in
`docs/plans/historical_testdata_inventory.md`. Der Bestand hebt mehrere bisherige
Referenzblocker fachlich auf, wird aber erst in separaten PRs gezielt nach
`tests/references/legacy_agrsich/` uebernommen.

Naechster bevorzugter Arbeitsschnitt:

- Keine Uebernahme von `VU014PR1.DAT`; der naechste groessere Schritt soll den
  geplanten VN-Carryover-Slice als ersten fachlichen Regressionstest
  vorbereiten.
  `VU014PR1.DAT` bleibt weiterhin geparkt; keine Simulation, keine automatische
  historische Regelwahl und keine Vollgleichheitsbehauptung.

## Aktuelle PR-Zaehlung

Nach PR 25 ist die demo-nahe, weiterhin read-only Carryover/Kern-Sicht
vorbereitet:

- PR 22: Carryover-Probe im Kernvalidierungsueberblick als Ergebnisvertrag
  einordnen, ohne Probe aus dem Overview heraus zu starten (erledigt).
- PR 23: Read-only API-Vertrag fuer bereits berechnete Carryover-Probe-Ergebnisse
  vorbereiten, ohne Schreibpfad und ohne Runner-Start (erledigt).
- PR 24: UI-Karte fuer die bereits berechnete Carryover-Probe-Sicht vorbereiten,
  ohne Startbutton oder Ausfuehrungsadapter (erledigt).
- PR 25: Demo-/Doku-Smoke fuer die read-only Carryover/Kern-Sicht ergaenzen
  (erledigt).

Danach bleiben mindestens 3 weitere fachliche Validierungs-PRs offen:

- die Umsetzung des geplanten VN-Carryover-Slices als Regressionstest;
- die Schaerfung der fachlichen Assertions und Dokumentation dieses Slices;
- ein separater Plan fuer einen spaeteren kontrollierten Ausfuehrungsadapter.

Zaehlschnitt: 0 PRs bis zur demo-nahen read-only Carryover/Kern-Sicht; 3+
PRs bis zu einem breiteren fachlichen Anschluss. Diese Zahl ist kein
Vollgleichheits- oder Gesamtabschlussversprechen.

Der erste echte fachliche Regressionstest ist nach PR 28 ausgefuehrt und
eingeordnet:

- PR 27: VN-Carryover-Slice aus
  `replay_vn_policyholder_transition_plan.json` als gezielten Regressionstest
  ausfuehren (erledigt:
  `tests/test_first_fachlicher_vn_carryover_regression.py`).
- PR 28: Assertions und Dokumentation fuer diesen Slice schaerfen, weiterhin
  ohne historische Vollgleichheitsbehauptung (erledigt:
  `docs/migration/first_fachlicher_regressionstest.md`).

Bis zur geschaerften Einordnung dieses ersten fachlichen Regressionstests
bleiben nach PR 28 noch 0 PRs.

Naechster bevorzugter fachlicher Schnitt:

- PR 29: zweiten schmalen Slice waehlen (erledigt:
  `docs/plans/second_fachlicher_slice_test_plan.md`). Gewaehlt ist eine
  VN-Regelwirkung ueber explizite `best_info`-Snapshots fuer Policyholder `21`,
  Versicherer `11/12` und Periode `5`. Auch dieser Schnitt bleibt ohne
  Simulation und ohne historische Vollgleichheitsbehauptung.
- PR 30: geplanten VN-Regel-Snapshot-Slice als zweiten fachlichen
  Regressionstest umsetzen und dokumentieren (erledigt:
  `tests/test_second_fachlicher_vn_rule_snapshot_regression.py` und
  `docs/migration/second_fachlicher_regressionstest.md`).

Bis zum zweiten ausgefuehrten fachlichen Regressionstest bleiben nach PR 30
noch 0 PRs.

Der dritte fachliche Slice ist nach PR 31 geplant:

- PR 31: VU-Carryover-Fixture fuer Versicherer `10` von lokaler Periode `2`
  nach `3` als naechsten schmalen Regressionstest waehlen (erledigt:
  `docs/plans/third_fachlicher_slice_test_plan.md`).
- PR 32: geplanten VU-Carryover-Fixture-Slice als dritten fachlichen
  Regressionstest umsetzen und dokumentieren (erledigt:
  `tests/test_third_fachlicher_vu_carryover_regression.py` und
  `docs/migration/third_fachlicher_regressionstest.md`).

Bis zum dritten ausgefuehrten fachlichen Regressionstest bleiben nach PR 32
noch 0 PRs.

Der naechste groessere Schnitt ist nach PR 33 geplant:

- PR 33: schmalen kontrollierten Ausfuehrungsadapter-Vertrag nach drei
  fachlichen Regressionstests planen (erledigt:
  `docs/plans/controlled_execution_adapter_plan.md`).
- PR 34: read-only Ausfuehrungsadapter-Vertrag als DTO und Vertragstest
  vorbereiten, weiterhin ohne Runner-Start (erledigt:
  `python_port/ims/api/controlled_execution_adapter_contract.py`,
  `tests/test_api_controlled_execution_adapter_contract.py` und
  `docs/migration/controlled_execution_adapter_contract.md`).

Bis zu einem read-only Ausfuehrungsadapter-Vertrag bleiben nach PR 34 noch 0 PRs.

Der lokale Adapter-Schnitt ist nach PR 35 umgesetzt:

- PR 35: lokalen Adapter fuer explizite Fixture-Ausfuehrung umsetzen, nur mit
  explizitem Freigabeflag und ohne API-/UI-Startpfad (erledigt:
  `python_port/ims/api/controlled_execution_adapter.py`,
  `tests/test_api_controlled_execution_adapter.py` und
  `docs/migration/controlled_execution_adapter.md`).

Bis zu einem lokalen expliziten Adapter ohne API-/UI-Startpfad bleiben nach PR 35 noch 0 PRs.

Der naechste Run-Control-Anschluss ist nach PR 36 geplant:

- PR 36: entscheiden, ob Run-Control den lokalen Adapter nur als read-only
  Resultat anzeigen darf oder ob zuerst ein weiterer schmaler fachlicher Slice
  folgt (erledigt: gewaehlt ist ein read-only Adapter-Resultat,
  `docs/plans/run_control_adapter_result_plan.md`).

Bis zur Entscheidung fuer ein read-only Adapter-Resultat bleiben nach PR 36 noch
0 PRs.

Der read-only Adapter-Resultat-Vertrag ist nach PR 37 umgesetzt:

- PR 37: Read-only Adapter-Resultat-DTO oder Vertrag vorbereiten, weiterhin
  ohne Adapterstart aus Run-Control (erledigt:
  `python_port/ims/api/run_control_adapter_result_contract.py`,
  `tests/test_api_run_control_adapter_result_contract.py` und
  `docs/migration/run_control_adapter_result_contract.md`).

Bis zu einem read-only Adapter-Resultat-Vertrag bleiben nach PR 37 noch 0 PRs.

Der read-only API-Vertrag fuer Adapter-Resultate ist nach PR 39 umgesetzt:

- PR 38: read-only API-/UI-Anzeige fuer Adapter-Resultate planen, weiterhin
  ohne Browser-Upload, Dateiauswahl, Startbutton oder Adapterstart
  (`docs/plans/run_control_adapter_result_view_plan.md`).
- PR 39: read-only API-Vertrag fuer vorab lokal gepruefte Adapter-Resultate,
  weiterhin ohne Upload, HTTP-Validierung oder Adapterstart
  (`python_port/ims/api/run_control_adapter_result_api_contract.py`,
  `tests/test_api_run_control_adapter_result_api_contract.py` und
  `docs/migration/run_control_adapter_result_api_contract.md`).

Die gesperrte UI-Karte fuer den Adapter-Resultat-Vertrag ist nach PR 40 umgesetzt:

- PR 40: gesperrte UI-Karte fuer den Adapter-Resultat-Vertrag anzeigen,
  weiterhin ohne Upload, Dateiauswahl, Startbutton oder Ausfuehrungsfreigabe
  (`frontend/src/main.tsx`, `frontend/src/styles.css` und
  `tests/test_frontend_shell.py`).

Der vierte fachliche VN-Slice ist nach PR 41 umgesetzt:

- PR 41: `best_info`-Wirkung plus VN-State-Carryover ueber zwei explizite
  Perioden pruefen, weiterhin ohne neue Folgeperioden-Snapshots, ohne
  Simulation und ohne Vollgleichheitsbehauptung
  (`tests/test_fourth_fachlicher_vn_best_info_carryover_regression.py` und
  `docs/migration/fourth_fachlicher_regressionstest.md`).

Der fuenfte fachliche VN-Slice ist nach PR 42 umgesetzt:

- PR 42: `sample_search` / Vrvn05 plus Schaden-/Settlement-Runner-Grenze
  pruefen, weiterhin mit expliziten Draws, ohne Simulation und ohne
  Vollgleichheitsbehauptung
  (`tests/test_fifth_fachlicher_vn_sample_search_regression.py` und
  `docs/migration/fifth_fachlicher_regressionstest.md`).

Aktueller Stand nach PR 48:

- PR 48: Demo-Smoke und Doku fuer den benutzbaren Ablauf,
  weiterhin ohne historische Vollgleichheitsbehauptung (dieser Schnitt:
  `tests/test_workbench_demo_smoke.py` und
  `docs/migration/workbench_demo_checklist.md`, erledigt).

Aktueller Stand nach PR 49:

- PR 49: Packaging-/Startskript-Haertung fuer die lokale Auslieferung,
  weiterhin ohne Simulation, Adapterstart oder Vollgleichheitsbehauptung
  (dieser Schnitt: Repo- und portable Start-/Check-Skripte, erledigt).

Vorgeschlagener naechster Schritt nach PR 49:

- PR 50: Produktionsreife-Roadmap festschreiben und wieder einen schmalen
  fachlichen Validierungsslice waehlen, weil der lokale Demo- und
  Packaging-Pfad jetzt reviewbar stabilisiert ist (dieser Schnitt:
  `docs/plans/production_readiness_pr_plan.md` und
  `docs/plans/sixth_fachlicher_slice_test_plan.md`).

## Rest-PR-Planung

- PR 1: `IMSVNR01.DAT` und `IMSVNR02.DAT` uebernehmen und validieren
  (erledigt).
- PR 2: `IMSVNR03.DAT` und `IMSVNR04.DAT` uebernehmen und validieren
  (erledigt).
- PR 3: `IMSVNR06.DAT` uebernehmen; `IMSVNR05.DAT` mit der Gesamtfamilie
  abgleichen (erledigt).
- PR 4: Coverage-/Next-Family-Plan so aktualisieren, dass `policyholder_rule`
  nach vollstaendiger IMSVNR-Abdeckung als covered erscheint (erledigt).
- PR 5: VN-Klassenaggregate `IMSVNVK*.DAT` vorbereiten und validieren
  (erledigt; `policyholder_class` ist im Bundle belegt).
- PR 6: Versicherer-Klassenaggregate `IMSVUVK*.DAT` vorbereiten und validieren
  (erledigt; `insurer_class` ist im Bundle belegt).
- PR 7: Parameterausgaben wie `VU014PR1.DAT` nur nach eigener Feldklaerung
  vorbereiten (erledigt: Inventar, verwandte lokale Kandidaten und Altcode-Spur
  dokumentiert; Feldmapping bleibt offen, keine Referenzuebernahme).
- PR 8: `VU014PR1.DAT` nur wieder aufnehmen, wenn eine historische
  Schreibstelle oder ein belastbares Feldmapping fuer `Pr1L1` bis `Pr1L5`
  vorliegt; dann eigener Parser und gezielte Tests.
- PR 9: Naechsten Kernlogik-Schnitt aus den vorhandenen Planfixtures waehlen
  (erledigt: stabile Execution-Summary fuer ausgefuehrte explizite
  VU/VN-Mehrperiodenlaeufe, ohne Simulation und ohne automatische historische
  Regelwahl).
- PR 10: Execution-Summary-Vertrag im `ims_core_validation_overview` read-only
  planen und dokumentieren (erledigt; keine Ausfuehrung aus dem Overview
  heraus).
- PR 11: Read-only API-/UI-Anbindung fuer den Kernvalidierungsueberblick
  vorbereiten, damit die UI den Demo-Status ohne Laufstart anzeigen kann
  (erledigt).
- PR 12: Read-only Brueckenplan fuer Run-Control-Aktionsplan und
  Kernlauf-Diagnosen dokumentieren und als kleines Python-DTO vorbereiten,
  ohne neuen Endpunkt, Schreibpfad oder Runner-Start (erledigt).
- PR 13: Optional eine rein lesende API-Anbindung fuer das Bruecken-DTO
  vorbereiten; weiterhin ohne UI-Startpfad und ohne Ausfuehrungsadapter
  (erledigt).
- PR 14: Optional eine rein lesende UI-Karte fuer die Bruecken-Antwort
  vorbereiten; weiterhin ohne Startbutton, Upload oder Ausfuehrungsadapter
  (erledigt).
- PR 15: Bruecken-Demo-/Screenshot-Smoke optional aktualisieren, wenn ein
  visueller Beleg fuer die neue Karte gebraucht wird (erledigt).
- PR 16: Naechsten schmalen fachlichen VU-/VN-Regel- oder Carryover-Slice aus
  vorhandenen Planfixtures planen: Altcode-Spur, Fixture-Bezug, erwartete
  Zwischenzustaende und Testgrenzen unter
  `docs/plans/explicit_period_transition_slice.md` dokumentieren, noch ohne neue Fachlogik.
  Periodenuebergangs-/Carryover-Grenze fuer `VU14L1.DAT` und `VUSK1L4.DAT` (erledigt).
- PR 17: Explizite Periodenuebergangs-/Carryover-Diagnose aus dem Plan
  vorbereiten, weiterhin ohne Runner-Start, Simulation oder automatische
  historische Regelwahl (erledigt).
- PR 18: Kleines VN-Policyholder- oder Carryover-Anschlussfixture planen, damit
  `explicit_period_transition_no_policyholders` gezielt aufgeloest oder als
  weiterhin offene Grenze bestaetigt wird (dieser Schnitt:
  `replay_vn_policyholder_transition_plan.json`).
- PR 19: Engen Carryover-Code-Slice aus dem Anschlussfixture planen oder
  vorbereiten, weiterhin ohne historische Regelableitung und ohne
  Vollsimulation (dieser Schnitt: Carryover-Kandidatenlisten in der
  Uebergangsdiagnose, keine Carryover-Ausfuehrung).
- PR 20: Echten Carryover-Code-Slice separat planen oder vorbereiten, dabei
  weiterhin nur vorhandene portierte Carryover-Bausteine nutzen und keine
  historische Regelableitung einfuehren (dieser Schnitt:
  `docs/plans/explicit_transition_carryover_code_slice.md`, noch keine
  Carryover-Ausfuehrung).
- PR 21: Den geplanten engen Carryover-Probe als Code-/Test-Schritt umsetzen:
  nur explizites Opt-in, nur vorhandene portierte Carryover-Bausteine,
  Uebergangsdiagnose als Grenzpruefung, keine API-/UI-/Run-Control-Anbindung
  (dieser Schnitt: `ims.engine.explicit_transition_carryover_probe`, erledigt).
- PR 22: Carryover-Probe im Kernvalidierungsueberblick als read-only Vertrag
  aufnehmen, aber keinen Probe-Start aus dem Overview heraus einfuehren
  (dieser Schnitt: `explicit_transition_carryover_probe_contract`, erledigt).
- PR 23: Read-only API-Vertrag fuer bereits berechnete Probe-Ergebnisse
  vorbereiten (dieser Schnitt:
  `GET /api/core-validation/carryover-probe-contract`, erledigt).
- PR 24: UI-Karte fuer die bereits berechnete Carryover-Probe-Sicht
  vorbereiten (dieser Schnitt: `Carryover-Probe-Vertrag` in der Workbench,
  erledigt).
- PR 25: Demo-/Doku-Smoke fuer die read-only Carryover/Kern-Sicht ergaenzen
  (dieser Schnitt: `carryover-probe-contract` im Demo-Smoke, erledigt).
- PR 26: Ersten fachlichen VN-Carryover-Slice-Test planen
  (dieser Schnitt: `docs/plans/first_fachlicher_slice_test_plan.md`).
- PR 27: Den geplanten VN-Carryover-Slice als fachlichen Regressionstest
  ausfuehren, nur ueber vorhandene portierte Probe-/Carryover-Bausteine
  (dieser Schnitt: `tests/test_first_fachlicher_vn_carryover_regression.py`,
  erledigt).
- PR 28: Assertions und Dokumentation fuer den ersten fachlichen
  Regressionstest schaerfen, ohne Vollgleichheitsbehauptung (dieser Schnitt:
  `docs/migration/first_fachlicher_regressionstest.md`, erledigt).
- PR 29: Zweiten schmalen fachlichen Slice auswaehlen, vorzugsweise
  VU-Carryover oder VN-Regelwirkung ueber explizite Snapshots (dieser Schnitt:
  VN-Regelwirkung ueber explizite `best_info`-Snapshots, erledigt).
- PR 30: Geplanten VN-Regel-Snapshot-Slice als zweiten fachlichen
  Regressionstest umsetzen und dokumentieren (dieser Schnitt:
  `tests/test_second_fachlicher_vn_rule_snapshot_regression.py`, erledigt).
- PR 31: Optional weiteren VN-Regel-Snapshot oder VU-Carryover-Fixture planen,
  falls der Review mehr fachliche Breite vor einer Run-Control-Planung
  verlangt (dieser Schnitt: VU-Carryover-Fixture geplant, erledigt).
- PR 32: Geplanten VU-Carryover-Fixture-Slice als dritten fachlichen
  Regressionstest umsetzen und dokumentieren (dieser Schnitt:
  `tests/test_third_fachlicher_vu_carryover_regression.py`, erledigt).
- PR 33: Danach entscheiden, ob ein weiterer VN-/VU-Regel-Snapshot oder ein
  schmaler Ausfuehrungsadapterplan fachlich sinnvoller ist (dieser Schnitt:
  Ausfuehrungsadapter-Vertrag geplant, erledigt).
- PR 34: Read-only Ausfuehrungsadapter-Vertrag vorbereiten, weiterhin ohne
  Runner-Start, API-/UI-Startpfad oder Queue-Worker (dieser Schnitt:
  `tests/test_api_controlled_execution_adapter_contract.py` und
  `docs/migration/controlled_execution_adapter_contract.md`, erledigt).
- PR 35: Optional lokalen Adapter fuer explizite Fixture-Ausfuehrung umsetzen,
  nur nach separater Freigabe und ohne API-/UI-Startpfad (dieser Schnitt:
  `tests/test_api_controlled_execution_adapter.py` und
  `docs/migration/controlled_execution_adapter.md`, erledigt).
- PR 36: Entscheiden, ob Run-Control den lokalen Adapter nur als read-only
  Resultat anzeigen darf oder ob zuerst ein weiterer schmaler fachlicher Slice
  folgt (dieser Schnitt: read-only Adapter-Resultat geplant, erledigt).
- PR 37: Read-only Adapter-Resultat-DTO oder Vertrag vorbereiten, weiterhin
  ohne Adapterstart aus Run-Control (dieser Schnitt:
  `tests/test_api_run_control_adapter_result_contract.py` und
  `docs/migration/run_control_adapter_result_contract.md`, erledigt).
- PR 38: Read-only API-/UI-Anzeige fuer das Adapter-Resultat planen,
  weiterhin ohne Upload, Dateiauswahl, Startbutton oder Adapterstart
  (erledigt).
- PR 39: Optional read-only API-Vertrag oder Endpunkt fuer ein vorab
  bereitgestelltes Adapter-Resultat vorbereiten, weiterhin ohne Upload und
  ohne Adapterstart (dieser Schnitt:
  `tests/test_api_run_control_adapter_result_api_contract.py` und
  `docs/migration/run_control_adapter_result_api_contract.md`, erledigt).
- PR 40: Optional UI-Karte fuer diesen Vertrag anzeigen, weiterhin ohne
  Upload, Dateiauswahl, Startbutton oder Ausfuehrungsfreigabe (dieser Schnitt:
  `frontend/src/main.tsx`, `frontend/src/styles.css` und
  `tests/test_frontend_shell.py`, erledigt).
- PR 41: Schmalen fachlichen VN-`best_info`-/Carryover-Slice ausfuehren und
  dokumentieren (dieser Schnitt:
  `tests/test_fourth_fachlicher_vn_best_info_carryover_regression.py` und
  `docs/migration/fourth_fachlicher_regressionstest.md`, erledigt).
- PR 42: Schmalen fachlichen VN-`sample_search`-/Settlement-Slice ausfuehren
  und dokumentieren (dieser Schnitt:
  `tests/test_fifth_fachlicher_vn_sample_search_regression.py` und
  `docs/migration/fifth_fachlicher_regressionstest.md`, erledigt).
- PR 43: Expliziten Run-Control-Ausfuehrungsfreigabeplan vorbereiten, bevor ein
  benutzbarer Startpfad freigeschaltet wird (dieser Schnitt:
  `docs/plans/run_control_execution_release_plan.md`, erledigt).
- PR 44: API-Startvertrag fuer den kontrollierten Adapter hart gegated
  vorbereiten (dieser Schnitt:
  `python_port/ims/api/run_control_adapter_start_contract.py`,
  `tests/test_api_run_control_adapter_start_contract.py` und
  `docs/migration/run_control_adapter_start_contract.md`, erledigt), weiterhin
  ohne POST-Start, UI-Button oder Queue-Worker.
- PR 45: Queue-/Status-/Resultat-Persistenz fuer freigegebene Ausfuehrung
  anbinden (dieser Schnitt:
  `python_port/ims/api/run_control_execution_result_store.py`,
  `tests/test_api_run_control_execution_result_store.py` und
  `docs/migration/run_control_execution_result_store.md`, erledigt), weiterhin
  ohne Adapterstart, UI-Button oder Queue-Worker.
- PR 46: UI-Flow Preflight -> explizite Freigabe -> Ausfuehren anzeigen
  (dieser Schnitt: `frontend/src/main.tsx`, `frontend/src/styles.css`,
  `tests/test_frontend_shell.py` und
  `docs/migration/run_control_execution_flow_ui.md`, erledigt), weiterhin
  ohne UI-Startbutton, Queue-Worker, Adapterstart oder Simulation.
- PR 47: Ergebnisanzeige fuer freigegebene Adapterlaeufe anbinden
  (dieser Schnitt: `python_port/ims/api/app.py`, `frontend/src/main.tsx`,
  `frontend/src/styles.css`, `tests/test_api_run_control_execution_result_store.py`,
  `tests/test_frontend_shell.py` und
  `docs/migration/run_control_execution_result_view.md`, erledigt), weiterhin
  ohne Upload, UI-Startbutton, Queue-Worker, Adapterstart oder Simulation.
- PR 48: Demo-Smoke und Doku fuer den benutzbaren Ablauf (dieser Schnitt:
  `tests/test_workbench_demo_smoke.py` und
  `docs/migration/workbench_demo_checklist.md`, erledigt).
- PR 49: Packaging-/Startskript-Haertung fuer die lokale Auslieferung (dieser
  Schnitt: Repo- und portable Start-/Check-Skripte, erledigt).
- PR 50: Produktionsreife-Roadmap und sechsten fachlichen Slice waehlen
  (dieser Schnitt: Vrvn04 / `search_history` als Plan fuer PR 51).
- PR 51: sechsten fachlichen VN-`search_history`-/Vrvn04-Slice als
  Regressionstest umsetzen und dokumentieren (dieser Schnitt:
  `tests/test_sixth_fachlicher_vn_search_history_regression.py` und
  `docs/migration/sixth_fachlicher_regressionstest.md`, erledigt).
- PR 52: siebten fachlichen VN-`preference`-/Vrvn03-Slice planen und umsetzen
  (dieser Schnitt: `tests/test_seventh_fachlicher_vn_preference_regression.py`
  und `docs/migration/seventh_fachlicher_regressionstest.md`, erledigt).
- PR 53: VN-`random`-/Vrvn02-Slice mit expliziten Draws und Seed-/Draw-Grenze
  als schmalen Regressionstest umsetzen (dieser Schnitt:
  `tests/test_eighth_fachlicher_vn_random_regression.py` und
  `docs/migration/eighth_fachlicher_regressionstest.md`, erledigt).
- PR 54: VN-Schaden-/Settlement-Pfad aus `Vrvn01` bis `Vrvn03` breiter gegen
  vorhandene explizite Fixtures pruefen (dieser Schnitt:
  `tests/test_ninth_fachlicher_vn_damage_settlement_breadth.py` und
  `docs/migration/ninth_fachlicher_regressionstest.md`, erledigt).
- PR 55: VU-Regelbreite ergaenzen, vorzugsweise ein expliziter VU-Random- oder
  VU-Markup-Slice mit Draw-/Carryover-Grenze (dieser Schnitt:
  `tests/test_tenth_fachlicher_vu_random_carryover_regression.py` und
  `docs/migration/tenth_fachlicher_regressionstest.md`, erledigt).
- PR 56: Produktions-Altdatenkorpus als Plan fixieren und fuer die erste
  Freigabe Ein-/Ausschluss, Herkunft, Header, Periodenfenster und Parsergrenzen
  dokumentieren (dieser Schnitt:
  `docs/plans/production_legacy_corpus_plan.md`, erledigt); `incomming/` bleibt
  unversioniert.
- PR 57: ausschliesslich `IMSVU014.DAT` und `IMSVUSK1.DAT` aus ZINS000 als
  getrennte Referenzschicht pruefen; keine Ersetzung der Baseline und kein
  Sammelimport (erledigt; versioniert unter
  `tests/references/legacy_agrsich/zins000/`).
- PR 58: berechneten kontrollierten Mehrperiodenvergleich fuer den
  19-Dateien-Kernkorpus als strikten Vertrag fuer 15 extern gelieferte
  Exporttabellen vorbereiten; ZINS000 nur separat waehlbar halten (erledigt).
- PR 59: ersten read-only Abweichungsbericht anbinden; fehlende berechnete
  Kernexporte blockierend und Legacy-Echo-Tabellen unzulaessig halten
  (erledigt; 15 blockierende Kerninputluecken).
- PR 60: ersten schmalen, tatsaechlich berechneten Output aus einem vorhandenen
  expliziten Mehrperiodenpfad anbinden; Modellkorrekturen weiter sperren, bis
  eine konkrete Abweichung belegt ist (erledigt: VU14 Perioden `1-4`, nur
  Aggregation/Export aus referenzausgerichteten Snapshots).
- PR 61: Level-IV-Selektormetadaten `all` und `SK1` technisch kanonisieren;
  VUSK1 bleibt ein `SK1`-/`all`-Aggregat auf Stufe IV (erledigt).
- PR 62: kontrollierte Run-Control-Ausfuehrungsfreigabe fuer den lokalen
  Adapter vorbereiten; keine Erweiterung der historischen Gleichheitsaussage
  (read-only Freigabecheck erledigt).
- PR 63: atomare Backend-Start-, Status- und Ergebnisgrenze gegen Doppelstarts
  schaffen; noch kein UI-Startbutton (erledigt).

Zaehlschnitt nach PR 63: grob `7-13` reviewbare PRs bis zu konservativer
Produktionsreife mit validiertem Altdaten-Korpus und laufender UI; 0 weitere
Pflicht-PRs bis zu einer startbar
verpackten kontrollierten Demo; der lokale benutzbare Ablauf ist als
API-/Doku-Smoke und Startskriptgrenze abgesichert. Das bleibt kein historischer
Vollgleichheitsnachweis.

Restgrenze fuer alle Folge-PRs: weiterhin ohne Vollgleichheitsbehauptung.

Naechster Schnitt ist PR 64: kontrollierte UI-Anbindung an den atomaren
Backend-Start, mit expliziter Freigabe und Idempotenz, weiterhin ohne
Queue-Worker oder freien Browser-Upload.

PR 64 ist erledigt. Neuer Zaehlschnitt: grob `6-12` reviewbare PRs bis zur
konservativen Produktionsreife. PR 65 stabilisiert als naechstes
Ergebnisverlauf, Fehlerzustaende und erneute Ergebnisanzeige, weiterhin ohne
automatische Wiederholung oder Erweiterung der historischen Gleichheitsaussage.

PR 65 ist erledigt. Neuer Zaehlschnitt: grob `5-11` reviewbare PRs bis zur
konservativen Produktionsreife. PR 66 prueft als naechstes den explizit
freigegebenen lokalen Demo-Run im Browser, weiterhin ohne Erweiterung des
Altdatenkorpus oder historische Vollgleichheitsbehauptung.

PR 66 ist erledigt. Der isolierte Browser-Smoke nutzt einen injizierten
Fake-Adapter und erweitert weder Altdatenkorpus noch Gleichheitsaussage. Neuer
Zaehlschnitt: grob `4-10` reviewbare PRs bis zur konservativen
Produktionsreife. PR 67 haertet als naechstes Packaging, Staging und
Startskripte fuer den sichtbar geprueften Demo-Stand.

PR 67 ist erledigt. Die Release-Checkliste `pr67-v1`, das lokale ZIP, das
portable Staging und der normale Produktionsstart sind getrennt vom
PR-66-Fake-Adapter geprueft. Neuer Zaehlschnitt: grob `3-9` reviewbare PRs bis
zur konservativen Produktionsreife. PR 68 prueft als naechstes Backup/Restore
und Update/Rollback lokaler Metadaten mit validiertem Ergebnisstand.

PR 68 ist erledigt. Die technische Recovery-Probe sichert und restauriert den
validierten Ergebnisstand ueber fuenf SQLite-Tabellen und prueft getrennte
Repo-/Portable-Anwendungspfade, ohne Simulation oder Schemamigration. Neuer
Zaehlschnitt: grob `2-8` reviewbare PRs bis zur konservativen Produktionsreife.
PR 69 erstellt als naechstes den Abschlussbericht fuer den ersten
Produktionsfreigabekorpus.

PR 69 ist erledigt. Der read-only Bericht `pr69-v1` trennt 19/19 abgedeckte
Referenzen und 6.300 eingetragene Perioden von den 15 weiterhin fehlenden
berechneten Kernexporten; eine fachliche Produktionsfreigabe wird nicht
erteilt. Neuer Zaehlschnitt: grob `1-7` reviewbare PRs, zuzueglich der externen
Datenvoraussetzung. PR 70 haertet als naechstes die technische CI-/Windows-
Pruefkette.

PR 70 ist erledigt. Das lokale PowerShell-Gate und GitHub Actions pruefen den
Python-Satz, Frontend-Build, blockierten Korpusbericht, ZIP/Staging und
Release-Smoke unter Windows. Damit bleiben `0` technische Pflicht-PRs fuer die
eingefrorene Pruefkette.

PR 71 ist erledigt. Die Herkunfts- und Erzeugungswegkarte ordnet alle 15
Kernexportidentitaeten den 19 Referenzzielen, historischen Agrsich-Ankern und
zwei gemeinsamen Python-Zustandsfamilien zu. Writer und expliziter Runner sind
fuer alle Identitaeten angeschlossen; unabhaengig erzeugte Vollfenster bleiben
`0/15`.

PR 72 ist erledigt. Der Vertrag `pr72-v1` friert fuer `imsvu014.dat` genau
Stufe I, VU 14, Perioden `1-100`, sechs Herkunftsgruppen und die Sperre gegen
Legacy-/Output-Echos ein. PR 73 hat VU14 an `Vdefmd6` gebunden, die zuvor
kuenstliche Referenz durch die dreifach belegte historische Reihe ersetzt und
Periode 1 unabhaengig in 14/14 Feldern bestaetigt. PR 74 hat die
25-VU-/200-VN-Population typisiert aufgebaut. PR 75 hat die wirksamen
Aktionsslots und moderne Seed-Policy lesend gebunden. PR 76 hat danach die
VU14-Vorschock-Regelprojektion klassifiziert und den fehlenden VN-/Schaden-/
Settlement-Pfad belegt. PR 77 ist nun mit sechs Regelabbildungen, 150 aktiven
Vorschock-VN und der explizit offenen historischen Draw-Reihenfolge erledigt.
PR 78 hat darauf 150 VN-Regel- und 150 Schaden-Snapshots fuer eine einzelne
Vorschockperiode materialisiert. PR 79 hat die 25 VU-Snapshots und
BAV-Vorperiodeninputs geschlossen. PR 80 hat die Informationskosten angewendet
und VU14/1-49 mit 236/686 Feldtreffern klassifiziert. PR 81 hat Schockgrenze,
50 spaete VN und VU14/1-100 mit 488/1.400 Feldtreffern geschlossen. PR 82 hat
SK1/all und die drei VU-Klassen fuer 1-100 mit 898/5.600 Feldtreffern
klassifiziert. Nach PR 82 waren vier reviewbare PRs bis PR 86 offen; die
historische VU-Klassenakkumulatorsemantik ist als eigener Blocker dokumentiert.
PR 83 hat anschliessend `imsvnr01.dat` bis `imsvnr03.dat` fuer Perioden 1-100
mit 946/3.900 Feldtreffern klassifiziert. Danach bleiben mindestens drei
reviewbare PRs bis PR 86; VN-Regelakkumulator und `Ev`-Feldbedeutung sind offen.
PR 84 hat anschliessend `imsvnr04.dat` bis `imsvnr06.dat` mit 926/3.900
Feldtreffern und 326/3.300 Fachwerttreffern klassifiziert. Danach bleiben zwei
reviewbare PRs bis PR 86; die konkrete `WVEMOD1`-Laufidentitaet ist ebenfalls
offen. PR 85 hat danach `imsvnvk1.dat` bis `imsvnvk3.dat` und `imsvnsk1.dat`
mit 1.234/5.200 Feldtreffern beziehungsweise 434/4.400 Fachwerttreffern
klassifiziert. Danach bleibt ein reviewbarer PR bis PR 86; die historische
VN-Klassenakkumulatorsemantik und die Laufidentitaet bleiben offen. PR 86 hat
alle 15 Kernexportidentitaeten fuer 1-100 gemeinsam durch den bestehenden
Abweichungsbericht gefuehrt. 4.492/20.000 Felder und 1.492/17.000 Fachwerte
treffen; die Empfehlung bleibt `keep_blocked`. Damit ist die vorab geplante
PR-72- bis PR-86-Serie abgeschlossen. Weitere Slices werden aus den offenen
Provenienz- und Kompatibilitaetsfragen neu abgeleitet.

## Validierungsregel

Jede Dateifamilie bekommt:

- echte Referenzdatei im Testbestand,
- Parser mit whitespace-robustem Headervergleich,
- mindestens eine positive Alignment-Zeile,
- mindestens einen Negativtest,
- Dokumentation der noch nicht validierten Bereiche.
