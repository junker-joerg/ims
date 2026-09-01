# IMS Workbench 2026 - Bedienungsanleitung fuer das Testpaket

Stand: 2026-09-01
Umfang: 8 Seiten
Zielgruppe: Versicherungsfachleute, Wissenschaftler und Entscheider ohne Kenntnis der Dissertation oder des Quellcodes

## Seite 1 - Was kann ich mit IMS heute machen?

Die IMS Workbench macht den modernisierten Stand des historischen
Versicherungsmarktmodells sichtbar und pruefbar. Sie ist derzeit vor allem ein
transparentes Analyse- und Demonstrationswerkzeug.

Als Anwender koennen Sie heute:

- die technische Betriebsbereitschaft der Anwendung pruefen;
- vorbereitete Szenarien und Runs suchen, auswaehlen und einordnen;
- Herkunft, Zeitraum und Validierungsstatus eines Datenstands nachvollziehen;
- den historischen Vergleich fuer 15 Tabellen und 6.300 Ergebniszeilen lesen;
- erkennen, welche Unterschiede exakt, toleriert oder fachlich offen sind;
- einen vorbereiteten Run-Control-Pfad per Dry-Run und expliziter Freigabe
  kontrollieren, sofern eine passende lokale Metadatenquelle bereitgestellt ist;
- gespeicherte Adapterresultate und ihren Ausfuehrungsverlauf lesen;
- die Oberflaeche und den kuenftigen Bedienablauf aus fachlicher Sicht bewerten.

Noch nicht moeglich sind ein freier Szenarioeditor, der Upload eigener
Marktdaten, eine beliebige neue Simulation im Browser, eine automatische
Kalibrierung auf reale Marktdaten oder eine belastbare Wirkungsanalyse neuer
Regulierung. Diese Funktionen gehoeren zum Ausbau von IMS 2.x.

Das historische Material dient als diagnostischer Legacy-Benchmark. Exakte
Zufallsfolgen aus 35 Jahre alten Bibliotheken sind kein Produktziel. Wichtig
sind nachvollziehbare Annahmen, moderne Reproduzierbarkeit, fachliche
Invarianten und erklaerbare Wirkungsrichtungen.

<!-- PAGE BREAK -->

## Seite 2 - Der Rundgang in zehn Minuten

### 1. Dashboard

Starten Sie auf `Dashboard`. Pruefen Sie zuerst:

- Backend: `bereit`;
- Frontend: `gebaut`;
- Metadatenquelle: erwartete lokale oder statische Quelle;
- keine unerwartete Schreib- oder Simulationsfreigabe.

Das Dashboard beantwortet: Ist die Anwendung technisch benutzbar und welchen
Datenstand sehe ich? Es beantwortet noch nicht: Ist ein konkretes Modell fuer
eine Management- oder Regulierungsentscheidung fachlich freigegeben?

### 2. Szenarien

Wechseln Sie zu `Szenarien`, waehlen Sie das `Agrsich Referenzfenster` und
lesen Sie Quelle, Umfang und Validierungshinweis. Der `Lokale Workbench-Entwurf`
zeigt den technischen Entwicklungsstand, nicht eine reale Marktprognose.

### 3. Validierung

Wechseln Sie zu `Validierung`. Lesen Sie Korpusabdeckung und offene Grenzen
getrennt. `15/15 Tabellen` bedeutet vollstaendige Bereitstellung der
vereinbarten Referenztabellen. Es bedeutet nicht, dass jede historische Zahl
identisch neu berechnet wurde.

### 4. Runs

Wechseln Sie zu `Runs`, waehlen Sie einen vorhandenen Eintrag und pruefen Sie
Szenario, Periodenfenster, Status und Ergebnisanzeige. Ohne vorbereitete lokale
Metadaten bleibt der kontrollierte Startpfad bewusst eingeschraenkt.

Beenden Sie den Rundgang mit der Frage: Sind Status, Grenzen und naechste
Aktion fuer eine fachfremde Person verstaendlich? Genau dieses Feedback ist
fuer das Testpaket wertvoll.

<!-- PAGE BREAK -->

## Seite 3 - Szenarien verstehen

Ein Szenario beschreibt einen fachlichen Ausgangsstand und dessen Herkunft.
Es ist nicht automatisch ein bereits ausgefuehrter Simulationslauf.

In der `Szenario-Uebersicht` koennen Sie:

1. nach Name oder ID suchen;
2. nach Status, Quelle oder Umfang filtern;
3. eine Zeile auswaehlen;
4. im `Metadaten-Detail` Herkunft und Validierungsangabe lesen;
5. die `Auswahlzusammenfassung` kontrollieren.

Beachten Sie drei Statusarten:

- `reference`: historischer oder versionierter Vergleichsstand;
- `draft`: vorbereiteter Entwurf ohne fachliche Freigabe;
- `planned`: beschriebener, aber noch nicht nutzbarer Ausbau.

Fragen, die Sie heute beantworten koennen:

