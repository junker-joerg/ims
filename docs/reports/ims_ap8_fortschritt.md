# AP8: Auftrag und Darstellung vorbereitet

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

Nächster Schritt M2 im selben Paket-PR: reine versionierte Projektion und frische
API mit bedeutungsvollen kleinen Tests; anschließend M3 Oberfläche/Drilldown und
M4 Anleitung/Bilder/einzigartige höhere Produktfassung/Installer. AP8 in_progress,
technisch nicht fertig, keine Anwenderabnahme/Mergefreigabe und kein öffentliches
Release. Kein AP9–AP14-Auftrag.
