# DORA-Referenzfall: drei Versicherer, Version 1

**Spezifikation vom 02.10.2026, Vorschlag.** Der vollständige Fall ist noch nicht
ausführbar. Technische Bestandsläufe stehen im [Laufbericht](../reports/ims_board_baseline_2026_10.md).
Alle Zahlen hier sind synthetische Modellannahmen in Modellwährung, keine
Firmenprofile, Ausfallwahrscheinlichkeiten oder Compliance-Bewertung.

## Vorstandsfrage und kontrollierte Ausgangslage

Welche zusätzliche Vorsorge kaufen wir mit sechs Geldeinheiten, bis wann muss
sie wirksam sein, und wann begrenzen wir die Aufnahme von wechselndem Geschäft?
Die Entscheidung richtet sich nach Ergebnis, verfügbarer Liquidität, Service
und Risikoaufnahme; eine vorgegebene Siegerstrategie gibt es nicht.

Fokus F und Wettbewerber G/H sind drei Einzelgesellschaften, jeweils eine eigene
synthetische Gruppe. Keine Konsolidierungs- oder Tochterdoppelzählung. Je Haus
sechs aktive Verträge (drei niedrige, drei höhere Risiken), Anfangs-Cash 30,
sonstige Aktiva 20, Verpflichtungen 20, Modell-Eigenkapital 30. Ein Vertrag
verdient vier Einheiten Prämie pro Periode; deklarierter Schadenaufwand je
aktivem niedrigen/höheren Risiko ist im Handpfad eins/drei, Zahlung eine Periode
später. Anfangsforderungen, Zahlungsverpflichtungen und Rückstand null.
Cash ist Teil der Aktiva. Keine Anlagebewertung, Rückversicherung oder SCR.

Sechs Perioden à eine Stunde: `[0,1)` bis `[5,6)`. Derselbe Anfang, dieselben
Verträge und dieselbe Schockfolge in jedem Strategieexperiment. Ein separater
Kontrollfaktor schaltet den Schock aus; er ändert keine Vorsorgekosten.
Alle periodischen Kosten werden einmal gebucht. Kein exogener AP3-Baseline-
Gewinn wird zusätzlich zu Prämien/Schäden als zweiter Ertrag übernommen.

## Prozess, Abhängigkeiten und Fähigkeiten

Der Handfall betrachtet ausschließlich Antrag/Vertragswechsel. Je Haus zwei
Anträge pro Stunde und drei Bearbeitungsplätze; Originale vor Nacharbeit,
FIFO mit stabiler Antrags-ID. Schadenansprüche aus bestehenden Verträgen
entstehen unabhängig vom Antragsrückstand. Eine später folgende Erweiterung
kann die vorhandenen vier ICT-Prozesse aufnehmen; sie darf dieselbe Personal-
kapazität dann nicht vierfach vergeben.

Die zwei Vorgänge sind zunächst eine fest deklarierte Arbeitslast aus den
18 bestehenden Risiken, etwa Vertragsänderungen/Wechselprüfungen, keine zwei
automatisch neu erzeugten Versicherungsverträge. Ein Risiko kann mehrere
verschiedene Verwaltungsvorgänge, aber höchstens einen offenen Wechselantrag
haben. Der gekoppelte Versuch ersetzt die konstante Last durch protokollierte
Vorgänge und Kundenbewegungen; die reine Handtabelle hält sie ausdrücklich fest.
Grund-Personalkosten drei je Haus/Periode werden auch im Ausfall bezahlt;
Rückstand kostet 0,2 je Vorgang am Periodenende, Nacharbeit zunächst null.
Andere Prozess-/Vorsorgekosten benötigen eigene Eingaben, keine implizite
zusätzliche Marge pro bearbeitetem Antrag.

Standardpfad: `Portal F/G/H → P-Antragsdienst → P-Identität und P-Daten`.
Alle drei nutzen den gemeinsamen synthetischen Provider P. Ausfall E1 ist
`[2,4)`, Intensität 100 Prozent. Eine nominelle Ersatzlösung mit P-Identität
bleibt abhängig und fällt mit aus. Die unabhängige Alternative Q hat eigene
Identität, Datenkopie und Netz-/Betriebsabhängigkeiten, die im Vertrag vollständig
benannt und gegen P geprüft werden. Q bleibt eine Annahme; ein gemeinsamer
Q-Unterlieferant wird als Sensitivität ergänzt und kann beide Pfade stilllegen.

