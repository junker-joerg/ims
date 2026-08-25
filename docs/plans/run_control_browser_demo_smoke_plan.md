# Plan: Run-Control-Browser-Demo-Smoke (PR 66)

## Ziel

PR 66 prueft den sichtbaren Workbench-Pfad fuer einen explizit freigegebenen
lokalen Demo-Run. Der Browser muss Freigabecheck, genau einen kontrollierten
Adapterstart, persistiertes Ergebnis und Ausfuehrungsverlauf zeigen.

Der Smoke startet keine Simulation. Er verwendet ausschliesslich einen
injizierten Fake-Adapter mit festem Resultatvertrag.

## Ursprung und Zuordnung

- Run-Control-Freigabe: `python_port/ims/api/run_control_execution_release.py`.
- atomarer Adapterstart: `python_port/ims/api/run_control_adapter_start.py`.
- Ergebnis und Verlauf:
  `python_port/ims/api/run_control_execution_result_store.py` und
  `python_port/ims/api/run_control_execution_history.py`.
- sichtbarer Bedienpfad: `frontend/src/main.tsx`.
- neuer isolierter Smoke-Startpunkt:
  `python_port/ims/api/run_control_browser_demo_smoke.py`.

Es gibt keine historische C-Entsprechung. Der Schnitt prueft nur die technische
Workbench-Bedienung und aendert keine Modellsemantik.

## Umsetzung

1. Der Smoke-Startpunkt verlangt eine frische explizite SQLite-Datei und ein
   gebautes Frontend.
2. Er legt genau den bekannten Run `baseline-python-tests` mit dem Szenario
   `agrsich-reference-window` als `validated` in der Queue an.
3. `create_app` erhaelt einen lokalen Fake-Adapter. Dieser akzeptiert nur den
   bereits freigegebenen Adaptermodus ohne Carryover und liefert einen kleinen
   vertragstreuen Ergebnis-Payload.
4. Der Server darf nur an eine Loopback-Adresse gebunden werden.
5. Der Browser-Smoke bestaetigt explizit die Freigabe, startet den Adapter
   einmal, liest Ergebnis und Verlauf erneut und prueft die mobile Darstellung.

## Validierung

- API-Test fuer Freigabe, Erststart, persistiertes Resultat und Verlauf;
- Idempotenztest: derselbe Start-Payload ruft den Fake-Adapter nicht erneut auf;
- Vertragstest fuer frische Datenbank, gebautes Frontend und Loopback-Bindung;
- Frontend-Build;
- sichtbarer Desktop- und Mobil-Smoke mit Screenshot;
- kompletter Pytest-Lauf.

## Grenzen

- keine Simulation und keine neue Fachlogik;
- kein echter `run_controlled_execution_adapter` im Browser-Smoke;
- kein Queue-Worker, Retry, Polling, Upload oder freier Dateipfad;
- keine automatische historische Regelwahl;
- keine historische Vollgleichheitsbehauptung;
- der Smoke-Startpunkt ist kein Produktionsstartskript.
