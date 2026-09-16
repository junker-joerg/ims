# IMS-Benutzerhandbuch

Stand: 2026-09-16
Handbuchstand: HB3d

Dieses Handbuch fuehrt Anwender durch die lokale IMS-Workbench und erklaert,
wie Bedienstatus und historische Vergleichsergebnisse zu lesen sind. Es ist
kein Entwicklerhandbuch und kein Nachweis, dass ein historischer Lauf mit
identischen Parametern und Zufallszahlen reproduziert wurde.

## Derzeit belegter Umfang

| Bereich | Status | Bedeutung |
| --- | --- | --- |
| Windows-Workbench | `verified_windows_hb3` | Kurzstart, portable Ablage, Entwickler-Checkout, Check, Start, Health, Stop, Datenpflege und Deinstallation sind dokumentiert und auf einem Leerzeichenpfad geprueft |
| Windows-Anwender-Testpaket | `documented_windows_hb3b` | Ein finales ZIP, lokale `.venv`-Installation, 2 Seiten Installationsdoku und 10 Seiten fachliche Bedienungsanleitung mit 8 Abbildungen sind vorbereitet und geprueft |
| Managementseminar | `documented_management_hb3d` | Nichttechnischer 90-Minuten-Ablauf, sieben Nutzenargumente, Wirkungsketten-Arbeitsblatt, fuenf Abbildungen und ehrliche Ausbaugrenzen sind dokumentiert |
| Bedienpfad | `documented_hb2` | Dashboard, Szenarien, Runs, Validierung, Run-Control und Ergebnisanzeige sind beschrieben |
| Einperioden-Wirkungsprobe | `verified_browser_pr132` | Strategie-Kandidat, ausdrueckliche Freigabe, genau eine isolierte Periode, gespeichertes Ergebnis und Verlauf sind auf breitem und schmalem Viewport belegt |
| Zwei-Perioden-Wirkungsprobe | `verified_browser_pr141` | Gespeicherte Kette, ausdrueckliche Freigabe, zwei isolierte Perioden, VU-/VN-Carryover, unveraenderliches Ergebnis und Verlauf sind auf breitem und schmalem Viewport belegt |
| Fuenf-Perioden-Wirkungsprobe | `verified_browser_pr146` | Vorhandener Zwei-Perioden-Prefix, fuenf isolierte Perioden, vier VU-/VN-Uebergaenge, unveraenderliches Ergebnis und Verlauf sind auf breitem und schmalem Viewport belegt |
| Linux | `not_verified` | Noch kein freigegebener Installationsweg; Plattformnachweis folgt in HB4 |
| iOS/Juno | `feasibility_open` | Weder lokale Installation noch Support zugesagt; Entscheidung folgt in HB5 |
| Historischer Vergleich | `accepted_diagnostic_benchmark` | PR102 hat 15/15 Tabellen und 6.300/6.300 Ergebniszeilen als diagnostischen Legacy-Benchmark eingeordnet; historische RNG- und Feldvollgleichheit ist kein Produktziel |

## Kapitel

1. [IMS im Managementseminar](management_seminar_guide.md)
2. [Testpaket in zwei Seiten installieren](installation_test_package_windows.md)
3. [Testpaket in zehn Seiten bedienen](user_guide_test_package.md)
4. [Windows-Kurzstart](quickstart_windows.md)
5. [Windows installieren](installation_windows.md)
6. [Workbench bedienen](operation.md)
7. [Ergebnisse und historische Validierung verstehen](results_and_validation.md)
8. [Daten, Backup und Updates](data_and_updates.md)
9. [Technische Quellen und Nachweise](technical_reference.md)

Die zusammengefasste Fehlerhilfe sowie gepruefte Linux- und iOS/Juno-Aussagen
folgen in HB4 bis HB6. Bis dahin bleiben fuer diese Plattformen die in der
technischen Referenz ausgewiesenen offenen Statuswerte massgeblich.

