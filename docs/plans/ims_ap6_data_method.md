# AP6: Vorschlag für Daten- und Auswahlmethode

Stand 02.10.2026. **Methodenvorschlag, keine nachgewiesene Auswahl oder
fachliche Abnahme.** [Umsetzungsplan](ims_ap6_implementation.md) und
[Quellen-Dossier](../research/ims_ap6_sources_2026_10.md).
Das angenommene AP6-Tor verlangt eine vollständige Rangbasis. Es ist noch offen.

## Auswahlmaß, Jahr und Gruppen

Das vorgeschlagene Ranking verwendet **gebuchte Bruttobeiträge des selbst
abgeschlossenen deutschen Erstversicherungsgeschäfts über alle Sparten**,
vor abgegebener Rückversicherung, in einer gemeinsamen Währung und Einheit.
Weltweite Konzernzahlen, IFRS-17-Umsatz, verdiente Beiträge und übernommene
Rückversicherung sind andere Größen. Abweichende Quellmaße bleiben als solche
erhalten; ohne belegte Überleitung fließen sie nicht in dieses Ranking ein.

2025 ist durch die veröffentlichte KIVI-Studienankündigung ein Datenkandidat.
Ob es das jüngste vollständige gemeinsame Jahr ist, ist nicht nachgewiesen.
Die derzeit tatsächlich geprüften BaFin-Tabellen betreffen 2024; das GDV-Heft
2026 enthält für EWR-Geschäft und Konzentration ebenfalls Daten bis 2024.
Ein Rückfall auf 2024 wird erst nach Prüfung einer vollständigen vergleichbaren
Basis begründet. `ranking_year` bleibt bis dahin leer. Eine Änderung des
Rankingmaßes würde vor Auswahl mit Abnahmeauswirkung erklärt.

Als Konsolidierungsregel wird vorgeschlagen: Gruppenbestand zum 31.12. des
gemeinsamen Datenjahrs; die Jahreswerte der zugeordneten Rechtsträger werden
genau einmal summiert. Das ist bei unterjährigen Übernahmen gegebenenfalls eine
abgeleitete Stichtagsaggregation und keine behauptete Konzernberichtszahl.
Solche Fälle bekommen Überleitung und Quellen. Selbständige regionale öffentliche
Gruppen werden einzeln geprüft; der Verbandswert ist kein zusätzlicher Anbieter.
VVaG-Verbund, Gemeinschaftsunternehmen und abweichende Berichtskreise benötigen
eine belegte konkrete Zuordnung, keine automatische Aufteilung nach Beteiligungsquote.

Muttergesellschaft mit konsolidierter Summe und ihre bereits darin enthaltenen
Töchter dürfen nicht addiert werden. Ausländische Gruppen, deutsche Töchter,
Niederlassungen und deutsches Dienstleistungsgeschäft werden auf derselben
Deutschlandbasis erfasst. Rechtsträger-/Niederlassungskennung, Quellenumfang und
Gruppenkennung verhindern, dass dieselben Beiträge zweimal eingehen.
Ein Versicherungsgruppenname ist getrennt von Modell-ID und Anzeigename.
IDs bleiben bei einer Änderung der Rangposition erhalten.

Pensionskassen/-fonds, Sterbekassen, Sicherungsunternehmen und sonstige
Quellkategorien werden mit begründetem Ein-/Ausschluss geführt. Die Abgrenzung
zwischen Erstversicherung und institutioneller Altersversorgung darf nicht
allein durch die Gliederung einer Statistik festgelegt werden.

## Primärdaten und prüfbare Auswahl

Jeder verwendete Wert benötigt Quell-ID, Bezugsjahr, Tabelle/Blatt/Zelle oder
PDF-Seite, Quellmaß, geografischen Umfang, Direkt-/Rückversicherungsumfang,
Einheit, Abrufdatum und Präzision. Betrag und Aussageklasse bleiben zusammen:
beobachtet, aus belegten Werten abgeleitet, Workshop-Annahme oder unbekannt.
Abgeleitete Werte bekommen Eingänge und Rechenregel. Quellenwidersprüche
werden dokumentiert und gelöst; das höhere oder passendere Ergebnis wird nicht
stillschweigend ausgewählt. Fehlend ist kein Nullbetrag; ein erwiesener Nullwert
braucht einen Nachweis. Quelldatei-Hash und Quellen-/Datenversionsstand gehören
zum späteren reproduzierbaren Nachweis.

Vor Auswahl ist das Kandidatenuniversum einschließlich nicht ausgewählter
Gruppen zu prüfen. BaFin-Bundes-/Landesaufsicht, EWR-Niederlassungen und
Dienstleistungsverkehr dürfen nicht unbemerkt fehlen. Ein aktuelles Register
belegt weder Beiträge noch automatisch den Bestand des historischen Datenjahrs.
Jeder Ausschluss benötigt Beleg; fehlende Werte in potenziell großen Gruppen
halten das Tor offen.

