# IMS: gebündelte Lieferung, einfache Installation und neue Workbench

Stand: 30.09.2026. Planungsvorschlag; Umsetzung nach Annahme dieses Planungs-PRs.
Basis: main **3659b47fe01c2cb89be565cfce003e105c721b49**.

## Entscheidungsvorschlag

**Drei Umsetzungs-PRs**: AP1 Installer, AP2 Oberfläche, AP3 fachliche Integration.
Die bisherigen 25 geplanten Schnitte werden zu zwei dieser PRs: zwei
Distributionsschritte in AP1 und alle 23 Fachschritte in einem gemeinsamen AP3.
AP2 ergänzt die ausdrücklich gewünschte neue Oberfläche.
Dieser kleine Planungs-PR zählt zusätzlich; er implementiert keine Produktfeatures.

Ein einziger PR für alle drei Pakete ist technisch möglich. Er würde jedoch
Paketierung, breite UI-Änderungen und noch offene fachliche Entscheidungen
gleichzeitig blockieren. Daher empfehlen wir drei separat abnehmbare Lieferungen.
Bei späterer Entscheidung für einen Gesamt-PR bleiben die internen Abnahmen
erhalten; die PR-Gruppierung wird dann explizit im Plan angepasst.

Keine Aufteilung mehr in einen PR je DTO, API-Endpunkt, UI-Tab oder Dokument.
Zusammenhängende Implementierung, Tests, Anleitung und Korrekturen gehören in
dasselbe Arbeitspaket. Größere Pakete dürfen mehrere Sitzungen umfassen; der
Agent beendet nicht nach dem ersten Teilschritt den fachlichen Auftrag.

## Was war bisher geplant?

Bei der Abfrage am 30.09.2026 gab es **0 offene GitHub-Pull-Requests**.
Mit den offenen PRs sind deshalb die **25 noch geplanten Schritte** gemeint.
Die Bezeichnungen PR179 usw. sind interne Plan-IDs, keine GitHub-PR-Nummern.
Diese Umplanung bündelt Anforderungen; es wurden keine bestehenden PR-Inhalte
zusammengeführt oder PRs geschlossen.

Die [Roadmap vom 18.09.2026](ims_2x_all_lines_management_lab_roadmap.md)
und der [Restplan ab PR179](ims_2x_restplan_ab_pr179.md) bleiben die
historische Anforderungsquelle. Deren Reihenfolge und kleine PR-Schnitte
werden durch diesen Vorschlag ersetzt, deren fachliche Grenzen bleiben erhalten.

| Bisheriger Block | Plan-IDs | Anzahl | Neue Zuordnung |
| --- | --- | ---: | --- |
| ICT-/DORA-Wirkungsketten | PR179–186 | 8 | AP3, Meilenstein M1 |
| Szenarioassistent und geführte 100er-Kette | PR187, PR187a–c | 4 | AP3, M2 |
| Vier Sparten über 100 Perioden | PR187d–f | 3 | AP3, M3 |
| Wirksame VU-/VN-Strategien je Sparte | PR187g–k | 5 | AP3, M4 |
| Seminarfälle, Moderation, End-to-End-Abnahme | PR188–190 | 3 | AP3, M5 |
| Windows-Bundle und Doppelklick-Verteilung | PR191–192 | 2 | AP1, vorgezogen |
| Neue Produktgestaltung | zusätzlicher Auftrag | — | AP2 |
| **Summe bestehender Restumfang** | | **25** | **2 PRs plus neuer UI-PR** |

Die alte grobe Schätzung von 8.000–16.000 zusätzlichen Codezeilen ist eine
ungeprüfte Planannahme. Eine kleinere PR-Zahl reduziert nicht automatisch diesen
fachlichen Aufwand. Nach AP1 und dem Strategie-Quellenmapping wird neu geschätzt.

## AP1: Eine Installationsdatei für Anwender

**Ergebnis:** Ein Download, etwa IMS-Setup-2.x.x-win-x64.exe. Doppelklick,
Installation im Benutzerkonto, IMS über das Startmenü starten. Auf dem
Zielrechner sind kein Python, Node.js, npm, Git und keine Paketinstallation nötig.
Der eingerichtete P52 bleibt eine Entwicklungsmaschine und behält diese Werkzeuge.

