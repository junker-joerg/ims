# Inventar historischer IMS-Testdaten

## Ziel

Diese Notiz inventarisiert die lokal bereitgestellten historischen Testdaten
unter `incomming/`, ohne sie in die referenzierten Testdaten zu uebernehmen.
Sie dient als fachliche Vorstufe fuer spaetere kleine PRs, die einzelne
Dateifamilien gezielt nach `tests/references/legacy_agrsich/` ueberfuehren.

## Quelle

Lokaler Pfad:

```text
C:\Users\mjkoe\Documents\Codex\ims\incomming
```

Der Ordner ist bewusst kein versionierter Referenzbestand. Die Dateien wurden
nur gelesen und gezaehlt. Es wurde nichts importiert, nichts verschoben und
keine Simulation gestartet.

## Inventarstand

Der lokale Bestand enthaelt:

- `39` direkt sichtbare `.DAT`-Dateien;
- `7` `.ZIP`-Archive;
- alte Quellzeitstempel ueberwiegend aus Juli und September 1995;
- ein bereits entpacktes `ZINS000`-Verzeichnis mit lokalen 2026-Zeitstempeln.

Direkt sichtbare, fuer den bestehenden Backlog relevante Dateien:

- `VU14L1.DAT`;
- `VUSK1L1.DAT` bis `VUSK1L5.DAT`;
- `VU014PR1.DAT`;
- `IMSVNR01.DAT`, `IMSVNR02.DAT`;
- `IMSVNSK1.DAT`;
- `IMSVU001.DAT` bis `IMSVU025.DAT`;
- `IMSVUSK1.DAT`.

In den ZIP-Archiven wurden weitere relevante Kandidaten gefunden:

- `IMSVNR01.DAT` bis `IMSVNR06.DAT`;
- `IMSVNVK1.DAT` bis `IMSVNVK3.DAT`;
- `IMSVUR01.DAT` bis `IMSVUR09.DAT`;
- `IMSVUVK1.DAT` bis `IMSVUVK3.DAT`;
- `IMSVU014.DAT`, `IMSVUSK1.DAT`;
- laengere Varianten mit 500 oder 3000 Periodenzeilen, je nach Archiv.

## Parser-Plausibilitaet

Die vorhandenen Parser konnten zentrale Kandidaten lesen:

| Datei | Parserfamilie | Zeilen | Perioden |
| --- | --- | ---: | --- |
| `VU14L1.DAT` | Versicherer | 100 | `1-100` |
| `VU014PR1.DAT` | Parameterausgabe | 100 | `1-100` |
| `VUSK1L1.DAT` | Versicherer | 100 | `401-500` |
| `VUSK1L2.DAT` | Versicherer | 100 | `301-400` |
| `VUSK1L3.DAT` | Versicherer | 100 | `201-300` |
| `VUSK1L4.DAT` | Versicherer | 100 | `101-200` |
| `VUSK1L5.DAT` | Versicherer | 100 | `1-100` |
| `IMSVU014.DAT` | Versicherer | 300 | `1-300` |
| `IMSVUSK1.DAT` | Versicherer | 300 | `1-300` |
| `IMSVUVK1.DAT` | Versicherer | 500 | `1-500` |
| `IMSVUVK2.DAT` | Versicherer | 500 | `1-500` |
| `IMSVUVK3.DAT` | Versicherer | 500 | `1-500` |
| `IMSVNR01.DAT` | VN | 300 | `1-300` |
| `IMSVNR02.DAT` | VN | 300 | `1-300` |
| `IMSVNR03.DAT` | VN | 500 | `1-500` |
| `IMSVNR04.DAT` | VN | 500 | `1-500` |
| `IMSVNR06.DAT` | VN | 500 | `1-500` |
| `IMSVNVK1.DAT` | VN | 500 | `1-500` |
| `IMSVNVK2.DAT` | VN | 500 | `1-500` |
| `IMSVNVK3.DAT` | VN | 500 | `1-500` |
| `IMSVNSK1.DAT` | VN | 300 | `1-300` |

ZIP-Stichproben waren ebenfalls mit den bestehenden Parsern lesbar, darunter
`IMSVNR03.DAT`, `IMSVNR04.DAT`, `IMSVNR06.DAT`, `IMSVNVK1.DAT`,
`IMSVUVK1.DAT`, `IMSVUR01.DAT` und `IMSVUVK3.DAT`.

## Abgrenzung zum bestehenden Referenzbestand

Die neuen Kandidaten sind nicht blind identisch mit den bereits versionierten
Referenzen unter `tests/references/legacy_agrsich/`. Fuer gleichnamige Dateien
wurden abweichende Groessen und SHA-256-Hashes beobachtet. Das ist kein
Ablehnungsgrund, aber ein Hinweis, dass jede Uebernahme Quelle, Archivfamilie,
Periodenfenster und Vergleichsannahme explizit dokumentieren muss.

Bis PR 72 wurden vorhandene Referenzen nicht ueberschrieben. PR 73 korrigiert
gezielt die faelschlich lineare `VU14L1.DAT`, nachdem Zeitfenster, Teildateien
und Archivfassung dieselbe historische Reihe dreifach belegt haben. Neue
Dateifamilien werden weiterhin nur in separaten PRs aufgenommen.

## Empfohlene Reihenfolge

1. `VUSK1L1.DAT` bis `VUSK1L5.DAT` sind als erste neue
   Versicherer-SK1-Zeitfenster uebernommen, weil Format und Periodenfenster zum
   vorhandenen Parser passen. Sie sind keine unterschiedlichen Aggregatebenen.
