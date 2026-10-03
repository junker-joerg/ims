# AP8: sechs Ansichten technisch fertig; frühere Prüfstände

03.10.2026. AP7 wurde tatsächlich nach main übernommen:
`32ba3112d994f57f33e64e1bc318e7d095223cd0`, [Mergebeleg](ims_ap7_merge.md).
Alle vier Checks am Abnahmekommitt f440f4c bestanden, Merge-Tree identisch.
Danach AP8-authorized-Auftrag gegen frisch gefetchtes origin/main erzeugt,
bevor der AP8-Status geändert wurde. Branch `codex/ims-market-visualizations`.

M1: [Plan](../plans/ims_ap8_implementation.md),
[Darstellungsvertrag](../plans/ims_ap8_view_contract.md),
[Herkunft/Mapping](../migration/ap8_market_explorer.md). Die separat angenommene
E08-01 ist mit Herkunft/Abnahmeauswirkung einbezogen. Keine neue Finanzlogik:
sechs Ansichten aus bestehenden geprüften Rechnungen, genaue Nenner/Gewichte,
wirksame Wechsel, Rückstand und konkrete Buchung. Exakte Addition ist keine
isolierte Kausalzerlegung; gemeinsame Mechanismen/Korrelation werden benannt.

Vorbereitende tatsächliche Beobachtungen vorhandener Kerne: Zwei-VU-/10er-
Wechselfall erfüllt alle VU-/Marktsummen und Buchungsbrücken, Eingang unverändert.
AP7-US-25er-Fall: 6.800 VU-/Sparten-/Periodenzeilen beider Seiten erfüllen Ergebnis-
und Eigenkapitalidentitäten ohne Rest (9,188 s), Quellen unverändert. Dies sind
vorhandene Kernbeobachtungen, keine AP8-Produktfälle, sechs fertigen Ansichten
oder alpha.8-Anwendung. Unabhängige Gewichtungs-/HHI-Handwerte stehen im Vertrag.

M2 implementiert: reine Projektion `ims.market-explorer-result.v1`, frische API
`/api/market/explore` unter derselben Rechensperre, unveränderter Modellnachweis,
eigener Ansichtsnachweis, vollständige 40-MiB-Grenze. Acht unabhängige Tests
prüfen 90/10-Gewichte/HHI, Null-/negative Basis, halbe gerade Rundung,
Mehrsparten-VU, tatsächliche Wechsel, Reinheit, dynamische Mitglieder,
einmalige Kosten, frische Exportbindung und gemeinsamen Rechenausschluss.
AP8/AP5/AP7 zusammen lokal: **39 bestanden**, eine bestehende Starlette-Warnung.
Echte AP8-US-25er-Projektion: **6.946.163 Bytes** vollständiger Wire-Response.

M3 implementiert: sechs verbundene Ansichten, gemeinsame lokale Filter,
Fokus/Rivalen/Modellmarkt, aktuelle Familien, wirksame Wechsel, Zeitfenster,
konkrete Providerpfade/Jobs/Buchungen, JSON/Einzel-VU-Excel. Erste echte
1440×900-Hell-Browserprüfung bestanden (20,4 s Test, 25,6 s Sitzung),
Tastatur/Filter/ICT und Axe-Kontrast geprüft. Eine zunächst uneindeutige
Label-Zuordnung der neuen Auswahlfelder wurde explizit berichtigt; diese
fehlgeschlagene Vorprüfung ist keine erfolgreiche Abnahme.

M4 in Arbeit: gemeinsame Produktfassung **2.0.0-alpha.8**, Windows **2.0.0.8**;
Frontend-Build bestanden, bestehender Größenhinweis. Offline-Anleitung und
Ressourcenanbindung vorhanden; aktuelle Browserbilder und sämtliche vier echten
100er-Fälle werden geprüft. Danach eingefrorener Produktkommitt, vier echte
CI-Prüfungen und tatsächlicher Windows-Installer mit installierten Browserläufen.
Noch keine Behauptung eines fertigen alpha.8-Installers oder bestandener
vollständiger Produkt-CI. AP8 in_progress, technisch nicht fertig,
keine Anwenderabnahme/Mergefreigabe/Veröffentlichung. Kein AP9–AP14-Auftrag.

## Produktstand vor der echten CI-Prüfung

