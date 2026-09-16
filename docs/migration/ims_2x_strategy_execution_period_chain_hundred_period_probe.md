# PR149: Technischer 100-Perioden-Lauf

Stand: 2026-09-16

## Herkunft und Mapping

| Historische Quelle | Heutige Komponente | Fachliche Bedeutung und Grenze |
| --- | --- | --- |
| `ESS.C:71-75` | `strategy_execution_period_chain_extended_probe.py` | Aufsteigende lokale Perioden 1-100, genau ein Runneraufruf je Periode |
| `IMSDATA.C:14`, `SIMLAENGE = 100` | `execution_period_chain_horizon_contract.py` v3 | 100 ist Obergrenze eines Einzellaufs; 300-/500-Zeilen-Fenster werden nicht als Einzellaeufe gedeutet |
| Historische Vorperiodenwerte | vorhandene VU-/VN-Carryover-Funktionen | 99 kanonische Uebergaenge mit hoechstens 198 expliziten Carryover-Aufrufen; keine neue Regel |
| Gespeicherter PR145-Nachweis | unveraenderte PR148-Prefixprojektion | Perioden 1-5 und Uebergaenge 1-4 stimmen vor Periode 6 semantisch und bytegenau ueberein |

Der vorhandene isolierte Prozesspfad akzeptiert mit dem versionierten
`ims.strategy-execution-extended-probe-request.v2` nun auch 100 Perioden.
Der v1-Eingang bleibt strikt auf 10/25/50 begrenzt und liefert weiterhin
den v1-Ergebnisvertrag. Fuer 100 werden alle Kandidaten und Kontexte vor
dem ersten Runner erneut geprueft; die explizite Freigabe muss ID und
Digest der vollstaendigen Kette treffen. Der HTTP-Pfad bleibt
`POST /api/run-control/strategy-period-chain-extended-effect-probe`.

## Getrennte 100er-Abnahme

Die kleine deterministische Windows-Fixtur wurde zweimal ausgefuehrt:
gleicher fachlicher Ergebnisdigest, genau 100 Perioden, 99 Uebergaenge,
198 Carryover-Aufrufe und unveraenderte gespeicherte Kandidaten. Eine
lokale Messung des ersten Laufs (keine Produktions- oder Skalierungszusage):

| Gesamtzeit | Peak-Worker-RSS | Kettenbytes | Ergebnisbytes |
| ---: | ---: | ---: | ---: |
| 0,72 s | 44,2 MB | 27.028 | 355.489 |

Die Obergrenzen bleiben 1.800 s gesamt, 30 s je Periode, 1.024 MiB
Peak-RSS, 64 MiB je Kette/Ergebnis und mindestens 256 MiB freier
Platz vor Start. Messung fehlt oder Grenze verletzt: der Worker wird
abgebrochen und es gibt kein Teilergebnis. Ein absichtlicher Fehler in
Periode 99 und ein erzwungener Speicherabbruch liefern keine Periode 100
und veraendern die Kandidatenablage nicht. Die API wurde mit einem echten
100er-Aufruf getestet; der alte v1-Eingang sperrt ihn weiter.

## Bewusste Restgrenze

Das ist ein **technisch verfuegbarer, fluechtiger** 100-Perioden-Lauf.
Identische Anfragen rechnen erneut; dauerhafte Idempotenz, unveraenderliche
Ergebnisablage, CSV/JSON/XLSX-Buendel und Workbench-Auswertung fehlen noch.
PR150 plant das Ergebnisbuendel, PR151 den Ergebnisarbeitsplatz und den
Bedienpfad; die konkrete persistierte Startgrenze ist dort separat zu
entscheiden. Auf anderen Plattformen ohne verlaessliche RSS-Messung bleibt
die Freigabe fail-closed. Es gibt keinen historischen RNG- oder
Vollgleichheitsnachweis, keine regulatorische Aussage und keinen Zugriff
auf `incomming/`.