2. `IMSVNR01.DAT` und `IMSVNR02.DAT` sind als erste zusaetzliche
   VN-Regelreferenzen uebernommen, weil Format, Header und Periodenfenster zum
   vorhandenen Parser passen.
3. `IMSVNR03.DAT` und `IMSVNR04.DAT` sind aus `WVEMOD1.ZIP` als weitere
   VN-Regelreferenzen uebernommen, weil Format, Header und Periodenfenster zum
   vorhandenen Parser passen.
4. `IMSVNR06.DAT` ist als letzte fehlende Datei der VN-Regelfamilie aus
   `WVEMOD1.ZIP` uebernommen; `IMSVNR05.DAT` wird im Bundle nun mit dem
   vollen `1-500`-Fenster der Gesamtfamilie abgeglichen.
5. `IMSVNVK1.DAT` bis `IMSVNVK3.DAT` sind aus `WVEMOD1.ZIP` als
   VN-Klassenaggregate uebernommen, weil Format, Header und Periodenfenster zum
   vorhandenen VN-Parser passen.
6. `IMSVUVK1.DAT` bis `IMSVUVK3.DAT` sind aus `WVEMOD1.ZIP` als
   Versicherer-Klassenaggregate uebernommen, weil Format, Header und
   Periodenfenster zum vorhandenen Versicherer-Parser passen.
7. `VU014PR1.DAT` ist als Parameterausgabe inventarisiert: Header
   `#t Pr1L1 Pr1l2 Pr1L3 Pr1L4 Pr1L5`, 100 Datenzeilen und Periodenfenster
   `1-100`; die Altcode-Spur belegt `Pr1` nur als Versicherer-Praemienbezug
   fuer Sparte 1, aber nicht die Bedeutung von `L1` bis `L5`. Verwandte lokale
   Kandidaten `VU14P1.DAT`, `VU14P2.DAT` und archivierte `IMSVU014.DAT`
   Varianten sind normale 13-spaltige Agrsich-Ausgaben und klaeren das
   Parameterausgabe-Format nicht. Keine Uebernahme ohne geklaertes
   Feldmapping.

## Grenzen

- keine weitere Uebernahme lokaler `incomming/`-Dateien ausserhalb gezielter
  Folge-PRs;
- keine Vergleichslaeufe gegen noch nicht versionierte Referenzen;
- keine Simulation;
- keine Fachlogikaenderung;
- keine historische Vollgleichheitsbehauptung.

## Produktionskorpus-Entscheidung PR 56

Der verpflichtende erste Freigabekorpus bleibt auf die 19 bereits
versionierten Referenzen und 6.300 Bundle-Zeilen begrenzt. Details und
Freigabegates stehen in `docs/plans/production_legacy_corpus_plan.md`.

PR 57 hat als einzigen lokalen Aufnahmeentscheid das ZINS000-Paar
`IMSVU014.DAT` und `IMSVUSK1.DAT`. Beide Dateien enthalten 300 Perioden im
Versicherer-Agrsich-Format, stimmen aber numerisch in keiner ueberlappenden
Periode mit `VU14L1.DAT` beziehungsweise den Zeitfenstern `VUSK1L5` bis
`VUSK1L3` ueberein. Sie sind deshalb unter
`tests/references/legacy_agrsich/zins000/` nur als getrennte historische
Schicht versioniert und nicht als Ersatz oder Fortsetzung der heutigen
Baseline bewertet. Das produktive Kernbundle bleibt unveraendert.

## Berechneter Vergleichsvertrag PR 58

PR 58 laesst Inventar und Kernbundle unveraendert. Der neue Sollplan verlangt
fuer einen spaeteren berechneten Vergleich exakt 15 Exporttabellen, 19 Ziele
und 6.300 Perioden. ZINS000 bleibt eine getrennt waehlbare Schicht. Es wurden
keine weiteren Dateien aus `incomming/` uebernommen.

## Read-only Abweichungsdiagnose PR 59

PR 59 veraendert Inventar, Referenzen und Bundle ebenfalls nicht. Ohne
gelieferte berechnete Tabellen meldet die Diagnose fuer den Kernkorpus 15
blockierende `required_export_missing`-Issues. Dieser Befund beschreibt die
noch fehlende Berechnungsanbindung und keine historische Modellabweichung.

## Erster berechneter VU14-Slice PR 60

PR 60 nutzt ausschließlich die bereits versionierte `VU14L1.DAT` und das
belegte Fenster `1-4`. Es werden keine weiteren historischen Dateien
uebernommen. Vier explizite, referenzausgerichtete Zustandsinputs liefern einen
passenden Aggregat-/Exportvergleich; eine unabhaengige historische
Zustandsentwicklung ist dadurch nicht belegt.

## VU14-Quellenkorrektur PR 73

PR 73 ersetzt die damals verwendete linear konstruierte VU14-Testreihe durch
den gezielt geprueften Kandidaten `incomming/IMS.DAT/VU14L1.DAT`. Dessen
Perioden 1-50 und 51-100 stimmen tokenweise mit `VU14P2.DAT` und `VU14P1.DAT`
ueberein; zusaetzlich stimmt `WVEMOD1.ZIP/IMSVU014.DAT` in 1-100. Nur die
100-zeilige Zielreferenz wurde versioniert, `incomming/` bleibt unversioniert.

Die bisherigen Vier-Perioden-Fixtures sind auf die echten Zeilen 1-4
ausgerichtet. Sie bleiben direkte Vergleichseingaben. Nur Periode 1 wird
zusaetzlich unabhaengig aus der `Vdefmd6`-Initialisierung erzeugt.
