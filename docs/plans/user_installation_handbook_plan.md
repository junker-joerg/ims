# Plan: Benutzer- und Installationshandbuch

Stand: 2026-09-01
Planungsschnitt: HB1
Umsetzungsstand: HB3a

## Ziel

Das neue Handbuch soll IMS-Anwender von der Installation bis zur kontrollierten
Nutzung der Browser-Workbench fuehren. Es richtet sich nicht primaer an
Entwickler und ersetzt keine Migrations-, Architektur- oder
Fachvalidierungsdokumentation.

Das Handbuch muss jederzeit unterscheiden zwischen:

- technisch startbarer Workbench;
- kontrollierter Bedienung und Ergebnisanzeige;
- diagnostischen Vergleichen mit historischen Referenzen;
- noch nicht belegter historischer Parameter-, RNG- oder Vollgleichheit;
- tatsaechlich gepruefter und nur geplanter Plattformunterstuetzung.

HB1 und HB3a aendern keine Fachlogik, starten keine Simulation und behaupten
keine historische Vollgleichheit.

## Zielgruppen

| Zielgruppe | Erwartung an das Handbuch |
| --- | --- |
| Anwender und Fachwissenschaftler | installieren, starten, Szenario waehlen, Status lesen, kontrollierten Lauf bedienen, Ergebnis und Grenzen verstehen |
| Lokale Administratoren | Voraussetzungen, portable Ablage, Ports, Metadaten, Backup, Update und Rollback beherrschen |
| Reviewer und Reproduzierbarkeitspruefer | Version, Referenzschicht, Teststatus und Aussagegrenzen nachvollziehen |
| Entwickler | ueber gezielte Verweise zu den bestehenden technischen Migrationsdokumenten gelangen, ohne dass diese in das Bedienhandbuch kopiert werden |

## Bestand

Die notwendigen Inhalte existieren zu grossen Teilen, sind aber auf technische
Quellen verteilt und verwenden unterschiedliche Detailstufen.

| Bestehende Quelle | Verwertbarer Inhalt | HB-Zuordnung |
| --- | --- | --- |
| `README.md` | Entwickler-Kurzstart, Build, Diagnose und lokaler Serverstart | Installationsvoraussetzungen und technischer Anhang |
| `docs/migration/workbench_demo_checklist.md` | sichtbarer Bedienablauf, UI-Karten, sichere Demo-Grenzen | Bedienhandbuch und Abbildungsverzeichnis |
| `docs/migration/workbench_shell.md` | vollstaendige technische Befehls- und Vertragsreferenz | technische Quelle, nicht direktes Benutzerkapitel |
| `docs/migration/workbench_release_checklist.md` | gepruefter Windows-ZIP-, Staging-, Check- und Startablauf | Windows-Installation und Abnahme |
| `docs/migration/workbench_packaging_plan.md` | portable Struktur, Build und Auslieferungsgrenzen | Windows-Installation und Wartungsanhang |
| `docs/migration/workbench_metadata_recovery.md` | Backup, Restore, Side-by-Side-Update und Rollback | Datensicherung und Wartung |
| `docs/migration/windows_release_gate.md` | reproduzierbare Windows-Pruefkette | Installationsnachweis und Troubleshooting |
| `scripts/workbench/README.md` | Verhalten der Windows-Start- und Checkskripte | Windows-Kurzstart |
| `python_port/pyproject.toml` und `frontend/package.json` | technische Laufzeit- und Build-Abhaengigkeiten | versionierte Voraussetzungsliste |

Festgestellte Luecken:

- kein zusammenhaengender, nichttechnischer Bedienpfad;
- keine klare Trennung zwischen normalem Benutzerstart und Entwickler-Build;
- kein einheitliches Glossar fuer Szenario, Run, Queue, Freigabe und Ergebnis;
- Screenshots sind in Smoke-Nachweisen vorhanden, aber nicht als gepflegte
  Handbuchabbildungen mit Versionsbezug organisiert;
- keine gepruefte Linux-Installation oder Linux-Startschale;
- keine Machbarkeitsentscheidung fuer iOS/Juno;
- Fehlerhilfe, Deinstallation und Datenablage sind nicht als Benutzerkapitel
  konsolidiert;
