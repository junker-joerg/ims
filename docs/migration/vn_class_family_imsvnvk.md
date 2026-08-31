# VN-Klassenaggregate IMSVNVK

## Ziel

Dieser Schnitt bereitet die historischen VN-Klassenaggregate `IMSVNVK1.DAT` bis
`IMSVNVK3.DAT` als weitere Legacy-Referenzfamilie vor. Er uebernimmt nur die
geprueften Originaldateien in den Referenzbestand und erweitert das
Validierungsbundle um belegte Ziele. Er startet keine Simulation, fuehrt keine neue Fachlogik ein
und behauptet keine historische Vollgleichheit.

## Mapping

| Legacy-Datei | Exportdatei | Subjekttyp | Stufe | Selektor |
| --- | --- | --- | --- | --- |
| `IMSVNVK1.DAT` | `imsvnvk1.dat` | `policyholder` | `III` | `rule_class = 1` |
| `IMSVNVK2.DAT` | `imsvnvk2.dat` | `policyholder` | `III` | `rule_class = 2` |
| `IMSVNVK3.DAT` | `imsvnvk3.dat` | `policyholder` | `III` | `rule_class = 3` |

Die Zuordnung entspricht dem bereits vorhandenen Agrsich-Exportpfad fuer
`policyholder_by_class`: `python_port/ims/model/agrsich_export.py` schreibt
`imsvnvk{aggregate_key}.dat` auf Stufe `III` mit `selector_kind =
"rule_class"`.

## Quelle und Format

Als Quelle wird gezielt `incomming/IMS.DAT/WVEMOD1.ZIP` verwendet. Dieses Archiv
passt zur bereits angebundenen `IMSVNR`-Familie und enthaelt die drei
`IMSVNVK`-Dateien jeweils mit 500 Ergebniszeilen. Diese zaehlen fuenf getrennte
Laeufe mit jeweils hoechstens 100 Perioden, keinen fortlaufenden 500er-Lauf.

Alle drei Dateien verwenden denselben VN-Agrsich-Header:

```text
#t Vu1 Vs1 Vp1 Ev1 Sh1 Vu2 Vs2 Vp2 Ev2 Sh2 Vm
```

| Datei | Zeilen | Perioden | SHA-256 |
| --- | ---: | --- | --- |
| `IMSVNVK1.DAT` | 500 | `1-500` | `bf21672275f325bc10584f9241827bdaf5288e471af23c3db94bd8fbfd308161` |
| `IMSVNVK2.DAT` | 500 | `1-500` | `cface3a3a521923c1b237985166930ef796872ada7d52265af3ab85b67b1cdf1` |
| `IMSVNVK3.DAT` | 500 | `1-500` | `766d5da11af81b6ff8fa98801f77ef0726a8b0237df27a090160490e831b93d4` |

## Validierung

Die Dateien werden vom vorhandenen VN-Legacy-Parser gelesen. Die Tests pruefen
Header, Periodenfenster und je Datei mindestens eine positive Alignment-Zeile.
Zum Zeitpunkt der VN-Klassenaufnahme enthielt das gemeinsame
Legacy-Validierungsbundle damit 16 historische Referenzziele mit 4800 konkret
verglichenen Zeilen; nach der anschliessenden `IMSVUVK`-Aufnahme umfasst das
aktuelle Bundle 19 Referenzziele mit 6300 konkret verglichenen Zeilen.

## Grenzen

- Die Referenzen belegen nur die konkret eingetragenen historischen Fenster.
- Alternative `IMSVNVK`-Varianten aus anderen ZIP-Archiven bleiben unversioniert
  und werden nicht stillschweigend vermischt.
- Die Aufnahme aendert keine VN-Klassenlogik und keine Vergleichstoleranz.
- `incomming/` bleibt lokaler Kandidatenbestand und wird nicht versioniert.

## Naechster Schritt

Nach diesem Schnitt ist `policyholder_class` im Legacy-Coverage-Backlog belegt.
Die danach vorbereiteten Versicherer-Klassenaggregate `IMSVUVK*.DAT` belegen
zusaetzlich `insurer_class`.

PR 85 erzeugt die drei VN-Klassen und VN-SK1/all fuer Perioden 1-100 nun aus
dem kontrollierten `Vdefmd6`-Zustand. Der Vergleich trifft 1.234/5.200 Felder
beziehungsweise 434/4.400 Fachwerte, aber keine vollstaendige Zeile. Die
historische klassenuebergreifende Akkumulatorsemantik und die konkrete
`WVEMOD1`-Laufidentitaet bleiben offen.
