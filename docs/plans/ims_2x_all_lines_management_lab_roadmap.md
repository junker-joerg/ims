# Roadmap: IMS 2.x Mehrsparten- und Regulationslabor

Stand: 2026-09-18
Status: aktive Produkt-Restplanung; PR178a Handbuch umgesetzt, PR179 DORA-Vertrag naechster Schritt
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
[SCR-Begriff und Kalibrierung](https://www.eiopa.europa.eu/rulebook/solvency-ii-single-rulebook/article-2188_en)
und zum
[MCR](https://www.eiopa.europa.eu/rulebook/solvency-ii-single-rulebook/article-2216_en),
erneut geprueft am 2026-09-18. Die
[Revision (EU) 2025/2](https://www.eiopa.europa.eu/browse/regulation-and-policy/solvency-ii_en)
gilt erst ab 30.01.2027. PR171 haelt den Quellen- und Versionsstand in
`docs/plans/ims_2x_pr171_solvency_scope_contract.md` fest und gibt noch
keine Rechtsregime- oder Formelwahl fuer eine Rechnung frei.

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
Voraussetzung und wird in PR187a-c gefuehrt geschlossen; eine persistierte
100er-Ausfuehrung ist nicht freigegeben.

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
| PR160 | Lebensfluss- und Bewertungsvertrag v3 | umgesetzt: read-only Zielvertrag fuer Quellen, Zeitpunkte, Reservefreisetzung, Kapital und Garantien; v1/v2 bleiben unveraendert, v3 rechnet noch nicht |
| PR161 | Tod und Kapitalbewegungen im geschlossenen Lebensbestand | umgesetzt: getrennte Leistung/Freisetzung, Kapitalfluesse, Bilanz/Bestand atomar; PR159-Spezialfall stabil, kein Runner |
| PR162 | Neugeschaeft mit getrennten Kohorten | umgesetzt: Ausgabeparameter, Praemien, Restlaufzeit und Garantiebeginn je Kohorte deterministisch; PR161-Spezialfall stabil, kein Runner |
| PR163 | Begrenzte Einzelpolicen und variable Ablaufleistung | umgesetzt: vollstaendige Liste bis 100 aktive Policen, Garantieuntergrenze, getrennte Auszahlung/Freisetzung und atomare Bilanz; kein Runner/UI |
| PR164 | Deterministische Anlage- und Mortalitaetsannahmen | umgesetzt: exklusive Quellen, lueckenlose Fenster, VU-Anlagebetrag und Kohorten-Todesfallauswahl; kein Runner |
| PR165 | Kontrollierter Lebensanschluss an die Periodenkette | umgesetzt: fluechtiger 100er-Pfad mit PR164-Quellen, PR163-Prefix, Carryover und Abbruch ohne Teilresultat; Nichtleben unveraendert |
| PR166 | Lebens-Ergebnis-API, Ablage und XLSX | umgesetzt: 20-Sekunden-API-Budget, erneute Digestpruefung, dauerhafte Idempotenz, read-only Verlauf und exakte Dezimaltexte im XLSX; Recovery-Abnahme offen |
| PR167 | Gefuehrte Lebens-Workbench fuer Seminare | umgesetzt: drei kuratierte Zwei-Perioden-Faelle, beschriftete Stellhebel, Baseline/Variante, Zeitreihe, explizite Ergebnisablage; neue Handbuchbilder und Browser-Dateidownload offen |
| PR168 | Zustands-, Fluss- und Strategievertrag fuer Kranken | umgesetzt: geschlossener Bestand, getrennte Beitrags-/Leistungsfluesse, offene Leistungsverpflichtung und kuenftige Strategie-Anschlussstellen; read-only ohne Rechnung |
| PR169 | Minimale deterministische Krankensparte | umgesetzt: expliziter Ein-/Zweiperiodenfall, exakte Dezimalbilanz, Carryover und atomarer Fehlerpfad; kein Runner oder Browserstart |
| PR169a | Kranken-Bestands- und Quellenvertrag | umgesetzt: Neugeschaeft, Abgang, Beitragsanpassung und exogene Leistungsannahmen versioniert und atomar validiert; kein Runner |
| PR169b | Kontrollierte Kranken-Periodenkette bis 100 | umgesetzt: 1/2/5/10/25/50/100 fluechtige Perioden, exakte Prefixe, Bilanz-/Bestandsinvarianten und atomarer Abbruch; kein Browserstart |
| PR169c | Kranken-Ergebnisablage, API und CSV/JSON/XLSX | umgesetzt: ausdrueckliche Freigabe, Idempotenz, Digest, verifizierter Verlauf und Herkunft in allen Exporten; keine Workbench-Eingabe |
| PR169d | Bedienbare Kranken-Workbench | umgesetzt: expliziter Seminarfall, Baseline/Variante, Zeitreihen, Verlauf und CSV/JSON/XLSX bis 100 Perioden auf breitem/schmalem Viewport abgenommen |
| PR170 | Spartenuebergreifende Konsolidierung | umgesetzt: vier neu berechnete Modellsegmente stimmen je VU und Periode atomar zur einfachen Gesamtbilanz ab; noch kein gemeinsamer Browser-Bedienweg |
| PR170a | Vier-Sparten-Bilanz in der Workbench | umgesetzt: gepruefte Eingaben gezielt uebernommen, VU-/Horizontkonflikte gesperrt, vier Allokationen und Gesamtbilanz auf breitem/schmalem Viewport abgenommen; keine Speicherung |

Die erste Mehrspartenstufe deckt damit vier fuer das Zielbild wichtige
Segmente ab. Sie behauptet weder die vollstaendige deutsche
Versicherungszweigsystematik noch eine aufsichtsrechtliche Rechnungslegung.
Die acht PRs 160-167 schliessen die nach PR159 erkannte Lebensluecke vor
Kranken und der Gesamtbilanz. Rueckkauf und Bonus bleiben ausgeschlossen;
PR160 hat den read-only Vertrag festgelegt; PR161 hat die separate
Rechnung fuer Tod und Kapital begonnen. PR162 hat Neugeschaeft und
getrennte Kohorten ergaenzt; PR163 hat begrenzte Einzelpolicen mit
expliziter Ablaufleistung ergaenzt. PR164 hat deterministische
Anlage- und Mortalitaetsquellen als getrennte Periodenaufloesung
ergaenzt. PR165 hat diese Quellen mit einer fluechtigen,
kontrollierten Lebens-Periodenkette verbunden. PR166 hat
Ergebnisablage, API und Export mit ausdruecklicher Freigabe ergaenzt;
der 100x100-Extremfall bleibt ausserhalb des interaktiven Zeitbudgets.
PR167 hat drei kleine Seminarfaelle in die Workbench gebracht; freie
Anfangsbestands- und Laufzeitgestaltung sowie neue Handbuchbilder
bleiben offen.
PR168 hat einen separaten Kranken-Vertrag fuer einen geschlossenen Bestand
festgelegt. Angefallene und ausgezahlte Leistungen sowie die offene
Leistungsverpflichtung sind getrennt; Tarife, Alterungsrueckstellung und
Strategieausfuehrung bleiben offen.
PR169 hat diesen eng begrenzten, atomaren Zwei-Perioden-Fall geliefert.
Die vollstaendige Simulationsdauer und der Browserweg sind jetzt
verbindlich als PR169a-d **vor PR170** eingeplant. Erst nach PR169d
ist Kranken ueber bis zu 100 Perioden bedienbar; PR169 allein erfuellt
dieses Ziel nicht.
Der Lebensausbau und sein UI-Bedienweg stehen in
`docs/plans/ims_2x_life_workshop_expansion_plan.md`; fuer Kranken beschreibt
`docs/plans/ims_2x_pr169_health_balance_and_simulation_plan.md` die
Rechnung und den verbindlichen Bedienpfad.

## Phase C: Solvency-II-Kapitalansicht

Ziel: Kapitalwirkungen werden als nachvollziehbare Modellgroessen sichtbar.
Die erste Stufe soll Entscheidungen und Wirkungsrichtungen erklaeren, nicht
eine Meldesoftware ersetzen.

| PR | Kleiner, reviewbarer Liefergegenstand | Zentrale Abnahme |
| --- | --- | --- |
| PR171 | Scope-, Terminologie-, Quellen- und Versionsvertrag | umgesetzt: read-only Vertrag mit Rechtsstand, Modellherkunft und fehlenden Bruecken; keine Kapitalrechnung oder regulatorische Aussage |
| PR172 | Solvenzmodellbilanz und vereinfachte Eigenmittelabbildung | umgesetzt: vier explizite Modell-Bewertungsdifferenzen, ein Stichtag, exakter Eigenmittel-Proxy und PR170-Digest; keine regulatorischen Eigenmittel |
| PR173 | Risikotreiber und Szenarioschock-Mapping | umgesetzt: serverseitig neu berechnete PR172-Quelle, benannte Teilbestaende und explizite Deltas; nur Ziel-Exposures veraendert, kein SCR/MCR |
| PR174 | Ausgewaehlte Markt- und versicherungstechnische Risikomodule | umgesetzt: vier begrenzte, szenariodeklarierte Modellmodule auf PR173-Exposures; Kfz, Sach-Haftpflicht, Leben und Kranken getestet, kein regulatorisches SCR |
| PR175 | Gegenpartei-, operationelles Risiko und Aggregation | umgesetzt: deklarierte Modellverluste, positive Ein-Faktor-Korrelation und unabhaengiger Modellpuffer versioniert; kein SCR |
| PR176 | SCR, MCR, Bedeckungsquote und Managementschwellen | umgesetzt: Managementgrenzen auf Modellwerten pruefbar; regulatorische Werte mangels Bewertung, Kalibrierung und Rechtsstichtag maschinenlesbar gesperrt |
| PR177 | Feste Faelle, Sensitivitaeten und Invarianten | umgesetzt: zwoelf feste Modellfaelle, Quellen-Digests, Bilanz- und Stressinvarianten, Grenzwerte und atomare Fehler geprueft; keine regulatorische Freigabe |
| PR178 | Kapitalansicht und Export | umgesetzt: gepruefte Vier-Sparten-Bilanz, deklarierte Seminarannahmen, digestgebundene Modellwirkung und getrennt gesperrte Regulatorik; JSON/XLSX ohne Speicherung |

Eine echte aufsichtsrechtliche SCR-/MCR-Rechnung ist nicht Teil von
PR176-178. Sie braucht nach Quellen- und Datenfreigabe einen separaten
Fachplan und eigene PRs; diese wuerden offen zur Meilensteinzahl addiert.

## Zwischenstufe: Handbuch nach PR178

| PR | Kleiner, reviewbarer Liefergegenstand | Zentrale Abnahme |
| --- | --- | --- |
| PR178a | Konsolidiertes Benutzer- und Installationshandbuch v1 | umgesetzt: 2 Seiten Windows-Installation und 10 Seiten Bedienung als Markdown/PDF mit echten Screenshots, Dissertation, Theorie, Schocks, Ergebnissen und Grenzen |

PR178a liegt **nach PR178 und vor PR179**. Das
[Handbuchzielbild](ims_2x_pr178a_handbook_plan.md) trennt die
historische Marktidee von neuen Modell-Stressen und vermeidet
unerfuellte Windows-Doppelklick-, Linux- oder iOS-Versprechen.

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
| PR187a | Vertrag fuer gefuehrte 100er-Kettenvorbereitung | 100 vollstaendige Periodenkontexte, Seeds, Strategiezeitfenster und Carryover werden vor dem Bau atomar geprueft; keine erfundenen Defaults |
| PR187b | Kontrollierter Bau der 100er-Kette | alle Kandidaten serverseitig neu materialisiert, Prefixe und Digest geprueft, ausdruecklich und idempotent gespeichert; noch kein Lauf |
| PR187c | Gefuehrter 100er-Start in der Workbench | PR151-Lauf und Download aus einer selbst aufgebauten Kette, mit Fehlersperren und breiter/schmaler Browserabnahme |
| PR187d | Quellen- und Periodenvertrag fuer vier Sparten ueber 100 Perioden | dieselbe VU und Perioden 1-100, gemeinsame Szenario-Variante ausdruecklich erklaert und geprueft; fehlende Nichtleben-ID und Altpositionsmapping bleiben sichtbar |
| PR187e | Kontrollierte 100er-Vier-Sparten-Rechnung | vorhandene vier Teilmodelle neu berechnen, periodische Bilanz- und Carryover-Invarianten, stabiler Zwei-Perioden-Prefix, Ressourcenbudget und atomarer Abbruch |
| PR187f | 100er-Mehrspartenansicht und Exporte | Baseline/Variante, vier Sparten und Gesamtbilanz im Browser, CSV/JSON/XLSX mit gleicher Herkunft sowie breite/schmale Browserabnahme und Handbuchbilder |
| PR188 | Kuratierte Seminarfaelle | Schadeninflation, Preiswettbewerb, Lebensbestand, Kapitaldruck und ICT-Ausfall sind reproduzierbar |
| PR189 | Moderationspaket und portable Szenariobuendel | Arbeitsblaetter, Import/Export und read-only Demonstration sind geprueft |
| PR190 | End-to-End-Abnahme des Managementseminars | Installation, 100 Perioden, Mehrsparten, Bilanz, Kapital, DORA-Fall und Export funktionieren gemeinsam |

Die PR187a-f sind die bislang **nicht mitgezaehlten** Luecken zwischen
vorbereiteter PR151-Kette, PR170a-Zwei-Perioden-Bilanz und der
PR190-Abnahme. Der [Abnahmeplan](ims_2x_pr187_hundred_period_readiness_plan.md)
legt die fachlichen Grenzen je Schnitt fest. PR188 und PR190 duerfen
keinen 100-Perioden-Mehrspartenfall als bestanden ausgeben, bevor
PR187c und PR187f abgenommen sind.

PR190 bezeichnet eine kontrollierte Seminar- und Demonstrationsreife. Eine
fachliche Produktionsfreigabe fuer Beratung, Aufsicht oder einzelne
Unternehmensentscheidungen benoetigt weiterhin einen benannten Datenstand,
einen konkreten Anwendungsfall und dessen eigene Validierung. Die
Handbuch-Erstausgabe aus PR178a wird bei PR186, PR187f und PR190 an den
jeweils belegten Bedienstand angepasst.

## Phase F: Windows Ready-to-run (spaeter)

Diese optionale Distributionsspur beginnt **erst nach PR190** und aendert
die vorangehenden Fachphasen nicht. Sie ersetzt auf dem Zielrechner Python-Installation und
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

| Meilenstein | Erreicht nach | PRs ab PR142 | verbleibend nach PR174 |
| --- | ---: | ---: | ---: |
| technischer 100-Perioden-Lauf | PR149 | 8 | 0 |
| bedienbarer 100-Perioden-Lauf mit Ergebnis und Export | PR151 | 10 | 0 |
| bedienbare Kranken-Simulation bis 100 Perioden | PR169d | 32 | 0 |
| vier Modellsegmente und konsolidierte Versichererbilanz (API) | PR170 | 33 | 0 |
| Vier-Sparten-Bilanz im Browser | PR170a | 34 | 0 |
| Solvency-II-Geltungsvertrag | PR171 | 35 | 0 |
| Modell-Solvenzbilanz und Eigenmittel-Proxy | PR172 | 36 | 0 |
| explizites Risikotreiber- und Schock-Mapping | PR173 | 37 | 0 |
| begrenzte Markt- und Verpflichtungs-Modellmodule | PR174 | 38 | 0 |
| deklarierte Gegenpartei-, Betriebs- und Korrelationsverluste | PR175 | 39 | 0 |
| Managementschwellen und gesperrte Kapitalwerte | PR176 | 40 | 0 |
| Feste Kapital-Modellfaelle und Invarianten | PR177 | 41 | 0 |
| erklaerbare Solvency-II-Kapitalansicht | PR178 | 42 | 0 |
| lesbares Benutzer- und Installationshandbuch v1 | PR178a | 43 | 0 |
| durchgaengige DORA-Wirkungskette | PR186 | 51 | 8 |
| gefuehrter 100er-Kettenaufbau und Start | PR187c | 55 | 12 |
| bedienbarer 100er-Mehrspartenlauf | PR187f | 58 | 15 |
| kontrollierte Managementseminar-Reife | PR190 | 61 | 18 |
| Windows Ready-to-run ohne Zielrechner-Python | PR192 | 63 | 20 |

Die 61 geplanten Schritte ab PR142 bis PR190, darunter PR178a und
PR187a-f, sowie zwei spaetere Windows-Packaging-PRs sind eine
Planungsbasis, keine Terminzusage. Nach PR178a verbleiben damit **18
Schritte bis zur Seminarabnahme** und **20 bis zum Windows-ZIP**.
Quellen- oder Performancebefunde koennen besonders die separate
Kapitalrechnung und PR187e
weiter teilen; ihre Zusatzschritte werden dann offen mitgezaehlt.
PR169a-d, PR170a, PR178a und PR187a-f zaehlen jeweils als eigener PR,
ohne die schon nummerierten PR170-192 umzubenennen.

## Grober Umfang

| Phase | Geschaetzter Umfang einschliesslich Tests und Doku |
| --- | ---: |
| 100 Perioden und Ergebnisarbeitsplatz | 3.000-5.500 LoC |
| Mehrsparten und Bilanz | 8.500-16.500 LoC |
| Solvency-II-Kapitalansicht | 3.000-5.500 LoC |
| DORA-Wirkungsketten | 3.000-5.000 LoC |
| Managementbedienung und Seminarfreigabe | 1.200-2.500 LoC |
| **Gesamt** | **18.700-35.000 LoC** |

Die Schaetzung umfasst produktiven Code, Tests und Dokumentation. Sie ist
bewusst breit und wird an jedem Phasenende anhand des tatsaechlichen Bestands
neu bestimmt. Sie stammt aus dem urspruenglichen Meilensteinplan; die jetzt
expliziten PR187a-f und das Handbuch PR178a sind darin nicht separat
kalkuliert. Die LoC-Prognose wird vor PR187a neu beziffert, statt die
Luecken als kostenneutral auszugeben.

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

Der nichttechnische Einstieg liegt nun in
`docs/handbook/user_guide_test_package.md` samt Druck-PDF; die Windows-
Installation steht in `installation_test_package_windows.md`. Der
Seminarleitfaden und die technischen Einzelkapitel bleiben Vertiefung.
PR178a hat die beiden Haupttexte und neue Kapital-Screenshots
zusammengefuehrt. HB4/HB5 bleiben separate Linux-/iOS-Juno-Pruefungen
ohne Supportversprechen; die bisherige HB6-Konsolidierung geht in PR178a
und die PR190-Endabnahme ein. Bilder und Bedienwege werden bei PR186
und PR187f nachgezogen, nicht vorweggenommen.

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
Aufbau einer 100er-Kette ist jetzt in PR187a-c mitgezaehlt. PR152 hat die
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
hat einen separaten read-only v3-Vertrag fuer Tod, Neugeschaeft,
Kapitalbewegungen, Policenwerte und abweichende Ablaufleistungen
festgelegt, ohne die v2-Rechnung zu veraendern. PR161 hat einen separaten
Rechenschnitt fuer Tod und Kapital umgesetzt. PR162 hat getrennte
Kohorten mit Neugeschaeft ergaenzt. PR163 fuehrt einen separat
versionierten, vollstaendig enumerierten Policenmodus mit expliziter
Ablaufleistung, individueller Gutschrift und 100er-Bestandsgrenze ein.
PR164 hat dafuer exklusive Anlage- und Mortalitaetsquellen mit
Periodenfenstern aufgeloest, aber keine Folgeperioden erzeugt.
PR165 hat diese Quellen auf geprueften Anfangs- und Vorperiodenwerten
fluechtig durch bis zu 100 Lebensperioden gefuehrt. PR166 hat eine
20-Sekunden-API-Grenze, digestgepruefte Ergebnisablage, read-only
Verlauf und XLSX ergaenzt; groessere reine Lebensfaelle bleiben
ausserhalb des interaktiven Starts. PR167 hat eine bedienbare
Lebens-Workbench fuer kuratierte Zwei-Perioden-Faelle geliefert.
PR168 hat den read-only Kranken-Vertrag mit getrennten Beitrags-,
Leistungs- und Bestandswerten geliefert. PR169 hat daraus einen
deterministischen Ein-/Zweiperiodenfall mit atomarer Bilanzpruefung aus
expliziten Szenariowerten gerechnet. PR169a hat Bestandsbewegungen,
Beitrags- und exogene Leistungsquellen je Periode versioniert und
atomar validiert; dies erzeugte noch keine Bilanz. PR169b hat den
geprueften Plan und explizite Bilanzwerte in einer fluechtigen Kette
fuer sieben Horizonte bis 100 Perioden verbunden. PR169c hat
kontrollierte Ergebnisablage, API und CSV/JSON/XLSX geliefert.
PR169d hat den gefuehrten Kranken-Bedienpfad mit Baseline/Variante,
Verlauf, Downloads und Browserabnahme fuer 100 Perioden ergaenzt.
PR170 hat die vier explizit eingegebenen Sparten je VU und Periode neu
berechnet und Vermoegen, Verpflichtungen, Eigenkapital und Kapitalbewegung
zur einfachen Gesamtbilanz abgestimmt. Die bisherige Zwei-Sparten-API ist
unveraendert; in der Workbench ist sie nun als Schadenbilanz beschriftet.
PR170a hat die vier geprueften Eingaben in der Workbench verbunden,
Baseline/Variante getrennt, VU- und Horizontkonflikte gesperrt sowie
Gesamt- und Spartenbilanz fuer zwei Perioden auf beiden Browserbreiten
abgenommen. PR171 hat Geltung, Begriffe, Quellen, Versionen und die
fehlenden Bewertungs- und Risikobruecken rein lesend festgehalten.
PR172 hat je VU und ausgewaehlter Periode vier ausdrueckliche
Modell-Bewertungsdifferenzen mit der PR170-Bilanz abgestimmt und daraus
einen als Modellwert markierten Eigenmittel-Proxy gebildet.
PR173 hat benannte, nicht ueberlappende Modell-Teilbestaende und
ausdrueckliche absolute Szenariodeltas an den neu berechneten PR172-
Checkpoint gebunden. Nicht zugeordnete Teilbestaende bleiben unveraendert.
PR174 hat szenariodeklarierte relative Modell-Stresssaetze fuer
Marktaktiva sowie Schaden-, Lebens- und Krankenverpflichtungen an
PR173-Teilbestaende gebunden. Die Einzelwirkungen sind deterministisch
und nicht regulatorisch kalibriert; zwischen Modulen wird nicht aggregiert.
PR175 hat Gegenpartei- und operationelle Szenarioverluste an die
PR174-Quelle gebunden. Die Aggregation verwendet explizite positive
Ein-Faktor-Korrelationen und einen separat deklarierten Modellpuffer;
das ist keine aufsichtsrechtliche Kapitalberechnung.
PR176 hat die Quellen- und Rechtsstandsgrenze entschieden: SCR, MCR,
anrechenbare Eigenmittel und Quoten bleiben ohne belastbare Grundlage
gesperrt. Zwei explizite Workshop-Grenzen koennen den PR172-Eigenmittel-
Proxy gegen den PR175-Netto-Modellstress pruefen, ohne Compliance-Aussage.
PR177 hat zwoelf feste Modellfaelle und die zugehoerigen Bilanz-,
Stress-, Quellen- und Managementinvarianten geprueft. Die
regulatorischen Werte bleiben auch bei bestandenen Workshop-Grenzen
gesperrt. PR178 zeigt die digestgebundene Modellwirkung aus der
Vier-Sparten-Bilanz mit deklarierten Workshop-Annahmen im Browser;
JSON und XLSX behalten die Regulatorik-Sperre bei. **PR178a ist
umgesetzt:** ein gut lesbares Benutzer- und Installationshandbuch
mit echten Screenshots des belegten Standes. **PR179 folgt:** der
gerichtete Vertrag fuer Geschaeftsservices, ICT-Assets, Anbieter und
Abhaengigkeiten als Einstieg in die DORA-Wirkungskette.
Der bedienbare 100-Perioden-Mehrspartenlauf ist als PR187d-f mit
Quellenbindung, Rechnung und Browserabnahme vor PR190 eingetragen.
Die Windows-Ready-to-run-Spur
PR191/192 bleibt ausdruecklich spaeter.

Die Planung aendert keine Fachlogik und behauptet keine historische
Vollgleichheit.
