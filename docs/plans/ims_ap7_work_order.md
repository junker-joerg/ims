# FREIGEGEBENER ARBEITSAUFTRAG – kein automatischer Start: AP7 – Vier Schock Demos mit erklärten Gegenmaßnahmen

Geprüfter Checkout: 88841290113a37faa6bf117d4cd67dcd9ff0867c; geprüfte main-Referenz: 88841290113a37faa6bf117d4cd67dcd9ff0867c.
Planstatus: accepted; technischer Status: planned.
Umsetzungsfreigabe: .tmp-pr-ap7\ap7-authorization.json.
Branchvorschlag: codex/ims-market-shock-demos; Paketmanifest: docs/plans/ims_explainable_market_plan.json.
Abhängigkeiten: AP6; offene main-Belege: keine.

Beleg: Auftraggeber dieser Codex-Sitzung, 2026-10-03T08:33:06+02:00; Umfang implementation.

Dokumentierter Auftrag: Gibst du AP6 zur Anwenderabnahme und zum Merge frei? Freigabe erteilt - fahre fort

## Entscheidungsnutzen

Vier deklarierte Schockverläufe und Gegenmaßnahmen mit erklärter Markt-/ICT-Wirkung untersuchen.

## Umfang in einem Paket-PR

- Vier vollständige portable 100-Perioden-Schockfälle
- Fiktiver Anbieter 41, deklarierter LV-Nachfrageschock, DORA-2.0-Workshop und US-Anbieterausfall
- Deklarierte Markt-/ICT-Zeit- und Buchungsbrücke
- Schreibfreie Demo, bearbeitbare Übernahme, aktive Gegenmaßnahmen und Rollen-Erklärpfade

## Abnahmen

- Alle vier Demos offline frisch ladbar und reproduzierbar
- Gemeinsame Anfangsperioden 1–5 und Akteur-/Perioden-Zufallsvertrag
- Anbieter aktiviert zum richtigen Zeitpunkt und Lebens-Altbestand erhalten
- Markt-/ICT-Verluste und gemeinsame Maßnahmenkosten genau einmal gebucht
- Transitive Ausfälle; unabhängiger Fallback wirkt, gemeinsam abhängiger Fallback fällt mit aus
- Handprüfbare Reaktionen und konsistente Markt-/Gruppensummen

## Voraussetzungen / fachliche Entscheidungstore

- Lebens-Nachfragevertrag mit erhaltenen Garantien erklärt und angenommen
- ICT-Zeitabbildung, Kostenzuordnung und Vermeidung doppelter Verluste erklärt und angenommen
- DORA 2.0 ausdrücklich hypothetisch; Firmen-/Providerdaten und Annahmen getrennt

## Quellen / Anforderungen / Meilensteine

- docs/plans/ims_explainable_market_plan.json
- docs/plans/ims_explainable_market_2026_10.md

Quellen-IDs: angenommener Folgeplan.
Anforderungs-IDs: R04, R05, R06, R07, R08, R12, R13.

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
