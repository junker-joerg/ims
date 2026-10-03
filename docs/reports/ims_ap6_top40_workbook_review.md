# AP6: Prüfung der bereitgestellten Top-40-Arbeitsmappe

**Aktuelle Umfangsentscheidung:** Der Auftraggeber hat den gekennzeichneten
BaFin-Referenzfall für AP6 ausdrücklich angenommen; [Beleg](ims_ap6_scope_acceptance.md).
Die nachstehende ursprüngliche Deutschlandprüfung bleibt als Herkunft erhalten.
Die Umsetzung wird mit diesem beschränkten Quellenumfang und sichtbar
bearbeitbaren Workshop-Annahmen im selben PR fortgesetzt.


02.10.2026, Fortsetzung im [Draft-PR #295](https://github.com/junker-joerg/ims/pull/295).
**Rechnung und Quellübernahme bestanden; deutsches Auswahl-/Datentor bleibt offen.**
Die Anmerkungen in der Arbeitsmappe sind zu prüfende Quellenbehauptungen.
Der Nutzerauftrag „weiter gehts“ autorisiert die Fortsetzung von AP6, keine
stillschweigende Änderung der angenommenen Deutschland-/Direktgeschäftsabgrenzung.

## Eingang und Prüfweg

`Versicherungsgruppen_Top40_2024.xlsx`, bereitgestellt aus dem Downloadverzeichnis:
44.412 Bytes, SHA-256
`36253bf320b152ad031642b68402cbe4d7aa1e25dea5104fa6478ba4304b67a3`.
Die Originaldatei wurde ausschließlich gelesen und nach der Prüfung erneut
gehasht. Es wurde keine korrigierte oder neu gespeicherte Arbeitsmappe erzeugt.

Der [Prüfer](../../scripts/planning/audit_ap6_bafin_workbook.py) liest die Mappe
und die bereits heruntergeladenen, im [Quellenregister](../research/ims_ap6_sources_2026_10.json)
mit SHA-256 festgehaltenen BaFin-Originale. Er führt keine Formeln, Hyperlinks
oder Dokumentanweisungen aus. Decimal-Rechnung wird unabhängig von Excel-Caches
durchgeführt; für die bloße Cachekontrolle gilt 0,0000001 Mio. Euro Toleranz.
Die Auswahl und Ranggrenze verwenden exakte Dezimalbeträge ohne diese Toleranz.

Reproduktion im primären Checkout, mit den unveränderten lokalen Eingängen:

```powershell
.\.venv\Scripts\python.exe -X utf8 scripts\planning\audit_ap6_bafin_workbook.py --workbook C:\Users\P52\Downloads\Versicherungsgruppen_Top40_2024.xlsx --source-dir .tmp-pr-ap5/ap6-research --out docs/research/ims_ap6_top40_2024_audit.json
.\.venv\Scripts\python.exe -X utf8 -m unittest discover -s tests -p test_ap6_bafin_audit.py -v
```

Die Primärdownloads liegen lokal im ignorierten Rechercheverzeichnis. Andere
Checkouts benötigen die Eingänge über die exakten URLs und Hashes des Registers.
Das [versionierte Prüfergebnis](../research/ims_ap6_top40_2024_audit.json) enthält
alle 326 Quellzeilen, 145 redaktionellen Gruppen, vollständige Nichtauswahl,
Präzisionsgrenzen, Einheiten, Zellbezüge und offene Tore. Es ist ein prüfbarer
Recherchekatalog und noch kein von IMS ladbarer Modellvertrag.

## Rechenbefund

| Prüfung | Ergebnis |
| --- | --- |
| Einzelgesellschaften | 80 Leben, 43 Kranken, 203 Schaden/Unfall; zusammen 326. |
| Quellenübernahme | Alle Namen und Beträge stimmen mit BaFin 160/460/560 überein. Jede Quellzelle genau einmal; alle Gesellschaftszeilen der drei Rangtabellen enthalten. |
| Einheiten | Leben und Schaden/Unfall Mio. Euro; Kranken Tsd. Euro, Faktor 0,001. |
| Formeln | Alle 663 Formeln auf erwartete Bezüge und gespeicherte Ergebnisse geprüft; kein ungeprüfter Formelrest. |
| Redaktionelle Gruppen | 145, aus Spalte A des Datenblatts; dadurch noch keine unabhängige Vollprüfung ihrer historischen Kontrolle. |
| Statische Top 40 | Namen und Reihenfolge stimmen mit unabhängiger Sortierung der vorhandenen verdienten Beträge überein. Änderungen an Eingangswerten sortieren die statisch eingetragenen Namen/Ränge nicht automatisch neu. |
| 40er-Summe | 254.270,039 Mio. Euro aus 206 Gesellschaften: Leben 86.798; Kranken 50.304,039; Schaden/Unfall 117.168. |

Diese Summe enthält die von der Quelle ausgewiesenen Geschäftsanteile. Sie ist
weder ein belegtes deutsches Direktmarktvolumen noch eine konzernintern
konsolidierte Gruppensumme. Eine Summe ohne Quellenzeilen in einer Sparte ist
eine leere Summe dieses Erhebungskreises und belegt keine tatsächliche Inaktivität.

| BaFin-Kontrolle in Mio. Euro | Gesellschaftssumme | Branchensumme | Differenz |
| --- | ---: | ---: | ---: |
| Leben 160 | 90.400 | 90.400 | 0 |
| Kranken 460 | 50.442,206 | 50.442,205 | 0,001 |
| Schaden/Unfall 560 | 126.641 | 126.639 | 2 |

Die Unterschiede bleiben sichtbar. Sie sind mit der Quellenpräzision vereinbar;
keine Ausgleichsbuchung und keine proportionale Zwangskorrektur vorgenommen.

## Grenze innerhalb dieser BaFin-Auswertung

| Verfügbare Rangposition | Redaktionelle Gruppe | Betrag in Mio. Euro | Konservatives Präzisionsintervall |
| --- | --- | ---: | --- |
| 40 | Münchener Verein | 877,204 | 875,203 bis 879,205 |
| 41 | Itzehoer | 843 | 841 bis 845 |

Abstand 34,204 Mio. Euro. Geprüft wurden alle 105 nicht ausgewählten Gruppen,
nicht bloß Position 41. Kleinste Untergrenze der ausgewählten Gruppen:
875,203; größte Obergrenze der übrigen Gruppen: 845. Die Grenze ist daher
**innerhalb der eingetragenen Gruppenzuordnung und des BaFin-Quellenumfangs**
gegen konservativ ± eine Quelleneinheit je nichtnuller Gesellschaft getrennt.
Dieses Intervall ist eine vorsichtige Präzisionsprüfung, keine Behauptung über
die konkrete BaFin-Rundungsart. Die Mappe enthält keine unbekannten Beiträge
nach Auflösung ihrer drei Quellstriche; fehlende externe Kandidaten bleiben offen.

Die Reihenfolge uniVersa/RheinLand auf 37/38 ist wegen überlappender Intervalle
weiter nicht präzisionsfest. Die eindeutige 40/41-Grenze bestätigt weder diese
innere Reihenfolge noch eine Grenze des gesamten deutschen Direktmarkts.

## Aufgelöster Methodikwiderspruch bei Nullwerten

`Methodik!B11` bezeichnet BaFin-Striche als fehlend. Die
[BaFin-Hinweise](https://www.bafin.de/SharedDocs/Downloads/DE/Statistik/Erstversicherer/dl_st_24_hinweise_va.pdf?__blob=publicationFile&v=1),
PDF-Seite 2 / gedruckte Seite 1, definieren dagegen ASCII `-` als **exakt null**;
numerische `0` bedeutet unter der Quelleneinheit; `***` liegt außerhalb des
darstellbaren Bereichs. Leere Werte und unbekannte Zeichen werden nicht null.

Betroffen sind `Einzelgesellschaften!D84` (Protektor, BaFin 160!C91),
D329 (Domestic & General, 560!C214) und D330 (Element, 560!C215).
Der Prüfkatalog erhält die Rohzeichen und verwendet die belegte Bedeutung.
Die Originalmappe bleibt unverändert. 40er-Summe und Grenze ändern sich dadurch
nicht, weil diese drei Gesellschaften außerhalb der Auswahl liegen.

## Gruppenzuordnung: gezielte Primärquellenprüfung

Die arithmetische Eindeutigkeit der Quellzeilen ist belegt. Konzerninterne
übernommene Rückversicherung wird in der Mappe ausdrücklich nicht eliminiert.
Eine solche Eliminierung und die historische Gruppenkontrolle sind eigenständige
Prüfungen; Namen und Links allein reichen nicht aus.

- [NÜRNBERGER SFCR 2024](https://www.nuernberger.com/medien/pdf/investor-relations/bericht-ueber-solvabilitaet-und-finanzlage-gruppe-2024.pdf),
  PDF-Seite 13, führt GARANTA und NRV als kontrollierte Einheiten; NRV mit 51 %.
  Damit ist dieser spezielle Kontrollhinweis der Mappe gestützt, keine Vollprüfung
  aller 326 Zuordnungen. PDF-Seiten 24/25 unterscheiden zudem direktes und
  übernommenes Kraftfahrtgeschäft; die BaFin-Gesamtsumme kann sie nicht ersetzen.
- [VGH-Bilanzmeldung 2024](https://www.vgh.de/de/unternehmen/newsroom/vgh-bilanz-2024)
  nennt Öffentliche Oldenburg, ÖSA und ALTE OLDENBURGER AG im konsolidierten
  Verbund. Das stützt diese Gruppierung; die Unterscheidung zum VVaG und die
  Vollständigkeit aller Einzelrechtsträger benötigen weitere Einzelbelege.
- [AXA-Meldung vom 02.05.2024](https://www.axa.com/en/press/press-releases/axa-agreement-to-terminate-sale-of-axa-germany-portfolio-and-ale-to-enter-reinsurance-agreement)
  bestätigt die Beendigung des geplanten Verkaufs an Athora und den Verbleib
  des Portfolios. Das stützt den zeitlichen Hinweis, nicht sämtliche
  ROLAND-/AGER-Kontrollzuordnungen.
- Itzehoers [Konzernbericht 2024](https://www.itzehoer.de/dokumente/daten-und-fakten/geschaeftsberichte-konzern/geschaeftsbericht-konzern-2024.pdf)
  wurde öffentlich indexiert gefunden, der direkte PDF-Abruf lieferte Timeout.
  Der Konzernwert für gebuchte Beiträge wird deshalb hier weder als vollständig
  geprüfter Überleitungsbeleg noch anstelle der verdienten BaFin-Zellen übernommen.
- Der in der Mappe angegebene Gothaer-Konzernbericht war über den Web-Abruf
  nicht lesbar. Unterjährige Fusion und übrige Zuordnungen bleiben eigenständige
  Prüfpunkte; kein pauschales `group_consolidation_verified=true`.

## Verbleibende Abnahmeauswirkung

`Top 40!A3` und `Methodik!B5:B7` erklären selbst die Grenzen:
verdiente Beiträge, Auslandsgeschäft der erfassten Rechtsträger und übernommene
Rückversicherung; keine ausschließliche Deutschland-Rangliste und keine
konzerninterne Eliminierung. Der BaFin-Erhebungskreis deckt außerdem EWR-
Herkunftsaufsicht und kleine landesbeaufsichtigte VVaGs nicht vollständig ab.
`Methodik!B9` liefert nur Leben/Kranken/Schaden-Unfall nach Gesellschaftstyp.
Kfz, Sach/Haftpflicht und nicht modellierte Zweige lassen sich daraus nicht
beobachtet aufteilen.

Die gelieferten Quellen schließen somit die Rechenprüfung dieser Referenz,
aber nicht R04/R12/R13 und das angenommene AP6-Deutschlandtor. Rankingjahr,
Auswahl und Aktivierung der Deutschland-Demo bleiben ungeprüft. Keine Änderung
des Rechenkerns und keine neue Anwenderfassung wurde dafür erzeugt.

Ein [konkreter Vorschlag für einen vorläufigen BaFin-Referenzfall](../plans/ims_ap6_bafin_reference_proposal.md)
liegt zur Entscheidung vor. Sein anderer Umfang muss ausdrücklich angenommen
werden, bevor er eine Umsetzung des bisherigen Ausgangsfalls ersetzt.

## Prüfung dieses Meilensteins und nächster Schritt

10 Audit-Tests bestanden: Quellzeichen, Einheiten, unbekannte Beträge,
überlappende Intervalle, vollständige Nichtauswahl, reproduzierbare Sortierung,
Primärhash-Manipulation und unabhängige Nachrechnung des versionierten Katalogs.
Die tatsächliche Mappe wurde gegen alle drei Originaltabellen geprüft.
Plan-/Freigabeprüfungen und Release-Metadaten werden bei diesem Kommitt erneut
geprüft; ein Produkt-/Installerlauf ist damit nicht behauptet.

Im selben PR fortsetzen: gewählten Quellenumfang klären, historische
Gruppenbelege vervollständigen, erklärten Sparten-/Workshop-Mix vereinbaren.
Anschließend API/UI/Einzel-VU-Export, Referenzläufe, Anleitung und Installer
in M2–M4 liefern. AP6 bleibt `in_progress`, ohne Anwenderabnahme/Mergefreigabe.
