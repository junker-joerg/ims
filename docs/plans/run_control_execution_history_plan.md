# Plan: Run-Control-Ergebnisverlauf (PR 65)

## Ziel

Die Workbench soll den bereits von PR 63 persistierten Adapterstart-Versuch
lesend einordnen. `starting`, `failed` und `result_persisted` muessen nach einer
erneuten Auswahl oder einem manuellen Neuladen stabil sichtbar bleiben.

## Ursprung und Zuordnung

- Ursprung: `run_control_execution_attempts` aus
  `python_port/ims/api/run_control_adapter_start.py`.
- Neue read-only Grenze:
  `python_port/ims/api/run_control_execution_history.py`.
- UI: bestehende Karte `Run-Control-Ergebnisanzeige` in
  `frontend/src/main.tsx`.

Die Attempt-Tabelle enthaelt bereits Idempotenzschluessel, Auditfelder,
Start-/Endzeit, Status und eine optionale Fehlermeldung. PR 65 fuegt keine neue
Ausfuehrungssemantik hinzu, sondern liest diese vorhandenen Daten.

## Umsetzungsschnitt

1. `GET /api/run-control/execution-history/{queue_id}` liest Queue-Status und
   vorhandene Attempts aus der expliziten SQLite-Metadatenquelle.
2. Die Antwort meldet, ob ein persistiertes Ergebnis vorhanden ist, und bleibt
   ohne Schreib-, Start- oder Simulationswirkung.
3. Die UI zeigt den neuesten Attempt mit Freigabe-, Zeit- und Fehlerdaten.
4. `Ergebnis neu laden` wiederholt nur die beiden GET-Abfragen fuer Verlauf und
   persistiertes Ergebnis.
5. Es gibt keinen Retry-, Reset-, Worker- oder automatischen Pollingpfad.

## Validierung

- Unit- und API-Tests fuer leeren, laufenden, fehlgeschlagenen und
  abgeschlossenen Verlauf;
- Frontend-Vertragstests fuer Endpunkt, Zustandsdarstellung und reinen
  Neuladepfad;
- Frontend-Build und Browser-Smoke ohne Adapterstart;
- kompletter Pytest-Lauf.

## Grenzen

- keine Simulation und keine neue Fachlogik;
- kein automatischer oder manueller Retry;
- kein Queue-Worker, Upload oder freier Pfad;
- keine automatische historische Regelwahl;
- keine historische Vollgleichheitsbehauptung.
