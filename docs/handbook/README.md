# IMS-Benutzerhandbuch

Stand: 2026-09-01
Handbuchstand: HB3a

Dieses Handbuch fuehrt Anwender durch die lokale IMS-Workbench und erklaert,
wie Bedienstatus und historische Vergleichsergebnisse zu lesen sind. Es ist
kein Entwicklerhandbuch und kein Nachweis, dass ein historischer Lauf mit
identischen Parametern und Zufallszahlen reproduziert wurde.

## Derzeit belegter Umfang

| Bereich | Status | Bedeutung |
| --- | --- | --- |
| Windows-Workbench | `verified_windows_hb3` | Kurzstart, portable Ablage, Entwickler-Checkout, Check, Start, Health, Stop, Datenpflege und Deinstallation sind dokumentiert und auf einem Leerzeichenpfad geprueft |
| Windows-Anwender-Testpaket | `documented_windows_hb3a` | Ein finales ZIP, lokale `.venv`-Installation, 2 Seiten Installationsdoku und 8 Seiten Bedienungsanleitung mit 5 datierten UI-Abbildungen sind vorbereitet und geprueft |
| Bedienpfad | `documented_hb2` | Dashboard, Szenarien, Runs, Validierung, Run-Control und Ergebnisanzeige sind beschrieben |
| Linux | `not_verified` | Noch kein freigegebener Installationsweg; Plattformnachweis folgt in HB4 |
| iOS/Juno | `feasibility_open` | Weder lokale Installation noch Support zugesagt; Entscheidung folgt in HB5 |
| Historische Kernvalidierung | `blocked_calculated_core_validation` | Nach PR101 sind 15/15 Tabellen und 6.300/6.300 Ergebniszeilen angeschlossen; die gemeinsame fachliche Bewertung folgt in PR102 |

## Kapitel

1. [Testpaket in zwei Seiten installieren](installation_test_package_windows.md)
2. [Testpaket in acht Seiten bedienen](user_guide_test_package.md)
3. [Windows-Kurzstart](quickstart_windows.md)
4. [Windows installieren](installation_windows.md)
5. [Workbench bedienen](operation.md)
6. [Ergebnisse und historische Validierung verstehen](results_and_validation.md)
7. [Daten, Backup und Updates](data_and_updates.md)
8. [Technische Quellen und Nachweise](technical_reference.md)

Die zusammengefasste Fehlerhilfe sowie gepruefte Linux- und iOS/Juno-Aussagen
folgen in HB4 bis HB6. Bis dahin bleiben fuer diese Plattformen die in der
technischen Referenz ausgewiesenen offenen Statuswerte massgeblich.

## Navigation in der Workbench

Die Workbench ist eine lange, lokal ausgelieferte Browseransicht. Die
Navigation springt zu vier stabilen Bereichen:

| Navigation | Inhalt |
| --- | --- |
| `Dashboard` | Systemstatus, Auswahlzusammenfassung und Betriebsdiagnose |
| `Szenarien` | vorhandene Szenarien, Filter und Detailauswahl |
| `Validierung` | Kernvalidierung, Vergleichsstatus und Grenzen |
| `Runs` | vorhandene Runs, Queue, Run-Control und Ergebnisanzeige |

## Begriffe

| Begriff | Einfache Bedeutung |
| --- | --- |
| Szenario | versionierte oder lokal bereitgestellte Beschreibung eines fachlichen Ausgangsstands |
| Run | ein zu einem Szenario gehoerender Laufdatensatz mit Periodenfenster und Status |
| Queue | kontrollierte Vormerkung eines Runs fuer den Run-Control-Ablauf |
| Dry-Run | prueft den Request und seine Grenzen, ohne den Adapter zu starten |
| Preflight | prueft technische Voraussetzungen vor einer Freigabe |
| explizite Freigabe | Person und Begruendung werden bestaetigt, bevor ein zulassiger Adapterstart moeglich wird |
| Adapter-Resultat | persistiertes Ergebnis des kontrollierten Adapters; nicht automatisch ein Simulationsresultat |
| historische Referenz | archivierte Ergebnisdatei zum diagnostischen Vergleich, nicht Eingabe fuer die moderne Berechnung |
| `blocked` | die fachliche Freigabe bleibt geschlossen; das bedeutet nicht automatisch, dass die Workbench technisch defekt ist |

## Verbindliche Grenzen

- Die Workbench darf technisch lauffaehig sein, obwohl die fachliche
  Produktionsfreigabe blockiert bleibt.
- `Adapter starten` bezeichnet den kontrollierten Adapterpfad. Daraus folgt
  keine Ausfuehrung des historischen Simulationskerns.
- Historische 300- und 500-Zeilen-Dateien werden als drei beziehungsweise
  fuenf getrennte Laeufe mit hoechstens 100 Perioden gelesen.
- Unterschiedliche damalige Parameter, Zinssaetze, Compiler und RNG-Folgen
  bleiben moeglich und teilweise unbelegt.
- `incomming/` ist lokaler Pruefbestand, kein Benutzer-Importordner und kein
  Bestandteil der versionierten Anwendung.
