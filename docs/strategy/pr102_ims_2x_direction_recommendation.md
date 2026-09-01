# Entscheidungsvorlage: PR102 und Zielbild IMS 2.x

Stand: 2026-09-01
Status: Empfehlung vorbereitet, noch nicht beschlossen
Planungswirkung: nicht in die aktive PR-Restplanung uebernommen

## Kurzempfehlung

PR102 soll den historischen 6.300-Zeilen-Vergleich als vollstaendig
angeschlossenen, diagnostischen Legacy-Benchmark abschliessen. Er soll nicht
versuchen, 35 Jahre alte, von damaligen `rnd()`-Implementierungen,
Bibliotheken, Compilern und teilweise unterschiedlichen Parametern gepraegte
Zahlenfolgen exakt zu reproduzieren.

Die empfohlene Entscheidung lautet:

1. Die historische Referenzsammlung bleibt als Herkunfts-, Format-,
   Plausibilitaets- und Regressionsnachweis erhalten.
2. Exakte historische Zufallsfolgen sind kein Produktziel von IMS 2.x.
3. Abweichungen werden nur dann zu Fachlogik-Arbeit, wenn sie ein belegtes
   fachliches Invariant, eine deterministische moderne Wiederholung oder eine
   erwartete Wirkungsrichtung verletzen.
4. Die heutige Produktionsfreigabe wird durch PR102 nicht automatisch
   erteilt. Stattdessen wird der alte Gleichheitsblocker durch einen neuen,
   anwendungsbezogenen Validierungsauftrag fuer IMS 2.x abgeloest.
5. IMS 2.x wird als gemeinsame, erweiterbare Plattform entwickelt, nicht als
   Sammlung voneinander abweichender Spezialprogramme.

## Vorgeschlagener Beschluss

Der historische IMS-Korpus ist mit 15/15 Tabellen und 6.300/6.300
Ergebniszeilen strukturell vollstaendig an den modernen Diagnosepfad
angeschlossen. Die historischen Referenzen stammen aus mehreren Lauf- und
Archivschichten; identische Parameter, Zinssaetze, Compiler- und RNG-Folgen
sind nicht belegt. Exakte Feldgleichheit wird daher nicht als notwendiges
Qualitaetskriterium fuer IMS 2.x festgelegt.

Die Referenzen werden als diagnostischer Legacy-Benchmark akzeptiert. Offene
Feldbedeutungen und fachliche Invarianten bleiben nachvollziehbar registriert.
IMS 2.x wird stattdessen gegen moderne, reproduzierbare Laufvertraege, reale
Marktkennzahlen, statistische Kalibrierungsziele, erklaerbare
Szenariowirkungen und versionierte Annahmen validiert. Dieser Beschluss ist
noch keine fachliche Produktionsfreigabe eines konkreten IMS-2.x-Produkts.

## Was PR102 feststellen soll

PR102 soll vier Aussagen getrennt ausweisen:

| Achse | Empfohlener Befund |
| --- | --- |
| Korpuslieferung | `complete`: 15/15 Tabellen und 6.300/6.300 Zeilen sind angeschlossen |
| Historische Reproduktion | `not_a_product_target`: exakte historische RNG- und Feldfolgen werden nicht verlangt |
| Legacy-Verwendung | `accepted_diagnostic_benchmark`: Referenzen bleiben fuer Herkunft, Form, Plausibilitaet und Regression erhalten |
| IMS-2.x-Freigabe | `modern_validation_program_required`: Freigabe folgt erst aus anwendungsbezogener moderner Validierung |

`production_release_approved` bleibt in PR102 `false`. Das verhindert eine
stille Umdeutung von vollstaendiger Vergleichsabdeckung in Produktreife. Der
bisherige Status `blocked_calculated_core_validation` darf aber fachlich neu
eingeordnet werden: Nicht die fehlende Rekonstruktion alter Zufallszahlen ist
der naechste Arbeitsauftrag, sondern der Aufbau passender moderner
Validierungsgates.

## Behandlung der Abweichungen

### Weiter verfolgen

