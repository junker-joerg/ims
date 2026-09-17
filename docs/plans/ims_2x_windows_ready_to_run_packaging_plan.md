# Windows Ready-to-run ohne Zielrechner-Installation

Stand: 2026-09-17
Einordnung: spaetere Distributionsspur nach PR190; PR169b bleibt der
unmittelbar naechste Schritt. Dieser Plan baut noch kein Paket.

## Ziel

Ein Anwender entpackt ein Windows-ZIP und startet `IMS-Workbench.exe` per
Doppelklick. Auf dem Zielrechner sind weder Python, Node.js, npm, Git,
`pip install`, Internet fuer Paketinstallationen noch `.cmd`-/PowerShell-
Skripte erforderlich. Das Paket bleibt lokal und bindet nur an Loopback.
Es ist ein testbarer Bedienweg, keine fachliche Produktionsfreigabe.

PyInstaller wird zuerst im One-folder-Modus auf Windows gebaut. Ein
One-file-EXE und ein grafischer Installer sind **keine** Voraussetzung
fuer den Doppelklick-Test; sie bleiben spaetere, gesondert zu begruendende
Optionen. Die Build-Umgebung darf weiterhin Python und Node.js nutzen.

## Zwei kleine PRs

| PR | Gegenstand | Abnahme |
| --- | --- | --- |
| PR191 | Windows-x64-PyInstaller-Bundle mit eigenem Einstiegspunkt und expliziten Ressourcenpfaden | EXE startet Backend samt gebautem Frontend offline und ohne Zielrechner-Python; Profil- und sonstige Laufzeitdaten sind enthalten; keine Schreibzugriffe in Bundle oder temporaere Entpackpfade. |
| PR192 | Doppelklick-Lebenszyklus, ZIP, Handbuch und Zielrechner-Abnahme | Browser oeffnet erst nach Health-Check; Portkonflikt, Zweitstart, Beenden, Datenablage und Fehleranzeige sind klar; frischer Windows-10/11-x64-Test ohne Python/Node und ohne Netzwerk fuer Installation besteht. |

## Technische Grenzen und Pruefpunkte

- `frontend/dist`, Python-Webabhaengigkeiten und erforderliche Paketdaten
  werden explizit aufgenommen. Pfade aus `__file__` bzw. Repo-Wurzel
  werden fuer den eingefrorenen Lauf angepasst und die betroffenen
  Endpunkte gegen das Paket geprueft.
- Nutzerdaten und Metadaten liegen ausserhalb des unveraenderlichen
  Bundles, vorzugsweise unter `%LOCALAPPDATA%`; Versionen duerfen diese
  Daten nicht stillschweigend ueberschreiben. Backup- und Migrationsweg
  werden dokumentiert.
- Der Server wird ausschliesslich an `127.0.0.1` gebunden. Ein belegter
  Port fuehrt zu einer sichtbaren, sicheren Entscheidung; kein stiller
  Wechsel auf eine oeffentliche Netzwerkschnittstelle.
- Start, erneuter Start und Beenden muessen ohne verborgen weiterlaufenden
  Prozess nachvollziehbar sein. Ein unsichtbares Fenster ist erst mit
  verlaesslichem Beenden sinnvoll.
- ZIP enthaelt einen Hash und kurze Installations- und Bedienhinweise.
  `incomming/`, historische Roharchive, Test-Caches und Build-Werkzeuge
  werden nicht beilaufig mit ausgeliefert.
- Unsignierte EXEs koennen von SmartScreen oder Unternehmensrichtlinien
  angehalten werden. Keine Schutzumgehung; Signierung und
  Verteilungsweg sind separate Freigabeentscheidungen.
- Der Windows-Build gilt nicht fuer Linux oder iOS/Juno. Beide brauchen
  eigene Installations- und Laufzeitentscheidungen.

## Herkunft des Bedarfs

Das heutige `IMS-Workbench-2026-Windows-Test.zip` verlangt laut
`docs/handbook/installation_test_package_windows.md` Python 3.12+,
einmalige Online-Installation und `install-workbench.cmd` sowie
`start-workbench.cmd`. PR191/192 ersetzen **nur den Zielrechnerpfad**;
der bestehende Entwickler- und Reproduktionsweg bleibt erhalten.

Offene Fragen vor PR191: genaues Windows-Buildprofil, Inventar aller zur
Laufzeit gelesenen Dateien und Entscheidung fuer portable Daten neben
dem Paket versus per-user AppData. Keine Fachlogik oder historische
Vollgleichheitsbehauptung ist Teil dieser Distributionsspur.
