# Roadmap: IMS 2.x Mehrsparten- und Regulationslabor

Stand: 2026-09-16
Status: aktive Produkt-Restplanung; PR159 umgesetzt, PR160 Lebensfluss-Vertrag naechster Schritt
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
| PR146 | Workbench- und Browserabnahme fuer fuenf Perioden | umgesetzt: breiter und schmaler Viewport, Fehlerpfade und Handbuchbilder sind belegt |
| PR147 | Horizontvertrag fuer 10, 25, 50 und 100 Perioden | umgesetzt: konkrete Sicherheitsbudgets und fail-closed Abbruch-/Fehlergrenzen; laengere Starts bleiben gesperrt |
| PR148 | Kontrollierte Ausfuehrung fuer 10, 25 und 50 Perioden | umgesetzt: fluechtige isolierte Probe mit stabilen Prefixen, Carryover-Invarianten, deterministischer Wiederholung und durchgesetzten Budgets; Speicherung/UI bleiben gesperrt |
| PR149 | Kontrollierte Ausfuehrung fuer 100 Perioden | umgesetzt: fluechtiger, reproduzierbarer Lauf mit exaktem Prefix, Abbruch und atomarem Fehlerpfad; Speicherung/UI bleiben geschlossen |
| PR150 | Versioniertes Ergebnisbuendel mit CSV, JSON und XLSX | umgesetzt: fluechtiger Download mit gleichen Zeilen und Herkunft; vollstaendiger Nachweis im JSON |
| PR151 | Ergebnisarbeitsplatz mit Zeitreihen und Vergleichen | umgesetzt: vorhandene VU-/VN-Zustandsfelder je Akteur, Vektorposition und Periode; zwei gleich praefixierte Laeufe und Digest-gebundener ZIP-Download |

Nach PR150 sind technischer 100-Perioden-Lauf und fluechtiger Export vorhanden.
Nach PR151 kann der Anwender vorbereitete 100er-Ketten im Browser
ausfuehren, ihre vorhandenen Zustandsfelder lesen und zwei gleich
praefixierte Laeufe vergleichen. Der Aufbau dieser Ketten bleibt eine
Voraussetzung; eine persistierte 100er-Ausfuehrung ist nicht freigegeben.

## Phase B: Mehrsparten und Versichererbilanz

Ziel: Das Modell wird von zwei historisch geerbten Schadenvektoren zu einer
erweiterbaren, benannten Spartenstruktur entwickelt. Leben und Kranken werden
als eigene, schmale Modellsegmente eingefuehrt und nicht als Varianten der
Schadenlogik ausgegeben.

