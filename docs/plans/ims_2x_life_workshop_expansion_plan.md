# Leben nach PR159: vom Rechenfall zum Workshop-Segment

Stand: 2026-09-17
Status: PR160-167 umgesetzt; PR168 Kranken-Vertrag folgt

## Warum der bisherige Plan nicht ausreichte

PR158/159 liefern einen geschlossenen, homogenen Lebensbestand mit
Garantieverpflichtung und einem festen Ablaufbeispiel. Die bisherige
Roadmap sprang danach direkt zu Kranken und zur Gesamtbilanz. Damit
fehlten fuer ein Management-Seminar ausgerechnet Bestandsbewegungen,
unterschiedliche Vertraege, strategische Stellhebel und ein Bedienweg.
Diese Luecke wird durch acht kleine PRs geschlossen. PR160 hat den
read-only Zielvertrag festgelegt; PR161 rechnet Tod und Kapital im
geschlossenen Bestand. PR162 ergaenzt getrennte Kohorten und
Neugeschaeft; PR163 ergaenzt explizite Policen und Ablaufleistungen.
PR164 hat Anlage- und Mortalitaetsquellen getrennt aufgeloest;
PR165 verbindet sie mit einer fluechtigen, atomaren Lebens-Periodenkette.
PR166 und PR167 sind umgesetzt. PR168 beginnt mit dem Kranken-Vertrag. Die
zuvor geplanten Nummern ab PR160 wurden um acht verschoben.

## Fachlicher Mindestumfang

- **Tod:** explizite oder deterministisch aus einer Szenarioannahme
  abgeleitete Todesfaelle; Todesfallleistung und Freisetzung der
  Garantieverpflichtung getrennt, mit offengelegter Bewertungsbasis.
  Mortalitaet ist ein exogener Risikotreiber, keine VN-Strategie.
- **Neugeschaeft:** neue, eindeutig bezeichnete Kohorten mit eigener
  Stueckzahl, Praemie, Laufzeit und unveraenderlichem Garantiesatz.
  Zinsbeginn und Einzahlungstiming werden festgelegt; keine rueckwirkende
  Gutschrift. Der PR159-Fall bleibt als Null-Neugeschaeft-Praefix erhalten.
- **Individuelle Vertragswerte:** fuer kleine Workshop-Faelle eine
  begrenzte Menge benannter Policen mit unterschiedlichen Laufzeiten,
  Garantien und Leistungen. Kohorten- und Policensummen muessen auf
  denselben Versichererbestand und dieselbe Bilanz abstimmen. Keine
  unbegrenzte Einzelvertrags-Engine fuer einen ganzen Markt.
- **Ablaufleistungen:** eine explizite Leistung darf vom Buchwert der
  Verpflichtung abweichen; Garantieuntergrenze, Freisetzung, Auszahlung
  und Ergebniseffekt werden getrennt und getestet. PR159s Gleichsetzung
  bleibt als Spezialfall erhalten.
- **Kapitalbewegungen:** Einlage und Ausschuettung werden als eigene
  Vermoegens-/Eigenkapitalfluesse mit Bilanzidentitaet gefuehrt.
  Spaetere Spartenaddition darf sie nicht doppelt zaehlen.
- **Anlage und Mortalitaet:** zuerst deterministische, versionierte
  Szenariokurven und einfache VU-Anlageregeln mit Periodenfenstern und
  festen Parametern. Expliziter Anlagefluss und berechneter Anlagefluss
  sind alternative Modi, nie kumulativ. Keine historische RNG-Nachbildung.
- **Rueckkauf/Bonus:** fuer diese Workshop-Stufe bewusst ausgeschlossen.
  Auch eine automatische Storno- oder VN-Rueckkaufstrategie wird nicht
  verdeckt eingefuehrt.

## Reviewbare PR-Folge

