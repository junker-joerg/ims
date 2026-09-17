# PR162: Neugeschaeft mit getrennten Lebens-Kohorten

Stand: 2026-09-17
Status: umgesetzt als separater, versionierter Python-Rechenschnitt

## Ziel und Abnahmegrenze

Ein Lebenssegment eines Versicherers fuehrt mehrere benannte homogene
Kohorten. Der Anfangsbestand und jede neue Ausgabe besitzen explizite
Stueckzahlen, Laufzeiten, feste Garantiesaetze und Buchverpflichtungen.
PR161 bleibt unveraendert. Kein Policenmodus, keine variable
Ablaufleistung, keine automatische Mortalitaet/Anlage, kein Runner,
keine API, Speicherung, UI oder Gesamtbilanzaddition.

## Modellentscheidungen

- Anfangskohorten koennen vor Periode 1 ausgegeben sein. Ihr ganzzahliger
  `issue_period` ist hoechstens 0 und stimmt mit
  `remaining_periods - issue_term_periods` ueberein. Neue Kohorten
  erhalten die laufende Modellperiode als Ausgabeperiode und die volle
  Laufzeit als Schluss-Restlaufzeit.
- Eine Kohorte hat eine stabile, eindeutige ID. IDs werden auch nach
  vollstaendigem Abgang nicht wiederverwendet. Hoechstens 100 Kohorten
  werden pro Fall ausgegeben/uebernommen; dies ist eine technische Grenze
  dieses schmalen Rechenschnitts, nicht des v3-Zielvertrags.
- Laufende Praemie, Zuweisung, Todesfallzahl und Todesfallleistung werden
  fuer **jede aktive Anfangskohorte** explizit geliefert. Fehlende oder
  unbekannte Kohortenfluesse sind Fehler. Tod vor Ablauf; Rundung der
  Gutschrift und proportionalen Todesfallfreisetzung je Kohorte halbgerade
  auf `0.0001`. Ablaufleistung bleibt gleich der Rest-Buchverpflichtung.
- Neue Kohorten werden erst nach den Abgaengen aufgenommen. Ihre
  Praemie und Zuweisung zaehlen bereits in dieser Periode zu Aktiva bzw.
  Garantieverpflichtung, aber es gibt weder Gutschrift noch Tod oder
  Ablauf im Ausgabezeitraum. Die erste Gutschrift erfolgt in der
  Folgeperiode auf die dann bestehende Anfangsverpflichtung.
- Anlageergebnis, Aufwand und Kapitalbewegungen bleiben explizite
  Segmentfluesse. Sie werden nicht stillschweigend auf Kohorten verteilt.
  Bei vollstaendig erloschenem Bestand sind leere Zwischenperioden
  zulaessig; spaeteres Neugeschaeft kann ihn erneut aufbauen.
- Kohorten-ID-Reihenfolge ist fuer Rechnung und Ergebnis kanonisch.
  Anfangs-/Schlussstueckzahlen und -verpflichtungen stimmen mit den
  Kohortensummen; Aktiva = Verpflichtung + Eigenkapital. Jeder Fehler
  verwirft alle Zeilen. Null-Neugeschaeft mit genau einer Anfangskohorte
  reproduziert die gemeinsamen PR161-Zeilenwerte.

## Herkunft, Risiken, Testumfang

`IMSDATA.C` (`MAXSPARTEN 2`, `classVU.Sp`, `classVN.Rk`) und `IMS.E`
belegen Praemie und Schadenreserve der Altsparten, aber keine
Lebens-Kohorten oder Ausgabeparameter. Der Python-Schnitt folgt dem
expliziten PR160-v3-Zielvertrag. Das neue Ausgabe-Timing und die
Anfangskohorten-Datierung sind Modellentscheidungen, nicht aus C
abgeleitet. Getestet werden fruehe/spaete Ausgabe, unterschiedliche
Garantiesaetze und Laufzeiten, Tod/Ablauf je Kohorte, Summenidentitaeten,
stabile Prefixe und Reihenfolge, PR161-Spezialfall sowie atomare Fehler
bei doppelten IDs, fehlenden Fluesse, ungueltigen Ausgabeparametern,
Praemiengrenzen und negativer Schlussaktivseite. Keine historische
Vollgleichheit oder gesetzliche Bilanz wird behauptet.
