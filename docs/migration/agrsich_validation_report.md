# Agrsich-Legacy-Validierungsreport

## Ziel

Dieser Schritt ergaenzt den bestehenden Agrsich-Replay- und Legacy-Vergleichspfad um
maschinenlesbare Ergebnisberichte. Der Report fasst vorhandene Fenstervergleiche zusammen,
ohne neue fachliche Exportlogik oder neue Simulationssemantik einzufuehren.

## Was der Report leistet

- Match-Status je validierter Exportdatei
- Target-Metadaten je Datei: Subjekttyp, Stufe, Selektorart und Selektorwert
- Zeilenanzahl, Treffer, Abweichungen und Match-Rate
- Perioden mit Abweichungen
- betroffene Feldnamen
- Detailabweichungen mit Ist- und Sollwerten
- Feldabweichungen als aggregierte Summaries je Datei und Feld
- Export als JSON, kompakte CSV-Dateizusammenfassung und Feldsummary-CSV

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
Die Feldsummary nennt Abweichungsanzahl, betroffene Perioden und, falls beide Werte numerisch
sind, die groesste absolute Differenz. Sie bewertet diese Differenz nicht fachlich.

## Anschluss

Dieser Reportpfad kann nun sowohl einzelne Versicherer-Fenstervergleiche als auch
mehrperiodige Tabellenvergleiche ueber mehrere Dateifamilien zusammenfassen. Damit lassen sich
Versicherer- und VN-Vergleiche in einem gemeinsamen Validierungsbericht buendeln.

Ein kleines Validierungs-Fixture kann nun mehrere reale Legacy-Zieldateien beschreiben und den
gemeinsamen Reportpfad automatisch ausfuehren. Das aktuelle Bundle validiert ein
Versicherer-Gesamtfenster aus `VUSK1L4.DAT`, ein Versicherer-Einzelfenster aus `VU14L1.DAT`,
ein VN-Gesamtfenster aus `IMSVNSK1.DAT` und ein VN-Regelfenster aus `IMSVNR05.DAT` in einem
Lauf. Alle vier Fenster umfassen aktuell je zehn Perioden.

Der Fixture-Lader weist unvollstaendige Targets mit fehlenden Datei-, Stufen- oder
Selektorangaben, doppelte, unsortierte oder lueckenhafte Perioden innerhalb eines Targets und
doppelt eingetragene Targets frueh zurueck, damit die Reportzahlen nicht durch versehentliche
Doppelvergleiche oder missverstaendliche Fenstergrenzen verzerrt werden.

Wenn ein Bundle Reports schreibt, entstehen nun drei Artefakte: der vollstaendige JSON-Report,
die Datei-Zusammenfassung als CSV und eine separate Feldsummary-CSV fuer schnelle Auswertungen
von Abweichungsschwerpunkten.

Der naechste sinnvolle Schritt ist, dieses Fixture-Format auf laengere Fenster und weitere
bereits parsergestuetzte Dateifamilien auszuweiten.