Technische Vorzugsvariante: das bereits geplante **PyInstaller-One-folder-Bundle
in einem Inno-Setup-Installer**. Eine Datei wird heruntergeladen und ausgeführt;
der Installer legt intern Anwendungsdateien an. Nutzerdaten bleiben separat.
Eine buchstäblich einzige Datei einschließlich veränderlicher Daten ist kein Ziel.
Die bestehende React-Oberfläche läuft zunächst im Standardbrowser auf Loopback;
ein zusätzliches Desktop-/WebView-Framework ist für diesen Schritt nicht nötig.

| Option | Einordnung für IMS |
| --- | --- |
| py2exe | Windows-Freezer, als Alternative im kurzen Paketierungsversuch prüfen. Laut Projekt sind bundle_files kleiner 3 unter Python 3.12+ nicht unterstützt; entsprechende Bündeloptionen sind zusätzlich abgekündigt. Daher keine unbelegte Zusage einer einzelnen py2exe-EXE. |
| PyInstaller + Inno Setup | Vorzugsvariante: vollständige Laufzeit bündeln, ein Installationsdownload, Startmenü und Deinstallation. Baut auf der bisherigen Planung auf. |
| PyInstaller One-file | Optionaler portabler Download ohne Installer. Erst nach funktionierendem One-folder-Build bewerten: temporäres Entpacken, Startzeit, Ressourcenpfade, Virenscanner und Beenden testen. Kein paralleler zweiter Pflicht-Verteilungsweg. |

Interne Schritte in **einem PR**:

1. Inventar benötigter Dateien: Python-Pakete, dynamische Imports, Profile,
   Frontend-Build, Beispiele, Hilfe und Lizenztexte. Pinned Build-Abhängigkeiten
   und Entscheidung zu py2exe/PyInstaller mit Messungen dokumentieren.
2. Eingefrorener Einstiegspunkt: Ressourcen unabhängig vom Arbeitsverzeichnis
   finden; gebaute Oberfläche einschließen; Browser nach erfolgreichem Health-Check
   öffnen; nur 127.0.0.1; Portkonflikt und Zweitstart verständlich behandeln.
3. Programm und Daten trennen: Benutzerdateien unter einem dokumentierten
   AppData-Verzeichnis; bestehende .ims_workbench-Daten nur mit explizitem
   Übernahme-/Backup-Schritt migrieren. Update und Deinstallation löschen keine
   Nutzerdaten ohne ausdrückliche Auswahl.
4. Installer mit Startmenü, Version, sauberem Beenden, Diagnoseexport und
   Deinstallation. Lizenzbedingungen der tatsächlich gewählten Build-Werkzeuge
   vor externer Verteilung prüfen; keine Käufe oder Signaturzertifikate voraussetzen.
5. Windows-CI baut das tatsächliche Artefakt, veröffentlicht zunächst ein
   Download-Artefakt am Run mit SHA-256 und testet Installation/Start/Update/
   Deinstallation. Ein Release auf GitHub wird gesondert freigegeben.

**Abnahme:** Frisches Windows 11 x64 ohne Entwicklerwerkzeuge, gewöhnlicher
Benutzer, offline nach Download; Installation, Doppelklick, Oberfläche, ein
bereits vorhandener Modellfall und Export funktionieren. Zusätzlich Pfade mit
Leerzeichen/Umlauten, Zweitstart, belegter Port, Update mit Datenerhalt,
Deinstallation und anschließender Wiederstart nach Neuinstallation.
Die jetzigen GitHub-Windows-Runner enthalten Entwicklerwerkzeuge; ihr grüner
Build ersetzt keinen separaten VM-/Sandbox-Nachweis ohne diese Werkzeuge.
Windows 10 bleibt eine ausdrücklich gesondert zu belegende Kompatibilität.
Signierung und mögliche SmartScreen-Meldungen sichtbar dokumentieren, keine
Schutzumgehung anleiten. AP1 darf bestehende fachliche Grenzen nicht verstecken.

## AP2: Ruhige, iOS-inspirierte Oberfläche

**Ergebnis:** Eine klare Seminar- und Managementoberfläche mit verständlichen
Aufgaben statt einer langen Liste technischer Zwischenstufen. iOS-like bezeichnet
die Gestaltung und Interaktion, nicht eine native iOS-App oder iPad-Installation.