| PR | Liefergegenstand | Abnahme |
| --- | --- | --- |
| PR160 | Lebensfluss- und Bewertungsvertrag v3 | umgesetzt: Zeitpunkte und Quellen fuer Tod, Neugeschaeft, Ablauf, Kapital, individuelle Werte und Garantieuntergrenze explizit; PR159-v2 bleibt gueltig |
| PR161 | Tod und Kapitalbewegungen im geschlossenen Bestand | umgesetzt: feste Positiv-/Negativfaelle, getrennte Leistung/Freisetzung, stabile Prefixe, keine Bilanzluecke oder Teilresultate |
| PR162 | Neugeschaeft mit Kohorten und Ausgabeparametern | umgesetzt: neue Kohorten tragen erst in der Folgeperiode Garantie; Bestand und Verpflichtung je Kohorte stimmen zum Gesamtwert, PR161-Spezialfall stabil |
| PR163 | Begrenzte Policenwerte und variable Ablaufleistung | umgesetzt: hoechstens 100 vollstaendig enumerierte Policen, individuelle Gutschrift, explizite Ablaufleistung und atomare Abstimmung; kein Runner/UI |
| PR164 | Deterministische Anlage- und Mortalitaetsannahmen | umgesetzt: lueckenlose Fenster, exklusive Quellenmodi, VU-Anlagewert und Todesfall-IDs je Kohorte; reine Aufloesung ohne Runner |
| PR165 | Kontrollierter Lebensanschluss an die Periodenkette | umgesetzt: bis 100 Perioden, PR164-Quellen aus geprueftem Carryover, PR163-Prefixrechnung und atomarer Abbruch; Nichtleben-Pfad unveraendert |
| PR166 | Lebens-Ergebnis-API, Ablage und XLSX | umgesetzt: kontrollierte Idempotenz, Herkunft/Digest, lesbarer Verlauf und gleiche Dezimalwerte in JSON und XLSX; 20-Sekunden-API-Budget |
| PR167 | Gefuehrte Lebens-Workbench fuer Seminar/Strategieworkshop | umgesetzt: drei kuratierte Zwei-Perioden-Presets, beschriftete Fluesse, Baseline/Variante, Bestands-/Leistungs-/Bilanz-Zeitreihen und breite/schmale Browserabnahme; neue statische Bilder offen |

## UI-Bedienweg fuer PR167

Der Anwender waehlt einen Versicherer und einen einfachen Ausgangsfall.
Im PR167-Pfad sieht er anfaengliche Policen, Bilanz,
Garantiesatz und Laufzeit, kann diese Ausgangswerte aber noch nicht frei
umstellen. Er aendert sichtbare Stellhebel: Neugeschaeft, Todesfallannahme,
Anlagerendite/-strategie und Kapitalzufuhr oder -ausschuettung. Eine
Variante wird gegen die unveraenderte Baseline gestellt. Die Ansicht
zeigt je Periode aktive Policen, neue und beendete Vertraege,
Praemien, Garantiegutschrift, Todes- und Ablaufleistungen, Aktiva,
Verpflichtung, Eigenkapital sowie die Herkunft jeder Zahl. Technische
Schemafelder und Roh-JSON sind nicht der normale Bedienweg. Rohwerte
und Annahmen bleiben fuer Experten im Export nachvollziehbar.

## Herkunft und Grenzen

Die C-Positionen in `IMSDATA.C` und die Reserveoperationen in `IMS.E`
belegen kein historisches Lebensversicherungsmodell. Alle neuen
Bewertungs- und Strategieentscheidungen sind als IMS-2.x-Annahmen zu
versionieren. Keine gesetzliche Bilanz, Solvency-II-Freigabe oder
historische Vollgleichheit. Das Lebenssegment wird erst nach PR167 und
dem separaten Kranken-Schnitt in PR170 zur Vier-Sparten-Gesamtbilanz
addiert; der heutige Zwei-Sparten-Export bleibt bis dahin unveraendert.
