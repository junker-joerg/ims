# AP7: bestätigte Anwenderabnahme und Mergeauftrag

Am 03.10.2026 bestätigt der Auftraggeber dieser Sitzung wörtlich:

> Anwenderabnahme und Merge bleiben offen - Anwenderabnahme erteilt - merge auf MAIN und fahre fort

Die Zustimmung bezieht sich auf die gelieferte Fassung **2.0.0-alpha.7** in
[PR #296](https://github.com/junker-joerg/ims/pull/296), Head
`48c7c9a7654c4efc924b2212e12568e9e41a6d7f`. Damit sind Anwenderabnahme und
AP7-Mergeauftrag ausdrücklich erteilt. „Fahre fort“ beauftragt nach tatsächlicher
Übernahme von AP7 nach main das nächste angenommene Paket **AP8**. Sein Tor zur
Unterscheidung von exakter Addition, Wechselwirkung und Korrelation bleibt
verbindlich. Die separat angenommene Ergänzung E08-01 erhält eigene Herkunft
und Abnahmebelege. Kein AP8-Merge, öffentliches Release oder AP9–AP14-Auftrag.

Die Abnahme gilt für den bereits ausdrücklich angenommenen begrenzten Lebens-/
ICT-Vertrag und den BaFin-Referenzmarkt. Altgarantien bleiben erhalten, Anträge/
Wechsel werden erst nach Bearbeitung wirksam. Claims-/Service-Kopplung betrifft
administrative Arbeit und Kosten; Versicherungszahlungen werden nicht verschoben.
BaFin-Quellenumfang, synthetische Provider-/Produkt-/Kostenannahmen und offene
deutsche Direktmarkt-Tore werden durch die Zustimmung nicht verändert.

Alle vier Checks des genannten Heads waren am 03.10.2026 erneut erfolgreich
geprüft. Die Abschlussdokumentation 48c7c9a ändert gegenüber dem geprüften
Produktkommitt 37fe791 weder Anwendung noch Installer-Ressourcen. Der gelieferte
Installer und die vier identischen Checkout-/Installations-Ergebnisdigests sind
mit eigenem Hash-/Kommittbezug in der [Produktprüfung](ims_ap7_produktpruefung.md)
und [Verifikation](ims_ap7_verification.json) festgehalten.

Die allgemeine Anwenderabnahme nennt keine Gerätedaten, Testdauer oder konkret
durchgeführte Upgradefolge. Diese Angaben bleiben unbekannt; eine unabhängige
Clean-Windows-Messung oder ein echtes alpha.6→alpha.7-Upgrade wird nicht daraus
abgeleitet. Kein öffentliches Release angelegt.

Erfassung am 03.10.2026 ab 11:04:36 UTC; dies ist die beobachtete Erfassungszeit,
kein behaupteter sekundengenauer Nachrichtenzeitpunkt. Der tatsächliche Merge
wird erst nach erfolgreicher Übernahme separat belegt.

**Nachtrag nach tatsächlicher Übernahme:** PR #296 wurde am 03.10.2026,
11:39:38 UTC, nach vier grünen Checks am Abnahmekommitt f440f4c nach main
übernommen (`32ba3112d994f57f33e64e1bc318e7d095223cd0`); getesteter Head-
und main-Tree sind identisch. [Mergebeleg](ims_ap7_merge.md). Danach AP8-Auftrag
gegen frisch gefetchtes main im authorized-Modus erfolgreich erzeugt. Der
ursprüngliche Abnahmebezug 48c7c9a bleibt unverändert erhalten.
