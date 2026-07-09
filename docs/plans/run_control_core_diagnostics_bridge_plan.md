# Plan: Read-only Run-Control-Anbindung an Kernlauf-Diagnosen

## Ziel

Dieser Plan beschreibt den naechsten kleinen Brueckenschritt zwischen
Run-Control-Aktionsplan und IMS-Kernvalidierungsueberblick. Er ist eine
Planungs- und Dokumentationsschicht: Es wird kein neuer HTTP-Endpunkt
eingefuehrt, kein Queue-Status veraendert, kein expliziter Periodenrunner
gestartet und keine Simulation ausgefuehrt.

Der spaetere Nutzen ist eine gemeinsame, read-only Sprache fuer die Frage:
Welche vorhandenen Kern-Diagnosen gehoeren zu einem vorgemerkten oder
validierten Run-Control-Eintrag, bevor ueberhaupt ein Ausfuehrungsadapter
freigegeben wird?

## Bestehende Ausgangspunkte

- Run-Control-Queue-Aktionsplan:
  `GET /api/run-control/queue/action-plan` und
  `python -m ims.api.run_control_queue_action_plan --db .\.ims_workbench\metadata.sqlite`.
- Kernvalidierungsueberblick:
  `GET /api/core-validation/overview` und
  `python -m ims.engine.core_validation_overview --legacy-fixture tests/fixtures/legacy_validation_bundle.json tests/fixtures/replay_vu14_period_plan.json tests/fixtures/replay_vusk1_period_plan.json`.
- Diagnose-Buendel fuer vorhandene explizite Periodenplaene:
  `python -m ims.engine.explicit_period_diagnostics_bundle tests/fixtures/replay_vu14_period_plan.json tests/fixtures/replay_vusk1_period_plan.json`.
- Execution-Summary-Vertrag:
  `build_explicit_multi_period_execution_summary` beschreibt nur bereits
  ausgefuehrte explizite Mehrperiodenergebnisse und wird hier nicht gestartet.

Aktueller Diagnosebefund fuer den lesenden Kernblick: 2 Planfixtures,
8 Perioden, globale Perioden `1, 2, 3, 4, 101, 102, 103, 104`,
19 Legacy-Referenzen, 6300 abgedeckte Zeilen und
`execution_performed = false`.

## Geplanter read-only Brueckenschnitt

Ein spaeterer kleiner PR darf einen rein lesenden Hilfsvertrag oder eine kleine
UI-Zusammenfassung vorbereiten. Dieser Vertrag wuerde vorhandene Antworten aus
Queue-Aktionsplan und Kernvalidierungsueberblick zusammen anzeigen, aber keine
neuen Fachentscheidungen treffen.

Moegliche Felder:

- `mode = "run_control_core_diagnostics_bridge"`
- `queue_id`
- `run_id`
- `scenario_id`
- `queue_status`
- `queue_next_action`
- `core_validation_status`
- `period_plan_count`
- `period_count`
- `global_periods`
- `legacy_reference_count`
- `execution_summary_available`
- `execution_summary_next_action`
- `bridge_next_action`
- `blocked_by`
- `writes_performed = false`
- `execution_performed = false`

Die Bruecke darf nur vorhandene Signale lesen. Sie darf nicht versuchen, aus
einem Queue-Eintrag automatisch ein Planfixture, eine historische Referenz oder
eine Fachregel abzuleiten, solange dieses Mapping nicht separat belegt ist.

## Konservative Aktionszuordnung

| Queue-/Kernsignal | Read-only Hinweis |
| --- | --- |
| Queue `planned` ohne Blocker | `inspect_core_validation_overview` oder `run_preflight` |
| Queue `validated` ohne Blocker | `await_execution_release`, keine Ausfuehrung |
| Kernueberblick `warning` mit `await_historical_reference` | `resolve_core_validation_blockers` |
| Keine Execution-Summary verfuegbar | `await_precomputed_execution_summary` |
| Unbekannter Queue-Status | `inspect_queue_status` |

Diese Hinweise bleiben Beschreibungen. Sie ersetzen weder Preflight noch
historische Fachvalidierung und schalten keinen Startpfad frei.

## Demo- und UI-Grenze

Die lokale Workbench darf Run-Control-Aktionsplan und Kernvalidierungsueberblick
nebeneinander oder in einer kleinen Lesebruecke anzeigen. Die Demo darf dadurch
besser erklaeren, warum nach `run_preflight` noch kein Ausfuehrungsadapter
aktiv ist.

Nicht erlaubt:

- kein neuer HTTP-Schreibpfad;
- kein Startbutton mit echter Funktion;
- kein Summary-Upload;
- kein Browser-Download;
- kein automatischer Lauf aus einem Queue-Eintrag;
- kein Start eines expliziten Periodenrunners;
- keine Simulation;
- keine neue Fachlogik;
- keine automatische historische Regelwahl;
- keine historische Vollgleichheitsbehauptung.

## PR-Reihenfolge

1. Dieser PR: Plan und Dokumentation fuer die read-only Bruecke, ohne Codepfad.
2. Danach optional: kleiner read-only Helper oder DTO, der vorhandene
   Queue-Aktionsplan- und Kernueberblick-Antworten zusammenfasst.
3. Danach optional: UI-Karte, die diese Zusammenfassung nur anzeigt.
4. Erst nach separater expliziter Freigabe: Planung eines echten
   Ausfuehrungsadapters, weiterhin als eigener PR und nicht als Nebeneffekt
   dieser Bruecke.

## Validierung

Dieser Plan wird ueber Dokumentationstests abgesichert. Die Tests pruefen, dass
die vorhandenen Lesepfade, die Diagnosezahlen und die harten Grenzen genannt
bleiben. Es wird keine Simulation gestartet.
