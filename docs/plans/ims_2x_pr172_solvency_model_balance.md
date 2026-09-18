# PR172: Modell-Solvenzbilanz und Eigenmittel-Proxy

Stand: 2026-09-18
Status: umgesetzt; PR173 Schock-Mapping, PR174 Modellmodule und PR175 Modellaggregation separat umgesetzt; PR176 folgt

## Ziel und konservative Grenze

PR172 bildet die Schlussbilanz **einer** ausgewaehlten IMS-Periode aus
PR170 auf eine explizit angepasste *Modell*-Bilanz ab. Genau vier
spartenspezifische Aenderungen der Modell-Aktiva und -Passiva werden als
Szenarioannahmen eingegeben. Daraus folgt ein rechnerischer
`model_own_funds_proxy = adjusted_model_assets - adjusted_model_liabilities`.
Das ist weder ein Basiseigenmittel- noch ein anrechenbarer Eigenmittelwert
nach Solvency II. Negative Proxy-Werte sind zulaessig und sichtbar.

Ein ISO-Datum bezeichnet nur den vom Szenario deklarierten Vergleichspunkt.
Eine IMS-Periode wird dadurch nicht zu einem Kalenderjahr. Weder
Rechtsregime, Marktdaten, Best Estimate, Risikomarge, Anrechenbarkeit noch
Waehrungsumrechnung werden aus dem Datum abgeleitet. Die vier Aenderungen
sind keine nach Art. 75/77 validierten Marktwertanpassungen; sie sind
bewusst frei definierte Modellannahmen.

## Herkunft und Abbildung

| Ursprung | PR172-Abbildung | Grenze |
| --- | --- | --- |
| `IMSDATA.C`/`IMS.E`: historische `Sp[1/2]`-Praemien, Schaeden und `Rs` | keine direkte Kapitalableitung | `Rs` ist nicht technische Rueckstellung oder Eigenmittel |
| `ims.accounting.four_sector_balance` (`ims.four-sector-balance-result.v1`) | vier neu berechnete Schluss-Aktiva, -Passiva und -Eigenkapitalwerte fuer denselben VU, dasselbe Szenario und dieselbe Periode | Nicht-Kranken-Szenariozusammenhang bleibt deklaratorisch |
| PR172-Szenarioeingang | je Sparte `asset_delta`, `liability_delta` und eindeutige Annahmenkennung | Modellwaehrung; keine gesetzliche Bewertung |

Je Sparte gilt exakt:

```text
adjusted_model_assets      = closing_assets + asset_delta
adjusted_model_liabilities = closing_liabilities + liability_delta
model_own_funds_proxy      = adjusted_model_assets - adjusted_model_liabilities
proxy_change_vs_equity     = asset_delta - liability_delta
```

Alle vier Zeilen und die Gesamtzeile werden exakt als Dezimaltexte mit vier
Nachkommastellen ausgegeben. Aktiva und Passiva duerfen nach Anpassung nicht
negativ sein. Eigenkapital, Anpassungseffekt und Proxy duerfen negativ sein.
Die Gesamtzeile ist die Summe der vier Sparten; zugleich muss
`Proxy = PR170-closing_equity + asset_delta - liability_delta` gelten.
Einzel- und Gesamtdifferenzen bleiben nebeneinander sichtbar.

## Vertrag und Fehlergrenze

Eingang `ims.solvency-model-balance-input.v1`:

- `scope_contract_schema_version = ims.solvency-scope-contract.v1`,
  `model_only_confirmed = true`;
- vollstaendiger PR170-Eingang, der serverseitig erneut berechnet wird;
- `checkpoint` mit `model_period`, `reference_date` im Format
  `YYYY-MM-DD` und `date_linkage = scenario_declared`;
- exakt eine Anpassung fuer `motor`, `property_liability`, `life`, `health`,
  jeweils mit `asset_delta`, `liability_delta` als begrenztem Dezimaltext,
  `assumption_id` und `assumption_note`.

Unbekannte oder fehlende Felder, doppelte/fehlende Sparten, ungueltige
Dezimalwerte oder Daten, ein fremder Scope-Vertrag, fehlende Bestaetigung,
ungueltige PR170-Quelle, unpassende Periode und negative angepasste Aktiva
oder Passiva liefern atomar **keine** Zeilen, Gesamtwerte oder Digests.
Die Quelle wird nicht anhand eines vom Aufrufer gelieferten Digests
geglaubt, sondern aus den vier Originaleingaben neu berechnet.

Ergebnis `ims.solvency-model-balance-result.v1` enthaelt den PR170-
Quelldigest, Eingangs- und Ergebnisdigest, VU/Szenario/Variante,
Checkpoint, Modellwaehrung, den deklarierten Quellenzusammenhang,
vier Brueckenzeilen und eine Gesamtzeile. Ein lesbarer Vertrag
und ein zustandsloser POST-Endpunkt stehen unter
`/api/accounting/solvency-model-balance-contract` und
`/api/accounting/solvency-model-balance`. Keine Speicherung, kein Runner,
keine UI-Aenderung und keine historische Vollgleichheitsaussage.

## Quellen, Validierung und naechster Schritt

Die regulatorische **Abgrenzung**, nicht die Rechenformel, folgt den
offiziellen EIOPA-Regelwerksseiten zu
[Art. 75 Bewertung](https://www.eiopa.europa.eu/rulebook/solvency-ii-single-rulebook/article-2158_en),
[Art. 77 versicherungstechnische Rueckstellungen](https://www.eiopa.europa.eu/rulebook/solvency-ii-single-rulebook/article-2160_en)
und [Art. 88 Basiseigenmittel](https://www.eiopa.europa.eu/rulebook/solvency-ii-single-rulebook/article-2176_en),
geprueft am 2026-09-18. Die [Revision (EU) 2025/2](https://www.eiopa.europa.eu/browse/regulation-and-policy/solvency-ii_en)
gilt ab 30.01.2027; sie wird nicht aus dem Szenariodatum aktiviert.

Tests pruefen identische Wiederholung, Quell- und Summenabgleich,
Negativ- und Fehlerpfade, 100er-Quellhorizont sowie FastAPI und
Starlette-Fallback. PR173 darf nur explizit zugeordnete Exposures und
Schocks anschliessen. PR174-176 bleiben fuer Risikomodule, Aggregation und
Kapitalquoten erforderlich; eine aufsichtsrechtliche Einhaltungsaussage
bleibt auch danach gesondert zu validieren.
