# PR173: Explizite Risikotreiber und Szenarioschocks

Stand: 2026-09-18
Status: umgesetzt; PR174 Risikomodule bleibt ein eigener Schritt

## Ziel und fachliche Grenze

Eine fluechtige Wirkungsprobe bindet benannte, nicht ueberlappende
Teilbestaende der PR172-Modellbilanz an explizite Schocks. Der Eingang
enthaelt die vollstaendige PR172-Eingabe; sie wird serverseitig neu
berechnet. Eine IMS-Periode und ein vom Szenario erklaerter Stichtag
werden uebernommen. Es gibt weder einen stillen Anteil der Bilanz als
Exposure noch eine implizite Kalibrierung aus Zinssaetzen, Schadenquoten
oder Mortalitaet.

Ein Exposure hat Kennung, Sparte, Bilanzseite und Modellbetrag. Seine
`source_kind` ist `scenario_declared_non_overlapping_subposition`.
Die Summe der Teilbestaende je Sparte und Seite darf den angepassten
PR172-Modellbestand nicht uebersteigen; fachliche Disjunktheit der
deklarierten Teilbestaende bleibt eine Szenarioannahme. Nicht erklaerte
Restbestaende werden nicht geschockt.

Ein Schock hat Kennung, Treiber, Ziel-Exposure, ausdrueckliche
`amount_delta` und Annahmentext. Ein Exposure darf in diesem Vertrag
hoechstens einen Schock erhalten; Stapelung und Korrelation bleiben
PR175 vorbehalten. `base_amount + amount_delta` darf nicht negativ sein.
Die vier engen, **modellinternen** Treiber sind:

| Treiber | Zulaessige Zuordnung |
| --- | --- |
| `asset_market_value` | Aktiva aller vier Sparten |
| `non_life_claim_obligation` | Passiva von Kfz oder Sach-Haftpflicht |
| `life_obligation` | Passiva von Leben |
| `health_benefit_obligation` | Passiva von Kranken |

Diese Namen bilden weder Risikomodule der Standardformel noch deren
Schockparameter ab. Die Aenderung wird ausschliesslich als
`amount_delta` in Modellwaehrung eingegeben. Das Ergebnis zeigt jeden
deklarierten Teilbestand, den Schock und die Veraenderung des
Modell-Eigenmittel-Proxys (`Aktivaaenderung - Passivaaenderung`). Es
ersetzt nicht die PR172-Ausgangsbilanz und schreibt keinen Zustand.

## Herkunft, Annahmen und Risiken

| Ursprung | Umsetzung | Grenze |
| --- | --- | --- |
| `IMSDATA.C`, `Sp[1/2]`, `Rs`, `Pr`, `Sh` | kein direkter Port | historische Zwei-Sparten-Vektoren enthalten keine vier modernen Risikopositionen oder Solvency-II-Schocks |
| `ims.accounting.four_sector_balance` und `ims.accounting.solvency_model_balance` | `ims.accounting.solvency_scenario_shocks` | PR170/172 neu berechnen, Periode und Digest uebernehmen; keine Veraenderung der Quelle |
| Szenariodeklaration | benannte Teilbestaende, Treiber und Deltas | Zuordnung und Delta werden fachlich vom Anwender gesetzt, nicht aus C- oder Solvency-II-Daten hergeleitet |

Der historische Bestand liefert keine marktwertigen Aktiva, Best
Estimate, Risikomarge, Duration, Stresskalibrierung oder
Korrelationsmatrix. Deshalb sind Betrag und Richtung eines Schocks
keine automatische Markt- oder Verpflichtungsbewertung. Insbesondere
werden kein SCR, MCR, Bedeckungsgrad und keine regulatorischen
Eigenmittel berechnet. Das Datum waehlt kein Rechtsregime. Eine
historische Vollgleichheit wird nicht behauptet.

Die begriffliche Abgrenzung folgt dem [EIOPA-Regelwerk, Art. 101](https://www.eiopa.europa.eu/rulebook/solvency-ii-single-rulebook/article-2188_en):
Ein SCR umfasst quantifizierbare Risiken und eine spezifische
Einjahreskalibrierung. [Art. 103](https://www.eiopa.europa.eu/rulebook/solvency-ii-single-rulebook/article-2190_en)
benennt weitere Bestandteile der Standardformel. Beides wird hier
ausdruecklich **nicht** umgesetzt.

## Abnahme

- Versionierter Vertrag und fluechtiger API-Pfad fuer FastAPI und
  Starlette-Fallback; keine Speicherung, kein Runner, keine UI.
- Exaktes Dezimalformat, vier Sparten, benannte Teilbestaende und
  vollstaendiger PR172-Digest; kanonische, reproduzierbare Ausgabe.
- Unzugeordnetes Exposure bleibt unveraendert; nur das zugeordnete
  Exposure traegt das Delta. Fehler liefern atomar keine Wirkungszeilen.
- Negativer Endbestand, Ueberallokation, doppelte/fehlende Kennung,
  falscher Treiber und ungueltige PR172-Quelle werden abgewiesen.

Offen fuer PR174-176: Datenquellen fuer Risikoexponierung und
Stressfaktoren, konkrete Module, Gegenpartei- und operationelles Risiko,
Korrelationen/Verlustabsorption sowie Kapitalanforderungen. Die
Planung darf aus diesem Wirkungsprototypen keine Rechtskonformitaet
ableiten.

## Umsetzung und Validierung

`ims.accounting.solvency_scenario_shocks` liefert den versionierten
Vertrag `ims.solvency-scenario-shocks-input.v1`, den neu berechneten
PR172-Quelldigest und einen kanonischen Wirkungsbericht. Die Endpunkte
`GET /api/accounting/solvency-scenario-shocks-contract` und
`POST /api/accounting/solvency-scenario-shocks` sind fuer FastAPI und
Starlette-Fallback angebunden; der POST ist zustandslos.

`tests/test_solvency_scenario_shocks.py` prueft Quellreproduktion,
betroffene und unbetroffene Teilbestaende, Dezimalgenauigkeit,
Invarianz sowie atomare Fehlergrenzen. `tests/test_api_solvency_scenario_shocks.py`
prueft beide API-Pfade, Methodengrenzen, Fehlerantworten und dass
weder Lauf noch Speicherung gestartet werden.
