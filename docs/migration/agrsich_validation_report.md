# Agrsich-Legacy-Validierungsreport

## Ziel

Dieser Schritt ergaenzt den bestehenden Agrsich-Replay- und Legacy-Vergleichspfad um
maschinenlesbare Ergebnisberichte. Der Report fasst vorhandene Fenstervergleiche zusammen,
ohne neue fachliche Exportlogik oder neue Simulationssemantik einzufuehren.

## Was der Report leistet

- Match-Status je validierter Exportdatei
- Zeilenanzahl, Treffer, Abweichungen und Match-Rate
- Perioden mit Abweichungen
- betroffene Feldnamen
- Detailabweichungen mit Ist- und Sollwerten
- Export als JSON und als kompakte CSV-Dateizusammenfassung

Der Replay-Runner liefert fuer ein Legacy-Fenster nun zusaetzlich zum bestehenden
`LegacyWindowComparison` einen `LegacyValidationReport`.

## Einordnung

Der Report baut auf den vorhandenen Vergleichsobjekten auf. Die Quelle der Wahrheit bleibt der
bereits vorhandene Legacy-Fenstervergleich gegen echte Dateien wie `VU14L1.DAT` und
`VUSK1L4.DAT`.

## Grenzen

Dies ist noch kein UI-Dashboard und keine neue Validierung weiterer Dateifamilien. Der Report
berechnet keine fachlichen Werte neu, sondern strukturiert nur bestehende Vergleichsergebnisse.
Er behauptet keine historische Vollgleichheit ausserhalb der konkret verglichenen Fenster.

## Anschluss

Der naechste sinnvolle Schritt ist, mehrere Dateifamilien in einem gemeinsamen Validierungslauf
zu buendeln und denselben Reportpfad fuer breitere Legacy-Fenster zu nutzen.
