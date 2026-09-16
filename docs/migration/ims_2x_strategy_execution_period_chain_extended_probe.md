# PR148: Isolierte Wirkungsprobe ueber 10, 25 und 50 Perioden

Stand: 2026-09-16

## Ursprung und Umsetzung

| Historische Quelle | Python-Grenze | Bedeutung |
| --- | --- | --- |
| `ESS.C:71-75` | `strategy_execution_period_chain_extended_probe.py` | Perioden laufen lokal geordnet von 1 bis N, jeweils genau einmal |
| `IMSDATA.C:14` (`SIMLAENGE = 100`) | `execution_period_chain_horizon_contract.py` v2 | 10/25/50 freigegeben, 100 bleibt bis PR149 geschlossen |
| VU-/VN-Vorperiodenzustand | vorhandene VU-/VN-Carryover und kanonische Uebergangsflags | keine neue Regel oder geaenderte Aggregatsemantik |
| PR145 gespeicherter Lauf | exakte Projektion von Perioden 1-5 und Uebergaengen 1-4 | vor Periode 6 semantisch und bytegleich nachzuweisen |

Der API-Eingang `POST /api/run-control/strategy-period-chain-extended-effect-probe`
verlangt das versionierte PR148-Format, die vollstaendige Kette, die ID und
Digests des gespeicherten Fuenf-Perioden-Nachweises sowie eine ausdrueckliche
Run-Control-Freigabe fuer die erneut gebaute Kette. Es ist eine **fluechtige
Wirkungsprobe**, noch kein persistierter idempotenter Start: identische
Aufrufe fuehren erneut aus. UI-Start, Ergebnisablage, Checkpoints und
automatische Wiederholung bleiben geschlossen. Die 100-Perioden-Grenze ist
weiterhin gesperrt.

## Sicherheit und Fehler

Vor dem Worker werden Kandidaten/Kontexte/Digests der gesamten Kette und
der gespeicherte Fuenf-Perioden-Nachweis geprueft. Im getrennten Prozess
werden alle Kandidaten nochmals geladen und die Akteursidentitaeten
abgeglichen. Der Elternprozess ueberwacht mit monotoner Uhr Gesamtzeit
und jede Periode, die Peak-RSS des Workers, Ketten- und Ergebnisbytes und
freien Plattenplatz. Windows nutzt Prozess-Speicherzaehler, Linux `VmHWM`;
andere Plattformen ohne Messung bleiben gesperrt. Ein Fehler oder harter
Abbruch beendet den Worker und liefert nie ein Teilergebnis. Quellen werden
nach dem Lauf erneut gelesen; der gespeicherte Stand bleibt unveraendert.

Kleine deterministische Testfixtur auf Windows, zweimal je Horizont; eine
lokale Messung (keine Produktionsprognose):

| Perioden | Gesamtzeit | Peak-RSS | Kettenbytes | Ergebnisbytes |
| ---: | ---: | ---: | ---: | ---: |
| 10 | 0,35 s | 36,5 MB | 3.622 | 34.322 |
| 25 | 0,40 s | 37,0 MB | 7.522 | 87.761 |
| 50 | 0,49 s | 38,8 MB | 14.022 | 176.913 |

Negativtests erzwingen falschen Prefix, Runnerfehler in Periode 3,
Ausdruecklichkeits-/Digestfehler, manuellen Abbruch, RSS- und
Periodenbudgetabbruch. Eine echte Fachlast kann anders ausfallen; sie
bleibt bei Limitverletzung gesperrt. Der globale Periodenindex ist Teil
der stabilen Fachprojektion: Baseline und laengere Kette muessen ihn in
Perioden 1-5 identisch abbilden. Diese technische Gegenprobe reproduziert
keine unbelegten historischen Zufallsfolgen.

## Offene Punkte

PR149 prueft 100 Perioden gesondert. Ergebnisablage, persistierte
Idempotenz und Anwenderbedienung sind in den Folge-PRs zu schliessen.
`incomming/` wurde weder eingelesen noch versioniert. Kein Nachweis einer
historischen Vollgleichheit oder regulatorischen Aussage.
