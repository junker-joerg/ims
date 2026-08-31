# Versicherer-Klassenaggregate IMSVUVK

## Ziel

Dieser Schnitt bereitet die historischen Versicherer-Klassenaggregate
`IMSVUVK1.DAT` bis `IMSVUVK3.DAT` als weitere Legacy-Referenzfamilie vor. Er
uebernimmt nur die geprueften Originaldateien in den Referenzbestand und
erweitert das Validierungsbundle um belegte Ziele. Er startet keine Simulation,
fuehrt keine neue Fachlogik ein und behauptet keine historische Vollgleichheit.

## Mapping

| Legacy-Datei | Exportdatei | Subjekttyp | Stufe | Selektor |
| --- | --- | --- | --- | --- |
| `IMSVUVK1.DAT` | `imsvuvk1.dat` | `insurer` | `III` | `rule_class = 1` |
| `IMSVUVK2.DAT` | `imsvuvk2.dat` | `insurer` | `III` | `rule_class = 2` |
| `IMSVUVK3.DAT` | `imsvuvk3.dat` | `insurer` | `III` | `rule_class = 3` |

Die Zuordnung entspricht dem bereits vorhandenen Agrsich-Exportpfad fuer
`insurer_by_class`: `python_port/ims/model/agrsich_export.py` schreibt
`imsvuvk{aggregate_key}.dat` auf Stufe `III` mit `selector_kind =
"rule_class"`.

## Quelle und Format

Als Quelle wird gezielt `incomming/IMS.DAT/WVEMOD1.ZIP` verwendet. Dieses Archiv
passt zu den bereits angebundenen `IMSVNR`- und `IMSVNVK`-Familien und enthaelt
die drei `IMSVUVK`-Dateien jeweils mit 500 Ergebniszeilen. Diese zaehlen fuenf
getrennte Laeufe mit jeweils hoechstens 100 Perioden, keinen fortlaufenden
500er-Lauf.

Alle drei Dateien verwenden denselben Versicherer-Agrsich-Header:

```text
#t Pr1 Wa1 Rs1 Vn1 Sa1 Sh1 Pr2 Wa2 Rs2 Vn2 Sa2 Sh2
```

| Datei | Zeilen | Perioden | SHA-256 |
| --- | ---: | --- | --- |
| `IMSVUVK1.DAT` | 500 | `1-500` | `49ed53daaf6d13a9f850ed5628f79e4d9fb5e73b61359009159517ef35cb6e0f` |
| `IMSVUVK2.DAT` | 500 | `1-500` | `619fc2e5624ab575c9b73ab0891ab88b1883317efbab262b726f1237f0cc3b3d` |
| `IMSVUVK3.DAT` | 500 | `1-500` | `ed280b96d3f6daf4cf64de88c8de17b79b595d7ec928f8ca2df0ef0635a595bc` |

## Validierung

Die Dateien werden vom vorhandenen Versicherer-Legacy-Parser gelesen. Die Tests
pruefen Header, Periodenfenster und je Datei mindestens eine positive
Alignment-Zeile. Das gemeinsame Legacy-Validierungsbundle enthaelt damit 19
historische Referenzziele mit 6300 konkret verglichenen Zeilen.

## Grenzen

- Die Referenzen belegen nur die konkret eingetragenen historischen Fenster.
- Alternative `IMSVUVK`-Varianten aus anderen ZIP-Archiven bleiben unversioniert
  und werden nicht stillschweigend vermischt.
- Die Aufnahme aendert keine Versicherer-Klassenlogik und keine
  Vergleichstoleranz.
- `incomming/` bleibt lokaler Kandidatenbestand und wird nicht versioniert.

## Naechster Schritt

Nach diesem Schnitt ist `insurer_class` im Legacy-Coverage-Backlog belegt. Der
naechste groessere Kandidat ist ein schmaler Kernlogik-/Planfixture-Schnitt.
Parameterausgaben wie `VU014PR1.DAT` bleiben bis zu einer belastbaren
Feldklaerung geparkt und werden nicht als Agrsich-Referenz importiert.
