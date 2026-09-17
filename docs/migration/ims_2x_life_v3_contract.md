# PR160: Lebensfluss- und Bewertungsvertrag v3

Stand: 2026-09-17
Vertrag: `ims.life-sector-contract.v3`
Abruf: `GET /api/model/life-sector-contract/v3`

## Herkunft und Trennung

| Ursprung | Python-Ziel | Grenze |
| --- | --- | --- |
| `IMSDATA.C`, `MAXSPARTEN 2`, `classVU.Sp[1/2]`, `classVN.Rk[1/2]`; `IMS.E` mit Schaden-/Praemien-/Reservevektoren | `ims.model.life_sector_v3_contract` | Die zwei historischen Schadenspositionen und das C-Kuerzel `LV` belegen keine Lebensversicherungslogik. |
| PR158/v1 und PR159/v2 | Neuer read-only Vertrag v3 fuer den spaeteren Ausbau | V1/v2-Payloads, PR159-Eingabe `ims.life-model-balance-input.v1` und dessen Rechnung bleiben unveraendert. |

Der bisherige Endpunkt `/api/model/life-sector-contract` liefert weiter
v2, `/v1` weiter v1. V3 wird nur ueber `/v3` gezeigt. Dieser API-Vertrag
ist weiterhin read-only und nicht als vollstaendige v3-Eingabe oder
Ausfuehrung freigegeben. PR161 liefert separat eine reine Python-Rechnung
fuer die geschlossene Ein-Kohorten-Teilmenge.

## Zustands- und Flussgrenze

Ein Versicherer fuehrt ein `life`-Segment mit hoechstens 100
IMS-Modellperioden. Mehrere Kohorten koennen unterschiedliche Ausgabe-
zeitpunkte, Laufzeiten und feste Garantiesaetze haben. Jede Kohorte hat
eine stabile ID und ist innerhalb ihrer Ausgabeparameter homogen.
Eine feste Ablaufleistung kann optional schon bei Ausgabe als
unveraenderlicher Vertragsterm festgelegt werden.
Anfangs- und Schluss-Stueckzahl sowie Garantieverpflichtung stimmen
zur Summe der Kohorten. Ein optionaler vollstaendiger Policenmodus ist
auf 100 aktive Policen zu Beginn und Ende begrenzt; jede Police hat eine
stabile ID und verweist auf eine Kohorte. Es gibt keine verdeckte
Stichprobe und keinen stillen Wechsel zwischen Kohorten- und
Policenmodus. Bei Policendetails stimmen Policen- und Kohortensummen.

Laufende und neue Praemien, ihre Zuweisung zur Garantieverpflichtung,
Todes- und Ablaufleistungen, die jeweils freigesetzte Verpflichtung,
Anlageergebnis, Aufwand sowie Kapitalzufuhr/-ausschuettung sind
getrennte Fluesse. `premiums_collected` und `liability_release` sind
jeweils nur die explizit benannten Summen ihrer Teilfluesse. Die
Bilanzgleichung bleibt `Aktiva = Garantieverpflichtung + Eigenkapital`.
Kapitalbewegungen veraendern Aktiva und Eigenkapital, nicht das
Periodenergebnis oder die Garantieverpflichtung. Die Spartenzuordnung
der Kapitalbewegung muss explizit sein; spaeteres Addieren darf sie
nicht doppelt zaehlen.

## Periodenfolge und Bewertung

1. Anfangszustand und Kohorten werden aus einem expliziten Szenario oder
   aus dem geprueften Schluss der Vorperiode uebernommen.
2. Ein explizites Anlageergebnis oder eine spaetere VU-Anlageregel wird
   auf Anfangsaktiva bezogen. Beides gleichzeitig ist unzulaessig;
   Praemien und Kapital der laufenden Periode erhalten in diesem Schritt
   keinen rueckwirkenden Anlageertrag.
3. Garantie wird auf die Garantieverpflichtung zu Periodenbeginn
   gutgeschrieben. Im aggregierten Modus wird je Kohorte, im voll
   enumerierten Policenmodus je Police mit `ROUND_HALF_EVEN` auf
   `0.0001` quantisiert. Diese beiden Granularitaeten werden nicht
   als vollgleich behauptet; die v2-Rechnung bleibt unveraendert.
