# Kontrollierter Ausfuehrungsadapter-Vertrag

## Zweck

Dieser PR 34 ergaenzt nur den read-only Vertrag fuer einen spaeteren
kontrollierten Ausfuehrungsadapter. Der Vertrag beschreibt, welche Eingaben ein
spaeterer lokaler Adapter annehmen darf und an welchen vorhandenen
Execution-Summary-Vertrag er sein Ergebnis binden muss.

Der Schnitt startet keinen Runner, keine Simulation, keinen Scheduler, keinen
HTTP-/UI-Startpfad und keinen Queue-Worker. Es gibt kein API-/UI-Startpfad-
Opt-in. Er fuehrt keine neue Fachlogik ein und erhebt keine historische Vollgleichheitsbehauptung.

## Ursprung und Mapping

| Ursprung / Anker | Neue Einordnung |
| --- | --- |
| `python_port/ims/engine/explicit_period_runner.py` | vorhandener expliziter VU/VN-Mehrperiodenrunner |
| `run_explicit_multi_period_from_fixture` | benannter spaeterer lokaler Runner-Anker, in diesem PR nicht ausgefuehrt |
| `build_explicit_multi_period_execution_summary` | erwarteter Summary-Builder fuer spaetere Adapterergebnisse |
| `ExplicitMultiPeriodExecutionSummary.to_dict()` | stabile Liste der erwarteten Output-Felder |
| `python_port/ims/api/controlled_execution_adapter_contract.py` | neuer beschreibender API-Vertrag ohne HTTP-Route |
| `tests/test_api_controlled_execution_adapter_contract.py` | Vertragstest fuer Eingaben, Grenzen, CLI und Schreibfreiheit |

## Vertragsinhalt

Der Vertrag meldet:

- `mode = "controlled_execution_adapter_contract"`;
- `adapter_mode = "explicit_multi_period_fixture_adapter"`;
- `expected_summary_mode = "explicit_multi_period_execution_summary"`;
- `source_runner = "ims.engine.explicit_period_runner.run_explicit_multi_period_from_fixture"`;
- `summary_builder = "ims.engine.explicit_period_runner.build_explicit_multi_period_execution_summary"`;
- erlaubte Fixture-Arten: `explicit_vu_vn_period_plan_fixture` und
  `explicit_multi_period_fixture`;
- erwartete Eingaben: `fixture_path`, `adapter_mode`,
  `explicit_execution_release`, `expected_summary_contract`,
  `carry_forward_vu_state`, `carry_forward_vn_state`;
- erwartete Summary-Felder aus `ExplicitMultiPeriodExecutionSummary.to_dict()`.

## Grenzen

Explizit verboten bleiben:

- Browser-Upload oder API-Request-Body als Startsignal;
- Queue-Ausfuehrungsanforderung;
- `execution_enabled=true` aus Queue-Metadaten;
- freie Output-Pfade;
- automatische historische Regelwahl;
- Legacy-Vollgleichheitserwartung;
- Runner-Start aus dem Vertrag;
- Simulation, Scheduler-Start, Queue-Worker, HTTP-Schreibendpunkt,
  UI-Startbutton, Metadaten-Schreibzugriff und Fachlogikmutation.

Die Flags bleiben entsprechend:

- `contract_only = true`;
- `http_enabled = false`;
- `ui_enabled = false`;
- `queue_worker_enabled = false`;
- `runner_start_enabled = false`;
- `writes_enabled = false`;
- `execution_enabled = false`;
- `writes_performed = false`;
- `execution_performed = false`;
- `simulation_performed = false`;
- `automatic_historical_rule_selection_performed = false`.

## Validierung

Der neue Test `tests/test_api_controlled_execution_adapter_contract.py` prueft:

- stabile JSON-Form und Modusfelder;
- erwartete Eingaben, Preconditions und Summary-Felder;
- verbotene Eingaben und Grenzen;
- CLI-Ausgabe ohne Schreibzugriff auf `.ims_workbench/metadata.sqlite`;
- Argumentablehnung beim direkten Modulaufruf.

Zusaetzlich sichert `tests/test_imports.py` den Paketimport.

## Offene Punkte

Der naechste moegliche PR 35 darf nur nach separater Freigabe einen lokalen,
explizit aufgerufenen Adapter bauen. Auch dieser Adapter bleibt zunaechst ohne
API-/UI-Startpfad, ohne Queue-Worker, ohne neue Fachlogik und ohne historische
Vollgleichheitsbehauptung.
