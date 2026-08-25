# Windows-Freigabegate

## Ziel und Einordnung

PR 70 buendelt die vorhandenen technischen Abschlusspruefungen in einer
lokal und in GitHub Actions identisch aufrufbaren Windows-Kette.

| Ursprung | Umsetzung |
| --- | --- |
| Python-Gesamttests | `python -m pytest -q` |
| Frontend-Produktionsbuild | `npm.cmd run build --prefix .\frontend` |
| PR-69-Korpusbericht | `ims.api.production_release_corpus_report` |
| ZIP und Staging | bestehende Workbench-Bundle-/Portable-Module |
| PR-67-Vertrag | `ims.api.workbench_release_smoke` |
| lokaler Check | portables `check-workbench.cmd` |
| gemeinsame Orchestrierung | `scripts/workbench/test-release-gate.ps1` |
| CI | `.github/workflows/windows-release-gate.yml` |

Das Gate fuegt keine neue fachliche Berechnung hinzu. Es prueft den vorhandenen
Stand und erhaelt die Trennung zwischen technischer Release-Bereitschaft und
fachlich blockierter Produktionsfreigabe.

## Lokaler Aufruf

Nach einmaliger Installation der Python- und Frontend-Abhaengigkeiten:

```powershell
python -m pip install -e ".\python_port[dev]"
npm.cmd ci --prefix .\frontend
.\scripts\workbench\test-release-gate.ps1
```

Ohne `-WorkRoot` erzeugt das Skript einen eindeutigen Ordner `ims-pr70-*` im
Windows-Tempverzeichnis und entfernt nur diesen selbst erzeugten, vorab
verifizierten Pfad. Ein expliziter `-WorkRoot` muss fehlen oder leer sein und
wird nicht automatisch entfernt. Pytest-Tempdaten und -Cache liegen ebenfalls
in diesem Arbeitsverzeichnis; der Lauf haengt damit nicht von globalen
Windows-Temp- oder Repo-Cache-Rechten ab.

## CI-Vertrag

Der Workflow laeuft auf `windows-latest` fuer Pull Requests, Pushes nach
`main` und manuelle Starts. Er verwendet Python 3.12, Node.js 22, den Python-
Extra-Satz `dev` und `npm.cmd ci` gegen das versionierte Lockfile.

Danach ruft der Workflow ausschliesslich das lokale Gate-Skript auf. Damit
bleiben lokale und entfernte Reihenfolge sowie Feldpruefungen identisch.

## Eingefrorene Korpusgrenze

PR 70 verlangt fuer den PR-69-Berichtsvertrag `pr69-v1`:

- `status = "blocked"`;
- `release_decision = "blocked_calculated_core_validation"`;
- 19 Referenzen und 6.300 abgedeckte Perioden;
- 15 fehlende berechnete Kernexporte;
- `production_release_approved = false`;
- keine Schreib-, Ausfuehrungs- oder Simulationsflags;
- keine historische Vollgleichheitsbehauptung.

Diese Werte sind kein dauerhaftes fachliches Sollmodell. Sie frieren den
ehrlichen Abschlussstand ein. Ein spaeterer PR mit belegten berechneten
Exporten muss Bericht, Tests und Gate gemeinsam reviewbar aktualisieren.

## Technische Release-Gates

Nach dem Korpusbericht verlangt das Skript:

- erfolgreiches ZIP mit `execution_performed = false`;
- erfolgreichen Bundle-Smoke;
- erfolgreiches portables Staging;
- erfolgreichen Staging-Smoke und portable Readiness;
- `release_ready = true`, passende Produktionsskripte und weiter getrennten
  PR-66-Demo-Adapter;
- erfolgreiches portables `check-workbench.cmd` ohne Metadatendatenbank.

Das Gate startet keinen Produktionsserver. Der normale Loopback-Start bleibt
durch den eingefrorenen PR-67-Smoke und dessen separate Nachweise abgedeckt.

## Ergebnis

Ein erfolgreicher Lauf endet mit einer kleinen JSON-Zeile:

- `mode = "windows_release_gate"`;
- `status = "ok"`;
- `corpus_report_status = "blocked"`;
- `production_release_approved = false`;
- `missing_calculated_export_count = 15`;
- `release_ready = true`;
- `simulation_performed = false`.

Damit koennen technisches Gate und fachlicher Blocker gleichzeitig korrekt
gruen beziehungsweise blockiert sein.

## Nachweis vom 25. August 2026

Der lokale Windows-Gesamtlauf fuer PR 70 war erfolgreich:

- 1.157 Python-Tests bestanden;
- Frontend-Produktionsbuild mit 1.578 transformierten Modulen bestanden;
- Bundle-, Staging-, Readiness-, Release- und portabler Check bestanden;
- technisches `release_ready = true`;
- fachlicher Korpusbericht weiter `status = "blocked"` mit 15 fehlenden
  berechneten Exporten und `production_release_approved = false`;
- keine Ausfuehrung und keine Simulation gestartet.

## Grenzen

- kein Browser- oder Serverstart;
- kein Adapter-, Runner-, Queue- oder Simulationsstart;
- keine Metadatenbank, kein Import und keine SQLite-Migration;
- kein Zugriff auf `incomming/`;
- keine neue Fachlogik oder automatische historische Regelwahl;
- keine historische Vollgleichheitsbehauptung;
- keine fachliche Produktionsfreigabe.
