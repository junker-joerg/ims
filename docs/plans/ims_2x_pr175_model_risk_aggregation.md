# PR175: Deklarierte Gegenpartei- und Betriebsverluste aggregieren

Stand: 2026-09-18
Status: umgesetzt; PR176 bleibt gesonderte Kapital- und Quellenentscheidung

## Ziel und Rechengrenze

PR175 baut auf dem vollstaendig neu berechneten PR174-Ergebnis auf. Die
vier dortigen Modulverluste werden um explizite Gegenpartei- und
operationelle Szenarioverluste ergaenzt. Daraus entsteht ein
**Modell-Stressverlust**, keine Solvency-II-Kapitalanforderung. Die
Eingabe und die Aggregationsannahmen sind versioniert; jeder erfolgreiche
Ausgang enthaelt Eingabe-, PR174-, PR173- und PR172-Digests.

| Eingang | Berechnung | Grenze |
| --- | --- | --- |
| PR174-Module | Betrag des negativen `model_proxy_change` je Modul, Summe je Risikogruppe | nur deklarierte Teilbestaende, keine Kapital-Kalibrierung |
| Gegenpartei-Fall | Aktiva-Teilposition mal deklarierter Ausfallverlustsatz; einmal auf 4 Stellen gerundet | nur ungestresste PR173-Aktiva, hoechstens ein Fall je Position; keine implizite Rueckversicherung |
| operationelles Ereignis | direkt deklarierter, nichtnegativer Modellverlust | kein aus Praemie oder Aufwand abgeleiteter regulatorischer OpRisk-Faktor |
| gemeinsamer Faktor | Ladung `a_i` je sechs Gruppen, 0..1; `corr(i,j)=a_i*a_j`, Diagonale 1 | nur nichtnegative Ein-Faktor-Korrelationen; stets positiv semidefinit, keine empirische Schaetzung |
| Verlustpuffer | separat deklarierte Kapazitaet und Anrechnung | Anrechnung <= Kapazitaet und <= Bruttoverlust; Unabhaengigkeit ist Anwenderannahme, nicht nachgewiesen |

Die sechs festen Gruppen sind `asset_market_value`,
`non_life_claim_obligation`, `life_obligation`,
`health_benefit_obligation`, `counterparty_model_loss` und
`operational_model_loss`. Alle sechs Faktorladungen muessen angegeben
werden, auch wenn eine Gruppe keinen Verlust hat. Fuer Gruppenverluste
`L_i >= 0` lautet die Bruttoaggregation
`sqrt((sum_i L_i*a_i)^2 + sum_i L_i^2*(1-a_i^2))`.
Erst danach wird der deklarierte Puffer abgezogen. Die Wurzel wird
einmal mit `ROUND_HALF_UP` auf vier Stellen gerundet; interne Rechnungen
verwenden `Decimal` mit fester Praezision. Die unkorrelierte Grenze
(`a_i=0`) und die voll gemeinsame Grenze (`a_i=1`) sind testbar.

Gegenpartei-Faelle duerfen nicht auf demselben Exposure wie ein
PR174-Marktmodul liegen. Operationelle Verluste und Puffer benoetigen
eine ausdrueckliche Annahmennotiz und Quellenkennung; ihre tatsaechliche
Unabhaengigkeit von anderen Positionen kann das Modell nicht belegen.
Ungueltige Quellen, Duplikate, Bereichsfehler, falsche Bilanzseite,
Doppelstress oder zu grosse Anrechnung liefern atomar keine Ergebniszeilen.

## Herkunft und Abgrenzung

| Ursprung | Umsetzung | Offener Punkt |
| --- | --- | --- |
| `IMSDATA.C`, `LV`/`KV`, `Rs`, `Sh`, `Pr` | kein direkter Port | historisches Zweispartenmodell enthaelt weder vier moderne Sparten noch diese Risikoaggregation |
| `ims.accounting.solvency_risk_modules` | neu berechnete PR174-Teilwirkungen | Szenariosaetze sind nicht regulatorisch kalibriert |
| `ims.accounting.solvency_scenario_shocks` | nicht ueberlappende deklarierte Aktiva-Teilpositionen | Gegenparteiqualitaet und Recovery sind nicht beobachtet |
| PR175-Szenariodeklaration | Gegenpartei-Faelle, Betriebsereignisse, Faktorladungen, Modellpuffer | Herkunft und Wirkung des Puffers beduerfen fachlicher Pruefung |

Das [EIOPA-Regelwerk, Art. 103](https://www.eiopa.europa.eu/rulebook/solvency-ii-single-rulebook/article-2190_en)
trennt Basic SCR, operationelles Risiko und Verlustabsorption in der
Standardformel. Die hiesige Ein-Faktor-Szenariorechnung **implementiert
diese Formel nicht**. Sie liefert weder SCR/MCR noch anrechenbare
Eigenmittel, Bedeckungsquote oder Einhaltungsaussage. Rechtsstand,
Kalibrierung, Korrelationen, technische Rueckstellungen und Steuereffekte
sind fuer PR176 gesondert zu klaeren. Keine historische Vollgleichheit.

## Abnahme

- Versionierter, zustandsloser Kern und GET-Vertrag/POST-Berechnung in
  FastAPI und Starlette, ohne Speicherung, Runner oder Simulation.
- Tests fuer Quellen-Digests, Gegenpartei- und Betriebsverlust, Rundung,
  Grenzladungen, reproduzierbare Ausgabe und atomare Fehlerfaelle.
- PR176 darf die Modellverlustsumme nicht stillschweigend als SCR
  weiterreichen; zuerst sind Rechtsstand, Kalibrierung und Quellen zu
  entscheiden.

## Umsetzung und Validierung

`ims.accounting.solvency_risk_aggregation` stellt den versionierten
Eingang `ims.solvency-risk-aggregation-input.v1` und die atomare
Rechnung bereit. `GET /api/accounting/solvency-risk-aggregation-contract`
und `POST /api/accounting/solvency-risk-aggregation` sind in FastAPI
und Starlette verfuegbar. Nur der eigene PR174-Eingang wird angenommen;
PR174, PR173, PR172 und PR170 werden serverseitig erneut berechnet.
`tests/test_solvency_risk_aggregation.py` prueft die sechs Komponenten,
Quellenbindung, Ein-Faktor-Grenzen, Rundung und Fehleratomaritaet.
`tests/test_api_solvency_risk_aggregation.py` prueft beide API-Varianten
ohne Speicherung oder Runner.