- verletzte Bilanz-, Mengen-, Bestands- oder Aggregatinvarianten;
- nicht reproduzierbare Ergebnisse bei identischem modernem Run-Manifest;
- unerwartete Vorzeichen oder Wirkungsrichtungen bei kontrollierten
  Parameter- und Regulierungsaenderungen;
- unstabile Scheduler-, Carryover- oder Zustandsuebergaenge;
- Parser-, Header-, Feldbreiten-, Perioden- oder Selektorfehler;
- Abweichungen, die durch einen belegten gemeinsamen historischen Lauf und
  identische Eingaben erklaerungsbeduerftig werden.

### Dokumentieren, aber nicht nachbauen

- Differenzen ohne belegte historische Parameter- und Laufidentitaet;
- andere Zufallsfolgen aus alten oder plattformabhaengigen `rnd()`-
  Implementierungen;
- Unterschiede durch GNU-C-, MS-DOS-, Linux- oder Solaris-Laufzeitumgebungen,
  sofern kein fachliches Invariant verletzt wird;
- historische Einzelwerte, deren statistische oder fachliche Bedeutung nicht
  aus Begleitdaten rekonstruiert werden kann;
- blosse Vollzeilen- oder Vollfeldabweichungen in stochastischen Trajektorien.

Diese Grenze spart nicht an Qualitaet. Sie verlagert Qualitaet von einer kaum
belegbaren Byte- und Zufallsfolgengleichheit auf fachlich aussagekraeftige,
reproduzierbare Kriterien.

## Zielbild IMS 2.x

Empfohlen wird eine gemeinsame Produktidee mit dem Arbeitstitel
**IMS 2.x Insurance Market Simulation Lab**. Sie verbindet mehrere
Anwendungsrichtungen auf demselben Simulationskern, demselben Szenarioformat
und derselben Ergebnis- und Provenienzschicht.

### 1. Kalibrierte Marktrekonstruktion

Die Formulierung "Reproduktion realer Marktzahlen" sollte als kalibrierte
Marktrekonstruktion und Backtesting verstanden werden, nicht als Nachspielen
einer einzelnen Zufallsfolge.

Der Modus soll:

- reale aggregierte Marktkennzahlen versioniert einlesen;
- Parameter gegen beobachtbare Zielgroessen kalibrieren;
- Niveau, Verteilung, Dynamik, Konzentration und Stabilitaet vergleichen;
- Unsicherheit und mehrere passende Parametersaetze sichtbar machen;
- Datenjahr, Quelle, Transformation und Modellversion ausweisen.

Dieser Modus ist die Glaubwuerdigkeitsbasis der gesamten Plattform. Er muss
schmal beginnen: wenige belastbare Kennzahlen und ein klar begrenztes
Marktsegment sind besser als eine scheinbar vollstaendige, unbelegte
Marktreplikation.

### 2. Regulationslabor als erstes Aushaengeschild

Die Wirkungsanalyse von Regulierungen wird als erster oeffentlich sichtbarer
Flagship-Modus empfohlen. Sie zeigt die besondere Kompetenz von IMS, weil sie
Marktstruktur, Versicherer, Vermittler, Verhalten, Zeit und aggregierte
Wirkungen zusammenfuehrt.

Der Modus soll:

- eine kalibrierte Baseline und eine Regulierung als getrennte Versionen
  vergleichen;
- direkte und indirekte Wirkungen zeitlich darstellen;
- Gewinner, Verlierer, Konzentration, Versorgung und Stabilitaet zeigen;
- Annahmen, Regelversion und Unsicherheitsband offenlegen;
- Ergebnisse als reproduzierbares Wirkungsdossier exportieren.

Die Staerke liegt nicht in einer scheinbar exakten Prognose, sondern in einer
transparenten, wiederholbaren Gegenfaktualanalyse.

### 3. Management-Simulation

Die Management-Simulation verwendet denselben Baseline- und Vergleichsmotor
fuer strategische Entscheidungen, etwa Produkt-, Vertriebs-, Kosten-, Risiko-
oder Informationsstrategien.

