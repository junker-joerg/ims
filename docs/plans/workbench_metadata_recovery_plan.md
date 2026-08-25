# Plan: Workbench-Metadaten-Recovery fuer PR 68

## Ziel

PR 68 prueft Backup/Restore sowie Update/Rollback der lokalen
Workbench-Metadaten mit einem bereits persistierten, validierten
Run-Control-Ergebnisstand. Der Schnitt bleibt technisch und fuegt weder
Fachlogik noch Simulation oder SQLite-Schemamigration hinzu.

## Vorhandene Datenquellen

| Bestand | Bedeutung fuer PR 68 |
| --- | --- |
| `scenarios`, `runs` | lokale Szenario- und Run-Metadaten |
| `run_control_queue` | Queue-Status `result_persisted` und Ausfuehrungsgrenzen |
| `run_control_execution_attempts` | Audit- und Abschlusszustand des kontrollierten Starts |
| `run_control_execution_results` | persistiertes, bereits validiertes Adapterresultat |
| `sqlite_readonly.py` | konservativer Read-only-Zugriff mit WAL-/SHM-Pruefung |

Der bestehende JSON-Metadatenexport umfasst nur `scenarios` und `runs`. Er ist
deshalb kein vollstaendiges Backup fuer den Ergebnisstand aus PR 63 bis PR 66.

## Umsetzung

1. Ein expliziter `backup`-Befehl liest eine vorhandene SQLite-Quelle und
   schreibt ueber die SQLite-Backup-API genau einen neuen Zielpfad.
2. Ein expliziter `restore`-Befehl schreibt ein geprueftes Backup in genau einen
   neuen Zielpfad.
3. Ein read-only `inspect`-Befehl validiert den belegten Ergebnisstand und gibt
   Tabellenzaehler sowie einen kanonischen Digest aus.
4. Ein read-only `verify`-Befehl vergleicht Quelle und Kandidat ueber die fuenf
   aktuell relevanten Tabellen.
5. Bestehende Ziele werden nicht ueberschrieben; fehlende Zielordner werden
   nicht implizit erzeugt.
6. Backup und Restore nutzen temporaere SQLite-Ziele im expliziten
   Zielverzeichnis und veroeffentlichen das Ergebnis erst nach erfolgreicher
   Zustandspruefung.

## Validierter Ergebnisstand

Die Probe akzeptiert nur einen Queue-Eintrag, fuer den gleichzeitig gilt:

- Queue-Status `result_persisted`;
- `execution_enabled = false`;
- mindestens ein abgeschlossener Attempt mit `result_persisted = true`;
- persistiertes Resultat mit `result_status = ok`;
- `simulation_performed = false`;
- keine automatische historische Regelwahl;
- keine historische Vollgleichheitsbehauptung.

Der Attempt darf dokumentieren, dass der kontrollierte technische Adapter
bereits gestartet wurde. PR 68 startet ihn nicht erneut.

## Update- und Rollback-Probe

- Der Repo-Pfad dient als bisheriger Anwendungspfad.
- Ein frisch gestagtes portables ZIP dient als getrennter Kandidatenpfad.
- Beide Anwendungspfade lesen dieselbe explizite Metadatenquelle mit ihrem
  jeweils eigenen `python_port` und liefern denselben Digest.
- Nach der Kandidatenpruefung liest der Repo-Pfad dieselbe Quelle erneut. Das
  ist der technische Rollback-Nachweis.

Beide Anwendungspfade enthalten im PR-Smoke denselben PR-68-Codebestand. Die
Probe belegt daher Pfadtrennung, reproduzierbaren Metadatenzugriff und den
Erhalt des Ergebnisstands, nicht die Kompatibilitaet beliebiger historischer
Programmversionen.

## Tests

- Backup, Restore und Digestgleichheit fuer alle fuenf Tabellen;
- committed WAL-Inhalt wird ueber SQLite-Backup erhalten;
- fehlender oder unvollstaendiger Ergebnisstand blockiert vor dem Schreiben;
- bestehende Ziele und gleiche Quell-/Zielpfade werden abgelehnt;
- CLI liefert stabile JSON-Grenzflags;
- realer Side-by-Side-Smoke aus Repo- und portablem Anwendungspfad.

## Grenzen

- kein automatisches Backup, Restore, Update oder Rollback;
- kein In-place-Ueberschreiben und keine SQLite-Schemamigration;
- kein Browser-Upload, Queue-Worker oder Adapterstart;
- keine Simulation und keine neue Fachlogik;
- keine historische Vollgleichheitsbehauptung.

## Danach

PR 69 erstellt den Abschlussbericht fuer den ersten
Produktionsfreigabekorpus: Altdatenumfang, Tests, bekannte Abweichungen,
Betriebsgrenzen und Bedienpfad.
