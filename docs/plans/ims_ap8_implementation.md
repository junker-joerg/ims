# AP8: sechs verknüpfte Marktansichten und erklärte Position

03.10.2026. Umsetzung nach ausdrücklicher AP7-Abnahme/Merge/Fortsetzung beauftragt.
AP7 ist tatsächlich in main: `32ba3112d994f57f33e64e1bc318e7d095223cd0`,
[Mergebeleg](../reports/ims_ap7_merge.md). Der [Arbeitsauftrag](ims_ap8_work_order.md)
wurde vor Änderung des AP8-Manifeststatus im authorized-Modus gegen frisch
gefetchtes origin/main erzeugt. Ein Branch `codex/ims-market-visualizations`,
ein Draft-PR für Plan, Implementierung, API/UI, Tests, Anleitung und Installer.

Menschlicher Auftrag dieser Sitzung:

> Anwenderabnahme und Merge bleiben offen - Anwenderabnahme erteilt - merge auf MAIN und fahre fort

„Fahre fort“ gilt für AP8 gemäß angenommener Reihenfolge. Kein AP8-Merge,
öffentliches Release oder AP9–AP14-Auftrag. Die beobachtete Auftragserfassung
11:40:21 UTC ist kein behaupteter sekundengenauer Nachrichtenzeitpunkt.

## Angenommener Umfang und Ergänzung

Lieferbasis: [Marktplan](ims_explainable_market_2026_10.md#ap8-marktprozesse-und-strategiefamilien-in-ims-visualisieren)
und [Manifest](ims_explainable_market_plan.json). AP6-/AP7-Workshop-Umfang bleibt
erhalten; keine erneute deutsche Direktmarkt-Abnahme. **E08-01** aus dem
[Boardmanifest](ims_board_strategy_plan.json), am 02.10.2026 separat angenommen
über [PR #292](https://github.com/junker-joerg/ims/pull/292): Fokus, Rivalen und
Modellmarkt mit absoluten Ergebnissen und relativer Position nebeneinander.
Eigene Herkunft/Abnahmebelege; keine rückwirkliche Erweiterung von AP7.

Sechs miteinander verknüpfte Ansichten: Markt/Sparten-Verlauf, Modellmarktanteile
und Konzentration, Familien/Streuung/Gewichte, wirksame Kundenwechsel,
Ereignis-/Entscheidungs-Zeitlinie und Provider/Prozesse/Rückstand/Wiederanlauf.
Periode, Sparte, Vergleichsgruppe und Seite bedienen dieselben geprüften Daten.
Diagramme führen zu konkretem VU-/Spartenbeitrag und Buchung. Datentabellen,
Tastatur, Hell/Dunkel und drei Bildschirmgrößen gehören zu jeder Ansicht.

## Darstellung statt neuer Modellkanäle

Der [Darstellungsvertrag](ims_ap8_view_contract.md) erklärt alle Nenner,
Gewichte, Zeitpunkte und Grenzen. Eine neue reine Projektion wird an die
bestehende frische AP5-/AP6-/AP7-Rechnung angeschlossen. Ihre Ansicht erhält
einen eigenen Nachweis und behält den unveränderten Modell-Ergebnisdigest.
API teilt die bestehende Rechensperre; Filter verändern keinen Lauf. JSON/
Einzel-VU-Excel bleiben frisch an das Originalquellenbündel gebunden.

Das AP8-Tor ist eine Darstellungsanforderung: exakte Buchungsidentität,
im Modell belegter Kanal, gemeinsam wirkende Mechanismen und nur beobachtete
Korrelation ausdrücklich unterscheiden. Dafür werden keine neuen Risiko-,
Kapital-, Nachfrage- oder Resilienzregeln eingeführt. Kein weiterer fachlicher
Vertrag wird stillschweigend als vom Menschen angenommen ausgegeben.

## Meilensteine im selben Paket

| Stand | Lieferung | Nachweis |
| --- | --- | --- |
| M1 vorbereitet | Auftrag, Herkunft, Darstellungs-/Nenner-/Gewichtsvertrag | Dieser Plan, Darstellungsvertrag und tatsächlicher AP7-Merge |
| M2 implementiert | Reine versionierte Projektion, frische API, Erhaltungs-/Rundungs-/Mitgliedschafts-/Wechseltests | Acht unabhängige kleine Tests, 39 gemeinsame AP8/AP5/AP7-Tests bestanden |
| M3 lokal geprüft | Sechs bedienbare verknüpfte Ansichten, Drilldown, Rollen/Fokus/Rivalen, JSON/Excel | Alle vier echten 100er-Digests/Prefixläufe, Nenner/Gewichte/Bücher, Filter und Exporte bestanden |
| M4 Produkt-CI folgt | Anleitung, zwölf echte Bilder, höhere Produktkennung und wirklicher Windows-Installer | Lokale Suite 2.763 + 14 Subtests bestanden; Ressourcen-/Produkt-/Installer-CI noch offen |

Neue gemeinsame Produktkennung alpha.8 ist noch kein geprüfter ausgelieferter Installer.
Aktueller Stand: [Fortschritt](../reports/ims_ap8_fortschritt.md).