- Welche Referenz wird gezeigt?
- Aus welcher Quelle stammt sie?
- Welcher fachliche Ausschnitt ist gemeint?
- Welche Aussage wird ausdruecklich nicht erhoben?

Fragen, die Sie heute noch nicht beantworten koennen:

- Wie veraendert ein selbst eingegebener Zinssatz den Markt?
- Welche Strategie maximiert den Erfolg eines Versicherers?
- Welche Regulierungsvariante wirkt im realen deutschen Markt am besten?

Die Szenarioansicht ist derzeit bewusst kein Editor. Sie nimmt keine Dateien
aus `incomming/` und keine beliebigen Browser-Uploads an. Damit bleibt die
Herkunft jedes sichtbaren Stands kontrollierbar.

<!-- PAGE BREAK -->

## Seite 4 - Runs und kontrollierte Ausfuehrung

Ein Run ist einem Szenario zugeordnet und besitzt ein Periodenfenster, einen
Status und eine Validierungsaussage. Ein vorhandener Run kann ein
Regressionstest, eine Vorschau oder ein kontrolliert vorbereitetes Ergebnis
sein. Er ist nicht automatisch eine historische Simulation.

### Sicherer Lesepfad

1. Run in der `Run-Uebersicht` auswaehlen.
2. Szenario-ID und Periodenfenster pruefen.
3. Status und Quelle lesen.
4. Im Run-Control-Bereich die vorgeschlagene naechste Aktion kontrollieren.
5. Vorhandenes Ergebnis und Verlauf nur lesend oeffnen.

### Kontrollierter Aktionspfad

Nur wenn eine ausdruecklich vorbereitete lokale Metadatenquelle vorhanden ist:

1. `Dry-Run pruefen` validiert den Request ohne Ausfuehrung.
2. `Queue vormerken` schreibt einen kontrollierten Queue-Eintrag.
3. `Freigabe pruefen` verlangt Person, Begruendung und Bestaetigung.
4. `Adapter starten` wird nur bei erfuellten Vorbedingungen aktiv.
5. `Ergebnis neu laden` liest Status und Verlauf erneut.

Der Start ist manuell und gegen Doppelstarts abgesichert. Es gibt keinen
automatischen Queue-Worker. Der derzeitige Adapterpfad ist ein kontrollierter
technischer Ausfuehrungspfad und keine freie historische Marktsimulation.

Der Knopf `Neuer Lauf` gehoert noch nicht zum freigegebenen Anwenderpfad.

<!-- PAGE BREAK -->

## Seite 5 - Historische Validierung richtig lesen

Die historischen Dateien sind wertvoll, aber sie stammen nicht sicher aus
einem einzigen identischen Lauf. Parameter, Zinssaetze, Compilerplattform und
Zufallszahlengenerator koennen sich unterschieden haben.

Der aktuelle Korpus umfasst:

- 15 von 15 vereinbarten Tabellen;
- 6.300 von 6.300 vereinbarten Ergebniszeilen;
- mehrere getrennte Laeufe von jeweils hoechstens 100 Perioden;
- VU-, VN-, Klassen- und SK1/all-Sichten.

Lesen Sie die Kennzahlen so:

- `Abdeckung`: Die vereinbarten Referenzdaten sind vorhanden und parserfaehig.
- `exakt`: Ein modernes Feld entspricht innerhalb des Vertrags der Referenz.
- `toleriert`: Eine kleine, vorher definierte numerische Differenz ist
  akzeptiert.
- `abweichend`: Das Feld unterscheidet sich und benoetigt Einordnung.
- `blocked`: Eine Freigabe ist nicht erteilt; die Anwendung kann trotzdem
  technisch funktionieren.

Eine abweichende stochastische Trajektorie ist nicht automatisch ein
fachlicher Fehler. Weiter untersucht werden insbesondere verletzte Bilanz-,
Bestands- oder Aggregatinvarianten, nicht reproduzierbare moderne Laeufe und
unerwartete Wirkungsrichtungen.

Die Zahl `6.300/6.300` ist deshalb ein Vollstaendigkeitsnachweis des
Vergleichskorpus, kein historischer Vollgleichheitsnachweis.

<!-- PAGE BREAK -->

## Seite 6 - Ergebnisse fachlich einordnen

Ein Ergebnis ist erst dann belastbar, wenn vier Dinge gemeinsam sichtbar sind:

1. **Ausgangslage:** Datenquelle, Zeitraum und Population.
2. **Annahmen:** Regeln, Parameter, Regulierung und Strategien.
3. **Reproduzierbarkeit:** Version, Seed-Policy und Run-Manifest.
4. **Aussagegrenze:** Was darf aus diesem Lauf geschlossen werden?

Bei vorbereiteten Adapterresultaten zeigt die Workbench Queue, Run, Szenario,
Summary-Modus, Persistenzzeitpunkt und Verlauf. Pruefen Sie, ob diese Angaben
zum erwarteten Auftrag passen. Ein technisch erfolgreiches Resultat ist noch
keine fachliche Freigabe.

