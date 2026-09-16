# PR159: Deterministischer Lebensfall

Stand: 2026-09-16
Vertrag: `ims.life-sector-contract.v2`
Eingang: `ims.life-model-balance-input.v1`
Ergebnis: `ims.life-model-balance-result.v1`

## Ursprung und fachliche Grenze

| Ursprung | Python-Ziel | Abgrenzung |
| --- | --- | --- |
| `IMSDATA.C`, `MAXSPARTEN 2`, `classVU.Sp[1/2]`, `classVN.Rk[1/2]`; `IMS.E` mit Schaden-, Praemien- und Reserveoperationen | `ims.accounting.life_model_balance.build_life_model_balance` | Die historischen Vektoren belegen kein Lebensmodell. Keine Altwerte oder Schadenregeln werden als Lebensdaten umgedeutet. |
| PR158 `ims.model.life_sector_contract` | v2 beschreibt die erste reine Rechnung; v1 bleibt unter `/api/model/life-sector-contract/v1` abrufbar. | Neue IMS-2.x-Modellkonvention, keine historische Vollgleichheitsbehauptung. |

## Bewertungs- und Buchungsfolge

Ein Versicherer hat genau einen geschlossenen, homogenen Bestand. Die
Restlaufzeit zaehlt Modellperioden, nicht Jahre. Der feste Garantiesatz
von 0 bis 1 je Modellperiode ist Ausgabeterm und keine VU-Strategie.
Eine Eingabe umfasst hoechstens 100 aufeinanderfolgende Perioden und
endet spaetestens mit der anfangs verbleibenden Vertragslaufzeit.

1. Periodenbeginn: aktive Vertraege, Restlaufzeit, deckende Aktiva,
   Garantieverpflichtung und Eigenkapital werden aus dem Anfangsbestand
   beziehungsweise der Vorperiode uebernommen. Aktiva = Verpflichtung +
   Eigenkapital muss gelten.
2. Garantie: `opening_guarantee_liability * guaranteed_rate_per_period`.
   Nur dieses Produkt wird explizit auf 0,0001 Modellwaehrungseinheiten
   mit `ROUND_HALF_EVEN` quantisiert. Kein Float und keine weitere
   implizite Rundung.
3. Praemien und Fluesse: Die Praemie wird eingezogen und erst **nach** der
   Garantiegutschrift am Periodenende der Verpflichtung zugewiesen.
   `premium_liability_allocation <= premiums_collected`. Nicht
   zugewiesene Praemie bleibt im Eigenkapital. Anlageergebnis (auch
   negativ) und bezahlter Aufwand kommen explizit aus dem Szenario.
4. Ablauf: Bei Restlaufzeit eins laufen alle Vertraege am Periodenende
   ab. Die nach Gutschrift und Praemienzuweisung bestehende Verpflichtung
   wird vollstaendig freigesetzt und in derselben Hoehe ausgezahlt.
   Davor gibt es keine Leistung und keine Freisetzung.
5. Schluss: Aktiva, Garantieverpflichtung und Eigenkapital werden nach
   den Gleichungen des PR158-Vertrags fortgeschrieben; die Bilanzidentitaet
   und ein nichtnegatives Aktivum sind zwingend. Alle Zeilen werden nur
   bei komplett gueltigem Eingang und Verlauf zurueckgegeben.

Die Eingaben verwenden Dezimalstrings mit bis zu 12 Vor- und vier
Nachkommastellen; der Garantiesatz hat bis zu sechs Nachkommastellen.
Berechnete Ausgaben koennen mehr Vorkommastellen haben und sind mit vier
Nachkommastellen kanonisiert.
Eine einzelne Beispielrechnung mit zehn Policen ueber zwei Perioden liegt
in `tests/fixtures/life_model_balance_v1.json`. Garantie: 5,0000 und
5,7000; bei Ablauf werden 128,7000 freigesetzt und ausgezahlt. Die
Schlussaktiva und das Eigenkapital betragen jeweils 22,3000.

## Ausdrueckliche Luecken im Stand PR159

Tod, Rueckkauf, Bonus, Neugeschaeft, Kapitalbewegungen, individuelle
Vertragswerte und abweichende Ablaufleistungen sind nicht implementiert.
Es gibt keine automatische Anlage-, Sterblichkeits- oder Stornostrategie,
keinen Runner, keine UI-Eingabe, Speicherung oder Excel-Ausgabe fuer
Leben. `life` wird noch nicht zur heutigen Zwei-Sparten-Gesamtbilanz
addiert; der vierteilige Anschluss ist nach der Lebens-Nachplanung fuer
PR170 geplant. Die Rechnung
ist weder gesetzliche Bilanz noch Solvency-II-Bewertung oder
historischer Gleichheitsnachweis.

Das ist keine dauerhafte Ausschlussliste: PR160-167 planen in kleinen
Schritten Tod, Neugeschaeft, Kapitalbewegungen, begrenzte Einzelpolicen,
abweichende Ablaufleistungen, deterministische Anlage- und
Mortalitaetsannahmen sowie Runner, Ergebnisablage, XLSX und gefuehrte
Workbench-Eingaben. Nur Rueckkauf und Bonus sowie eine automatische
Stornostrategie bleiben fuer diese Workshop-Stufe bewusst ausserhalb des
Umfangs. Die genaue PR-Folge und ihre Abnahmekriterien stehen in
`docs/plans/ims_2x_life_workshop_expansion_plan.md`.
