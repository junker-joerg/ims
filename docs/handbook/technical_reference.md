# Technische Quellen und Nachweise

Stand: 2026-09-01
Handbuchstand: HB2

Dieses Kapitel vermeidet doppelte Entwickleranleitungen. Es verweist auf die
versionierten Quellen, aus denen Installations-, Bedien- und
Validierungsaussagen des Benutzerhandbuchs abgeleitet sind.

## Workbench und Bedienpfad

- [Technischer Workbench-Vertrag](../migration/workbench_shell.md)
- [Lokale Demo-Checkliste](../migration/workbench_demo_checklist.md)
- [Kontrollierter Run-Control-Ausfuehrungsflow](../migration/run_control_execution_flow_ui.md)
- [Run-Control-Ergebnisanzeige](../migration/run_control_execution_result_view.md)
- [Run-Control-Ausfuehrungsverlauf](../migration/run_control_execution_history.md)

## Windows, Packaging und Recovery

- [Windows-Release-Gate](../migration/windows_release_gate.md)
- [Release-Checkliste](../migration/workbench_release_checklist.md)
- [Packaging-Plan](../migration/workbench_packaging_plan.md)
- [Metadaten-Backup, Restore und Rollback](../migration/workbench_metadata_recovery.md)
- [Windows-Skriptreferenz](../../scripts/workbench/README.md)

Diese Quellen belegen derzeit nur den lokalen Windows-Pfad. Linux bleibt bis
HB4 `not_verified`; iOS/Juno bleibt bis HB5 `feasibility_open`.

## Historische Validierung

- [Produktionskorpusbericht](../migration/production_release_corpus_report.md)
- [Provenienz- und Vollfensterplan](../plans/historical_reference_provenance_and_full_window_plan.md)
- [Referenzschicht-Vertrag](../migration/historical_reference_layer_contract.md)
- [Ergebniszeilenvertrag 100/300/500](../migration/historical_horizon_contract.md)
- [PR100: VN-Klassenlieferung](../migration/historical_500_period_vn_class_delivery.md)

Die Migrationsdokumente sind fuer Reviewer und Entwickler verbindlich. Das
Benutzerhandbuch uebersetzt ihren aktuellen Stand, ersetzt aber weder Tests
noch maschinenlesbare Vertraege.

## Installationsstatus

| Plattform | Handbuchstatus | Naechster Nachweis |
| --- | --- | --- |
| Windows | technischer Pfad belegt, Benutzerkapitel noch offen | HB3: frischer Kurzstart, Installation, Stop und Deinstallation |
| Linux | nicht verifiziert | HB4: Distribution, Shellpfad, Build, Health und Browser-Smoke |
| iOS/Juno | Machbarkeit offen | HB5: Browser-Client und lokale Juno-Ausfuehrung getrennt bewerten |

Die [Handbuchplanung](../plans/user_installation_handbook_plan.md) ist die
Quelle fuer Reihenfolge, Abnahme und verbleibenden Umfang.
