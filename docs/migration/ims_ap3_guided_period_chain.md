# AP3 M2: frischer geführter 100-Perioden-Aufbau

`ims.guided-period-chain-input.v1` enthält 100 vollständige Profile und
Kandidateneingaben sowie 99 explizite Carryover-Übergänge. Der synthetische
Workshop stammt aus dem bestehenden Vdefmd6-Profil und dem bisherigen
PR125-Kandidatentest. Die neue Produktionsvorlage liegt in
`ims/strategies/profiles/guided_candidate_template_v1.json`; Testmodule werden
vom Produkt nicht importiert. Ein VU, ein VN und zwei anonyme historische
Positionen sind deklariert, ohne Kfz-/Sach-Zuordnung oder historische Gleichheit.

Der Assistent erstellt für jede Periode eigene Seeds und Kanalwerte aus einer
versionierten SHA-256-Policy. Die vollständigen Werte bleiben im Quellenvertrag
sichtbar und editierbar; der Runner zieht beim Start keine Ersatzwerte. Sowohl
2- und 5-Perioden-Referenzen als auch die 100er-Kette werden frisch materialisiert.

Die bestehenden Kandidatenmaterialisierer und Profillader prüfen auch deklarierte
In-memory-Profile mit denselben fachlichen Prüfungen. Die vorhandene
Kettenauflösung akzeptiert neu bereits gebaute Payloads, verifiziert aber erneut
die Digests, Kontexte und Akteursidentität. Der alte Dateiprofil-/SQLite-Weg
bleibt erhalten. Der kanonische Ketteninhalt entspricht dem späteren gespeicherten
Inhalt; die read-only Vorschau benötigt keine temporären Profildateien oder DB.

Speicherung verlangt einen erwarteten Gesamtdigest und ausdrückliche Freigabe.
Alle 107 Kandidaten, drei Ketten und das deklarierte Bündel werden in einer
SQLite-Transaktion geschrieben. Konflikte rollen alles zurück; Wiederholungen
prüfen jeden bestehenden Datensatz und reparieren keine beschädigten Inhalte
stillschweigend. Ungültige Quellen bis einschließlich Periode 100 erzeugen keine
Teilresultate und keine Datenbank. 16-MiB-Quellenlimit und ein gleichzeitiger Bau.

Die UI bestätigt Speicherung und Referenzläufe getrennt. Tatsächliche PR140-/
PR145-Referenzläufe werden über die vorhandene Run-Control ausgeführt und
gespeichert. Erst anschließend startet der vorhandene PR151-Weg den ausdrücklich
bestätigten flüchtigen 100er-Lauf und dessen digestgebundenen ZIP-Export.
Vorhandene unveränderliche Referenzen werden erneut gelesen und geprüft.

## Zeitachsen-Grenze

`ims.model.agrsich_export.compute_global_period` berechnet bisher
`run_index * max_periods + period`. Das entspricht bei verkürzten Prüfhorizonten
für Laufindizes über 0 verschiedenen Globalperioden. Der neue Assistent
verwendet deshalb ausdrücklich nur Laufindex 0; unterschiedliche Fälle erhalten
eigene Seeds und Inhaltsnachweise. Andere Indizes werden vor Bau/Speicherung
gesperrt. Die vorhandene historische Exportsemantik und Prefixprojektion werden
nicht geändert. Ein zusätzlicher gemeinsamer Globalperiodenursprung braucht
einen eigenen geprüften Zeitvertrag, bevor diese Einschränkung aufgehoben wird.

## Technische Abnahme des Zwischenstands

15 neue Kern-/API-Prüfungen bestanden (39,43 s), einschließlich eines echten
100er-Laufs mit bytegleichen 2er-/5er-Prefixnachweisen. Zusätzlich bestanden
30 bestehende Kandidatenbau-/Kettenbau-/Auflösungsprüfungen; der erste gemeinsame
Lauf vor Ergänzung des Negativfalls für Laufindex 1 umfasste 44 Tests (35,73 s).
Vier reale Browserfälle bestanden in Hell/Dunkel bei 1440/390 Pixeln:
frischer Bau, Freigaben, reale Prefixläufe, 100 Zeilen, ZIP, Zustandserhalt,
Expertenfehler, kein Seitenüberlauf und keine axe-Verletzungen. TypeScript/Vite
bestanden. Die 100er-Tabelle erhielt einen beschrifteten Tastaturfokus.

M3–M5 und die AP3-Gesamtabnahme bleiben offen. Dieser Nachweis ist keine
fachliche Freigabe von Kfz-/Sach-Katalogstrategien oder regulatorischen Kennzahlen.

## Gefrorene Windows-Anwendung

Die neue tatsächliche 100er-Installerprüfung fand einen fehlenden Spawn-
Einstieg in `scripts/installer/entry.py`: Der isolierte PR151-Worker verwendet
unter Windows dieselbe eingefrorene EXE. Der normale Desktop-Parser darf seine
Workerargumente nicht verarbeiten. Der Einstieg ruft deshalb vor Desktop-
Import/Argumentverarbeitung `multiprocessing.freeze_support()` auf, gemäß
der [PyInstaller-Dokumentation](https://pyinstaller.org/en/stable/common-issues-and-pitfalls.html#multi-processing)
und dem lokalen Runtime-Hook der gepinnten Version 6.22.3. Der Worker bleibt
isoliert und erhält dieselben Zeit-/RSS-/Prefixprüfungen; die Rechnung wird
nicht ersatzweise in den Hauptprozess verlegt. Die tatsächliche neue Installer-
Wiederprüfung wird im Zwischenbericht festgehalten.

Beim Lesen der realen Installerprotokolle trat außerdem ein Fehler der bereits
vorhandenen gemeinsamen SQLite-Metadatenverbindung bei parallelen Lesezugriffen
auf. Ein isolierter CPython-3.12.10-Stresstest reproduzierte bei 28.800 Zugriffen
1.220 falsche/fehlende Zeilen oder SQLite-Fehler. `metadata_repository` schützt
jetzt die Verbindung einschließlich vollständigem Fetch/Transaktionsabschluss
und die erstmalige Lazy-Erzeugung. Derselbe Probeweg hat anschließend null
Fehler; zwei neue parallele Tests und 73 bestehende/ergänzte Repository-/
Import-/Desktopprüfungen bestanden (2,58 s). IDs, Datenschema, Importregeln und
Ausführungssperren bleiben erhalten. Neue 100er-Browserfälle prüfen auch
unerwartete API-Serverfehler; neue EXE und CI werden erneut abgenommen.
