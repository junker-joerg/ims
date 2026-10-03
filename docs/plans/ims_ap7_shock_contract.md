# AP7: angenommener Vertrag für vier Schockfälle und die begrenzte Kopplung

03.10.2026. **Fachlich ausdrücklich angenommen; Produktumsetzung läuft.**
[Wörtlicher Annahmebeleg](../reports/ims_ap7_contract_acceptance.md).
AP7 ist nach tatsächlichem AP6-Merge zur Umsetzung beauftragt.
Die Lebens-Nachfrage- und ICT-Zeit-/Buchungstore sind angenommen.
AP6s angenommener BaFin-Referenzumfang bleibt Ausgangsquelle; Firmennamen
begründen keine tatsächlichen Strategien oder Providerbeziehungen.

[Umsetzungsauftrag und Meilensteine](ims_ap7_implementation.md),
[Herkunft](../migration/ap7_shock_contract.md) und
[wirklich ausgeführte Kern-/Handproben](../reports/ims_ap7_contract_probes.json).

## Vier Lieferfälle in einem Paket

| Fall | Gemeinsamer Schock | Variante / sichtbare Reaktion |
| --- | --- | --- |
| Google kommt in die Kfz-Versicherung | Ausdrücklich fiktiver Anbieter 41, aktiv ab P21, Preis 2,4, deklarierte Reichweite und Kapazität. | Ausgewählte Modell-VU antwortet mit Preis 2,1 statt 3; Kosten und Vorlauf ausdrücklich. Werbung wird Aufwand, keine unbelegte Werbeelastizität. |
| LV wird unattraktiv | Attraktivitätsfaktor für neue Interessenten von 1 auf 0,25 ab P21. | Deklarierte Vertriebsmaßnahme erhöht ihn auf 0,5; alte Policen und Garantien bleiben erhalten. |
| Regulierungsschock ICT DORA 2.0 | Hypothetisches Umstellungs-/Kosten- und Kapazitätsfenster P21–P30. | Vorbereitete zusätzliche Kapazität bzw. Ersatzpfad mit eigenen Kosten und Aktivierungszeit. Keine reale neue DORA-Vorschrift behauptet. |
| Alle US-Hyperscaler fallen aus | Alle im Szenario ausdrücklich als US-kontrolliert deklarierten synthetischen Provider fallen ab P21 für 36 Stunden aus. | Tatsächlich unabhängiger deklarierter Q-Pfad; ein Ersatz mit demselben ausgefallenen IAM/DNS/Schlüsselpfad bleibt wirkungslos. |

Alle vier Fälle: 100 Modellperioden, schreibfreies Original, eigene bearbeitbare
Übernahme, frische Rechnung, wiederaufnehmbares JSON, Quellenbindung,
Einzel-VU-Excel, CIO-/COO-/CSO-Erklärpfade und Anleitung im selben Draft-PR.
Neue Produktfassung erst nach Implementierung und Prüfungen; während M1 bleibt
das ausgelieferte Produkt alpha.6. Der separate Drei-VU-Vorstandsfall und seine
weiteren Rivalen-/Cash-/Informationsverträge bleiben AP10 vorbehalten.

## Vergleich und gemeinsame Anfangsperioden

Standardvergleich: **derselbe Schock ohne Gegenmaßnahme** gegen **denselben
Schock mit Gegenmaßnahme**. Alternativ wählbar: kein Schock gegen Schock;
beide Achsen werden benannt. Eine No-shock-Kontrolle entfernt nur das Ereignis,
keine bereits beschlossenen Vorsorgekosten. Keine vorgegebene Siegerstrategie.

P1–P5 sind in Baseline und Variante identisch; der anfängliche AP6-Preisbeispiel-
Variantenwechsel wird beim ausdrücklich abgeleiteten AP7-Fall ersetzt. Die
AP6-Quelle selbst bleibt erhalten. Neue Workshopkanäle beginnen frühestens P6.
Vorgeschlagene Maßnahmenentscheidung P16, vier Perioden Vorlauf, verfügbar ab
P20; Schock P21. Termine, Intensität und Kosten sind editierbare Annahmen.
Planentscheidungen sind keine Prognose; reaktive Regeln sehen nur erlaubte
eigene/öffentliche Informationen bis zum erklärten Entscheidungszeitpunkt.