| PR | Kleiner, reviewbarer Liefergegenstand | Zentrale Abnahme |
| --- | --- | --- |
| PR152 | Versionierte Spartentaxonomie und Erweiterungsvertrag | umgesetzt: vier stabile Ziel-IDs; zwei historische Positionen bleiben ohne implizite Zuordnung |
| PR153 | Kompatibilitaetsadapter fuer die zwei vorhandenen Schadenvektoren | umgesetzt: C 1/2 zu Python 0/1 unter neutralen Legacy-IDs; moderne Zuordnung bleibt offen; Altpfad unveraendert |
| PR154 | Strategie- und Parameterzuordnung je Sparte | umgesetzt: getrennte Kfz-/Sach-Haftpflicht-Strategien, skalare Parameter und Periodenfenster je VU/VN validierbar; nur Plan, keine Ausfuehrung |
| PR155 | Vertrag fuer Bewegungsrechnung und einfache Modellbilanz | umgesetzt: versionierte Felder, Gleichungen, Bilanzidentitaeten und Carryover read-only; keine Rechnung |
| PR156 | Modellbilanz fuer Kfz und Sach-Haftpflicht | umgesetzt: exakte Szenario-Dezimalwerte, atomare Bilanzidentitaeten und Perioden-Carryover bis 100; kein Alt-Runner-Anschluss |
| PR157 | Konsolidierte Versichererbilanz in Workbench und XLSX | umgesetzt: exakte Zwei-Sparten-Summe, atomarer Fehlerpfad, Browseransicht und Digest-gebundener XLSX-Export ohne Runner |
| PR158 | Zustands-, Fluss- und Strategievertrag fuer Leben | umgesetzt: geschlossener Vertragsbestand, Garantieverpflichtung, getrennte Fluesse und nicht ausfuehrbare Strategie-Anschlussstellen; Bewertungstiming bleibt offen |
| PR159 | Minimale deterministische Lebensparte | umgesetzt: geschlossener Zwei-Perioden-Fall mit Gutschrift auf Anfangsverpflichtung, spaeter Praemienzuweisung, Ablauf zum Verpflichtungswert und atomarer Bilanz; kein Runner oder Gesamtbilanzanschluss |
| PR160 | Lebensfluss- und Bewertungsvertrag v3 | Tod, Neugeschaeft, Kapital, Policenwerte und abweichende Ablaufleistungen erhalten ausdrueckliche Quellen, Zeitpunkte und Bewertungsgrenzen |
| PR161 | Tod und Kapitalbewegungen im geschlossenen Lebensbestand | Leistungen und Verpflichtungsfreisetzung sind getrennt; Bilanz und Bestand stimmen atomar |
| PR162 | Neugeschaeft mit getrennten Kohorten | Ausgabeparameter, Praemien, Restlaufzeit und Garantiebeginn je Kohorte sind deterministisch |
| PR163 | Begrenzte Einzelpolicen und variable Ablaufleistung | Policenwerte, Kohorten und Gesamtbilanz stimmen; Garantieuntergrenze und Ergebniswirkung sind sichtbar |
| PR164 | Deterministische Anlage- und Mortalitaetsannahmen | versionierte Szenariokurven, einfache VU-Anlageregel und eindeutige Periodenfenster; keine RNG-Vollmodellbehauptung |
| PR165 | Kontrollierter Lebensanschluss an die Periodenkette | bis 100 Perioden, Prefix und Carryover stabil; alter Nichtleben-Pfad bleibt unveraendert |
| PR166 | Lebens-Ergebnis-API, Ablage und XLSX | Digest, Idempotenz und gleiche Zahlen in gespeicherten Ergebnissen und Export |
| PR167 | Gefuehrte Lebens-Workbench fuer Seminare | beschriftete Eingaben, Baseline/Variante, Zeitreihen, Presets und Browserabnahme ohne Roh-JSON als Pflicht |
| PR168 | Zustands-, Fluss- und Strategievertrag fuer Kranken | Beitrags-, Leistungs- und Bestandslogik sind begrenzt und getrennt |
| PR169 | Minimale deterministische Krankensparte | feste Falltests und Bilanzanschluss ohne Vollmodellbehauptung |
| PR170 | Spartenuebergreifende Konsolidierung | vier Modellsegmente stimmen je Versicherer zur Gesamtbilanz ab |

Die erste Mehrspartenstufe deckt damit vier fuer das Zielbild wichtige
Segmente ab. Sie behauptet weder die vollstaendige deutsche
Versicherungszweigsystematik noch eine aufsichtsrechtliche Rechnungslegung.
Die acht PRs 160-167 schliessen die nach PR159 erkannte Lebensluecke vor
Kranken und der Gesamtbilanz. Rueckkauf und Bonus bleiben ausgeschlossen;
Umfang, Annahmen und UI-Bedienweg stehen in
`docs/plans/ims_2x_life_workshop_expansion_plan.md`.

## Phase C: Solvency-II-Kapitalansicht

Ziel: Kapitalwirkungen werden als nachvollziehbare Modellgroessen sichtbar.
Die erste Stufe soll Entscheidungen und Wirkungsrichtungen erklaeren, nicht
eine Meldesoftware ersetzen.