Sortierung: exakter vergleichbarer Jahresbetrag absteigend. Bei einem belegten
echten Gleichstand wird als Vorschlag die stabile Gruppen-ID aufsteigend verwendet
und der Gleichstand sichtbar ausgewiesen. Quellenrundung und unbekannte Werte
sind keine echten Gleichstände. Die Ranggrenze enthält Rang 40, Rang 41, Differenz,
Quellenpräzision und offene Kandidaten. Überschneiden sich belastbare
Betragsintervalle, ist die Grenze nicht nachgewiesen. Genau 40 ausgewählte Namen
allein erfüllen diese Prüfung nicht.

## Kleine Handfälle der vorgeschlagenen Regeln

Alle folgenden Gruppen und Zahlen sind **fiktiv**, Beträge in Mio. Euro.
Sie erklären die Prüfung, sind kein Test einer bereits implementierten AP6-Pipeline.

| Fall | Quellen / Rechnung | Konsequenz |
| --- | --- | --- |
| Tochterkonsolidierung | Gruppe A berichtet konsolidiert 100; enthaltene A1 70 und A2 30. | 70 + 30 = 100; zusätzlich 100 ergäbe die unzulässige Doppelzählung 200. |
| Deutschlandabgrenzung | A deutsches Direktgeschäft 100; B weltweite Beiträge 700, belegtes deutsches Direktgeschäft 90. | A liegt vor B; 700 ist kein deutscher Rankingbetrag. |
| Ranggrenze offen | Rangkandidat 40: 100; Kandidat 41: 99; weiterer ungeklärter Kandidat: belastbares Intervall 98–102. | Keine geprüfte Grenze, weil der weitere Kandidat 100 überschreiten kann. |
| Nicht simulierte Sparte | Kfz 40, Sach/Haftpflicht 30, Leben 20, Kranken erwiesen 0, sonstige direkte Zweige 10. | Ranking 100; modellierte Teilmenge 90; Rest 10 bleibt außerhalb der vier Modellsparten sichtbar. |

## Gewichte, Rest und Abbildung in den Modellmarkt

Alle Erstversicherungssparten zählen für die Auswahl. Die Modellsparten sind
weiter `motor`, `property_liability`, `life`, `health`. Rechtsschutz, Unfall,
Transport, Kredit/Kaution oder Assistance werden nicht pauschal Sach/Haftpflicht
zugeschlagen. Für jeden Quellzweig gibt es eine erklärte Abbildung oder den
ausgewiesenen Status nicht modelliert. Fehlender Spartenmix bleibt unbekannt.

Für Gruppen-/Spartenbeitragsgewichte müssen die verwendeten Summen und Nenner
nachrechenbar sein. Ein Anteil am ausgewählten 40er-Beitragsvolumen ist ein
anderer Nenner als der gesamte deutsche Markt oder die simulierte Teilmenge.
Der Rest enthält getrennt Geschäft nicht ausgewählter Gruppen und nicht
simulierte Zweige ausgewählter Gruppen; dieselben Beiträge dürfen nicht in beide
Restkomponenten fallen. Die Quellabdeckung wird gesondert genannt.

Beitragsgewichte sind keine Vertragszahlen, Kundenzahlen oder Risiken. Erst die
erklärte Szenarioabbildung legt Modellmengen, Preise, Anfangsbilanzen und
Skalierung in Modellwährung fest. Diese bleiben Workshop-Annahmen. Ein späterer
Simulationsanteil wird aus dem Modelllauf berechnet und darf vom beobachteten
Ausgangs-Beitragsanteil abweichen. Ohne diese Trennung gäbe es eine stille
Kalibrierungsbehauptung. Tatsächliche Firmenstrategien und Cloud-Abhängigkeiten
werden durch Namen oder Quellengewichte nicht belegt.

## Offenes Tor und anschließende Abnahme

Noch benötigt: vollständige nutzbare Rangtabelle mit Tochterdaten und
Deutschland-/Direktgeschäftsabgrenzung, gemeinsames Jahr, belegter Spartenmix,
Nichtauswahl und überprüfbare Grenze 40/41. Die KIVI-Ausgabe 2025 ist ein
Quellenkandidat; ihre Verbandsaggregation und tatsächliche Abdeckung sind vor
Übernahme zu prüfen. Alternativ kann eine vollständig belegte Primärdatenbasis
aus Geschäfts-/SFCR-Berichten aufgebaut werden. Die bisherigen öffentlichen
Quellen alleine schließen das Tor nicht.

Nach bestandener Datenprüfung: editierbarer Faktenkatalog, offline ladbares
Demooriginal und bearbeitbare Übernahme, frische API-/IMS-Rechnung,
quellengebundener Einzel-VU-Excel-Export, nachvollziehbare Gewichte und Rest,
deterministische Tests, Anleitung und aktuelle Installerprüfung im selben PR.
