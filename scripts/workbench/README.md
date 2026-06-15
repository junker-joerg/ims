# Lokale Workbench-Skripte

Diese Skripte kapseln den lokalen Workbench-Start fuer Windows. Sie bleiben bewusst schmal und fuehren keine Simulation, keinen Import und keine Queue-Schreiboperation aus.

```powershell
scripts\workbench\check-workbench.cmd
scripts\workbench\start-workbench.cmd
```

- `check-workbench.cmd` prueft `frontend/dist`, Startdiagnose und Readiness. Es startet keinen dauerhaften Server und schreibt keine Metadaten.
- `start-workbench.cmd` startet nur den lokalen Backend-Server auf `http://127.0.0.1:8000/` und nutzt das vorhandene gebaute Frontend.

Vorher muss das Frontend gebaut sein:

```powershell
cd frontend
npm.cmd run build
cd ..
```

Die Skripte sind kein Installer, kein Release-Artefakt, kein Szenario-Editor und kein Run-Start.
