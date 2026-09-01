# Daten, Backup und Updates

Stand: 2026-09-01
Handbuchstand: HB3

Anwendung und lokale Daten werden getrennt behandelt. Diese Trennung macht
Backup, Update und Rollback nachvollziehbar und verhindert, dass eine neue
Version still ueber eine bestehende Datenablage kopiert wird.

## Was wo liegt

| Bestandteil | Portabler Ordner | Entwickler-Checkout |
| --- | --- | --- |
| Anwendung | `app`, Startskripte | `python_port`, `frontend/dist`, Startskripte |
| Metadaten | `data/.ims_workbench/metadata.sqlite` | `.ims_workbench/metadata.sqlite` |
| SQLite-Begleitdateien | neben `metadata.sqlite` | neben `metadata.sqlite` |
| lokale Logs | `logs` | explizit gewaehlter lokaler Pfad |

Die SQLite-Begleitdateien `metadata.sqlite-wal` und `metadata.sqlite-shm`
koennen waehrend des Betriebs vorhanden sein. `incomming/` gehoert nicht zu
diesen Benutzerdaten und ist kein Importpfad der Workbench.

## Backup

1. Workbench mit `Strg+C` vollstaendig stoppen.
2. Einen neuen, datierten Backup-Ordner anlegen.
3. Metadatendatei und vorhandene SQLite-Begleitdateien gemeinsam kopieren.

Beispiel fuer einen portablen Ordner:

```powershell
$source = ".\data\.ims_workbench"
$backup = "C:\IMS Backups\2026-09-01"
New-Item -ItemType Directory -Path $backup
Copy-Item -Path "$source\metadata.sqlite*" -Destination $backup
```

Die Workbench darf waehrend dieses Datei-Backups nicht laufen. Ein Backup des
Anwendungsordners ersetzt das Metadaten-Backup nicht.

## Restore in einen neuen Pfad

Ein Restore wird nicht in eine laufende oder ungepruefte vorhandene Datenbank
geschrieben. Kopiere das Backup zuerst in einen neuen Zielordner:

```powershell
$restore = "C:\IMS Daten\Restore 2026-09-01"
New-Item -ItemType Directory -Path $restore
Copy-Item -Path "C:\IMS Backups\2026-09-01\metadata.sqlite*" -Destination $restore
$env:IMS_METADATA_DB = "$restore\metadata.sqlite"
.\check-workbench.cmd
```

Erst nach einem erfolgreichen Check wird die Workbench mit derselben
`IMS_METADATA_DB`-Einstellung gestartet. Das urspruengliche Backup bleibt
unveraendert.

## Update Side-by-Side

Eine neue Workbench-Version wird immer in einen neuen Ordner gelegt:

```text
C:\IMS\IMS Workbench 2026-08-25\
C:\IMS\IMS Workbench 2026-09-01\
C:\IMS Daten\metadata.sqlite
```

Vorgehen:

1. alte Workbench stoppen;
2. Metadaten sichern;
3. neue Version in einen eigenen Ordner bereitstellen;
4. Python-Umgebung der neuen Version einrichten;
5. neue Version mit explizitem Metadatenpfad pruefen;
6. erst danach die neue Version starten.

Beispiel im neuen Workbench-Ordner:

```powershell
$env:IMS_METADATA_DB = "C:\IMS Daten\metadata.sqlite"
$env:Path = "$(Resolve-Path .\.venv\Scripts);$env:Path"
.\check-workbench.cmd
.\start-workbench.cmd
```

Eine neue Version wird nicht ueber die alte kopiert. Es gibt keine
automatische SQLite-Schemamigration und keinen automatischen Updater.

## Rollback

1. neue Workbench stoppen;
2. neue Version nicht loeschen, solange die Ursache ungeklart ist;
3. alte Version mit ihrer bekannten Python-Umgebung starten;
4. den zuletzt geprueften Metadatenpfad verwenden;
5. bei Bedarf zuerst eine gesicherte Datenbank in einen neuen Pfad
   wiederherstellen.

Rollback bedeutet Versionswechsel, nicht automatisches Datenbank-Downgrade.
Falls eine spaetere Version eine Schemamigration einfuehrt, braucht sie einen
eigenen Migrations- und Rueckfallvertrag.

## Aufbewahrung und Loeschen

- Backups erhalten Datum und verwendete IMS-Version im Ordnernamen.
- Mindestens das letzte vor einem Update erstellte Backup bleibt erhalten.
- Logs koennen nach fachlicher und technischer Pruefung separat archiviert
  oder geloescht werden.
- Ein Anwendungsordner wird erst nach Serverstop, Backup und erfolgreichem
  Start der gewaehlten Version entfernt.

## Aussagegrenzen

Backup und Restore erhalten lokale Workbench-Metadaten. Sie erzeugen keine
historischen Parameter, RNG-Folgen oder Simulationsergebnisse und sind kein
Nachweis historischer Vollgleichheit. Der technische Side-by-Side-Pfad ist
belegt; die Kompatibilitaet beliebiger zukuenftiger Datenbankschemata ist es
nicht.
