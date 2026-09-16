# PR158: Eigenstaendiger Lebenssparten-Vertrag

Stand: 2026-09-16
Vertrag: `ims.life-sector-contract.v1`

## Herkunft und Abgrenzung

| Historischer Ausgangspunkt | Python-Ziel | Fachliche Grenze |
| --- | --- | --- |
| `IMSDATA.C`, `MAXSPARTEN 2`, `classVU.Sp[1/2]`, `classVN.Rk[1/2]` | `ims.model.life_sector_contract` beschreibt die neue ID `life` aus der Taxonomie. | Keine der zwei alten Positionen wird als Lebensversicherung identifiziert. Auch das C-Kuerzel `LV` ist kein Beleg dafuer. |
| `IMSDATA.C`, ein `Vr` je VU/VN; `IMS.E`, Schaden-, Praemien- und Reserveoperationen | Separate Anschlussstellen fuer VU-Bonus und VN-Rueckkauf. | Kein historischer Regelsatz, keine Snapshot-Materialisierung und keine Uebernahme der Schadenformel. |
| PR155-157, Cash-/Schadenmodellbilanz fuer zwei Nichtleben-Segmente | Vermoegen, Garantieverpflichtung und Eigenkapital als **anderes** Bilanzmodell. | Keine automatische Addition zur Zwei-Sparten-Bilanz vor PR162. |

PR158 ist ein neuer IMS-2.x-Zielvertrag, keine Portierung eines alten
Lebensmodells. `GET /api/model/life-sector-contract` liefert ihn rein
lesend ueber beide Webserver-Varianten. Weder Eingaben noch Ergebnisse
werden gespeichert; es gibt keinen Berechnungs- oder Simulationsaufruf.

## Erster Modellumfang

Pro Versicherer beginnt **ein geschlossener homogener Vertragsbestand**.
Ein Garantievertragssatz wird bei Ausgabe festgehalten. Die Restlaufzeit
zaehlt IMS-Modellperioden, nicht Kalenderjahre. Ohne Neugeschaeft sinkt
der Bestand nur durch Tod, Ablauf oder Rueckkauf; diese Abgaenge sind
disjunkt. Am Ende der Vertragslaufzeit muessen die verbleibenden Vertraege
ablaufen. Spartenuebergreifende Umschichtungen sind nicht enthalten.

Die drei Bilanzgroessen sind deckende Vermoegenswerte,
Garantieverpflichtung und Eigenkapital. Anfangs und am Periodenende gilt
`Vermoegen = Garantieverpflichtung + Eigenkapital`. Praemien und
Anlageergebnis erhoehen das Vermoegen; Todesfall-, Ablauf- und
Rueckkaufsleistungen sowie Aufwand vermindern es. Zugewiesene Praemien,
Garantie- und Bonusgutschrift erhoehen die Verpflichtung, eine
Freisetzung (`liability_release`) vermindert sie. Die Freisetzung ist **nicht automatisch**
gleich der Auszahlung. Das Periodenergebnis ist der Vermoegensfluss ohne
Kapitalbewegungen abzueglich der Veraenderung der Verpflichtung.

Die fuenf Bestandswerte (Vertragszahl, Restlaufzeit, Vermoegen,
Garantieverpflichtung, Eigenkapital) werden explizit in die Folgeperiode
getragen. Modellbetraege sollen wie in PR156 als Dezimalstrings ohne
implizite Rundung gefuehrt werden; das Gutschriftverfahren selbst ist
noch nicht beschlossen.

## Strategiegrenze

`life_insurer_bonus_crediting` beschreibt eine kuenftige VU-Entscheidung
ueber eine zusaetzliche Bonusgutschrift. Sie darf den bei Ausgabe
festgelegten Garantiesatz nicht nachtraeglich vermindern.
`life_policyholder_surrender` beschreibt eine kuenftige VN-Entscheidung,
die nur aktive Vertraege betrifft. Beide Namen sind **Anschlussstellen**,
keine heute waehlbaren Katalogregeln. Parameterformeln, benoetigte
Marktwerte, Einzelkundenaggregation und Periodenfenster-Zuweisung sind
vor Ausfuehrung separat zu klaeren. PR154s Schadenregel-Plan laesst
`life` weiterhin nicht zu.

## Offene Fachfragen fuer PR159

- Wann innerhalb der Periode faellt eine Praemie an, und auf welcher Basis
  und mit welcher Quantisierung wird die Garantie gutgeschrieben?
- Wie werden Verpflichtungen je Todesfall, Ablauf und Rueckkauf
  freigesetzt? Leistungen und Verpflichtungsfreisetzung koennen abweichen.
- Das Anlageergebnis ist vorerst ein expliziter Szenariofluss, keine aus
  einer Anlagestrategie oder historischen Zinsreihe abgeleitete Groesse.
- Kein Neugeschaeft, mehrere Kohorten, Sterbetafeln, Stochastik,
  regulatorische Rueckstellungsbewertung oder Solvency-II-Aussage.

Tests pruefen die eindeutigen Felder, Gleichungen und Carryover-Beziehungen,
die Trennung beider Strategieakteure, JSON-Stabilitaet, fehlende
Schreib-/Runnerpfade und die GET-only-API. Ein Ergebnisvergleich ist noch
nicht moeglich, weil PR158 keine Werte berechnet.
