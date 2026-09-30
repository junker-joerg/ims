# AP1: Windows-Distribution und Entscheidung

## Mapping und Laufzeitinventar

| Bisheriger Ursprung | AP1-Komponente | Entsprechung |
| --- | --- | --- |
| `scripts/workbench/build-user-test-package.ps1` | `scripts/installer/build-installer.ps1`, `ims.spec`, `ims.iss` | Separate Laufzeit und einzelner Setup-Download |
| `ims/api/app.py::_repo_root` | `ims/desktop/paths.py::resource_root` | Repo im Entwicklerlauf; `_internal/resources` im eingefrorenen Lauf |
| `scripts/workbench/start-workbench.cmd` | `ims/desktop/launcher.py` | Loopback, Health-Check, Browser, GUI und Beenden |
| `.ims_workbench/metadata.sqlite` | `ims/desktop/data.py` | Separate AppData-Ablage, ausdrücklich bestätigte Übernahme mit SQLite-Backups |

Keine historische C-Funktion wird in AP1 neu portiert; Scheduler, Seeds,
Strategien, Aggregatbildung und bestehende Ausführungsfreigaben bleiben erhalten.
Der Entwickler-/ZIP-Paketweg bleibt zusätzlich nutzbar.

`stage_resources.py` inventarisiert ausdrücklich die **versionierten**
`tests/fixtures/*.json` und kuratierten DAT-/JSON-Referenzen unter
`tests/references/legacy_agrsich/` sowie Handbuch-/Migrationsnotizen. Sie sind
für die vorhandenen Diagnoseendpunkte vorgesehen. Kein `incomming/`, kein
Roharchiv und kein C-Quellbestand wird beiläufig verteilt. Die vollständige
Dateiliste mit SHA-256 steht in `resource-inventory.json` am CI-Artefakt.
Zusätzlich: `frontend/dist`, vorhandene Bedienungs-PDF, neue lokale HTML-Hilfe,
Lizenztexte und das Strategie-Profil JSON als PyInstaller-Paketdaten.
Die frühere Installations-PDF mit Zielrechner-Python-Anforderung wird ausgelassen.

Uvicorn verwendet explizit asyncio/h11/lifespan; tkinter enthält den Windows-
Launcher. Diese dynamischen Imports sind im Spec benannt. Schreibzugriffe gehen
in die Benutzerablage, Exporte in den gewählten Download-/Diagnosepfad.
Repository-relative Diagnosepfade werden über die unveränderliche
Ressourcenwurzel aufgelöst. Der instanzbezogene Steuerungsendpunkt verlangt
einen zufälligen Schlüssel und POST; fremde Webseiten bekommen keine Freigabe.
Proxy-Umgebungsvariablen werden für Loopback-Steuerung/Health-Check ignoriert.

## Werkzeugentscheidung und Versuch

PyInstaller 6.22.3 One-folder plus Inno Setup 6.7.3 erzeugt den geforderten
einzelnen Download. One-file ist kein zweiter Pflicht-Verteilungsweg.
[PyInstaller dokumentiert](https://pyinstaller.org/en/stable/operating-mode.html)
die Laufzeitbündelung und die Diagnosevorteile des Verzeichnisbundles.

Kurzer Alternativversuch auf P52, CPython 3.12.10 x64, py2exe 0.14.2.0:
`probe_py2exe.py` friert ein Minimalprogramm ein, nicht die vollständige IMS-App.
Messwerte am 30.09.2026: `bundle_files=1` wurde nach **0,402 s** mit
`Values of bundlefiles<3 are incompatible with Python 3.12+!` abgewiesen;
`bundle_files=3` baute nach **7,250 s**, EXE startete mit Exitcode 0 und
`py2exe-probe-ok`. Die zugehörigen Logs liegen zunächst lokal unter
`.tmp-pr-ap1/py2exe-probe`. Die Grenze entspricht der
[Projektbeschreibung](https://github.com/py2exe/py2exe).
Es wird keine einzelne py2exe-EXE oder vollständige IMS-Kompatibilität behauptet.
Der bereits vorgesehene PyInstaller-Weg vermeidet einen zweiten Freezer-/Hook-
Vertrag und ist durch den tatsächlichen IMS-Installer belegbar.

## Lizenzen und Signierung

Die gebündelten Python-/Tcl-/Paketlizenztexte werden mitgeliefert.
Die [PyInstaller-Ausnahme](https://pyinstaller.org/en/stable/license.html)
erlaubt die Verteilung erzeugter Anwendungen bei Einhaltung ihrer eigenen
Abhängigkeitslizenzen. Die tatsächlich heruntergeladene Inno-6.7.3-`License.txt`
erlaubt auch kommerzielle Nutzung unter Beibehaltung der Copyright-Hinweise;
siehe [Originaltext](https://jrsoftware.org/files/is/license.txt). Der Hersteller
bittet auf seiner Website bei kommerzieller Nutzung um einen Lizenzkauf; AP1
kauft nichts. Der Tool-Download wird per SHA-256 und Authenticode geprüft.
py2exe ist nur ein Entwicklungsversuch und wird nicht ausgeliefert.

Eine gesonderte Distributionslizenz des IMS-Projektcodes ist im Repository
bisher nicht vorhanden. Vor öffentlicher/externer Veröffentlichung sind
Projekt-/Referenzdatenrechte und Signierung verbindlich zu klären; der CI-
Download ist ein Prüfarbeitsstand. Kein regulatorisches oder juristisches
Freigabeurteil wird aus dem Tool-Build abgeleitet.

## Reproduzierbarer Build

Windows x64, CPython 3.12.10 und Node 22. Eigene `.venv` dieses Checkouts;
vollständig gepinnte Python-Build-Abhängigkeiten und `npm.cmd ci` mit Lockfile.

```powershell
.\.venv\Scripts\python.exe -m pip install -r scripts/installer/requirements-build.txt
.\.venv\Scripts\python.exe -m pip install --no-deps -e python_port
.\scripts\installer\install-build-tools.ps1
.\scripts\installer\build-installer.ps1
```

Ausgabe: `dist/installer/IMS-Setup-2.0.0-alpha.1-win-x64.exe`, SHA-256-Datei,
Build-Evidenz mit Commit, Dirty-Status, Version, Umgebung und gemessener Laufzeit,
Ressourceninventar. Gepinnte Eingaben und wiederholbarer Buildablauf sind
belegt; bitidentische PE-Dateien sind wegen Build-Metadaten nicht zugesagt.
GitHub Actions veröffentlicht nur ein 30 Tage verfügbares Run-Artefakt.

`test_installer.py` prüft den tatsächlichen Installer: separate Benutzerablage,
EXE mit System32-only PATH, Proxies unerreichbar, Umlaut-/Leerzeichenpfade,
Zweitstart, belegter Port, bestehenden Kranken-Zwei-Perioden-Fall und drei
Exporte, Übernahme mit Backups, Update während laufender Instanz sowie
Deinstallation/Neuinstallation mit wieder lesbarem Ergebnis.
Der Vorgänger-Installer ist eine **synthetische ältere Setup-Version desselben
Bundles**; dies prüft den Installationslebenszyklus, keine fachliche Migration
zwischen unterschiedlichen historischen IMS-Versionen. Auch CI ersetzt keine
separate Clean-Windows-Abnahme. Der vorhandene Windows-Release-Gate bleibt Pflicht.
