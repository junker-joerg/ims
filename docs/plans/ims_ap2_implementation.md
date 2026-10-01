# AP2: Umsetzung und Abnahmen der Workbench

Start: 01.10.2026. Basis main `965156caf02734cc47e93615c1f8ca91692d51fe`;
AP1 ist mit unabhängiger Windows-11-Abnahme nach main übernommen (PR #288).
Branch `codex/ims-elegant-workbench`, ein eigener Draft-PR für das gesamte AP2.

## Ausgangspunkt und Mapping

- `frontend/src/main.tsx`: bestehende API-Verträge, Metadaten, Strategie- und
  Run-Control-Ansichten. Keine Änderung der API-Anfragen oder Fachsemantik.
- `ModelBalanceWorkbench`, `LifeWorkbench`, `HealthWorkbench`,
  `FourSectorBalanceWorkbench`, `CapitalWorkbench`: vorhandene Eingaben,
  Berechnungen, Ergebnisnachweise, Speicherfreigaben und Exporte beibehalten.
- `styles.css`: bisherige Farben und Komponenten auf gemeinsame Variablen,
  Systemschrift, Abstände, Radien, Fokus und hell/dunkel umstellen.
- Historische Terminal-UI und C-Regeln bleiben unverändert. Herkunfts- und
  Modellgrenzen sind weiterhin am jeweiligen Fall und an Freigaben sichtbar.

## Interne Meilensteine

1. Ausgangsbilder auf 1440×900, 1024×768 und 390×844 sichern. Gepinnte
   Playwright-/axe-Abhängigkeiten und Chromium reproduzierbar installieren.
2. Wiederverwendbare Shell, Bereiche und aufklappbare Details einführen:
   Übersicht, Szenario, Simulation, Ergebnisse, Hilfe. Bestehende Anker weiter
   auflösen; Browser-Zurück/Vorwärts und direkte Links erhalten.
3. Zustände beim Navigieren erhalten: Komponenten bleiben gemountet.
   Simulation bietet vorhandene Modellfälle und ausdrücklich getrennte
   Strategie-/Ausführungswerkzeuge. Ergebnisse zeigen tatsächliche Resultate
   und gespeicherte Fälle; keine leere Berechnung als Ergebnis darstellen.
4. Ruhige helle/dunkle Gestaltung, benannte Status- und Fehlerzustände,
   Tabellen innerhalb ihrer Flächen scrollen lassen, reduzierte Bewegung,
   klare Tastaturbedienung und mindestens 44×44 für wesentliche Aktionen.
5. Echte Browserläufe für Modell-/Exportpfad, ungültige Eingabe und Korrektur,
   Formularzustand/Freigaben, Downloads, drei Viewports und beide Farbmodi.
   Vorhandene Browser-Skripte an Navigation und reproduzierbaren Browser anpassen.
6. Handbuch und CI ergänzen; Installer mit neuer Oberfläche bauen/testen,
   vorhandenen Windows-Release-Gate ausführen. Bericht und Evernote-Ablage
   entsprechend der Lieferübergabe sichern.

## Risiken und Entscheidungstore

Ausblendung darf Formularzustand oder geprüfte Quellketten nicht zurücksetzen.
Ergebnisse und Freigaben müssen sich bei geänderter Eingabe weiterhin wie
bisher entwerten. Navigation/Fokus dürfen Fehlerkorrektur nicht unterbrechen.
Die vorhandene regulatorische Trennung und technischen Ausführungssperren
bleiben sichtbar. Eine reine Layoutprüfung oder ein TypeScript-Build genügt
nicht als Produktabnahme. Keine neue Fachfunktion aus AP3 und kein neues
Desktop-/UI-Framework. Keine automatische Zusammenführung von AP2.

Status: Alle Produktabnahmen abgeschlossen. Bericht/Evidenz stehen in
`docs/reports/ims_ap2_abschlussbericht.md`, `ims_ap2_p52_evidence.json` und
`ims_ap2_ci_evidence.json`. Produkthead 7dc368e hat vier grüne Checks.
Ready erst nach erneut grünen Checks des abschließenden Dokumentations-Heads.
AP2-Merge und AP3-Start bleiben gesondert freizugeben; Evernote-Ablage mangels
Zugriff offen, vollständiger Bericht entsprechend der erlaubten Alternative
im Repository und PR gesichert.
