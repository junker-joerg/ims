# AP1: vorbereitete Clean-Windows-Abnahmematrix

Status: **Produktabnahme durch Auftraggeber bestätigt am 01.10.2026**.
AP1 wurde auf einem unabhängigen Windows-11-Rechner getestet und freigegeben.
Die tatsächliche Erklärung und ihre Nachweisgrenzen stehen in
[ims_ap1_user_acceptance.md](ims_ap1_user_acceptance.md).
Diese vorbereitete Matrix ist kein nachträglich erzeugtes Einzeltestprotokoll.
P52 und GitHub Windows Runner enthalten Entwicklerwerkzeuge. Ein
eingeschränkter PATH oder grüner CI-Lauf ersetzt den externen Test nicht.

## Testumgebung vorbereiten

Windows 11 x64 neu aufsetzen (VM oder vorhandene Windows Sandbox), gewöhnliches
Benutzerkonto, keine Python-/Node-/npm-/Git-Installation. OS-Build, Kontotyp,
Prüfer und Datum/Uhrzeit Europe/Berlin protokollieren. Frische VM-Basis sichern.
Installer, SHA-256 und optional synthetischen Vorgänger aus demselben grünen
CI-Run herunterladen. Run-Link, Commit und tatsächliche Hashes festhalten.
Netzwerk nach Download deaktivieren. Nur dieses Prüfpaket in die VM übertragen.
`prepare-clean-windows.ps1` erstellt dafür einen lokalen Kit-Ordner und eine
Sandbox-Konfiguration ohne Netzwerk; es startet/aktiviert die Sandbox nicht.

## Vollständige Abnahmematrix

Die folgenden Abläufe sind die vorbereiteten Prüfkriterien. Einzelbelege zur
externen Abnahme wurden nicht übermittelt und werden hier nicht erfunden.

| Prüfung | Ablauf / erwartetes Verhalten | Nachweis |
| --- | --- | --- |
| Saubere Umgebung | Windows 11 x64, Standardbenutzer; Entwicklerwerkzeuge fehlen, Netzwerk aus | OS-/Kontonachweis, installierte Programme, Datum |
| Installation | Doppelklick; keine UAC-/Paketinstallation; Ziel mit Leerzeichen/Ü wählen | Setup-Log, Bildschirmbild, Commit/Hash |
| Startmenü/Doppelklick | IMS starten, Browser erst bei Bereitschaft; komplette Oberfläche und Hilfe offline | Screenshots Launcher/Oberfläche/Hilfe |
| Zweitstart | Startmenü erneut öffnen: gleiche Instanz, zweiter Browserzugriff möglich | Prozessliste vorher/nachher |
| Portkonflikt | Eine erste IMS-Instanz in separater Testablage auf Port 8000 starten, dann normale Instanz; Dialog und Auswahl eines anderen Ports prüfen | Dialog/Screenshot, lokale Adressen; beide Instanzen beenden |
| Loopback | Nur 127.0.0.1 lauscht, keine externe Schnittstelle | Netzwerk-/Prozessnachweis |
| Modellfall | Vorhandenen Kranken-Zwei-Perioden-Baselinefall anzeigen, Vorschau berechnen, Speicherfreigabe bewusst bestätigen | Eingabe-/Ergebnis-Digest, zwei Perioden, Screenshot |
| Export | JSON, CSV, XLSX herunterladen und öffnen; Inhalte stimmen mit Anzeige überein | Exportdateien und Digests |
| Diagnose | ZIP über Launcher speichern; keine Datenbank/Backups/Instanzschlüssel | ZIP-Inhaltsliste |
| Beenden | Browser schließen lässt IMS laufen; „IMS beenden“ und Fensterschließen stoppen Backend | Prozessliste/Port vorher/nachher |
| Übernahme | Bestehende metadata.sqlite explizit auswählen/bestätigen; Quell- und Zielbackup erhalten, Quelle unverändert | Backup-Dateien, Hash der Quelle, Ergebnis nach Neustart |
| Update | Synthetischen Vorgänger installieren, Ergebnis speichern; neuesten Installer bei laufendem IMS ausführen | Setup-Logs, beendeter Prozess, erhaltenes Ergebnis |
| Deinstallation | Laufendes IMS kontrolliert beenden; Anwendung/Startmenü weg, Daten/Backups erhalten | Prozess-/Dateiliste |
| Neuinstallation | Neu installieren und erhaltenes Ergebnis erneut öffnen/exportieren | Digest/Exportvergleich |
| Unsigniert | Etwaige SmartScreen-/Richtlinienmeldung protokollieren; keine Schutzumgehung | Meldung und ggf. Supportentscheidung |

Portkonflikt ohne Entwicklerwerkzeuge: Zwei Verknüpfungen derselben EXE mit
unterschiedlichem `--data-dir` (außerhalb der Installation) und `--port 8000`
verwenden. Die erste belegt den Port; die zweite muss einen verständlichen
Dialog zeigen. Nachher beide Instanzen über ihre Fenster beenden.

## Belegablage und Freigabe

Belege in `docs/reports/` bzw. als zugängliches PR-Artefakt ablegen, keine
sensiblen realen Nutzerdaten veröffentlichen. Testmatrix mit Umgebung,
Ergebnis und konkretem Beleg vervollständigen. Erst nach allen Prüfungen,
Windows-Release-Gate und grünen erforderlichen CI-Checks AP1 im Manifest
auf done setzen, echte completion_evidence eintragen und PR Ready stellen.
Merge/öffentliches Release bleiben einer gesonderten Freigabe vorbehalten.
