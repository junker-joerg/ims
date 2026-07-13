# Plan: Kontrollierter Ausfuehrungsadapter nach drei Fach-Slices

## Zweck

Dieser PR 33 legt den naechsten groesseren Schritt nach drei fachlichen
Regressionstests fest. Nach VN-Carryover, VN-`best_info`-Snapshot und
VU-Carryover-Fixture ist genug erste Fachbreite vorhanden, um den ersten
Ausfuehrungsadapter nur als kontrollierte Grenze zu planen.

Der Schnitt bleibt ein Plan-PR: Er fuehrt keinen Adaptercode ein, startet
keinen Periodenrunner, keine Simulation, keinen HTTP-/UI-Startpfad und behauptet
keine historische Vollgleichheit.

## Entscheidung

Gewaehlt wird ein schmaler Ausfuehrungsadapterplan statt eines weiteren
Regel-Snapshots.

Begruendung:

- Drei fachliche Regressionstests decken inzwischen je einen VN-Carryover-,
  VN-Regel- und VU-Carryover-Zwischenzustand ab.
- Der naechste Review-Schritt sollte klaeren, wie ein spaeterer Lauf
  kontrolliert gestartet und als Ergebnisvertrag eingeordnet werden darf.
- Ein weiterer Regel-Snapshot bleibt fachlich sinnvoll, wuerde aber die
  Ausfuehrungsgrenze nicht klaeren.

## Geplanter Adapterumfang

Der erste Adapter darf spaeter nur vorhandene explizite Fixture-Pfade und
bereits portierte Runner-Bausteine verwenden.

Erlaubter spaeterer Zielpfad:

- lokale, explizite Adapterfunktion oder CLI;
- kein API-/UI-Startpfad im ersten Adapter-PR;
- nur explizite VU/VN-Periodenfixtures;
- keine automatische historische Regelwahl;
- keine neue Fachregel;
- keine Queue-Ausfuehrung und kein Worker;
- Ergebnis nur als bestehender Execution-Summary-Vertrag, nicht als
  Vollgleichheitsnachweis.

Technische Anker:

- `python_port/ims/engine/explicit_period_runner.py`;
- `build_explicit_multi_period_execution_summary`;
- `python_port/ims/api/run_control_queue_action_plan.py`;
- `python_port/ims/api/run_control_core_diagnostics_bridge.py`;
- `docs/plans/run_control_core_diagnostics_bridge_plan.md`;
- `docs/migration/workbench_run_control_plan.md`.

## Umgesetzter Vertrag in PR 34

PR 34 bereitet den Ausfuehrungsadapter-Vertrag als read-only DTO vor:

- klare Adapter-Eingaben benennen, etwa Fixture-Pfad, Adaptermodus und
  explizite Freigabeflags;
- verbotene Eingaben benennen, etwa Browser-Upload, historische
  Regelautomatik, freie Output-Pfade und `execution_enabled=true` aus Queue-
  Metadaten;
- erwartete Output-Felder an den vorhandenen
  `explicit_multi_period_execution_summary`-Vertrag binden;
- weiter `execution_performed = false` in API, UI, Queue, Preflight,
  Aktionsplan und Kernblick-Bruecke;
- Dokumentation und Tests, aber keinen Runner-Start.

Umgesetzt sind:

- `python_port/ims/api/controlled_execution_adapter_contract.py`;
- `tests/test_api_controlled_execution_adapter_contract.py`;
- `docs/migration/controlled_execution_adapter_contract.md`.

Der Vertrag bindet spaetere Adapterergebnisse an
`explicit_multi_period_execution_summary`, meldet aber weiterhin
`runner_start_enabled = false`, `writes_enabled = false` und
`execution_performed = false`.

PR 35 kann danach einen lokalen, explizit aufgerufenen Adapter umsetzen, wenn
der Vertrag geprueft und separat freigegeben ist. Dieser spaetere Schritt
bleibt ohne API-/UI-Startpfad.

## Grenzen

- keine Simulation;
- kein Scheduler-Start;
- kein HTTP-/UI-Startpfad;
- kein Queue-Worker;
- keine Ausfuehrung aus Run-Control, API, UI oder Overview;
- keine neue Fachregel;
- keine automatische historische Regelwahl;
- keine Uebernahme weiterer historischer Referenzdateien;
- keine historische Vollgleichheitsbehauptung.

## Folgeplanung

- PR 34: read-only Ausfuehrungsadapter-Vertrag als DTO und Vertragstest
  umsetzen und dokumentieren (erledigt).
- PR 35: optional lokalen Adapter fuer explizite Fixture-Ausfuehrung umsetzen,
  nur nach separater Freigabe und ohne API-/UI-Startpfad.
- PR 36+: erst danach entscheiden, ob Run-Control den Adapter nur lesen,
  vormerken oder weiterhin blockieren soll.

## Validierung dieses Plan-/Vertragsstands

Dieser Stand wird ueber Dokumentationstests und den neuen Vertragstest
validiert. Er prueft die Entscheidung, die Grenzen, die naechsten PR-Schritte
und die stabile JSON-Form des read-only Vertrags.
