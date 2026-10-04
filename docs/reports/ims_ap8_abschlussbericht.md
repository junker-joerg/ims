# AP8: Abschluss zur Anwenderabnahme

**Neue Fassung:** Die gemeinsame Cockpitkorrektur alpha.10 besitzt jetzt eigene
[Produktbelege](ims_ap8_cockpit_produktpruefung.md) und einen
[aktuellen Abschluss](ims_ap8_cockpit_abschlussbericht.md). Dieser Bericht
bleibt der historische alpha.8-Nachweis.

**Historischer Zwischenstand:** AP8 ist nach Anwenderkritik an der Orientierung zur
Bedienkorrektur erneut in Arbeit. Dieser Bericht belegt die historische
alpha.8-Fassung. Alpha.9 ist als Vorschau separat geprüft; vollständige
Produktprüfung und Anwenderabnahme bleiben offen.
[Damaliger Stand](ims_ap8_fortschritt.md),
[Bedienprüfung](ims_ap8_usability_verification.json).

Erfasst 2026-10-03 17:18:19 +02:00 (Europe/Berlin). **Technisch fertig**, Produkt **2.0.0-alpha.8** / Windows **2.0.0.8**,
ein [Paket-PR #297](https://github.com/junker-joerg/ims/pull/297).
AP7 wurde zuvor nach Ihrer ausdrücklichen Abnahme tatsächlich nach main übernommen.
Der danach autorisierte AP8-Auftrag ist mit Implementierung, API/UI, Tests,
Anleitung und geprüftem Windows-Installer erfüllt.

Sechs gemeinsam gefilterte Ansichten verbinden Markt/Sparten, Modellanteile/HHI,
aktuelle Familien, wirksame Wechsel, Ereignis-/Entscheidungszeit und Provider/
Prozesse/Wiederanlauf. Die separat angenommene E08-01 zeigt Fokus, Rivalen und
Modellmarkt mit absoluten Buchungswerten und relativer Position. Gewichte,
Nenner, Einheiten und Quellenreste sind sichtbar. Diagramm und Tabelle führen
zu tatsächlichem Akteur und Buchung; exakte Addition, Modellkanal, gemeinsame
Wirkung und Korrelation werden ausdrücklich unterschieden.

Der besonders gewünschte ICT-Erklärweg zeigt Ausfallstunden, transitive
Abhängigkeiten, tatsächlich nutzbare Ersatzpfade, gemeinsame Kapazität,
Rückstand und Erholung. Filter verändern keinen Lauf; Finanz-/Risiko-/Garantie-/
Nachfrage-/FIFO-/RNG-Kerne bleiben unverändert. JSON und Einzel-VU-Excel sind
frisch gebunden. Unversicherter Schaden ist ausdrücklich keine VU-Buchung.

Vier Produkt-CI-Checks bestanden: **2.764 Python-Tests + 14 Subtests,
83 Browserfälle, 14 Installer-Lifecycle-Prüfungen und 83 installierte Browserfälle**.
Vier 100er-Modell-/Ansichtsdigests stimmen zwischen Checkout und installiertem
Produkt überein und erhalten die AP7-Modell-Digests. Installer und 387 Ressourcen
sind unabhängig an den geprüften Git-Tree gebunden.
[Produktprüfung mit Zeiten, Hash und Download](ims_ap8_produktpruefung.md),
[maschinenlesbare Belege](ims_ap8_verification.json),
[Offline-Anleitung mit zwölf echten Bildern](../handbook/market_ap8.html),
[Herkunft und Grenzen](../migration/ap8_market_explorer.md).

**Anwenderabnahme und AP8-Merge bleiben offen.** Die freigegebene BaFin- und
begrenzte Claims-/Service-Workshop-Kopplung ist unverändert; keine neue deutsche
Direktmarkt-, Kalibrierungs-, DORA- oder historische Gleichheitsbehauptung.
Keine öffentliche Veröffentlichung oder AP9–AP14-Umsetzung. Erst tatsächlich
übernommenes AP8 und eigener Folgeauftrag erlauben AP9. Evernote-Ablage mangels
Werkzeugverbindung ausstehend; der vollständige Bericht ist im selben Paket-PR.