03.10.2026, 13:01 UTC: vollständige lokale Python-Suite **2.763 bestanden,
14 Subtests bestanden**, eine bestehende Warnung, **1.282,57 s**. Danach reine
Darstellung verbessert: breite Ergebnis-/Positions-/Zeitlinientabellen,
ausdrücklich undefinierte Balken/Leerzustände und sichtbare Quellenreste in
Mio. EUR getrennt von Modellwährung. Die Simulationskerne bleiben unverändert.

Alle vier echten 100er-Fälle mit unverändertem übernommenem AP7-Modell-Digest
und exakt gleichem 25er-Prefix lokal bestanden. Der erste Gesamt-AP8-Browserlauf
hatte zwölf bestandene Tests und ein noch nicht erzeugtes Anleitungsbild (404).
Die vollständigen zwölf Bilder sind inzwischen vorhanden. Nach Layoutkorrektur
acht echte Tests in einem Lauf bestanden (5,1 min): US-100, BaFin/Offline-Hilfe
und alle sechs Hell-/Dunkel-Größen. Abschließend drei gezielte Tests bestanden
(13,5 s): unabhängige Handwerte, Wechsel/Leerzustände/JSON/Excel und BaFin-
Quellenreste/Offline-Hilfe. Dies sind getrennte Iterationsbelege, kein behaupteter
fehlerfreier 13er-Gesamtlauf. Die vollständige neue CI-Suite umfasst 83 Browser-
prüfungen einschließlich bisheriger Pakete; ihr Erfolg ist noch offen.

Zwölf tatsächliche Bilder: sechs Ansichten aus dem 100er-US-Fall und sechs
1440×900/1024×768/390×844-Hell-/Dunkelbilder. Sichtprüfung von Providergraph,
Pfadnachweis und vollständig lesbarer Fokus-/Rivalen-/Modellmarkttabelle.
Die aktuelle [Offline-Anleitung](../handbook/market_ap8.md) ist im Ressourcen-
manifest zugelassen und von der Oberfläche sowie Installerhilfe erreichbar.
Frontend-Build und gemeinsame Versionsmetadaten bestanden; alpha.8 / 2.0.0.8.
Browser-CI-Zeitbudget 60 min, Installer 70 min, installierter Harness 60 min,
für die zusätzlich gemessenen vier 100er-/Prefixläufe und Darstellungsprüfungen.
Keine Tests übersprungen oder automatische Testwiederholung aktiviert.

## Abschließende Korrektur der Risikoanzeige

Vor technischer Fertigstellung fiel eine missverständliche Wechselspalte auf:
`customer_decisions.risk_loss` bezeichnet den gesamten Kohortenschaden,
auch wenn `insurer_id=null` und `uninsured_loss` denselben Schaden klassifiziert.
Die VU-Bücher hatten diesen Betrag korrekt nicht als Versicherungsaufwand
gebucht. Die Oberfläche trennt nun **beim VU gebuchten Risikoaufwand** und
**unversicherten Schaden ohne VU-Buchung**; beide Rohfelder werden nicht addiert.
Konkreter vorhandener AP5-Handfall: Kapazitäten beider VUs ab P6 gleich null,
G1 bleibt mit 40 Schaden unversichert; VU-Risikoaufwand exakt 0, unversichert 40.
Neun AP8-Tests bestanden (2,53 s); aktualisierter echter Browser-Handfall samt
JSON/Excel, Quellenresten/Offline-Hilfe und unabhängigen Handwerten bestanden
(drei Tests in 13,8 s). Kein Finanz-, Risiko-, Nachfrage-, Garantie- oder RNG-Kern
geändert.

Der frühere Produktpunkt 815ed86 hatte erfolgreiche Plan- und Release-Gate-
Prüfung (2.763 + 14 Subtests, 1.060,95 s), noch laufende Browser-/Installer-
Prüfungen und einen lokalen echten Installer mit drei erfolgreichen direkten
Frozen-App-Prüfungen. Diese Belege ersetzen keine Prüfung der korrigierten
Oberfläche. Neuer eingefrorener Produktpunkt und vollständige vier CI-Prüfungen
folgen im selben PR. Die Suite enthält jetzt **2.764 Python-Tests + 14 Subtests**
und **83 echte Browserprüfungen**; Erfolg am neuen Punkt noch offen.

## Vollständige CI: veraltete Release-Erwartungen berichtigt

