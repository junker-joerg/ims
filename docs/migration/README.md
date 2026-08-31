# Migration IMS/ESS -> Python

Dieses Verzeichnis buendelt die fachliche und technische Dokumentation fuer die kontrollierte Migration des historischen IMS/ESS-Codes nach Python.

## Grundsaetze

- Die Migration erfolgt schrittweise und PR-basiert.
- Fachliche Semantik hat Vorrang vor syntaktischer Naehe zum C-Code.
- Historische UI-/Terminallogik wird nicht priorisiert portiert.
- Jede nichttriviale Portierung soll auf den Altcode zurueckgefuehrt werden koennen.
- Unsicherheiten werden ausdruecklich dokumentiert.

## Reihenfolge der Migration

1. Bestandsaufnahme des Altcodes
2. Zielarchitektur fuer Python
3. Technisches Grundgeruest
4. Scheduler- und Zeitlogik
5. Zustandscontainer / Entitaeten
6. RNG / Reproduzierbarkeit
7. Erste fachliche Slices
8. Regressionstests gegen Referenzszenarien

## Dokumente in diesem Verzeichnis

- `ims_inventory.md`: Inventar und grobe Klassifikation der Altdateien
- `python_target_architecture.md`: geplante Zielstruktur des Python-Ports
- `legacy_agrsich_validation_step.md`: erster echter Versicherer-Agrsich-Vergleich
- `legacy_vn_validation_step.md`: erster echter VN-Agrsich-Vergleich
- `legacy_agrsich_multi_period_step.md`: mehrperiodiger Rahmen fuer validierte Agrsich-Legacy-Vergleiche
- `agrsich_replay_runner.md`: deterministischer Mehrperioden-Replay-Runner mit Legacy-Fenstervergleich
- `vu_replay_legacy_targets.md`: mehrere Legacy-Ziele fuer deterministische VU-Agrsich-Replay-Laeufe
- `agrsich_replay_plan.md`: deterministische Replay-Snapshot-Erzeugung aus Startzustand plus expliziten Periodenupdates
- `agrsich_validation_report.md`: maschinenlesbarer Report, rein lesender Ueberblick und Coverage-Matrix fuer Agrsich-Legacy-Fenstervergleiche
- `bav_frmdinf_sector_vectors.md`: sparten- und risikogetrennte BAV-Fremdinformationen
- `vu_foreign_info_rule_core.md`: kleiner VU-Regelkern fuer Dumping-, Durchschnitts- und Angriffslogik auf BAV-Frmdinf-Vektoren
- `vu_foreign_info_period_runner.md`: kleiner deterministischer Periodenschritt fuer BAV-Frmdinf plus explizite VU-Regelparameter-Snapshots
- `vu_global_period_order.md`: globale Periodenfolge im expliziten VU-Mehrperiodenrunner
- `explicit_vu_vn_period_runner.md`: gemeinsame explizite Periodenstrecke fuer VU-Regeln und VN-Schaden-/Abrechnung
- `explicit_period_transition_diagnostics.md`: rein lesende Uebergangsdiagnose und enger In-Memory-Carryover-Probe fuer vorhandene explizite Periodenplaene
- `explicit_period_legacy_targets.md`: optionale Legacy-Ziele fuer gemeinsame explizite VU/VN-Periodenlaeufe
- `explicit_vu_vn_period_plan.md`: deterministischer Periodenplan fuer gemeinsame explizite VU/VN-Laeufe
- `explicit_period_plan_legacy_targets.md`: Legacy-Ziele im deterministischen expliziten VU/VN-Periodenplan
- `period_plan_input_validation.md`: kontrollierte Validierung von Entity-Update-Listen in Periodenplaenen
- `period_plan_context_overrides.md`: explizite Kontext-Overrides fuer Periodenplaene
- `vu_free_linear_rule.md`: Vrvu10-Slice fuer frei definierbare lineare VU-Fortschreibung
- `vn_damage_core.md`: gemeinsamer VN-Schadenerzeugungskern aus Vrvn01 bis Vrvn03
- `vn_damage_draw_basis.md`: reproduzierbare Python-Draw-Basis fuer VN-Schadensnapshots ohne explizite Draws
- `vn_compulsory_insurance_rule.md`: Vrvn01-Baustein fuer Pflichtversicherung und Startentscheidungen
- `vn_random_insurance_rule.md`: Vrvn02-Baustein fuer zufaelligen VN-Versicherungsstatus und aktive VU-Auswahl
- `vn_preference_insurance_rule.md`: Vrvn03-Baustein fuer Praeferenzwahl nach aktiver VU-Werbung
- `vn_search_insurance_rule.md`: Vrvn04-Baustein fuer Suchwahl nach frueheren VN-Praemien
- `vn_sample_search_insurance_rule.md`: Vrvn05-Baustein fuer Stichprobensuche nach aktuellen VU-Praemien
- `vn_best_info_insurance_rule.md`: Vrvn06-Baustein fuer beste Information ueber aktive aktuelle VU-Praemien
- `vn_insurance_rule_dispatch.md`: expliziter Dispatch fuer portierte VN-Versicherungsregel-Snapshots
- `vn_settlement_core.md`: deterministischer VN-Abrechnungskern nach expliziten Entscheidungen
- `vn_damage_settlement_link.md`: explizite Kopplung von VN-Schadenerzeugung und VN-Abrechnung
- `vn_explicit_damage_period.md`: expliziter Periodenpfad fuer VN-Schaden plus VN-Abrechnung
- `vn_multi_period_runner.md`: deterministischer Mehrperiodenrunner fuer explizite VN-Szenarien
- `vn_state_carryover.md`: optionaler Zustandstransfer fuer explizite VN-Mehrperiodenlaeufe
- `vn_snapshot_target_integrity.md`: Integritaetsvalidierung fuer disjunkte VN-Snapshot-Ziele
- `vn_agrsich_replay.md`: Agrsich-Export aus expliziten VN-Periodenlaeufen
- `vn_agrsich_legacy_targets.md`: optionale Legacy-Ziele fuer VN-Agrsich-Replay
- `vn_agrsich_replay_plan.md`: deterministische VN-Replay-Snapshot-Erzeugung aus Startzustand plus expliziten Periodenupdates
- `vn_period_plan_legacy_targets.md`: Legacy-Ziele im deterministischen VN-Agrsich-Periodenplan
- `vn_rule_family_imsvnr.md`: Vorbereitung der historischen VN-Regelfamilie `IMSVNR01.DAT` bis `IMSVNR06.DAT`
- `vn_class_family_imsvnvk.md`: Vorbereitung der historischen VN-Klassenaggregate `IMSVNVK1.DAT` bis `IMSVNVK3.DAT`
- `insurer_class_family_imsvuvk.md`: Vorbereitung der historischen Versicherer-Klassenaggregate `IMSVUVK1.DAT` bis `IMSVUVK3.DAT`
- `parameter_output_vu014pr1.md`: Inventar und offene Feldklaerung fuer die historische Parameterausgabe `VU014PR1.DAT`
- `zins000_reference_layer.md`: getrennte historische Referenzschicht fuer `IMSVU014.DAT` und `IMSVUSK1.DAT` ohne Erweiterung des Kernbundles
- `calculated_legacy_multi_period_contract.md`: strikter PR-58-Eingangsvertrag fuer berechnete Mehrperiodenergebnisse ohne Legacy-Selbstvergleich oder Simulation
- `calculated_legacy_deviation_report.md`: read-only PR-59-Diagnose fuer Inputblocker, exakte Treffer, tolerierte Zahlenunterschiede und offene Feldfragen
- `explicit_vu14_calculated_deviation_slice.md`: erster PR-60-Adapter von vier explizit berechneten VU14-Aggregat-/Exportperioden zur read-only Legacy-Diagnose
- `level_iv_selector_canonicalization.md`: enge PR-61-Kanonisierung der technischen Level-IV-Selektorwerte `all` und `SK1` ohne Aenderung von Aggregatstufe oder Fachlogik
- `fachlogik_migration_status.md`: Abschlussstand der kontrollierten Fachlogik-Migration im engeren Sinn mit Grenzen und Folgephasen
- `workbench_demo_checklist.md`: lokale Demo-Checkliste fuer Start, UI-Reihenfolge, Demo-Signale und Grenzen ohne Simulation
- `fourth_fachlicher_regressionstest.md`: vierter schmaler fachlicher Test fuer VN-`best_info`-Wirkung plus VN-State-Carryover ueber zwei explizite Perioden
- `fifth_fachlicher_regressionstest.md`: fuenfter schmaler fachlicher Test fuer VN-`sample_search` / Vrvn05 plus Schaden-/Settlement-Runner-Grenze
- `sixth_fachlicher_regressionstest.md`: sechster schmaler fachlicher Test fuer VN-`search_history` / Vrvn04 plus Schaden-/Settlement-Runner-Grenze
- `seventh_fachlicher_regressionstest.md`: siebter schmaler fachlicher Test fuer VN-`preference` / Vrvn03 plus Schaden-/Settlement-Runner-Grenze
- `eighth_fachlicher_regressionstest.md`: achter schmaler fachlicher Test fuer VN-`random` / Vrvn02 plus explizite Draw- und Schaden-/Settlement-Runner-Grenze
- `ninth_fachlicher_regressionstest.md`: neunter fachlicher Test fuer breitere VN-Schaden-/Settlement-Kopplung aus `Vrvn01` bis `Vrvn03`
- `tenth_fachlicher_regressionstest.md`: zehnter fachlicher Test fuer `Vrvu01` / Zufall I mit zwei expliziten Draw-Vektoren und kontrollierter Carryover-Opt-in-Grenze
- `run_control_adapter_start_contract.md`: Entwicklung des hart gegateten Startvertrags von der read-only Vorbereitung bis zur atomaren Backend-Grenze
- `run_control_execution_release_check.md`: read-only PR-62-Freigabecheck mit Auditfeldern, validierter Queue, gruenem Preflight und serverseitigem lokalem Fixture-Profil ohne Adapterstart
- `run_control_atomic_adapter_start.md`: atomarer PR-63-Backendstart mit Idempotenz, Statuswechseln und Ergebnisablage, weiterhin ohne UI-Button, Queue-Worker oder Simulation
- `run_control_execution_result_store.md`: kontrollierte lokale Persistenzgrenze fuer vorab validierte Adapter-Resultate, Queue-Status `result_persisted` und weiterhin ohne Adapterstart oder Simulation
- `run_control_execution_flow_ui.md`: Entwicklung der Workbench-Karte von der read-only Statussicht bis zum zweistufig freigegebenen PR-64-UI-Start, weiterhin ohne Queue-Worker, Upload oder Simulation
- `run_control_execution_result_view.md`: read-only API- und Workbench-Ergebnisanzeige fuer persistierte Run-Control-Adapterresultate, weiterhin ohne Upload, Adapterstart, Queue-Worker oder Simulation
- `run_control_execution_history.md`: read-only PR-65-Verlauf fuer vorhandene Adapterstart-Audit-, Zeit- und Fehlerdaten ohne Retry, Queue-Worker oder Simulation
- `run_control_browser_demo_smoke.md`: isolierter PR-66-Browser-Smoke fuer Freigabe, Fake-Adapterstart, persistiertes Ergebnis und Verlauf ohne Engine-Runner oder Simulation
- `workbench_release_checklist.md`: eingefrorener PR-67-Vertrag `pr67-v1` fuer ZIP, portables Staging und normalen Produktionsstart ohne Demo-Adapter oder Simulation
- `workbench_metadata_recovery.md`: PR-68-Probe fuer SQLite-Backup, Restore und Side-by-Side-Update/Rollback eines validierten lokalen Ergebnisstands
- `production_release_corpus_report.md`: PR-69-Abschlussbericht mit 19-/6.300-Korpus, technischen Betriebsnachweisen und weiterhin 15 fehlenden berechneten Kernexporten
- `windows_release_gate.md`: PR-70-Windows-Gate fuer Python-Tests, Frontend-Build, blockierten Korpusbericht, ZIP/Staging und Release-Smoke
- `calculated_export_provenance_map.md`: PR-71-Karte der 15 Kernexportidentitaeten mit C-/Python-Ankern, zwei Zustandsfamilien und offenen Vollfensterluecken
- `vu14_100_period_generation_contract.md`: PR-72-Abnahmevertrag fuer den unabhaengigen VU14-Zustandsweg ueber Perioden `1-100` ohne Exporterzeugung oder Vollgleichheitsbehauptung
- `vu14_vdefmd6_source_binding.md`: PR-73-Quellenbindung fuer VU14/`Vrvu06`, korrigierte historische Referenz und unabhaengige Perioden-1-Probe
- `vdefmd6_population_builder.md`: PR-74-Builder fuer die typisierte 25-VU-/200-VN-Ausgangspopulation mit konservativer VN-Gruppengrenze
- `vdefmd6_action_seed_contract.md`: PR-75-Vertrag fuer 200 wirksame Aktionsslots und eine explizite moderne Seed-Policy ohne Ausfuehrungs- oder historische RNG-Gleichheitsbehauptung
- `vdefmd6_pre_shock_snapshot_contract.md`: PR-78-Vertrag fuer 150 VN-Regel- und 150 Schaden-Snapshots einer Vorschockperiode mit expliziter moderner Drawfolge
- `vdefmd6_vu_snapshot_contract.md`: PR-79-Vertrag fuer 25 VU-Snapshots, BAV-Vorperiodeninputs und die belegte offene Informationskostenanwendung
- `vdefmd6_pre_shock_run_contract.md`: PR-80-Vertrag fuer Informationskosten und den kontrollierten VU14-Vollzustand der Perioden 1-49
- `vdefmd6_100_period_run_contract.md`: PR-81-Vertrag fuer Schockgrenze,
  Aktivierung der spaeten VN und kontrollierten VU14-Vollzustand 1-100
