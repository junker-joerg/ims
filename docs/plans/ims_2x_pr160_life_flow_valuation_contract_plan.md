# PR160: Lebensfluss- und Bewertungsvertrag v3

Stand: 2026-09-17
Status: umgesetzt als rein lesender v3-Zielvertrag

## Ziel und Schnitt

PR160 legt die Zielsemantik fuer den Ausbau nach PR159 fest. Die neue
Version ist ausschliesslich lesbar und explizit unter
`GET /api/model/life-sector-contract/v3` erreichbar. Der bisherige
Standard-Endpunkt bleibt v2 und die PR159-Eingabe-/Ergebnisversion
unveraendert. Weder v3-Eingabevalidierung noch Lebensrechnung, Runner,
Speicherung oder UI werden hier freigegeben.

## Beschlossene Grenzen

1. Ein `life`-Segment je Versicherer, bis 100 IMS-Modellperioden. V3
   fuehrt mehrere eindeutig bezeichnete Kohorten mit festen Ausgabe-
   parametern. Fuer kleine Faelle ist ein vollstaendig enumerierter
   Policenmodus bis 100 aktive Policen vorgesehen; groessere Bestaende
   bleiben aggregierte Kohorten. Moduswechsel innerhalb eines Laufs
   werden nicht implizit vorgenommen.
2. V2 bleibt ein gueltiger Spezialfall: ein geschlossener homogener
   Bestand, kein Todesfall/Neugeschaeft/Kapital, Ablaufleistung gleich
   freigesetzter Garantieverpflichtung. Die v2-Gutschrift auf der
   Anfangsverpflichtung bleibt unveraendert.
3. Periodenfolge: Anfangszustand; Anlageergebnis auf Anfangsaktiva;
   Garantie auf Anfangsverpflichtung; laufende Praemie und Zuweisung;
   Todesfaelle; Ablauf der danach verbleibenden faelligen Policen;
   Ausgabe neuer Kohorten samt Praemie und Zuweisung; Aufwand und
   Kapitalbewegungen; Schlussbilanz. Neugeschaeft traegt erst ab der
   Folgeperiode Garantie und ist im Ausgabezeitraum nicht abgangsfaehig.
4. Im aggregierten homogenen Bestand wird die Verpflichtung bei Tod
   proportional nach Stueckzahl nach Gutschrift und laufender
   Praemienzuweisung freigesetzt; bei vollstaendigem Abgang der Rest.
   Im Policenmodus wird stattdessen die Summe der betroffenen
   Policenwerte freigesetzt. Leistung und Freisetzung sind getrennt.
5. Eine Todesfallleistung ist ein expliziter, nichtnegativer
   Szenariobetrag, bis ein eigener Produktausgabeterm beschlossen wird.
   Sie ist nicht stillschweigend gleich der Reserve. Die abweichende
   Ablaufleistung muss mindestens die freigesetzte Garantieverpflichtung
   decken; eine Mehrleistung mindert das Periodenergebnis.
6. Kapitalzufuhr und -ausschuettung sind Eigenkapitalfluesse, weder
   Praemie noch Ertrag. Die Zuordnung zur Sparte ist explizit; bei
   spaeterer Gesamtbilanz darf dieselbe Bewegung nur einmal erscheinen.
7. Anlage und Mortalitaet sind pro Periode entweder explizit oder
   deterministisch aus versionierten Parametern abgeleitet. Ein
   berechneter Anlagefluss verwendet Anfangsaktiva, nicht die erst
   spaeter eingezogene Praemie. Mortalitaet ist exogen und keine
   VN-Strategie. Kein RNG und kein Doppelzaehlen von Flussmodi.
8. Dezimalstrings und explizite Rundung bleiben wie in v2. Der
   Geldfluss, die Garantieverpflichtung, das Eigenkapital sowie
   Stueckzahlen und Kohortensummen stimmen am Periodenende atomar.

## Herkunft und Unsicherheit

`IMSDATA.C` (`MAXSPARTEN 2`, `classVU.Sp`, `classVN.Rk`) und `IMS.E`
liefern Schaden- und Reservemerkmale, aber keinen nachgewiesenen
Lebensvertrag. V3 ist ein IMS-2.x-Zielvertrag, keine Portierung einer
historischen Lebensregel. Die konkrete v3-Payloadform, detaillierte
Policenverteilung und Strategiezuteilung werden in PR161-164 vor
Ausfuehrung geprueft. Gesetzliche Rueckstellung, Solvency-II-Aussage,
Rueckkauf und Bonus bleiben ausserhalb dieses Schritts.

## Validierung

- Tests fuer vollstaendige, widerspruchsfreie v3-Vertragsangaben,
  JSON-Stabilitaet und GET-only-API in FastAPI und Starlette.
- V1/v2-Payloads und PR159-Fall bleiben byte-/wertgleich; kein
  neuer Berechnungspfad oder Schreibzugriff.
- Doku benennt Ursprung, getroffene Annahmen und offene Abnahmefragen.
