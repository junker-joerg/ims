# Plan: Read-only Anzeige fuer Adapter-Resultate

## Zweck

Dieser Plan schlaegt den naechsten Schritt nach dem
Run-Control-Adapter-Resultat-Vertrag aus PR 37 vor.

Der naechste reviewbare Schnitt soll keine Ausfuehrung oeffnen, sondern eine
rein lesende API-/UI-Anzeige fuer bereits lokal erzeugte Adapterresultate
vorbereiten. Run-Control darf ein geprueftes
`controlled_execution_adapter`-JSON sichtbar einordnen, aber weiterhin keinen
Adapter starten.

## Vorschlag fuer PR 38

PR 38 soll eine read-only Anzeigegrenze planen:

- Quelle bleibt ein bereits lokal erzeugtes und lokal geprueftes
  `controlled_execution_adapter`-JSON;
- der vorhandene Vertrag
  `python_port/ims/api/run_control_adapter_result_contract.py` bleibt die
  Formgrenze;
- die API darf zunaechst hoechstens einen Vertrag oder eine Platzhalterantwort
  fuer ein vorab bereitgestelltes Ergebnis beschreiben;
- die UI darf zunaechst hoechstens eine gesperrte Karte fuer
  Adapter-Resultate planen;
- kein Browser-Upload, kein Dateipicker, kein Editor, kein Startbutton;
- kein Zugriff auf freie Output-Pfade;
- kein Start von `ims.api.controlled_execution_adapter`;
- kein Schreiben in Queue- oder Metadatenbanken.

## Empfohlene PR-Reihenfolge

- PR 38: read-only API-/UI-Anzeige fuer Adapter-Resultate planen und
  dokumentieren, ohne neuen Endpunkt und ohne UI-Startpfad (erledigt).
- PR 39: optional read-only API-Vertrag oder Endpunkt fuer ein vorab
  bereitgestelltes Adapter-Resultat vorbereiten, weiterhin ohne Upload und
  ohne Adapterstart (dieser Schnitt:
  `python_port/ims/api/run_control_adapter_result_api_contract.py`,
  `tests/test_api_run_control_adapter_result_api_contract.py` und
  `docs/migration/run_control_adapter_result_api_contract.md`).
- PR 40: optional UI-Karte fuer diesen Vertrag anzeigen, weiterhin ohne
  Upload, Dateiauswahl, Startbutton oder Ausfuehrungsfreigabe (dieser Schnitt:
  `Adapter-Resultat-Vertrag` in `frontend/src/main.tsx` und
  `tests/test_frontend_shell.py`).
- PR 41: danach wieder einen schmalen fachlichen VN-Slice umsetzen:
  `best_info`-Wirkung plus VN-State-Carryover ueber zwei explizite Perioden
  (erledigt).
- PR 42: weiteren schmalen fachlichen VN-Slice umsetzen:
  `sample_search` / Vrvn05 plus Schaden-/Settlement-Runner-Grenze
  (erledigt).
- PR 43+: danach den expliziten Run-Control-Ausfuehrungsfreigabeplan
  vorbereiten, weiterhin ohne sofortigen UI-Startbutton.

## Grenzen

- keine Simulation;
- kein Scheduler-Start;
- kein Runner-Start;
- kein Adapterstart aus Run-Control;
- kein Browser-Upload;
- kein HTTP-Schreibpfad;
- kein UI-Startpfad;
- kein Queue-Worker;
- keine neue Fachregel;
- keine automatische historische Regelwahl;
- keine historische Vollgleichheitsbehauptung.

## Validierung

Dieser Plan soll ueber Dokumentationstests abgesichert werden. Er selbst
startet keinen Adapter und fuehrt keine fachliche Berechnung aus.
