# FREIGEGEBENER ARBEITSAUFTRAG – kein automatischer Start: AP4 – Erklärbare Oberfläche und geführter Einstieg

Geprüfter Checkout: de3d1de330df81ec948491dbcfbc97ca00a70c60; geprüfte main-Referenz: de3d1de330df81ec948491dbcfbc97ca00a70c60.
Planstatus: accepted; technischer Status: planned.
Umsetzungsfreigabe: .tmp-pr-ap4\ap4-authorization.json.
Branchvorschlag: codex/ims-explainable-roles; Paketmanifest: docs/plans/ims_explainable_market_plan.json.
Abhängigkeiten: AP3; offene main-Belege: keine.

Beleg: Auftraggeber dieser Codex-Sitzung, 2026-10-02T08:22:29.821931+02:00; Umfang implementation.

Dokumentierter Auftrag: Merge den Plan auf Main
Falls ohne die Dora pdf möglich : starte dann ap4

## Entscheidungsnutzen

Einsteiger und Wiedereinsteiger können Fall, nächsten Schritt und eine Ergebnisänderung bis Eingabe/Regel/Buchung erklären.

## Umfang in einem Paket-PR

- Vier Rollensichten mit erhaltenem Fallzustand
- Übersicht mit echten Kennzahlen, Verlauf und nächsten Schritten
- Erklärweg von Eingabe und Regel zu Entscheidung und Buchung
- Geführte vorhandene AP3-Demos und Einsteiger-/Wiedereinsteigeranleitung

## Abnahmen

- Preisfall 302 × 95 = 28.690 in IMS nachvollziehbar
- Diagramme und Kennzahlen stimmen mit API und Export überein
- Rollenwechsel erhält Eingaben, Ergebnis und Freigaben
- API-Fehler, veraltetes Ergebnis, Nullvergleich und echte Laufperioden verständlich
- Drei Bildschirmgrößen, zwei Farbmodi, Tastatur und mindestens 4,5:1 Textkontrast

## Voraussetzungen / fachliche Entscheidungstore

- Annahme der Folgeplanung und AP3 in main
- Persona-Sichten verändern keine fachliche Rechnung

## Quellen / Anforderungen / Meilensteine

- docs/plans/ims_explainable_market_plan.json
- docs/plans/ims_explainable_market_2026_10.md

Quellen-IDs: angenommener Folgeplan.
Anforderungs-IDs: R01, R02, R03, R04, R10, R13.

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
