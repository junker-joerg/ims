# Deutsche Marktdaten und Modellannahmen verstehen

Aktualitätshinweis 06.10.2026: Der folgende Text dokumentiert seinen datierten Fach-/Testpaketstand. Aktuelle Menüwege und das gemeinsame Marktexperiment stehen in der [AP8-Anleitung](market_ap8.md). Ältere Begrenzungen sind auf ihren damaligen Modellpfad bezogen, keine Aussage gegen heute vorhandene AP5-/AP7-Marktkanäle. Der gelieferte BaFin-Fall ist in [BaFin-Referenzfall AP6](market_ap6.html) erklärt; die deutschen Direktmarkt-Datentore bleiben offen.

**Arbeitsfassung für AP6, Stand 02.10.2026.** Die aktuelle Anwenderfassung
alpha.5 lädt die erklärten synthetischen AP5-Märkte. Der deutsche Top-40-Fall
befindet sich in der Datenprüfung und ist noch nicht ausgeliefert.

Eine Versicherungsgruppe kann mehrere Gesellschaften enthalten. Für die
Marktauswahl zählen ihre deutschen direkten Versicherungsbeiträge insgesamt
einmal. Beispiel: Eine konsolidierte Gruppenzahl von 100 und darin enthaltene
Tochterzahlen 70 und 30 ergeben weiter 100. Eine zusätzliche Addition der
Gruppenzahl würde denselben Beitrag doppelt zählen.

Der Ort des Konzerns sagt noch nichts über den geografischen Umfang einer
Beitragszahl. Ein ausländischer Konzern kann deutsches Geschäft betreiben;
ein deutscher Konzern kann viel Auslandsgeschäft haben. Die Auswahl braucht
für beide dieselbe Deutschland-Abgrenzung und dasselbe Datenjahr.

Beitragsanteile brauchen einen genannten Nenner. Anteil am gesamten deutschen
Markt, Anteil an den ausgewählten 40 Gruppen und Anteil an den simulierten
Sparten sind unterschiedliche Aussagen. Nicht ausgewählte Anbieter und nicht
simulierte Zweige müssen sichtbar bleiben. Ein unbekannter Betrag wird als
unbekannt gezeigt; er ist kein belegter Nullwert.

Eine Rangliste nach beobachteten Jahresbeiträgen liefert noch keine Zahl der
Kunden oder ihrer Risiken. Für einen Workshop müssen Modellmengen, Preise,
Anfangsbilanzen und Strategien gesondert erklärt werden. Die spätere Simulation
berechnet eigene Marktanteile und Ergebnisse. Ein Firmenname belegt keine
tatsächliche Strategie und keinen Cloud-Anbieter.

**Quellenstand:** Das [Dossier](../research/ims_ap6_sources_2026_10.md)
erklärt die aktuell geprüften Statistiken. Gemeinsames Jahr, vollständige
Gruppenrangfolge, Spartenmix und Grenze 40/41 sind noch offen. Erst eine
überprüfbare Auswahl wird zum ladbaren Deutschland-Fall. Diese Arbeitsfassung
ist noch nicht als neue installierte Offline-Anleitung geprüft.

Die inzwischen gelieferte Tabelle lässt sich vollständig nachrechnen. Sie
beschreibt aber Beiträge der erfassten BaFin-Gesellschaften einschließlich
Ausland und übernommener Rückversicherung. Verdient heißt: dem Geschäftsjahr
zugerechnet; gebucht bezeichnet eine andere Beitragsgröße. Das kann zu anderen
Rängen führen. Eine gute Rechenprüfung ersetzt die Prüfung dieser Abgrenzung
nicht. Der [Prüfbericht](../reports/ims_ap6_top40_workbook_review.md) erklärt,
welche Aussagen die Tabelle trägt und welche weitere Belege benötigen.
