# PR157: Versicherer-Modellbilanz in Workbench und XLSX

Stand: 2026-09-16

## Fachliche Einordnung

Die Workbench rechnet fuer einen Versicherer die beiden in PR156 definierten
Modellsparten Kfz und Sach-Haftpflicht aus **expliziten Szenariowerten**.
Vorbelegte Werte sind ein editierbares Beispiel, keine Marktdaten. Beide
Sparten haben dieselbe Versicherer-ID und 1 bis 100 gleiche Perioden.
Gesamtwerte sind die feldweise exakte Summe der beiden Sparten; Anfangs-
und Schlussidentitaet sowie Carryover werden erneut geprueft. Ein Fehler
in einer Sparte verhindert das ganze Ergebnis und den Download.

| Ursprung / Vertrag | PR157-Umsetzung | Grenze |
| --- | --- | --- |
| `IMSDATA.C`, `classVU.Sp[1/2]` und `IMS.E` | Herkunftshinweis in `insurer_balance.py` und Workbench | Historische Positionen bleiben ohne Kfz-/Sach-Haftpflicht-Zuordnung. |
| PR155-Bilanzfelder und PR156-Einzelspartenrechnung | `insurer_balance.py` summiert alle 14 Betragsfelder mit `Decimal`. | Nur vereinfachte Modellbilanz; keine gesetzliche Rechnungslegung. |
| PR156-Versionseingang | `GET /api/accounting/insurer-balance-contract` und `POST /api/accounting/insurer-balance` | Zustandslos; keine Persistenz oder Runner-Anbindung. |
| Kanonische Ergebniszeilen | `POST /api/accounting/insurer-balance.xlsx` und `insurer_balance_workbook.py` | Export nur mit erneut geprueftem Ergebnis-Digest (`If-Match`). |
| Fachliche Ergebnisansicht | `frontend/src/ModelBalanceWorkbench.tsx` | Kein historischer Vollgleichheitsnachweis. |

## Bedienweg

In der Workbench unter **Versicherer-Modellbilanz** eine Versicherer-ID
waehlen, je Sparte Anfangsbestaende und Periodenfluesse eingeben und
**Bilanz berechnen** ausloesen. Die Tabs **Gesamt**, **Kfz** und
**Sach-Haftpflicht** zeigen Schlussbestaende, Periodenergebnis und eine
Zeitreihe. Jede Eingabeaenderung verwirft das angezeigte Ergebnis. Erst
nach einer gueltigen Rechnung steht **XLSX** bereit.

Das Arbeitsbuch enthaelt `Gesamt`, `Kfz`, `Sach-Haftpflicht` und
`Herkunft`. Betraege stehen als kanonische Dezimalstrings in **Textzellen**:
Excel veraendert deshalb keine Stellen unbemerkt, behandelt sie aber
ohne bewusste Umwandlung nicht als Zahlen fuer eigene Formeln oder Diagramme.
Die Periodennummer ist eine Zahl. Ein numerischer Analyseexport mit
deklarierter Rundung ist eine separate Entscheidung.

## Pruefung und offene Punkte

Feste Zwei-Perioden-Faelle, ein 100-Perioden-Prefix, Bilanzidentitaeten,
Spartensumme, deterministischer Digest, spaeter Fehler, unguelige
Quellenangabe, XLSX-Zelltypen und API-Fehlerpfade sind getestet. Breite
und schmale Browseransicht samt negativem Eingabefall wurden geprueft.
Die Vereinfachungen aus PR155/PR156 gelten unveraendert: keine
Forderungen, Rueckversicherung, Steuern oder Solvency-II-Berechnung.
Leben und Kranken sowie eine Vier-Sparten-Konsolidierung folgen separat.