## E07-01: gemeinsame Ereignishülle

Eigene neue Hülle `ims.market-shock-bundle.v1`, getrennt von den unveränderten
AP3-/AP5-/AP6-Eingangsversionen. Enthalten sind Referenzquelle, synthetische
Ergänzungen, Ereignisfolge, Reaktionen, Kopplungsparameter und Vergleichsmodus.
Jedes Ereignis hat stabile ID, Typ, Beginn, Dauer, Intensität, Zielakteure,
Wirkungskanäle und Annahmen-/Quellenhinweis. Einzelereignis und Sequenz verwenden
denselben Vertrag. Zeitfenster sind halboffen; Wirkung am exakten Ende entfällt.

Gleichzeitige Kapazitätsausfälle derselben Ressource werden nicht addiert;
größter Verlustanteil begrenzt ihre Kapazität auf 0–1. Verschiedene wirtschaftliche
Kosten benötigen verschiedene eindeutige Buchungs-IDs. Keine doppelte Zahlung
desselben Providerereignisses über mehrere Abhängigkeitspfade.

Bestehende AP5-Draws bleiben unverändert. Zusätzliche Zufallskanäle erhalten
eigene Version und Schlüssel aus Seed, stabiler Akteur-/Kunden-ID, Periode,
Ereignis-ID und Zweck; dieselben benötigten Draws gelten für beide Seiten.
Anzeigenamen, Sortierung und ein neuer Anbieter verschieben keine alten Draws.
Der vorgeschlagene erste Lebens-Nachfragekanal ist ausdrücklich deterministisch.

## Anbieter 41 und Nichtleben

Google ist ein fiktiver Modellanbieter außerhalb des BaFin-Katalogs, kein
recherchierter 41. Rang. Separate stabile ID und Gruppe. Bis P20 registriert,
aber nicht angebots-/kundenaktiv; Anfangsaktiva, -reserve und -eigenkapital null.
Bei Eintritt einmalige ausdrücklich externe Kapitalzuführung 100.000
Modellwährung, kein Prämienertrag. Ab P21 Preis 2,4, Werbeaufwand 2 je Periode,
Aufnahmekapazität 25 % der deklarierten Kfz-Kohortenmenge. Alle Zahlen angenommen.

Die deklarierte Reichweite bestimmt, welche Kohorten überhaupt wählen dürfen.
Die bestehende günstigste-zulässige-Angebotslogik und Ganzkohortenaufnahme bleiben
kartiert. Werbung wird gebucht; ein Reichweiten-/Nachfrageeffekt entsteht nur
durch einen ausdrücklich benannten Parameter, nicht aus dem Werbeetikett.
Die Gegenmaßnahme hat Kosten 100 einmal in P16 und Preis 2,1 ab P21; sie hält
die deklarierte Aufnahmekapazität der antwortenden VU ein.

Bestehender Kern-Handfall mit drei registrierten Anbietern: Bis P20 bleiben
Prämie und Kapital des neuen Hauses null. P21: externe Einzahlung 1.000 +
Prämie 10 − bezahlter Schaden 8 = Aktiva/Eigenkapital 1.002. Eine Preisantwort
mit Prämie 5 übernimmt denselben Schaden 8; ein billigeres Angebot ist keine
Gewinngarantie. AP5 zählt den registrierten dritten Anbieter schon vor Eintritt
als aktiv. AP7 muss daher ein eigenes geprüftes Aktivierungsmerkmal liefern;
die kleine Bestandsprobe ist noch keine fertige Eintritts-Demo.

Ein beantragter Wechsel in den gekoppelten Fällen bleibt bis zur Bearbeitung
beim bisherigen Versicherer. Prämie und Risiko werden nie zwei Häusern
gleichzeitig zugeordnet. Der alte AP5-Direktwechselvertrag bleibt unverändert;
die neue Warteschlangenfassung wird mit eigenem Herkunftsbezug ausgewiesen.

