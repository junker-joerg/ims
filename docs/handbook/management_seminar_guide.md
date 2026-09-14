# IMS im Managementseminar

Stand: 2026-09-14
Handbuchschnitt: HB3d
Zielgruppe: Fuehrungskraefte, Lehrende und Seminargruppen ohne Kenntnis der
Dissertation oder des Quellcodes

## Wozu IMS dient

IMS ist ein Labor fuer Versicherungsmaerkte. Es zeigt nicht nur, wie sich ein
einzelnes Unternehmen entscheidet, sondern wie viele Versicherer,
Vermittler, Kundenreaktionen und Marktinformationen ueber mehrere Perioden
zusammenwirken.

Im Seminar hilft IMS bei Fragen wie:

- Welche unmittelbaren und mittelbaren Folgen hat ein Schock?
- Reagieren alle Versicherer gleich oder entstehen Gewinner und Verlierer?
- Wann stabilisiert sich der Markt, und welche Anpassung kostet Zeit?
- Welche Strategie wirkt fuer ein Unternehmen sinnvoll, kann aber den Markt
  insgesamt destabilisieren?
- Wie unterscheiden sich Wirkung, Risiko und Kapitalbedarf zwischen Sparten?
- Wie kann ein ICT-Ausfall ueber Prozesse, Kunden und Bilanz bis zum Kapital
  weiterwirken?

IMS liefert keine sichere Zukunftsprognose. Es macht Annahmen, Mechanismen,
Zeitverlaeufe und Zielkonflikte sichtbar, damit eine Gruppe bessere Fragen
stellt und Entscheidungen nachvollziehbar vergleicht.

![Der periodische Marktprozess des IMS](images/ims_market_cycle_diss_2026-09-01.png)

*Abbildung 1: Der Grundgedanke aus der Dissertation. Entscheidungen,
Marktwirkung, neue Informationen und die naechste Periode bilden einen
wiederholten Prozess.*

## Was heute bereits geht

Die heutige Workbench kann:

- den Modell- und Validierungsstand lesbar anzeigen;
- Szenarien und vorhandene Strategien untersuchen;
- Strategiezuordnungen und Parameterentwuerfe pruefen;
- kontrollierte Kandidaten fuer Versicherer und Vermittler bilden;
- eine Ein- oder Zwei-Perioden-Wirkungsprobe ausdruecklich freigeben,
  ausfuehren und unveraenderlich ablegen;
- den Uebergang von Periode 1 nach Periode 2 nachvollziehbar zeigen.

Noch nicht verfuegbar sind:

- ein frei bedienbarer Lauf ueber 100 Perioden;
- ein Ergebnisarbeitsplatz mit Zeitreihen, Vergleichen und XLSX-Export;
- benannte Sparten Kfz, Sach-Haftpflicht, Leben und Kranken;
- Versichererbilanzen und Solvency-II-Kapitalansichten;
- ein DORA-Szenarioeditor mit durchgaengiger Wirkungskette.

Diese Funktionen sind in der aktiven
[Produkt-Roadmap](../plans/ims_2x_all_lines_management_lab_roadmap.md)
in kleinen Schritten geplant. Die Trennung ist wichtig: Der Leitfaden zeigt
den vorgesehenen Nutzen, ohne den heutigen Stand groesser darzustellen, als
er ist.

## Sieben Vorteile im Fuehrungskraefteseminar

1. **Markt statt Einzelrechnung:** Entscheidungen werden zusammen mit
   Wettbewerbern, Vermittlern und Rueckwirkungen betrachtet.
2. **Zeit statt Momentaufnahme:** Anpassungen, Verzoegerungen und Carryover
   werden periodisch sichtbar.
3. **Strategien statt Einheitsverhalten:** Gruppen von Versicherern und
   Vermittlern koennen unterschiedlich reagieren.
4. **Schocks statt statischer Planung:** Eine Gruppe kann direkte,
   veraenderte und mittelbare Wirkungen getrennt diskutieren.
5. **Unternehmen und Markt gemeinsam:** Kuenftige Sparten-, Bilanz- und
   Kapitalansichten verbinden Mikro- und Makroperspektive.
6. **Nachvollziehbarkeit statt Black Box:** Szenario, Annahmen, Version und
   Ergebnis bleiben zusammen; eine Pruefsumme schuetzt den verwendeten Stand.
7. **Gemeinsames Lernen:** Teams koennen vor dem Lauf Hypothesen formulieren,
   Ergebnisse vergleichen und Abweichungen als Erkenntnis nutzen.

## Die drei Arten eines Schocks

Ein Schock ist eine kontrollierte Veraenderung der Ausgangslage oder der
Umwelt des Modells. Fuer die Diskussion helfen drei Blickwinkel:

