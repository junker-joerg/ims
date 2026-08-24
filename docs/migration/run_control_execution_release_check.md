# Read-only Run-Control-Ausfuehrungsfreigabecheck

## Ziel

PR 62 verbindet den vorhandenen Queue- und Preflight-Stand mit einem
serverseitig kontrollierten Freigabeprofil. Der neue Endpunkt

```text
POST /api/run-control/adapter-release-check
```

prueft, ob ein spaeterer lokaler Adapterstart freigabereif waere. Er startet
den Adapter nicht, veraendert keinen Queue-Status, persistiert kein Ergebnis
und startet keine Simulation.

## Ursprung und Mapping

| Ursprung | Python-Ziel | Rolle |
| --- | --- | --- |
| Start-Preconditions aus `run_control_execution_release_plan.md` | `run_control_execution_release.py` | strikte, rein lesende Freigabechecks |
| vorhandener Queue-Eintrag | `run_control_queue.py` | muss existieren, passen und Status `validated` haben |
| vorhandener Run-/Szenario-Preflight | `run_control_preflight.py` | muss ohne blockierende Issues enden |
| vorhandener lokaler Adaptervertrag | `run_control_adapter_start_contract.py` | legt Adaptermodus und gesperrten Startpfad fest |
| Workbench-API | `app.py` | nimmt nur den Freigabecheck-Payload entgegen |

Es wird keine neue C-Fachlogik portiert. Der PR fuegt ausschliesslich eine
technische Kontroll- und Auditgrenze vor einer spaeteren Ausfuehrung hinzu.

## Audit-Payload

Pflichtfelder sind unter anderem:

- `queue_id`, `run_id` und `scenario_id`;
- `release_profile_id`;
- `expected_adapter_mode`;
- `explicit_execution_release = true`;
- `released_by`, `released_at` und `release_reason`.

Fixture- und Ausgabepfade sind keine akzeptierten Request-Felder. Ebenso werden
`browser_upload` und andere unbekannte Felder verworfen. Das lokale Profil
`vu14-calculated-diagnostic` verweist serverseitig auf das bereits versionierte
Fixture `tests/fixtures/calculated_vu14_explicit_slice.json`.

## Freigabechecks

Der Check verlangt:

- einen vorhandenen Queue-Eintrag mit exakt passenden IDs;
- Queue-Status `validated`;
- weiterhin `execution_enabled = false` und `execution_performed = false` in
  den Queue-Metadaten;
- einen gefundenen Run und ein gefundenes Szenario im Preflight;
- keine blockierenden Preflight-Issues;
- ein bekanntes lokales Profil mit passendem Run, Szenario und Adaptermodus;
- ein vorhandenes Fixture innerhalb des vertrauenswuerdigen lokalen
  Fixture-Verzeichnisses;
- einen zum Profil passenden Fixture-Typ;
- keinen vom Profil unerlaubten VU-/VN-Carryover.

Ein positiver Check liefert `status = "ready"` und `release_ready = true`.
Trotzdem bleiben `adapter_start_allowed = false`, `adapter_started = false`,
`writes_performed = false`, `execution_performed = false` und
`simulation_performed = false`.

## Warum noch kein Adapterstart

Der aktuelle Queue-Eintrag besitzt noch keine atomare Zwischenstufe fuer
`starting`, `running`, `completed` oder einen idempotenten Startschluessel. Ein
sofortiger Start waere deshalb wiederholbar, bevor Ergebnis und Queue-Status
gesichert sind. Diese Luecke wird nicht still durch einen ungeschuetzten
Startendpunkt uebersprungen.

## Validierung und Grenzen

Die Tests pruefen positive und blockierte Freigaben, verpflichtende
Auditfelder, verbotene Browserpfade, Queue-Status, unbekannte Profile,
Carryover-Sperren sowie den HTTP-Endpunkt. `POST /api/run-control/adapter-start`
bleibt weiterhin nicht vorhanden.

Der Freigabecheck ist kein historischer Neu-/Alt-Vergleich und behauptet keine
historische Vollgleichheit. Es wurde keine Simulation gestartet.

## Naechster Schritt

PR 63 fuegt die atomare Backend-Start-, Status- und Ergebnisgrenze hinzu. Erst
danach darf PR 64 den UI-Startpfad hinter der expliziten Freigabe aktivieren.
