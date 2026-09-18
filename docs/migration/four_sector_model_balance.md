# PR170: einfache Vier-Sparten-Modellbilanz

## Zweck

`POST /api/accounting/four-sector-balance` nimmt ein versioniertes Objekt
`ims.four-sector-balance-input.v1` an. Es enthaelt `insurer_id`,
`scenario_id`, `variant_id` und `sectors` mit genau den Schluesseln
`motor`, `property_liability`, `life`, `health`. Unter jedem Schluessel
steht die **urspruengliche Eingabe** des jeweiligen Rechners, kein
behauptetes oder editierbares Ergebnis:

| Sparte | Eingabeversion | Neuberechnung |
| --- | --- | --- |
| Kfz, Sach-Haftpflicht | `ims.insurer-model-balance-input.v1` | `build_non_life_model_balance` |
| Leben | `ims.life-period-chain-input.v1` | `run_life_policy_period_chain` |
| Kranken | `ims.health-period-chain-input.v1` | `run_health_period_chain` |

Der Vertrag ist mit `GET /api/accounting/four-sector-balance-contract`
lesbar. Gemeinsame Horizonte sind 1, 2, 5, 10, 25, 50 und 100
Perioden; die Kranken-Periodenkette begrenzt die Auswahl. Eingaben und
Ergebnisse werden weder gespeichert noch an den
allgemeinen VU-/VN-Runner angeschlossen. Das alte
`/api/accounting/insurer-balance` bleibt der getrennte Zwei-Schaden-Sparten-
Vertrag.

PR170a verbindet die geprueften Eingaben der drei vorhandenen Workbench-
Bereiche fluechtig mit diesem Endpunkt. Die gefuehrte Lebensansicht
liefert derzeit zwei Perioden; mehrperiodige API-Unterstuetzung ist
daher noch kein bedienbarer 100-Perioden-Vier-Sparten-Lauf.

## Bilanzabbildung

Pro Sparte und Periode werden nur gemeinsame Modellgroessen normalisiert:

- Kfz/Sach-Haftpflicht: Cash zu `assets`, Schadenverbindlichkeit zu
  `liabilities`.
- Leben: deckende Vermoegenswerte zu `assets`, Garantieverpflichtung zu
  `liabilities`.
- Kranken: Cash zu `assets`, offene Leistung zu `liabilities`.
- Eigenkapital, Periodenergebnis und explizite Kapitalzufuehrung/
  -ausschuettung behalten ihre Bedeutung und werden pro Position addiert.

Je Sparte und fuer den VU insgesamt gelten `assets = liabilities + equity`
am Anfang und Schluss jeder Periode,
`closing_equity = opening_equity + period_profit + capital_contribution
- capital_distribution` sowie der exakte Uebergang der drei Bestandswerte
zur naechsten Periode. Der Antwort-Digest schliesst den Digest aller
Eingaben, die vier Allokationen und die Gesamtzeilen ein. Fehler liefern
keine Teilzeilen. Alle Geldbetraege sind exakte Dezimaltexte mit vier
Nachkommastellen.

Die Krankenquelle muss die aeusseren `scenario_id` und `variant_id`
explizit bestaetigen. Kfz, Sach-Haftpflicht und Leben besitzen noch keine
gleichartigen Szenariokennungen; ihre Zusammengehoerigkeit wird daher
vom Aufrufer deklariert. Das ist eine offene Herkunftsgrenze, kein Beleg
fuer identische historische Laeufe oder wirtschaftlich abgestimmte
Annahmen. Schaden- und Lebensleistungen oder Policenzahlen werden nicht
zu einer irrefuehrenden gemeinsamen Flussgroesse addiert. Konzerninterne
Transfers, gesetzliche Bilanz, Solvency II und historische Vollgleichheit
sind nicht Teil dieses Vertrags.

Der Altcode `IMSDATA.C` definiert mit `LV`/`KV` nur zwei historische
Schadenpositionen. Leben und Kranken sind explizite IMS-2.x-Erweiterungen,
keine Ableitung oder Umdeutung jener C-Strukturen.
