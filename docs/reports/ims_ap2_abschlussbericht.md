# IMS | AP2 Abschlussbericht – Oberfläche

**Zwischenstand: Umsetzung vorhanden, technische Abnahme läuft.**
Stand 01.10.2026, Europe/Berlin (UTC+02:00).
AP1 wurde nach ausdrücklicher unabhängiger Windows-11-Abnahme in
[PR #288](https://github.com/junker-joerg/ims/pull/288) gemergt; main
`965156caf02734cc47e93615c1f8ca91692d51fe` ist die verifizierte AP2-Basis.
AP2 ist im [Draft-PR #289](https://github.com/junker-joerg/ims/pull/289),
Branch `codex/ims-elegant-workbench`. AP2 ist noch nicht nach main übernommen.

## Anwendernutzen und Umsetzung

Fünf Bereiche gliedern die vorhandenen Funktionen: Übersicht, Szenario,
Simulation, Ergebnisse und Hilfe. Hell-/Dunkelmodus, gemeinsame Farben,
Systemschrift, Abstände, Radien, sichtbarer Fokus und eine mobile Navigation
machen die Oberfläche konsistent. Die bisher funktionslose Aktion „Neuer Lauf“
ist durch tatsächliche Navigation zum bestehenden Modellfall ersetzt.

Beim Navigieren bleiben Eingaben, Ergebnisse und ausdrückliche Freigaben
erhalten. Dieselben Modellinstanzen bleiben gemountet; geänderte Eingaben
entwerten ihre Nachweise und abhängigen Quellen weiterhin. Ergebnisse zeigen
tatsächliche Resultate, Speicheraktionen und vorhandene Verläufe. Breite
Tabellen scrollen in ihrer Fläche. Technische Diagnose-/Vertragsdetails sind
aufklappbar; Herkunft, Modellgrenzen und Ausführungssperren bleiben sichtbar.

| Ursprung | AP2-Anschluss | Fachliche Grenze |
| --- | --- | --- |
| Vorhandene React-Ansichten in `main.tsx` | `WorkbenchShell.tsx`, Bereichs-/Modellhüllen | Keine Änderung der API-Anfragen oder Ausführungserlaubnisse |
| Bestehende Kfz/Sach-, Leben-, Kranken-, Gesamtbilanz- und Kapitalmodule | Gemeinsame Navigation und lokale Ergebnisansicht | Dieselben Berechnungen, Quellprüfungen, Digest-/Export- und Speicherfreigaben |
| Vorhandene Komponentenstile | Farbvariablen in `styles.css`, Shell/Controls in `WorkbenchShell.css` | Warnung/Fehler bleiben benannt; keine neue Fachsemantik |
| Drei vorhandene Modell-Browsernachweise | Gepinnte Playwright-Läufe und `legacy-models.spec.ts` | Vorhandene Quellen-/Digest-/Export-Prüfungen erhalten |
| AP1-Installer-Lifecycle | Optionale vollständige AP2-Browserprüfung gegen installierte EXE, in CI verbindlich | Developer-Harness ist vom laufzeitfreien Anwenderpaket getrennt |

Historische C-Regeln, Terminal-UI, Python-Simulationskern, Seeds und API-Verträge
bleiben unverändert. Der geführte 100-Perioden-Mehrspartenablauf gehört zu AP3.

## Teststand

Produktcommit `ef18086fbd03aec7138cbf7bdcbb90a060d59674`; die anschließende
CI-Korrektur `4ead38e1667cd5b79e964881380e06940a0ef8e4` installiert das
vorhandene Python-Web-Extra für den neu eingerichteten Browserjob.
Alle UI-Produktdateien sind zwischen diesen Commits identisch.

| Prüfung | Umgebung | Stand |
| --- | --- | --- |
| Frontend-Build | P52, Node 22.23.2, TypeScript/Vite | Bestanden |
| Zwölf echte Browserfälle | P52, gepinntes Chromium 153, Playwright 1.63.0, axe 4.13.0 | Bestanden; 2,3 Minuten gemessen, vollständiger JSON-Bericht lokal |
| Quelle, Handbuch, Sprintplan | Checkout-Python 3.12.10 | 46 Tests und 8 Subtests bestanden, 0,92 s |
| Drei Viewports, beide Farbmodi, alle Bereiche/Modellfälle | 1440×900, 1024×768, 390×844 | Kein Seitenüberlauf, axe ohne Befunde; wesentliche Hauptaktionen mindestens 44×44 |
| Fehlerkorrektur, Zustand/Freigabe, echte CSV/JSON/XLSX, Tabellen-Tastatur | Vorhandener Krankenfall mit 100 Perioden | Bestanden |
| Vier-Sparten-Kette und Kapitalmodell | Vorhandene Browsernachweise | Quellen, Bilanzgleichung, Digest, Exportfehler, veraltete Eingaben und regulatorische Nichtberechnung bestanden |
| Sauberer aktueller Installer-Build | P52 | Bestanden; `dirty=false`, 73,456 s |
| Echter Installer-Lifecycle mit Browsermatrix | P52, eingefrorene EXE ohne Entwickler-PATH und mit unerreichbaren Proxies | Läuft; vollständiger Nachweis noch ausstehend |
| Bestehender Windows-Release-Gate | P52 | Läuft |
| Aktuelle CI | GitHub Windows | Läuft; erster Browserjob ohne Web-Extra scheiterte vor Start, Korrektur gepusht |
| Unabhängiger Windows-11-Rechner | Erklärung des Auftraggebers zu AP1 | AP1 abgenommen; keine neue externe AP2-Prüfung behauptet |

Die automatisierte Farbprüfung fordert zusätzlich zum axe-Standard mindestens
4,5:1 auch für große Texte. Die Nachweise dieser verschärften Prüfung werden
im Installer-/CI-Browserbericht gesammelt; vor Abschluss nicht als bestanden
vorausgesetzt. Die automatisierten Prüfungen ersetzen keine umfassende
manuelle Screenreader-Abnahme.

Vorher-/Nachher-Bilder: [Bedienhilfe](../handbook/workbench_ap2.md).
Der Ausgangsstand zeigte bei 1024×768 einen Seitenüberlauf bis 1201 Pixel;
zusätzliche Überläufe in Szenario-/Expertentabellen wurden in der neuen Matrix
gefunden und korrigiert. Die neue Matrix prüft alle elf Bereichs-/Modellansichten.
24 Bilder sind im Repository gesichert (6 vorher, 18 nachher).

## Installer und Zeiten

Lokal auf P52: `dist/installer/IMS-Setup-2.0.0-alpha.1-win-x64.exe`,
18.248.983 Bytes; SHA-256
`b82295f38e4026458ad5a443318c8593e4a08e7f3301eb0b04f826b0fd79e7ee`.
Dies ist der saubere Build von ef18086, kein öffentlicher Download.
Ein tatsächlicher CI-Artefaktlink und dessen eigener SHA-256 werden nach
erfolgreicher Prüfung ergänzt. Unterschiedliche lokale/CI-PE-Dateien werden
nicht als bitidentisch behauptet. Installer weiterhin unsigniert.

Messwerte: Frontend-Build zuletzt 3,06 s Vite-Zeit (ohne TypeScript),
Browsermatrix 2,3 Minuten gerundete Playwright-Ausgabe, gezielte pytest-Prüfung
0,92 s, sauberer Installer-Build 73,456 s. Gesamte aktive Bearbeitungszeit,
Nacharbeitszeit und externe AP2-Prüfdauer sind unbekannt. Läufe überschneiden
sich; keine Summierung als vermeintliche Gesamtarbeitszeit.

## Offene Schritte, Grenzen und Ablage

Installer-Lifecycle/Browsertest, Windows-Release-Gate und aktuelle CI vollständig
abschließen. Danach Evidenz und Manifest aktualisieren; Ready erst nach grünen
Checks des aktuellen PR-Heads. AP2-Merge ist nicht freigegeben. AP3 bleibt
geplant und wartet auf AP2 in main sowie einen Folgeauftrag. Keine öffentliche
Release-Veröffentlichung. Fachliche Vollgleichheit, gesetzliche Bilanz und
SCR/MCR-Berechnung bleiben unverändert nicht behauptet.

Evernote-Werkzeuge sind in dieser Sitzung nicht verfügbar. Der vollständige
Bericht wird entsprechend der erlaubten Ausweichablage im Repository und PR
gesichert. Notizbuch `MK | 80 IMS1995-2026`, ID
`ade45e59-57bd-4ada-abaf-dab970f2e126`; Solltitel
`IMS | AP2 Abschlussbericht – Oberfläche`. Vor späterem Speichern dieselbe
PR-Notiz suchen, aktualisieren und erneut lesen; keine Dublette zur
GitHub-Abschlussautomatik anlegen. Ablage und Notizbuch-Verifikation sind
**ausstehend**. Auch die bestehende AP1-Notiz muss noch mit Abnahme/Merge
aktualisiert werden.
