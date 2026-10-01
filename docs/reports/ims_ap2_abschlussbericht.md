# IMS | AP2 Abschlussbericht – Oberfläche

**In main übernommen.** Stand: 01.10.2026, 09:48:11 Uhr Europe/Berlin (UTC+02:00).
[PR #289](https://github.com/junker-joerg/ims/pull/289), Branch
`codex/ims-elegant-workbench`. AP2 ist im Manifest done mit echten Nachweisen.
Der Auftraggeber bestätigt am 01.10.2026 einen erfolgreichen Test auf einem
anderen Rechner und beauftragt AP3. Weitere Oberflächenverbesserungen folgen
später. AP2 wurde am 01.10.2026 um 09:48:11 Uhr Berlin in main übernommen,
Merge-Commit **2e70b8f814870807a7c8c34d8fc384f8f6a5bb3c**.
Zuletzt geprüfter PR-Head: **0148efc2359a2de3880cdd69889486f9c562626a**.
Alle vier Checks dieses abschließenden Heads waren vor dem Merge grün:
[Release-Gate](https://github.com/junker-joerg/ims/actions/runs/36826117298/job/110252081170),
[Installer](https://github.com/junker-joerg/ims/actions/runs/36826117453/job/110252074511),
[Browser](https://github.com/junker-joerg/ims/actions/runs/36826117379/job/110252074013),
[Plan](https://github.com/junker-joerg/ims/actions/runs/36826117311/job/110252073813).

AP1 ist nach unabhängiger Windows-11-Abnahme durch den Auftraggeber und
ausdrücklicher Freigabe mit [PR #288](https://github.com/junker-joerg/ims/pull/288)
in main übernommen. AP2-Basis: `965156caf02734cc47e93615c1f8ca91692d51fe`.
Geprüfter AP2-Produktcode: **7dc368ec5defb5754ba037a80b2bfa2ae2251d60**.
Vier Checks dieses Heads sind grün: Plan, Browser, Installer, Release-Gate.

## Anwendernutzen

Übersicht, Szenario, Simulation, Ergebnisse und Hilfe gliedern vorhandene
Funktionen. Hell-/Dunkelmodus, gemeinsame Farben, Systemschrift, Abstände,
Radien, sichtbarer Fokus und eine mobile Navigation erleichtern die Bedienung.
Die bisher funktionslose Aktion „Neuer Lauf“ ist durch tatsächliche Navigation
zum bestehenden Modellfall ersetzt. Es werden keine noch nicht verfügbaren
Funktionen angeboten.

Bereiche wechseln erhält Eingaben, Ergebnisse und ausdrückliche Freigaben.
Dieselben Modellinstanzen bleiben gemountet. Geänderte Eingaben entwerten die
davon abhängigen Ergebnisse und Nachweise weiterhin. Ergebnisse zeigen echte
Resultate, vorhandene Speicher-/Exportaktionen und lokale Fallverläufe.
Technische Vertrags-/Diagnosedetails sind aufklappbar. Breite Tabellen scrollen
innerhalb ihrer Fläche; Freigaben, Herkunft und Modellgrenzen bleiben sichtbar.

## Ursprung und Umsetzung

| Ursprung | AP2-Anschluss | Grenze |
| --- | --- | --- |
| Bestehende React-Ansichten in `main.tsx` | `WorkbenchShell.tsx`, Bereichs-/Modellhüllen, Hash-Navigation mit Direktlinks/Zurück/Vorwärts | Berechnungs-, API- und Zustandslogik erhalten |
| Vorhandene fünf Modell-Workbench-Komponenten | Navigation/Ergebnisansicht; benannte Inhaltsgruppen mit gültigen ARIA-Roles | Gleiche Berechnungen, Quellen-/Digest-Prüfungen und ausdrückliche Speicher-/Ausführungsfreigaben |
| Komponentenstile | Variablen in `styles.css`, gemeinsame Shell/Controls in `WorkbenchShell.css` | Warn-/Fehlertexte bleiben benannt |
| Drei vorhandene Modell-Browsernachweise | Gepinnte Playwright-/axe-Läufe, `legacy-models.spec.ts` | Quellen, Bilanzgleichung, Stale-/Fehler- und Exportprüfungen erhalten |
| AP1-Installer-Lifecycle | Browsermatrix gegen installierte aktuelle EXE, in CI verbindlich | Build/Test-Harness und laufzeitfreies Anwenderpaket getrennt |

Der AST-Abgleich mit main bestätigt 357 unveränderte App-Anweisungen vor dem
UI-Return sowie 22/34/30/29/29 in den fünf Modellkomponenten. Python-Kern und
historische Quellen haben keinen Diff. Das belegt die Begrenzung des Eingriffs;
es ist keine neue Behauptung historischer Vollgleichheit. Der geführte
100-Perioden-Mehrspartenablauf bleibt AP3 zugeordnet.

## Testmatrix

| Prüfung | Umgebung | Ergebnis und Nachweis |
| --- | --- | --- |
| TypeScript/Vite-Build | P52 und Windows-CI | Bestanden |
| Elf Bereichs-/Modellansichten × drei Viewports × zwei Farbmodi | 1440×900, 1024×768, 390×844, reales Chromium 153 | 66 Ansichten, kein Seitenüberlauf; axe ohne Befunde; alle sichtbaren Buttons/Hauptlinks und Checkbox-Labels mindestens 44×44 |
| Textkontrast einschließlich großer Schrift | Beide Modi, dieselben 66 Ansichten | Minimum **6,13:1**, 5.480 Textbeobachtungen; gefordert mindestens 4,5:1 |
| Kernpfad/Fehlerkorrektur/Formularzustand/Freigabe/Downloads | Kranken bis 100 Perioden | Echte CSV/JSON/XLSX, explizites Speichern, Verlauf, veränderte Eingabe entwertet Ergebnis und Freigabe; Lade-/API-Fehler werden korrigiert |
| Vorhandene Spartenkette bis Kapitalwirkung | Drei vorhandene Browsernachweise | Spartenquellen, beide Varianten, Bilanzgleichung, Digest, Exportfehler, ungültige/veraltete Eingaben und regulatorische Nichtberechnung bestanden |
| Tastatur und Details | Echter Browser | Fokus, Zum-Inhalt-Link, Zurück/Vorwärts, Farbmodus nach Reload, reduzierte Bewegung, aufklappbare Details, Pfeiltasten in fokussierter Tabelle bestanden |
| Zwölf vollständige Browserfälle gegen installierte EXE | P52 / CI | **12/12** bestanden, keine ausgelassenen oder flaky Fälle |
| Tatsächlicher Installer-Lifecycle | P52 / CI | **14/14** bestanden: Installation, Start, Zweitstart, Update/Deinstallation bei laufendem IMS, Neuinstallation, Exporte, Backups/Datenerhalt, Portkonflikt, Browsermatrix |
| Bestehender Windows-Release-Gate | P52 / CI | **2.597 Tests + 8 Subtests** und gesamter Gate bestanden; fachliche Produktionsfreigabe bleibt false |
| Gezielt nach Quellen-/ARIA-Korrekturen | Checkout-.venv | 33 Quellen-/Anschlussprüfungen bestanden, 0,84 s |
| Anderer Rechner, externe AP2-Abnahme | Erklärung des Auftraggebers am 01.10.2026 | „Habe AP2 auf einem anderen Rechner getestet. Es funktioniert.“; Betriebssystem, Einzelprüfungen und Dauer nicht angegeben |

Vollständige Evidenz: [P52](ims_ap2_p52_evidence.json),
[CI](ims_ap2_ci_evidence.json), [CI-Release-Gate](https://github.com/junker-joerg/ims/actions/runs/36824042714).
Playwright 1.63.0 und axe-Playwright 4.13.0 sind exakt gepinnt, Chromium wird
reproduzierbar installiert. Die Browserprüfung startet eine eigene temporäre
Ablage oder prüft über `IMS_BASE_URL` die installierte EXE. Der lokale Gate
startete bei 25c2166 und endete bei 7dc368e; währenddessen wurden ausschließlich
ARIA-Gruppen ergänzt, danach gesondert Quelle und Browser geprüft. **CI prüfte
7dc368e vollständig als festen Stand.** Die genaue GitHub-Testmerge-SHA steht
im CI-Buildnachweis und ist vom PR-Head getrennt.

Die automatisierten Prüfungen ersetzen keine umfassende Screenreader-Abnahme.
Vorher-/Nachher-Bilder und [aktuelle Bedienhilfe](../handbook/workbench_ap2.md)
liegen vor: 6 Ausgangs- und 18 Ergebnisbilder. Der Ausgangsstand hatte bei
1024 Pixel einen Seitenüberlauf bis 1201 Pixel. Die neue Matrix hat keinen
Seitenüberlauf. Breite Datentabellen bleiben innerhalb ihrer Fläche scrollbar.

## Installer, Download und Prüfsummen

**Tatsächlicher CI-Download:**
[Installer und vollständige Nachweise](https://github.com/junker-joerg/ims/actions/runs/36824042759/artifacts/11144572266)
aus [Installer-Run 36824042759](https://github.com/junker-joerg/ims/actions/runs/36824042759).
Actions liefert ein ZIP, kein öffentliches Release. Artefaktablauf laut GitHub:
31.10.2026. EXE-Version weiterhin `2.0.0-alpha.1`; für diesen AP2-Stand gelten
der angegebene Quellcommit und diese Prüfsummen.

- CI-EXE **IMS-Setup-2.0.0-alpha.1-win-x64.exe**, 18.219.208 Bytes.
  SHA-256: `1680b5521c61e51347de52bcd08669c83f50a6997c47942563a0ffb238756d24`.
- ZIP-Artefakt (andere Datei), SHA-256: `ff9333f8a707411cc25f0b73c0e3b92f10d7b970e25f88d0129631f6710ee1e2`.
- **Nur lokal auf P52:** `C:\Users\P52\source\ims\dist\installer\IMS-Setup-2.0.0-alpha.1-win-x64.exe`,
  18.254.745 Bytes; SHA-256 `60f02ee9c5ad93301f7216014c1781421e6ea4aa1aafab180a9c5baa14dd5ca9`.
  Sauberer Build von 7dc368e (`dirty=false`). Lokaler und CI-Build sind
  getrennt; bitidentische PE-Dateien werden nicht behauptet.

CPython 3.12.10 x64, PyInstaller 6.22.3, Inno Setup 6.7.3. Installer unsigniert.
EXE-Tests laufen mit nur System32 im PATH und unerreichbaren Proxies; die
Testumgebung hat Entwicklerwerkzeuge. Das ist kein neuer Clean-VM-Nachweis.
Die aktuelle Offline-Hilfe ist gebündelt; die ältere Modell-PDF wird als
solche eingeordnet. Update/Deinstallation erhalten Nutzerdaten, vorhandene
Übernahme sichert Quell-/Zieldaten ausdrücklich. Der synthetische Vorgänger
prüft den Setup-Lifecycle, keine fachliche Versionsmigration.

## Gemessene Zeiten

| Vorgang | P52 | CI |
| --- | ---: | ---: |
| Sauberer Installer-Build | 82,638 s | 52,747 s |
| Vollständiger Installer-Lifecycle inkl. Browser | 199,541 s | 152,042 s |
| Darin vollständige Browsermatrix | 132,928 s | 126,592 s |
| Start / Zweitstart P52 | 2,641 s / 0,251 s | — |
| Update bei laufendem IMS P52 | 14,879 s | — |
| Deinstallation / Neuinstallation P52 | 1,857 s / 5,556 s | — |
| Gesamter Windows-Release-Gate P52 | 894,933 s | siehe CI-Log |
| Darin pytest P52 | 857,39 s | siehe CI-Log |

Gesamte aktive Bearbeitungszeit, Nacharbeitszeit und externe AP2-Prüfdauer:
**unbekannt**. Prüfläufe überschneiden sich; keine Summierung als vermeintliche
Gesamtarbeitszeit oder Schätzung als Messung.

## Freigabe, Grenzen und Ablage

AP2 ist extern abgenommen und in main übernommen; Merge und main wurden
erneut aus GitHub/origin verifiziert. Der Folgeauftrag autorisiert genau AP3.
Vor dessen Umsetzung wird dieser ausführliche Bericht in Evernote abgelegt.
Weitere Verbesserungen der Oberfläche bleiben einer späteren Lieferung
vorbehalten. Keine öffentliche Veröffentlichung.
Historische Vollgleichheit, gesetzliche Bilanz und regulatorische SCR/MCR-
Berechnung bleiben unverändert nicht behauptet; der Release-Gate meldet die
bekannte fachliche Produktionssperre und 15 fehlende berechnete Kernexporte.

Der vollständige Bericht bleibt zusätzlich im Repository und PR gesichert.
Evernote-Ziel: Notizbuch `MK | 80 IMS1995-2026`, ID
`ade45e59-57bd-4ada-abaf-dab970f2e126`; Titel
`IMS | AP2 Abschlussbericht – Oberfläche`. Die gezielte Suche nach AP2 im
Zielnotizbuch ergab vor dem Anlegen keine vorhandene Notiz. Das Notizbuch wurde
über seine sichtbare Ansicht und URL mit der vorgesehenen ID verifiziert.
Die [Evernote-Notiz](https://www.evernote.com/client/web#/notebook/ade45e59-57bd-4ada-abaf-dab970f2e126/note/18c2dc8d-2534-6cd5-20ae-1c862506946c)
wurde vor AP3 gespeichert. Nach vollständigem Neuladen wurden Titel, Notizbuch,
Merge, Prüfsummen, vollständige Test-/Zeittabellen und Grenzen erneut gelesen;
der Editor bestätigte „Alle Änderungen gespeichert“. Der verifizierte Inhalt
umfasst 10.228 Textzeichen einschließlich der Editor-Überschriftverweise.
Keine Dublette zur Abschlussautomatik. Die zusätzliche native Bildschirmaufnahme
wurde mangels sicher erkannter Browser-URL abgebrochen; die erfolgreiche
Browser-Leseprüfung bleibt der Ablagenachweis.
Die ältere AP1-Notiz muss gesondert mit Abnahme/Merge aktualisiert werden.
