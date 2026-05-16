# Agrsich-Legacy-Validierungsreport

## Ziel

Dieser Schritt ergaenzt den bestehenden Agrsich-Replay- und Legacy-Vergleichspfad um
maschinenlesbare Ergebnisberichte. Der Report fasst vorhandene Fenstervergleiche zusammen,
ohne neue fachliche Exportlogik oder neue Simulationssemantik einzufuehren.

## Was der Report leistet

- Match-Status je validierter Exportdatei
- Target-Metadaten je Datei: Subjekttyp, Stufe, Selektorart und Selektorwert
- Zeilenanzahl, Treffer, Abweichungen und Match-Rate
- Gruppensummaries je Subjekttyp und Aggregatstufe
- Periodensummaries je globaler Periode
- flacher Abweichungsindex je Datei, Periode und Feld
- Perioden mit Abweichungen
- betroffene Feldnamen
- Detailabweichungen mit Ist- und Sollwerten
- Feldabweichungen als aggregierte Summaries je Datei und Feld
- Export als JSON, kompakte CSV-Dateizusammenfassung, Feldsummary-CSV, Gruppensummary-CSV,
  Periodensummary-CSV, Abweichungsindex-CSV und Artefaktmanifest

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

Wenn ein Bundle Reports schreibt, entstehen nun sieben Artefakte: der vollstaendige JSON-Report,
die Datei-Zusammenfassung als CSV, eine separate Feldsummary-CSV fuer schnelle Auswertungen
von Abweichungsschwerpunkten, eine Gruppensummary-CSV fuer Subjekttyp-/Stufen-Auswertungen,
eine Periodensummary-CSV fuer globale Perioden-Auswertungen sowie eine flache
Abweichungsindex-CSV fuer direkte Drilldowns und ein Artefaktmanifest, das alle Dateien mit
stabilen Rollen auflistet.
Das Artefaktmanifest kann wieder geladen und gegen die erwartete Artefaktanzahl sowie die
existierenden Dateien geprueft werden.
Aus dem Manifest kann zudem der vollstaendige JSON-Report wieder geladen und gegen die
Manifest-Summen geprueft werden.
Auf dieser Grundlage kann nun auch eine typisierte Report-Payload-Summary erzeugt werden.
Sie verdichtet Reportname, Artefaktrollen, Gesamtzaehler, Match-Rate und die vorhandenen
Abweichungsachsen nach Datei, Periode und Feld, ohne den eigentlichen Vergleich neu zu
berechnen.
Mehrere solche Manifest-Summaries koennen nun zu einem Batch-Buendel zusammengefasst werden.
Das Buendel aggregiert Reportanzahl, Datei- und Zeilenzaehler, Match-Rate, Artefaktrollen und
Abweichungsachsen ueber mehrere bereits erzeugte Reports. Auch dieser Pfad liest nur bestehende
Reportartefakte und fuehrt keinen neuen Legacy-Vergleich aus.
Das Batch-Buendel kann als JSON-Artefakt und als kompakte CSV-Datei geschrieben werden. JSON
enthaelt die Gesamtsicht und alle enthaltenen Einzelreport-Summaries; CSV schreibt je Report
eine Zeile fuer schnelle manuelle oder tabellarische Kontrollen.
Fuer diese Batch-Buendelartefakte kann nun ebenfalls ein Manifest geschrieben und geladen
werden. Es listet JSON, CSV und Manifest selbst mit stabilen Artefaktrollen auf und prueft
beim Laden optional, ob alle referenzierten Dateien existieren. Der JSON-Buendelpayload kann
aus diesem Manifest wieder geladen und gegen die Manifest-Summen geprueft werden.

Der naechste sinnvolle Schritt ist, dieses Fixture-Format auf laengere Fenster und weitere
bereits parsergestuetzte Dateifamilien auszuweiten.