Die aktive fachliche Ausbaufolge fuer 100 Perioden, Kfz, Sach-Haftpflicht,
Leben, Kranken, Versichererbilanzen, Solvency-II-Kapitalansicht,
DORA-Wirkungsketten und Managementbedienung steht in der
[IMS-2.x-Produkt-Roadmap](../plans/ims_2x_all_lines_management_lab_roadmap.md).

## Navigation in der Workbench

Die Workbench ist eine lange, lokal ausgelieferte Browseransicht. Die
Navigation springt zu fuenf stabilen Bereichen:

| Navigation | Inhalt |
| --- | --- |
| `Dashboard` | Systemstatus, Auswahlzusammenfassung und Betriebsdiagnose |
| `Szenarien` | vorhandene Szenarien, Filter und Detailauswahl |
| `Strategien` | Strategiekatalog, Entwuerfe, Snapshots sowie kontrollierte Einperioden-Kandidaten und Periodenketten |
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
| Strategie-Kandidat | unveraenderlich gespeicherte Kombination aus Marktgrundzustand, Strategiezuordnungen und VU-/VN-Snapshots fuer genau eine Periode |
| Einperioden-Wirkungsprobe | einmalige kontrollierte Anwendung dieses Kandidaten mit gespeichertem Vorher/Nachher-Nachweis; noch kein Mehrperiodenlauf |
| Periodenkette | unveraenderlich gespeicherte Folge periodenspezifischer Kandidaten mit ausdruecklichen VU-/VN-Carryover-Flags |
| Zwei-Perioden-Wirkungsprobe | kontrollierte Anwendung der Kandidaten fuer Periode 1 und 2 mit genau einem gespeicherten Uebergang; noch kein freier Mehrperioden- oder 100-Periodenlauf |
| Fuenf-Perioden-Wirkungsprobe | kontrollierte Anwendung von Periode 1 bis 5 mit vier gespeicherten Uebergaengen und exaktem Nachweis, dass Periode 1-2 stabil geblieben ist |
| Adapter-Resultat | persistiertes Ergebnis des kontrollierten Adapters; nicht automatisch ein Simulationsresultat |
| historische Referenz | archivierte Ergebnisdatei zum diagnostischen Vergleich, nicht Eingabe fuer die moderne Berechnung |
| `blocked` | die fachliche Freigabe bleibt geschlossen; das bedeutet nicht automatisch, dass die Workbench technisch defekt ist |

## Verbindliche Grenzen

- Die Workbench darf technisch lauffaehig sein, obwohl die fachliche
  Produktionsfreigabe blockiert bleibt.
- `Adapter starten` bezeichnet den kontrollierten Adapterpfad. Daraus folgt
  keine Ausfuehrung des historischen Simulationskerns.
- `Wirkungsprobe starten` fuehrt genau den geprueften Einperioden-Kandidaten
  aus. Carryover, Scheduler und Ergebnisdateien bleiben fuer diesen Pfad
  gesperrt.
- `Zwei Perioden starten` fuehrt genau eine gespeicherte Kette fuer Periode 1
  und 2 samt explizitem VU-/VN-Carryover aus. Freie Horizonte,
  100-Periodenlauf und Ergebnisdateien bleiben gesperrt.
- `Fuenf Perioden starten` fuehrt genau eine gespeicherte Kette fuer Periode
  1 bis 5 aus und prueft den Prefix 1-2 gegen ein unabhaengig gespeichertes
  Zwei-Perioden-Ergebnis. Laengere Horizonte und Ergebnisdateien bleiben
  gesperrt.
- Historische 300- und 500-Zeilen-Dateien werden als drei beziehungsweise
  fuenf getrennte Laeufe mit hoechstens 100 Perioden gelesen.
- Unterschiedliche damalige Parameter, Zinssaetze, Compiler und RNG-Folgen
  bleiben moeglich und teilweise unbelegt.
- `incomming/` ist lokaler Pruefbestand, kein Benutzer-Importordner und kein
  Bestandteil der versionierten Anwendung.
