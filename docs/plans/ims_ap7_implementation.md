# AP7: vier Schockfälle im angenommenen BaFin-Referenzmarkt

03.10.2026. **Umsetzung beauftragt; fachliche Kopplungstore angenommen, M1–M4 technisch fertig; Anwenderabnahme und Mergeauftrag erteilt, tatsächlicher Merge folgt.**
[Wörtliche Annahme und ICT-Erkläranforderung](../reports/ims_ap7_contract_acceptance.md).
Ein Branch `codex/ims-market-shock-demos`, ein Draft-PR für das gesamte Paket.
Der [Arbeitsauftrag](ims_ap7_work_order.md) wurde gegen frisch gefetchtes main
`88841290113a37faa6bf117d4cd67dcd9ff0867c` erzeugt, nachdem AP6 tatsächlich
[übernommen](../reports/ims_ap6_merge.md) war. Der menschliche Auftrag lautet:

> Gibst du AP6 zur Anwenderabnahme und zum Merge frei? Freigabe erteilt - fahre fort

„Fahre fort“ setzt die angenommene Reihenfolge mit AP7 fort. Erfassung des Belegs
03.10.2026, 08:33:06 Europe/Berlin; genauer Nachrichtenzeitpunkt nicht ausgewiesen.
Planannahme und Umsetzungsauftrag ersetzen keine Annahme eines noch nicht
erklärten neuen Lebens-/ICT-Vertrags. Keine Merge-/Veröffentlichungsfreigabe
für AP7 und kein Auftrag für AP8–AP14.

## Umfang und Herkunft

Lieferbasis: [angenommener Marktplan](ims_explainable_market_2026_10.md#ap7-vier-schock-demos-mit-erklärten-gegenmaßnahmen)
und [Manifest](ims_explainable_market_plan.json). Ausgangsdaten: der bereits
angenommene AP6-BaFin-Referenzfall einschließlich offener Deutschland-/Gruppen-
grenzen; keine erneute deutsche Top-40-Abnahme. Strategien, neue Produkte und
Providerbeziehungen sind ausdrücklich Workshop-Annahmen.

Vier portable 100-Perioden-Fälle: fiktiver Anbieter 41 in Kfz, geringere Lebens-
Neunachfrage, hypothetische DORA-2.0-Umstellung, gemeinsamer Ausfall deklarierter
US-Provider. Schreibfreies Original, eigene Sitzung, gemeinsame P1–P5,
editierbarer Schock ab P21, Gegenmaßnahmen, API/UI, quellengebundenes JSON/Excel,
Rollenpfade, Anleitung und echter Installer gehören zusammen.

**Angenommene Ergänzung E07-01** hat eigene Herkunft in
[Boardmanifest](ims_board_strategy_plan.json), `candidate_amendments` AP7:
angenommen über [Plan-PR #292](https://github.com/junker-joerg/ims/pull/292).
Einzelereignis und Sequenz erhalten stabile ID, Beginn, Dauer, Intensität,
Akteure und Wirkungskanäle. Abnahmeauswirkung: Zeitfenster-/Überlappungs-/
Sequenzprüfungen und Ereigniserklärung zusätzlich; historische Abnahmen bleiben
unverändert. Keine Übernahme vorgeschlagener AP10–AP14-Kanäle.

## Meilensteine im selben Paket

| Stand | Arbeit | Nachweis / nächstes Tor |
| --- | --- | --- |
| M1 angenommen | C-/Python-Herkunft, Grenzen, konkreter Lebens-/Zeit-/Buchungs-/Ersatzpfadvertrag und kleine Handfälle | [Vertrag](ims_ap7_shock_contract.md), [Proben](../reports/ims_ap7_contract_probes.json), ausdrückliche menschliche Annahme |
| M2 implementiert | Versionierter Schockvertrag, aktiver Eintritt, begrenzte Lebensanträge, physische Prozesszeit, Warteschlangen und einmalige Buchung | Angenommene zwei fachliche Tore; deterministische kleine Regressionen |
| M3 produktverifiziert | Vier echte 100er-Fälle, API/UI-Original/eigene Sitzung, frisches JSON/Excel und Rollen-Erklärpfade | Prefixe, Quellen-/Draw-Bindung, Bilanz-/Risiko-/Kosten-/Mengenabnahmen, Ressourcenmessung |
| M4 produktverifiziert | Offline-Anleitung, echte Bilder, höhere gemeinsame Produktversion und tatsächlicher Windows-Installer | Produkt-/Browser-/Lifecycle-CI, Anwenderabnahme separat, Merge separat |

M1 veränderte keinen Produktkern und lieferte keine alpha.7-Anwendung. M2/M3
implementieren die ausdrücklich angenommenen Kanäle; alpha.7 ist im
Branch vollständig geliefert und tatsächlich installiert geprüft.
[Produktprüfung](../reports/ims_ap7_produktpruefung.md) und
[Verifikation](../reports/ims_ap7_verification.json) binden den Produktkommitt.
Anwenderabnahme und Merge bleiben separat offen. Probeberichte unterscheiden bestehenden
Kernlauf, unabhängige Handrechnung und erst vorgeschlagene Modellkanäle.

## Angenommener begrenzter Vertrag

Der [vollständige Vorschlag](ims_ap7_shock_contract.md) erklärt einen synthetischen
Lebens-Interessentenpool, erhaltene Altgarantien, Ausgabe erst nach Bearbeitung,
24 Prozessstunden je Modellperiode, fortbestehenden alten Versicherungsschutz
bei wartendem Nichtleben-Wechsel, konkrete transitive Ersatzpfade und einmalige
Kosten. Claims-/Service-Queues erfassen zunächst administrative Arbeit/Kosten;
Versicherungszahlungen verschieben sie nicht. Diese Grenze gehört ausdrücklich
zur neuen Abnahme, keine stillschweigende Ausweitung oder Vollkopplungsbehauptung.

## Risiken und Prüfung

AP5 zählt registrierte Sektorzeilen, kein zeitabhängiges Aktivierungsmerkmal;
AP3s skalarer Fallback belegt keine Pfadunabhängigkeit. Lebens-Nachfrage und
gekoppelte Vorgänge sind moderne Erweiterungen mit
[eigenem Mapping](../migration/ap7_shock_contract.md). Konservative Trennung
bewahrt alte Eingänge und Regressionen. Neue Budget-/Fälligkeits-/Storno- oder
SCR-Regeln bleiben außerhalb. Zeiteinheiten, Finanzierung, Rundung, unversicherte
Anträge und Horizont-Rückstände müssen in Oberfläche und Export sichtbar sein.

M2/M3 prüfen insbesondere: alte Garantien/Ablauf, 40/41 aktive Anbieter,
Kapitalzuführung, gemeinsame Anfangsperioden/akteurgebundene Draws, Warteschlangen-
und Risikokonservation, halboffene Stundenkanten, Aufholung statt pauschalem
Doppelverlust, gemeinsame Kosten genau einmal und No-shock-Vorsorgekosten.
Vier reale 100er-Läufe und installierte Browserprüfung sind M4-Pflicht; die
M1-Handfälle ersetzen sie nicht. Aktueller Stand und genaue Prüfungen:
[Fortschritt](../reports/ims_ap7_fortschritt.md).