| Blickwinkel | Einfache Frage | Beispiel |
| --- | --- | --- |
| Aktivierung | Was wird neu ausgeloest? | Ein Schadenereignis oder ein ICT-Ausfall tritt ein. |
| Veraenderung | Welcher bestehende Wert wird anders? | Schadenhoehe, Zinssatz oder Bearbeitungskapazitaet aendert sich. |
| Indirekte Wirkung | Was folgt erst durch Reaktionen anderer? | Preise, Nachfrage, Vermittlerverhalten oder Marktanteile verschieben sich. |

![Drei Schockarten im IMS](images/ims_shock_types_diss_2026-09-01.png)

*Abbildung 2: Ein Schock ist nicht nur ein einzelner geaenderter Wert. Fuer
Managementfragen ist meist die Kette aus direkter und indirekter Wirkung
entscheidend.*

## Ein Seminar in 90 Minuten

| Zeit | Arbeitsschritt | Ergebnis der Gruppe |
| --- | --- | --- |
| 0-10 Minuten | Gemeinsames Marktbild | gleiche Begriffe und eine klare Fragestellung |
| 10-25 Minuten | Schock oder Intervention beschreiben | Baseline, Ausloeser und betroffene Akteure |
| 25-40 Minuten | Wirkungen vorhersagen | schriftliche Hypothesen zu Richtung, Staerke und Zeit |
| 40-55 Minuten | Kontrollierten IMS-Pfad zeigen | sichtbare Eingaben, Freigabe, Lauf und Ergebnis |
| 55-70 Minuten | Unternehmen, Gruppen und Markt vergleichen | Gewinner, Verlierer, Anpassung und Nebenwirkungen |
| 70-85 Minuten | Auf das eigene Unternehmen uebertragen | Handlungsoptionen, Fruehindikatoren und offene Daten |
| 85-90 Minuten | Abschluss | Entscheidung, Annahmen und naechster Testfall |

Fuer den heutigen Stand sollte die Moderation eine vorbereitete
Zwei-Perioden-Wirkungsprobe verwenden. Nach PR151 kann derselbe Ablauf mit
einem 100-Perioden-Lauf, sichtbaren Zeitreihen und Exporten durchgefuehrt
werden.

## Die fuenf Arbeitsansichten

| Ansicht | Was die Gruppe dort klaert |
| --- | --- |
| Dashboard | Ist die Arbeitsumgebung bereit, und welcher Stand wird gezeigt? |
| Szenarien | Welche Ausgangslage und welche Vergleichsfrage verwenden wir? |
| Strategien | Wer folgt wann welcher Regel, und welche Parameter unterscheiden Gruppen? |
| Validierung | Was ist belegt, was nur diagnostisch und was noch offen? |
| Runs | Welcher Versuch wurde wirklich gestartet, und welches Ergebnis gehoert dazu? |

Die sichtbare Navigation soll die Diskussion fuehren. Technische
Vertragsnamen, interne Datenfelder und Entwicklungsbefehle gehoeren nicht in
den Seminarablauf.

![Strategien und kontrollierte Periodenkette](images/windows_strategy_period_chain_effect_probe_pr141_wide_2026-09-14.png)

*Abbildung 3: Die Workbench zeigt den vorbereiteten Zwei-Perioden-Fall,
Freigabe, Ergebnis und Verlauf in einer gemeinsamen Arbeitsansicht.*

## Die heutige Zwei-Perioden-Probe bedienen

1. In **Strategien** den Abschnitt **Periodenkette** oeffnen.
2. Pruefen, dass Periode 1 und 2 sowie der Uebergang dazwischen vollstaendig
   angezeigt werden.
3. Namen und Begruendung der Freigabe eintragen.
4. Die ausdrueckliche Bestaetigung setzen und **Zwei Perioden starten**
   waehlen.
5. Vorher/Nachher-Werte beider Perioden und den Uebergang 1 nach 2 lesen.
6. Das Ergebnis neu laden und pruefen, dass derselbe Versuch erhalten bleibt.

Die angezeigte Pruefsumme ist der Fingerabdruck des vorbereiteten Falls. Sie
hilft festzustellen, ob beim erneuten Laden wirklich derselbe Fall betrachtet
wird. Sie ist kein fachliches Guetesiegel.

![Zwei-Perioden-Pfad auf schmalem Bildschirm](images/windows_strategy_period_chain_effect_probe_pr141_narrow_2026-09-14.png)

*Abbildung 4: Derselbe kontrollierte Pfad bleibt auf einem schmalen
Bildschirm lesbar. Fuer ein Seminar ist ein breiter Bildschirm dennoch
uebersichtlicher.*

## Arbeitsblatt fuer eine Wirkungskette

Vor dem Lauf fuellt jede Gruppe eine Zeile aus. Danach wird nicht nur gefragt,
ob die Zahl richtig geraten wurde, sondern welcher Mechanismus die
Abweichung erklaert.

