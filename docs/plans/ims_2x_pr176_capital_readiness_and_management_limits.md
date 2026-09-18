# PR176: Kapitalfreigabe und Managementschwellen trennen

Stand: 2026-09-18
Status: umgesetzt; PR177 feste Faelle und Sensitivitaeten folgt

## Entscheidung

PR172 liefert einen Eigenmittel-**Modellproxy** in Modellwaehrung.
PR173-175 liefern nur szenariodeklarierte Teilpositionen und
Stressverluste. Ein Stichtag ist dort einer IMS-Periode durch
Szenarioannahme zugeordnet, nicht als Aufsichtsberichtsstichtag belegt.
Darum sind Solvency-II-SCR, MCR, anrechenbare Eigenmittel und
Bedeckungsquoten **nicht berechenbar**. Insbesondere wird der
PR175-Nettoverlust weder in SCR umbenannt noch mit einem pauschalen
Prozentsatz zu einem MCR gemacht.

Der versionierte PR176-Eingang enthaelt die vollstaendige PR175-Eingabe
und zwei getrennt deklarierte Managementgrenzen: einen maximal
akzeptierten Modell-Stressverlust und ein minimales verbleibendes
Modell-Eigenkapital. PR175 sowie PR172 werden serverseitig neu berechnet;
ihre Digests muessen uebereinstimmen. Fuer den Workshop gilt:

`remaining_model_equity_proxy = PR172.model_own_funds_proxy - PR175.net_model_stress_loss`

Die zwei Vergleiche sind inklusiv. Sie beschreiben nur die Konsequenz
der gewaehlen Modellannahmen; sie sind **keine aufsichtsrechtliche
Einhaltungsentscheidung**. Der PR175-Verlust ist ein aggregierter
Stressproxy und keine durchgebuchte Bilanzveraenderung. Ein negativer
Restproxy wird angezeigt, nicht auf Null gekappt. Alle Betraege bleiben
in `model_currency_unit_not_eur` und als Dezimaltext mit vier Stellen.

## Rechts- und Quellenfenster

Der PR172-Referenztag wird nur als Hinweis `before_2027_review` oder
`from_2027_review_unverified` klassifiziert. Diese Klassifikation ist
**keine Rechtsregime-Auswahl**. Fuer einen echten regulatorischen
Stichtag waeren anwendbarer Rechtsstand und Rechtsraum gesondert zu
belegen. Der Code implementiert weder die derzeitige noch die ab
30.01.2027 anzuwendende revidierte Standardformel.

| Offizielle Quelle, geprueft 18.09.2026 | Konsequenz fuer IMS |
| --- | --- |
| [EIOPA, Art. 101](https://www.eiopa.europa.eu/rulebook/solvency-ii-single-rulebook/article-2188_en) | SCR erfasst quantifizierbare Risiken mit 99,5-%-VaR ueber ein Jahr; PR175-Szenariosaetze sind dafuer nicht kalibriert |
| [EIOPA, Art. 103](https://www.eiopa.europa.eu/rulebook/solvency-ii-single-rulebook/article-2190_en) und [104](https://www.eiopa.europa.eu/rulebook/solvency-ii-single-rulebook/article-2191_en) | Standardformel trennt Basis-SCR, operationelles Risiko und Verlustabsorption; PR175-Ein-Faktor-Verlust ist keine solche Formel |
| [EIOPA, Art. 129](https://www.eiopa.europa.eu/rulebook/solvency-ii-single-rulebook/article-2216_en) | MCR benoetigt eigene netto-rueckversicherte Eingangsgroessen, Kalibrierung und absolute EUR-Untergrenze; 25/45 % allein ist keine MCR-Formel |
| [EUR-Lex, konsolidierte Richtlinie 17.01.2025](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A02009L0138-20250117) und [EIOPA zur Revision](https://www.eiopa.europa.eu/eiopa-completes-solvency-ii-review-mandate-final-guidelines-and-draft-technical-standards-revised-2026-07-15_en) | revidierter Rahmen ab 30.01.2027; nicht automatisch auf IMS-Perioden abbildbar |

Die EIOPA-Single-Rulebook-Seiten dienen der Orientierung; fuer eine
rechtsverbindliche Freigabe sind die amtlichen Fassungen im Amtsblatt,
die konkrete Anwendbarkeit und fachliche Pruefung erforderlich.

## Maschinenlesbare Sperren

`regulatory_metrics` enthaelt `eligible_own_funds`, `scr`, `mcr`,
`scr_coverage_ratio` und `mcr_coverage_ratio` ausschliesslich als `null`.
Der Status bleibt `blocked_missing_regulatory_basis`, auch wenn beide
Managementgrenzen eingehalten werden. Die versionierte Checkliste nennt
fehlende Marktwert-/Rueckstellungsbewertung, Eigenmittelanrechenbarkeit,
Kalibrierung und Standardformel, Verlustabsorption, MCR-Eingaben,
EUR-Bruecke sowie einen belegten Berichts- und Rechtsstichtag. Ab
30.01.2027 kommt die Revisionspruefung hinzu. Der Vertrag akzeptiert
keine vermeintlich regulatorischen Parameter oder Nutzer-Ueberschreibung
dieser Sperre.

## Herkunft und offene Arbeit

| Ursprung | Neue Entsprechung | Grenze |
| --- | --- | --- |
| `IMSDATA.C`, `LV`/`KV`, `Rs`, `Sh`, `Pr` | kein regulatorischer Port | historisches Zweispartenmodell kennt keine Solvency-II-Kapitalanforderung |
| `ims.accounting.solvency_model_balance` | neu berechneter Gesamt-Eigenmittel-Proxy | Modellwaehrung und Modellbewertung, keine anrechenbaren Eigenmittel |
| `ims.accounting.solvency_risk_aggregation` | neu berechneter Netto-Stressverlust | nicht 99,5-%-einjaehrig kalibriert, keine Standardformel |
| PR176-Managementgrenzen | zwei deterministische Workshop-Vergleiche | freie Szenarioannahmen, keine aufsichtsrechtlichen Schwellen |

PR177 kann feste Grenz- und Sensitivitaetsfaelle testen. PR178 soll
Workshop-Kennzahlen und gesperrte regulatorische Kennzahlen im Browser
**getrennt** anzeigen. Ein spaeterer echter SCR-/MCR-Rechner braucht
einen eigenen, quellengebundenen Fachauftrag samt Bewertungsdaten,
Rechtsstand, Parameterfreigabe und externer aktuarieller/rechtlicher
Abnahme; er ist mit PR176 nicht implizit zugesagt.
Keine historische Vollgleichheit, kein Runner und keine Speicherung.

## Abnahme

- Versionierter, zustandsloser Vertrag mit PR172-/PR175-Digest und
  atomaren Fehlerantworten.
- Tests fuer positive/negative/equal Managementgrenzen, negativen
  Restproxy, Quellenbindung, 2027-Fenster und dauerhaft gesperrte
  regulatorische Werte.
- FastAPI und Starlette-Fallback ohne Speicherung oder Simulation.

## Umsetzung und Validierung

`ims.accounting.solvency_capital_readiness` berechnet die
Managementgrenzen erst nach erneuter PR175-/PR172-Pruefung und
Digestabgleich. `GET /api/accounting/solvency-capital-readiness-contract`
und `POST /api/accounting/solvency-capital-readiness` sind fuer FastAPI
und Starlette verfuegbar. Die Tests in
`tests/test_solvency_capital_readiness.py` und
`tests/test_api_solvency_capital_readiness.py` decken Quellenbindung,
Grenzen, Datum, Sperren und atomare API-Fehler ab.
