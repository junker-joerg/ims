# Workbench-Metadaten Backup, Restore, Update und Rollback

## Ziel und Einordnung

PR 68 ergaenzt eine explizite technische Recovery-Probe fuer lokale
Workbench-Metadaten. Sie erhaelt neben Szenarien und Runs auch Queue,
Ausfuehrungsversuch und persistiertes Run-Control-Resultat.

| Ursprung | Umsetzung |
| --- | --- |
| `metadata_repository.py` | Tabellen `scenarios` und `runs` |
| `run_control_queue.py` | Queue-Eintrag und Status `result_persisted` |
| `run_control_adapter_start.py` | abgeschlossener Ausfuehrungsversuch |
| `run_control_execution_result_store.py` | persistiertes validiertes Resultat |
| `sqlite_readonly.py` | WAL-/SHM-bewusster Read-only-Zugriff |
| `workbench_metadata_recovery.py` | Inspect, SQLite-Backup, Restore und Digestvergleich |

Der vorhandene JSON-Metadatenexport bleibt fuer portable Szenario-/Run-Bundles
geeignet, enthaelt aber keine Queue-, Attempt- oder Resultatzeilen. Fuer den
vollstaendigen lokalen Ergebnisstand verwendet PR 68 deshalb die SQLite-
Backup-API.

## Befehle

Validierten Ergebnisstand rein lesend pruefen:

```powershell
python -m ims.api.workbench_metadata_recovery inspect --db .\.ims_workbench\metadata.sqlite --queue-id baseline-python-tests
```

Explizites Backup in einen vorbereiteten Zielordner schreiben:

```powershell
python -m ims.api.workbench_metadata_recovery backup --source-db .\.ims_workbench\metadata.sqlite --out .\backup\metadata.sqlite --queue-id baseline-python-tests
```

Backup in einen neuen Zielpfad wiederherstellen:

```powershell
python -m ims.api.workbench_metadata_recovery restore --backup-db .\backup\metadata.sqlite --out .\restore\metadata.sqlite --queue-id baseline-python-tests
```

Quelle und wiederhergestellten Kandidaten rein lesend vergleichen:

```powershell
python -m ims.api.workbench_metadata_recovery verify --source-db .\.ims_workbench\metadata.sqlite --candidate-db .\restore\metadata.sqlite --queue-id baseline-python-tests
```

`backup` und `restore` schreiben nur den expliziten, vorher noch nicht
vorhandenen Zielpfad. Der Zielordner muss existieren. Bestehende Dateien werden
nicht ersetzt. Vor dem Schreiben muss die Quelle einen vollstaendigen
validierten Ergebnisstand enthalten; das temporaere SQLite-Ziel wird vor der
Veroeffentlichung erneut geprueft.

## Gepruefter Zustand

Der Digest umfasst in stabiler Tabellen- und Primaerschluesselreihenfolge:

- `scenarios`;
- `runs`;
- `run_control_queue`;
- `run_control_execution_attempts`;
- `run_control_execution_results`.

Die Probe verlangt `result_persisted`, einen abgeschlossenen Attempt, ein
Resultat mit `result_status = ok`, `simulation_performed = false`, keine
automatische historische Regelwahl und keine historische
Vollgleichheitsbehauptung. JSON-Felder des Resultats muessen lesbare Objekte
sein.

## Update und Rollback

Ein konservativer Side-by-Side-Test verwendet eine gemeinsame explizite
Metadatenquelle und zwei getrennte Anwendungspfade:

1. Repo-Anwendung prueft die Quelle mit ihrem `python_port`.
2. Frisch gestagte portable Anwendung prueft dieselbe Quelle mit
   `app\python_port`.
3. Beide `inspect`-Ausgaben muessen denselben `critical_digest` liefern.
4. Der Repo-Anwendungspfad liest die Quelle danach erneut mit unveraendertem
   Digest. Damit ist der technische Rollback-Pfad belegt.

Die Probe kopiert keine neue Anwendung ueber eine alte, mutiert die gemeinsame
Metadatenquelle nicht und setzt `PYTHONPATH` je Anwendungspfad explizit. Im
PR-68-Smoke enthalten beide Anwendungspfade denselben Codebestand. Das ist ein
Pfad- und Datenerhaltstest, keine Aussage zur Kompatibilitaet beliebiger alter
Programmversionen.

## Ergebnisfelder

- `recovery_contract_version = "pr68-v1"`;
- `states_match`, `update_probe_ready`, `rollback_probe_ready`;
- Tabellenzaehler und `critical_digest` je Zustand;
- `output_created` und `writes_performed` nur fuer Backup/Restore;
- `execution_performed = false` und `adapter_started = false`;
- `simulation_performed = false`;
- `historical_full_equality_claimed = false`.

## Nachweis vom 2026-08-25

Der reale PR-68-Smoke verwendete einen ohne Runner oder Simulation direkt
persistierten validierten Ergebnisstand. Quelle, Backup, Restore, der
Repo-Anwendungspfad, ein frisch aus dem ZIP gestagter portabler Anwendungspfad
und der anschliessende Repo-Rollback lieferten denselben `critical_digest`.

| Tabelle | Zeilen |
| --- | ---: |
| `scenarios` | 2 |
| `runs` | 2 |
| `run_control_queue` | 1 |
| `run_control_execution_attempts` | 1 |
| `run_control_execution_results` | 1 |

Das frisch gebaute ZIP enthielt 112 Eintraege. Der PR-67-Release-Smoke blieb
mit `release_ready = true`, `artifact_scripts_match_repo = true`,
`pr66_demo_adapter_separated = true` und `simulation_performed = false` gruen.
Der Nachweis ist eine technische Recovery- und Pfadpruefung; er erweitert weder
den historischen Altdatenkorpus noch dessen Gleichheitsaussage.

## Grenzen

- kein automatischer Zeitplan und keine Aufbewahrungsverwaltung;
- kein In-place-Restore und kein automatischer Versionswechsel;
- keine SQLite-Schemamigration;
- kein Adapterstart, Queue-Worker oder Browser-Schreibpfad;
- keine Simulation und keine neue Fachlogik;
- keine historische Vollgleichheitsbehauptung.
