# AP7: Abschluss zur Anwenderabnahme

03.10.2026. **Technisch fertig im ausdrücklich angenommenen Workshop-Umfang**,
Produkt **2.0.0-alpha.7** in [Draft-PR #296](https://github.com/junker-joerg/ims/pull/296).
Die spätere [Anwenderabnahme und der AP7-Mergeauftrag](ims_ap7_user_acceptance.md)
wurden am 03.10.2026 ausdrücklich erteilt; tatsächlicher Merge wird separat belegt.
Keine öffentliche Veröffentlichung freigegeben.

Vier echte portable 100-Perioden-Schockfälle, gemeinsame Anfangsperioden,
bearbeitete Lebensanträge/Wechsel, erhaltene Altgarantien, konkrete Ersatzpfade
und einmalige Kosten sind mit API, bedienbarer Oberfläche, JSON/Einzel-VU-Excel,
Offline-Anleitung und echtem Windows-Installer geliefert. Der besonders
angeforderte ICT-Erklärweg verbindet Ereignis, Vorleistungen, gemeinsames
Arbeitsbudget/Rückstand, Vertragswirkung und Buchung auf beiden Vergleichsseiten.
Verlauf, Stundenkanten, Ersatzabhängigkeiten, Aufholung und Kosten sind sichtbar.

Vier Produkt-CI-Checks bestanden: 2.755 Python-Tests/14 Subtests, 70 Browserfälle,
14 Installer-Lifecycle-Prüfungen und 70 Browserfälle am installierten Produkt.
Alle vier 100er-Ergebnisdigests stimmen zwischen Checkout und installierter
Anwendung überein. Installer, Ressourcen, Quellen und getesteter Git-Tree sind
unabhängig gebunden. [Vollständige Produktprüfung](ims_ap7_produktpruefung.md),
[maschinenlesbare Belege](ims_ap7_verification.json),
[Anleitung](../handbook/market_ap7.html),
[Altcode-/Erweiterungs-Mapping](../migration/ap7_shock_contract.md).

Die [ausdrückliche Vertragsannahme](ims_ap7_contract_acceptance.md) umfasst die
begrenzte administrative Claims-/Service-Kopplung. Sie verschiebt keine
Versicherungszahlungen. BaFin-Quellenumfang, angenommene Provider-/Kostenprofile,
hypothetische DORA-Ausprägung und offene deutsche Direktmarkt-Tore bleiben
sichtbar. Keine alte Abnahme wurde rückwirkend erweitert.

Nächster Schritt ist der ausdrücklich beauftragte AP7-Merge nach den grünen
Checks des Abnahmestands. Erst tatsächliches AP7 in main erfüllt die Abhängigkeit
für den nun beauftragten AP8-Start. Kein AP8-Merge oder AP9–AP14-Auftrag.