## Neues, begrenztes Lebens-Neugeschäft

Ein ausdrücklich synthetischer Interessentenpool: zunächst vier potenzielle
Neupolicen pro Modellperiode für den gesamten Markt ab P6, nicht vier je VU.
Attraktivitätsfaktor a liegt zwischen 0 und 1. Kaufwillige Anträge = floor(Pool × a).
Im Handfall: a=1 → 4, Schock a=0,25 → 1, Vertriebsantwort a=0,5 → 2.
Nicht kaufwillige Interessenten, nicht zulässige Angebote und Warteschlange
werden getrennt ausgewiesen; sie sind keine verkauften Policen.

Wahl unter deklarierten aktiven Lebensangeboten nach niedrigster angenommener
Prämie, Gleichstand nach stabiler VU-ID; explizite Annahmekapazität. Im Ausgangs-
profil Prämie 3, Garantiezuführung 2, Verlängerungsprämie 3/Garantiezuführung 2,
Laufzeit zehn Modellperioden und Garantiesatz 0,001 je Periode. Ablaufleistung
entspricht der dann fälligen deklarierten Garantie; Neupolicen haben zunächst
keine Todesfälle. Das ist ein begrenztes Produktprofil, keine reale Tarifierung.
Fremde Altpolicen behalten ihre eigenen Quellen, Garantien, Todes-/Ablauftermine.

Nach tatsächlicher Antragsbearbeitung wird die Police zum nächsten Periodenbeginn
ausgegeben. Neue Prämie, Garantie und Verlängerung erscheinen erst im gültigen
Vertragszeitraum. Ein geringer Attraktivitätswert löscht keine Altpolice und
erzeugt weder Storno noch Rückkauf. Neue policenbezogene IDs bleiben stabil.
Bestehender `life_period_chain`-/Policenbilanzkern wird wiederverwendet;
AP5 lehnt sein bisher unzulässiges Neugeschäft weiterhin ab.

Handprobe des bestehenden Kerns, keine implementierte Nachfrage: Der vorhandene
Zwei-Perioden-Fall mit deklarierter Neupolice hat P1 A=104, L=54, E=50 und
P2 A=33, L=0, E=33. Ohne diese Neupolice bleiben die alten Todesleistungen 65
und alten Ablaufleistungen 25/60 erhalten; P1 94=46+48, P2 35=0+35.
Weniger Neugeschäft ist also nicht automatisch in jedem Horizont wirtschaftlich
schlechter. Keine Erfolgsbehauptung aus der Nachfragemenge allein.

## Physische ICT-Zeit und fachliche Kopplung

Default: eine Modellperiode umfasst **24 deklarierte Prozessstunden**.
Pp = [(p−1)×24,p×24); P21 beginnt bei Stunde 480. Dies ist eine Workshop-
Abbildung, kein historisches Kalenderjahr oder empirischer Zeitmaßstab.
Bestehende Finanzraten bleiben ausdrücklich Raten je Modellperiode.

Schock- und Maßnahmenkanten werden in der physischen Zeit aufgeteilt. Original-
vorgänge kommen vor Nacharbeit; FIFO mit stabiler Vorgangs-ID. Identische Personal-
oder Plattformkapazität darf nicht vierfach in vier Prozessqueues ausgegeben
werden. Deklarierte Ressourcenbudgets und Eigentümer begrenzen alle Prozesse.

Der erste gekoppelte Kanal ist **Antrag/Vertragswechsel**: verfügbare Sales-/
Underwriting-Ressourcen bearbeiten eindeutige Lebens-Neuanträge und Nichtleben-
Wechselanträge. Abschluss bis Ende Pp gilt ab Pp+1. Beim wartenden Wechsel
bleibt bestehender Schutz einschließlich Risiko beim alten Haus. Ein neuer
Antrag bleibt unversichert, bis eine Police gültig wird. Aktuellen Schockzeitraum
zu kennen erlaubt keine Verwendung späterer Schadenswerte bei der Kundenwahl.