- der aktuelle historische Vergleichsstatus ist dokumentiert, aber noch nicht
  in eine kurze, allgemein verstaendliche Aussage uebersetzt.

## Zielstruktur

Ab HB2 soll unter `docs/handbook/` eine zusammenhaengende, versionierte
Handbuchstruktur entstehen:

| Kapitel | Inhalt |
| --- | --- |
| `README.md` | Einstieg, Zielgruppen, Versionsstand und Navigation |
| `quickstart_windows.md` | kuerzester gepruefter Weg vom Artefakt zur laufenden Workbench |
| `installation_windows.md` | Voraussetzungen, Installation, Check, Start, Stop und Deinstallation |
| `operation.md` | Dashboard, Szenarien, Validierung, Run-Control und Ergebnisanzeige |
| `results_and_validation.md` | Ergebnisstatus, historischer Vergleich und Aussagegrenzen in einfacher Sprache |
| `data_and_updates.md` | Datenablage, Backup, Restore, Side-by-Side-Update und Rollback |
| `troubleshooting.md` | typische Start-, Port-, Python-, Node-, Frontend- und Metadatenfehler |
| `installation_linux.md` | erst nach erfolgreichem HB4-Plattformnachweis |
| `installation_ios_juno.md` | nur mit dem in HB5 belegten Nutzungsmodell und klarer Supportstufe |
| `technical_reference.md` | knappe Verweise auf Migrationsdoku, Checks und Entwicklerbefehle |

Das Bedienhandbuch verwendet kurze Handlungsfolgen, sichtbare UI-Begriffe und
Screenshots. Lange Vertragsfelder, interne Payloads und historische
Codekartierungen verbleiben in `docs/migration/` und werden nur verlinkt.

## Plattformstatus

| Plattform | Aktueller Status | Belegt | Offen vor einer Handbuchfreigabe |
| --- | --- | --- | --- |
| Windows | `verified_windows_hb3` | Benutzer-Kurzstart, Entwickler-Checkout, Frontend-Build, ZIP/Staging, Leerzeichenpfad, Checkskript, Startskript, Loopback-Health, Browseransicht, Datenpflege und Deinstallation | konsolidierte Fehlerhilfe und abschliessende Handbuchabnahme in HB6 |
| Linux | `not_verified` | Python-/Webarchitektur ist grundsaetzlich plattformneutral angelegt | Shell-Startskript, Pfade, Node-/Python-Installation, ZIP-Layout, Browser-Smoke, CI oder reale Testmaschine |
| iOS/Juno | `feasibility_open` | keine lokale IMS-Installation belegt | Entscheidung zwischen Browser-Client zu einem extern laufenden IMS und lokaler Juno-Ausfuehrung; Abhaengigkeiten, Loopback-Server, Frontend-Artefakt, Dateizugriff und Metadatenhaltung pruefen |

Fuer iOS/Juno werden in HB5 zwei unterschiedliche Modelle getrennt bewertet:

1. **Browser-Client:** IMS laeuft auf einem anderen, vertrauenswuerdigen
   Rechner; iOS bedient nur die Weboberflaeche. Dies ist keine lokale
   iOS-Installation.
2. **Lokale Juno-Ausfuehrung:** Python-Kern, Webserver, vorgebautes Frontend,
   SQLite und Dateipfade laufen auf dem iOS-Geraet. Dies darf erst nach einem
   reproduzierbaren Minimal-Smoke als experimentell oder unterstuetzt
   dokumentiert werden.

Bis HB4 beziehungsweise HB5 erfolgreich abgeschlossen sind, duerfen Linux und
iOS/Juno nicht als unterstuetzte Installation bezeichnet werden.

## Handbuchregeln

- Jeder Installationsweg nennt eine konkrete, getestete IMS-Version und ein
  konkretes Artefakt oder Checkout-Layout.
- Voraussetzungen werden vor dem ersten Befehl genannt und mit einer
  Versionspruefung versehen.