| Fokusstrategie | Zusatzbudget und Verwendung | Investition / Verfügbarkeit | Nach E1 |
| --- | --- | --- | --- |
| F0 bestehende Vorsorge | 0 ausgegeben, 6 ausdrücklich eingespart | Bestehender dokumentierter Plan; kein zusätzlicher Notbetrieb | Normalbetrieb ab t=4 |
| F1 getesteter Wiederanlauf / Notbetrieb | 6: 4 Vorbereitung/Test, 2 reservierte Aktivierung | Entscheidung t=-5, technisch verfügbar t=-2, Test t=-1 | Nach Erkennung t=2,25 und Entscheidung t=2,5: Notbetrieb ab t=3 mit 1,5 Vorgängen/h, Normalbetrieb t=4 |
| F2 unabhängige Alternative | 6: 4 Aufbau/Test Q, 2 reservierte Umschaltung | Entscheidung t=-5, verfügbar t=-2, Test t=-1 | Erkennung t=2,25, Entscheidung t=2,5, Umschaltung ab t=3 mit 3 Vorgängen/h |

G nutzt im ersten Experiment dokumentierte Vorsorge ohne technisch verfügbaren
Notbetrieb. H hat einen getesteten Q-Pfad wie F2; seine Eingaben und Kosten
bleiben über Fokusvarianten identisch. Alternative Rivalensätze verändern diese
Zuordnung ausdrücklich. Niemand repariert den gemeinsamen Provider durch einen
lokalen Neustart. F1 ist getesteter lokaler Notbetrieb, keine Behauptung über
die Wiederherstellung von P.

Dokumentationsnachweis, technische Verfügbarkeit und erfolgreicher Test besitzen
je eigene Zeit-/Quellenfelder. Dokumentation allein ändert weder Kapazität noch
Erholungszeit. Kosten der Vorbereitung werden t=-5 bezahlt und aufwandwirksam;
die zwei Aktivierungseinheiten werden bei Aktivierung bezahlt, sonst bleiben
sie reserviertes Cash. Reservierter Betrag, Ausgabe und ungebundenes Cash
erscheinen getrennt. F0 gibt nichts aus und spart das gesamte Budget von sechs.
F1/F2 geben ohne Schock jeweils vier aus und reservieren zwei; mit Aktivierung
sind es sechs Ausgaben. Die Cash-Differenz gegenüber F0 ist deshalb ohne Schock
vier, mit Schock sechs, jeweils vor allen übrigen Geschäftszahlungen.
Die verfügbaren sechs Einheiten sind eine identische Entscheidungsgrenze, kein
zusätzlicher Kapitalzufluss. Investitionsentscheidungen vor t=0 werden als
Opening-Reconciliation ausgewiesen; **vor** Investition identische Startbilanz,
danach erklärbare Kostendifferenzen.

## Handprüfung der reinen Prozesswirkung

Zunächst Kundenwechsel ausschalten. `q_end = q_start + arrivals − processed`;
`processed = min(q_start + arrivals, capacity)`. Die Kapazitätstabelle gilt nach
Erkennung/Entscheidung/Umschaltung, noch ohne zufällige Schäden oder Kundenwahl.

| Periode / Uhrzeit | F0 Kapazität / Rückstand Ende | F1 Kapazität / Rückstand Ende | F2 Kapazität / Rückstand Ende |
| --- | --- | --- | --- |
| 1 / [0,1) | 3 / 0 | 3 / 0 | 3 / 0 |
| 2 / [1,2) | 3 / 0 | 3 / 0 | 3 / 0 |
| 3 / [2,3) | 0 / 2 | 0 / 2 | 0 / 2 |
| 4 / [3,4) | 0 / 4 | 1,5 / 2,5 | 3 / 1 |
| 5 / [4,5) | 3 / 3 | 3 / 1,5 | 3 / 0 |
| 6 / [5,6) | 3 / 2 | 3 / 0,5 | 3 / 0 |

Flüssige Mengen sind Expositionsgewichte; eine spätere Ganzzahl-Variante hat
eigene Rundungs- und Tie-Break-Regeln. Im Kontrolllauf ohne E1 sind alle Rückstände
null. Diese Handtabelle prüft den neuen Vertrag, sie ist kein gemessenes IMS-Ergebnis.
Rückstand ist kein automatisch endgültiger Prämienverlust: verzögerter Abschluss,
Kündigung und endgültig verlorener Abschluss sind unterschiedliche Vorgänge.

## Kundenwahl, Risiko, Aufnahmegrenzen und Rivalen