| Frage | Eintrag der Gruppe |
| --- | --- |
| Was ist der Ausloeser? |  |
| Welche Sparte oder welcher Prozess ist zuerst betroffen? |  |
| Welche Entscheidung aendert ein Versicherer unmittelbar? |  |
| Wie reagieren Wettbewerber, Vermittler oder Kunden? |  |
| Welche Kennzahl sollte zuerst sichtbar reagieren? |  |
| Was erwarten wir fuer Unternehmen, Gruppe und Gesamtmarkt? |  |
| Nach wie vielen Perioden erwarten wir die groesste Wirkung? |  |
| Welche Annahme ist fuer das Ergebnis am unsichersten? |  |
| Welche Managemententscheidung wuerden wir vom Ergebnis abhaengig machen? |  |

## Geeignete Seminarfaelle

Die folgenden Faelle beschreiben die geplante fachliche Richtung. Sie sind
nicht alle im heutigen Stand ausfuehrbar.

### Schadeninflation in Kfz

Eine anhaltende Erhoehung von Reparatur- und Schadenkosten trifft
Versicherer unterschiedlich. Die Gruppe vergleicht Preisreaktion,
Bestandswirkung, Ergebnis, Marktanteil und spaeter Kapitalbedeckung.

### Preiswettbewerb in Sach-Haftpflicht

Ein Teil des Marktes senkt Preise, andere Unternehmen halten Marge oder
reduzieren Wachstum. Die Gruppe untersucht, wann eine einzelwirtschaftlich
plausible Strategie zu Konzentration oder Instabilitaet fuehrt.

### Kapitaldruck ueber mehrere Sparten

Schaden, Leben und Kranken reagieren auf Zins-, Leistungs- oder
Bestandsschocks verschieden. Die Gruppe verfolgt Einzelsparten,
konsolidierte Bilanz, Risikotreiber und Bedeckungsquote.

### ICT-Dienstleister faellt aus

Ein gemeinsamer Anbieter beeintraechtigt Schadenbearbeitung, Vertrieb oder
Kundenservice. Die Gruppe zeichnet die Kette von Kapazitaetsverlust und
Rueckstand ueber Kundenreaktion und Kosten bis zu Bilanz und Kapital nach.
Sie bewertet Wiederanlauf, Fallback und Drittparteienkonzentration, nicht die
rechtliche DORA-Konformitaet.

## Ergebnisse richtig lesen

Bei jeder Auswertung helfen sechs Fragen:

1. **Richtung:** Steigt oder faellt die Kennzahl gegenueber der Baseline?
2. **Groesse:** Ist der Unterschied wirtschaftlich relevant oder nur klein?
3. **Zeit:** Wann beginnt, gipfelt und endet die Wirkung?
4. **Verteilung:** Welche Unternehmen, Gruppen oder Sparten tragen sie?
5. **Robustheit:** Bleibt die Aussage bei anderen plausiblen Annahmen oder
   Zufallsfolgen bestehen?
6. **Grenze:** Welche Daten oder Modellmechanismen fehlen fuer die konkrete
   Entscheidung?

![Historische Aggregationsebenen des IMS](images/diss_figure_5_10_aggregation.png)

*Abbildung 5: Ergebnisse koennen auf unterschiedlichen Ebenen gelesen
werden. Eine Gesamtmarktzahl allein erklaert nicht, welche Gruppe oder
welches Unternehmen die Wirkung traegt.*

## Wann die Gruppe stoppen sollte

Ein Ergebnis darf nicht als Entscheidungsgrundlage ausgegeben werden, wenn:

- die Baseline oder der Schock nicht fachlich beschrieben ist;
- eine benoetigte Sparte oder Wirkungskette im Modell noch fehlt;
- Bilanz- oder Bestandsidentitaeten verletzt sind;
- das Resultat bei identischem modernen Versuch nicht reproduzierbar ist;
- eine regulatorische Modellgroesse mit einer aufsichtsrechtlich validierten
  Meldung verwechselt wird;
- aus historischen Zufallszahlen eine unbelegte Vollgleichheit abgeleitet
  wird.

## Was als Naechstes hinzukommt

Die aktive Roadmap liefert in dieser Reihenfolge:

1. einen bedienbaren 100-Perioden-Lauf mit Diagrammen und CSV-/JSON-/XLSX-
   Export;
2. Kfz, Sach-Haftpflicht, Leben und Kranken mit unterschiedlichen
   Strategien;
3. eine einfache Bilanz je Versicherer und die Konsolidierung ueber Sparten;
4. eine erklaerbare Solvency-II-Kapitalansicht;
5. DORA-Wirkungsketten von ICT-Abhaengigkeiten bis zu Bilanz und Kapital;
6. einen gefuehrten Szenarioassistenten und kuratierte Seminarfaelle.

Die technische Installation und die detaillierten Bediennachweise bleiben in
den uebrigen Kapiteln dieses Handbuchs erhalten. Dieser Leitfaden ist der
fachliche Einstieg fuer Menschen, die IMS anwenden und diskutieren wollen,
nicht seine innere Implementierung studieren muessen.
