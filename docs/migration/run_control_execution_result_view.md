# Run-Control-Ergebnisanzeige

## Zweck

PR 47 bindet persistierte Run-Control-Adapterresultate als reine
Ergebnisanzeige in API und Workbench an. Der Schnitt liest nur bereits im
lokalen Ergebnisstore abgelegte Datensaetze und startet keinen Adapter.

## Ursprung

Der Schnitt baut auf PR 45 und PR 46 auf:

- `python_port/ims/api/run_control_execution_result_store.py` speichert und
  liest `run_control_execution_results`;
- Queue-Status `result_persisted` fuehrt im Aktionsplan zu
  `inspect_persisted_result`;
- die Workbench-Karte `Run-Control-Ausfuehrungsflow` zeigt den gesperrten
  Startablauf und verweist auf das persistierte Ergebnis.

## Umsetzung

Die Workbench-API stellt einen neuen read-only Endpunkt bereit:

```text
GET /api/run-control/execution-result/{queue_id}
```

Der Endpunkt liest das persistierte Ergebnis fuer eine bekannte Queue-ID aus
der expliziten SQLite-Metadatenquelle. Fehlende Ergebnisse liefern eine
stabile Fehlerantwort mit
`mode = "run_control_execution_result_store_show"`,
`writes_performed = false`, `execution_performed = false`,
`adapter_started = false` und `simulation_performed = false`.

Die Workbench-Karte `Run-Control-Ergebnisanzeige` zeigt nur kompakte
Metadaten:

- Queue, Run und Szenario;
- Resultatstatus, Summary-Modus und Persistenzzeitpunkt;
- Adaptermodus;
- Grenzflags fuer Adapterausfuehrung, Simulation, Schreibpfade,
  Ausfuehrung und historische Vollgleichheitsbehauptung.

## Grenzen

- Kein `POST /api/run-control/adapter-start`.
- Kein HTTP-Upload fuer Adapterresultate.
- Kein Browser-Dateipicker.
- Kein UI-Startbutton.
- Kein Queue-Worker.
- Kein Adapterstart.
- Keine Simulation.
- Keine neue Fachlogik.
- Keine historische Vollgleichheitsbehauptung.

## Validierung

Die API-Tests pruefen den erfolgreichen read-only Zugriff und die fehlende
Ergebnisform ohne Schreib- oder Startwirkung. Die Frontend-Tests pruefen den
stabilen UI-Anker `run-control-execution-result`, die Ergebniszeilen und die
gesperrten Grenzen.

PR 48 sichert den benutzbaren lokalen Ablauf als Demo-Smoke und Doku ab. Danach
bleibt optional noch Packaging-/Startskript-Haertung fuer eine startbar
verpackte kontrollierte Demo.

## Erweiterung in PR 65

PR 65 ergaenzt die persistierte Ergebnisanzeige um den read-only Endpunkt
`GET /api/run-control/execution-history/{queue_id}`. Die bestehende
Attempt-Tabelle liefert Auditfelder, Start-/Endzeit, `starting`, `failed`,
`result_persisted` und eine optionale Fehlermeldung. Die UI zeigt diese Angaben
und kann Ergebnis plus Verlauf mit `Ergebnis neu laden` erneut per GET lesen.

Es gibt keinen Retry-Button und kein automatisches Polling. Automatische
Wiederholung, Queue-Worker, Upload, freie Pfade, Simulation und historische
Vollgleichheitsbehauptung bleiben gesperrt. Die technische Zuordnung ist in
`run_control_execution_history.md` dokumentiert.
