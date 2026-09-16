# PR159: Schmaler deterministischer Lebensfall

Stand: 2026-09-16

## Ziel und Grenze

Der PR158-Vertrag erhaelt eine reine, versionierte Python-Rechnung fuer einen
geschlossenen, homogenen Lebensbestand. Ein Fall darf bis zu 100 explizite
Modellperioden enthalten, jedoch nicht laenger als die anfangs verbleibende
Vertragslaufzeit. Es gibt keinen Runner, keine Speicherung und noch keine
Addition zur Zwei-Sparten-Versichererbilanz; diese folgt erst mit PR162.

## Beschlossene Periodenfolge und Bewertungsbasis

1. Der Garantiesatz ist ein unveraenderlicher Ausgabeterm und liegt im
   Eingangsvertrag zwischen null und eins je Modellperiode. Der Fall
   verwendet ihn unveraendert in allen Perioden.
2. Die Gutschriftbasis ist ausschliesslich die Garantieverpflichtung zu
   Periodenbeginn. Die Garantie wird am Periodenende vor einem Ablauf
   gutgeschrieben. Es wird auf vier Dezimalstellen mit `ROUND_HALF_EVEN`
   quantisiert. Der Gutschriftbetrag wird separat ausgewiesen; es gibt
   keine stillschweigende Rundung anderer Fluesse.
3. Eingezogene Praemien werden am Periodenende, nach der Garantiegutschrift,
   der Verpflichtung zugewiesen. Daher tragen sie erst ab der folgenden
   Periode Garantie. Der nicht zugewiesene Teil bleibt im Eigenkapital.
4. Anlageergebnis und gezahlter Betriebsaufwand sind explizite
   Szenariofluesse. Es gibt weder Sterblichkeit noch Rueckkauf,
   Bonusgutschrift, Neugeschaeft oder Kapitalbewegungen.
5. Wenn die Restlaufzeit eins ist, laufen alle verbliebenen Vertraege am
   Periodenende ab. Die Freisetzung der dann aufgelaufenen
   Garantieverpflichtung und die Ablaufzahlung sind gleich hoch. Eine
   abweichende Leistung oder individuelle Deckung wird hier nicht bewertet.
6. Aktiva = Garantieverpflichtung + Eigenkapital gilt zu Beginn und am
   Schluss jeder Periode. Bestand, Restlaufzeit und Bilanzgroessen werden
   explizit fortgeschrieben. Ungueltige Eingaben oder ein unzulaessiger
   Schlussbestand verwerfen alle Ergebniszeilen atomar.

## Herkunft und Unsicherheit

`IMSDATA.C` (`MAXSPARTEN 2`, `classVU.Sp`, `classVN.Rk`) und `IMS.E`
liefern historische Schaden-/Praemien-/Reserveoperationen, aber keinen
belegten Lebensvertrag. Die Rechnung ist daher eine neue IMS-2.x-Annahme,
kein Nachbau historischer Lebenslogik. Insbesondere sind Garantieverzinsung
auf Anfangsverpflichtung, Endperiodenpraemie und Auszahlung zum Buchwert
bewusst gesetzte Modellkonventionen. Es gibt keine gesetzliche
Rueckstellungsbewertung, Solvency-II-Aussage oder Vollgleichheitsbehauptung.

## Review- und Testumfang

- Reiner Rechenkern und separater v2-Read-only-Vertrag; v1 bleibt abrufbar.
- Fester Zwei-Perioden-Fall mit Ablauf, Bilanz, Carryover und exakten
  Dezimalwerten; Wiederholung und Prefix-Stabilitaet.
- Negativfaelle fuer Vertragsversion, Betrag-/Satzformat, Bestandsdauer,
  Praemienzuweisung, Anfangsbilanz und spaeten Fehlerschluss.
- Gezielte Modell-, API- und Dokumentationstests; kein Simulationslauf.
