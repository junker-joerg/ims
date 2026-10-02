# AP6: gekennzeichnete BaFin-Gruppenauswertung mit 40 Modell-VUs

**Aktuelle Umfangsentscheidung:** Der Auftraggeber hat den gekennzeichneten
BaFin-Referenzfall für AP6 ausdrücklich angenommen; [Beleg](../reports/ims_ap6_scope_acceptance.md).
Die nachstehende ursprüngliche Deutschlandprüfung bleibt als Herkunft erhalten.
Die Umsetzung wird mit diesem beschränkten Quellenumfang und sichtbar
bearbeitbaren Workshop-Annahmen im selben PR fortgesetzt.


Begonnen am 02.10.2026 nach dem tatsächlichen AP5-Merge über
[PR #294](https://github.com/junker-joerg/ims/pull/294). Basis ist
`03f87662e85e6081998bab79e32ee12baac52da1`; der Tree entspricht dem geprüften
AP5-Abnahmekommitt. Branch `codex/ims-german-market-top40`; alle Meilensteine
gehören in denselben [Paket-Draft-PR #295](https://github.com/junker-joerg/ims/pull/295).
[AP5-Mergebeleg](../reports/ims_ap5_merge.md).

Der Auftraggeber beauftragte „Fahre mit dem nächsten IMS AP fort“ und erteilte
anschließend die AP5-Abnahme/Mergefreigabe. Das nächste angenommene Paket ist
AP6. Der [archivierte Arbeitsauftrag](ims_ap6_work_order.md) wurde vor Änderung
des AP6-Manifests gegen gefetchtes origin/main im Modus `authorized` erzeugt.
Die dortige Zeit benennt den tatsächlichen AP5-Merge als Eintritt der
Voraussetzung; der genaue Zeitpunkt der ursprünglichen Nachricht ist unbekannt.
Der Auftrag umfasst Umsetzung, keine AP6-Anwenderabnahme oder Mergefreigabe.

## Lieferumfang und Herkunft

Lieferbasis: angenommener [AP4–AP9-Plan](ims_explainable_market_2026_10.md),
Manifest und [Boardplanung](ims_board_strategy_2026_10.md). Der Boardplan ergänzt
AP6 nicht um einen weiteren Modellkanal. R04, R12 und R13 gelten unverändert.

Der Ausgangsfall umfasst genau 40 belegte Versicherungsgruppen nach deutschem
direktem Erstversicherungsgeschäft über alle Sparten. Ausländische Gruppen mit
deutschem Geschäft sind eingeschlossen. Gruppengrenzen, Töchter, Bezugsjahr,
Rankingmaß und Rang 40/41 werden vor Auswahl nachgewiesen. Der nicht simulierte
Rest bleibt sichtbar. Reale Namen und Beitragsgewichte belegen keine tatsächlichen
Strategien, Anfangsbilanzen, Kundenrisiken oder ICT-Abhängigkeiten.

| Meilenstein | Lieferung / Prüfweg | Stand |
| --- | --- | --- |
| M1 Daten- und Methodenprüfung | Quellen-Dossier, gemeinsames Jahr, direkte deutsche gebuchte Bruttobeiträge, Gruppen-/Tochterzuordnung, vollständige Rangbasis und Grenze 40/41. | Gelieferte BaFin-Mappe: 326 Quellwerte und 663 Formeln geprüft, 145 redaktionelle Gruppen und begrenzte 40/41-Grenze nachgerechnet; Deutschlandumfang, Gruppen-Vollprüfung und AP6-Auswahl offen. |
| M2 Daten und Modellabbildung | Editierbare Primärdaten, stabile IDs, genau 40 Gruppen, belegte Sparten und Gewichte, fehlende Werte sowie nicht modellierte Sparten; getrennter Workshop-Vertrag. | Offen; M1-Tor bleibt verbindlich. |
| M3 API, IMS und Export | Offline-Demooriginal, bearbeitbare Übernahme/Import, frische Rechnung, sichtbare Quellen/Annahmen und Einzel-VU-Excel. | Offen; keine Top-40-Demo angekündigt oder freigeschaltet. |
| M4 Prüfung und Lieferung | Deterministische Referenzfälle, aktuelle Browser-/Ressourcenprüfung, Einsteigeranleitung/Glossar, höhere unbenutzte Releasekennung und echter Installer. | Offen; aktuelle Anwenderfassung bleibt alpha.5. |

## Aktuelle Umsetzung des angenommenen Referenzumfangs

Der [Quellen-/Modellvertrag](ims_ap6_reference_mapping.md) konkretisiert die
angenommene Umfangsänderung. M1: alle Originalwerte und Formeln nachgerechnet;
redaktionelle Gruppen-/Umfangsgrenzen bleiben am Fall sichtbar. M2: gepinnter
Offline-Katalog, stabile Identitäten, begründete Overrides, Neusortierung aller
145 Kandidaten, genaue Quellengewichte und disjunkte Reste implementiert.
M3: API-Referenzbündel, schreibfreies Original, eigene Sitzung, Mix-/Override-
Bedienung, frische Läufe und quellengebundener Einzel-VU-Export implementiert.
M4: Handfälle, 40×100-/Prefix-/Bilanzprüfungen und aktuelle Browserfälle begonnen;
HTML-Anleitung und reale Bilder vorhanden. Neue Produktkennung alpha.6 /
Windows 2.0.0.6 gesetzt. Installerprüfung und endgültige Paketabnahme offen.
Die vorausgehende Tabelle beschreibt die ursprüngliche Deutschlandplanung.

## Architektur und Semantik vor Produktänderungen

Die relevanten Altstellen `IMSDATA.C` classBAV/Vuag/Vnag und `IMS.E`
Aggregatbildung sowie das [AP5-Mapping](../migration/ap5_common_market.md) wurden
gelesen. Historische Aktivitätszählungen und Regeldurchschnitte liefern keine
moderne Beitragsrangfolge. AP6 ist eine belegte moderne Szenarioquelle; es ist
keine neue Portierung eines historischen deutschen 40er-Markts.

Der AP5-Kern `ims.market.contract`/`runner` liefert bereits bis 41 Anbieter,
explizite Sparten, Kohorten und reproduzierbare Rechnungen. Er erlaubt nur die
bisherigen erklärten Modellquellen in Modellwährung. Ein künftiger Faktenkatalog
und seine Quellen bleiben getrennt von diesem Rechenvertrag. Die Abbildung muss
Gewichte, Skalierung und Workshop-Annahmen ausdrücklich zeigen; das bloße
Umbenennen des gleichgewichteten AP5-Musters wäre keine AP6-Lieferung.

Leben bleibt im angenommenen AP5-Bestandskanal, Kranken im deklarierten Profil.
Lebens-Nachfrage und Markt-/ICT-Kopplung gehören weiter in AP7. Historische
25er-Validatoren und AP3-Verträge werden durch neue Namen oder IDs nicht erweitert.

## Nächster konkreter Schritt

[Methodenvorschlag](ims_ap6_data_method.md),
[Quellenprüfung](../research/ims_ap6_sources_2026_10.md) und
[Arbeitsstand](../reports/ims_ap6_fortschritt.md) gemeinsam fortsetzen. Eine
vollständige nutzbare Primärtabelle oder Studie muss zuerst auf Deutschland,
Direktgeschäft, Einheit, Rundung und Gruppenaggregation geprüft werden. Die
KIVI-Pressemitteilung belegt die Existenz einer Ausgabe 2025, keine Top-40-Auswahl.
Liegt die vollständige Tabelle nicht vor, die Datenfrage offen halten. Keine
Schätzung ersetzt Rang 40/41 und keine Vollständigkeit aus bekannten Namen ableiten.

Die danach gelieferte BaFin-Top-40-Mappe wurde inzwischen vollständig
nachgerechnet; [Prüfbericht](../reports/ims_ap6_top40_workbook_review.md).
Ihr beschränkter Quellenumfang ist keine angenommene Änderung des AP6-Plans.
Der [vorläufige Referenzfall](ims_ap6_bafin_reference_proposal.md) liegt konkret
zur Entscheidung vor; nach Entscheidung im selben PR fortsetzen.
