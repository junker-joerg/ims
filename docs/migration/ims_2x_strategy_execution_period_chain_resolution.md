# PR135: Kandidatenreferenzen und Kettenkontext aufloesen

Stand: 2026-09-11

## Einordnung

PR134 prueft Form, Identitaetsreferenzen, Horizont und Uebergaenge eines
Periodenketten-Eingangs ohne Speicherzugriff. PR135 schliesst daran einen
read-only Speicher- und Kontextabgleich an. Eine erfolgreiche Antwort belegt,
dass alle genannten Kandidaten unveraendert gespeichert und untereinander
anschlussfaehig sind. Sie ist noch keine gebaute oder ausfuehrbare Kette.

## C-zu-Python-Mapping

| Historischer Ursprung | Python-Ziel | Bedeutung |
| --- | --- | --- |
| `IMSDATA.C`, `SIMLAENGE = 100` | Abgleich von `simulation_context.max_periods` | gemeinsamer Laufhorizont aller Kandidaten |
| periodenindizierte VU-/VN-Strukturen in `IMSDATA.C` | Abgleich von Identitaets- und Kontextperiode | jeder Kandidat gehoert eindeutig zu seinem Kettenschritt |
| globale VU-/VN-Population des historischen Laufs | kettenweiter ID-Mengenabgleich | Carryover darf spaeter nicht zwischen verschiedenen Akteursmengen erfolgen |

PR135 fuehrt keine neue Regel, Ziehung oder Zustandsfortschreibung aus.

## Umsetzung

`ims.api.strategy_execution_period_chain_resolution` liefert:

- `ims.strategy-execution-period-chain-resolution-contract.v1`;
- `ims.strategy-execution-period-chain-resolution.v1`;
- den vorgeschalteten PR134-Validator;
- read-only Kandidatenauflosung ueber die vorhandene PR127-Ablage;
- erneute Inhalts-, Digest-, ID- und Metadatenpruefung durch den vorhandenen
  Kandidatenleser;
- Abgleich von Referenz und gespeichertem Kandidaten;
- Abgleich von `period`, `run_index` und `max_periods`;
- kettenweiten Abgleich von BAV-, VU- und VN-Identitaeten;
- atomare Kandidatenzusammenfassungen nur bei vollstaendigem Erfolg.

FastAPI und der Starlette-Fallback stellen Vertrag und POST-Pruefung unter
denselben Pfaden bereit. Die Datenbankquelle stammt allein aus der
serverseitigen Workbench-Konfiguration.

## Validierung

Die Tests verwenden zwei echte, kanonisch gebaute Kandidaten in einer
temporaeren SQLite-Ablage und sichern:

- erfolgreiche, deterministische Aufloesung von Periode 1 und 2;
- Abbruch vor dem Speicherzugriff bei ungueltigem PR134-Eingang;
- atomare Blockade bei fehlendem Kandidaten;
- erneute Erkennung eines veraenderten Referenzdigests;
- Erkennung eines nachtraeglich manipulierten gespeicherten Inhalts;
- Blockade bei abweichendem Laufindex;
- Blockade bei wechselnder VU-Identitaet trotz formal gueltigem Digest;
- unveraenderte SQLite-Datei sowie ausbleibende Carryover- und Runneraufrufe;
- API-Methoden-, Pfad- und Konfigurationsgrenzen.

## Bewusste Grenzen

PR135 berechnet keinen Kettendigest und erzeugt kein neues Kettenobjekt. Die
aufgeloesten Kandidaten werden nicht erneut materialisiert und nicht
gespeichert. Carryover, Periodenrunner, Ergebnisablage und UI-Start bleiben
gesperrt.

Aus dem Speicher- und Kontextabgleich folgt weder eine Reproduktion eines
historischen RNG-Laufs noch eine historische Vollgleichheit.

## Naechster Schritt

PR136 bildet aus einem vollstaendig erfolgreichen PR135-Ergebnis inzwischen
eine kanonische fluechtige Periodenkette und ihren Gesamtdigest. PR137 soll
sie unveraenderlich und idempotent speichern. Carryover und Ausfuehrung
bleiben weiterhin getrennte spaetere Freigaben.
