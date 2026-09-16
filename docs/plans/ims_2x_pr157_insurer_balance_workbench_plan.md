# PR157: Versicherer-Modellbilanz in Workbench und XLSX

Stand: 2026-09-16

## Ziel

Die beiden in PR156 berechneten Nichtleben-Sparten werden fuer genau einen
Versicherer und ein gemeinsames 1-100-Periodenfenster zu einer einfachen
Gesamt-Modellbilanz abgestimmt. Das Ergebnis ist im Browser lesbar und als
XLSX ohne Veraenderung der Zahlen herunterladbar.

## Herkunft und fachliche Grenze

`IMSDATA.C` kennt VU-Sparten 1/2 mit `Pr`, `Wa`, `Rs`, `Vn`, `Sa`, `Sh`;
`IMS.E` und die portierte VN-Abrechnung veraendern `Rs`. Das ist kein
Bilanzsystem. PR157 summiert ausschliesslich **explizite PR156-Szenario-
Eingaben** fuer `motor` und `property_liability`. Es findet keine
historische Spartenbindung, Bilanzkalibrierung oder Solvency-II-Ableitung
statt.

## Schnitt

1. Versionierter Gesamteingang mit genau zwei PR156-Dokumenten, gleicher
   `insurer_id` und lueckenlos identischem Periodenfenster. Alle
   Einzelrechnungen muessen gueltig sein; sonst kein Gesamtergebnis.
2. Fuer jede Periode werden alle 14 PR155-Betragsfelder mit festem
   `Decimal`-Kontext summiert. Anfangs- und Schlussidentitaet sowie
   Carryover werden gesondert geprueft.
3. Zustandslose API: read-only Vertrag, POST zur fluechtigen Rechnung,
   POST zum XLSX-Download. Ergebnis-Digest und `If-Match` koppeln den
   Download an die im Browser gezeigten Zahlen.
4. XLSX enthaelt Gesamt, Kfz und Sach-Haftpflicht mit denselben
   kanonischen Dezimalstrings; diese stehen absichtlich als Textzellen,
   damit Excel keine unbemerkte Praezision verliert. Herkunftsblatt nennt
   Modellgrenzen. Keine Server-Dateiablage.
5. Workbench: editierbare Anfangsbestaende und Periodenfluesse beider
   Sparten, Ergebnisumschaltung Gesamt/Einzelsparte, klare Fehlerpfade
   und Download nur fuer den aktuellen berechneten Entwurf. Breiter und
   schmaler Viewport werden geprueft.

## Risiken und offen

Eine XLSX-Textzelle ist exakt, aber nicht sofort als Excel-Zahl
aggregierbar. Das ist eine bewusste Praezisionsgrenze; numerische
Analyseformate brauchen eine separat deklarierte Rundungsentscheidung.
Die Anbindung an historische Runner und vier Sparten folgt nicht in
diesem PR. Die Workbench-Rechnung ist eine Modellbilanz aus eigenen
Szenariowerten, kein gesetzlicher Abschluss.