- `vdefmd6_vu_aggregate_run_contract.md`: PR-82-Vertrag fuer SK1/all und die
  drei VU-Klassenaggregate mit offener historischer Akkumulatorsemantik
- `vdefmd6_vn_rule_group_1_run_contract.md`: PR-83-Vertrag fuer
  `imsvnr01.dat` bis `imsvnr03.dat` mit klassifizierten Abweichungen und
  offener VN-Regelakkumulator-/`Ev`-Feldgrenze
- `vdefmd6_vn_rule_group_2_run_contract.md`: PR-84-Vertrag fuer
  `imsvnr04.dat` bis `imsvnr06.dat` mit Fachwertzaehlung und offener
  `WVEMOD1`-Laufidentitaet
- `vdefmd6_vn_aggregate_run_contract.md`: PR-85-Vertrag fuer die drei
  VN-Klassen und VN-SK1/all mit klassifizierten Abweichungen und offener
  historischer Klassenakkumulatorsemantik
- `vdefmd6_core_export_review.md`: PR-86-Gesamtbewertung aller 15
  Kernexportidentitaeten fuer Perioden 1-100 mit Abweichungsklassen,
  Vollfenstergrenze und Empfehlung `keep_blocked`
- `historical_archive_run_metadata.md`: PR-90-Auswertung des einzigen
  direkten `IMSREPOR.DAT`, sechs Archive ohne Laufmetadaten und die gesperrte
  archivuebergreifende Seed-/Parameteruebertragung
- `vu14_pre_shock_projection.md`: PR-76-Projektion fuer VU14/Perioden 1-49 mit Regeltreffern bis 16 und offenem VN-/Schaden-/Settlement-Pfad
- weitere Mapping- und Verifikationsnotizen folgen in spaeteren PRs
