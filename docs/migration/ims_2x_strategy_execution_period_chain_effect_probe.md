# PR139: Isolierte Zwei-Perioden-Wirkungsprobe

Stand: 2026-09-11

## Einordnung

PR138 prueft eine gespeicherte Periodenkette read-only an der
Run-Control-Grenze. PR139 verwendet erstmals genau eine solche Zwei-
Perioden-Kette fuer eine fluechtige Wirkungsprobe. Der neue Adapter
orchestriert ausschliesslich vorhandene VU-/VN-Periodenrunner und vorhandene
Carryover-Funktionen.

## C-zu-Python-Mapping

| Historischer Bezug | Python-Ziel | Bedeutung |
| --- | --- | --- |
| Periodenschleife in `ESS.C:71-75` | `run_strategy_execution_period_chain_effect_probe` | kleinster kontrollierter Ausschnitt aus Periode 1 und 2 |
| `IMSDATA.C:14`, `SIMLAENGE = 100` | `exact_two_period_horizon_required` | PR139 ist ein Testausschnitt und noch kein 100-Perioden-Lauf |
| historischer globaler Folgezustand | `apply_vu_foreign_info_carryover` und `apply_vn_state_carryover` | explizite, getrennt freigegebene Zustandsfortschreibung |
| bestehende VU-/VN-Regeln | `run_loaded_explicit_period` | unveraenderte Ausfuehrung bereits portierter Snapshot-Logik |

Ketten-ID, Digest und atomare Freigabegrenzen haben keine direkte
historische C-Entsprechung. PR139 fuegt keine Fachregel hinzu.

## Umsetzung

`ims.api.strategy_execution_period_chain_effect_probe` definiert:

- einen versionierten Vertrag, Request und Ergebnis;
- die Wiederverwendung des vollstaendigen PR138-Freigabechecks;
- die Beschraenkung auf genau zwei Kandidaten und den Uebergang 1 nach 2;
- die erneute read-only Kandidatenaufloesung und Digestpruefung;
- das Laden beider isolierten Kandidatenkopien vor dem ersten Runneraufruf;
- die getrennte Anwendung beider gespeicherten Carryover-Flags;
- zwei fluechtige Periodenwirkungen und eine Uebergangsdiagnose.

Die gemeinsame Zustands- und Wirkungsprojektion aus der Einperiodenprobe
wird wiederverwendet. Dadurch bedeuten dieselben Felder in beiden Proben
dasselbe.

## Atomarer Fehlerstopp

Vor Periode 1 muessen Kette, beide Kandidaten, beide Digests, beide Kontexte
und die Akteursidentitaeten gueltig sein. Scheitert diese Vorbereitung, wird
kein Runner aufgerufen.

Scheitern Carryover oder Periode 2, liefert die Fehlerantwort kein
Teilergebnis: keine Wirkung aus Periode 1 und keine Uebergangsdiagnose. Die
Anzahl bereits versuchter
Runner- und Carryover-Aufrufe bleibt zur Diagnose sichtbar. Gespeicherte
Kette und Kandidaten werden nie als Arbeitszustand verwendet.

## API

- `GET /api/run-control/strategy-period-chain-effect-probe-contract`
- `POST /api/run-control/strategy-period-chain-effect-probe`

FastAPI und der Starlette-Fallback verwenden denselben Handler. Der Browser
kann keine Datenbank-, Fixture-, Ausgabe- oder freien Carryover-Felder
uebergeben.

## Validierung

Die Tests sichern:

- den exakten Request und die ausdrueckliche Ausfuehrungsfreigabe;
- eine echte Zwei-Perioden-Probe mit erneut geprueften Kandidaten;
- alle vier Kombinationen der VU-/VN-Carryover-Flags;
- reproduzierbare Wiederholung ohne gespeicherte Idempotenz;
- Ablehnung groesserer Horizonte vor dem ersten Runner;
- eine nachtraeglich fehlende Kandidatenreferenz vor dem ersten Runner;
- vollstaendiges Laden beider Kandidaten vor dem ersten Runner;
- Unterdrueckung partieller Ergebnisse bei einem Fehler in Periode 2;
- unveraenderte SQLite-Daten und ausbleibende Ausgabedateien;
- Methoden und Statuscodes in FastAPI und Starlette.

## Bewusste Grenzen

PR139 legt weder Queue-Eintrag noch Idempotenz- oder Ergebnisdatensatz an.
Die Probe ist kein Workbench-Start, kein allgemeiner Mehrperiodenrunner und
keine vollstaendige Simulation. Es gibt keinen Legacy-Vergleich und keine
historische RNG- oder Vollgleichheitsbehauptung. `incomming/` bleibt
unversioniert.

## Naechster Schritt

PR140 soll die Zwei-Perioden-Probe ueber einen ausdruecklichen Workbench-
Start mit dauerhafter Idempotenz und unveraenderlichem Ergebnisverlauf
kontrollieren. Der Ausbau auf groessere Horizonte bleibt davon getrennt.
