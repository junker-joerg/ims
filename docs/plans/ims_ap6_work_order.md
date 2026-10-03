# FREIGEGEBENER ARBEITSAUFTRAG – kein automatischer Start: AP6 – Deutscher Versicherungsmarkt mit 40 Gruppen

Geprüfter Checkout: 03f87662e85e6081998bab79e32ee12baac52da1; geprüfte main-Referenz: 03f87662e85e6081998bab79e32ee12baac52da1.
Planstatus: accepted; technischer Status: planned.
Umsetzungsfreigabe: .tmp-pr-ap6\ap6-authorization.json.
Branchvorschlag: codex/ims-german-market-top40; Paketmanifest: docs/plans/ims_explainable_market_plan.json.
Abhängigkeiten: AP5; offene main-Belege: keine.

Beleg: Auftraggeber dieser Codex-Sitzung, 2026-10-02T12:39:03+00:00; Umfang implementation.

Dokumentierter Auftrag: Fahre mit dem nächsten IMS AP fort
Gibst du AP5 zur Anwenderabnahme und zum Merge frei? Ja

## Entscheidungsnutzen

Einen begrenzten deutschen Modellmarkt mit nachvollziehbaren Gruppen und sichtbaren Datenlücken laden.

## Umfang in einem Paket-PR

- Belegte 40er-Gruppenauswahl mit deutschen Anzeigenamen und Tochterzuordnung
- Dokumentierte Rankingkennzahl, gemeinsames Jahr, Deutschlandumfang und Grenzprüfung
- Offline ladbarer Modellmarkt mit getrennten Fakten und Workshop-Annahmen
- Quellen-Dossier und ausdrückliche Darstellung des nicht simulierten Restmarkts

## Abnahmen

- Genau 40 eindeutige Gruppen und geprüfte Grenze Rang 40/41
- Keine Doppelzählung oder Vermischung globaler, deutscher, gebuchter und verdienter Beiträge
- Belegte Sparten und Gewichtssummen, fehlende Werte gekennzeichnet
- Unbekannte Strategien und ICT-Abhängigkeiten nicht als reale Unternehmensdaten ausgegeben
- Laden, Import, frische Berechnung und reproduzierbare Nachweise

## Voraussetzungen / fachliche Entscheidungstore

- Gemeinsames Datenjahr, Rankingmaß und Gruppen-/Deutschlandkonsolidierung nachgewiesen
- Vollständige Rangbasis; keine unbelegte Top-40-Abnahme

## Quellen / Anforderungen / Meilensteine

- docs/plans/ims_explainable_market_plan.json
- docs/plans/ims_explainable_market_2026_10.md

Quellen-IDs: angenommener Folgeplan.
Anforderungs-IDs: R04, R12, R13.

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
