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
Zusaetzlich gibt es einen direkten Schreibpfad, der vorhandene Einzelreport-Manifeste oder ein
Verzeichnis mit solchen Manifesten einliest, daraus das Summary-Buendel erzeugt und die
manifestierten Batch-Artefakte in ein Zielverzeichnis schreibt.
Ein kleines Batch-Fixture kann nun mehrere vorhandene Legacy-Validierungsfixtures ausfuehren,
deren Einzelreport-Artefakte in getrennte Unterverzeichnisse schreiben und anschliessend das
manifestierte Summary-Buendel fuer den gesamten Batch erzeugen. Auch dieser Runner orchestriert
nur bestehende Validierungsfixtures; er fuehrt keine neue fachliche Vergleichslogik ein.
Der Batchlauf schreibt zusaetzlich ein Batch-Run-Manifest. Es verbindet Batch-Fixture,
Einzellauf-Ausgabeverzeichnisse, Einzelreport-Manifeste und Summary-Buendelmanifest, sodass ein
Batchlauf spaeter ohne erneutes Durchsuchen des Ausgabebaums nachvollzogen werden kann.
Der Batch-Run-Manifest-Lader trennt Payload-Schema und Artefakt-Existenzpruefung: Run-Eintraege
und Pflichtpfade werden immer validiert, auch wenn Dateiexistenzpruefungen fuer spezielle
Analysefaelle deaktiviert sind.
Bei aktivierter Artefaktpruefung gleicht der Lader nun zusaetzlich die im Batch-Run-Manifest
gespeicherten Summen gegen das referenzierte Summary-Buendelmanifest ab. Dadurch werden
nachtraeglich veraenderte oder nicht mehr zusammenpassende Batch-Manifeste frueh erkannt.
Auch die Einzellauf-Eintraege werden gegen ihre jeweiligen Report-Manifeste validiert:
Fixture-Pfad, Ausgabeverzeichnis und Report-Manifest muessen vorhanden sein, und die pro Run
gespeicherten Summen muessen zu den Manifest-Summen des Einzelreports passen.
Fuer aufrufende Batch- oder Analysepfade gibt es nun zusaetzlich einen nicht-werfenden
Manifest-Check. Er kapselt denselben Lade- und Validierungspfad in einem maschinenlesbaren
Ergebnisobjekt mit Status, gepruefter Run-Anzahl, gepruefter Artefaktanzahl und Diagnose-Issues.
Mehrere Batch-Run-Manifeste koennen zu einem Diagnose-Buendel zusammengefasst werden. Dieses
Buendel aggregiert Manifestanzahl, Run-Anzahl, gepruefte Artefakte und Issues ueber explizit
uebergebene Manifestpfade oder einen Verzeichnisscan und kann als JSON-Artefakt geschrieben
werden. Zusaetzlich kann das Diagnose-Buendel nun als kompakte CSV-Datei geschrieben werden:
eine Zeile je Batch-Run-Manifest mit Status, Zaehlern und Issue-Zusammenfassung.
JSON und CSV des Diagnose-Buendels koennen nun zusammen mit einem Artefaktmanifest geschrieben
werden. Der Manifest-Lader prueft die stabilen Artefaktrollen, optionale Dateiexistenz und die
Summen des JSON-Payloads gegen die Manifest-Summen.
Das manifestierte Diagnosepaket kann direkt aus expliziten Batch-Run-Manifestpfaden oder per
Verzeichnisscan erzeugt werden, ohne dass aufrufende Batchpfade das Buendel vorher selbst
konstruieren muessen.
Bereits geschriebene Diagnose-Artefaktmanifeste koennen nun ebenfalls per Verzeichnisscan
wieder geladen werden. Der Scan filtert auf die stabilen Diagnose-Artefaktrollen, damit
andere Summary- oder Batch-Manifeste im selben Ausgabebaum nicht versehentlich als
Diagnosepakete gelesen werden.
Mehrere geladene Diagnosepakete koennen nun zu einer uebergreifenden Payload-Summary
verdichtet werden. Diese Summary zaehlt Diagnosepakete, validierte Batch-Manifeste, Runs,
gepruefte Artefakte, Issues und fehlschlagende Diagnosepakete, ohne die zugrunde liegenden
Batchlaeufe oder Legacy-Vergleiche erneut auszufuehren.
Diese Diagnosepaket-Summary kann nun ebenfalls als JSON- und CSV-Artefakt mit eigenem
Artefaktmanifest geschrieben und aus dem Manifest wieder geladen werden. Damit bleibt auch
die uebergeordnete Diagnoseauswertung reproduzierbar und maschinenlesbar pruefbar.
Mehrere solcher manifestierten Diagnosepaket-Summaries koennen wiederum per Verzeichnisscan
geladen und zu einem Gesamt-Buendel verdichtet werden. Der Scan filtert auf die stabilen
Summary-Artefaktrollen und ignoriert darunterliegende Diagnose-Buendelmanifeste im selben
Ausgabebaum.
Dieses Gesamt-Buendel kann nun ebenfalls als JSON- und CSV-Artefakt mit Manifest geschrieben
und aus dem Manifest wieder geladen werden. Damit kann ein hoeherer Abnahme- oder
Batch-Workflow die letzte Diagnoseebene persistieren, ohne die darunterliegenden Laeufe erneut
zu starten.
Aus diesem Gesamt-Buendel kann nun zusaetzlich ein kompakter Acceptance Verdict abgeleitet
werden. Er fasst Status, Gruende, Issue-Zaehler und die wichtigsten Diagnosezaehler zusammen
und kann ebenfalls als JSON-/CSV-Artefakt mit Manifest persistiert werden. Der Verdict ist eine
technische Abnahmeentscheidung ueber die vorhandenen Diagnoseartefakte, keine neue fachliche
Bewertung der historischen Modellgleichheit.
Fuer Batch- oder Release-nahe Aufrufer gibt es nun zusaetzlich einen One-Shot-Schreibpfad:
Aus einem Verzeichnis mit manifestierten Diagnosepaket-Summaries werden das Summary-Gesamtbuendel
und der daraus abgeleitete Acceptance Verdict in einem Schritt persistiert.
Dieser One-Shot-Pfad schreibt nun auch ein Acceptance-Run-Manifest, das Summary-Gesamtbuendel
und Verdict-Manifest zusammen referenziert und beim Laden zentrale Zaehler konsistent gegen
die referenzierten Artefakte prueft.
Die Artefaktzaehlung dieses Diagnosepfads entspricht den tatsaechlich geprueften Pfaden:
Summary-Manifest sowie Fixture-Pfad, Ausgabeverzeichnis und Report-Manifest je Run. Das
Ausgabeverzeichnis muss dabei auch wirklich ein Verzeichnis sein, nicht nur ein existierender
Dateipfad.
Die Artefaktmanifest-Lader loesen relative Pfade tolerant auf und neu geschriebene Manifeste
speichern Artefaktpfade relativ zum Manifestverzeichnis. Der rekursive Batch-Scan ignoriert
Summary-Buendelmanifeste, damit wiederholte Laeufe im selben Ausgabebaum nicht versehentlich
ihre eigenen Summary-Ausgaben erneut als Einzelreports einlesen.

