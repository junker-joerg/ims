# Roadmap: IMS 2.x Mehrsparten- und Regulationslabor

Stand: 2026-09-14
Status: aktive Produkt-Restplanung; PR145 umgesetzt, PR146 naechster Schritt
Beschlussgrundlage: angenommene IMS-2.x-Richtung aus PR102 und
Managemententscheidung vom 2026-09-14

## Entscheidung

IMS 2.x wird zu einem gut bedienbaren Versicherungsmarkt-Simulationslabor
ausgebaut. Die verbindliche Entwicklungsrichtung umfasst:

1. einen kontrollierten und auswertbaren Lauf ueber 100 Perioden;
2. benannte Sparten mit zunaechst Kfz, Sach-Haftpflicht, Leben und Kranken;
3. eine einfache Bewegungsrechnung und Modellbilanz je Versicherer sowie eine
   konsolidierte Sicht;
4. eine erklaerbare Solvency-II-Kapitalansicht mit klar ausgewiesenem
   Modellierungsgrad;
5. DORA-bezogene operative Wirkungsketten vom ICT-Ereignis bis zu
   Markt-, Bilanz- und Kapitalfolgen;
6. eine nichttechnische, visuelle Bedienung fuer Forschung, Lehre und
   Managementseminare.

Die Punkte waren bisher teilweise als Zielbild oder Paketgrenze vorhanden.
Sie waren aber nicht gemeinsam, nummeriert und mit einem lieferbaren
Bedienpfad geplant. Dieses Dokument schliesst diese Luecke und ersetzt keine
der fachlichen Einzelentscheidungen, die in den jeweiligen PRs noch belegt
werden muessen.

## Fachliche und regulatorische Grenze

Die historischen zwei anonymen Schadenversicherungsvektoren werden nicht
stillschweigend in heutige Sparten umbenannt. PR152 und PR153 muessen ihre
belegte Bedeutung, das Kompatibilitaetsmapping und verbleibende Unsicherheiten
explizit festhalten.

