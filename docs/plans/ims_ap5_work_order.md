# FREIGEGEBENER ARBEITSAUFTRAG – kein automatischer Start: AP5 – Marktmodell und auswertbare Strategiefamilien

Geprüfter Checkout: 9b0d45a22be4314eda8e9ab1db61c506a44160f7; geprüfte main-Referenz: 9b0d45a22be4314eda8e9ab1db61c506a44160f7.
Planstatus: accepted; technischer Status: planned.
Umsetzungsfreigabe: .tmp-pr-ap5\ap5-authorization.json.
Branchvorschlag: codex/ims-market-strategy-groups; Paketmanifest: docs/plans/ims_explainable_market_plan.json.
Abhängigkeiten: AP4; offene main-Belege: keine.

Beleg: Auftraggeber dieser Codex-Sitzung, 2026-10-02T10:50:41.754299+02:00; Umfang implementation.

Dokumentierter Auftrag: 1) anbei DORA PDF
2) Anwenderabhnahme erfolgt - Freigabe zum Merge erteilt
3) Fahre dann mit AP5 fort

## Entscheidungsnutzen

Kunden-/Risikowechsel und Strategiefamilien mit konsistenten Einzel-VU- und Marktsummen vergleichen.

## Umfang in einem Paket-PR

- Neuer expliziter moderner Mehr-VU-Marktvertrag mit 40/41 Anbietern
- Gemeinsame Risiko-, Mengen-, Buchungs- und Bestandszuordnung
- Getrennte Versicherungs-, Vergleichs-, Kunden- und Strategiegruppen
- Gruppen-/Familien-API und erste nutzbare Marktsicht
- Quellengebundener Einzel-VU-Excel-Export

## Abnahmen

- Zwei/drei-VU-Handfälle und deterministischer 40/41-VU-Lauf mit 100 Perioden
- Marktsumme und disjunkte Familiensummen stimmen mit Einzel-VUs überein
- Prämien, Risiko- und Mengenwechsel ohne Doppelbuchung; unversicherte Mengen bleiben sichtbar
- A = L + E, Carryover und gemeinsamer Anfang/Prefixe
- Akteurgebundene Zufallswerte und reproduzierbare Tie-Breaks
- Familienzuordnung mit Zeitfenstern und unverändertes Ergebnis bei bloßem Filterwechsel

## Voraussetzungen / fachliche Entscheidungstore

- Mehr-VU-, Risiko-, Aggregat- und Strategiegruppenvertrag anhand kleiner Handfälle erklärt und angenommen
- Neue Lebens-Nachfrage und zusätzliche Regelkerne explizit kartiert
- Ressourcenlimits anhand tatsächlicher 40/41-VU-Messungen festgelegt

## Quellen / Anforderungen / Meilensteine

- docs/plans/ims_explainable_market_plan.json
- docs/plans/ims_explainable_market_2026_10.md

Quellen-IDs: angenommener Folgeplan.
Anforderungs-IDs: R05, R06, R09, R10, R11, R12, R13.

- Meilensteine im angenommenen Paket-PR festhalten.

## Separat vorgeschlagene Ergänzungen

Keine Erweiterung des angenommenen Umfangs durch diesen Auftrag.

## Fortsetzen und abschließen

Vor Arbeit origin aktualisieren, AGENTS.md, Handoff und Paketquellen lesen.
Bei veraltetem main oder neuer Planung Auftrag erneut erzeugen. Vorhandenen
passenden Branch/Draft-PR fortsetzen; keine fremden Änderungen überschreiben.
Eigene editable Umgebung je Checkout; Windows: .venv/Scripts/python.exe und npm.cmd.
Ein Paket mit Implementierung/API/UI/Tests/Anleitung/Installer über mehrere
Meilensteine und Sitzungen. Quellenmapping, Annahmen und Modellgrenzen erhalten.
Vor Pause Commit, Fortschritt, Tests, Blocker und nächsten Schritt im selben PR
dokumentieren. Technisch done erst nach echten Abnahmen und Abschlussbelegen.
Übernahme in main mit gesondertem Merge-Beleg; Folgepakete benötigen diese
main-Belege. Planannahme, Umsetzungsfreigabe, technische Fertigstellung und Merge
bleiben getrennt. Vorschau startet keine Umsetzung; Merge/Release nur nach
gesondertem tatsächlichem Auftrag. Freigabedateien niemals zum Umgehen eines
fehlenden menschlichen Auftrags erfinden.