Nach einer beobachteten Wartezeit über eine Stunde wird ein Antrag in der nächsten
Periode neu angeboten. Sein altes Versicherungsverhältnis bleibt bis zur
Annahme wirksam. Wechsel tritt erst am nächsten Periodenanfang ein. Abgelehnte
Anträge bleiben beim alten Haus oder werden ausdrücklich unversichert; kein
erzwungener Wechsel zu F. Aufnahmegrenze zunächst zwei neue Verträge je Periode,
innerhalb der verbleibenden Prozesskapazität. Rückstandsaufholung beansprucht
dieselbe Kapazität. Preisrang, beobachtete Wartezeit, segmentbezogene Annahme und
Tie-Break entscheiden anhand veröffentlichter Regeln; nicht anhand zukünftiger
Ausfall- oder Schadensdaten. Jeder Transfer enthält Herkunft/Ziel, Risiko-ID,
Gültigkeitszeitpunkt und genau eine Prämien-/Schadenzuordnung.

Feste Entscheidungen: vollständige Preis-, Annahme- und Kapazitätstabellen für
G/H festhalten. Feste Reaktionsregeln: identische Regeln und Parameter in jedem
Fokuslauf, **resultierende Entscheidungen dürfen verschieden sein**. Rivalen sehen
öffentliche Preise mit einer Periode Verzögerung, eigene Wartezeit aktuell,
eigene ausgezahlte Schäden verzögert, keine privaten fremden Reserven. Ein
zusätzlicher Kundentransfer darf ihre Regelreaktion auslösen.

Fünf einfache, vor Abnahme zu prüfende Regelvarianten: Preisführerschaft reagiert
auf den verzögerten niedrigsten Preis innerhalb einer Preisuntergrenze;
Margensicherung auf eigene beobachtete Schadenquote; selektives Wachstum auf
Segmentmarge und freien Platz; Rückzug auf ein beobachtetes Verlust-/Service-
Limit; hohe Servicekapazität auf Rückstand, mit Kosten und Umsetzungsvorlauf.
Jede Regel nennt Beobachtung, Schwelle, Entscheidungszeit, Vorlauf, Dauer und
Grenzen. Zunächst keine LLM-gesteuerten Konkurrenten.

Handprüfung der Risikomischung: zwei zusätzliche hohe Risiken bringen bei Preis
4 und Schaden 3 vor anderen Kosten 2 Einheiten Deckungsbeitrag. Bei Schaden 6
sind es −4. Zwei niedrige Risiken mit Schaden 1 bringen 6. Dieselbe Neuaufnahme
kann also je deklarierter Schadensannahme sinnvoll oder nachteilig sein; zusätzliche
Aufnahme bei voll belegter Kapazität kann Rückstand und Kündigungen vergrößern.
Diese Rechnung ist eine Sensitivitätsillustration, kein vorweggenommenes Laufergebnis.

## Experimentvertrag und Buchungen

Erste Matrix: F0/F1/F2 × Schock/kein Schock × feste Entscheidungen/feste Regeln,
also zwölf kontrollierte Läufe; anschließend alternative G/H-Strategien. Danach
Kundenwahl ausschalten/einschalten, verzögertes Verfügbarwerden t=3,5/4,5,
Ausfalldauer 0,5/2/4, Schadenhöhe höheres Risiko 3/4/6/7, Aufnahmegrenze 0/1/2,
Q gemeinsam abhängig/unabhängig sowie Wartezeitschwelle 0,5/1/2 prüfen.

Der erste Handpfad ist deterministisch. Stochastische Erweiterung liefert eine
versionierte Draw-Tabelle, Schlüssel `(seed, actor_id, period, event_id,
purpose, risk_id)`. Das ist ein neuer Vertrag mit eigener Algorithmusversion.
Neue Akteure oder Sortierung dürfen bestehende Werte nicht verschieben;
Namensänderungen der Anzeige verändern keine ID. Gleiche Seeds allein reichen
bei einem globalen fortlaufenden RNG nicht. Alle Varianten teilen die benötigten
Draws, gleiche Prefixe und den vollständigen Ereignisplan. Nur Beobachtung bis
zum jeweiligen Informationszeitpunkt gelangt in Entscheidungen.

