# IMS Workbench 2026 - Installation des Windows-Testpakets

Stand: 2026-09-01
Umfang: 2 Seiten
Zielgruppe: Anwender ohne Entwicklungsumgebung

## Seite 1 - Installieren und starten

### Was Sie benoetigen

- Windows 10 oder Windows 11;
- Python 3.12 oder neuer von `python.org`;
- eine Internetverbindung bei der ersten Installation;
- etwa 500 MB freien Speicherplatz;
- das ZIP `IMS-Workbench-2026-Windows-Test.zip`.

Node.js, npm, Git und Administratorrechte sind fuer dieses Testpaket nicht
erforderlich. Beim Installieren von Python muss die Option
`Add python.exe to PATH` aktiviert sein.

### 1. ZIP vollstaendig entpacken

Entpacken Sie das ZIP in einen neuen, lokal beschreibbaren Ordner, zum
Beispiel:

```text
C:\IMS\IMS-Workbench-2026
```

Starten Sie die Anwendung nicht direkt aus der ZIP-Vorschau. Kopieren Sie auch
keine Einzeldateien in eine aeltere IMS-Version. Jede Testversion bleibt in
ihrem eigenen Ordner.

### 2. Einmalig installieren

Doppelklicken Sie im entpackten Ordner auf:

```text
install-workbench.cmd
```

Das Skript prueft Python, legt ausschliesslich im IMS-Ordner die Umgebung
`.venv` an, installiert die benoetigten Web-Pakete und fuehrt danach den
technischen Check aus. Es installiert keinen Windows-Dienst und veraendert
keine globale Python-Umgebung.

Die Installation ist erfolgreich, wenn am Ende die Meldung erscheint, dass
die Workbench bereit ist. Das Fenster darf danach geschlossen werden.

### 3. Starten

Doppelklicken Sie auf:

```text
start-workbench.cmd
```

Lassen Sie das schwarze Serverfenster geoeffnet und rufen Sie im Browser auf:

```text
http://127.0.0.1:8000/
```

Die Adresse ist nur auf diesem Rechner erreichbar. Beim ersten Test sind keine
Firewall- oder Netzwerkfreigaben erforderlich.

<!-- PAGE BREAK -->

## Seite 2 - Pruefen, beenden und Fehler beheben

### Technischen Zustand pruefen

`check-workbench.cmd` kann jederzeit vor dem Start ausgefuehrt werden. Ein
erfolgreicher Check meldet Diagnose und Readiness mit `status: ok`. Er startet
keinen dauerhaften Server und keine Simulation.

Im Browser sollte das Dashboard `Backend bereit` und `Frontend gebaut`
anzeigen. Die Beispiel-Szenarien und -Runs werden aus dem mitgelieferten
Anwendungsstand geladen. Eine spaeter ausdruecklich konfigurierte lokale
Metadatendatei bleibt davon getrennt.

### Beenden

Aktivieren Sie das schwarze Serverfenster und druecken Sie `Strg+C`. Warten Sie,
bis der Prozess beendet ist. Danach kann der gesamte entpackte Ordner geloescht
werden. IMS richtet keinen Autostart und keinen Windows-Dienst ein.

### Haeufige Probleme

| Problem | Loesung |
| --- | --- |
| `Python was not found` | Python 3.12+ installieren, `Add python.exe to PATH` aktivieren und ein neues Fenster oeffnen |
| Installation der Pakete scheitert | Internetzugang und Firmen-Proxy pruefen, dann `install-workbench.cmd` erneut starten |
| `No module named uvicorn` | `install-workbench.cmd` im entpackten IMS-Ordner ausfuehren |
| Port 8000 ist belegt | In PowerShell vor dem Start `$env:IMS_WORKBENCH_PORT = "8138"` setzen und danach Port 8138 im Browser verwenden |
| Frontend fehlt | ZIP erneut vollstaendig in einen neuen Ordner entpacken |
| Windows warnt vor dem Skript | Herkunft und ZIP-Pruefsumme pruefen; betriebliche Sicherheitsregeln nicht umgehen |

### Was diese Installation belegt

Ein erfolgreicher Start belegt, dass die lokale Workbench auf diesem Rechner
technisch laeuft. Er ist keine fachliche Produktionsfreigabe und kein Nachweis,
dass historische Zufallszahlen oder alte Einzellaeufe exakt reproduziert
werden. Welche Funktionen Sie heute sinnvoll testen koennen, steht in der
`BEDIENUNGSANLEITUNG.pdf`.
