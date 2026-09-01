# Windows installieren

Stand: 2026-09-01
Handbuchstand: HB3
Supportstufe: `verified_windows_hb3`

IMS wird derzeit als lokale Browser-Workbench bereitgestellt. Es gibt keinen
nativen Windows-Installer, keinen Windows-Dienst und keinen automatischen
Updater. Die Workbench bindet standardmaessig ausschliesslich an
`127.0.0.1` und ist damit nur auf dem lokalen Rechner erreichbar.

## Gepruefte Voraussetzungen

| Bestandteil | Benutzer eines portablen Ordners | Entwickler-Checkout |
| --- | --- | --- |
| Windows und PowerShell | erforderlich | erforderlich |
| Python 3.12 oder neuer | erforderlich | erforderlich |
| Python-Pakete `fastapi` und `uvicorn` | erforderlich | im Extra `dev` enthalten |
| Node.js 22 und npm | nicht erforderlich | fuer Frontend-Build erforderlich |
| Git | nicht erforderlich | nur fuer Checkout und Versionspflege |

Der HB3-Abnahmelauf erfolgte mit PowerShell 7.6.4, Python 3.13.7,
Node.js 22.18.0 und npm 10.9.3. Das Windows-CI-Gate verwendet Python 3.12
und Node.js 22. Python 3.12+ ist der Paketvertrag; die genannten lokalen
Patchversionen sind keine zusaetzliche Mindestanforderung.

Pruefe die installierten Werkzeuge mit:

```powershell
python --version
python -m pip --version
node --version
npm.cmd --version
```

Die beiden letzten Befehle sind nur fuer den Entwickler-Checkout notwendig.

## Weg A: Vorbereiteter portabler Ordner

Dieser Weg ist fuer Anwender vorgesehen. Das technisch erzeugte lokale
Workbench-ZIP wird vor der Weitergabe in die portable Struktur gestaged. Ein
bereitgestellter Ordner enthaelt mindestens:

```text
IMS Workbench 2026/
  app/
    frontend/dist/
    python_port/
  data/.ims_workbench/
  logs/
  check-workbench.cmd
  start-workbench.cmd
```

Wenn dieser Ordner fuer den Transport nochmals als ZIP verpackt wurde, muss er
vollstaendig in einen neuen Zielordner entpackt werden. Einzelne Dateien duerfen
nicht in eine vorhandene Workbench-Version kopiert werden.

### Einmalige Python-Einrichtung

```powershell
Set-Location "C:\IMS Tests\IMS Workbench 2026"
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".\app\python_port[web]"
$env:Path = "$(Resolve-Path .\.venv\Scripts);$env:Path"
```

Danach:

```powershell
.\check-workbench.cmd
.\start-workbench.cmd
```

Der kuerzeste vollstaendige Ablauf steht im
[Windows-Kurzstart](quickstart_windows.md).

## Weg B: Entwickler-Checkout

Dieser Weg baut das Frontend aus dem versionierten Quellstand neu. Fuehre die
Befehle im Repository-Root aus:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".\python_port[dev]"
$env:Path = "$(Resolve-Path .\.venv\Scripts);$env:Path"
npm.cmd ci --prefix .\frontend
npm.cmd run build --prefix .\frontend
.\scripts\workbench\check-workbench.cmd
.\scripts\workbench\start-workbench.cmd
```

`npm.cmd ci` verwendet das versionierte Lockfile. Ein fehlendes `tsc` wird
durch diesen Installationsschritt bereitgestellt; ein global installiertes
TypeScript ist nicht erforderlich.

## Check, Start und Health

| Schritt | Wirkung |
| --- | --- |
| `check-workbench.cmd` | prueft Frontend, Python-Import, Web-Abhaengigkeiten und Readiness; startet keinen Server |
| `start-workbench.cmd` | startet den lokalen FastAPI-/Uvicorn-Server und liefert das gebaute Frontend aus |
| `GET /api/health` | bestaetigt Backendstatus und Verfuegbarkeit des Frontends |
| `Strg+C` | beendet den Server im Startfenster |

Der Start erzeugt keinen Run und startet keine Simulation. Bedienaktionen wie
Queue-Vormerkung oder Adapterstart sind davon getrennte, ausdrueckliche
Schritte.

## Konfiguration fuer einen einzelnen Start

Die Skripte akzeptieren vier Umgebungsvariablen:

```powershell
$env:IMS_WORKBENCH_HOST = "127.0.0.1"
$env:IMS_WORKBENCH_PORT = "8138"
$env:IMS_FRONTEND_DIST = "C:\IMS Tests\IMS Workbench 2026\app\frontend\dist"
$env:IMS_METADATA_DB = "C:\IMS Daten\metadata.sqlite"
```

Der Host soll lokal auf `127.0.0.1` bleiben. Eine Freigabe im Netzwerk ist
nicht Bestandteil des HB3-Supportvertrags.

Standardpfade:

| Layout | Frontend | Metadaten |
| --- | --- | --- |
| portabler Ordner | `app\frontend\dist` | `data\.ims_workbench\metadata.sqlite` |
| Entwickler-Checkout | `frontend\dist` | `.ims_workbench\metadata.sqlite` |

Der reine Check legt eine fehlende Metadatendatei nicht an. Ein gestarteter
Workbench-Prozess kann die konfigurierte lokale Ablage fuer seine
Metadatenpfade verwenden.

## Stop und Deinstallation

1. Serverfenster aktivieren und `Strg+C` druecken.
2. Kontrollieren, dass `http://127.0.0.1:<port>/api/health` nicht mehr
   erreichbar ist.
3. Lokale Metadaten und benoetigte Logs sichern.
4. Den Workbench-Ordner ueber den Windows-Explorer entfernen.
5. Die lokale `.venv` darf zusammen mit dem Anwendungsordner entfernt werden.

IMS registriert in diesem Bereitstellungsweg keinen Dienst und keine
Autostart-Aufgabe. Eine systemweit installierte Python- oder Node.js-Laufzeit
wird nicht automatisch entfernt.

## Haeufige Installationsfehler

| Meldung | Naechster Check |
| --- | --- |
| `python` wurde nicht gefunden | Python 3.12+ installieren und neues PowerShell-Fenster oeffnen |
| `No module named uvicorn` | Python-Umgebung wie oben einrichten und deren `Scripts`-Ordner in diesem Fenster voranstellen |
| `frontend dist is missing` | portablen Ordner auf Vollstaendigkeit pruefen oder im Checkout den Frontend-Build ausfuehren |
| `tsc` wurde nicht gefunden | im Checkout zuerst `npm.cmd ci --prefix .\frontend` ausfuehren |
| Port bereits belegt | freien `IMS_WORKBENCH_PORT` setzen und Browseradresse anpassen |

Eine zusammengefasste Fehlerhilfe folgt in HB6. Datenpflege und sichere
Versionswechsel stehen bereits in
[Daten, Backup und Updates](data_and_updates.md).

## Gepruefter HB3-Nachweis

Am 2026-09-01 wurde ein neues lokales ZIP erzeugt und in
`Portable IMS Workbench 2026` unter einem Pfad mit Leerzeichen gestaged.
Frontend-Build, portables Checkskript, Startskript, HTTP-Health und die
Browseroberflaeche waren erfolgreich. Der Server wurde danach kontrolliert
beendet. Es wurden keine Queue-Aktion, kein Adapter und keine Simulation
gestartet.
