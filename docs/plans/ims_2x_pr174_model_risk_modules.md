# PR174: Begrenzte Modell-Risikomodule

Stand: 2026-09-18
Status: umgesetzt; PR175 Gegenpartei, operationelles Risiko und Aggregation folgt separat

## Ziel und Vertrag

PR174 berechnet fuer benannte, von PR173 gepruefte Modell-Teilbestaende
einen einfachen relativen Szenariostress. Das ist eine didaktische
Wirkungsrechnung fuer ein Managementseminar, **keine** Solvency-II-
Standardformel, SCR-Teilkapitalanforderung oder Kalibrierung.

Der versionierte Eingang enthaelt eine vollstaendige PR173-Eingabe mit
**leerer** `shocks`-Liste. PR173 berechnet PR172 und PR170 serverseitig
neu, validiert Exposures und liefert den Quelldigest. PR174 nimmt je
Modulparameter `module_id`, `module_kind`, `exposure_id`, `stress_rate`,
`parameter_source_kind` und `assumption_note` entgegen. Die Quelle muss
`scenario_declared_not_regulatory` sein. Ein Exposure darf hoechstens
einen Modulparameter tragen. Nicht zugeordnete Exposures bleiben
unveraendert; eine Modulverkettung findet nicht statt.

| Modellmodul (`module_kind`) | Zulaessige PR173-Position | Delta |
| --- | --- | --- |
| `asset_market_value` | Aktiva in Kfz, Sach-Haftpflicht, Leben oder Kranken | `-base_amount * stress_rate` |
| `non_life_claim_obligation` | Passiva in Kfz oder Sach-Haftpflicht | `+base_amount * stress_rate` |
| `life_obligation` | Passiva in Leben | `+base_amount * stress_rate` |
| `health_benefit_obligation` | Passiva in Kranken | `+base_amount * stress_rate` |

`stress_rate` ist ein szenariodeklarierter Dezimaltext von 0 bis 1 mit
hoechstens vier Nachkommastellen. Das Produkt wird einmal auf vier
Nachkommastellen mit `ROUND_HALF_UP` gerundet. Fuer jede Modulzeile
werden Basis, Satz, Delta, Nach-Schock-Betrag und Veraenderung des
PR172-Modell-Eigenmittel-Proxys ausgegeben. Eine Summe oder
Diversifikation **zwischen Modulen** wird in PR174 nicht ausgewiesen;
das gehoert in PR175. Weder Zinsduration noch Schadenhaeufigkeit,
Sterblichkeit, Morbiditaet oder Rueckversicherung werden aus dem
historischen Modell implizit abgeleitet.

## Herkunft und offene Fragen

| Ursprung | Python-Entsprechung | Grenze |
| --- | --- | --- |
| `IMSDATA.C`: `Sp[1/2]`, `Rs`, `Sh`, `Pr` | kein direkter Port | zwei historische Schadenrisiken und Reserven, keine vier modernen Bilanz-Exposures oder Standardformel |
| `ims.accounting.solvency_model_balance` | durch PR173 neu berechnete Modellpositionen | Modellwaehrung, kein EUR-Marktwert und keine regulatorischen Eigenmittel |
| `ims.accounting.solvency_scenario_shocks` | validierter, ungeschockter Exposure-Bestand und Treiber-Ziel-Mapping | deklarierte Teilbestaende sind fachlich nicht unabhaengig verifiziert |
| Szenarioparameter | `ims.accounting.solvency_risk_modules` | relative Stresssaetze sind Annahmen des Anwenders, keine regulatorischen Faktoren |

Das [EIOPA-Regelwerk, Art. 101](https://www.eiopa.europa.eu/rulebook/solvency-ii-single-rulebook/article-2188_en)
verlangt fuer ein SCR die Erfassung quantifizierbarer Risiken und eine
Einjahreskalibrierung. Beides wird hier nicht geleistet. Auch
Gegenpartei-, operationelles Risiko, Korrelationen, Verlustabsorption,
MCR und Bedeckungsquote fehlen. Rechtsstand und Kalenderbezug der
IMS-Periode bleiben ungeklaert; keine historische Vollgleichheit.

## Abnahme

- Versionierter, zustandsloser Kern mit expliziten Parametern und
  PR173-/PR172-Digest; Fehler atomar ohne Modulzeilen.
- Tests fuer alle vier Modellmodule, Kfz und Sach-Haftpflicht,
  Richtung, Monotonie, Rundung, unbetroffene Exposures und exakten
  Anschluss des berechneten Deltas an eine PR173-Wirkungszeile.
- Ablehnung von unzulaessigem Ziel, doppelter Zuordnung, Satz ausserhalb
  0..1, fehlender Quellenkennzeichnung und nichtleerem PR173-Schock.
- FastAPI und Starlette-Fallback ohne Speicherung, Runner oder UI.

Offen fuer PR175/176: fachlich begruendete Kalibrierungsquellen,
Gegenpartei- und operationelles Risiko, Aggregation, Diversifikation,
Verlustabsorption sowie Kapitalanforderungen. Vor einer regulatorischen
Verwendung sind separate Rechts- und Aktuariatspruefungen erforderlich.

## Umsetzung und Validierung

`ims.accounting.solvency_risk_modules` liefert den Vertrag
`ims.solvency-risk-modules-input.v1`, prueft die ungeschockte PR173-
Quelle und veroeffentlicht je Modul die gerundete Einzelwirkung mit
Quell- und Eingabedigest. `GET /api/accounting/solvency-risk-modules-contract`
und `POST /api/accounting/solvency-risk-modules` sind fuer FastAPI
und Starlette-Fallback verfuegbar. Es gibt keine Speicherung, keinen
Runner und keine UI-Eingabe.

`tests/test_solvency_risk_modules.py` prueft Quellenbindung, Richtung,
Rundung, vier Treiber, beide Schadensparten, unveraenderte Positionen,
PR173-Gleichlauf der abgeleiteten Deltas und atomare Fehlerfaelle.
`tests/test_api_solvency_risk_modules.py` prueft beide API-Varianten,
Methodengrenzen, Fehlerantworten sowie fehlende Schreib-/Laufeffekte.
