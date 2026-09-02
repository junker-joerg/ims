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
