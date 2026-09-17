# PR162: Lebens-Neugeschaeft in getrennten Kohorten

Stand: 2026-09-17
Eingang: `ims.life-cohort-balance-input.v1`
Ergebnis: `ims.life-cohort-balance-result.v1`
Python: `ims.accounting.life_cohort_balance.build_life_cohort_balance`

## Herkunft und Grenze

| Ursprung | Python-Ziel | Fachliche Grenze |
| --- | --- | --- |
| `IMSDATA.C` (`MAXSPARTEN 2`, `classVU.Sp[1/2]`, `classVN.Rk[1/2]`) und `IMS.E` (Praemien, Schadenreserven, Schadenanzahl) | Keine historische Lebensregel portiert | Die historischen Vektoren belegen weder Lebens-Kohorten noch Garantien oder Ausgabezeitpunkte. |
| PR160: `ims.model.life_sector_v3_contract` | Separater, versionierter Kohorten-Rechenschnitt | Nur explizite Szenariowerte; der read-only v3-API-Vertrag und v1/v2 bleiben unveraendert. |
| PR161: `ims.accounting.life_closed_cohort_balance` | Gleiche Dezimal-/Feldgrenzen und Tod/Kapital-Semantik, jetzt pro Kohorte | PR161-Eingabe und -Rechnung bleiben unveraendert. Eine Kohorte ohne Neugeschaeft liefert dieselben gemeinsamen Zeilenwerte. |

Dies ist eine IMS-2.x-Modellannahme. Es gibt keine historische
Vollgleichheits-, gesetzliche Bilanz- oder Solvency-II-Behauptung.

## Eingang

Der reine Python-Eingang verlangt `schema_version`,
`life_sector_contract_schema_version = "ims.life-sector-contract.v3"`,
`sector_taxonomy_schema_version`, `source_kind = "explicit_scenario"`,
`historical_mapping_status = "unresolved"`, `insurer_id` (1 bis 25),
`sector_id = "life"`, `opening` und 1 bis 100 lueckenlose `periods`.
Betraege sind Dezimalstrings mit maximal 12 Vor- und vier Nachkommastellen,
Garantiesaetze liegen zwischen 0 und 1 mit maximal sechs Dezimalstellen.
Nur Anlageergebnis und Eigenkapital duerfen negativ sein.

`opening` enthaelt die Segment-Summen fuer aktive Policen, Aktiva,
Garantieverpflichtung und Eigenkapital sowie `cohorts`. Eine
Anfangskohorte enthaelt `cohort_id`, `issue_period` (von -99 bis 0),
`issue_term_periods`, `remaining_periods`, `active_policies`,
`guaranteed_rate_per_period` und `guarantee_liability`.
Am **Anfang der Modellperiode 1** gilt fuer den bereits vorhandenen
Bestand `issue_period = remaining_periods - issue_term_periods`.
Diese negative/Null-Modellperiode ist eine explizite Datierung des
Vorbestands, kein historisches Kalenderdatum. Ein leerer Anfangsbestand
mit null Verpflichtung ist zulaessig. Anfangs-Stueckzahl und
-Verpflichtung muessen exakt den Kohortensummen entsprechen; Aktiva
muessen Verpflichtung plus Eigenkapital sein.

Jede Periode enthaelt genau einen `cohort_flows`-Eintrag je **aktiver
Anfangskohorte** mit `cohort_id`, `renewal_premiums_collected`,
`renewal_liability_allocation`, `deaths` und `death_benefits_paid`.
Unbekannte, doppelte oder fehlende Kohorten sind unzulaessig. Die
`new_business`-Liste enthaelt je neuer Kohorte `cohort_id`,
`issue_term_periods`, `guaranteed_rate_per_period`,
`new_business_policies`, `new_business_premiums_collected` und
`new_business_liability_allocation`. Ausgabeperiode und anfaengliche
Restlaufzeit werden daraus und aus der aktuellen Periode abgeleitet.
`investment_result`, `operating_expense_paid`, `capital_contribution`
und `capital_distribution` sind separate Segmentfluesse. Praemien-
Zuweisung darf die jeweilige Praemie nicht uebersteigen. Positive
Todesfallleistung ohne Todesfall ist unzulaessig; eine Null-Leistung
bei Tod bleibt ohne Produktausgabeterm moeglich.