Claims-/Service-Queues dürfen deklarierte Verwaltungsarbeit und echte Betriebs-
kosten ausweisen; **sie verschieben in dieser Lieferung keine Todes-/Ablaufleistung
oder Versicherungs-Schadenzahlung**. Dafür wäre ein weiterer Leistungs-/Fälligkeits-
vertrag nötig. Der begrenzte Kanal ist am Ergebnis sichtbar; keine vermeintliche
Schadenregulierungsverzögerung aus einer administrativen Queue abgeleitet.

## Buchung genau einmal

Die gekoppelte Marktbilanz ist alleinige finanzielle Rechnung. Kein exogener
ICT-Baseline-Gewinn und kein pauschaler `operational_impact` werden zusätzlich
über die bereits berechneten Versicherungsflüsse gelegt.

- Versicherung: tatsächliche Prämie und Risiko-/Garantiezuordnung pro gültigem
  Vertrag. Ausstehender Antrag ist weder Forderung noch verdiente Prämie.
- Aufholung: später bearbeitete Anträge können später Geschäft auslösen.
  Ausstehende Vorgänge am Horizont bleiben sichtbar; temporäre Differenz ist
  kein automatischer endgültiger Verlust.
- Betrieb: deklarierte Personal-/Halte-/Nacharbeitskosten als tatsächlicher
  Aufwand einmal in VU und Sparte. Gleiche Ausgangskosten auch ohne Schock.
- Vorsorge: Entscheidungskosten einmal; Betriebs-/Aktivierungskosten im
  tatsächlichen Fenster. Bei No-shock-Kontrolle bleiben beschlossene Kosten.
- Geteilte Providerkosten: eindeutige Kosten-ID und explizite Gewichtssumme 1;
  vierstellige Rundung mit Rest beim letzten stabil sortierten Kostenträger.
  Drei Gewichte 0,3333/0,3333/0,3334 teilen 6 in 1,9998/1,9998/2,0004, Summe 6.
- Kontrolle: A=L+E, Carryover, Markt=VU-Summe und disjunkte Gruppen; kein zweiter
  ICT-Margenabzug für bereits fehlende Versicherungsprämie.

Unabhängiger Stunden-Handfall: zwölf neue Anträge in sechs Stunden, Kapazität
drei/h, Ausfall Stunden [2,4). Ohne Schock: zehn bis Horizont ausgegebene Policen,
zwei bearbeitet für die nächste Periode, kein Rückstand. Mit Schock: sieben
ausgegeben, drei bearbeitet für die nächste Periode, zwei noch in der Queue.
12=10+2=7+3+2. Bei Erstprämie 3 sind 9 am Horizont noch nicht verdiente Prämie;
kein zusätzlicher ICT-Margenverlust von 9. Der Stunden-Handfall ist keine der
vier angekündigten fertigen 100er-Demos.

## Ersatzpfad und Datenherkunft

Ein Fallback nennt einen konkreten Ersatzpfad mit vollständigem transitivem
IAM-/DNS-/Schlüssel-/Daten-/Netzbezug und erklärter verfügbarer Kapazität.
Der Ersatz wirkt nur, wenn sein Pfad verfügbar ist und das Aktivierungsfenster
gilt. Ein lokaler Restart repariert keinen fremden gemeinsamen Provider.
Ein unbekannter Kontroll- oder Abhängigkeitswert wird nicht als Unabhängigkeit
ausgegeben. EU-Standort allein ist kein Unabhängigkeitsbeweis.

Der bestehende ICT-Kern setzt einen skalaren Kapazitätswert nach der Abhängigkeits-
auswertung. Die Bestandsprobe bearbeitet damit 240 statt 0 Vorgänge trotz
beibehaltener ausgefallener Plattformabhängigkeit. Das ist seine deklarierte
Semantik, kein Beweis eines unabhängigen Ersatzpfads. AP7 benötigt dafür eine
eigene graphbasierte Erweiterung; alte AP3-Fälle bleiben Regressionen.

