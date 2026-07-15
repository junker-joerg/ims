# Run-Control Ergebnis-Persistenzgrenze

## Zweck

Dieser PR 45 bereitet die Queue-/Status-/Resultat-Persistenz fuer eine spaeter
freigegebene Ausfuehrung vor. Der Schnitt speichert nur ein bereits lokal
erzeugtes und gegen den Run-Control-Adapter-Resultat-Vertrag geprueftes
`controlled_execution_adapter`-JSON in eine explizite SQLite-Metadatenquelle.

Der lokale Befehl lautet:

```powershell
python -m ims.api.run_control_execution_result_store persist --db .\.ims_workbench\metadata.sqlite --queue-id baseline-python-tests --adapter-result .\adapter_result.json --persisted-at 2026-07-15T00:00:00Z --explicit-persistence-release
```

Der Persistenzpfad startet keinen Adapter, keinen Runner, keinen Queue-Worker,
keine Simulation und keinen UI-Startbutton. Er ist auch kein historischer
Vollgleichheitsnachweis.

## Ursprung und Mapping

| Ursprung | Python-Ziel |
| --- | --- |
| `docs/plans/run_control_execution_release_plan.md` | PR-45-Persistenzschritt aus der Freigabekette |
| `python_port/ims/api/run_control_adapter_result_contract.py` | Validierung des vorab erzeugten Adapter-Resultats |
| `python_port/ims/api/run_control_queue.py` | Queue-Eintrag und neuer Abschlussstatus `result_persisted` |
| `python_port/ims/api/run_control_queue_action_plan.py` | lesender Folgeschritt `inspect_persisted_result` |
| `python_port/ims/api/run_control_execution_result_store.py` | lokaler SQLite-Resultatstore |
| `tests/test_api_run_control_execution_result_store.py` | Schema-, Persistenz-, CLI- und Negativtests |

## Persistenzgrenze

Der Store legt bei Bedarf die Tabelle `run_control_execution_results` an. Pro
Queue-ID werden gespeichert:

- Queue-, Run- und Szenario-ID;
- Adaptermodus, Fixture-Art und Fixture-Pfad aus dem Adapter-Resultat;
- Summary-Modus und Resultatstatus;
- expliziter Persistenzzeitpunkt `persisted_at`;
- vollstaendiges Adapter-Resultat-JSON;
- Summary-JSON;
- Validierungs-JSON des Run-Control-Adapter-Resultat-Vertrags;
- Grenzflags fuer Adapterausfuehrung, Simulation, automatische historische
  Regelwahl und historische Vollgleichheitsbehauptung.

Nach erfolgreicher Persistenz wird der Queue-Status auf `result_persisted`
gesetzt. Das Queue-Feld `execution_performed` bleibt `false`, weil dieser
PR-45-Pfad selbst keine Ausfuehrung startet. Der Aktionsplan zeigt fuer diesen
Status nur `inspect_persisted_result`.

## Preconditions

Der Persistenzpfad verlangt:

- explizite SQLite-Metadatenquelle per `--db`;
- existierenden Queue-Eintrag;
- Queue-Status `validated` oder bereits `result_persisted`;
- `execution_enabled = false` in der Queue;
- `execution_performed = false` in der Queue;
- lokales Adapter-Resultat-JSON;
- erfolgreiches `run_control_adapter_result_contract`-Validationsergebnis;
- `explicit_execution_release = true` im Adapter-Resultat;
- `--explicit-persistence-release` fuer diesen Schreibschritt.

## Nicht-Ziele

- kein Start von `ims.api.controlled_execution_adapter`;
- kein `POST /api/run-control/adapter-start`;
- kein HTTP-Upload fuer Adapter-Resultate;
- kein Browser-Dateipicker;
- kein UI-Startbutton;
- kein Queue-Worker;
- kein Scheduler-Start;
- keine freie Output-Pfadauswahl;
- keine neue Fachlogik;
- keine automatische historische Regelwahl;
- keine historische Vollgleichheitsbehauptung.

## Folgeschritt

PR 46 zeigt den UI-Flow `Preflight -> explizite Freigabe -> Ausfuehren`
inzwischen als reine Statussicht in der Workbench. Nach PR 46 bleiben grob
1 bis 3 reviewbare PRs bis zu einer benutzbaren kontrollierten
Demo-Simulation. Diese Schaetzung ist kein historischer
Vollgleichheitsnachweis.