IDs sind ASCII-Bezeichner mit Buchstabenbeginn und hoechstens 32
Zeichen. Sie werden innerhalb eines Falls auch nach Abgang nicht
wiederverwendet. Dieser erste Rechenschnitt begrenzt den Fall auf 100
ausgegebene/eingebrachte Kohorten und eine Milliarde gleichzeitig
aktive Policen. Diese Grenzen sind technische Eingabegrenzen des
Teilrechners, keine allgemeine Grenze des v3-Zielvertrags.

## Periodenfolge und Abgleich

Fuer jede Anfangskohorte wird erst die Garantie auf ihrer
Anfangsverpflichtung mit `ROUND_HALF_EVEN` auf `0.0001` gerundet, dann die
laufende Praemienzuweisung addiert. Danach werden Todesfaelle
proportional zum Anfangsbestand mit derselben Rundung freigesetzt; bei vollstaendigem Abgang
der ganze Rest. Erst anschliessend laufen alle ueberlebenden Policen
mit Restlaufzeit 1 zum verbliebenen Buchwert ab. Gutschrift- und
Freisetzungsrundung erfolgen **je Kohorte**, nicht auf der
Versicherer-Summe.

Neue Kohorten werden danach ausgegeben. Ihre Praemie erhoeht bereits
die Aktiva, ihre Zuweisung bereits die Garantieverpflichtung. In der
Ausgabeperiode erhalten sie weder Garantie noch Tod/Ablauf. Die erste
Garantie ist in der Folgeperiode auf die dann bestehende
Anfangsverpflichtung faellig. Auch eine Laufzeit von einer Periode
endet damit fruehestens in der Folgeperiode. Ausgabeparameter bleiben
bis zum Abgang unveraendert. Leere Zwischenperioden sind zulaessig;
spaeteres Neugeschaeft kann den Bestand erneut aufbauen.

Die Zeilen enthalten Anfangs-/Schlusskohorten, Bewegungen je alter
Kohorte, neue Ausgaben, Summen fuer Praemien, Garantie, Tod, Ablauf,
Kapital, Gewinn und Bilanz. Es gilt:

- `premiums_collected = renewal_premiums_collected + new_business_premiums_collected`.
- `premium_liability_allocation = renewal_liability_allocation + new_business_liability_allocation`.
- `liability_release = death_liability_release + maturity_liability_release`.
- Schlussbestand = Anfangsbestand - Todesfaelle - Ablaeufe + Neugeschaeft.
- Schlussverpflichtung = Anfangsverpflichtung + Garantie + beide
  Praemienzuweisungen - beide Freisetzungen = Summe der Schlusskohorten.
- Schlussaktiva = Anfangsaktiva + beide Praemien + Anlageergebnis +
  Kapitalzufuhr - Todesfall-/Ablaufleistung - Aufwand - Ausschuettung.
- Schluss-Eigenkapital = Anfangs-Eigenkapital + Periodenergebnis +
  Kapitalzufuhr - Ausschuettung; Kapital ist kein Periodenertrag.

Nur die Schlussaktiva muessen nichtnegativ sein. Eine intraperiodische
Liquiditaetspruefung erfolgt nicht. Eingabe und Rechnung sind atomar:
Fehler in einer beliebigen Periode liefern null Ergebniszeilen.
Reihenfolge von Kohorten und Fluesseingaben aendert das Ergebnis nicht;
die Ausgabe ist nach Kohorten-ID sortiert.

## Offen

PR163 ergaenzt begrenzte Einzelpolicen und von der Freisetzung
abweichende Ablaufleistungen. PR164 fuehrt deterministische Anlage-
und Mortalitaetsannahmen ein. Erst PR165-167 bringen kontrollierten
Runner, Ergebnisablage/Export und gefuehrte Workbench. Kein
Rueckkauf, Bonus, automatisches Storno oder historische RNG-Nachbildung.