- Benutzerbefehle und Entwickler-/Releasebefehle bleiben getrennt.
- Jeder Startweg hat einen passenden Check-, Stop- und Fehlerpfad.
- Lokale Anwendung und lokale Metadaten werden getrennt erklaert.
- Update bleibt Side-by-Side, solange kein eigener Migrationsvertrag vorliegt.
- Screenshots tragen Ansichtsname, Version und Aufnahmedatum; sie belegen
  Bedienbarkeit, keine fachliche Gleichheit.
- Historische Referenzen werden als Vergleichsdaten beschrieben, nicht als
  automatisch reproduzierbarer Ursprungslauf.
- `incomming/` bleibt unversioniert und ist kein Benutzer-Datenimportpfad.

## Umsetzungsstand HB3a und Restplanung HB4 bis HB6

### HB2: Benutzerhandbuch-Grundgeruest und Bedienpfad (umgesetzt)

- `docs/handbook/` mit Einstieg, Bedienpfad, Ergebnisdeutung und technischer
  Verweisuebersicht angelegt;
- Begriffe sowie die Navigation `Dashboard`, `Szenarien`, `Validierung` und
  `Runs` konsolidiert;
- Bedienpfad von Auswahl und Dry-Run ueber Queue und explizite Freigabe bis
  zur Ergebnisanzeige anhand der vorhandenen UI-Begriffe beschrieben;
- historischen Stand nach PR100 als 12/15 Tabellen und 4.800/6.300
  Ergebniszeilen in einfache Sprache uebersetzt;
- Windows nur als technisch belegten Pfad, Linux als `not_verified` und
  iOS/Juno als `feasibility_open` ausgewiesen;
- keine Simulation und keine Screenshot-Aufnahme gestartet.

Umgesetzt in `docs/handbook/` und `tests/test_user_handbook.py`.

### HB3: Windows-Installationshandbuch (umgesetzt)

- Voraussetzungen und zwei Wege getrennt: Entwickler-Checkout und
  vorbereiteter portabler ZIP-/Ordnerweg;
- Check, Start, Stop, Datenablage, Backup, Restore, Side-by-Side-Update,
  Rollback und Deinstallation dokumentiert;
- portablen Zielpfad mit Leerzeichen mit PowerShell 7.6.4, Python 3.13.7,
  Node.js 22.18.0 und npm 10.9.3 geprueft;
- Frontend-Build mit 1.578 Modulen, portables Checkskript, Startskript,
  HTTP-Health und Browseransicht erfolgreich;
- zwei datierte Benutzer-Screenshots fuer Start- und Validierungszustand
  aufgenommen;
- Server nach dem Smoke kontrolliert beendet, ohne Queue-Aktion, Adapter oder
  Simulation.

Umgesetzt in `docs/handbook/`, `tests/test_user_handbook.py` und
`tests/test_windows_handbook.py`. Es waren keine Skriptkorrekturen und keine
neue Fachlogik erforderlich.

### HB3a: Portables Windows-Anwender-Testpaket (umgesetzt)

- finales ZIP mit eigenem Rootordner und gebautem Frontend vorbereitet;
- `install-workbench.cmd` richtet eine lokale `.venv` ein;
- Check und Start verwenden diese Umgebung ohne erneute PATH-Anpassung;
- 2-seitige Installationsdoku und 8-seitige Bedienungsanleitung als PDF
  erzeugt und visuell geprueft;
- Dashboard, Szenarien, Runs, Validierung und kontrollierten Dry-Run mit fuenf
  datierten UI-Abbildungen direkt im Bedienpfad gezeigt;
- Anwendernutzen und noch nicht verfuegbare Simulation ehrlich getrennt;
- PR102 und die fachliche Korpusbewertung bleiben ein eigener Schritt.

Umgesetzt unter `docs/plans/portable_user_test_package_plan.md`.

### HB4: Linux-Plattformnachweis und Installationskapitel

- unterstuetzte Distribution und Laufzeitversionen explizit festlegen;
- virtuelle Python-Umgebung, Frontend-Build oder vorgebautes Frontend sowie
  Shell-Start/Check pruefen;
- Loopback-Health, UI-Smoke, Metadatenpfad und Stop-Verhalten testen;
- erst nach gruenem Nachweis `installation_linux.md` als unterstuetzten Pfad
  freigeben, sonst die Luecke offen dokumentieren.