Fuer IMS 2.x sollen deterministische Formeln weiterhin exakt getestet werden.
Stochastische Ergebnisse sollen dagegen ueber Verteilungen, Quantile,
Wirkungsrichtung, Effektstaerke und Robustheit mehrerer Seeds bewertet werden.

Eine gute fachliche Ergebnisfrage lautet zum Beispiel:

- Bleibt die Aggregation konsistent?
- Ist der moderne Lauf bei gleichem Manifest reproduzierbar?
- Wirkt eine kontrollierte Parameteraenderung in die erwartete Richtung?
- Bleibt der Befund ueber mehrere Seeds stabil?
- Ist die Unsicherheit sichtbar und erklaerbar?

Eine schlechte Ergebnisfrage lautet: Ist jede zufallsgetriebene Einzelzahl
aus einem nicht vollstaendig dokumentierten Lauf von 1995 bytegleich?

<!-- PAGE BREAK -->

## Seite 7 - Wofuer soll IMS 2.x ausgebaut werden?

Das Zielbild ist eine gemeinsame, erweiterbare Plattform fuer
Versicherungsmarktsimulationen. Der heutige Teststand zeigt die technische und
wissenschaftliche Grundlage; die folgenden Anwendungen benoetigen weitere,
jeweils eigene Validierung.

### Kalibrierte Marktrekonstruktion

Reale Marktkennzahlen dienen als Kalibrierungs- und Backtesting-Ziele. IMS soll
nicht behaupten, die Realitaet punktgenau vorherzusagen, sondern erklaeren,
welche Modellannahmen beobachtete Strukturen plausibel erzeugen.

### Management-Simulation

Versichererstrategien koennen spaeter als kontrollierte Szenarien verglichen
werden, etwa Preis, Werbung, Reservepolitik oder Informationssuche. Ergebnisse
muessen relativ zu einer Basislinie und mit Unsicherheit gezeigt werden.

### Regulierungs-Wirkungsanalyse

Regeln oder Eingriffe koennen als versionierte Gegenwelten verglichen werden.
Wichtig sind Wirkungsrichtung, Verteilungsfolgen, Robustheit und erklaerbare
Annahmen. Dies ist das empfohlene erste oeffentliche Leuchtturmthema.

### Forschung und Publikation

Kuratierte, schreibgeschuetzte Szenarien koennen Methoden, historische
Entwicklung und moderne Erweiterungen nachvollziehbar zeigen. Provenienz und
Run-Manifeste machen Ergebnisse zitier- und reviewbar.

Die vier Richtungen sollen denselben Kern, dasselbe Szenarioformat und dieselbe
Ergebnis- und Nachweisschicht verwenden. So bleibt IMS ausbaubar, ohne zu vier
unvereinbaren Spezialprogrammen zu werden.

<!-- PAGE BREAK -->

## Seite 8 - Grenzen, Feedback und Kurzglossar

### Bitte testen Sie besonders

- Ist nach dem Start sofort klar, wo Szenarien, Validierung und Runs liegen?
- Verstehen Sie den Unterschied zwischen technischer Bereitschaft und
  fachlicher Freigabe?
- Ist bei jeder Kennzahl erkennbar, worauf sie sich bezieht?
- Finden Sie einen vorbereiteten Run und dessen Herkunft ohne Zusatzwissen?
- Bleiben gesperrte oder noch geplante Funktionen ehrlich erkennbar?
- Welche zwei fachlichen Diagramme oder Vergleiche wuerden Ihnen fuer eine
  echte Management- oder Regulierungsfrage zuerst fehlen?

### Nicht mit diesem Testpaket tun

- keine vertraulichen oder personenbezogenen Daten einspielen;
- den lokalen Server nicht ins Netzwerk freigeben;
- historische Referenzdateien nicht ueberschreiben;
- angezeigte Vergleichswerte nicht als Prognose oder Produktfreigabe verwenden;
- `incomming/` nicht als Benutzerimport behandeln.

### Kurzglossar

| Begriff | Bedeutung |
| --- | --- |
| Szenario | dokumentierte Ausgangslage mit Annahmen und Herkunft |
| Run | einem Szenario zugeordneter Lauf- oder Ergebnisdatensatz |
| Queue | kontrollierte Vormerkung fuer einen Ausfuehrungsschritt |
| Dry-Run | Request-Pruefung ohne Ausfuehrung |
| Adapter | eng begrenzte technische Verbindung zum vorbereiteten Laufpfad |
| Legacy-Benchmark | historische Daten fuer Herkunft, Struktur und Diagnose |
| Seed | Startwert einer modernen reproduzierbaren Zufallsfolge |
| Invariant | fachliche Bedingung, die unabhaengig vom Zufall gelten muss |

Zum Beenden wechseln Sie in das Serverfenster und druecken `Strg+C`. Installation
und Fehlerhilfe stehen in `INSTALLATION.pdf`.
