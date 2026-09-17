# PR168: Eigenstaendiger Kranken-Vertrag

Stand: 2026-09-17
Vertrag: `ims.health-sector-contract.v1`

## Herkunft und fachliche Grenze

| Historischer Ausgangspunkt | Python-Ziel | Keine stillschweigende Zuordnung |
| --- | --- | --- |
| `IMSDATA.C`: `MAXSPARTEN 2`, `classVU.Sp[1/2]`, `classVN.Rk[1/2]` | `ims.model.health_sector_contract` beschreibt die Taxonomie-ID `health`. | Die zweite alte Position wird **nicht** als Kranken identifiziert. Das C-Kuerzel `KV` reicht nicht als Nachweis: die Felder und `IMS.E` beschreiben Schadenwahrscheinlichkeit, Schadenhoehe, Praemie und Schadenreserve. |
| `ims.accounting.model_balance_contract` (PR155) und `ims.model.life_sector_contract` (PR158) | Separater Zustands- und Flussvertrag fuer Kranken. | Gleiche Bilanzidentitaet ist kein Beleg gleicher Reserven-, Tarif- oder Risikosemantik. Keine alte Schaden- oder Lebensregel wird wiederverwendet. |

PR168 ist ein **neuer IMS-2.x-Zielvertrag**, nicht die Portierung eines
historischen Krankenmodells. `GET /api/model/health-sector-contract` liefert
ihn rein lesend ueber FastAPI und Starlette. Keine Eingabe, Berechnung,
Speicherung, Strategiezuweisung oder Ausfuehrung wird freigegeben.

## Kleiner Ausgangsfall

Pro Versicherer gibt es anfangs einen geschlossenen, homogenen Bestand
aktiver Krankenvertraege. Die Vertragszahl ist innerhalb der Periode
konstant und wird explizit fortgetragen. Eine IMS-Periode ist **kein
Kalenderjahr**. Neugeschaeft und Austritte sind in diesem ersten Fall
ausgeschlossen, nicht als null beobachtete historische Abgaenge zu lesen.

Die Kasse, eine **Verpflichtung fuer angefallene, noch nicht bezahlte
Leistungen** und Eigenkapital bilden eine einfache Modellbilanz. Am
Anfang und Ende gilt `Kasse = offene Leistungsverpflichtung + Eigenkapital`.
Vereinnahmte Beitraege sind hier auch periodengleich verdient.
`benefits_incurred` werden im Ergebnis und in der Verpflichtung erfasst;
`benefits_paid` mindern Verpflichtung und Kasse, aber nicht nochmals das
Ergebnis. Auszahlungen duerfen nicht groesser als die alte und neue
offene Verpflichtung zusammen sein. Anlageergebnis und bezahlter
Betriebsaufwand fallen ebenfalls periodengleich an. Kapitalbewegungen
veraendern Kasse und Eigenkapital, aber nicht den Periodengewinn.
Kasse und Leistungsverpflichtung bleiben nichtnegativ; Eigenkapital und
Anlageergebnis duerfen vorzeichenbehaftet sein.

Im geschlossenen Ausgangsfall ohne aktive Vertraege sind neue
Beitragseinnahmen und neu angefallene Leistungen null; eine bereits
offene Leistung darf noch bezahlt werden. Alle vier Schlussbestaende
(Vertraege, Kasse, Leistungsverpflichtung, Eigenkapital) sind die
Anfangsbestaende der Folgeperiode. Dezimalstrings mit vier
Nachkommastellen sind fuer PR169 vorgesehen; PR168 parst oder rundet
keine Betragswerte.

## Strategie- und Quellenverantwortung

Die benannten Anschlussstellen `health_insurer_pricing` (VU: kuenftiger
Beitrag je Vertrag) und `health_policyholder_switching` (VN: kuenftige
Bestandswahl) sind **nicht aktiv**. Insbesondere wirkt die VN-Stelle
nicht auf den hier geschlossenen Bestand. Formel, Fristen, Berechtigung
und Parameterbindung werden vor einer Aktivierung separat entschieden.
Angefallene Leistungen sind ein exogener Szenariofluss und koennen
nicht durch eine VU-Regel einfach wegentschieden werden. Alle Quellen
fuer PR169 sind explizit; `Sp[1/2]`, `Rk[1/2]` und bestehende Schaden-
Regelkataloge liefern keine Krankenwerte.

## Grenzen und naechste Schritte

Keine Tarife, Alters- oder Morbiditaetsstruktur, Behandlungen,
Alterungsrueckstellung, Forderungen, Rueckversicherung, gesetzliche
Bilanz oder Solvency-II-Bewertung. Diese Modellrechnung darf nicht als
realistischer Privatkrankenversicherungsbestand oder historische
Vollgleichheit bezeichnet werden.

PR169 entscheidet das Eingabeformat und prueft eine kleine deterministische
Ein-/Zweiperiodenrechnung mit Bilanz- und Bestandsinvarianten atomar.
PR170 klaert anschliessend die Kapitalallokation und Konsolidierung der
vier Modellsegmente. Die offenen Produkt-, Reserve- und Strategiethemen
benoetigen eigene fachliche Zuschnitte vor einem groesseren Gesundheitsmodell.
