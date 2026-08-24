# Getrennte historische Referenzschicht ZINS000

## Ziel

PR 57 uebernimmt genau zwei zuvor lokal bereitgestellte Agrsich-Dateien als
getrennte historische Referenzschicht:

- `IMSVU014.DAT` fuer Versicherer 14;
- `IMSVUSK1.DAT` fuer das Versicherer-`SK1`-/`all`-Aggregat.

Die Schicht ergaenzt nicht das produktive Legacy-Validierungsbundle. Dessen
Kern bleibt bei 19 Dateien und 6.300 Vergleichsperioden. Es wird keine
Simulation gestartet, keine Fachlogik geaendert und keine historische
Vollgleichheit behauptet.

## Herkunft und versionierte Ablage

Die lokale Quelle war `incomming/ZINS000/`. Die beiden gezielt geprueften
Dateien liegen versioniert unter:

```text
tests/references/legacy_agrsich/zins000/
```

Der lokale Verzeichnisname `ZINS000` bezeichnet den bereitgestellten
Quellkontext. Die lokalen Zeitstempel aus 2026 belegen weder den historischen
Erzeugungszeitpunkt noch einen bestimmten Archivlauf. Ein genauerer
historischer Generator- oder C-Funktionsnachweis liegt fuer dieses Paar nicht
vor; PR 57 erfindet keine nachtraegliche Zuordnung.

Die maschinenlesbare Herkunfts- und Mappinggrenze steht in
`tests/fixtures/legacy_zins000_reference_layer.json`.

| Datei | SHA-256 | Zeilen / Perioden |
| --- | --- | --- |
| `IMSVU014.DAT` | `0276eab7b1f80dfc39773eb0e5a4a5df02b69b140792be9f810baa222e8ce828` | 300 / `1-300` |
| `IMSVUSK1.DAT` | `dc066d624c443fc165b0fb83481083dae33d823bd8a3a20d934adb4bf5426b2a` | 300 / `1-300` |

`incomming/` selbst bleibt unversioniert.

## C-zu-Python-Zuordnung

Dieser PR portiert keine C-Logik. Er ordnet historische Ausgaben vorhandenen
Python-Lese- und Exportgrenzen zu:

| Historische Ausgabe | Python-Komponente | Fachliche Einordnung |
| --- | --- | --- |
| `IMSVU014.DAT` | `parse_legacy_insurer_dat` | insurer / Stufe I / `entity = 14` / Export `imsvu014.dat` |
| `IMSVUSK1.DAT` | `parse_legacy_insurer_dat` | insurer / Stufe IV / `all = SK1` / Export `imsvusk1.dat` |

Beide Dateien verwenden den vorhandenen 13-spaltigen Versicherer-Agrsich-
Header:

```text
#t Pr1 Wa1 Rs1 Vn1 Sa1 Sh1 Pr2 Wa2 Rs2 Vn2 Sa2 Sh2
```

## Belegte Grenzen

Parser-, Hash- und Periodentests sichern folgende Aussagen ab:

- beide Dateien sind mit `parse_legacy_insurer_dat` lesbar;
- jede Datei enthaelt genau die lueckenlosen Perioden `1-300`;
- die versionierten Inhalte entsprechen den dokumentierten SHA-256-Werten;
- `IMSVU014.DAT` hat im Fenster `1-100` keine numerisch identische
  Periodenzeile mit `VU14L1.DAT` (`0/100`);
- `IMSVUSK1.DAT` hat im Fenster `1-300` keine numerisch identische
  Periodenzeile mit den zusammengehoerigen Baseline-Zeitfenstern `VUSK1L5`,
  `VUSK1L4` und `VUSK1L3` (`0/300`).

Die Nichtidentitaet ist kein fachlicher Abweichungsbefund eines berechneten
Neu-/Alt-Laufs. Sie belegt nur, dass ZINS000 weder Ersatz noch Fortsetzung der
heutigen Baseline ist.

## Bewusster Ausschluss aus dem Kernbundle

`tests/fixtures/legacy_validation_bundle.json` bleibt unveraendert. Das
Unterverzeichnis `legacy_agrsich/zins000/` wird vom flachen Kernkorpus-Scan
nicht als zusaetzliche Bundle-Datei gezaehlt. Ein spaeterer berechneter
Mehrperiodenvergleich muss die Schicht explizit auswaehlen und darf Ergebnisse
nicht mit dem Kernkorpus vermischen.

## Offene Punkte

- Der genaue historische Laufkontext von ZINS000 bleibt unbelegt.
- Historischer RNG, Scheduler und automatische Regelwahl lassen sich aus den
  beiden Ausgabedateien nicht rekonstruieren.
- PR 58 bereitet den kontrollierten berechneten Mehrperiodenvergleich fuer den
  Kernkorpus vor. ZINS000 bleibt dabei eine separat waehlbare Referenzschicht.