Sie soll:

- wenige klar benannte Stellhebel statt freier Modellparameter anbieten;
- Baseline, Strategie A und Strategie B gemeinsam vergleichen;
- Zielkonflikte und Verteilungseffekte statt nur eines Endwerts zeigen;
- mehrere Seeds oder Szenarien als Band, nicht als scheinbar sichere Zahl
  darstellen;
- Entscheidungen und Annahmen in einem Run-Manifest festhalten.

Dieser Modus ist besonders fuer Workshops, Lehre und strategische Diskussion
geeignet. Er darf nicht zu einem Spiel mit unerklaerten Reglern werden.

### 4. Forschungs- und Publikationsmodus

Ein vierter Modus macht Modellkompetenz nach aussen pruefbar:

- kuratierte, read-only Beispielszenarien;
- Methoden- und Modellkarten;
- reproduzierbare Experimentserien;
- Sensitivitaets- und Robustheitsanalysen;
- zitierbare Versionen von Daten, Annahmen, Modell und Ergebnis;
- Exporte fuer Tabellen, Grafiken und Publikationsanhaenge.

Er bildet die Bruecke zu Wissenschaft, Lehre, Vortraegen und einer
oeffentlichen Demonstration, ohne interne Arbeitsdaten offenzulegen.

## Warum keine vier getrennten Produkte

Alle Richtungen benoetigen dieselben Grundbausteine:

- versionierte Markt- und Szenariodaten;
- einen deterministischen modernen Simulationsvertrag;
- explizite Seeds und Run-Manifeste;
- Kalibrierungs-, Vergleichs- und Unsicherheitsmetriken;
- Regel- und Strategievarianten;
- Ergebnisprovenienz und Export;
- eine gemeinsame, rollenbewusste Workbench.

Getrennte Implementierungen wuerden Fachlogik, Datenvertraege und UI
verdoppeln. Empfohlen werden stattdessen schmale, versionierte Schnittstellen
fuer Datenquellen, Regelpakete, Strategien und Auswertungen. Ein allgemeines
Plugin-Framework wird erst eingefuehrt, wenn mindestens zwei reale Adapter
denselben Erweiterungspunkt belegen.

## Nach aussen sichtbare Kompetenz

IMS 2.x sollte Kompetenz durch Nachvollziehbarkeit zeigen, nicht durch
Marketingbehauptungen. Jeder sichtbare Ergebnisstand soll beantworten:

1. Welche Marktfrage wird untersucht?
2. Welche Daten und Annahmen bilden die Baseline?
3. Welche Intervention oder Strategie wurde geaendert?
4. Welche Wirkungsmechanismen im Modell sind beteiligt?
5. Wie robust ist das Ergebnis ueber Seeds und Parametersaetze?
6. Welche Grenzen und offenen Fragen bleiben?
7. Mit welcher Modell-, Daten- und Regelversion ist der Lauf reproduzierbar?

Besonders wirksam fuer die Aussendarstellung sind ein versioniertes
Run-Manifest, sichtbare Datenprovenienz, Sensitivitaetsbaender, eine knappe
Methodenkarte und ein exportierbares Ergebnisdossier. Diese Elemente zeigen
Versicherungsmarkt- und Simulationskompetenz besser als ein einzelner hoher
historischer Feldtrefferwert.

## UI-Empfehlung

Die bestehende Workbench soll zum eigentlichen Arbeitsinstrument ausgebaut
werden, nicht durch eine separate Marketingseite ersetzt werden. Empfohlen
wird eine ruhige, professionelle Oberflaeche mit vier eng verbundenen
Arbeitsansichten:

| Ansicht | Primaere Aufgabe |
| --- | --- |
| Marktbild | Baseline, Datenjahr, Kalibrierungsstatus und zentrale Marktkennzahlen lesen |
| Szenarien | Regulierung oder Managementstrategie waehlen, Annahmen vergleichen und Run vorbereiten |
| Wirkung | Baseline und Varianten ueber Zeit, Verteilung und Akteursgruppen vergleichen |
| Nachweis | Run-Manifest, Datenquellen, Modellversion, Unsicherheit und Export pruefen |