Bestehende Basis weiterverwenden: React 19, TypeScript, Vite und lucide-react.
Die aktuelle main.tsx hat 9.211 Zeilen, styles.css 4.622 Zeilen; diese Messung
ist kein Qualitätsurteil, erklärt aber den Bedarf an einer geordneten UI-Struktur.
Betroffene Ansichten in Komponenten mit gemeinsamen Zustandsmustern zerlegen.
Keine fachliche Neuschreibung als Nebenwirkung des Redesigns.

**Informationsarchitektur:** Übersicht, Szenario, Simulation, Ergebnisse, Hilfe.
Modell-/Quellendetails, technische Diagnosen und Expertenparameter gezielt
aufklappen. Herkunft, Modellgrenzen und notwendige Ausführungsfreigaben bleiben
an der Stelle sichtbar, an der eine Entscheidung getroffen wird.
AP2 gestaltet die vorhandenen Funktionen; die noch fehlenden geführten
Fachfunktionen kommen in AP3. Keine Schaltfläche darf Verfügbarkeit vortäuschen.

**Gestaltungsvorschlag:**

- Heller neutraler Hintergrund, klar abgesetzte weiße Flächen, zurückhaltender
  blauer Akzent; Dunkelmodus über dieselben Farbvariablen.
- Systemschriften, deutliche Titelhierarchie, konsistentes 8-Pixel-Raster,
  großzügige Abstände und etwa 12–16 Pixel Eckradien.
- Eine erkennbare Hauptaktion je Arbeitsschritt; Gruppen-/Periodenauswahl mit
  verständlichen Beschriftungen; Status auch in Text, nicht nur als Farbe.
- Ergebnis zuerst: Baseline/Variante, Verlauf, Gesamtbilanz und Sparten;
  Detailtabellen nachgeordnet mit gut lesbaren Zahlen und Einheiten.
- Lade-, Leer-, Fehler-, Abbruch- und Erfolgszustände; erhaltener Formularzustand
  und Tastaturfokus; reduzierte Bewegung respektieren.

**Abnahme:** Vorher-/Nachher-Bilder und reale Browserläufe auf 1440×900,
1024×768 und 390×844; kein Seitenüberlauf, Tabellen gezielt scrollbar.
Eigene Qualitätsziele: Textkontrast mindestens 4,5:1, klarer Tastaturfokus,
mindestens 44×44 CSS-Pixel für wesentliche Touch-Ziele. Heller und dunkler Modus
bleiben verständlich. Kernpfad, ungültige Eingaben, erneute Eingabe nach Fehler,
Downloads und Ausführungsfreigaben mit Browser-Tests prüfen.
Die vorhandenen Skripte unter tests/browser werden weiterverwendet/angepasst;
die Browser-Testabhängigkeiten werden reproduzierbar installiert und in CI
ausgeführt. Ein TypeScript-Build allein ist keine UI-Abnahme.

## AP3: Ein Integrations-PR für die 23 fachlichen Restschritte

**Ergebnis:** Ein selbst aufgebauter, reproduzierbarer 100-Perioden-Seminarfall
mit vier Sparten, begrenzten wirksamen Strategien, DORA-Wirkungskette,
Modellbilanz, Kapitaldarstellung und nachvollziehbaren Exporten.

Ein Branch, ein Draft-PR, mehrere kleine nachvollziehbare Commits und fünf
interne Meilensteine. Der PR bleibt offen, während Codex über mehrere Sitzungen
weiterarbeitet. Nach jedem Meilenstein Prüfergebnisse und Restpunkte festhalten.

