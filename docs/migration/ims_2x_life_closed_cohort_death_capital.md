# PR161: Todesfaelle und Kapital im geschlossenen Lebensbestand

Stand: 2026-09-17
Eingang: `ims.life-closed-cohort-input.v1`
Ergebnis: `ims.life-closed-cohort-result.v1`
Python: `ims.accounting.life_closed_cohort_balance.build_life_closed_cohort_balance`

## Herkunft und fachliche Grenze

| Ursprung | Umsetzung | Abweichung/Grenze |
| --- | --- | --- |
| `IMSDATA.C`, `MAXSPARTEN 2`, `classVU.Sp[1/2]`, `classVN.Rk[1/2]`; `IMS.E` mit Schadenreserve, Praemie und Schaden | Keine historische Lebensregel portiert | Die C-Positionen tragen die neue Todesfall- und Garantieverpflichtungslogik nicht. |
| PR159: `ims.accounting.life_model_balance` | Getrennter PR161-Rechenkern und neue Eingabe-/Ergebnisversion | PR159/v2 bleibt unveraendert und ist bei null Tod/null Kapital ein exakter Spezialfall der gemeinsamen Zeilenfelder. |
| PR160: `ims.model.life_sector_v3_contract` | Geschlossene homogene **Teilmenge** der v3-Zielsemantik | Der read-only API-Vertrag bleibt unveraendert; eine vollstaendige v3-Eingabe, API und UI existieren noch nicht. |

Das ist eine IMS-2.x-Modellannahme, kein historischer Vollgleichheitsnachweis.
`life` ist ein separates Segment; die Zwei-Sparten-Bilanz und der
100-Perioden-Runner fuer Nichtleben werden nicht veraendert.

## Eingang und Berechnung

Der reine Python-Eingang hat `schema_version`,
`life_sector_contract_schema_version = "ims.life-sector-contract.v3"`,
`sector_taxonomy_schema_version`, `source_kind = "explicit_scenario"`,
`historical_mapping_status = "unresolved"`, eine VU-ID von 1 bis 25,
`sector_id = "life"`, einen `opening`-Bestand, einen festen
`guaranteed_rate_per_period` und 1 bis 100 lueckenlose `periods`.
Anfangsbestand: positive `opening_active_policies`, Restlaufzeit 1 bis
100, `opening_backing_assets`, `opening_guarantee_liability` und
`opening_equity`. Die Bilanzidentitaet gilt schon zu Beginn.

Jede Periode benoetigt ausdruecklich `renewal_premiums_collected`,
`renewal_liability_allocation`, `investment_result`, `deaths`,
`death_benefits_paid`, `operating_expense_paid`, `capital_contribution`
und `capital_distribution`. Betraege sind Dezimalstrings mit maximal
12 Vor- und vier Nachkommastellen; nur Anlageergebnis und Eigenkapital
duerfen negativ sein. Der Garantiesatz hat hoechstens sechs
Nachkommastellen. Es gibt keine Defaults und keine RNG-Ziehung.

Die Reihenfolge ist Anlagefluss, Garantie auf die Anfangsverpflichtung
(`ROUND_HALF_EVEN` auf `0.0001`), laufende Praemie/Zuweisung, Tod, Ablauf
der ueberlebenden Policen bei Restlaufzeit eins, Aufwand und Kapital,
dann Bilanzabstimmung. Ohne Policendetails wird die Verpflichtung nach
Gutschrift/Zuweisung proportional nach Toten des Anfangsbestands
freigesetzt und halbgerade auf `0.0001` gerundet; beim vollstaendigen
Abgang der ganze Rest. `death_benefits_paid` bleibt ein eigener
expliziter Betrag und kann vom freigesetzten Buchwert abweichen. Ohne
Todesfall muss er null sein; bei Tod darf er mangels festgelegter
Produktgarantie null sein. Faellige Ueberlebende erhalten in diesem
Schnitt den gesamten verbliebenen Buchwert als Ablaufleistung.

`closing_backing_assets` = Anfangsaktiva + Praemie + Anlageergebnis +
Kapitalzufuhr - Todesfallleistung - Ablaufleistung - Aufwand -
Kapitalausschuettung. `closing_guarantee_liability` =
Anfangsverpflichtung + Garantie + Praemienzuweisung - Todesfallfreisetzung
- Ablauffreisetzung. `period_profit` enthaelt Praemie, Anlageergebnis,
Leistungen, Aufwand und Verpflichtungsaenderung, **keine**
Kapitalbewegung. Schluss-Eigenkapital = Anfangs-Eigenkapital + Ergebnis
+ Kapitalzufuhr - Ausschuettung. Anfangs- und Schlussaktiva stimmen
jeweils mit Verpflichtung plus Eigenkapital ueberein. Nur nichtnegative
Schlussaktiva sind gefordert, keine intraperiodische Liquiditaetspruefung.

Die vollstaendige Eingabe wird geprueft; ungueltige Zahlen, zu viele
Todesfaelle, ein weiterer Zeitraum nach vollstaendiger Ausloeschung,
negative Schlussaktiva oder eine verletzte Bilanz fuehren zu **null**
Ergebniszeilen. Ergebniszeilen enthalten getrennte Todesfall- und
Ablauffreisetzung, Stueckzahlen, Bilanz und unveraenderten Carryover.

## Offen

PR162 hat neue Kohorten und Neugeschaeft ergaenzt; PR163 bringt begrenzte
Einzelpolicen und abweichende Ablaufleistungen; PR164 deterministische
Mortalitaets-/Anlageannahmen. PR165-167 bringen kontrollierten Runner,
Ablage/Export und eine gefuehrte Workbench. Keine gesetzliche Bilanz,
Solvency-II-Bewertung oder historische Vollgleichheit. Rueckkauf,
Bonus und automatische Stornostrategie bleiben ausgeschlossen.
