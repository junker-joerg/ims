# Strategie und Entscheidungsvorlagen

Dieses Verzeichnis enthaelt fachliche Zielbilder und Entscheidungsvorlagen
fuer die Weiterentwicklung von IMS. Die IMS-2.x-Empfehlung wurde am
2026-09-01 angenommen und ist damit Grundlage fuer PR102. Der technische Migrationsstand ist unter
`ims-legacy-baseline-2026-09-01` eingefroren; PR103 beginnt die aktive
IMS-2.x-Alpha-Linie mit dem dokumentierten Modul- und Paketaudit.
Die Kandidatenfolge in der damaligen Entscheidungsvorlage war noch keine aktive PR-Roadmap;
die anschliessende Planung hat sie inzwischen ab PR103 konkretisiert.

- [PR102 und Zielbild IMS 2.x](pr102_ims_2x_direction_recommendation.md):
  angenommene Entscheidung zum Abschluss des historischen 6.300-Zeilen-Vergleichs und zur
  Ausrichtung von IMS 2.x als ausbaubare Versicherungsmarkt-
  Simulationsplattform.
- [PR103 Modul- und Paketaudit](../plans/ims_2x_module_package_audit.md):
  gemessener Python-Bestand, Zielpakete und Schutzgrenzen fuer den Aufbau der
  Strategie-, Bilanz- und Regulierungsschichten.
- [PR104 Strategiekatalog](../migration/ims_2x_strategy_catalog.md):
  versionierter read-only Vertrag fuer alle historischen VU-/VN-Regeln,
  moderne Familien, Parameterfaehigkeit und Teststatus.
- [PR105 Strategiekatalog in der Workbench](../migration/ims_2x_strategy_catalog_ui.md):
  rein lesender API- und Anzeigeweg fuer den Katalog, weiterhin ohne
  Strategieauswahl, Parameterbearbeitung oder Ausfuehrung.
- [PR106 Strategiezuordnungs- und Parametervertrag](../migration/ims_2x_strategy_assignment_contract.md):
  Akteurs-, Sektor- und Parametergrenzen sowie die belegten
  Vdefmd6-Zuordnungsprofile, weiterhin ohne Bearbeitung oder Ausfuehrung.
- [PR107 Strategiezuordnungen in der Workbench](../migration/ims_2x_strategy_assignment_ui.md):
  rein lesende Tabs fuer Vdefmd6-Quellprofile und vorhandene
  Parameterschemata, weiterhin ohne konkrete Werte, Schreiben oder
  Ausfuehrung.
- [PR108 Strategiezuordnungsentwurf](../migration/ims_2x_strategy_assignment_draft.md):
  versioniertes Format fuer konkrete Strategie- und Parameterentwuerfe mit
  zustandsloser Validierung, weiterhin ohne Speicherung, Snapshot-Uebersetzung
  oder Ausfuehrung.
- [PR109 Strategieentwurf in der Workbench](../migration/ims_2x_strategy_assignment_draft_ui.md):
  lokaler Formular- und Pruefpfad fuer einzelne VU-/VN-Zuordnungen, weiterhin
  ohne Speicherung, Snapshot-Uebersetzung oder Ausfuehrung.
- [PR110 Snapshot-Bauplaene](../migration/ims_2x_strategy_assignment_snapshot_translation.md):
  deterministische Zuordnung gueltiger Entwuerfe zu vorhandenen
  VU-/VN-Regel-Snapshottypen mit typisierten Parametern und explizit offenen
  Laufzeitfeldern, weiterhin ohne Defaults, Materialisierung oder Ausfuehrung.
- [PR111 Snapshot-Bauplaene in der Workbench](../migration/ims_2x_strategy_assignment_snapshot_translation_ui.md):
  read-only Vorschau fuer einen erfolgreich geprueften lokalen Entwurf mit
  vorbereiteten und offenen Snapshotfeldern, weiterhin ohne Speicherung,
  Materialisierung oder Ausfuehrung.
- [PR112 Snapshot-Kontextvertrag](../migration/ims_2x_strategy_assignment_snapshot_context.md):
  versionierter Einperiodenkontext fuer Ziehungen, Zins, Schock-, Markt- und
  Vorperiodenwerte mit zustandsloser Validierung, weiterhin ohne Defaults,
  Materialisierung oder Ausfuehrung.
- [PR113 Snapshot-Kontext in der Workbench](../migration/ims_2x_strategy_assignment_snapshot_context_ui.md):
  lokaler Editor fuer Periode und offene Bauplanwerte mit feldbezogener
  PR112-Pruefung, weiterhin ohne Speicherung, Materialisierung oder
  Ausfuehrung.
- [PR114 Materialisierungsvertrag](../migration/ims_2x_strategy_assignment_snapshot_materialization_contract.md):
  read-only Merge- und Loadervertrag mit neun fachlich geklaerten,
  verschachtelten VN-Kontextformen und periodenabhaengigen Anforderungen,
  weiterhin ohne Snapshot-Erzeugung, Runner oder Simulation.
