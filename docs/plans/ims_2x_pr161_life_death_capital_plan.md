# PR161: Tod und Kapital im geschlossenen Lebensbestand

Stand: 2026-09-17
Status: umgesetzt als eigener, versionierter Rechenschnitt ohne Runner

## Ziel und Grenze

Eine homogene, geschlossene Lebens-Kohorte wird mit expliziten Todesfaellen,
getrennter Todesfallleistung und Verpflichtungsfreisetzung sowie expliziter
Kapitalzufuhr/-ausschuettung deterministisch fortgeschrieben. Die PR159/v2-
Eingabe und -Rechnung bleiben unveraendert. Kein Neugeschaeft, keine
Einzelpolicen, keine variable Ablaufleistung, keine automatische
Sterblichkeit oder Anlage, kein Runner, keine UI, keine Speicherung.

## Annahmen und Abnahme

- Neuer v3-Teil-Eingang fuer eine Kohorte; laufende Praemien und deren
  Zuweisung sind explizit und voneinander getrennt. Todesfallzahl und
  -leistung sind explizite Szenariowerte; ohne Todesfall ist die
  Todesfallleistung null. Bei Todesfall ist auch eine Leistung null
  zulaessig, solange keine Produktgarantie festgelegt wurde.
- Garantie auf die Anfangsverpflichtung, dann laufende Praemienzuweisung,
  dann Tod, dann Ablauf. Tod mindert nur den Anfangsbestand. Freisetzung
  proportional zur Verpflichtung nach Gutschrift/Zuweisung, halbgerade
  auf vier Nachkommastellen; bei vollstaendigem Abgang wird der ganze
  verbleibende Betrag freigesetzt. Am Laufzeitende laufen alle Ueberlebenden
  ab; die Ablaufleistung entspricht hier noch dem freigesetzten Buchwert.
- Kapitalzufuhr/-ausschuettung erfolgen am Periodenende. Sie veraendern
  Aktiva und Eigenkapital, nicht Periodenergebnis oder Garantieverpflichtung.
  Nur Schlussaktiva muessen nichtnegativ sein; keine intraperiodische
  Liquiditaets- oder Solvenzpruefung.
- Bestand, Verpflichtung, Aktiva und Eigenkapital tragen exakt in die
  Folgeperiode. Bei vollstaendig erloschener Kohorte ist keine weitere
  Periode im selben Eingang zulaessig. Jeder Fehler liefert null Zeilen.
- Positiv-/Negativfaelle pruefen Tod vor Ablauf, volle Ausloeschung,
  abweichende Leistung/Freisetzung, Kapitalwirkung, Rundung, stabile
  Prefixe, 100 Perioden und PR159-Spezialfall ohne Tod/Kapital.

## Herkunft und Risiken

`IMSDATA.C` (`MAXSPARTEN 2`, `classVU.Sp`, `classVN.Rk`) und `IMS.E`
enthalten Schadens-/Reserveoperationen, aber keine belegte historische
Lebensversicherung. Der neue Python-Rechenschnitt ist eine explizite
IMS-2.x-Erweiterung des PR160-Vertrags, keine Portierung einer C-Lebensregel.
Die proportionale Freisetzung ist eine Kohorten-Annahme; individuelle
Policenwerte und andere Rundungsgranularitaeten folgen erst PR163.
Keine historische Vollgleichheit, gesetzliche Bilanz oder Solvency-II-
Bewertung wird behauptet.