Erwarteter Umfang: 180-360 Dokumentationszeilen, 60-160 Test-/Skriptzeilen.

### HB5: iOS/Juno-Machbarkeitsentscheidung

- Browser-Client und lokale Juno-Ausfuehrung getrennt pruefen;
- Python-Version, Paketinstallation, FastAPI/Uvicorn, SQLite, Dateipfade,
  Loopback-Zugriff und vorgebautes Frontend anhand eines Minimal-Smokes
  bewerten;
- Ergebnis als `supported`, `experimental` oder `not_supported` mit Begruendung
  festhalten;
- kein Installationskapitel veroeffentlichen, wenn nur Vermutungen vorliegen.

Erwarteter Umfang: 120-260 Dokumentationszeilen und 20-100 Test-/Protokollzeilen.

### HB6: Konsolidierung und Handbuchabnahme

- Screenshots, Querverweise, Glossar und Troubleshooting vervollstaendigen;
- alle dokumentierten Befehle und Links pruefen;
- Plattformmatrix und Versionshinweise einfrieren;
- kurze Anwenderabnahme fuer Installation, Start, Bedienung, Ergebnislesen,
  Backup und Stop durchfuehren;
- HTML/PDF-Ausgabe erst dann separat planen, falls sie weiterhin benoetigt wird.

Erwarteter Umfang: 160-320 Dokumentationszeilen und 40-120 Testzeilen.

## Aufwand und Reihenfolge

Nach HB3a bleiben **3 Handbuch-Schnitte**. Die grobe Bruttoabschaetzung fuer
HB4 bis HB6 liegt bei 580-1.320 LoC in Dokumentation, Dokumentationstests und
kleinen plattformspezifischen Skripten. Nicht enthalten sind ein nativer
Installer, Signierung, App-Store-Verteilung, ein automatischer Updater oder
groessere Plattformanpassungen.

PR101, HB3 und HB3a sind als getrennte reviewbare Schnitte vorbereitet. PR102
und HB4 sind die naechsten getrennten Schnitte. Plattformzusagen aus HB4/HB5
duerfen die Kernvalidierungsbewertung in PR102 nicht vorwegnehmen.

## Abnahme HB1

- Quellenbestand und Luecken sind benannt;
- Zielgruppen und Zielstruktur sind festgelegt;
- Windows, Linux und iOS/Juno besitzen unterschiedliche belegte Statuswerte;
- HB2 bis HB6 haben Ziel, Grenze und groben Umfang;
- Bedienhandbuch, Installationshandbuch und technische Migrationsdoku bleiben
  klar getrennt;
- keine Simulation, keine neue Fachlogik und keine historische
  Vollgleichheitsbehauptung.

## Abnahme HB2

- der Einstieg verlinkt alle vorhandenen Handbuchkapitel;
- der Bedienpfad verwendet die in der Workbench sichtbaren Begriffe und
  trennt pruefende, schreibende und startende Aktionen;
- der historische Vergleichsstand ist allgemein verstaendlich, aber ohne
  Vollgleichheits- oder Produktionsfreigabebehauptung eingeordnet;
- technische Details werden verlinkt und nicht als zweite Entwicklerdoku
  dupliziert;
- Plattformstatus und verbleibende HB3-bis-HB6-Schnitte sind aktualisiert;
- Dokumentationstests pruefen Navigation, Grenzen, Links und Restplanung.

## Abnahme HB3

- Windows-Kurzstart und vollstaendige Installation trennen Benutzerweg und
  Entwickler-Build;
- Python- und Node-Anforderungen sind aus den versionierten Paket- und
  CI-Vertraegen abgeleitet;
- Check, Start, Health und Browseransicht sind auf einem frischen portablen
  Leerzeichenpfad belegt;
- Stop, Datenablage, Backup, Restore, Side-by-Side-Update, Rollback und
  Deinstallation sind dokumentiert;
- Screenshots tragen Ansicht, Handbuchstand und Aufnahmedatum;
- Windows ist `verified_windows_hb3`, Linux bleibt `not_verified` und
  iOS/Juno bleibt `feasibility_open`;
- keine Simulation, keine neue Fachlogik und keine historische
  Vollgleichheitsbehauptung.