| PR | Kleiner, reviewbarer Liefergegenstand | Zentrale Abnahme |
| --- | --- | --- |
| PR171 | Scope-, Terminologie-, Quellen- und Versionsvertrag | Modellrechnung und regulatorisch validierte Aussage bleiben klar getrennt |
| PR172 | Solvenzmodellbilanz und vereinfachte Eigenmittelabbildung | Herkunft jeder Kapitalgroesse ist zur Versichererbilanz rueckverfolgbar |
| PR173 | Risikotreiber und Szenarioschock-Mapping | jeder Schock veraendert nur explizit zugeordnete Exposures |
| PR174 | Ausgewaehlte Markt- und versicherungstechnische Risikomodule | Schaden, Leben und Kranken besitzen getestete, begrenzte Module |
| PR175 | Gegenpartei-, operationelles Risiko und Aggregation | Korrelationen und verlustabsorbierende Effekte sind versioniert |
| PR176 | SCR, MCR, Bedeckungsquote und Managementschwellen | Kennzahlen sind reproduzierbar und fachlich beschriftet |
| PR177 | Feste Faelle, Sensitivitaeten und Invarianten | Richtung, Monotonie, Grenzwerte und Bilanzanschluss sind geprueft |
| PR178 | Kapitalansicht und Export | Unternehmen, Sparte, Treiber und Unsicherheit sind sichtbar; kein Filing-Anspruch |

Falls PR174 oder PR175 bei der Quellenklaerung zu gross werden, werden sie in
weitere kleine Fach-PRs geteilt. Die Meilensteinzahl erhoeht sich dann, statt
unterschiedliche Risikomodule in einem Sammel-PR zu verstecken.

## Phase D: DORA-Wirkungsketten

Ziel: Ein operatives Ereignis wird von der technischen Stoerung ueber
Geschaeftsprozesse bis zu Kunden-, Markt-, Bilanz- und Kapitalwirkungen
verfolgbar.

| PR | Kleiner, reviewbarer Liefergegenstand | Zentrale Abnahme |
| --- | --- | --- |
| PR179 | Vertrag fuer wichtige Geschaeftsservices, ICT-Assets, Anbieter und Abhaengigkeiten | gerichtete Herkunft und Verantwortungsgrenzen sind explizit |
| PR180 | Ereignis- und Interventionsvertrag | Ausfall, Kapazitaetsverlust, Datenintegritaet und Anbieterausfall sind getrennt |
| PR181 | Adapter von Stunden und Tagen auf IMS-Perioden | keine stille Vermischung operativer und marktlicher Zeitskalen |
| PR182 | Wirkung auf Vertrieb, Underwriting, Schaden und Service | Kapazitaet, Rueckstand und Erholung sind als Kette nachvollziehbar |
| PR183 | Drittparteienkonzentration und korrelierter Ausfall | gemeinsame Anbieter koennen mehrere Versicherer kontrolliert treffen |
| PR184 | Praeventions-, Wiederanlauf- und Fallback-Strategien | Kosten, Wirksamkeit und Restlaufzeit sind parametrierbar |
| PR185 | Anschluss an Bilanz und Kapital | operative Folgen schlagen nachvollziehbar auf Ergebnis und Bedeckung durch |
| PR186 | DORA-Wirkungsansicht und Dossier | Zeitlinie, Abhaengigkeiten, Engpaesse und Unsicherheit sind exportierbar |

Nicht vorgesehen sind ein automatisches DORA-Compliance-Urteil, eine
Rechtsauslegung oder der Ersatz einer operativen Resilienzpruefung.

## Phase E: Managementbedienung und Seminarfreigabe

Ziel: Die Fachlogik wird als ruhiges Entscheidungswerkzeug bedienbar, ohne
dass Anwender interne Datenvertraege oder Quellcode kennen muessen.

| PR | Kleiner, reviewbarer Liefergegenstand | Zentrale Abnahme |
| --- | --- | --- |
| PR187 | Gefuehrter Szenarioassistent mit optionalem Expertenmodus | Frage, Baseline, Schock, Strategien und Ergebnisziel bilden einen Ablauf |
| PR188 | Kuratierte Seminarfaelle | Schadeninflation, Preiswettbewerb, Lebensbestand, Kapitaldruck und ICT-Ausfall sind reproduzierbar |
| PR189 | Moderationspaket und portable Szenariobuendel | Arbeitsblaetter, Import/Export und read-only Demonstration sind geprueft |
| PR190 | End-to-End-Abnahme des Managementseminars | Installation, 100 Perioden, Mehrsparten, Bilanz, Kapital, DORA-Fall und Export funktionieren gemeinsam |

