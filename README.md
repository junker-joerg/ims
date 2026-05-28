# ims

Dieses Repository enthält das Arbeitsgerüst für eine schrittweise, PR-basierte und semantisch konservative Migration von IMS.
Weitere Hinweise stehen unter `docs/migration/README.md`.

## Lokale Workbench

Eine erste lokale Backend-/Frontend-Shell ist unter `docs/migration/workbench_shell.md` beschrieben.

Kurzstart:

```powershell
python -m pip install -e .\python_port[dev]
cd frontend
npm.cmd install
npm.cmd run build
cd ..
python -m ims.api.workbench_diagnostics --frontend-dist frontend/dist
python -m uvicorn ims.api.app:app --app-dir python_port --host 127.0.0.1 --port 8000
```

Danach ist die Workbench lokal unter `http://127.0.0.1:8000/` erreichbar. Die aktuelle Workbench ist weiterhin rein lesend: keine Simulation, kein Browser-Upload und keine HTTP-/UI-Schreibpfade.

Optional kann die Diagnose eine explizite lokale Konfigurationsdatei lesen:

```powershell
python -m ims.api.workbench_diagnostics --config .\workbench.local.json
```
