# VN-Regelfamilie IMSVNR01 bis IMSVNR06

## Ziel

Diese Notiz bereitet die historischen VN-Regeldateien `IMSVNR01.DAT` bis
`IMSVNR06.DAT` als zusammenhaengende Validierungsfamilie vor. Sie fuegt keine
neue Fachlogik hinzu, uebernimmt keine lokalen `incomming/`-Dateien und startet
keine Simulation.

## Mapping

| Legacy-Datei | VN-Regel | Exportdatei | Ebene | Selektor |
| --- | --- | --- | --- | --- |
| `IMSVNR01.DAT` | `Vrvn01` | `imsvnr01.dat` | `II` | `rule = 1` |
| `IMSVNR02.DAT` | `Vrvn02` | `imsvnr02.dat` | `II` | `rule = 2` |
| `IMSVNR03.DAT` | `Vrvn03` | `imsvnr03.dat` | `II` | `rule = 3` |
| `IMSVNR04.DAT` | `Vrvn04` | `imsvnr04.dat` | `II` | `rule = 4` |
| `IMSVNR05.DAT` | `Vrvn05` | `imsvnr05.dat` | `II` | `rule = 5` |
| `IMSVNR06.DAT` | `Vrvn06` | `imsvnr06.dat` | `II` | `rule = 6` |

Alle sechs Dateien nutzen das vorhandene VN-Agrsich-Tabellenformat mit den
Spalten:

```text
#t Vu1 Vs1 Vp1 Ev1 Sh1 Vu2 Vs2 Vp2 Ev2 Sh2 Vm
```

## Aktueller Stand

Im versionierten Referenzbestand sind derzeit `IMSVNR01.DAT`, `IMSVNR02.DAT`
und `IMSVNR05.DAT` als Regelreferenzen enthalten. Die Coverage-Matrix fuehrt die
ganze Familie bereits unter `policyholder_rule`; `IMSVNR03.DAT`,
`IMSVNR04.DAT` und `IMSVNR06.DAT` bleiben dort bewusst als fehlende historische
Quellen sichtbar.

`IMSVNR01.DAT` und `IMSVNR02.DAT` wurden aus dem lokalen Kandidatenpfad
`incomming/ZINS000/` uebernommen. Beide Dateien sind mit dem vorhandenen
VN-Parser lesbar, haben den erwarteten Header, 300 Datenzeilen und den
Periodenbereich `1-300`.

| Datei | Zeilen | Perioden | SHA-256 |
| --- | ---: | --- | --- |
| `IMSVNR01.DAT` | 300 | `1-300` | `79cff0463c0bd9489459fd92694e4650b59c0a52c0703d879e5142aeaea4b9c9` |
| `IMSVNR02.DAT` | 300 | `1-300` | `695ca328675b1eb46bcb6e15c0e8c41ce78a48c98ac5216c7644423ced5a4eec` |

Weitere lokale Kandidaten unter `incomming/` duerfen erst in separaten, kleinen
Schritten nach `tests/references/legacy_agrsich/` uebernommen werden. Dabei muss
jede Datei einzeln mit Quelle, Periodenbereich, Header und mindestens einer
Alignment-Zeile dokumentiert werden.

## Grenzen

- keine historische Vollgleichheitsbehauptung;
- keine neue VN-Regelentscheidung;
- kein Import weiterer nicht versionierter Rohdaten in diesem Schritt;
- keine Umdeutung von Writer-Referenzen als historische Baseline.
