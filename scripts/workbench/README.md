# Lokale Workbench-Skripte

Diese Skripte kapseln den lokalen Workbench-Start fuer Windows. Sie bleiben bewusst schmal und fuehren keine Simulation, keinen Import und keine Queue-Schreiboperation aus.

```powershell
scripts\workbench\check-workbench.cmd
scripts\workbench\start-workbench.cmd
.\scripts\workbench\test-release-gate.ps1
```

- `check-workbench.cmd` prueft `frontend/dist`, Startdiagnose und Readiness. Es startet keinen dauerhaften Server und schreibt keine Metadaten.
- `start-workbench.cmd` startet nur den lokalen Backend-Server auf `http://127.0.0.1:8000/` und nutzt das vorhandene gebaute Frontend.
- Beide Skripte setzen konservative Defaults, falls nichts vorgegeben ist:
  `IMS_FRONTEND_DIST`, `IMS_METADATA_DB`, `IMS_WORKBENCH_HOST=127.0.0.1` und
  `IMS_WORKBENCH_PORT=8000`. Diese Werte koennen vor dem Skriptaufruf
  ueberschrieben werden.
- Das Check-Skript uebergibt `IMS_METADATA_DB` nur, wenn die Datei bereits
  existiert; ein Erstcheck ohne lokale Datenbank bleibt dadurch read-only und
  erfolgreich.
- `build-user-test-package.ps1` erzeugt aus dem gebauten Frontend ein finales
  Windows-ZIP mit Installationsskript und den kurzen PDF-Handbuechern.
- Das portable `install-workbench.cmd` legt `.venv` lokal an; Check und Start
  verwenden diese Umgebung danach automatisch.
- `test-release-gate.ps1` fuehrt Python-Tests, Frontend-Build, den blockierten
  PR-69-Korpusbericht, ZIP/Staging, Release-Smoke und das portable Checkskript
  in einer Windows-Kette aus. Es startet keinen Server oder Adapter.

Vorher muss das Frontend gebaut sein:

```powershell
cd frontend
npm.cmd run build
cd ..
```

Die Skripte sind kein Installer, kein Release-Artefakt, kein Szenario-Editor und kein Run-Start.
Die eingefrorene lokale Release-Reihenfolge und die Trennung vom isolierten
PR-66-Demo-Adapter stehen in
`docs/migration/workbench_release_checklist.md`.
Das PR-70-Gate und seine CI-Grenzen stehen in
`docs/migration/windows_release_gate.md`.
