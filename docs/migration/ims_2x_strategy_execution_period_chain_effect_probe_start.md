# PR140: Zwei-Perioden-Wirkungsprobe kontrolliert starten und nachweisen

Stand: 2026-09-14

## Einordnung

PR139 fuehrt eine verifizierte Kette aus Periode 1 und 2 fluechtig auf
isolierten Kandidatenkopien aus. PR140 ergaenzt die Bedien- und
Nachweisschicht: Ein manueller Workbench-Start reserviert seine Idempotenz
dauerhaft, ruft den PR139-Pfad hoechstens einmal auf und speichert nur ein
vollstaendiges Ergebnis.

## C-zu-Python-Mapping

| Historischer Bezug | Python-Ziel | Fachliche Entsprechung |
| --- | --- | --- |
| Periodenschleife in `ESS.C:71-75` | `run_strategy_execution_period_chain_effect_probe` | unveraenderter PR139-Ausschnitt aus Periode 1 und 2 |
| `IMSDATA.C:14`, `SIMLAENGE = 100` | exakte Zwei-Perioden-Startgrenze | kleinster Bediennachweis, noch kein historischer Gesamthorizont |
| historischer manueller Programmstart | `start_strategy_execution_period_chain_effect_probe` | ausdrueckliche auditierte Freigabe mit atomarem Idempotenzanspruch |
| unmittelbar sichtbare Folgewirkung | gespeichertes PR139-Ergebnis und Workbench | Vorher-/Nachher- und Carryover-Nachweis ohne neue Regelableitung |

PR140 portiert keine C-Regel. Ketten-ID, Idempotenzschluessel,
Ergebnisdigest und SQLite-Historie sind moderne Kontroll- und
Beobachtbarkeitsgrenzen.

## Persistenter Start

`ims.api.strategy_execution_period_chain_effect_probe_start` akzeptiert
exakt den PR139-Request. Der Server prueft Ketten-ID, erwarteten Volldigest,
gespeicherte Kette und die ausdruecklichen Freigaben vor dem Start erneut.

Ein `BEGIN IMMEDIATE` erzwingt:

- derselbe Schluessel und dieselbe Freigabe lesen das vorhandene Ergebnis;
- derselbe Schluessel mit veraenderter Freigabe wird abgewiesen;
- parallele Starts derselben Kette werden blockiert;
- je Kette wird hoechstens ein erfolgreiches Ergebnis gespeichert;
- nach einem Fehler ist nur ein neuer manueller Versuch mit neuem Schluessel
  zulaessig;
- automatische Wiederholungen und Queue-Worker bleiben gesperrt.

Ein Fehler in Periode 2 speichert kein Ergebnis aus Periode 1. Im
Versuchsdatensatz bleiben nur Fehler, Zeitpunkte sowie die Anzahl bereits
erreichter Runner-, Carryover- und Kandidatenpruefungen sichtbar.

## SQLite-Nachweis

`strategy_execution_period_chain_effect_probe_attempts` speichert Freigabe,
Idempotenz, Status, Zeitpunkte, Fehler und Aufrufzaehler.

`strategy_execution_period_chain_effect_probe_results` speichert genau ein
vollstaendiges PR139-Ergebnis je Kette. Der Ergebnisinhalt erhaelt einen
eigenen SHA-256-Digest. Read-only Zugriffe pruefen erneut:

- aktuellen Kettendigest;
- Ergebnisdigest und Requestidentitaet;
- PR139-Schemaversion;
- exakt die Perioden 1 und 2 sowie den Uebergang 1 nach 2;
- zwei Runneraufrufe, vollstaendige Ausfuehrung und fehlendes Teilresultat;
- fehlende Ausgabedateien und `simulation_performed = false`.

Ein Ergebnis wird weder aktualisiert noch ueberschrieben.

## API

- `GET /api/strategies/execution-period-chains`;
- `GET /api/run-control/strategy-period-chain-effect-probe-start-contract`;
- `POST /api/run-control/strategy-period-chain-effect-probe-start`;
- `GET /api/run-control/strategy-period-chain-effect-probe-result/{chain_id}`;
- `GET /api/run-control/strategy-period-chain-effect-probe-history/{chain_id}`.

Der erste erfolgreiche Start antwortet mit `201`, die idempotente
Wiederholung mit `200`. Unbekannte Ketten ergeben `404`; Integritaets-,
Idempotenz- und Laufkonflikte ergeben `409`. Ergebnis-, Verlaufs- und
Uebersichtsabfragen schreiben nichts und fuehren nichts aus.

## Workbench

Der Tab `Periodenkette` verwendet nur serverseitig verifizierte
Kettenkurzsaetze. Der Browser sendet Ketten-ID, erwarteten Digest,
Freigabedaten und die ausdrueckliche Zwei-Perioden-Bestaetigung. Er sendet
keine Ketteninhalte, Kandidaten, Carryover-Flags oder freien Pfade.

Nach erfolgreichem Start zeigt die Workbench die beiden Periodenwirkungen,
den gespeicherten VU-/VN-Carryover, Ergebniszeit, Ergebnisdigest und alle
Startversuche. Der Start ist danach auch in der Oberflaeche gesperrt; der
Server erzwingt dieselbe Grenze unabhaengig davon.

## Validierung

Die Tests sichern:

- verifizierte read-only Kettenuebersicht ohne Tabellenerzeugung;
- ersten Start mit exakt zwei Runneraufrufen;
- idempotente Wiederholung ohne weiteren Runner;
- Konflikt bei abweichender Wiederholung und zweitem Ergebnisstart;
- atomare Blockade paralleler Starts;
- Fehler in Periode 2 ohne gespeichertes Teilresultat;
- manuellen Neuversuch nach Fehler;
- Ablehnung laengerer Horizonte vor dem ersten Runner;
- Erkennung manipulierter Ergebnisinhalte;
- FastAPI- und Starlette-Endpunkte samt Methoden und Statuscodes;
- Workbench-Vertrag und produktiven Frontend-Build.

## Grenzen und Anschluss

PR140 aendert weder VU-/VN-Regeln noch Carryover-Semantik. Es entstehen
keine fachlichen Ausgabedateien, kein Legacy-Vergleich und keine historische
RNG- oder Vollgleichheitsbehauptung. Die Probe ist noch keine allgemeine
Mehrperiodensimulation.

PR141 nimmt den Bedienpfad im Browser auf breitem und schmalem Viewport ab
und aktualisiert die Handbuchbilder. Erst danach wird der Horizont in
getrennten, deterministisch geprueften Stufen erweitert.
