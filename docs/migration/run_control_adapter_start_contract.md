# Run-Control Adapter-Startvertrag

## Zweck

Dieser PR 44 stellt nur den hart gegateten Startvertrag fuer den kontrollierten
Adapter ueber die Workbench-API bereit:

```text
GET /api/run-control/adapter-start-contract
```

Der Endpunkt beschreibt, welche Voraussetzungen ein spaeterer Startpfad fuer
`ims.api.controlled_execution_adapter` erfuellen muss. Er nimmt keinen
Start-Payload entgegen, prueft keinen Payload ueber HTTP, startet keinen
Adapter, schreibt keine Ergebnisse und startet keine Simulation.

## Ursprung und Mapping

| Ursprung | Python-Ziel |
| --- | --- |
| `docs/plans/run_control_execution_release_plan.md` | Freigabekette und Preconditions aus PR 43 |
| `python_port/ims/api/controlled_execution_adapter.py` | spaeterer lokaler Adapter, in diesem PR nicht gestartet |
| `python_port/ims/api/run_control_adapter_start_contract.py` | neuer read-only API-Startvertrag |
| `python_port/ims/api/app.py` | `GET /api/run-control/adapter-start-contract` |
| `tests/test_api_run_control_adapter_start_contract.py` | Modul-, CLI-, HTTP- und negativer Startpfad-Test |
| `tests/test_api_health.py` | HTTP-Endpunkt bleibt lesend und ohne Seiteneffekte |

## Vertragsgrenze

Die Antwort enthaelt `mode = "run_control_adapter_start_contract"`,
`endpoint = "/api/run-control/adapter-start-contract"` und
`planned_start_endpoint = "/api/run-control/adapter-start"`.

Der Vertrag benennt die spaeter erforderlichen Request-Felder:

- `queue_id`;
- `run_id`;
- `scenario_id`;
- `explicit_execution_release`;
- `expected_adapter_mode`.

Der Vertrag benennt die spaeter erforderlichen Preconditions:

- Queue-Eintrag existiert;
- Queue-Eintrag gehoert zu bekanntem Run und Szenario;
- Queue-Status ist `validated` oder explizit freigegeben;
- Preflight ist gruen oder Blocker sind explizit aufgeloest;
- `explicit_execution_release = true`;
- Fixture-Pfad stammt aus bekannter lokaler Metadatenquelle;
- Ergebnisablage erfolgt nur ueber kontrollierten Run-Control-Pfad.

Die Sperren bleiben explizit:

- `api_accepts_start_payload = false`;
- `api_validates_start_payload = false`;
- `api_starts_adapter = false`;
- `ui_start_enabled = false`;
- `queue_worker_enabled = false`;
- `writes_enabled = false`;
- `execution_enabled = false`;
- `writes_performed = false`;
- `execution_performed = false`;
- `simulation_performed = false`;
- `automatic_historical_rule_selection_performed = false`;
- `historical_full_equality_claimed = false`.

Der geplante `POST /api/run-control/adapter-start` ist in diesem PR nicht
vorhanden. Der negative API-Test prueft genau diese Grenze.

## Nicht-Ziele

- kein POST-Startendpunkt;
- kein Start von `ims.api.controlled_execution_adapter`;
- kein Runner-Start;
- kein Queue-Worker;
- kein UI-Startbutton;
- kein Browser-Upload;
- keine freie Fixture- oder Output-Pfadauswahl;
- keine Ergebnis-Persistenz;
- keine neue Fachlogik;
- keine automatische historische Regelwahl;
- keine historische Vollgleichheitsbehauptung.

## Folgeschritt

PR 45 soll als naechsten reviewbaren Schritt die Queue-/Status-/Resultatgrenzen
fuer eine spaeter freigegebene Ausfuehrung vorbereiten. Auch dieser Schritt
soll noch klein bleiben und darf nur die kontrollierte Persistenzgrenze
schaffen, nicht automatisch Queue-Worker oder UI-Startbutton einfuehren.

## Erweiterung in PR 62

PR 62 laesst den Startendpunkt weiterhin gesperrt, ergaenzt aber den
read-only Freigabecheck `POST /api/run-control/adapter-release-check`.
`api_accepts_release_payload = true` und
`api_validates_release_payload = true` gelten nur fuer diesen Check. Die
Startflags `api_accepts_start_payload`, `api_validates_start_payload` und
`api_starts_adapter` bleiben `false`.

Der Freigabecheck verlangt zusaetzlich `release_profile_id`, `released_by`,
`released_at` und `release_reason`. Fixture- oder Ausgabepfade duerfen nicht
aus dem Browserpayload stammen. PR 63 muss vor einem echten Adapterstart eine
atomare Status-/Idempotenz- und Ergebnisgrenze schaffen.

## Erweiterung in PR 63

PR 63 aktiviert den eng gegateten Backend-Endpunkt
`POST /api/run-control/adapter-start`. Der Vertrag verlangt nun zusaetzlich
`idempotency_key`; `api_accepts_start_payload`,
`api_validates_start_payload`, `api_starts_adapter`, `writes_enabled` und
`execution_enabled` beschreiben diese Backend-Faehigkeit mit `true`.

Der lesende GET-Vertrag selbst fuehrt weiterhin nichts aus und meldet deshalb
`writes_performed = false`, `execution_performed = false` und
`simulation_performed = false`. UI-Startbutton, Queue-Worker, freie Pfade,
automatische historische Regelwahl und historische Vollgleichheitsbehauptung
bleiben ausgeschlossen. Die atomare Umsetzung ist in
`run_control_atomic_adapter_start.md` dokumentiert.

## Erweiterung in PR 64

PR 64 setzt `ui_start_enabled = true` und entfernt den UI-Startbutton aus den
verbotenen Vertragsgrenzen. Das aktiviert ausschliesslich den zweistufigen
Workbench-Pfad `Freigabe pruefen -> Adapter starten`. Der UI-Start bleibt an
Queue-Status `validated`, Auditfelder, das feste serverseitige Profil und den
unveraenderten Idempotenzpayload gebunden. `queue_worker_enabled = false`,
freie Pfade, Browser-Upload und Simulation bleiben gesperrt.