- [PR115 Materialisierungseingang validieren](../migration/ims_2x_strategy_assignment_snapshot_materialization_validation.md):
  atomare serverseitige Pruefung der regelabhaengigen VN-Kontextformen,
  Fallbacks und Periodenbedingungen, weiterhin ohne Snapshot-Erzeugung,
  Runner oder Simulation.
- [PR116 VN-Snapshots materialisieren](../migration/ims_2x_strategy_assignment_snapshot_materialization.md):
  atomare Erzeugung typisierter VN-Regel-Snapshots aus einem vollstaendig
  gueltigen Einperiodenkontext, weiterhin ohne Speicherung, Runner oder
  Simulation.
- [PR117 VN-Snapshots in der Workbench](../migration/ims_2x_strategy_assignment_snapshot_materialization_ui.md):
  rein lesende Vorschau der vollstaendig materialisierten VN-Snapshots mit
  fachlich gruppierten Werten, weiterhin ohne Speicherung, Runner oder
  Simulation.
- [PR118 VU-Snapshot-Materialisierungsbestand](../migration/ims_2x_strategy_assignment_vu_snapshot_materialization_contract.md):
  getrennte read-only Bestandsaufnahme der zehn VU-Strategien, acht
  Snapshottypen, offenen Laufzeitfelder und externen Zustaende, weiterhin
  ohne Eingabevalidierung, Materialisierung, Runner oder Simulation.
- [PR119 VU-Materialisierungseingang](../migration/ims_2x_strategy_assignment_vu_snapshot_materialization_validation.md):
  versionierter Eingang und atomare Pruefung mit belegten Schwellenquellen,
  expliziten Ziehungen und gesperrten technischen Fallbacks, weiterhin ohne
  Snapshot-Erzeugung, Speicherung, Runner oder Simulation.
- [PR120 VU-Zustand und Herkunft](../migration/ims_2x_strategy_assignment_vu_snapshot_state_validation.md):
  versionierter Zustandsbeleg und atomarer Abgleich von Periodenwerten,
  Anspruchsprofilen, Bestand `t-2` und aktiver VN-Zahl, weiterhin ohne
  Snapshot-Erzeugung, Speicherung, Runner oder Simulation.
- [PR121 VU-Snapshots materialisieren](../migration/ims_2x_strategy_assignment_vu_snapshot_materialization.md):
  atomare Erzeugung aller zehn VU-Strategien in acht vorhandene Snapshottypen
  nach erfolgreicher Herkunftspruefung, weiterhin ohne Speicherung,
  Regelanwendung, Runner oder Simulation.
- [PR122 VU-Snapshots in der Workbench](../migration/ims_2x_strategy_assignment_vu_snapshot_materialization_ui.md):
  rein lesende Vorschau der vollstaendig materialisierten VU-Snapshots mit
  getrennt erfasstem Zustandsbeleg und sichtbarer Herkunftsgrenze, weiterhin
  ohne Speicherung, Regelanwendung, Runner oder Simulation.
- [PR123 gemeinsamer Ausfuehrungsanschluss](../plans/ims_2x_strategy_execution_connection_plan.md):
  Architektur- und Freigabeplan fuer einen unveraenderlichen, gehashten
  Einperioden-Ausfuehrungskandidaten aus VU-/VN-Snapshots, Marktgrundzustand
  und VN-Prozesseingaben; noch ohne Vertragscode, Speicherung oder Runner.
- [PR124 Vertrag fuer den Ausfuehrungskandidaten](../migration/ims_2x_strategy_execution_candidate_contract.md):
  versionierter read-only Vertrag fuer Pflichtabschnitte, Quellversionen und
  elf `LoadedScenario`-Sammlungen; Kandidatenbau, Speicherung, Run-Control und
  Runner bleiben gesperrt.
- [PR125 Kandidateneingang validieren](../migration/ims_2x_strategy_execution_candidate_validation.md):
  zustandslose atomare Pruefung eines gemeinsamen Entwurfs und Kontexts, der
  VU-Herkunft, einer lokalen Profilreferenz und expliziter VN-Prozesswerte;
  weiterhin ohne Kandidatenbau, Digest, Speicherung oder Runner.
- [PR126 Ausfuehrungskandidaten bauen](../migration/ims_2x_strategy_execution_candidate_build.md):
  serverseitige Aufloesung eines registrierten Marktgrundprofils, erneute
  VU-/VN-Materialisierung und kanonischer fluechtiger Kandidat samt
  SHA-256-Digest; weiterhin ohne Speicherung, Run-Control oder Runner.
- [PR127 Ausfuehrungskandidaten speichern](../migration/ims_2x_strategy_execution_candidate_store.md):
  explizit freizugebende, unveraenderliche SQLite-Ablage mit serverseitigem
  Neubau und wiederholter Digest-Pruefung; weiterhin ohne Run-Control,
  Runner oder Simulation.
- [PR128 Ausfuehrungskandidaten beobachten](../migration/ims_2x_strategy_execution_candidate_ui.md):
  rein lesende Workbench-Uebersicht fuer Reife, Herkunft, Digest und
  Speicherstatus mit erneuter Integritaetspruefung; weiterhin ohne Freigabe,
  Runner oder Simulation.