DORA 2.0 ist ein hypothetischer Workshopname. Quellenregister und geprüfte
DORA-Benchmark-PDF bleiben als Herkunft; Umstellungsaufwand, Kapazität und
Providerprofile sind angenommene Szenariodaten. Befragungsquoten werden nicht
zu Ausfallwahrscheinlichkeiten oder Modellwirkungen umgerechnet. Keine SCR-/MCR-
oder Compliance-Aussage. Dokumentiert/verfügbar/getestet darf nicht vermischt
werden; der größere Capability-/Budget-/Rivalenversuch gehört weiter AP10.

## Grenzen und zu liefernde Prüfungen

Default vier, maximal 20 potenzielle Lebensanträge im Gesamtmarkt je Periode;
Neupolicenlaufzeit zunächst zehn, höchstens 20 Modellperioden. Zusätzlich bis
41 registrierte Anbieter, 200 Nichtleben-Kohorten und 100 Perioden. Bestehende
Input-/Ergebnisbudgets bleiben bestehen; tatsächliche vier 100er-Läufe werden
vor Freigabe gemessen, größere Eingaben scheitern atomar statt mit Teilergebnissen.

M2/M3 müssen Handfälle für aktive VU-Zählung und Finanzierung, Garantien,
Antrags-/Risikoerhaltung, Stunden-/Periodengrenzen, gemeinsame Kosten,
Abhängigkeiten und No-shock-Kosten liefern; dann vier echte vollständige Läufe,
Prefixe/Draws, API/UI/Excel-Digests und eigene Sitzung prüfen. M4 liefert
aktuelle Bilder, Anfängeranleitung, höhere eindeutige Releasekennung und den
tatsächlichen installierten Windows-Produktlauf. M1-Proben ersetzen dies nicht.

## Entscheidung

Zur Annahme stehen der deterministische Lebens-Neugeschäftskanal mit erhaltenen
Altgarantien, die 24-Stunden-Abbildung, der wirksame Antrags-/Wechselkanal,
einmalige Kostenbuchung und die Prüfung konkreter Ersatzpfade. Die begrenzte
Claims-/Service-Kopplung ist ausdrücklich Teil der Abnahmeauswirkung.
Der Auftraggeber hat diesen Umfang ausdrücklich angenommen; zusätzlich müssen
die ICT-Schocks sehr gut sichtbar und erklärbar werden. Der Erklärpfad zeigt
Ereignis → Provider/Abhängigkeit → Prozesskapazität/Rückstand → Vertragswirkung
→ einmalige Buchung, mit exakten Werten pro Periode und VU auf beiden Seiten.
Annahme autorisiert ihre AP7-Umsetzung im selben Paket-PR, keinen Merge,
kein öffentliches Release und kein AP8–AP14-Paket.

## Konkrete sichtbare Standardannahmen der Umsetzung

Die administrative Arbeit wird je VU der Modellsparte mit den größten
deklarierten Anfangsaktiva zugeordnet. Gemeinsame Ressourcen-, Provider- und
Bereitschaftskosten folgen expliziten vierstelligen Gewichten nach dieser
Anfangsbasis, Gewichtskorrektur beim größten Träger. Jede Zahlung wird stabil
auf vier Stellen gerundet, der letzte Kostenträger erhält den Rest; ein früher
Anteil wird auf den verbleibenden Betrag begrenzt, damit Kleinstzahlungen
keinen negativen Rest erzeugen. Kein Sparten-Funding oder zusätzliche
Finanzierung wird eingeführt. Alle Angaben stehen im portablen Bündel, in
Oberfläche, Export und Anleitung; eigene Einstellungen können abweichende
zulässige Gewichte deklarieren.

Ein gemeinsamer Ressourcenpfad hat genau einen erklärten Maßnahmenbezug und
alle Kostenträger als Zielakteure. Personal-Kapazität gilt auf dem verfügbaren
Primär-/Ersatzpfad unabhängig von der Listenreihenfolge; überlappende
Personal-Faktoren werden mangels zusätzlichen Budgetvertrags abgewiesen.
Providerereignisse benennen alle eingebundenen Akteure, konkrete Betroffenheit
folgt transitiv aus dem Graphen. Positiver Ereignisaufwand verlangt den
ausdrücklichen Kostenkanal. Eintritt ist Aktivierung mit Intensität 1.
