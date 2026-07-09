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
- `explicit_period_transition_diagnostics.md`: rein lesende Uebergangsdiagnose fuer vorhandene explizite Periodenplaene
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
- `fachlogik_migration_status.md`: Abschlussstand der kontrollierten Fachlogik-Migration im engeren Sinn mit Grenzen und Folgephasen
- `workbench_demo_checklist.md`: lokale Demo-Checkliste fuer Start, UI-Reihenfolge, Demo-Signale und Grenzen ohne Simulation
- weitere Mapping- und Verifikationsnotizen folgen in spaeteren PRs