Produktpunkt `23e493bf9eb5f835bf977467c1307bf19cca7384`: Plan und Windows-Release-
Gate bestanden (2.764 Python-Tests + 14 Subtests, eine Warnung, 796,44 s).
Checkout und tatsächliches installiertes Produkt haben jeweils **77 bestandene,
sechs fehlgeschlagene Browserfälle**, keine übersprungenen/instabilen Fälle.
Alle **13 neuen AP8-Fälle** einschließlich vier echten 100er-/25er- und sechs
Hell-/Dunkel-Größenfällen bestanden in beiden Umgebungen. Die sechs Fehler
betreffen ausschließlich ältere AP5-/AP6-/AP7-Prüfstellen, die nach dem korrekten
Versionswechsel noch alpha.7 in der Sidebar verlangten statt sichtbarem alpha.8.
Diese übersehenen Erwartungen sind keine erfolgreiche Gesamt-CI; der Installer-
Lifecycle brach deshalb nach sechs bestandenen Teilprüfungen ab.

Die drei betroffenen Testdateien beziehen ihre genaue Erwartung nun aus der
Frontend-Release-Metadatei, nach dem bereits bestehenden Muster der Workbench-
Versionsprüfungen. Die Übereinstimmung mit der gemeinsamen Python-Releasequelle
wird weiterhin im echten Release-Gate geprüft. Keine Produkt-/Modelländerung,
kein abgeschwächter Versionscheck oder übersprungener Fall. Alle 83 Tests werden
vollständig aufgezählt; neue vierfache Produkt-CI folgt im selben PR #297.

## M4 technisch abgeschlossen am korrigierten Produktpunkt

Vier tatsächliche Produktchecks am Kommitt `17cbf5e631233ff5e5f5153a673a2eb6adaa7375` erfolgreich.
2.764 Python-Tests + 14 Subtests, 83 Checkout-Browserfälle, 14 echte
Installer-Lifecycle-Prüfungen und 83 Browserfälle am installierten Produkt bestanden.
Keine übersprungenen/instabilen/fehlgeschlagenen Browserfälle. Alle vier frischen
100er-Rechnungen und exakten 25er-Prefixe erhalten die AP7-Modell-Digests;
Checkout und installierte Anwendung liefern dieselben Modell-/Ansichtsnachweise.
CI-Prüfmerge-Tree entspricht exakt dem Produkt-Tree. 387 Ressourcen gebunden,
darunter zwölf tatsächliche AP8-Bilder; SHA/Version/EXE/GitHub-Archiv geprüft.
Korrigierter lokaler Installer und drei direkte Frozen-App-Prüfungen separat
erfolgreich; keine lokale Installation behauptet.

[Produktprüfung](ims_ap8_produktpruefung.md), [Verifikation](ims_ap8_verification.json)
und [Abschluss](ims_ap8_abschlussbericht.md) enthalten echte Zeiten, Download,
Hash, Grenzen und Iterationsbelege. AP8 done/technisch fertig, Anwenderabnahme
pending/Merge false. Kein öffentlicher Release oder AP9–AP14-Auftrag.
Nachstehende beziehungsweise vorstehende frühere offene Prüfstände sind historisch.

## Anwenderhinweis: tatsächlichen Einstieg in der Anleitung berichtigt

Am 03.10.2026 meldete der Auftraggeber, den in Schritt 1 genannten Bereich
„Markt und Strategien“ nicht zu finden. Die tatsächliche Navigation aus
`frontend/src/WorkbenchShell.tsx` lautet **Simulation → Markt und Familien**;
auf der Übersicht führt **Markt und Familien öffnen** zum selben `#market`.
`MarketExplorerWorkbench.tsx` zeigt dort oben die Überschrift
**Markt verstehen · sechs verknüpfte Ansichten**. Markdown-/Offline-HTML-Anleitung
benennen nun diese konkreten Schritte, die gestartete Anwendung und die
benötigte Release-Anzeige ab alpha.8. HTML mit dem vorhandenen Renderer neu
erzeugt; sichtbare Bezeichnungen mit dem UI-Quellcode abgeglichen.

Nur Anleitung und Arbeitsnachweis berichtigt, keine neue Produktfassung oder
geänderter Installer ausgeliefert. Der geprüfte alpha.8-Installer bleibt am
Produktpunkt 17cbf5e gebunden und enthält noch die frühere Anleitung; die lokale
HTML-Anleitung enthält die Korrektur. Der versehentlich noch auf 23e493b zeigende
Produktpunkt im AGENTS-Status wurde auf den tatsächlich erfolgreichen 17cbf5e
berichtigt. Historische fehlgeschlagene Prüfstände bleiben dokumentiert.
Anwenderabnahme und Merge weiterhin offen.
