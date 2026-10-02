# AP5 – Arbeitsstand und Handfallprüfung

## AP5 technisch zur Anwenderabnahme bereit

02.10.2026: Vertragsannahme dokumentiert, M2–M4 umgesetzt. Abschlussbericht
`docs/reports/ims_ap5_abschlussbericht.md` und Prüfprotokoll
`docs/reports/ims_ap5_verification.json`: 16 aktuelle AP5-Modell/APItests,
50 lokale Browserfälle, nochmals zehn aktuelle AP5-Browserfälle inklusive
Offlinebildern; vollständige Pythonregression 2715+14. Alle vier erforderlichen
Checks für Produkthead 04617fb erfolgreich; CI-Release-Gate 2715+14,
Installer-Lifecycle 14 und installierte Browserfälle 50 erfolgreich.
40/41×100 mit stabilen Quellen-/Ergebnisdigests und gemessenen Grenzen.
Guide, Bildstände und ausdrückliche Excel-/Prefixerklärung aktualisiert.
Anwenderfassung alpha.5 / Windows 2.0.0.5. Finalen Dokumentationshead im selben
Draft-PR #294 prüfen; keine Modelländerung nach geprüftem Produkthead.

Manifest: AP5 done (technisch)/technically_complete, Produktabnahme und Merge
ausstehend. Keine Freigabe für AP6–AP14 oder Public-Release. Hauptcheckout
bleibt AP4-main 9b0d45a. Nächster menschlicher Schritt: alpha.5-Produkt prüfen.
Die untenstehenden Zwischenstände bleiben datierte Herkunft.

