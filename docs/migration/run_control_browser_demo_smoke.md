# Run-Control-Browser-Demo-Smoke

## Ziel

PR 66 prueft den vollstaendigen sichtbaren Run-Control-Pfad der lokalen
Workbench gegen einen injizierten Fake-Adapter. Der Smoke zeigt explizite
Freigabe, genau einen Adapteraufruf, Ergebnisablage, Verlauf und read-only
Neuladen.

Der Smoke ist kein Simulationslauf und kein historischer Ergebnisnachweis.

## Ursprung und Mapping

| Ursprung | Smoke-Komponente | Entsprechung |
| --- | --- | --- |
| `run_control_execution_release.py` | UI-Schritt `Freigabe pruefen` | serverseitig geprueftes lokales Fixture-Profil |
| `run_control_adapter_start.py` | UI-Schritt `Adapter starten` | atomarer, idempotenter Startvertrag |
| `run_control_execution_result_store.py` | Ergebnisanzeige | persistiertes synthetisches Adapterresultat |
| `run_control_execution_history.py` | Verlaufssicht | genau ein abgeschlossener Attempt ohne Retry |
| `frontend/src/main.tsx` | stabile `data-testid`-Anker | sichtbarer Desktop- und Mobil-Smoke |
| kein historischer C-Pfad | `run_control_browser_demo_smoke.py` | rein technische Testschale mit Fake-Adapter |

## Sicherer lokaler Start

Das Frontend wird zuerst normal gebaut. Danach wird der isolierte Smoke-Server
mit einer frischen Datenbank gestartet:

```powershell
npm.cmd run build --prefix .\frontend
$env:PYTHONPATH = ".\python_port"
python -m ims.api.run_control_browser_demo_smoke --db .\.ims_workbench\pr66-browser-smoke.sqlite --frontend-dist .\frontend\dist --host 127.0.0.1 --port 8011
```

Der Startpunkt verweigert vorhandene Datenbanken, fehlende Frontend-Builds und
Nicht-Loopback-Adressen. Er ist kein Produktionsstartskript.

## Browser-Ablauf

1. `http://127.0.0.1:8011/#validation` oeffnen.
2. Den Queue-Eintrag `baseline-python-tests` mit Status `validated` auswaehlen.
3. Freigebenden und Begruendung eintragen sowie die explizite Freigabe
   bestaetigen.
4. `Freigabe pruefen` ausloesen und `release_ready = true` abwarten.
5. `Adapter starten` genau einmal ausloesen.
6. In Ergebnis und Verlauf `result_persisted` und einen Attempt pruefen.
7. `Ergebnis neu laden` ausloesen und bestaetigen, dass kein zweiter Attempt
   und kein Retry entsteht.
8. Desktop-Screenshot aufnehmen und anschliessend die Darstellung bei 390 px
   Breite ohne horizontalen Ueberlauf pruefen.

## Fake-Adapter

Der injizierte Runner akzeptiert ausschliesslich:

- `explicit_multi_period_fixture_adapter`;
- `explicit_execution_release = true`;
- ausgeschalteten VU- und VN-Carryover.

Er liefert einen kleinen synthetischen Vertragspayload mit
`execution_performed = true`, aber `simulation_performed = false`,
`automatic_historical_rule_selection_performed = false` und
`historical_full_equality_claimed = false`. Es wird kein Engine-Runner
aufgerufen.

## Validierung

- frische SQLite-Metadatenquelle mit genau einem validierten Queue-Eintrag;
- erfolgreicher Freigabecheck und Erststart;
- persistiertes Resultat und Verlauf mit genau einem Attempt;
- identischer zweiter POST wird idempotent gelesen und ruft den Fake-Adapter
  nicht erneut auf;
- wiederholte GET-Abfragen bleiben identisch;
- Frontend-Build sowie sichtbarer Desktop- und Mobil-Smoke.

## Grenzen

- keine Simulation und keine neue Fachlogik;
- kein produktiver Adapter im Browser-Smoke;
- kein Queue-Worker, automatischer Retry oder Polling;
- kein Browser-Upload, Dateipicker oder freier Pfad;
- keine automatische historische Regelwahl;
- keine historische Vollgleichheitsbehauptung.
