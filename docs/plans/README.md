# Plans

Dieses Verzeichnis ist für kleine, nachvollziehbare Arbeitspläne der IMS-Migration reserviert.
Hier sollen spätere PR-Schritte, offene Entscheidungen und Reihenfolgen dokumentiert werden.

- `ims_core_fachlogik_resume_plan.md`: IMS-Kern-Fachlogik nach Workbench-v1,
  mit konservativem Anschluss an vorhandene VU/VN-Periodenplaene und ohne
  neue Ausfuehrung.
- `run_control_core_diagnostics_bridge_plan.md`: Read-only Plan fuer eine
  spaetere Verbindung von Run-Control-Aktionsplan und Kernlauf-Diagnosen, ohne
  neuen Schreib- oder Ausfuehrungspfad.
- `explicit_period_transition_slice.md`: PR-16-Plan fuer den naechsten
  schmalen fachlichen Slice aus vorhandenen VU-Periodenfixtures, zunaechst nur
  als Periodenuebergangs- und Carryover-Grenze ohne neue Fachlogik.
- `explicit_transition_carryover_code_slice.md`: PR-20-Plan fuer den engen
  Carryover-Code-Slice aus vorhandenen expliziten Periodenfixtures, nur mit
  bestehenden portierten Carryover-Bausteinen und ohne historische
  Regelableitung.
- `first_fachlicher_slice_test_plan.md`: PR-26-Plan fuer den ersten fachlichen VN-Carryover-Slice-Test aus dem vorhandenen
  `replay_vn_policyholder_transition_plan.json`, weiterhin ohne Simulation und
  ohne Vollgleichheitsbehauptung.
- `second_fachlicher_slice_test_plan.md`: PR-29-Plan fuer den zweiten
  fachlichen Slice als VN-Regelwirkung ueber explizite `best_info`-Snapshots,
  weiterhin ohne Simulation und ohne Vollgleichheitsbehauptung.
- `third_fachlicher_slice_test_plan.md`: PR-31-Plan fuer den dritten
  fachlichen Slice als VU-Carryover-Fixture, weiterhin ohne Simulation und ohne
  Vollgleichheitsbehauptung.
- `production_readiness_pr_plan.md`: PR-50-Roadmap bis zur konservativen
  Produktionsreife mit validiertem Altdaten-Korpus, laufender UI und
  dokumentierten Abweichungsgrenzen.
- `production_legacy_corpus_plan.md`: PR-56-Festlegung des verpflichtenden
  19-Dateien-Kernkorpus mit 6.300 Vergleichszeilen, Ausschlussgrenzen und dem
  in PR 57 getrennt versionierten ZINS000-Paar; PR 58 bleibt der naechste
  berechnete Mehrperiodenvergleich und ist als strikter Eingangsvertrag
  umgesetzt; der read-only Abweichungsbericht aus PR 59 weist fuer den
  Kernkorpus 15 noch fehlende berechnete Exporte aus. PR 60 schliesst den
  ersten engen VU14-Aggregat-/Export-Slice fuer Perioden `1-4` an; PR 61
  kanonisiert die technische Level-IV-Selektorgrenze `all`/`SK1`. PR 62 setzt
  den read-only Run-Control-Freigabecheck um; PR 63 schliesst die atomare
  Backend-Start-/Status-/Ergebnisgrenze. PR 64 bindet den vorbereiteten UI-Flow
  kontrolliert an; PR 65 stabilisiert Ergebnisverlauf und Fehlerzustaende.
  PR 66 prueft den freigegebenen lokalen Demo-Run mit injiziertem Fake-Adapter
  im Browser. PR 67 friert Packaging-, Staging- und Produktionsstart-Smoke als
  Release-Checkliste `pr67-v1` ein; PR 68 prueft Backup/Restore und
  Update/Rollback lokaler Metadaten. PR 69 erstellt den Abschlussbericht fuer
  den ersten Produktionsfreigabekorpus; PR 70 haertet die technische CI-/
  Windows-Pruefkette. PR 71 kartiert alle 15 Kernexporte auf zwei gemeinsame
  Zustandsfamilien und offene Vollfensterluecken. PR 72 hat den read-only
  100-Perioden-Erzeugungsvertrag fuer `imsvu014.dat` vorbereitet; PR 73 hat
  die Quellenbindung, echte Referenz und unabhaengige Periode 1 ergaenzt;
  PR 74 baut die typisierte `Vdefmd6`-Population fuer 25 VU und 200 VN;
  PR 75 bindet deren wirksame Aktionsslots und moderne Seed-Policy read-only;
  PR 76 klassifiziert die unabhaengige VU14-Vorschock-Regelprojektion.
- `vdefmd6_population_builder_plan.md`: enger PR-74-Plan fuer die typisierte
  Ausgangspopulation ohne Scheduler-, RNG-, Schaden- oder Regelausfuehrung.
- `vdefmd6_action_seed_plan.md`: enger PR-75-Plan fuer wirksame Aktionsslots
  und explizite moderne Seed-Ableitung ohne Schedulerstart oder RNG-Ziehung.
