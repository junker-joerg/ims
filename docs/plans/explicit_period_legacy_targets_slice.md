# Plan: Legacy-Ziele fuer expliziten VU/VN-Runner

## Ziel

Dieser Slice schliesst den kombinierten expliziten VU/VN-Periodenrunner an die
bereits vorhandenen Agrsich-Legacy-Vergleiche an. Dadurch koennen die nach VU-
und VN-Fachlogik erzeugten Exporttabellen gezielt gegen kleine Referenzfenster
geprueft werden.

## Begrenzung

- Keine neue VU-/VN-Fachlogik.
- Kein historischer Scheduler.
- Keine Vollsimulation und keine historische Gleichheitsbehauptung.
- Keine neue Reporting-Oberflaeche; nur vorhandene Vergleichs- und Reportbausteine.

## Umsetzung

1. Expliziten Legacy-Zieltyp fuer kombinierte VU/VN-Exports ergaenzen.
2. Exporttabellen mehrerer Perioden je Datei zusammenfassen.
3. Versicherer- und VN-Referenzparser mit vollstaendiger Periodenabdeckung
   wiederverwenden.
4. Optional vorhandene Validierungsreports schreiben, wenn ein Reportname und
   ein Ausgabeordner gesetzt sind.

## Validierung

- Gruener Versicherer-Legacyvergleich fuer zwei explizite Perioden.
- Fehlerfall fuer fehlende Replay-Periode gegen ein laengeres Legacy-Fenster.
- Fixture-Test fuer relative Legacy-Ziele und geschriebene Reportartefakte.