| Meilenstein | Inhalt | Abnahme innerhalb desselben PRs |
| --- | --- | --- |
| M1: DORA | Services, Assets, Anbieter, Ereignisse, Zeitadapter, Kapazität, Rückstand, Erholung, Konzentration und Gegenmaßnahmen | Deterministischer Fall vom ICT-Ereignis über operative Effekte zur Bilanz; Dossier mit Quellen und Annahmen |
| M2: Geführter Lauf | Szenarioassistent, 100 vollständige Kontexte, atomarer Kandidatenbau und kontrollierter Start | Seeds/Digests/Prefixe stabil; fehlerhafter Kontext erzeugt weder Lauf noch Teilresultat |
| M3: Vier Sparten | Gemeinsamer Quellenvertrag, periodische Bilanz, Carryover, Baseline/Variante | Rechnung je VU und Periode stimmig; Zwei-Perioden-Prefix erhalten; CSV/JSON/XLSX und Anzeige stimmen überein |
| M4: Strategiewirkung | Quellen-/Zeitmapping, begrenzte Nichtleben-/Leben-/Kranken-Adapter und bedienbare Eingabe | Mindestens eine belegte Reaktion von Entscheidung über Spartenfluss zur 100er-Modellbilanz; nicht gekoppelte Kanäle explizit |
| M5: Seminar | Kuratierte Fälle, Moderation, Szenariobündel, aktualisiertes Handbuch | Installierte Anwendung besteht den gesamten Seminarpfad einschließlich Export; AP1-Artefakt mit aktuellem Code neu bauen |

**Fachliches Entscheidungstor vor Ausführungsadaptern:** Das bisherige PR187g
bleibt verbindlich. Historische anonyme Schadenpositionen sind keine belegte
Kfz-/Sach-Zuordnung. VU/VN, Gruppe, Sparte, Parameter, Zeitfenster und exogene
Annahmen müssen begründet abgebildet sein. Bei fehlendem Mapping den betroffenen
Teil als blockiert dokumentieren; keine Strategie erfinden und keine Freigabe
aus einem bestandenen technischen Test ableiten.

Ein zusammengefasster PR darf die sequentiellen fachlichen Abhängigkeiten nicht
überspringen. Muss ein fachlich ungeklärter Teil abgetrennt werden, Umfang und
PR-Zahl offen ändern; keine stillschweigende Streichung aus der Restliste.
EIOPA-/weitere Schockideen aus dem Weekly Scan zunächst in den Backlog aufnehmen,
mit Quelle und Modellwirkung; sie erweitern AP3 nicht automatisch.

**Unveränderte Grenzen:** Keine historische Vollgleichheitsbehauptung,
keine regulatorischen SCR/MCR-/Bedeckungsquoten, kein DORA-Konformitätsurteil.
Eine additive Vier-Sparten-Rechnung ist kein Nachweis vollständiger endogener
Marktkopplung. Historische Rohdaten nicht beiläufig versionieren oder ausliefern.

## So läuft der Plan auf GitHub

Der maschinenlesbare [Ausführungsplan](ims_ai_sprint_plan.json) ordnet jede der
25 alten Plan-IDs genau einem Paket zu und enthält Status, Abhängigkeiten,
Akzeptanzkriterien und Entscheidungstore. Verbindlicher Leseeinstieg für Codex:
AGENTS.md → dieses Dokument → Manifest → fachliche Quellen.

Der neue Workflow **IMS AI sprint plan**:

- prüft bei relevanten PRs und Pushes Planvollständigkeit, eindeutige Zuordnung,
  Abhängigkeiten, Dokumentpfade und Statuskonsistenz;
- erzeugt einen Planbericht und einen vorbereiteten Codex-Arbeitsauftrag als
  herunterladbares Artefakt; der Auftrag enthält Commit und konkretes Paket;
- ist nach Aufnahme in den Default-Branch über Actions → Run workflow mit
  Paketauswahl startbar; die PR-Prüfung läuft bereits vor dem Merge;
- erzeugt keine Modellantwort, verändert keinen Produktcode, startet keinen
  P52-Prozess und merged nichts. Ein grüner Plancheck belegt Planstruktur,
  nicht die Erfüllung der Produktabnahmen.

GitHub übernimmt damit jetzt die maschinenprüfbare Aufgabenübergabe. Die lokale
Codex-App setzt das ausgewählte Paket mit dem vorhandenen ChatGPT-Login um.
Ein Workflow in GitHub startet die Windows-App nicht automatisch. Dafür wäre
ein ausdrücklich eingerichteter Ausführungskanal auf dem P52 erforderlich.
Für diesen öffentlichen Codebestand ist ein persönlicher Self-hosted Runner
mit breiten Rechten kein voreingestellter Bestandteil des Vorschlags.