- `vdefmd6_pre_shock_snapshot_plan.md`: PR-78-Plan fuer 150 explizite VN-
  Vorschock-Snapshots und die moderne Drawfolge ohne Runnerstart.
- `vdefmd6_vu_snapshot_plan.md`: PR-79-Plan fuer alle 25 VU-Snapshots,
  BAV-Vorperiodeninputs und die explizite Informationskostengrenze.
- `vdefmd6_pre_shock_run_plan.md`: PR-80-Plan fuer Informationskosten,
  kontrollierte Perioden 2-49 und die VU14-Abweichungsklassifikation.
- `vdefmd6_shock_run_plan.md`: PR-81-Plan fuer die Schockgrenze, Aktivierung
  der spaeten VN und die kontrollierten VU14-Perioden 50-100.
- `vdefmd6_vu_aggregate_run_plan.md`: PR-82-Plan fuer SK1/all und die drei
  VU-Klassenaggregate aus demselben kontrollierten 100-Perioden-Zustand.
- `vdefmd6_vn_rule_group_1_run_plan.md`: PR-83-Plan fuer die ersten drei
  VN-Regelaggregate mit offener historischer Akkumulator- und `Ev`-Feldgrenze.
- `vdefmd6_vn_rule_group_2_run_plan.md`: PR-84-Plan fuer die Regeln 4-6 mit
  zusaetzlicher offener `WVEMOD1`-Lauf- und Seed-Provenienz.
- `vdefmd6_vn_aggregate_run_plan.md`: PR-85-Plan fuer die drei VN-Klassen
  und VN-SK1/all mit getrennten historischen Akkumulatorgrenzen.
- `vdefmd6_core_export_review_plan.md`: PR-86-Abschlussplan fuer den
  gemeinsamen 1-100-Abweichungsbericht aller 15 Kernexportidentitaeten und
  die konservative Freigabeempfehlung `keep_blocked`.
- `historical_reference_provenance_and_full_window_plan.md`: PR-87-Plan fuer
  vier Provenienz-PRs, gestaffelte 100-/300-/500-Ergebniszeilen und den
  abschliessenden 6.300-Zeilen-Bericht ohne Vollgleichheitsbehauptung; PR 88
  hat das read-only Archivmanifest fuer sieben ZIPs umgesetzt, PR 89 die
  Referenz-zu-Archiv-Koharenzmatrix und PR 90 die archivlokale Auswertung von
  Laufmetadaten und Begleitdateien. PR 91 friert vier getrennte
  Referenzschichten fuer alle 19 Ziele ein; PR 92 setzt den Ergebniszeilenvertrag
  100/300/500 um. PR 93 bindet zwei vollstaendige 100-Perioden-Tabellen an
  den Korpusbericht. PR 94 erweitert den kontrollierten Zustand bis Periode
  300 mit exakt stabilem 100er-Prefix. PR 95 vergleicht die beiden
  300er-Regeltabellen `imsvnr01.dat` und `imsvnr02.dat` vollstaendig. PR 96
  erweitert den kontrollierten Zustand bis Periode 500. PR 97 bindet die
  VU-SK1-Tabelle an; PR 98 korrigiert alle 300/500-Zeilen-Vergleiche auf drei
  beziehungsweise fuenf unabhaengige Laeufe mit maximal 100 Perioden.
- `vu14_pre_shock_projection_plan.md`: PR-76-Plan fuer die unabhaengige
  VU14-Regelprojektion 1-49 und die konservative Downstream-Klassifikation.
- `workbench_metadata_recovery_plan.md`: enger PR-68-Plan fuer SQLite-Backup,
  Restore und Side-by-Side-Update/Rollback eines validierten Ergebnisstands,
  weiterhin ohne Simulation oder Schemamigration.
- `production_release_corpus_report_plan.md`: enger PR-69-Plan fuer den
  read-only Abschlussbericht, der technische Demo-Reife von der wegen 15
  fehlender berechneter Exporte blockierten Produktionsfreigabe trennt.
- `windows_release_gate_plan.md`: PR-70-Plan fuer die gemeinsame lokale und
  GitHub-Actions-Windows-Pruefkette ohne Server-, Adapter- oder
  Simulationsstart.
- `calculated_export_provenance_plan.md`: PR-71-Plan fuer die read-only
  Herkunfts- und Erzeugungswegkarte der 15 Kernexportidentitaeten.
- `vu14_generation_contract_plan.md`: PR-72-Plan fuer Zielidentitaet,
  Eingangsherkunft, Periodenfolge und Referenz-Echo-Grenze von
  `imsvu014.dat` fuer Perioden `1-100`.
- `vu14_source_binding_plan.md`: PR-73-Plan fuer `Vdefmd6`, die korrigierte
  historische VU14-Reihe und die unabhaengige Perioden-1-Probe.
- `workbench_release_smoke_plan.md`: enger PR-67-Plan fuer ZIP-, Staging- und
  Produktionsstart-Smoke mit harter Trennung vom PR-66-Fake-Adapter.
- `run_control_ui_start_plan.md`: enger PR-64-Plan fuer zweistufige
  Freigabepruefung und manuellen UI-Start ohne Queue-Worker oder Simulation.