PR190 bezeichnet eine kontrollierte Seminar- und Demonstrationsreife. Eine
fachliche Produktionsfreigabe fuer Beratung, Aufsicht oder einzelne
Unternehmensentscheidungen benoetigt weiterhin einen benannten Datenstand,
einen konkreten Anwendungsfall und dessen eigene Validierung.

## Phase F: Windows Ready-to-run (spaeter)

Diese optionale Distributionsspur beginnt **erst nach PR190** und verschiebt
PR160 nicht. Sie ersetzt auf dem Zielrechner Python-Installation und
Startskripte durch ein entpackbares Windows-ZIP mit Doppelklick-EXE.
Details und Grenzen stehen in
`docs/plans/ims_2x_windows_ready_to_run_packaging_plan.md`.

| PR | Kleiner, reviewbarer Liefergegenstand | Zentrale Abnahme |
| --- | --- | --- |
| PR191 | PyInstaller-One-folder-Bundle fuer Windows x64 | Backend, gebautes Frontend und erforderliche Laufzeitdaten laufen offline ohne Zielrechner-Python; Nutzerdaten bleiben ausserhalb des Bundles |
| PR192 | Doppelklick-Start, ZIP, Zielrechner-Smoke und Kurzhandbuch | Start, Portkonflikt, Zweitstart und Beenden sind verstaendlich; frischer Windows-10/11-Rechner ohne Python/Node und Installationsnetz besteht |

Ein One-file-EXE, grafischer Installer oder Code-Signierung sind damit
nicht versprochen. SmartScreen- und Unternehmensrichtlinien koennen einen
unsignierten Download weiter blockieren. Linux und iOS/Juno sind nicht
Teil dieses Windows-Pakets.

## Meilensteine und Restzahl

| Meilenstein | Erreicht nach | PRs ab PR142 | verbleibend nach PR159 |
| --- | ---: | ---: | ---: |
| technischer 100-Perioden-Lauf | PR149 | 8 | 0 |
| bedienbarer 100-Perioden-Lauf mit Ergebnis und Export | PR151 | 10 | 0 |
| vier Modellsegmente und konsolidierte Versichererbilanz | PR170 | 29 | 11 |
| erklaerbare Solvency-II-Kapitalansicht | PR178 | 37 | 19 |
| durchgaengige DORA-Wirkungskette | PR186 | 45 | 27 |
| kontrollierte Managementseminar-Reife | PR190 | 49 | 31 |
| Windows Ready-to-run ohne Zielrechner-Python | PR192 | 51 | 33 |

Die 49 fachlichen PRs bis PR190 und zwei spaeteren Windows-Packaging-PRs
sind eine Planungsbasis, keine Terminzusage. Realistisch ist eine
Unsicherheit von etwa acht zusaetzlichen PRs, insbesondere bei Leben,
Kranken, Risikomodulen und regulatorischer Quellenvalidierung. Erkenntnisse
werden durch Teilung sichtbar gemacht; sie werden nicht in groessere PRs
gedrueckt.

## Grober Umfang

| Phase | Geschaetzter Umfang einschliesslich Tests und Doku |
| --- | ---: |
| 100 Perioden und Ergebnisarbeitsplatz | 3.000-5.500 LoC |
| Mehrsparten und Bilanz | 6.500-12.500 LoC |
| Solvency-II-Kapitalansicht | 3.000-5.500 LoC |
| DORA-Wirkungsketten | 3.000-5.000 LoC |
| Managementbedienung und Seminarfreigabe | 1.200-2.500 LoC |
| **Gesamt** | **16.700-31.000 LoC** |

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
Meilensteinen PR151, PR167, PR170, PR178 und PR186 aktualisiert.

## Naechster Schritt

