# PR169b: Kontrollierte Kranken-Periodenkette

Stand: 2026-09-17
Eingang: `ims.health-period-chain-input.v1`
Ergebnis: `ims.health-period-chain-result.v1`
Schnittstelle: `ims.accounting.health_period_chain.run_health_period_chain`

## Ursprung und fachliche Grenze

| Ursprung | Python | Entsprechung und Grenze |
| --- | --- | --- |
| `IMSDATA.C`: periodische VU-Bestaende `Sp[1/2]` und VN-Risiken `Rk[1/2]` | `ims.accounting.health_period_chain` | expliziter IMS-2.x-`health`-Bestand mit Periodenuebergang; keine belegte historische Zuordnung der zweiten Schadensparte zu moderner Krankenversicherung. |
| `IMS.E`: Aggregation alter Praemien, Schaden- und Reservefelder | PR169a-Quellenplan | keine Wiederverwendung alter Preis-, Wechsel- oder Schadenregeln. |
| PR169: `ims.accounting.health_model_balance` | Einperioden-Bilanzschritt | unveraenderte Buchung von Beitrag, angefallener/bezahlter Leistung, Anlage, Aufwand und Kapital; neue Bestandsbewegung erst nach diesem Schritt. |

Die Kette ist eine **neue, begrenzte IMS-2.x-Modellrechnung**. Sie
reproduziert keinen historischen Lauf, keine individuellen Policen,
Tarife, Morbiditaet oder gesetzliche Alterungsrueckstellung. Eine
IMS-Modellperiode ist nicht automatisch ein Kalenderjahr.

## Eingang und Zeitordnung

Ein Eingang enthaelt die festen Vertragsversionen, eine VU-ID 1-25,
`health`, `source_kind = versioned_health_period_chain`, einen
PR169a-Quellenplan (`sources`), den geprueften Bilanzanfang (`opening`)
und pro Periode exakt `benefits_paid`, `investment_result`,
`operating_expense_paid`, `capital_contribution` und
`capital_distribution`. Diese fuenf Werte bleiben explizite Szenariowerte.
Die Vorlage steht in `tests/fixtures/health_period_chain_v1.json`.
Freigegeben sind genau 1, 2, 5, 10, 25, 50 und 100 Perioden; Quellenplan
und Kette muessen denselben Horizont, dieselbe VU und dieselbe Zahl
anfangs aktiver Vertraege haben. `scenario_id` und `variant_id` kommen
aus dem validierten Quellenplan.

Zuerst gelten die zum Periodenbeginn aktiven Vertraege. Deren Zahl mal
`premium_per_opening_policy` ergibt die periodengleich vereinnahmten
Beitraege; mal `benefit_per_opening_policy` den exogen angefallenen
Leistungsbetrag. Die PR169-Bilanz bucht angefallene Leistungen als
Aufwand und offene Verpflichtung. `benefits_paid` mindert diese
Verpflichtung und die Kasse, nicht nochmals den Gewinn. **Erst danach**
gilt `Schlussbestand = Anfangsbestand - Abgang + Neugeschaeft`. Der
Schluss von Kasse, Verpflichtung, Eigenkapital und Vertragszahl wird
vollstaendig zum naechsten Anfang. Ausgeschiedene Vertraege tragen noch
die aktuelle Periodenexposition; neue erst die naechste. Leistung ist
kein frei abschaltbarer VU-Strategiehebel.

## Abnahme und Grenzen

Der PR169a-Plan und **alle** expliziten Periodenfluesse werden vor der
ersten Rechnung geprueft. Jede Periode verwendet den PR169-Einperioden-
Rechenschritt ohne Aenderung des bisherigen geschlossenen Falls. Die
Rechnung hat hoechstens 100 Schritte und maximal 1 MB kanonische
Zeilenausgabe. Anfangs-/Schlussidentitaet, Nichtnegativgrenzen und das
12+4-Betragsbudget gelten auch ueber lange Folgen. Bei jedem Fehler,
auch erst in Periode 100, oder bei Abbruch liefert die Funktion **null**
Ergebniszeilen. Sie schreibt keine Datei und speichert keinen Teilstand.

Die Tests pruefen die exakt gleichen Prefixe aller sieben Horizonte,
deterministische Wiederholung, Bestands-/Bilanzgleichungen, einen
geschlossenen Zwei-Perioden-Fall gegen PR169, Grenz- und Fehlerfaelle,
Abbruch sowie ein grobes Laufzeit-/Speicherbudget. Die reine
Python-Funktion ist noch keine API-Freigabe oder bedienbare Simulation.
PR169c plant erst Idempotenz, unveraenderliche Ergebnisablage und
CSV/JSON/XLSX; PR169d den Workbench-Start. Weder Solvency-II-Bewertung
noch historische Vollgleichheit werden behauptet.