Fuer eine hochwertige Wirkung nach aussen braucht die UI:

- echte Ergebnisgrafiken statt dekorativer Visualisierung;
- direkte Baseline-gegen-Szenario-Vergleiche;
- kleine Multiples fuer Akteursgruppen und Zeitfenster;
- Unsicherheitsbaender und Sensitivitaetsansichten;
- klar erkennbare Statuswerte fuer kalibriert, experimentell und freigegeben;
- kuratierte Showcase-Szenarien in einem read-only Modus;
- konsistente Typografie, Farben und Abstaende ohne uebergrosse
  Marketingflaechen;
- gute Desktop-Nutzung und eine lesbare, reduzierte Tablet-Ansicht.

"Schick" bedeutet hier: fachliche Dichte, klare Hierarchie, schnelle
Vergleichbarkeit und sichtbare Sorgfalt. Die Oberflaeche soll wie ein modernes
wissenschaftliches Entscheidungswerkzeug wirken.

## Moderne Validierungsgates

Nach PR102 soll ein spaeterer IMS-2.x-Plan folgende Gates getrennt vorsehen:

| Gate | Kernfrage |
| --- | --- |
| Determinismus | Erzeugt dasselbe moderne Run-Manifest dieselben Ergebnisse? |
| Fachliche Invarianten | Bleiben Bilanzen, Mengen, Bestandsgrenzen und Aggregationen konsistent? |
| Kalibrierung | Trifft das Modell vereinbarte reale Zielgroessen und Verteilungen innerhalb dokumentierter Guetegrenzen? |
| Sensitivitaet | Reagiert das Modell in erwarteter Richtung und nachvollziehbarer Groessenordnung? |
| Gegenfaktual | Ist die Differenz zwischen Baseline und Intervention reproduzierbar und erklaerbar? |
| Robustheit | Bleiben Kernaussagen ueber Seeds und plausible Parametersaetze stabil? |
| Betrieb und UI | Sind Start, Run, Ergebnis, Export, Backup und Fehlerpfade kontrolliert? |

Exakte Werte bleiben fuer deterministische Formeln, Vertraege und Invarianten
wichtig. Fuer stochastische Markttrajektorien werden Verteilungen, Quantile,
Wirkungsrichtungen, Effektgroessen und Robustheit bewertet.

## Empfohlene Reihenfolge nach einer Entscheidung

Diese Reihenfolge ist eine Kandidatenfolge, keine aktive PR-Roadmap:

1. PR102 schliesst die Legacy-Bewertung mit der oben beschriebenen Trennung.
2. Ein IMS-2.x-Validierungscharter legt moderne Gates und erste Zielgruppe
   fest.
3. Ein schmaler realer Daten- und Kalibrierungsvertrag erzeugt eine belastbare
   Marktbaseline.
4. Ein gemeinsamer Baseline-gegen-Szenario-Vergleich wird technisch und
   fachlich abgesichert.
5. Das Regulationslabor liefert den ersten kuratierten End-to-End-Fall.
6. Die Wirkungsansicht und das reproduzierbare Ergebnisdossier machen diesen
   Fall praesentationsfaehig.
7. Management-Stellhebel verwenden denselben Szenario- und Vergleichsmotor.
8. Forschungs-, Publikations- und read-only Showcase-Modi konsolidieren die
   Aussendarstellung.

Erst nach der Richtungsentscheidung werden daraus kleine, reviewbare PRs mit
Umfangsschaetzung und Abnahmekriterien gebildet.

## Nicht-Ziele dieser Empfehlung

- keine Aenderung der Fachlogik;
- keine Simulation oder Runnerausfuehrung;
- keine Neubewertung einzelner 6.300 Referenzzeilen;
- keine historische RNG- oder Vollgleichheitsbehauptung;
- keine automatische Produktionsfreigabe;
- keine Festlegung konkreter realer Datenquellen oder Lizenzen;
- keine Aufnahme der Kandidatenfolge in die aktive Rest-PR-Planung.