PR142 hat den engen read-only Vertrag fuer einen auf fuenf Perioden
begrenzten Kettenrunner und die exakte fachliche Prefixprojektion 1-2
festgelegt. PR143 hat die kanonische Fuenf-Perioden-Kette gebaut und atomar
validiert. PR144 hat sie fluechtig auf isolierten Kandidatenkopien ausgefuehrt
und prueft den Prefix 1-2 semantisch und als kanonisches JSON bytegenau.
PR145 hat kontrollierten Serverstart, dauerhafte Idempotenz und eine durch
Gesamtdigest geschuetzte Ablage von Request, kanonischer Kette und Ergebnis
angeschlossen. PR146 hat den Pfad in der Workbench bedienbar gemacht und die
breite sowie schmale Browseransicht, Fehlerpfade und Handbuchbilder
abgenommen. PR147 hat fuer 10, 25, 50 und 100 Perioden die Laufzeit-,
Ressourcen-, Abbruch- und Fehlergrenzen read-only festgelegt, ohne einen
laengeren Runner freizugeben. PR148 hat danach 10, 25 und 50 Perioden als
isolierte, fluechtige Wirkungsprobe mit Budgetkontrolle und exaktem Prefix
1-5 freigegeben. PR149 hat diese Schutzgrenzen getrennt fuer genau 100
Perioden geprueft und den technischen Lauf fluechtig freigegeben. PR150
hat das versionierte, rein fluechtige Ergebnisbuendel als ausdruecklichen
100er-Download mit gleicher Kennzahlentabelle in JSON, CSV und XLSX
angeschlossen. Eine dauerhafte Ablage ist damit noch nicht freigegeben.
PR151 macht vorbereitete 100er-Ketten, deren vorhandene Zustandsfelder
und gleich praefixierte Vergleiche im Browser nutzbar. Der erneute Lauf
fuer den Download ist an den sichtbaren Digest gebunden. Der gefuehrte
Aufbau einer 100er-Kette bleibt eine zusaetzliche, noch nicht nummerierte
Produktluecke; sie ist in den Restzahlen nicht enthalten. PR152 hat die
vier Zielsparten als versionierte, rein lesende Taxonomie bereitgestellt.
Die zwei historischen Zweiervektor-Positionen bleiben ohne Zuordnung zu
diesen Namen. PR153 hat C-Position 1/2 zu Python-/Exportindex 0/1
verlustfrei und unter neutralen Legacy-IDs abgebildet. Eine moderne
Spartenbindung bleibt offen. PR154 hat fuer die geplanten Nichtleben-Sparten
unterschiedliche Katalogstrategien, skalare Parameter und Zeitfenster je
VU/VN rein validierend beschrieben. Die alten Runner nutzen diese Plaene
noch nicht. PR155 hat die Bewegungsrechnung und einfache Modellbilanz als
read-only Vertrag mit Bilanzidentitaeten, Perioden-Carryover und ausdruecklich
offener Quellbindung festgelegt. PR156 rechnet nun Kfz oder Sach-Haftpflicht
aus expliziten Szenariowerten deterministisch ueber bis zu 100 Perioden,
ohne die alten Positionen zuzuordnen oder einen Runner zu starten. PR157
stellt beide Sparten und ihre exakte Summe in der Workbench dar und liefert
einen Digest-gebundenen XLSX-Export. PR158 hat einen eigenstaendigen
read-only Vertrag fuer einen geschlossenen Lebensbestand, seine
Garantieverpflichtung und Strategie-Anschlussstellen festgelegt. PR159
hat daraus einen schmalen deterministischen Lebensfall mit expliziter
Gutschriftbasis, Ablaufzahlung und Bilanzpruefung gerechnet. Der zu
schmale Lebensumfang wurde danach ausdruecklich nachgeplant: PR160
klaert als Naechstes die Bewertungsbasis fuer Tod, Neugeschaeft,
Kapitalbewegungen und abweichende Ablaufleistungen. PR161-167 setzen
diese Entscheidungen schrittweise um und liefern eine bedienbare
Lebens-Workbench mit Export. Kranken folgt ab PR168, die
Vier-Sparten-Gesamtbilanz in PR170. Bis dahin bleibt die heutige
Zwei-Sparten-Gesamtbilanz unveraendert. Die Windows-Ready-to-run-Spur
PR191/192 bleibt ausdruecklich spaeter.

Die Planung aendert keine Fachlogik und behauptet keine historische
Vollgleichheit.
