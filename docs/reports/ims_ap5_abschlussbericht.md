# AP5 – gemeinsamer Markt und auswertbare Strategiefamilien

Stand 02.10.2026. Umsetzung in [PR #294](https://github.com/junker-joerg/ims/pull/294),
Branch `codex/ims-market-strategy-groups`, Anwenderkennung **2.0.0-alpha.5**,
Windows-Dateiversion **2.0.0.5**. Technisch geprüft und vom Auftraggeber
abgenommen; Merge ausdrücklich freigegeben. Alle vier erforderlichen CI-Checks
für endgültigen Produkthead `417a0ca` bestehen; [Prüfprotokoll](ims_ap5_verification.json).
AP5 ist nach vier grünen Checks am Abnahmekommitt 525916c über PR #294 nach main
übernommen (`03f87662e85e6081998bab79e32ee12baac52da1`); Tree identisch.
[Mergebeleg](ims_ap5_merge.md). Die nachfolgende Produktabnahme ist im
[Abnahmebeleg](ims_ap5_user_acceptance.md) getrennt von der Vertragsannahme dokumentiert.

## Auftrag und fachliche Annahme

AP4 wurde nach bestätigter Anwenderabnahme über PR #293 nach main übernommen:
`9b0d45a22be4314eda8e9ab1db61c506a44160f7`, am 02.10.2026 um 10:49:21 Uhr
Europe/Berlin. Erst danach wurde AP5 begonnen. Der Paketauftrag wurde vor
Änderungen am Paketmanifest mit dem authorized-Generator gegen diese tatsächlich
gefetche main-Basis geprüft; [archivierter Auftrag](../plans/ims_ap5_work_order.md).

Der Auftraggeber nahm den konkreten Mehr-VU-/Risiko-/Gruppenvertrag aus
Vorschlagscommit `0a21cf8f6718a4b1188da92587a820058ca7c0a3` ausdrücklich mit
**„Vertrag annehmen und umsetzen“** an. [Annahmebeleg](ims_ap5_contract_acceptance.md)
und [Marktvertrag](../plans/ims_ap5_market_contract.md) halten den Umfang fest.
E05-01/E05-02 aus dem separat angenommenen Boardplan #292 sind eigene
Abnahmen: Maßnahmenkosten mit Vorlauf/Dauer und Information ohne Zukunftswissen.
Kein AP5-Merge/Public-Release oder AP6–AP14-Auftrag wird daraus abgeleitet.

## Was Anwender jetzt tun können

In **Simulation → Markt und Familien** oder über den Link in der Übersicht
werden vollständig erklärte synthetische Fälle geladen und frisch berechnet:

| Fall | Zweck | Nachvollziehbares Ergebnis |
| --- | --- | --- |
| Wechsel mit Altreserve | Zwei VUs, Kundenwechsel und bleibende Altreserve | P6: A=172, L=15, E=157; 172=15+157. |
| Kapazität und unversicherte Nachfrage | Drei VUs, ganze Kohorten, Preisgleichstand und Aufnahmelimit | P6: Markt E=315, gedeckt 14, unversichert 5; Risiko 20=13+7. |
| Synthetischer Modellmarkt | 40/41 gemeinsam bilanzierte VUs, vier Sparten, bis 100 Perioden | Alle VU-Zeilen, Markt-/Familien-/Gruppensummen und Baseline/Variante im selben Lauf. |

Ergebnisperiode, Variante, Sparte und Gruppe filtern die abgeschlossene Rechnung.
Eigenkapitalverlauf, genaue Verlaufstabelle, Familiendarstellung, Bilanz-/
Aufwandstabelle und Kunden-/Risikobuchung bleiben in IMS. Die globale
Marktsumme und der Inhaltsnachweis bleiben bei Gruppenfiltern sichtbar.
CEO und Vertrieb haben direkte Einstiege; Rollen-/Navigationswechsel erhalten
die Sitzung und führen keine zusätzliche Rechnung aus.

Kfz-Familien können für eine VU ab Periode 6 bis zu einem einschließlich
geltenden Ende übernommen werden. Der Aufnahmeeditor erklärt Kosten,
Vorlauf und Wirkdauer. Übernehmen entwertet das alte Ergebnis; erst erneute
Prüfung erzeugt gültige Werte und Exporte. Eine noch nicht übernommene
Editorwahl bleibt ein Entwurf. Ungültige Gesamtläufe zeigen keine Teilbilanz.

**Einzel-VU in Excel** enthält die ausgewählte VU für Baseline/Variante,
ihre Kundenbuchungen und vollständige Quellherkunft. Die geprüften Dezimaltexte
erhalten vier Stellen und große Werte. **Marktquelle als JSON sichern** und
**Marktdatei öffnen** erlauben frische Wiederrechnung mit demselben Nachweis.
Die Exporte verlangen denselben aktuellen `If-Match`-Nachweis; geänderte
Quellen können keinen alten Export erzeugen.

## Rechnung und Modellgrenzen

Der eigene Eingang `ims.modern-market.v1` und das Ergebnis
`ims.modern-market-result.v1` sind getrennt vom unveränderten AP3-Vertrag.
Alle aktiven VUs werden gemeinsam über die Perioden geführt. Kundengruppen
haben eine stabile Kennung, Menge und ausdrücklich deklarierte Risiken.
Bei Wechsel folgt die neue Prämie und das künftige Risiko dem neuen Träger;
bereits gebuchte unbezahlte Schäden bleiben Verbindlichkeiten des alten Trägers.
Neue Zahlungen und erklärte Altzahlungen werden getrennt nachgewiesen.

Ganze homogene Kohorten werden in stabiler Gruppenreihenfolge aufgenommen.
Günstigstes zulässiges Angebot und bei Preisgleichstand kleinere VU-ID;
fehlende Kapazität führt zum nächsten geeigneten Anbieter. Nicht aufnehmbare
Nachfrage und ihre Schäden bleiben außerhalb der VU-Bilanzen sichtbar.
Keine Teilung, optimale Marktallokation oder implizite Ersatzversicherung.

Vier Gruppenbegriffe sind getrennt: eindeutige Versicherungsgruppe,
überlappende VU-Vergleichsgruppe, VN-Kundengruppe und disjunkte ausführbare
Strategiefamilie je VU/Sparte/Periode. Im Kapazitätsfall ergeben die gemeinsamen
Festpreisfamilien **215+100=315**. Peers VU1/VU2 und VU2/VU3 ergeben 215/212;
deren Addition würde VU2 doppelt zählen. Alle Geldsummen stimmen mit den
VU-Zeilen überein. Expositionen und Policenzahlen verschiedener Sparten
werden nicht zu einer erfundenen Gesamtmenge oder einem Mischpreis addiert.
Innerhalb einer Sparte ist der Preis gebuchte Prämie / tatsächlich gedeckte
Menge; bei Menge null ist er undefiniert.

Maßnahmenkosten werden einmal in der Entscheidungsperiode gebucht.
Vorlauf 2 und Dauer 3 ab Entscheidung P6 wirken in P8–P10; ab P11 gilt
wieder das Grundprofil. Vorlauf null wirkt vor der Kundenwahl derselben
Periode. Überlappende widersprüchliche Parameter werden zurückgewiesen.
VU-Information reicht höchstens bis zur abgeschlossenen Vorperiode;
Kunden sehen aktuelle öffentliche Angebote vor der Risikobuchung.
Zukünftige Schäden ändern die frühere Wahl nicht. Zufallswerte sind an
Seed, Akteur, Periode und Kanal gebunden; VU41 verschiebt keine vorhandenen
Angebotsziehungen. Tatsächlich neue Konkurrenz darf Zuordnungen verändern.

Leben führt vorhandene geschlossene Policenbestände mit erklärtem Anlagesatz;
Kranken verwendet vorhandene Preis-/Bestands-/Leistungskanäle. Die vorhandenen
Ketten werden je moderner VU isoliert mit lokaler Rechen-ID1 verwendet.
Stabile moderne IDs und vollständige Ursprungsquellen bleiben außen erhalten.
Die historischen 25er-Validatoren wurden nicht pauschal erweitert.

Kein deutscher Top-40-Datenfall, keine neue Lebens-Nachfrage, keine vier neuen
Schock-Demos oder Markt-/ICT-Kopplung sind enthalten. Diese benötigen die
späteren Paket-/Vertragstore. Ebenso keine dynamische Insolvenz, Querverrechnung
zwischen Sparten, SCR/MCR oder vollständige historische Gleichheit.
Die erhaltene DORA-PDF schließt die dokumentierte Zugangslücke; sie ist keine
AP5-Ausfall-/Schadenkalibrierung und keine AP13-Abnahme.

## Technische Herkunft und Ressourcen

`ims.market.contract` prüft den eigenen Eingang; `runner` führt gemeinsame
Phasen, Risikoledger, Bilanzen und Summen aus; `presets`, `export` und
`transport` stellen vollständige Fälle, Einzel-VU-Excel und verlustlose
Tabellenübertragung bereit. `ims.api.market` ist in beiden vorhandenen
Backendpfaden angeschlossen; `MarketWorkbench` zeigt dieselben geprüften Zeilen.
[C-/Python-Mapping](../migration/ap5_common_market.md): IMS.E Vrvu01/Vrvn06
über vorhandene Kerne, ESS.C/IMSDATA.C als Zustands-/Perioden-/Aggregatherkunft.
Die neue Buchung/Kapazität ist der ausdrücklich angenommene moderne Vertrag.

Die API benennt Spalten je Tabelle einmal (`ims.market-row-table.v1`).
Fehlende Felder und vorhandene Nullwerte bleiben unterscheidbar; der
verlustlose Transport wird gegen das semantische Ergebnis getestet.
Der Inhaltsnachweis umfasst dessen Quellen und Zeilen. Identische vorhandene
Lebens-/Krankenverträge werden nur innerhalb einer Rechnung memoisiert;
abweichende Bestände, Parameter oder Kosten erhalten eigene Rechnungen.

| Vollständiger Produktlauf | 40 VUs | 41 VUs |
| --- | ---: | ---: |
| Perioden / Sparten | 100 / 4 | 100 / 4 |
| VU-Zeilen je Vergleichsseite | 16.000 | 16.400 |
| Kundenentscheidungen je Seite | 8.000 | 8.200 |
| Eingang, UTF-8-Bytes | 4.351.336 | 4.460.047 |
| API-Antwort einschließlich beider Seiten, Bytes | 35.369.741 | 36.239.738 |
| Erste lokale Laufzeit | 15,6959 s | 16,1241 s |
| Wiederholung parallel zu Gesamtprüfungen | 20,1721 s | 22,6788 s |

Beide Messreihen haben identische Inhaltsdigests. Dies sind vollständige
Produktläufe; der ältere 0,18-s-Angebotskernversuch bleibt ein eigener
Vorversuch. Reproduzierbar über `scripts/planning/probe_ap5_market.py --out DATEI.json`.
Grenzen: Eingang 16 MiB, vollständige Antwort 48 MiB, 41 VUs, 200 Nichtleben-
Kohorten, unterstützte Horizonte bis 100, begrenzte weitere Listen und
vorhandene Policenverträge, ein gleichzeitiger Marktauftrag. Eine frühere
32-MiB-Grenze scheiterte am vollständigen Markt; Wiederholungen von Feldnamen
wurden reduziert und das Budget anhand echter Messungen festgelegt.
Noch größere erklärte Quellen scheitern atomar, ohne gekürztes Teilergebnis.

## Prüfungen und Lieferung

| Prüfung | Tatsächliches Ergebnis |
| --- | --- |
| AP5-Modell/API | 16 bestanden in 50,64 s nach gemeinsamer Festpreisfamilie: Handfälle, Risikoerhaltung, Altreserve, Rundung, A=L+E, Carryover, Prefix/Replay, Information, Maßnahmen, 40/41×100, Adapter, Transport, Desktopanschluss, Export und AP3-Regression. |
| Gesamte lokale Pythonregression während Umsetzung | 2.715 Tests und 14 Untertests bestanden in 1.319,74 s; bekannter Starlette-Testclient-Hinweis. Die letzte Handfall-Familienpräzisierung ist separat oben geprüft und Teil des nachfolgenden CI-Laufs. |
| Gesamte lokale Browserregression | 50/50 bestanden in 871,06 s: AP2-/AP3-/AP4-Bestandsfälle und zehn neue AP5-Fälle. |
| Letzter AP5-Browserlauf | 10/10 in 57,14 s nach Familienpräzisierung und ergänzter Offlinebildprüfung. |
| Sechs AP5-Ansichten | Desktop 1440×900, Tablet 1024×768, Mobil 390×844; jeweils hell/dunkel. Axe ohne Verstöße, Textkontrast ≥4,5:1, kein Seitenoverflow, Tastaturzugriff auf Tabellen. |
| Gebündelte Anwendung | Echter Frozen-Start ohne Python/Node im PATH, gesperrtes externes Netzwerk, isolierter Datenpfad mit Leerzeichen/Umlauten; Markt-Handfall, ausgewählte VU-Datei und Offlinehilfe/Bild bestanden. Dies ist kein Installer-Lifecycle-Test. |
| Lokaler tatsächlicher Installer | Erster sauberer Produktbuild `1611937`: 19.945.343 Bytes, 81,35 s, SHA-256 `f4bfd55363b871fa1dd26bffc76f41a0965a09c071a341e46752632ad5fb5f60`; historischer erster Build vor Familienpräzisierung; aktuelle CI-Lieferung separat nachgewiesen. |
| Windows-CI-Release-Gate | 2.715 Tests und 14 Untertests in 944,03 s; anschließendes vollständiges Release-Gate-Skript status ok. Historisches Produktionskorpus bleibt erwartungsgemäß blocked; kein historischer Produktionsfreigabeanspruch. |
| Tatsächlicher Windows-CI-Installer | 14 Lifecycle-Prüfungen in 643,58 s bestanden, einschließlich 50/50 Browserfällen gegen die installierte Anwendung in 616,24 s. |
| CI-Installer-Binary | Sauberer PR-Mergecommit `a51f70d0142d90609003360e37812e8ef71b1695`, 19.912.844 Bytes, 55,73 s, SHA-256 `533ac083ccfff3f538ba24d89a1e09c0d92dcc6d53e8605419af517952a39ceb`. Heruntergeladen und gegen Hash/Größe geprüft. |
| Erforderliche Checks | Plan, Browser, Windows-Release-Gate und Installer für Produkthead `04617fb` erfolgreich. Finale Dokumentation/Bildprüfung folgt im selben PR; aktueller Checkstand dort sichtbar. |

Der CI-Lifecycle verwendet einen synthetischen alpha.0-Vorgängerinstaller mit
demselben alpha.5-Bundle. Er prüft Update-/Datenmechanik, keinen echten
alpha.4→alpha.5-Binarywechsel. Der CI-Rechner enthält Entwicklertools; PATH
ist für das Executable auf System32 beschränkt. Eine unabhängige Abnahme
auf Windows 11 ohne Entwicklertools ist weiterhin ausstehend.

Auch der anschließende Dokumentationsstand `a7b007c` hat alle vier
erforderlichen Checks bestanden. Der frisch daraus gebaute lokale Installer
hat 19.946.759 Bytes und SHA-256
`4f20c53fa467e4855cc910a17df91147a8737f32a3e5b776af378562bfb8bf6c`.
Ein zusätzlicher Frozen-Lauf mit frischem Datenordner bestätigt beide
Handfälle, die Einzel-VU-Datei und die Offlinehilfe. Ein vorheriger Lauf mit
wiederverwendetem Testordner hatte einen Verbindungsreset; im Laufzeitprotokoll
war keine Backend-Ausnahme zu sehen. Eine Ursache ist nicht nachgewiesen.
Der letzte Bedienungsabgleich korrigiert außerdem die deaktivierte
Anbieterauswahl: Zwei-/Drei-VU-Handfälle zeigen jetzt ihre tatsächliche
Anbieterzahl. Quelle und Rechnung verwendeten bereits die korrekte Anzahl.
Alle zehn AP5-Browserfälle einschließlich dieser Anzeigeprüfung sind lokal
in 62,45 Sekunden bestanden; TypeScript und der Produktbuild ebenfalls.
Der endgültige Installer und die Checks dieser kleinen Anzeigeänderung
werden im selben PR mit Commit und Hash nachgewiesen.

Der Installer ist unsigned; Produktfassung und Wiederholungen bleiben über
Commit, Windows-Dateiversion und SHA-256 nachvollziehbar. Die bestehende lokale
IMS-Startmenügruppe enthält fünf Verknüpfungen. Der Installer-Lifecycle wird
im getrennten CI-Testkonto geprüft; bestehende Nutzerverknüpfungen werden
nicht überschrieben, um eine Abnahme zu erzwingen.

[Einsteigeranleitung](../handbook/market_ap5.md), die offline mitgelieferte
HTML-Fassung und echte neue Bildschirmbilder führen durch den Fünf-Minuten-
Handfall, Gruppenvergleich, 40er-Markt, Maßnahmen, Dateien und Grenzen.
[Arbeitsstand](ims_ap5_fortschritt.md) bewahrt frühe Vorversuche getrennt.
Der Auftraggeber bestätigt anschließend am 02.10.2026 die allgemeine
AP5-Anwenderabnahme und erteilt die ausdrückliche Mergefreigabe. Konkrete
Rechner-/Testdauer-/Updateangaben fehlen weiterhin. AP6 wurde nach dem
tatsächlichen AP5-Merge gemäß Fortsetzungsauftrag im eigenen Branch begonnen;
seine Daten-/Methodentore sind offen. AP7–AP14 bleiben offen.
Evernote bleibt bis zu verfügbarem Plugin/angemeldeter Websitzung ausstehend;
der In-app Browser zeigte beim letzten Zugriff die Loginseite.
