# PR147: Read-only Horizontvertrag bis 100 Perioden

Stand: 2026-09-16

## C-zu-Python-Mapping

| Historischer Bezug | Heutige Grenze | Bedeutung und Abweichung |
| --- | --- | --- |
| `ESS.C:71-75` | `execution_period_chain_horizon_contract.py` | Aufsteigende lokale Perioden 1 bis N; der Vertrag selbst ruft keine Periode auf |
| `IMSDATA.C:14`, `SIMLAENGE = 100` | vier getrennte Zielhorizonte 10/25/50/100 | 100 ist Obergrenze eines Einzellaufs, keine Zusage eines 300-/500-Perioden-Laufs |
| VU-/VN-Vorperiodenzustand | vorhandene Carryover-Pfade und kanonische Kettenflags | maximal zwei explizite Carryover-Aufrufe je Uebergang, ohne neue Regel |
| PR145/146 | gespeicherter Fuenf-Perioden-Nachweis | eine laengere Kette muss dessen fachliche Wirkung 1-5 exakt beibehalten |

Die historischen Limits beschreiben keine Laufzeit, keinen Speicherverbrauch
und keine Reproduzierbarkeit alter Zufallsfolgen. Alle Ressourcenbudgets sind
neue Sicherheitsentscheidungen und beduerfen vor jeder Freigabe Messungen.

## Vertrag statt Freigabe

`ims.strategy-execution-period-chain-horizon-contract.v1` ist unter
`GET /api/run-control/strategy-period-chain-horizon-contract` in FastAPI und
Starlette lesbar. Es gibt keinen Schreib- oder Startendpunkt fuer die vier
Folgehorizonte. Der bestehende Fuenf-Perioden-Start bleibt freigegeben; sein
read-only Bestandsflag wurde entsprechend PR146 berichtigt.

Die vier Horizonte enthalten je die exakte Zahl von Kandidaten, Uebergaengen,
Runner- und Carryover-Aufrufen, Gesamt- und Periodenzeitbudgets, Speicher-
und Payloadgrenzen sowie einen Mindestplatz vor dem Start. Die Werte stehen
im [PR147-Plan](../plans/ims_2x_strategy_execution_period_chain_horizon_contract_plan.md).
Keine Messung oder isolierte Durchsetzung wird durch den GET-Aufruf behauptet.

## Freigabevoraussetzungen

Vor dem ersten Runner muessen alle Kandidaten mit Digests und Kontexten
erneut geprueft, die vollstaendige Kette und vier bzw. N-1 Uebergaenge
validiert und ein erfolgreicher gespeicherter Fuenf-Perioden-Nachweis
verifiziert sein. Der Prefix 1-5 wird vor Periode 6 ohne Toleranz semantisch
und als kanonisches JSON verglichen; Huellenfelder eines laengeren Horizonts
zaehlen nicht zur fachlichen Prefixwirkung. Die eingeschlossenen Wirkungs-
und Uebergangsfelder entsprechen exakt der bereits versionierten PR142-
Prefixprojektion; reine Ketten-, Lauf- und Ergebnisidentitaeten sind
ausgeschlossen. Der Fuenf-Perioden-Nachweis enthaelt bereits den exakten
Prefix 1-2.

Vor Freigabe sind ein isoliert abbrechbarer Worker, monotone Zeitmessung,
RSS-/Payload-/Freiplatzmessung, Lasttests je Horizont und fail-closed
Budgetpruefungen nachzuweisen. Thread-Abbruch reicht nicht. Nach manuellem
Abbruch, Budgetverletzung oder erstem Fehler: kein Teilergebnis, kein
Checkpoint, keine automatische Wiederholung; ein auditierbarer Versuch ist
zulaessig. Nur ein vollstaendiges, digestgeprueftes Ergebnis darf atomar
gespeichert werden.

## Pruefung und offene Punkte

- Unit-Tests belegen jede Tabellenzeile, die gesperrten Freigaben, Prefix-,
  Abbruch- und Fehlerpolitik und unveraenderliche Vertragsdaten.
- API-Tests belegen identisches GET in FastAPI und Starlette, 405 fuer
  POST/PUT/DELETE sowie fehlenden Datenbank- und Runnerzugriff.
- PR148 muss 10/25/50 messen und die Schutzgrenzen tatsaechlich durchsetzen;
  PR149 entscheidet nach eigenem Lasttest ueber 100. Uebersteigt ein
  realistischer Lauf die gesetzten Obergrenzen, bleibt er gesperrt, bis ein
  neuer versionierter Vertrag fachlich und technisch begruendet ist.

Keine neue VU-/VN-Fachlogik, kein automatischer Start, keine Ausgabedatei,
kein Zugriff auf `incomming/`, keine historische RNG- oder
Vollgleichheitsbehauptung.