4. Laufende Praemien bestehender Policen und ihre Verpflichtungszuweisung
   fallen nach der Gutschrift und vor Abgaengen an. Die Zuweisung je
   Kohorte darf die zugehoerige eingezogene Praemie nicht uebersteigen.
5. Todesfallzahlen werden je Kohorte ausgewiesen und betreffen nur den
   Anfangsbestand. Im homogenen
   Kohortenmodus wird die nach Gutschrift und laufender Praemienzuweisung
   bestehende Verpflichtung proportional zur Zahl der Toten freigesetzt,
   mit expliziter Rundung; beim vollstaendigen Abgang der Rest. Im
   Policenmodus gilt die Summe der betroffenen Policenwerte. Die
   Todesfallleistung ist zunaechst ein separat gelieferter,
   nichtnegativer Szenariobetrag. Sie muss **nicht** dem freigesetzten
   Buchwert entsprechen; die Differenz wirkt auf das Ergebnis. Eine
   produktspezifische Todesfallgarantie wird damit nicht behauptet.
6. Danach laufen die faelligen, nicht bereits verstorbenen Policen ab.
   Ihre Buchverpflichtung wird freigesetzt. Die explizite oder bei
   Ausgabe festgelegte Ablaufleistung kann hoeher sein, darf aber nicht
   unter der freigesetzten Garantieverpflichtung liegen. PR159s
   Gleichsetzung bleibt ein Spezialfall.
7. Erst nach den Abgaengen werden neue Kohorten mit eigener Stueckzahl,
   Ausgabezeit, Laufzeit und Garantiesatz aufgenommen. Ihre Praemie
   und Verpflichtungszuweisung zaehlen in dieser Periode, die erste
   Garantie erst in der Folgeperiode. Neuvertraege koennen im
   Ausgabezeitraum weder sterben noch ablaufen.
8. Aufwand und explizit der Sparte zugeteilte Kapitalbewegungen werden
   gebucht; Schlussbestand und Schlussbilanz werden atomar abgestimmt.
   Nur der Schlussbestand muss nichtnegative Aktiva zeigen. Eine
   intraperiodische Liquiditaetspruefung ist noch kein Vertragsbestandteil.

Die Garantieverpflichtung ist ein fortgeschriebener **Modellbuchwert**.
Es gibt keine gesetzliche Rueckstellung, marktwertige Bewertung,
Solvency-II-Aussage oder historische Vollgleichheit. Rueckkauf, Bonus
und automatische Stornostrategie sind fuer diesen Workshop-Schnitt
ausgeschlossen. Mortalitaet ist ein exogener Risikotreiber, keine
VN-Strategie. PR164 hat eine separate deterministische Zaehl- und
Auswahlregel fuer enumerierte Policen festgelegt, ohne RNG-Ziehung;
der read-only v3-Vertrag selbst bleibt unveraendert.

## Offene Implementierungsgates

- PR161: v3-Teil-Eingang und atomare Validierung fuer Tod und Kapital im
  geschlossenen Bestand mit erster Rechnung umgesetzt; siehe
  `ims_2x_life_closed_cohort_death_capital.md`.
- PR162: Neugeschaeft/Kohorten mit konkreter Verteilung der Praemien
  umgesetzt; siehe `ims_2x_life_cohort_new_business.md`.
- PR163: vollstaendig enumerierter Policenmodus mit expliziter
  abweichender Ablaufleistung umgesetzt; der alternative,
  unveraenderliche Ausgabeterm bleibt offen. Siehe
  `ims_2x_life_policy_maturity.md`.
- PR164: separate deterministische Anlage- und Mortalitaetsquellen,
  Zaehlrundung und Periodenfenster je VU umgesetzt; siehe
  `ims_2x_life_assumptions.md`. Kein Lebens-Runner-Anschluss.
- PR165: fluechtige kontrollierte Lebens-Periodenkette bis 100 mit
  PR164-Quellen und PR163-Bilanz umgesetzt; siehe
  `ims_2x_life_period_chain.md`.
- PR166-167: Ergebnisablage/Export und gefuehrte Workbench. Erst
  danach ist dies ein bedienbares Workshop-Segment.
