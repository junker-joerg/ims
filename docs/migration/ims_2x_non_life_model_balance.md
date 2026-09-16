# PR156: Deterministische Modellbilanz fuer Kfz und Sach-Haftpflicht

Der reine Python-Rechenkern
`ims.accounting.non_life_model_balance.build_non_life_model_balance`
berechnet fuer **einen** Versicherer und **eine** benannte Nichtleben-Sparte
1 bis 100 aufeinanderfolgende Perioden. Er veraendert keinen Altzustand,
speichert nichts und startet keinen Runner. PR157 hat die getrennte
Einzelspartenrechnung in eine zustandslose Versichereransicht mit XLSX
angebunden; Details stehen in `ims_2x_insurer_balance_workbench.md`.

## Historische Einordnung

| Altcode / Zustand | PR156-Entscheidung |
| --- | --- |
| `IMSDATA.C`, `classVU.Sp[1/2].Rs` und `IMS.E`, Reservefortschreibung | `Rs` bleibt ein Legacy-Diagnosewert, kein Bilanzposten und kein Anfangs-Cash. |
| `IMSDATA.C`, `Pr` und `Wa` | Preis- und Werbegroessen werden nicht automatisch als Zahlung bzw. Aufwand gebucht. |
| `IMS.E`, VN-Zahlung und Schaden; `python_port/ims/model/vn_rules.py` | Kein direkter Datenadapter: erst eine spaetere, belegte Zuordnung koennte Praemien-/Schadensummen als Quelle freigeben. |
| Zwei historische Spartenpositionen | Weiterhin keine Kfz-/Sach-Haftpflicht-Zuordnung. `sector_id` benennt nur die neue Modellrechnung. |

**Alle** Eingaben sind explizite Szenariowerte. Es wird nicht behauptet,
dass diese Bilanz historisch errechnet wurde oder den damaligen Modelllauf
abbildet. Je Sparte zugeteiltes Kapital ist ein eigener Eingabewert.

## Eingang und Ausgabe

Das versionierte JSON-Objekt ist in
`tests/fixtures/non_life_model_balance_v1.json` beispielhaft ausgefuellt.
Es enthaelt `schema_version = ims.insurer-model-balance-input.v1`,
`model_balance_contract_schema_version = ims.insurer-model-balance-contract.v2`,
`sector_taxonomy_schema_version`, `source_kind = explicit_scenario`,
`historical_mapping_status = unresolved`, `insurer_id` (Vdefmd6: 1-25),
`sector_id` (`motor` oder `property_liability`), `opening` und `periods`.
`opening` enthaelt Cash, Schadenverbindlichkeit und Eigenkapital. Jede
Periode enthaelt ihre Nummer sowie die sieben im PR155-Vertrag benannten
Fluesse. Die Folge beginnt bei 1, ist lueckenlos und auf 100 begrenzt.

Betragsfelder sind **Strings**, keine JSON-Zahlen: bis zu 12
Vorkommastellen, optional bis zu vier Nachkommastellen, ohne Exponent oder
Tausendertrennzeichen. `Decimal` rechnet in einem festen lokalen
Praezisionskontext exakt, unabhaengig vom Aufrufer; die Ausgabe ist auf vier
Nachkommastellen aufgefuellt, nicht gerundet. Negatives Zinsergebnis und
negatives Eigenkapital sind moeglich; die uebrigen im Vertrag bezeichneten
Eingaenge und Cash-/Schadenbestaende muessen nichtnegativ sein.

Der Ergebnisbericht `ims.insurer-model-balance-result.v1` enthaelt je
Periode Anfangsbestaende, sieben Fluesse, Periodenergebnis und drei
Schlussbestaende als kanonische Dezimalstrings. Er prueft die Identitaeten
`Cash = Schadenverbindlichkeit + Eigenkapital` am Anfang und Schluss und
uebernimmt nur die drei Schlussbestaende in die Folgeperiode. Bei einem
beliebigen Fehler ist `valid = false`, `rows = []` und
`calculated_period_count = 0`; es gibt keine Teilergebnisse. Die
zweiperiodige Referenz ergibt Schlussbestaende `117 / 33 / 84` und danach
`116 / 29 / 87` fuer Cash / Schadenverbindlichkeit / Eigenkapital.

## Grenzen

Die Modellbilanz haelt die Vereinfachungen von PR155 ein: Praemien,
Zinsertrag und Aufwand sind jeweils gleichzeitig verdient/angefallen und
geflossen. Es gibt keine Forderungen, Beitragsabgrenzung, Kapitalanlagen,
Rueckversicherung, Steuern oder weiteren Verbindlichkeiten. Damit ist sie
**keine gesetzliche Bilanz und kein Solvency-II-Nachweis**. Die PR155-v1-
Vertragsfassung bleibt unter `GET /api/accounting/model-balance-contract/v1`
erhalten; der aktuelle read-only Vertrag v2 beschreibt den Python-Kern.
