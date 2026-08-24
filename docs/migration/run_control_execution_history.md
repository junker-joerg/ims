# Run-Control-Ausfuehrungsverlauf

## Ziel

PR 65 macht vorhandene Adapterstart-Auditdaten in API und Workbench lesbar.
Laufende, fehlgeschlagene und abgeschlossene Starts bleiben damit nach Auswahl
oder manuellem Neuladen sichtbar. Der Schnitt fuegt keinen Start- oder
Wiederholungspfad hinzu.

## Ursprung und Mapping

| Ursprung | Neue Komponente | Entsprechung |
| --- | --- | --- |
| `run_control_execution_attempts` in `python_port/ims/api/run_control_adapter_start.py` | `python_port/ims/api/run_control_execution_history.py` | Read-only Verlauf mit Audit-, Zeit- und Fehlerfeldern |
| Queue-Status `starting`, `failed`, `result_persisted` | `GET /api/run-control/execution-history/{queue_id}` | Sichtbarer aktueller Ausfuehrungszustand |
| `run_control_execution_results` | `persisted_result_available` und `persisted_at` | Verweis auf ein bereits persistiertes Ergebnis |
| bestehende Workbench-Ergebnisanzeige | Verlaufsteil und `Ergebnis neu laden` | Erneute GET-Abfrage ohne Retry |

Es gibt keine historische C-UI-Entsprechung, die portiert wird. Der Verlauf ist
eine technische Betriebsgrenze der Python-Workbench und aendert keine
Fachlogik.

## API

```text
GET /api/run-control/execution-history/{queue_id}
```

Die Antwort enthaelt Queue-Status, sortierte Attempts, den neuesten Attempt,
Auditfelder, Start-/Endzeit, optionale Fehlermeldung und den Hinweis auf ein
persistiertes Ergebnis. `automatic_retry_enabled`, `queue_worker_enabled`,
`writes_performed`, `execution_performed`, `adapter_started` und
`simulation_performed` bleiben fuer diesen GET-Zugriff `false`.

Eine validierte Queue ohne Attempt liefert einen erfolgreichen leeren Verlauf.
Eine unbekannte Queue liefert eine stabile 404-Fehlerform ohne Seiteneffekt.

## UI

Die Karte `Run-Control-Ergebnisanzeige` laedt Ergebnis und Verlauf gemeinsam.
Sie zeigt insbesondere:

- Attempt- und Idempotenz-ID;
- Freigebenden, Freigabezeit und Begruendung;
- `starting`, `failed` oder `result_persisted`;
- Abschlusszeit und gespeicherte Fehlermeldung;
- vorhandenes persistiertes Ergebnis;
- gesperrte automatische Wiederholung und gesperrten Queue-Worker.

`Ergebnis neu laden` wiederholt nur die beiden GET-Abfragen. Es gibt keinen
Retry-Button, kein automatisches Polling und keine Queue-Statusmutation.

## Validierung

- leere validierte Queue ohne implizite Tabellenerzeugung;
- laufender Attempt ohne Abschluss oder Retry;
- fehlgeschlagener Attempt mit gespeicherter Fehlermeldung;
- wiederholbar identischer abgeschlossener Verlauf mit persistiertem Ergebnis;
- unbekannte Queue mit passiver 404-Form;
- Frontend-Vertrags-, Build- und Browserpruefung.

## Grenzen

- keine Simulation und keine neue Fachlogik;
- kein Retry, Reset, Queue-Worker oder automatisches Polling;
- kein Browser-Upload und kein freier Pfad;
- keine automatische historische Regelwahl;
- keine historische Vollgleichheitsbehauptung.
