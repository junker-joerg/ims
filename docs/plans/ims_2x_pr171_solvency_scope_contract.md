# PR171: Geltungs- und Quellenvertrag fuer die Solvency-II-Kapitalansicht

Stand: 2026-09-18
Status: umgesetzt; PR172 liefert separat einen Modell-Eigenmittel-Proxy,
keine regulatorische Eigenmittelbewertung. PR173 liefert separat ein
explizites Modell-Schock-Mapping, PR174 begrenzte Modellmodule;
PR175 liefert separat eine deklarierte Modell-Risikoaggregation;
PR176 ist der naechste Schritt fuer Quellen und Kapitalgrenze.

## Ziel und Grenze

Ein versionierter, rein lesbarer Vertrag trennt die vorhandene
Vier-Sparten-**Modellbilanz** von den erst geplanten aufsichtsrechtlichen
Groessen. Er nennt Begriffe, Datenherkunft, Rechtsquellen, Stichtage und
Freigabesperren. Er berechnet weder Eigenmittel noch SCR, MCR oder
Bedeckungsquoten und gibt keine regulatorische Konformitaet aus.

Die IMS-Periode ist keine automatisch gleich lange Kalender- oder
aufsichtsrechtliche Berichtsperiode. Ohne expliziten Bewertungsstichtag,
Rechtsstand und Umrechnung der Modellwaehrung gibt es keine Rechtsregime-
Auswahl und keine Kapitalberechnung.

## Herkunft und Begriffe

| Quelle | Heute verfuegbar | Keine stille Gleichsetzung mit |
| --- | --- | --- |
| `IMSDATA.C` (`Sp[1/2]`, `Rs`, `Pr`, `Sh`) | historische Zweisparten-Simulation | modernen Sparten, technischer Rueckstellung oder Solvenzbilanz |
| `ims.accounting.four_sector_balance` (`ims.four-sector-balance-result.v1`) | je VU/Periode explizit neu berechnete `closing_assets`, `closing_liabilities`, `closing_equity` und vier Allokationen | marktwertigen Vermoegenswerten, Best Estimate, Risikomarge oder anrechenbaren Eigenmitteln |
| Lebens- und Kranken-Teilmodelle | einfache Verpflichtungen und Zahlungsstroeme im Modell | vollstaendiger versicherungsmathematischer Bewertung |

Die regulatorischen Begriffe werden nur als Zielterminologie verwendet:
Solvenzbewertung der Aktiva und Passiva, versicherungstechnische
Rueckstellungen (Best Estimate plus Risikomarge), Basiseigenmittel,
anrechenbare Eigenmittel, SCR, MCR und Bedeckungsquote. Modell-Eigenkapital
ist keiner dieser Werte. Auch eine schlichte Summe von Sparten-SCRs waere
ohne Aggregations-, Diversifikations- und Verlustabsorptionsregeln falsch.

## Quellen- und Versionsstand

Die folgenden **offiziellen Quellen** wurden am 2026-09-18 fuer Begriffe
und Abgrenzungen geprueft, nicht fuer eine Formelimplementierung:

| Kennung | Quelle | Einordnung |
| --- | --- | --- |
| `directive_2025` | [Richtlinie 2009/138/EG, konsolidierter Stand 17.01.2025](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A02009L0138-20250117) | begrifflicher Bezug fuer den Stand vor der Revision |
| `valuation` | [Art. 75](https://www.eiopa.europa.eu/rulebook/solvency-ii-single-rulebook/article-2158_en) und [Art. 77](https://www.eiopa.europa.eu/rulebook/solvency-ii-single-rulebook/article-2160_en) | Bewertung, Best Estimate und Risikomarge |
| `own_funds` | [Art. 88](https://www.eiopa.europa.eu/rulebook/solvency-ii-single-rulebook/article-2176_en) | Basiseigenmittel, nicht Modell-Eigenkapital |
| `eligible_own_funds` | [Art. 98 der konsolidierten Richtlinie](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A02009L0138-20250117) | anrechenbare Eigenmittel und Grenzen, getrennt von Basiseigenmitteln |
| `scr` | [Art. 100](https://www.eiopa.europa.eu/rulebook/solvency-ii-single-rulebook/article-2187_en), [101](https://www.eiopa.europa.eu/rulebook/solvency-ii-single-rulebook/article-2188_en), [103](https://www.eiopa.europa.eu/rulebook/solvency-ii-single-rulebook/article-2190_en) | Kapitalanforderung und Standardformelstruktur |
| `mcr` | [Art. 129](https://www.eiopa.europa.eu/rulebook/solvency-ii-single-rulebook/article-2216_en) | eigene Mindestkapitalanforderung, nicht pauschaler SCR-Prozentsatz |
| `level2` | [Delegierte Verordnung (EU) 2015/35](https://www.eiopa.europa.eu/browse/regulation-and-policy/solvency-ii_en) | Detailregeln; fuer Rechnungen noch kein konsolidierter Versionsstand freigegeben |
| `review_2027` | [Richtlinie (EU) 2025/2](https://eur-lex.europa.eu/eli/dir/2025/2/oj/eng), [EIOPA-Ueberblick](https://www.eiopa.europa.eu/browse/regulation-and-policy/solvency-ii_en) | geaenderter Rahmen ab 30.01.2027; **nicht** automatisch auf IMS-Perioden anzuwenden |

Ein spaeterer Rechner muss Rechtsstand, Anwendungsdatum, Level-2-Details,
Parameter und Datenquellen gesondert fixieren und testen. Die heutigen
Quellenlinks sind keine Zusage, dass Formeln oder Zahlen der kuenftigen
Revision bereits implementiert sind.

## Gesperrte Bruecken und Folge-PRs

1. **PR172:** Bewertungsstichtag, Marktwert-/Verpflichtungsbruecke und
   vereinfachte *Modell*-Eigenmittel. Bilanzdifferenzen bleiben sichtbar;
   kein regulatorischer Eigenmittel-Nachweis.
2. **PR173-175:** explizite Risikotreiber, Exposures, Schocks, Module,
   Korrelationen und Verlustabsorption. Kein Rueckschluss aus
   `closing_equity` oder alten `Rs`-Werten allein.
3. **PR176:** erst nach Freigabe dieser Quellen eine beschriftete
   Modell-SCR-/MCR- und Quotenrechnung. Regulatorische Meldung und
   Einhaltungsaussage bleiben ohne separate Fachvalidierung ausgeschlossen.
4. **PR177-178:** feste Faelle, Sensitivitaeten, Export und UI muessen
   Modellgrad, Quellenstand und fehlende Komponenten mitfuehren.

## Umsetzung und Nachweis

`ims.model.solvency_scope_contract.solvency_scope_contract_payload` liefert
denselben JSON-faehigen Vertrag direkt und unter
`GET /api/model/solvency-scope-contract` (FastAPI und Starlette-Fallback).
POST/PUT/DELETE sind gesperrt. Tests pruefen Begriffsgrenzen, Quellenstand,
vier vorhandene Sparten, fehlende Rechengroessen und den read-only Pfad.

Offen bleiben alle Bewertungs- und Risikomethoden, die Rechtsregime-Wahl
fuer einen konkreten Stichtag, Datenqualitaet und externe fachliche
Validierung. Keine Simulation, keine Speicherung, keine historische
Vollgleichheitsaussage.