| Kanal | Periodische Buchung / Kontrolle |
| --- | --- |
| Versicherung | Verdiente Prämie je aktivem Risiko einmal; Schadenaufwand → Verpflichtung; Zahlung nächste Periode reduziert Cash und Verpflichtung, kein zweiter Aufwand |
| Betrieb | Tatsächliche Bearbeitungs-/Haltekosten einmal; verspätete Prämie in ihrem tatsächlichen Vertragszeitraum; kein zusätzlicher pauschaler ICT-Margenabzug |
| Vorsorge | Vorbereitung und Aktivierung separat; gemeinsame Kosten mit genau einer Eigentümer-/Allokationsregel |
| Cash | Opening + Einzahlungen − Auszahlungen = Closing; reserviertes Cash gesondert; Forderung nicht verfügbarer Zahlungsmittelbestand |
| Bilanz | A = Cash + sonstige Aktiva + Forderungen; A = L + E; Carryover je Haus; Eigenmittel nur als deklarierter Modellwert |
| Markt | 18 Anfangsrisiken = alle versicherten und ausdrücklich unversicherten Risiken; disjunkte Transfers und periodischer Nenner für Marktanteile |

Unverdiente Prämien und längerfristige Verpflichtungen werden im minimalen Fall
durch einstündige Periodenverträge vermieden, ausdrücklich keine reale Policen-
kalibrierung. Sie verlängern sich automatisch beim bisherigen Haus, solange
kein angenommener Wechsel oder ausdrücklich unversicherter Abgang wirksam wird;
der Antragsausfall beendet deshalb nicht automatisch den Versicherungsschutz.
Schlussbericht zeigt ausstehende Zahlungen/Rückstände; ein optionaler
Run-off-Vergleich mit unverändertem Vertrag prüft Horizonteffekte. Keine doppelte
Verlustbuchung zwischen Marktbilanz und ICT-Overlay.

## Auswertung, Nutzenabnahme und Entscheidungstor

Vorstandsblatt: Kosten heute; Mindest-Cash und offene Zahlungen; Ergebnis samt
Endverpflichtungen; Bearbeitung und Wartezeit; Bestand, niedriger/höherer Risikomix,
Marktanteil und unversicherter Rest. Jede Differenz führt über Ereignis → sichtbare
Information → Regel/Entscheidung → Kapazität/Kundenbewegung → Buchung zu Eingaben.
Modellkapital trägt seine Methodik; SCR/MCR bleiben unbesetzt.

Umschaltsignale sind vorab beobachtbar: eigener Rückstand über vier, verfügbare
Kapazität unter erwarteter Aufnahme, Cash unter zehn oder segmentbezogene
beobachtete Deckung unter null. Das sind zu prüfende Workshopgrenzen. Eine
Empfehlung nennt tragende Parameter, spätesten Bereitstellungstermin und
Gegenbeispiele. Der reine Handfall kann Q beim Service besser zeigen; ob der
Mehrwert seine Kosten trägt, bleibt eine wirtschaftliche Auswertung.

Nutzenabnahme: aktuelle ungekoppelte ICT-Rechnung plus einfache Prozess-/Budget-
Tabelle als Vergleich. Der gekoppelte Fall muss mindestens einen erklärbaren
Unterschied in Aufnahme, Risiko, Cash oder sinnvollem Umsteuern zeigen, ohne
ihn vorzugeben. Bei gleichen Regeln und wirkungslosen Parametern muss er auch
keinen Unterschied liefern können. Empfehlungen mit einem günstigen und einem
ungünstigen Parameterfall prüfen; keine Robustheitsbehauptung außerhalb des
untersuchten Raums. AP14 nutzt zusätzliche, bei Auswahl nicht verwendete Pfade.

Mit mindestens drei Einsteigern und einem Wieder-Einsteiger messen: tatsächlich
benötigte Eingabefelder/Quellen, fehlende Daten, aktive Vorbereitungsminuten,
Bedienminuten, Hilfeaufrufe und richtige Erklärung von Kosten, Risiko und
Umschaltpunkt. Aufgaben und Bewertungsrubrik vorher festlegen; Zeitmessung und
Verständlichkeit getrennt ausweisen. Keine ungemessene Laufzeit-/Einfachheitszusage.

**Vor Umsetzung freizugeben:** dieser Mengen-/Zeit-/Buchungsvertrag, Kunden-
Fortbestand bei Wechsel, beobachtbare Rivaleninformationen, Capability-/Fallback-
Nachweise und die Beschränkung auf synthetische Periodenverträge. AP7 muss seine
Markt-/ICT-Brücke zuerst in main nachweisen. Die AP3-Zustimmung ersetzt dieses
Tor nicht. [Erweiterungsplan](ims_board_strategy_2026_10.md) und Manifest führen
AP10 als Vorschlag; der Planungsauftrag implementiert keinen dieser Kanäle.
