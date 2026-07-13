# Kontrollierter lokaler Ausfuehrungsadapter

## Zweck

Dieser PR 35 setzt den ersten lokalen Ausfuehrungsadapter um. Er ist nur als
explizit aufgerufene Python-Funktion und CLI verfuegbar und bleibt von API, UI,
Run-Control-Queue und Workbench-Demo getrennt.

Der Adapter startet keine Simulation und keinen Scheduler. Er fuehrt nur den
bereits portierten expliziten VU/VN-Periodenrunner fuer ein angegebenes Fixture
aus und gibt das Ergebnis als vorhandenen
`explicit_multi_period_execution_summary`-Vertrag zurueck.

## Ursprung und Mapping

| Ursprung / Anker | Neue Einordnung |
| --- | --- |
| `python_port/ims/api/controlled_execution_adapter_contract.py` | freigegebener Vertrag aus PR 34 |
| `python_port/ims/api/controlled_execution_adapter.py` | lokaler Adapter fuer explizit freigegebene Fixture-Ausfuehrung |
| `run_explicit_multi_period_from_fixture` | Runner-Anker fuer einfache `periods`-Fixtures |
| `run_explicit_multi_period_from_plan_fixture` | Runner-Anker fuer `base_snapshot` plus `period_updates`-Planfixtures |
| `build_explicit_multi_period_execution_summary` | einzige Ergebnisform des Adapters |
| `tests/test_api_controlled_execution_adapter.py` | Test fuer Freigabe, Fixture-Arten, Schreibfreiheit und CLI-Grenzen |

## Lokale Bediengrenze

Der Adapter kann lokal so aufgerufen werden:

```powershell
python -m ims.api.controlled_execution_adapter --fixture tests\fixtures\replay_vn_policyholder_transition_plan.json --explicit-execution-release
```

Ohne `--explicit-execution-release` startet der Adapter nicht. Ein freier
Output-Pfad wird in diesem PR nicht akzeptiert; `--output-dir` ist bewusst kein
gueltiges Argument.

## Erlaubt

- `explicit_multi_period_fixture` mit `periods`;
- `explicit_vu_vn_period_plan_fixture` mit `base_snapshot` und
  `period_updates`;
- optionale `--carry-forward-vu-state` und `--carry-forward-vn-state` fuer
  einfache Mehrperiodenfixtures;
- Ergebnis nur als `explicit_multi_period_execution_summary`.

## Grenzen

- kein HTTP-Endpunkt;
- kein UI-Startpfad;
- kein Queue-Worker;
- kein Run-Control-Start;
- kein freier Output-Pfad;
- keine Metadaten-Schreiboperation;
- keine neue Fachlogik;
- keine automatische historische Regelwahl;
- keine historische Vollgleichheitsbehauptung.

In diesem PR bleibt `writes_enabled = false`; bei den getesteten Aufrufen bleibt
auch `writes_performed = false`. Der Adapter meldet `execution_performed = true`
nur fuer den explizit lokal freigegebenen Fixture-Lauf.

## Validierung

`tests/test_api_controlled_execution_adapter.py` prueft:

- fehlende explizite Freigabe blockiert den Adapter;
- einfache `periods`-Fixtures laufen ohne Ausgabedateien;
- vorhandene Planfixtures laufen ohne Output-Pfad;
- die CLI gibt JSON aus;
- ein freier `--output-dir` wird abgelehnt;
- die Fixture-Art wird konservativ erkannt.

Zusaetzlich haelt `tests/test_imports.py` den Paketimport stabil.

## Offene Punkte

PR 36 sollte noch keine automatische Run-Control-Ausfuehrung oeffnen. Naheliegend
ist ein read-only Adapter-Resultat fuer Run-Control oder ein weiterer schmaler
fachlicher Slice, weiterhin ohne Vollgleichheitsbehauptung.