Eine vollständige Ausführung auf GitHub kann später über openai/codex-action
ergänzt werden. Der dokumentierte Weg benötigt API-Authentifizierung und hat
eigene Kosten/Quoten; das Pro-Abonnement allein ist keine hinterlegte
Actions-Authentifizierung. Keine Schlüssel werden in diesen PR aufgenommen.
Die API-Variante ist eine spätere Betriebsentscheidung, keine Voraussetzung
für die vorgeschlagenen drei PRs.

### Konkreter Start auf dem P52 nach Annahme des Planungs-PRs

1. Vorhandene Arbeit sichern; Branch und Änderungen prüfen. Den angenommenen
   Planstand aus GitHub holen, ohne fremde/uncommittete Änderungen zu überschreiben.
2. Codex das erste ausführbare Paket aus dem Manifest vollständig bearbeiten
   lassen; für AP1 einen eigenen Branch und Draft-PR eröffnen.
3. Für Python die .venv des aktuellen Checkouts verwenden. In einem neu erzeugten
   Worktree die Umgebung neu aufbauen; nicht den Interpreter eines anderen
   Checkouts samt editable install übernehmen.
4. Kleine Zwischenprüfungen nach Bedarf, vollständige passende Abnahme vor
   Abschluss. Der bestehende Windows-Release-Gate bleibt erhalten.
5. Status und Evidenz in derselben Paket-PR aktualisieren. Ein Paket gilt im
   gemeinsamen main-Manifest erst nach dem Merge als erledigt. Abhängige Pakete
   vorher nicht als eigenständig startbereit ausgeben.

Lokale Vorbereitung desselben Arbeitsauftrags:

~~~powershell
.\.venv\Scripts\python.exe scripts/planning/ims_sprint_plan.py --package auto --out .tmp-pr-sprint
~~~

Die Ausgabe enthält plan-report.md und gegebenenfalls codex-work-order.md.
Die Skripte dieser Planungs-PR benötigen nur die Python-Standardbibliothek.

## Wochenrhythmus und Kapazität

Die drei Erstpakete sind **keine Zusage, dass der gesamte Restumfang in einer
Woche fertig ist**. Für die erste Woche AP1 und AP2 als Lieferziele, für AP3
zunächst Quellenmapping und M1 als Arbeitsziel. Nach dem Installer-Versuch und
dem ersten langen Lauf Umfang anhand der tatsächlichen Befunde neu bewerten.
AP3 kann über mehrere Wochen im selben Draft-PR weiterlaufen.

Für spätere kleinere Erweiterungen bleibt das Ziel 3–4 größere PRs pro Woche.
Die Retro steuert anhand von abgeschlossenen Abnahmen, aktiver Agentenzeit,
Testzeit, Nacharbeit und Blockern; PR-Anzahl oder Laufzeit allein messen
keinen fachlichen Fortschritt. Reserven für Fehlerbehebung einplanen.

Freitag: Weekly Scan mit höchstens drei begründeten Ausbauideen.
Samstag: Retro und Auswahl des nächsten Wochenumfangs.
Abends: gewünschter Bericht mit Paket/PR, Commit, fachlichem Ergebnis,
Testnachweisen, Blockern und nächstem Schritt in Evernote.
Dieser PR richtet diese Berichte oder lokalen Zeitpläne noch nicht ein.
Er dokumentiert die Übergabe; die bereits separat eingerichtete Scan-Aufgabe
wird nicht verändert.

## Quellen für technische Entscheidungen

- [py2exe: unterstützte Versionen und Bündelgrenzen](https://github.com/py2exe/py2exe)
- [PyInstaller: One-folder und One-file](https://pyinstaller.org/en/stable/operating-mode.html)
- [Inno Setup: einzelner Installer, Startmenü, Deinstallation](https://jrsoftware.org/isinfo.php)
- [OpenAI: Codex GitHub Action](https://learn.chatgpt.com/docs/github-action)
- [OpenAI: Authentifizierung](https://learn.chatgpt.com/docs/auth)
- [GitHub: Workflow-Syntax und workflow_dispatch](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax)

Prüfstand der externen Dokumentation: 30.09.2026. Paketierungswerkzeuge werden
erst nach einem erfolgreichen Build-/Zielrechner-Versuch verbindlich festgelegt.
