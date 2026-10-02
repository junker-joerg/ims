# AP6: Quellenprüfung für den deutschen Markt

Abruf und Prüfung: 02.10.2026. **Recherchebefund, keine bestätigte Top-40-Liste.**
Maschinenlesbare Quellen, Hashes und offene Nachweise:
[Quellenregister](ims_ap6_sources_2026_10.json).
[Methodenvorschlag](../plans/ims_ap6_data_method.md).

| Quelle | Tatsächlich geprüft | Verwendung / Grenze |
| --- | --- | --- |
| [BaFin Erstversicherungsstatistik](https://www.bafin.de/DE/die-bafin/publikationen-daten/statistiken/erstversicherung/erstversicherung_node.html) | Aktuelles Portal direkt per HTTPS erreichbar; Gesamttabellen, Leben, Kranken, Schaden/Unfall 2024 und Hinweise heruntergeladen. | Quelle für Einzelgesellschaften und Prüfumfang; kein vollständiger deutscher Gruppenrang. Ältere Links und der Web-Abruf lieferten 403/404; dieser Zugangsstand ist jetzt teilweise überwunden. |
| BaFin Excel, Blätter 010 / 160 / 460 / 560 | 010 enthält auch gebuchte Beiträge des Gesamtgeschäfts. 160/460/560 sortieren verdiente Bruttobeiträge; Fußnoten schließen übernommene Rückversicherung ein. 160/560 verwenden Mio. Euro, 460 Tsd. Euro. | Summen dieser Rangtabellen sind kein Nachweis für das vorgeschlagene Rankingmaß. Einheiten dürfen nicht ungeprüft addiert werden. |
| [BaFin Hinweise 2024](https://www.bafin.de/SharedDocs/Downloads/DE/Statistik/Erstversicherer/dl_st_24_hinweise_va.pdf?__blob=publicationFile&v=1) | PDF-Seiten 2–3, gedruckte Seiten 1–2, gelesen und gerendert geprüft. | EWR-Unternehmen unter Herkunftsaufsicht und kleine landesbeaufsichtigte VVaGs fehlen im beschriebenen Erhebungskreis. Zweigranglisten 5610–5690 haben eine Veröffentlichungsgrenze; fehlende Zeilen sind keine Nullwerte. |
| [GDV Statistikheft 2026](https://www.gdv.de/resource/blob/215380/7c86eab9b3f0dd744669a41342ff8aaf/statistiken-zur-deutschen-versicherungswirtschaft-2026-pdf-data.pdf) | PDF-Seiten 25/27: I\|20 EWR-Geschäft und I\|22 Konzentration, beide bis 2024; Text und gerenderte Tabellen geprüft. | EWR-Tabelle beschreibt gebuchtes selbst abgeschlossenes Deutschlandgeschäft als Aggregat, ohne Gruppennamen. Konzentration verwendet verdiente Beiträge und größte 5/10/15; keine Ranggrenze 40/41. |
| [KIVI/Assekurata Pressemitteilung vom 23.09.2026](https://www.assekurata-rating.de/wp-content/uploads/2021/09/Assekurata_Pressemitteilung_23_09_2026_Marktanteilstudie_2025.pdf) | Beide PDF-Seiten gelesen und gerendert. Die Mitteilung nennt eine Studie für 2025 mit 68 Anbietern, 263 Einzelgesellschaften und 99,38 % Abdeckung sowie Deutschlandkorrekturen. | Existenz einer aktuellen Studie belegt. Vollständige Tabellen, genauer Nenner und Zuordnung fehlen hier. Die öffentlich-rechtliche Sammelposition erfordert eine gesonderte Konsolidierungsprüfung. Keine Bestellung oder Kontaktaufnahme erfolgt. |
| [Verband öffentlicher Versicherer](https://www.voev.de/oeffentliche-versicherer/) | Primärseite beschreibt regionale Unternehmen, unterschiedliche Träger und Kooperationen. | Ein Verbandsaggregat wird nicht ohne Gruppenprüfung als ein selbständiger Modellanbieter übernommen. |
| [EIOPA Versicherungsregister](https://register.eiopa.europa.eu/registers/register-of-insurance-undertakings) | Öffentlich indexierte Beschreibung: Identität, Länder, grenzüberschreitender Status und Datumsfelder; direkter Registerabruf hier mit Timeout. Keine Exportdatei geprüft. | Mögliche ergänzende Kandidatenquelle, keine Beitragsrangfolge und keine bereits bestätigte Jahresabdeckung. |

Die vollständige KIVI-Ausgabe und Schaden-/Unfall-Sondertabellen sind noch nicht
bereitgestellt. Ihre Nennung bedeutet weder Lizenz-/Nutzungsprüfung noch
Bestätigung des vorgeschlagenen gebuchten Direktgeschäftsmaßes. Das gemeinsame
Datenjahr bleibt ungeklärt. Ein frei zugänglicher Artikel mit wenigen Spitzenrängen
oder eine weltweite Umsatzliste ersetzt die vollständige Primärtabelle nicht.

Die Pressemitteilung nennt 99,38 %; einzelne sekundäre Berichte nennen 98,38 %.
Für den Recherchebefund wurde die Primärangabe erfasst. Der Unterschied und der
tatsächliche Studiennenner müssen an der vollständigen Tabelle geklärt werden;
beide Angaben sind keine schon geprüfte IMS-Marktabdeckung.

Noch nachzuweisen sind vollständiges Kandidatenuniversum, konsolidierte deutsche
Direktbeiträge, gemeinsames Jahr, Gruppen/Töchter, Spartenmix, ausgeschlossene
Zweige und Grenze 40/41. Deshalb bleiben Auswahl, Gewichte und Deutschland-Demo
offen. Vorhandene AP5-Demos rechnen weiterhin synthetische Modellanbieter.

Die Downloads liegen lokal unter `.tmp-pr-ap5/ap6-research/`; ihre exakten URLs,
Größen und Hashes stehen im Register. Die Dokumente wurden nicht verändert und
die kommerzielle Studie nicht als verfügbar ausgegeben. Ein späteres Offline-
Dossier benötigt die konkreten zulässigen Quellenbelege der tatsächlich
verwendeten Daten; der heutige Recherchebefund ersetzt diese Lieferung nicht.