Der naechste sinnvolle Schritt ist, dieses Fixture-Format auf laengere Fenster und weitere
bereits parsergestuetzte Dateifamilien auszuweiten.

## Lokaler Validierungsueberblick

Fuer den Ruecksprung von der Workbench in die Fachlogik gibt es einen rein lesenden
Ueberblick ueber ein vorhandenes Legacy-Agrsich-Validierungsfixture:

```powershell
python -m ims.model.legacy_validation_overview tests/fixtures/legacy_validation_bundle.json
```

Der Befehl gibt eine stabile JSON-Form mit `mode =
"legacy_agrsich_validation_overview"` aus. Sie enthaelt Referenz-, Tabellen-,
Perioden-, Feldabweichungs- und Toleranzzaehler sowie die vorhandenen Datei-,
Perioden- und Feldsummaries. Die Toleranzangabe dokumentiert die heute genutzte
Vergleichsgrenze `legacy_compare_default` mit `0.05`; sie veraendert die
Vergleichslogik nicht.

Dieser Ueberblick startet keine Simulation, keinen Runner und keinen Scheduler.
Er schreibt keine Reportartefakte, oeffnet keinen HTTP- oder UI-Schreibpfad und
behauptet keine historische Vollgleichheit ausserhalb der konkret referenzierten
Legacy-Fenster.
