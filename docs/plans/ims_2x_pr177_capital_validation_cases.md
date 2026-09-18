# PR177: Feste Kapital-Modellfaelle und Invarianten

Stand: 2026-09-18
Status: umgesetzt; PR178 Kapitalansicht und Export folgt

## Ziel und Herkunft

PR177 nimmt die bestehende, rein modellhafte Kette PR172-176 mit
nachrechenbaren festen Faellen ab. Er fuehrt weder Fachlogik noch einen
Runner ein. `IMSDATA.C` (`LV`/`KV`, `Pr`, `Rs`, `Sh`) enthaelt die
historischen Sparten-Zustandsvektoren, aber keine Solvency-II-Bilanz,
keine Risikokapitalformel und keine aufsichtsrechtliche Schwelle.
Die Zuordnung ist deshalb eine neue Seminar-Modellrechnung, keine
Portierung einer historischen Kapitalzahl und keine historische
Vollgleichheit.

| Quelle | Gepruefte Entsprechung | Grenze |
| --- | --- | --- |
| PR170 Vier-Sparten-Bilanz und PR172 Modellbilanz | Saldo je Sparte, Gesamt-Eigenmittel-Proxy und gepruefte Quellen-Digests | Modellwaehrung, keine regulatorische Bewertung |
| PR173/174 deklarierte Teilpositionen und Modulsaetze | nur zugeordnete Teilpositionen tragen Stressverluste | keine empirische SCR-Kalibrierung |
| PR175 deklarierte Gegenpartei-, Betriebs- und Ein-Faktor-Verluste | Brutto, Puffer und Netto sind algebraisch geschlossen | Puffer ist eine eigenstaendige Modellannahme |
| PR176 Managementgrenzen | Restproxy und inklusive Vergleiche | keine Compliance-Entscheidung; SCR/MCR bleiben `null` |

## Feste Fallmatrix

Alle Zahlen sind Modellwaehrung mit vier Dezimalstellen. Ausgangspunkt
ist der bereits versionierte Seminarfall in
`tests/test_solvency_capital_readiness.py::_input`. Die Erwartungen in
`tests/test_solvency_capital_chain_cases.py` sind als feste Dezimalwerte
notiert und werden nicht aus einer zweiten Produktfunktion abgeleitet.

| Fall | Geaenderte Annahme | Eigenmittel-Proxy | Brutto | Netto | Restproxy |
| --- | --- | ---: | ---: | ---: | ---: |
| Basis | keine | 319.0000 | 1.7750 | 1.6000 | 317.4000 |
| Bilanz plus eins | Motor-Asset-Anpassung 10 auf 11 | 320.0000 | 1.7750 | 1.6000 | 318.4000 |
| Leben-Verpflichtung | Lebens-Haftungsanpassung -3 auf -2 | 318.0000 | 1.7750 | 1.6000 | 316.4000 |
| Marktstress | Markt-Modulsatz 0.25 auf 0.50 | 319.0000 | 2.0250 | 1.8500 | 317.1500 |
| Lebensstress | Lebens-Modulsatz 0.125 auf 0.25 | 319.0000 | 1.9000 | 1.7250 | 317.2750 |
| Krankenstress | Kranken-Modulsatz 0.10 auf 0.30 | 319.0000 | 1.9750 | 1.8000 | 317.2000 |
| Gegenpartei | Verlustsatz 0.4 auf 0.6 | 319.0000 | 1.9750 | 1.8000 | 317.2000 |
| Betriebsereignis | Verlust 0.2 auf 0.4 | 319.0000 | 1.9750 | 1.8000 | 317.2000 |
| Puffer | Anrechnung 0.175 auf 0.25 | 319.0000 | 1.7750 | 1.5250 | 317.4750 |
| Unabhaengige Faktoren | alle Ladungen 1 auf 0 | 319.0000 | 0.8821 | 0.7071 | 318.2929 |
| Ohne Stress | Module/Faelle/Puffer leer bzw. null | 319.0000 | 0.0000 | 0.0000 | 319.0000 |
| Grossschaden | Betriebsereignis 0.2 auf 400 | 319.0000 | 401.5750 | 401.4000 | -82.4000 |

Die Werte erlauben insbesondere die getrennte Pruefung: Mehr Aktiva
heben nur den Bilanzproxy; hoehere positive Stressannahmen heben den
Modellverlust und senken den Restproxy; ein groesserer separat
deklarierter Puffer wirkt in Gegenrichtung. Die Null- und
Grossschadenfaelle pruefen die Grenzwerte ohne stilles Kappen.

## Invarianten und Fehlergrenze

- Je Spartensaldo und gesamt gilt `Eigenmittel-Proxy = angepasste
  Aktiva - angepasste Verpflichtungen = Schluss-Eigenkapital +
  Proxy-Aenderung`. Die vier Sparten summieren sich zum Gesamtwert.
- Sechs PR175-Komponenten summieren sich zum unbereinigten Verlust;
  `Diversifikations-Proxy = Summe - Brutto` und
  `Netto = Brutto - angerechneter Puffer`. Bei den zulaessigen
  nichtnegativen Faktorladungen liegt Brutto zwischen groesster
  Komponente und ihrer Summe.
- `Restproxy = PR172-Eigenmittel-Proxy - PR175-Nettoverlust`.
  Die zwei Workshop-Grenzen werden separat und inklusiv verglichen.
- Quellen-Digests verknuepfen PR172, PR174, PR175 und PR176.
  Wiederholte Auswertung desselben Eingangs bleibt identisch.
- Ungueltige Doppelbelegung einer Teilposition oder ungueltiger
  Puffer liefert atomar keine Teilrechnung. Alle regulatorischen
  Kennzahlen bleiben auch bei bestandenen Managementgrenzen `null`.

Die Ein-Faktor-Korrelation ist positiv semidefinit und rein
szenariodeklariert. Eine groessere Faktorladung ist kein
empirischer Beweis groesserer realer Gefahr; die Fallmatrix prueft
lediglich die implementierte Formel. Die PR175-Verluste werden nicht
als Bilanzbuchungen ausgegeben. Fuer SCR, MCR, anrechenbare
Eigenmittel oder Bedeckungsquoten fehlen weiterhin Bewertung,
Kalibrierung und Rechtsstichtag. PR178 darf diese Sperre nur
verstaendlich anzeigen, nicht implizit aufheben.

## Validierung und offene Punkte

`tests/test_solvency_capital_chain_cases.py` prueft die feste
Fallmatrix, Quellenbindung, Monotonie, Grenzwerte und Atomaritaet.
Keine Simulation, keine Speicherung und kein historischer
Vollgleichheitsnachweis. Ein rechtlich und aktuariell freigegebener
SCR-/MCR-Rechner bleibt ein gesonderter Fachauftrag.
