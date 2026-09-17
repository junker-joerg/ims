# PR163: Einzelpolicen und abweichende Ablaufleistungen

Stand: 2026-09-17
Eingang: `ims.life-policy-balance-input.v1`
Ergebnis: `ims.life-policy-balance-result.v1`
Python: `ims.accounting.life_policy_balance.build_life_policy_balance`

## Herkunft und fachliche Grenze

| Ursprung | Python-Ziel | Einordnung |
| --- | --- | --- |
| `IMSDATA.C`: `MAXSPARTEN 2`, `classVU.Sp`, `classVN.Rk`; `IMS.E`: Praemien-, Schaden- und Reserveoperationen | Keine historische Lebenspolice portiert | Die zwei C-Schadenpositionen belegen keine individuelle Lebenspolice. |
| PR160: `ims.model.life_sector_v3_contract` | Vollstaendig enumerierter, auf 100 aktive Policen begrenzter Modus | Separate IMS-2.x-Annahme; v1/v2 und read-only v3-API bleiben unveraendert. |
| PR162: `ims.accounting.life_cohort_balance` | Eine Police wird intern als Ein-Stueck-Kohorte gerechnet und anschliessend ihrer fachlichen Kohorte zugeordnet | PR162-Eingabe und Standardrechnung bleiben unveraendert; Rundung je Police kann fachlich von der Kohortenrundung abweichen. |

Keine historische Vollgleichheit, gesetzliche Bilanz oder Solvency-II-
Aussage. Der Rechenschnitt ist eine reine Python-Funktion, kein Runner,
API-Endpunkt, Workbench-Eingang, Speicher- oder Excelpfad.

## Eingang und Modus

Der vollstaendige Fall `tests/fixtures/life_policy_balance_v1.json`
zeigt das JSON-Format. Oben sind `schema_version`,
`life_sector_contract_schema_version = "ims.life-sector-contract.v3"`,
`sector_taxonomy_schema_version`, `source_kind = "explicit_scenario"`,
`historical_mapping_status = "unresolved"`, `insurer_id` (1 bis 25),
`sector_id = "life"`, `mode = "fully_enumerated_policies"`, `opening`
und 1 bis 100 lueckenlose `periods` verpflichtend. Der PR162-Modus
hat eine eigene Version und keinen impliziten Wechsel in den
Policenmodus. Betraege sind Dezimalstrings mit hoechstens vier
Nachkommastellen, Garantiesaetze mit hoechstens sechs.

`opening` nennt Aktiva, Garantieverpflichtung, Eigenkapital und
Stueckzahl wie in PR162, ausserdem `cohorts` **und alle** `policies`.
Jede Anfangspolice hat eine stabile `policy_id`, `cohort_id`,
`issue_term_periods`, `remaining_periods`,
`guaranteed_rate_per_period` und `guarantee_liability`. Laufzeit,
Restlaufzeit und Satz stimmen zu ihrer Kohorte; Buchwerte duerfen
abweichen. Policenzahl und Buchwertsumme stimmen je Kohorte und im
Segment exakt. `issue_period` der Anfangspolice wird aus der Kohorte
uebernommen. IDs sind ASCII-Bezeichner mit Buchstabenbeginn und
hoechstens 32 Zeichen; sie bleiben nach Abgang vergeben.

Jede Periode nennt fuer **jede aktive Anfangspolice** genau einen
`policy_flows`-Eintrag: `policy_id`, `renewal_premiums_collected`,
`renewal_liability_allocation`, boolesches `death`,
`death_benefits_paid` und `maturity_benefits_paid`. Die letzten
beiden Felder sind auch bei null explizit. `new_business` nennt je
neuer Kohorte die PR162-Ausgabeparameter sowie eine vollstaendige
`policies`-Liste aus `policy_id`, individueller Einmalpraemie und
Verpflichtungszuweisung. Policensummen und -zahl stimmen exakt zur
Ausgabekohorte. Anlageergebnis, Aufwand, Kapitalzufuhr und
-ausschuettung bleiben separate Periodenfelder.

## Bewertung und Abstimmung

Die Garantie wird auf den **Anfangsbuchwert jeder Police** mit
`ROUND_HALF_EVEN` auf `0.0001` berechnet. Danach folgt die laufende
Praemienzuweisung. Tod geht vor Ablauf: Bei Tod wird der gesamte
Policenbuchwert freigesetzt und die explizite Todesfallleistung
ausgezahlt. Eine ueberlebende Police mit Restlaufzeit 1 laeuft ab;
ihre explizite Ablaufzahlung muss mindestens dem freigesetzten
Garantiebuchwert entsprechen. Nicht faellige oder verstorbene Policen
haben `maturity_benefits_paid = 0`. Eine positive Zahlung bei Tod ist
auch bei faelliger Laufzeit unzulaessig. Die separate, bei Ausgabe
unveraenderlich vereinbarte Ablaufleistungsquelle aus dem v3-Zielbild
ist **noch nicht implementiert**. Sie darf hier nicht stillschweigend
aus Garantie oder Praemie abgeleitet werden.

Neupolicen zaehlen nach den Abgaengen in der Ausgabeperiode zu Praemie,
Aktiva, Garantieverpflichtung und Stueckzahl. Ihre erste Gutschrift
erfolgt erst in der Folgeperiode. Zahlungen und Buchwertfreisetzungen
werden getrennt gezeigt; die Mehrleistung mindert Periodenergebnis,
Aktiva und Eigenkapital. Der feste Referenzfall zeigt in Periode 1
25.0000 Ablaufzahlung gegen 22.0000 Freisetzung und in Periode 2
72.0000 gegen 61.9000. Schlussaktiva = Garantieverpflichtung +
Eigenkapital. Schlussbestand und -verpflichtung stimmen zugleich auf
Policen-, Kohorten- und Segmentebene. Reihenfolge der Eingabelisten
aendert das Ergebnis nicht; Ausgaben sind nach IDs sortiert.

Beginn und Ende jeder Periode haben hoechstens 100 aktive Policen.
Es gibt keine Stichprobe. Spaete Validierungs- oder Bilanzfehler
liefern atomar **null Ergebniszeilen**. Nur Schlussaktiva muessen
nichtnegativ sein; intraperiodische Liquiditaet wird nicht geprueft.

## Offen

PR164 hat deterministische Anlage- und Mortalitaetsannahmen samt
eindeutiger Perioden- und Auswahlregel separat ergaenzt. PR165 hat
sie in einer fluechtigen Lebens-Periodenkette angeschlossen.
PR166-167 behandeln Ergebnisablage/Export und eine nichttechnische
Workbench. Rueckkauf, Bonus, automatische Storno- und Anlageentscheide,
individuelle Ausgabevertragsleistungen sowie die Vier-Sparten-
Gesamtbilanz bleiben ausserhalb dieses PRs.
