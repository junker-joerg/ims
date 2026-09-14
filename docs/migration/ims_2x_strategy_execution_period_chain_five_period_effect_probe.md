# PR144: Fuenf Perioden fluechtig ausfuehren

Stand: 2026-09-14

## Einordnung

PR144 erweitert die kontrollierte Wirkungsprobe von zwei auf genau fuenf
Perioden. Die vorhandenen VU- und VN-Regelrunner werden unveraendert je
Periode aufgerufen. Zwischen zwei Perioden werden ausschliesslich die vier
in der kanonischen PR143-Kette enthaltenen VU-/VN-Carryover-Schalter
angewendet.

Die Probe ist weiterhin keine allgemeine Mehrperiodensimulation. Sie
speichert weder Request noch Ergebnis und erzeugt keine fachliche
Ausgabedatei.

## C-zu-Python-Mapping

| Historischer Ursprung | Python-Ziel | Fachliche Entsprechung |
| --- | --- | --- |
| Periodenschleife `ESS.C:73-75` | `run_strategy_execution_five_period_effect_probe` | Perioden 1 bis 5 werden streng aufsteigend je einmal ausgefuehrt |
| Vorperiodenzustaende in den VU-/VN-Vektoren | vorhandene `apply_vu_foreign_info_carryover`- und `apply_vn_state_carryover`-Funktionen | explizite Fortschreibung in die isolierte Kopie der Folgeperiode |
| `SIMLAENGE = 100` in `IMSDATA.C:14` | feste PR144-Grenze von 5 | kleine moderne Freigabestufe, kein historischer Sonderhorizont |
| globale Periodennummer | vorhandenes `compute_global_period` | Prefixreferenz und Fuenf-Perioden-Probe muessen dieselben Globalperioden 1-2 abbilden |

PR144 portiert keine weitere C-Regel und aendert keine stochastische Logik.

## Vorbereitung und Ablauf

Der neue Pfad verarbeitet nur einen vollstaendigen PR143-Eingang. Vor dem
ersten Runneraufruf werden:

1. alle fuenf Kandidaten und vier Uebergaenge atomar gebaut und geprueft;
2. das gespeicherte PR140-Ergebnis samt Ketten- und Ergebnisdigest gelesen;
3. alle Kandidaten erneut aufgeloest und als isolierte Szenarien geladen;
4. Perioden, Laufkontext, Globalperioden und Akteursidentitaeten abgeglichen.

Danach folgen Periode und Carryover streng in der Reihenfolge 1 bis 5. Nach
Periode 2 wird die versionierte fachliche Prefixprojektion gebildet. Sie
enthaelt dieselben Perioden-, Zustands-, Regelaufruf-, Export- und
Carryoverfelder wie der PR142-Vertrag. Kettenidentitaet und Gesamthorizont
sind weiterhin ausgeschlossen.

## Exakter Prefixnachweis

Die Projektionen von gespeichertem Zwei-Perioden-Ergebnis und aktueller
Fuenf-Perioden-Probe muessen:

- als Python-Werte semantisch gleich sein;
- als kanonisches ASCII-JSON bytegleich sein;
- denselben SHA-256-Projektionsdigest besitzen;
- ohne numerische Toleranz auskommen.

Bei der ersten Differenz werden die Perioden 3 bis 5 nicht aufgerufen. Der
Fehlerpfad unterdrueckt bereits berechnete Teilwirkungen vollstaendig.

## API

- `GET /api/run-control/strategy-period-chain-five-period-effect-probe-contract`
- `POST /api/run-control/strategy-period-chain-five-period-effect-probe`

Der POST verwendet nur die konfigurierte SQLite-Ablage. Ein Datenbankpfad,
Ausgabeverzeichnis oder eingebetteter Kandidateninhalt ist nicht Teil des
Requests. Einen Workbench-Start gibt es in PR144 noch nicht.

## Grenzen

Das Ergebnis umfasst fuenf Periodenwirkungen, vier Uebergangswirkungen und
den Prefixnachweis nur im Arbeitsspeicher. Es entstehen keine Queue, keine
Idempotenzspur, keine Ergebnisablage und keine Ausgabedatei. `incomming/`
wird nicht gelesen und bleibt unversioniert.

Der Nachweis betrifft ausschliesslich die moderne fachliche Stabilitaet des
freigegebenen Zwei-Perioden-Prefixes. Er ist keine historische RNG- oder
Vollgleichheitsbehauptung. PR145 hat darauf einen kontrollierten,
idempotenten Serverstart mit unveraenderlicher Ergebnisablage aufgebaut.
PR146 darf ihn in der Workbench bedienbar machen und im Browser abnehmen.