Die Solvency-II-Sicht beginnt als vereinfachte, lehr- und
managementtaugliche Modellrechnung. Sie darf erst dann als regulatorisch
belastbare Berechnung bezeichnet werden, wenn Umfang, Daten, Formeln,
Korrelationen und Versionen separat validiert wurden. Orientierung geben die
offiziellen EIOPA-Regelwerksseiten zur
[SCR-Standardformel](https://www.eiopa.europa.eu/rulebook/solvency-ii-single-rulebook/article-2411_en)
und zum
[MCR](https://www.eiopa.europa.eu/rulebook/solvency-ii-single-rulebook/article-5908_en),
abgerufen am 2026-09-14.

Die DORA-Schicht simuliert operative Wirkungsketten. Sie ist kein
Compliance-Score, kein Audit und keine Rechtsberatung. Der Zuschnitt folgt
den Themen ICT-Risikomanagement, Vorfaelle, Resilienztests und
Drittparteienrisiken aus der
[Verordnung (EU) 2022/2554](https://eur-lex.europa.eu/eli/reg/2022/2554/oj),
abgerufen am 2026-09-14.

## Gemeinsamer Bedienpfad

Alle Ausbaustufen sollen denselben einfachen Arbeitsablauf verwenden:

1. **Marktbild:** Ausgangslage, Datenstand und Modellgrenzen lesen.
2. **Szenario:** Schock, Regulierung oder Managemententscheidung waehlen.
3. **Strategien:** Verhalten von Versicherern und Vermittlern nach Gruppen
   oder Sparten zuordnen.
4. **Wirkung:** Baseline und Variante ueber Zeit, Unternehmen, Sparten und
   Kennzahlen vergleichen.
5. **Nachweis:** Annahmen, Versionen, Pruefsummen, Unsicherheit und Exporte
   nachvollziehen.

Ein gefuehrter Modus bietet wenige verstaendliche Stellhebel. Ein spaeterer
Expertenmodus darf mehr Parameter zeigen, muss aber dieselbe versionierte
Ausfuehrungs- und Nachweisschicht verwenden.

## Phase A: Bedienbarer 100-Perioden-Lauf

Ziel: Die heute kontrollierte Zwei-Perioden-Wirkungsprobe wird ohne Sprung in
einen freien oder unbegrenzten Runner schrittweise zu einem auswertbaren
100-Perioden-Lauf erweitert.

| PR | Kleiner, reviewbarer Liefergegenstand | Zentrale Abnahme |
| --- | --- | --- |
| PR142 | Vertrag fuer einen auf fuenf Perioden begrenzten Kettenrunner | Prefix 1-2 bleibt exakt stabil; Grenzen und Fehler sind explizit |
| PR143 | Kanonischer Bau und Validierung einer Fuenf-Perioden-Kette | lueckenlose Kontexte, Carryover und Gesamtdigest werden atomar geprueft |
| PR144 | Isolierte Fuenf-Perioden-Wirkungsprobe | umgesetzt: deterministische Wiederholung, unveraenderte Kandidaten und bytegleicher Prefix 1-2 |
| PR145 | Kontrollierter Start, Idempotenz und Ergebnisablage fuer fuenf Perioden | umgesetzt: erneuter Start liefert ohne Runner dasselbe gespeicherte Ergebnis |
| PR146 | Workbench- und Browserabnahme fuer fuenf Perioden | breiter und schmaler Viewport, Fehlerpfade und Handbuchbild |
| PR147 | Horizontvertrag fuer 10, 25, 50 und 100 Perioden | Laufzeit-, Abbruch-, Ressourcen- und Fehlergrenzen vor Ausfuehrung festgelegt |
| PR148 | Kontrollierte Ausfuehrung fuer 10, 25 und 50 Perioden | stabile Prefixe, Carryover-Invarianten und deterministischer Replay |
| PR149 | Kontrollierte Ausfuehrung fuer 100 Perioden | vollstaendiger reproduzierbarer Lauf, Abbruch und atomarer Fehlerpfad |
| PR150 | Versioniertes Ergebnisbuendel mit CSV, JSON und XLSX | gleiche Kennzahlen und Herkunft in allen Exportformaten |
| PR151 | Ergebnisarbeitsplatz mit Zeitreihen und Vergleichen | Baseline/Variante, Unternehmen, Sparten und Perioden im Browser lesbar |

Nach PR149 ist der technische 100-Perioden-Lauf vorhanden. Nach PR151 ist er
fuer einen Anwender mit sichtbaren Ergebnissen und Exporten sinnvoll nutzbar.

## Phase B: Mehrsparten und Versichererbilanz

Ziel: Das Modell wird von zwei historisch geerbten Schadenvektoren zu einer
erweiterbaren, benannten Spartenstruktur entwickelt. Leben und Kranken werden
als eigene, schmale Modellsegmente eingefuehrt und nicht als Varianten der
Schadenlogik ausgegeben.

| PR | Kleiner, reviewbarer Liefergegenstand | Zentrale Abnahme |
| --- | --- | --- |
| PR152 | Versionierte Spartentaxonomie und Erweiterungsvertrag | Kfz, Sach-Haftpflicht, Leben und Kranken sind fachlich getrennt benannt |
| PR153 | Kompatibilitaetsadapter fuer die zwei vorhandenen Schadenvektoren | Altpfad bleibt reproduzierbar; Mapping und Unsicherheit sind sichtbar |
| PR154 | Strategie- und Parameterzuordnung je Sparte | unterschiedliche Strategien je Versicherer und Sparte sind validierbar |
| PR155 | Vertrag fuer Bewegungsrechnung und einfache Modellbilanz | Bestands-, Erfolgs-, Zahlungs- und Kapitalbewegungen sind explizit |
| PR156 | Modellbilanz fuer Kfz und Sach-Haftpflicht | Bilanzidentitaeten und Periodenuebergaenge sind getestet |
| PR157 | Konsolidierte Versichererbilanz in Workbench und XLSX | Einzelsparten und Gesamtunternehmen sind abstimmbar |
| PR158 | Zustands-, Fluss- und Strategievertrag fuer Leben | garantienahe Verpflichtungen, Laufzeit und Ergebnisquellen sind begrenzt |
| PR159 | Minimale deterministische Lebensparte | feste Falltests und Bilanzanschluss ohne Vollmodellbehauptung |
| PR160 | Zustands-, Fluss- und Strategievertrag fuer Kranken | Beitrags-, Leistungs- und Bestandslogik sind begrenzt und getrennt |
| PR161 | Minimale deterministische Krankensparte | feste Falltests und Bilanzanschluss ohne Vollmodellbehauptung |
| PR162 | Spartenuebergreifende Konsolidierung | vier Modellsegmente stimmen je Versicherer zur Gesamtbilanz ab |

Die erste Mehrspartenstufe deckt damit vier fuer das Zielbild wichtige
Segmente ab. Sie behauptet weder die vollstaendige deutsche
Versicherungszweigsystematik noch eine aufsichtsrechtliche Rechnungslegung.

## Phase C: Solvency-II-Kapitalansicht

Ziel: Kapitalwirkungen werden als nachvollziehbare Modellgroessen sichtbar.
Die erste Stufe soll Entscheidungen und Wirkungsrichtungen erklaeren, nicht
eine Meldesoftware ersetzen.

| PR | Kleiner, reviewbarer Liefergegenstand | Zentrale Abnahme |
| --- | --- | --- |
| PR163 | Scope-, Terminologie-, Quellen- und Versionsvertrag | Modellrechnung und regulatorisch validierte Aussage bleiben klar getrennt |
| PR164 | Solvenzmodellbilanz und vereinfachte Eigenmittelabbildung | Herkunft jeder Kapitalgroesse ist zur Versichererbilanz rueckverfolgbar |
| PR165 | Risikotreiber und Szenarioschock-Mapping | jeder Schock veraendert nur explizit zugeordnete Exposures |
| PR166 | Ausgewaehlte Markt- und versicherungstechnische Risikomodule | Schaden, Leben und Kranken besitzen getestete, begrenzte Module |
| PR167 | Gegenpartei-, operationelles Risiko und Aggregation | Korrelationen und verlustabsorbierende Effekte sind versioniert |
| PR168 | SCR, MCR, Bedeckungsquote und Managementschwellen | Kennzahlen sind reproduzierbar und fachlich beschriftet |
| PR169 | Feste Faelle, Sensitivitaeten und Invarianten | Richtung, Monotonie, Grenzwerte und Bilanzanschluss sind geprueft |
| PR170 | Kapitalansicht und Export | Unternehmen, Sparte, Treiber und Unsicherheit sind sichtbar; kein Filing-Anspruch |

Falls PR166 oder PR167 bei der Quellenklaerung zu gross werden, werden sie in
weitere kleine Fach-PRs geteilt. Die Meilensteinzahl erhoeht sich dann, statt
unterschiedliche Risikomodule in einem Sammel-PR zu verstecken.

## Phase D: DORA-Wirkungsketten

Ziel: Ein operatives Ereignis wird von der technischen Stoerung ueber
Geschaeftsprozesse bis zu Kunden-, Markt-, Bilanz- und Kapitalwirkungen
verfolgbar.

| PR | Kleiner, reviewbarer Liefergegenstand | Zentrale Abnahme |
| --- | --- | --- |
| PR171 | Vertrag fuer wichtige Geschaeftsservices, ICT-Assets, Anbieter und Abhaengigkeiten | gerichtete Herkunft und Verantwortungsgrenzen sind explizit |
| PR172 | Ereignis- und Interventionsvertrag | Ausfall, Kapazitaetsverlust, Datenintegritaet und Anbieterausfall sind getrennt |
| PR173 | Adapter von Stunden und Tagen auf IMS-Perioden | keine stille Vermischung operativer und marktlicher Zeitskalen |
| PR174 | Wirkung auf Vertrieb, Underwriting, Schaden und Service | Kapazitaet, Rueckstand und Erholung sind als Kette nachvollziehbar |
| PR175 | Drittparteienkonzentration und korrelierter Ausfall | gemeinsame Anbieter koennen mehrere Versicherer kontrolliert treffen |
| PR176 | Praeventions-, Wiederanlauf- und Fallback-Strategien | Kosten, Wirksamkeit und Restlaufzeit sind parametrierbar |
| PR177 | Anschluss an Bilanz und Kapital | operative Folgen schlagen nachvollziehbar auf Ergebnis und Bedeckung durch |
| PR178 | DORA-Wirkungsansicht und Dossier | Zeitlinie, Abhaengigkeiten, Engpaesse und Unsicherheit sind exportierbar |

Nicht vorgesehen sind ein automatisches DORA-Compliance-Urteil, eine
Rechtsauslegung oder der Ersatz einer operativen Resilienzpruefung.

## Phase E: Managementbedienung und Seminarfreigabe

Ziel: Die Fachlogik wird als ruhiges Entscheidungswerkzeug bedienbar, ohne
dass Anwender interne Datenvertraege oder Quellcode kennen muessen.

| PR | Kleiner, reviewbarer Liefergegenstand | Zentrale Abnahme |
| --- | --- | --- |
| PR179 | Gefuehrter Szenarioassistent mit optionalem Expertenmodus | Frage, Baseline, Schock, Strategien und Ergebnisziel bilden einen Ablauf |
| PR180 | Kuratierte Seminarfaelle | Schadeninflation, Preiswettbewerb, Kapitaldruck und ICT-Ausfall sind reproduzierbar |
| PR181 | Moderationspaket und portable Szenariobuendel | Arbeitsblaetter, Import/Export und read-only Demonstration sind geprueft |
| PR182 | End-to-End-Abnahme des Managementseminars | Installation, 100 Perioden, Mehrsparten, Bilanz, Kapital, DORA-Fall und Export funktionieren gemeinsam |

PR182 bezeichnet eine kontrollierte Seminar- und Demonstrationsreife. Eine
fachliche Produktionsfreigabe fuer Beratung, Aufsicht oder einzelne
Unternehmensentscheidungen benoetigt weiterhin einen benannten Datenstand,
einen konkreten Anwendungsfall und dessen eigene Validierung.

## Meilensteine und Restzahl

| Meilenstein | Erreicht nach | PRs ab PR142 | verbleibend nach PR145 |
| --- | ---: | ---: | ---: |
| technischer 100-Perioden-Lauf | PR149 | 8 | 4 |
| bedienbarer 100-Perioden-Lauf mit Ergebnis und Export | PR151 | 10 | 6 |
| vier Modellsegmente und konsolidierte Versichererbilanz | PR162 | 21 | 17 |
| erklaerbare Solvency-II-Kapitalansicht | PR170 | 29 | 25 |
| durchgaengige DORA-Wirkungskette | PR178 | 37 | 33 |
| kontrollierte Managementseminar-Reife | PR182 | 41 | 37 |

Die 41 PRs sind eine Planungsbasis, keine Terminzusage. Realistisch ist eine
Unsicherheit von etwa acht zusaetzlichen PRs, insbesondere bei Leben,
Kranken, Risikomodulen und regulatorischer Quellenvalidierung. Erkenntnisse
werden durch Teilung sichtbar gemacht; sie werden nicht in groessere PRs
gedrueckt.

## Grober Umfang

| Phase | Geschaetzter Umfang einschliesslich Tests und Doku |
| --- | ---: |
| 100 Perioden und Ergebnisarbeitsplatz | 3.000-5.500 LoC |
| Mehrsparten und Bilanz | 3.500-6.500 LoC |
| Solvency-II-Kapitalansicht | 3.000-5.500 LoC |
| DORA-Wirkungsketten | 3.000-5.000 LoC |
| Managementbedienung und Seminarfreigabe | 1.200-2.500 LoC |
| **Gesamt** | **13.700-25.000 LoC** |

Die Schaetzung umfasst produktiven Code, Tests und Dokumentation. Sie ist
bewusst breit und wird an jedem Phasenende anhand des tatsaechlichen Bestands
neu bestimmt.

## Durchgaengende Tests

Jeder Fach-PR muss die zum Risiko passende Teilmenge dieser Nachweise liefern:

- deterministische Wiederholung mit explizitem Seed und Run-Manifest;
- stabile Prefixe bei verlaengerten Periodenketten;
- Bilanz-, Bestands-, Mengen- und Aggregatinvarianten;
- feste Positiv- und Negativfaelle fuer neue Sparten und Kapitalmodule;
- erwartete Wirkungsrichtung und Sensitivitaet kontrollierter Schocks;
- atomare Fehlerpfade ohne Teilergebnis oder teilweise Speicherung;
- Browserabnahme auf breitem und schmalem Viewport;
- inhaltlich gleiche CSV-, JSON- und XLSX-Exporte;
- sichtbare Quellen-, Versions-, Annahmen- und Unsicherheitsgrenzen.

Der historische 6.300-Zeilen-Korpus bleibt diagnostischer Legacy-Benchmark.
Er ist kein Zwang zur Reproduktion unbelegter alter Zufallsfolgen.

## Handbuchspur

Der nichttechnische Einstieg ist in
`docs/handbook/management_seminar_guide.md` angelegt. Die bestehenden
Installations- und technischen Bedienkapitel bleiben Referenz. HB4 bis HB6
liefern weiterhin Linux-Nachweis, iOS/Juno-Entscheidung und konsolidierte
Handbuchabnahme. Die fachlichen Bilder und Bedienwege werden nach den
Meilensteinen PR151, PR162, PR170 und PR178 aktualisiert.

## Naechster Schritt

PR142 hat den engen read-only Vertrag fuer einen auf fuenf Perioden
begrenzten Kettenrunner und die exakte fachliche Prefixprojektion 1-2
festgelegt. PR143 hat die kanonische Fuenf-Perioden-Kette gebaut und atomar
validiert. PR144 fuehrt sie fluechtig auf isolierten Kandidatenkopien aus
und prueft den Prefix 1-2 semantisch und als kanonisches JSON bytegenau.
PR145 hat kontrollierten Serverstart, dauerhafte Idempotenz und eine durch
Gesamtdigest geschuetzte Ablage von Request, kanonischer Kette und Ergebnis
angeschlossen. PR146 bindet diesen Pfad als naechsten Produkt-PR in die
Workbench ein und nimmt breite sowie schmale Browseransicht, Fehlerpfade und
Handbuchbild ab. Der Ausbau ueber fuenf Perioden bleibt bis PR147 gesperrt.

Dieser Planungsschnitt selbst aendert keine Fachlogik, startet keine
Simulation und behauptet keine historische Vollgleichheit.
