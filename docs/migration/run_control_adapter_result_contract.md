# Run-Control Adapter-Resultat-Vertrag

## Zweck

Dieser PR 37 ergaenzt nur den read-only Vertrag fuer ein bereits lokal
erzeugtes Adapterergebnis. Run-Control kann damit die erwartete Form eines
`controlled_execution_adapter`-JSON beschreiben und lokal validieren, startet
aber keinen Adapter.

Der Schnitt fuehrt keine neue Fachlogik ein, startet keine Simulation, keinen
Scheduler, keinen Runner, keinen Queue-Worker und keinen HTTP-/UI-Startpfad.

## Ursprung und Mapping

| Ursprung / Anker | Neue Einordnung |
| --- | --- |
| `python_port/ims/api/controlled_execution_adapter.py` | Quelle des vorab lokal erzeugten Resultats |
| `ControlledExecutionAdapterResult.to_dict()` | erwartete Top-Level-Form |
| `explicit_multi_period_execution_summary` | erwartete Summary-Form |
| `python_port/ims/api/run_control_adapter_result_contract.py` | neuer read-only Vertrag und lokaler Validator |
| `tests/test_api_run_control_adapter_result_contract.py` | Test fuer Vertrag, Validator und CLI-Grenzen |

## Vertragsinhalt

Der Vertrag meldet:

- `mode = "run_control_adapter_result_contract"`;
- `expected_result_mode = "controlled_execution_adapter"`;
- `expected_summary_mode = "explicit_multi_period_execution_summary"`;
- `precomputed_result_required = true`;
- `adapter_start_allowed = false`;
- `api_accepts_upload = false`;
- `http_enabled = false`;
- `ui_enabled = false`;
- `queue_worker_enabled = false`;
- `writes_enabled = false`;
- `execution_enabled = false`;
- `execution_performed = false`.

Der Validator akzeptiert nur ein bereits vorhandenes JSON mit der
`controlled_execution_adapter`-Form. Er lehnt unbekannte Top-Level-Felder,
fehlende Summary-Felder, `writes_performed = true`, `simulation_performed =
true`, automatische historische Regelwahl und historische
Vollgleichheitsbehauptungen ab.

## Lokale Bediengrenze

Der Vertrag kann lokal ohne Datei ausgegeben werden:

```powershell
python -m ims.api.run_control_adapter_result_contract
```

Ein bereits erzeugtes Adapterergebnis kann read-only geprueft werden:

```powershell
python -m ims.api.run_control_adapter_result_contract check .\adapter_result.json
```

Der Check schreibt keine Metadaten, erzeugt keine SQLite-Datei und startet den
Adapter nicht.

## Grenzen

- kein Start von `ims.api.controlled_execution_adapter` aus Run-Control;
- kein Browser-Upload;
- kein freier Output-Pfad;
- kein Queue-Ausfuehrungsflag;
- kein UI-Startbutton;
- kein HTTP-Schreibpfad;
- kein Metadatenschreiben;
- keine neue Fachregel;
- keine automatische historische Regelwahl;
- keine historische Vollgleichheitsbehauptung.

## Offene Punkte

PR 38 kann danach optional eine rein lesende API-/UI-Anzeige fuer dieses
vorab erzeugte Adapterresultat planen oder umsetzen. Auch dieser Folgeschritt
bleibt ohne Adapterstart aus Run-Control.
