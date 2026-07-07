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

Im versionierten Referenzbestand ist derzeit `IMSVNR05.DAT` als erstes
Regelfenster enthalten. Die Coverage-Matrix fuehrt die ganze Familie bereits
unter `policyholder_rule`; nicht vorhandene Referenzen bleiben dort bewusst als
fehlende historische Quellen sichtbar.

Lokale Kandidaten unter `incomming/` duerfen erst in separaten, kleinen Schritten
nach `tests/references/legacy_agrsich/` uebernommen werden. Dabei muss jede
Datei einzeln mit Quelle, Periodenbereich, Header und mindestens einer
Alignment-Zeile dokumentiert werden.

## Grenzen

- keine historische Vollgleichheitsbehauptung;
- keine neue VN-Regelentscheidung;
- kein Import nicht versionierter Rohdaten in diesem Schritt;
- keine Umdeutung von Writer-Referenzen als historische Baseline.
