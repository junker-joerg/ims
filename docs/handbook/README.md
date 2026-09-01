# IMS-Benutzerhandbuch

Stand: 2026-09-01
Handbuchstand: HB2

Dieses Handbuch fuehrt Anwender durch die lokale IMS-Workbench und erklaert,
wie Bedienstatus und historische Vergleichsergebnisse zu lesen sind. Es ist
kein Entwicklerhandbuch und kein Nachweis, dass ein historischer Lauf mit
identischen Parametern und Zufallszahlen reproduziert wurde.

## Derzeit belegter Umfang

| Bereich | Status | Bedeutung |
| --- | --- | --- |
| Windows-Workbench | `verified_local_workbench_path` | Build, portable Ablage, Startskript und technisches Release-Gate sind vorhanden; der zusammenhaengende Installationsweg folgt in HB3 |
| Bedienpfad | `documented_hb2` | Dashboard, Szenarien, Runs, Validierung, Run-Control und Ergebnisanzeige sind beschrieben |
| Linux | `not_verified` | Noch kein freigegebener Installationsweg; Plattformnachweis folgt in HB4 |
| iOS/Juno | `feasibility_open` | Weder lokale Installation noch Support zugesagt; Entscheidung folgt in HB5 |
| Historische Kernvalidierung | `blocked_calculated_core_validation` | Nach PR100 sind 12/15 Tabellen und 4.800/6.300 Ergebniszeilen angeschlossen; das ist keine Produktionsfreigabe |

## Kapitel

1. [Workbench bedienen](operation.md)
2. [Ergebnisse und historische Validierung verstehen](results_and_validation.md)
3. [Technische Quellen und Nachweise](technical_reference.md)

Der Windows-Kurzstart, die vollstaendige Windows-Installation, Datensicherung,
Fehlerhilfe sowie die geprueften Plattformkapitel werden in den folgenden
Handbuchschnitten ergaenzt. Bis dahin bleiben die bestehenden technischen
Quellen massgeblich; sie sind in der technischen Referenz verlinkt.

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