Stand nach Vertragsannahme am 02.10.2026. **AP5 in Arbeit, produktiver Runner/API/UI implementiert.**
Der Auftraggeber nahm den Vorschlag mit „Vertrag annehmen und umsetzen“ an;
[Annahmebeleg](ims_ap5_contract_acceptance.md). Fortsetzung im selben
[Draft-PR #294](https://github.com/junker-joerg/ims/pull/294).

Gemeinsame Cash-/Reserve-/Eigenkapitalrechnung und Risikoledger, alle VUs,
Gruppen-/Familiensummen, zeitliche Strategien/Maßnahmen, API, Marktsicht und
Einzel-VU-Excel sind angeschlossen. Die ersten zwölf Modell-/APItests bestanden
(43,80 s, inklusive echter 40/41×100-Märkte). Weitere fachliche Randfälle
und der reale Desktop-APIanschluss wurden ergänzt. Neun Browserfälle und
anschließend der komplette 41×100-Fall bestanden: drei Hand-/Bedienfälle,
sechs Ansichten mit Axe ohne Verstöße, Kontrast ≥4,5:1 und ohne Seitenoverflow,
sowie Großlauf mit echten API-/Tabellenwerten. Die vollständige neue AP5-
Browsersuite bestand anschließend mit **10/10 Fällen (1,2 Minuten)**.
Die bestehenden Browser-/Pythonregressionen und Installerprüfung folgen.

Der vollständige 40er-Lauf dauerte 15,6959 s, der 41er-Lauf 16,1241 s.
Eingänge 4.351.336/4.460.047 Bytes; verlustlose Antworten mit Baseline und
Variante 35.369.741/36.239.738 Bytes. Das tatsächlich erforderliche Budget
ist 48 MiB, Eingänge bleiben 16 MiB. Vorherige 32-MiB-Grenze schlug am
vollen Lauf an; die wiederholten Feldnamen sind nun je Tabelle einmalig,
ohne Verlust von Zeilen, Nullwerten oder Präzision. Vollständige Messung
reproduzierbar über `scripts/planning/probe_ap5_market.py --out DATEI.json`.

Neue Anleitung `../handbook/market_ap5.md`/`.html`, Herkunft
`../migration/ap5_common_market.md`. Konsistente Produktkennung alpha.5,
Windows-Dateiversion 2.0.0.5. Installer und Gesamt-CI stehen noch aus.
Vertragsannahme ist keine Anwenderabnahme der späteren Produktlieferung;
AP5-Merge/Public-Release und AP6–AP14 bleiben unautorisiert.

## Historischer Meilenstein vor Vertragsannahme (Vorschlagscommit 0a21cf8)

Stand 02.10.2026. **In Arbeit; kein fertiggestellter AP5-Produktlauf.**
Begonnen nach abgenommenem AP4 und seinem autorisierten Merge #293.
Basis-main `9b0d45a22be4314eda8e9ab1db61c506a44160f7`.
Branch `codex/ims-market-strategy-groups`; denselben Draft-PR fortsetzen.

## Bereits konkret geprüft

Der [Fachvertrag](../plans/ims_ap5_market_contract.md) enthält den gemeinsamen
Periodenablauf und zwei unabhängige Handrechnungen. Das Skript
`scripts/planning/probe_ap5_contract.py` vergleicht die vorab berechneten Werte
mit den vorhandenen Vrvn06- und Cash-/Reserve-/Eigenkapitalkernen. Die vorgeschlagene
Kapazitätszulassung ist separat gekennzeichnet. Es führt keinen Produktmarkt aus.
Maschinenbeleg: [ims_ap5_contract_probes.json](ims_ap5_contract_probes.json).

| Versuch | Tatsächlicher Nachweis |
| --- | --- |
| H1 Zwei-VU-Wechsel | Neuer Träger VU2; Prämie 20, neuer Schaden 40 dort. Alte Reserve/Zahlung bei VU1. Markt A=172, L=15, E=157. |
| H2 Drei-VU-Kapazität | Preisgleichstand nimmt kleinere ID auch bei umgekehrter Eingabereihenfolge. G1→VU1, G2→VU2, G3 unversichert. Markt A=E=315, L=0; gedeckt 14, unversichert 5. |
| Risikokonservierung | H2: Gesamtrisiko 20 = versichert 13 + unversichert 7. Prämie 28 wird genau einmal zugeordnet. |
| Gruppen / Carryover | Disjunkte Familien 215+100=315; überlappende Peers 215/212 sind keine Marktsumme. Nächste Anfangsbilanz entspricht dem vorherigen Schluss. |
| Maßnahmen-Handplan | Kosten 3 in p2, Kapazität 8 ausschließlich p4/p5, danach wieder 6. Nur Handplan geprüft, noch kein Maßnahmen-Produktmotor. |
| 40/41-Angebotskerne ×100 | 0,1849 / 0,1783 Sekunden; serialisierte Angebots-Snapshots 682.827 / 699.790 Bytes. Zweiter Lauf mit identischen Digests. |
| Neuer Akteur | Bindung der Zufallswerte an Akteur/Periode/Kanal lässt alle ersten 40 Angebote und Zufallswerte identisch. Unterschiedliche Auswahl durch ein tatsächlich neues Angebot bleibt möglich. |
| Alter Bilanzvalidator | ID41 wird erwartungsgemäß zurückgewiesen. Das alte 25er-Limit wurde nicht entfernt; der neue moderne Validator fehlt noch. |

Die Zeiten stammen aus diesem lokalen Versuch, nicht aus einer Schätzung.
Angebots-Snapshotgröße und -laufzeit sind keine fertige API-Größe oder
Ressourcenfreigabe für den gemeinsam bilanzierten Markt. Die Maße benötigen
nach M2 Wiederholung am tatsächlichen Produktlauf.

Zusätzlich bestanden alle **35 Plan-/Status-/Freigabeprüfungen in 5,365 s**.
Release-Metadaten bleiben konsistent bei `2.0.0-alpha.4` / `2.0.0.4`, da dieser
Zwischenstand noch kein verändertes Produkt ausliefert. `git diff --check`
bestand. Browser, vollständiger Markt-Runner und neuer Installer wurden in
diesem AP5-Meilenstein noch nicht geprüft.

## Neue Quelle

Die gelieferte KPMG-PDF wurde gelesen und die relevanten Diagramme visuell
geprüft. [DORA-Quellenaufnahme](../research/dora_benchmark_2026_06.md) und ihr
JSON-Register enthalten Hash, Ausgabe, Seiten, Fragen, Mehrfachantworten,
Untergruppen und Rundungsdifferenzen. G-BENCH ist als Zugangslücke geschlossen.
Keine Quelle oder Quote wird zu einer Provider-Ausfallwahrscheinlichkeit;
die Quelle liefert keinen empirischen Verlustpfad für den AP5-Markt.
Die datierten historischen Planbefunde bleiben Herkunft, AP13 bleibt offen.

## Offener Entscheidungspunkt und nächste Arbeit

Die in AGENTS und angenommenem Plan verlangte Annahme des Mehr-VU-/Risiko-/
Aggregat-/Familienvertrags ist noch offen. Die konkreten H1/H2-Werte und die
vorgeschlagene ganze Kohortenaufnahme werden dem Auftraggeber zur Prüfung
vorgelegt. Nach Annahme folgen im selben PR eigener Validator, gemeinsamer
Runner, echte Größen-/Prefix-/Familien-/Informationsregressionen, API/IMS-
Anschluss, Einzel-VU-Excel, Einsteigeranleitung, höherer Installer und CI.
AP5 bleibt `in_progress`, Abschlussbelege leer; keine Erweiterung auf AP6–AP14.

AP4 ist inzwischen vollständig nach main übernommen; seine bestätigte
Benutzerabnahme gilt. Evernote-Bericht noch ausstehend, weil die zeitweise
sichtbaren Werkzeuge derzeit nicht aufrufbar sind. Repository und PR sichern
den Bericht bis zur möglichen Aktualisierung des vorgesehenen IMS-Notizbuchs.