- `run_control_execution_history_plan.md`: enger PR-65-Plan fuer read-only
  Attempt-Verlauf, Fehleranzeige und manuelles Neuladen ohne Retry oder
  Simulation.
- `run_control_browser_demo_smoke_plan.md`: enger PR-66-Plan fuer den
  sichtbaren Freigabe-, Fake-Adapterstart-, Ergebnis- und Verlaufspfad ohne
  Engine-Runner oder Simulation.
- `sixth_fachlicher_slice_test_plan.md`: PR-50-Auswahl des sechsten
  fachlichen Slice fuer Vrvn04 / `search_history`; die Testumsetzung ist
  separat in PR 51 umgesetzt.
- `../migration/sixth_fachlicher_regressionstest.md`: PR-51-Einordnung des
  sechsten fachlichen VN-Slices fuer `search_history` / Vrvn04 plus
  Schaden-/Settlement-Runner-Grenze, weiterhin ohne Simulation.
- `../migration/seventh_fachlicher_regressionstest.md`: PR-52-Einordnung des
  siebten fachlichen VN-Slices fuer `preference` / Vrvn03 plus
  Schaden-/Settlement-Runner-Grenze, weiterhin ohne Simulation.
- `../migration/eighth_fachlicher_regressionstest.md`: PR-53-Einordnung des
  achten fachlichen VN-Slices fuer `random` / Vrvn02 plus explizite Draw- und
  Schaden-/Settlement-Runner-Grenze, weiterhin ohne Simulation.
- `../migration/ninth_fachlicher_regressionstest.md`: PR-54-Einordnung des
  breiteren VN-Schaden-/Settlement-Slices fuer `Vrvn01` bis `Vrvn03`,
  weiterhin ohne Simulation.
- `../migration/tenth_fachlicher_regressionstest.md`: PR-55-Einordnung des
  VU-`Vrvu01`-/Zufall-I-Slices mit expliziten Draws und kontrollierter
  Carryover-Opt-in-Grenze, weiterhin ohne Simulation.
- `controlled_execution_adapter_plan.md`: PR-33 bis PR-35-Plan fuer Vertrag
  und lokalen schmalen Ausfuehrungsadapter nach drei fachlichen
  Regressionstests, weiterhin ohne API-/UI-Startpfad, Queue-Worker oder
  Vollgleichheitsbehauptung.
- `run_control_adapter_result_plan.md`: PR-36-Entscheidung fuer ein
  read-only Adapter-Resultat in Run-Control und PR-37-Vertrag, weiterhin ohne
  Adapterstart, Browser-Upload, Queue-Worker oder UI-Startpfad.
- `run_control_adapter_result_view_plan.md`: Vorschlag fuer PR 38 als
  read-only API-/UI-Anzeigeplanung fuer bereits lokal erzeugte
  Adapterresultate, weiterhin ohne Upload, Startbutton oder Adapterstart.
- `../migration/run_control_adapter_result_api_contract.md`: PR-39-API-Vertrag
  fuer `GET /api/run-control/adapter-result-contract`, weiterhin ohne
  Payload-Upload, HTTP-Validierung, Startbutton oder Adapterstart.
- `../migration/fourth_fachlicher_regressionstest.md`: PR-41-Einordnung des
  vierten fachlichen VN-Slices fuer `best_info`-Wirkung plus VN-State-Carryover,
  weiterhin ohne Simulation und ohne Vollgleichheitsbehauptung.
- `../migration/fifth_fachlicher_regressionstest.md`: PR-42-Einordnung des
  fuenften fachlichen VN-Slices fuer `sample_search` / Vrvn05 plus
  Schaden-/Settlement-Runner-Grenze, weiterhin ohne Simulation.
- `run_control_execution_release_plan.md`: PR-43-Plan fuer die explizite
  Run-Control-Ausfuehrungsfreigabe vor einem spaeter benutzbaren Startpfad,
  weiterhin ohne UI-Startbutton, Queue-Worker oder Simulation.
- `../migration/run_control_adapter_start_contract.md`: PR-44-Startvertrag
  fuer `GET /api/run-control/adapter-start-contract`, weiterhin ohne
  POST-Start, UI-Startbutton, Queue-Worker, Persistenz oder Simulation.
- `../migration/run_control_execution_result_store.md`: PR-45-Persistenzgrenze
  fuer vorab validierte Adapter-Resultate und Queue-Status
  `result_persisted`, weiterhin ohne Adapterstart, Queue-Worker oder
  Simulation.
- `../migration/run_control_execution_flow_ui.md`: PR-46-UI-Flow
  `Preflight -> explizite Freigabe -> Ausfuehren`, weiterhin ohne
  UI-Startbutton, Queue-Worker, Adapterstart oder Simulation.
- `../migration/run_control_execution_result_view.md`: PR-47-read-only
  Ergebnisanzeige fuer persistierte Run-Control-Adapterresultate, weiterhin
  ohne Upload, UI-Startbutton, Queue-Worker, Adapterstart oder Simulation.
