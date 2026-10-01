# IMS installieren: Windows-Installer (AP1)

Aktueller AP3-Stand: **2.0.0-alpha.3**, Installer
`IMS-Setup-2.0.0-alpha.3-win-x64.exe` für Windows 11 x64.
Frühere AP1-/AP2- und erste AP3-Pakete trugen noch dieselbe Nummer alpha.1.
Auf dem Startbildschirm und allen Bereichen steht der Release-Stand unten links.
Bei unterschiedlichen Browser-/Anwendungsversionen erscheint dort ein Hinweis:
IMS neu starten und die Browserseite mit Strg+F5 neu laden.
Der Download enthält Python-Laufzeit, Backend, gebaute React-Oberfläche,
Beispiele, Diagnose-Referenzen, Profile, Hilfe und Lizenztexte. Auf dem
Zielrechner ist keine Installation von Python, Node.js, npm oder Git nötig.
Die Alpha-Funktionen und fachlichen Freigaben bleiben unverändert.
Der Auftraggeber hat AP1 am 01.10.2026 auf einem unabhängigen Windows-11-Rechner
abgenommen und zum Merge freigegeben. Die [Bestätigung mit ihren Nachweisgrenzen](../reports/ims_ap1_user_acceptance.md)
liegt vor; weitere Einzelheiten der externen Testumgebung wurden nicht mitgeteilt.

1. Installer und SHA-256 vom zugehörigen GitHub-Actions-Artefakt herunterladen.
   Prüfsumme mit dem veröffentlichten Nachweis vergleichen. Kein öffentliches
   Release ist damit freigegeben.
2. Installer im gewöhnlichen Benutzerkonto öffnen. Ziel ist standardmäßig
   `%LOCALAPPDATA%\Programs\IMS Workbench`; keine Administratorrechte nötig.
3. Im Startmenü „IMS Workbench“ öffnen. Nach erfolgreichem Health-Check öffnet
   sich der Standardbrowser. Das zusätzliche IMS-Fenster enthält Öffnen,
   Hilfe, Diagnose und Beenden.
4. Zum Beenden „IMS beenden“ im Fenster oder Startmenü verwenden. Browser-Tabs
   schließen beendet das Backend nicht. Laufende Rechnungen dürfen abschließen.

IMS bindet ausschließlich an `127.0.0.1`. Ein zweiter Start öffnet dieselbe
Instanz. Bei belegtem Port bietet der Launcher einen anderen lokalen Port an;
er öffnet niemals die fremde Anwendung. Unterstützungs-/Testoptionen sind
`--port`, `--no-browser`, `--headless`, `--stop` und `--data-dir`; die letzte
Option muss außerhalb der Installation liegen.

## Ablage, Update und Deinstallation

| Inhalt | Ort |
| --- | --- |
| Unveränderliche Anwendung | `%LOCALAPPDATA%\Programs\IMS Workbench` |
| Benutzerdaten | `%LOCALAPPDATA%\IMS\Workbench\metadata.sqlite` |
| Übernahme-Backups | `%LOCALAPPDATA%\IMS\Workbench\backups` |
| Rotierende Startprotokolle | `%LOCALAPPDATA%\IMS\Workbench\logs` |
| Temporäre Instanzsteuerung | `instance.lock` / `instance.json` in der Benutzerablage |

Updates im selben Benutzerkonto installieren. Setup fordert die laufende
Instanz zum kontrollierten Beenden auf und wartet auf die freigegebene
Instanzsperre, bevor Dateien ersetzt werden. Antwortet IMS nicht oder rechnet
zu lange, bricht die Vorbereitung verständlich ab. Daten werden nicht
zurückgesetzt; alle bisherigen fachlichen Speicherfreigaben bleiben nötig.

Deinstallation entfernt Anwendungsdateien und Startmenüeinträge. Daten und
Backups bleiben erhalten; Neuinstallation verwendet sie erneut. Vor Updates
eine externe Datensicherung anlegen. In AP1 gibt es bewusst keine automatische
Löschoption für die Benutzerablage.

## Explizite Übernahme alter Daten

Alte und neue Anwendung zuerst beenden. „Bestehende IMS-Daten übernehmen“
im Startmenü öffnen, die alte `.ims_workbench/metadata.sqlite` wählen und die
Übernahme bestätigen. IMS erstellt SQLite-Snapshots der importierten Daten
und der gegebenenfalls vorhandenen Zieldatenbank, einschließlich committed
WAL-Seiten. Erst nach erfolgreichen Sicherungen ersetzt es die Zielbasis.
Die Quelle wird nicht verändert. Andere Dateien und externe Quellpfade
werden nicht verschoben oder automatisch umgeschrieben; sie separat sichern.
Für unterstützte manuelle Wiederherstellung eine gesicherte `.sqlite` über
denselben Übernahmeweg wählen. Keine rohe Kopie offener WAL-Dateien durchführen.

Diagnoseexport enthält Version und Startprotokolle, keine Datenbank,
Modell-Eingaben, Backups oder Instanzschlüssel. Protokolle können lokale Pfade
enthalten; vor Weitergabe prüfen.

## Unterstützung und Grenzen

Der Installer ist unsigniert. SmartScreen oder Unternehmensrichtlinien können
Warnungen anzeigen oder die Ausführung sperren; in diesem Fall den zuständigen
Support kontaktieren. Signierung und öffentliche Veröffentlichung benötigen
eine eigene Entscheidung. Windows 10 sowie ARM64 sind nicht abgenommen.

Die vorhandene [Bedienungsanleitung](user_guide_test_package.md) bleibt die
fachliche Anleitung. Der Installer begründet keine historische Vollgleichheit,
regulatorische SCR/MCR-Kennzahlen oder DORA-Konformität. Referenz-/Replay-
Diagnosen bleiben von berechneten Modellergebnissen getrennt.

Details für Entwickler: [Build und Ressourceninventar](../migration/ims_ap1_windows_installer.md).
Abnahme ohne Entwicklerwerkzeuge: [Checkliste](../reports/ims_ap1_clean_windows_acceptance.md).
