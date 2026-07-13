# Run-Control Adapter-Resultat-API-Vertrag

## Zweck

Dieser PR 39 stellt den read-only Vertrag fuer Adapter-Resultate ueber die
Workbench-API bereit:

```text
GET /api/run-control/adapter-result-contract
```

Der Endpunkt beschreibt nur, welche bereits lokal erzeugten und lokal geprueften
`controlled_execution_adapter`-Resultate spaeter angezeigt werden duerfen. Er
nimmt keinen Payload entgegen, liest keine Datei, startet keinen Adapter und
validiert kein Adapter-Resultat ueber HTTP.

## Ursprung und Mapping

| Ursprung | Python-Ziel |
| --- | --- |
| `python_port/ims/api/run_control_adapter_result_contract.py` | lokaler Vertrag und lokaler Validator fuer vorab erzeugte Adapter-Resultate |
| `python_port/ims/api/run_control_adapter_result_api_contract.py` | neuer read-only API-Vertrag fuer die spaetere Anzeigegrenze |
| `python_port/ims/api/app.py` | `GET /api/run-control/adapter-result-contract` |
| `tests/test_api_run_control_adapter_result_api_contract.py` | Modul-, CLI- und Vertragsform-Tests |
| `tests/test_api_health.py` | HTTP-Endpunkt bleibt lesend und ohne Seiteneffekte |

## Vertragsgrenze

Die Antwort enthaelt `mode = "run_control_adapter_result_api_contract"`,
`endpoint = "/api/run-control/adapter-result-contract"`,
`expected_result_mode = "controlled_execution_adapter"` und
`expected_validation_mode = "run_control_adapter_result_validation"`.

Die Sperren bleiben explizit:

- `precomputed_result_required = true`;
- `api_accepts_result_payload = false`;
- `api_validates_result_payload = false`;
- `api_starts_adapter = false`;
- `ui_enabled = false`;
- `queue_worker_enabled = false`;
- `writes_performed = false`;
- `execution_performed = false`;
- `simulation_performed = false`.

Der Endpunkt ist damit nur ein lesbarer Vertrag. Die eigentliche lokale Pruefung
bleibt weiterhin:

```powershell
python -m ims.api.run_control_adapter_result_contract check .\adapter_result.json
```

## Nicht-Ziele

- kein Browser-Upload;
- kein Dateipicker;
- kein HTTP-Payload-Check fuer Adapter-Resultate;
- kein Start von `ims.api.controlled_execution_adapter`;
- kein Queue-Worker;
- kein Schreiben in Metadaten;
- keine neue Fachregel;
- keine automatische historische Regelwahl;
- keine historische Vollgleichheitsbehauptung.

## Naechster Schritt

PR 40 kann eine gesperrte UI-Karte fuer diesen Vertrag anzeigen. Auch dieser
Folgeschritt bleibt ohne Upload, Dateiauswahl, Startbutton und
Ausfuehrungsfreigabe.
