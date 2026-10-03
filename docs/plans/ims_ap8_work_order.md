# FREIGEGEBENER ARBEITSAUFTRAG – kein automatischer Start: AP8 – Marktprozesse und Strategiefamilien in IMS visualisieren

Geprüfter Checkout: 32ba3112d994f57f33e64e1bc318e7d095223cd0; geprüfte main-Referenz: 32ba3112d994f57f33e64e1bc318e7d095223cd0.
Planstatus: accepted; technischer Status: planned.
Umsetzungsfreigabe: .tmp-pr-ap8\authorization.json.
Branchvorschlag: codex/ims-market-visualizations; Paketmanifest: docs/plans/ims_explainable_market_plan.json.
Abhängigkeiten: AP7; offene main-Belege: keine.

Beleg: Auftraggeber dieser Codex-Sitzung, 2026-10-03T11:40:21Z; Umfang implementation.

Dokumentierter Auftrag: Anwenderabnahme und Merge bleiben offen - Anwenderabnahme erteilt - merge auf MAIN und fahre fort

## Entscheidungsnutzen

Marktprozesse, Gruppen und Strategiefamilien unmittelbar in IMS bis zur Buchung interpretieren.

## Umfang in einem Paket-PR

- Sechs verknüpfte Markt-, Sparten-, Familien-, Wechsel-, Zeitlinien- und Provider-/Prozessansichten
- Erklärte Gewichte, Nenner, Einheiten und Modellmarktumfang
- Klickpfad von Verlauf und Gruppenvergleich zu Akteur und Buchung
- Marktinterpretation in IMS und Einzel-VU-Details in Excel
- Aktuelle Rollen-/Markthilfe mit tatsächlichen Browserbildern

## Abnahmen

- Jeder Grafikpunkt stimmt mit API, Buchungen und Export überein
- Filter bleiben konsistent und ändern keinen Lauf
- Zeitabhängige Familien und Gruppen, korrekte Gewichte und Marktanteilsnenner
- Kunden-Wechselmengen ohne Doppelzählung und korrekte Ereigniszeiten
- Echte Gruppenauswertung ohne Excel interpretierbar
- Tastatur, zugängliche Tabellen, responsive Hell-/Dunkelansichten

## Voraussetzungen / fachliche Entscheidungstore

- Exakte Ursachenzerlegung, Wechselwirkungen und bloße Korrelation im jeweiligen Diagramm unterschieden

## Quellen / Anforderungen / Meilensteine

- docs/plans/ims_explainable_market_plan.json
- docs/plans/ims_explainable_market_2026_10.md

Quellen-IDs: angenommener Folgeplan.
Anforderungs-IDs: R01, R02, R09, R10, R11, R13.

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
