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

Im versionierten Referenzbestand sind derzeit `IMSVNR01.DAT` bis
`IMSVNR06.DAT` als Regelreferenzen enthalten. Die Coverage-Matrix fuehrt die
ganze Familie unter `policyholder_rule` und zeigt fuer diese Familie keine
fehlende historische Quelle mehr.

`IMSVNR01.DAT` und `IMSVNR02.DAT` wurden aus dem lokalen Kandidatenpfad
`incomming/ZINS000/` uebernommen. Beide Dateien sind mit dem vorhandenen
VN-Parser lesbar, haben den erwarteten Header, 300 Datenzeilen und den
Periodenbereich `1-300`.

`IMSVNR03.DAT`, `IMSVNR04.DAT` und `IMSVNR06.DAT` wurden gezielt aus
`incomming/IMS.DAT/WVEMOD1.ZIP` uebernommen. Dieser ZIP-Kandidat wurde
konservativ gewaehlt, weil `IMSVNR05.DAT` aus demselben Archiv bytegleich zur
bereits versionierten Referenz `tests/references/legacy_agrsich/IMSVNR05.DAT`
ist. `IMSVNR05.DAT` wird im Bundle nun ebenfalls ueber das volle
`1-500`-Fenster der Archivfamilie validiert. Die Dateien sind mit dem
vorhandenen VN-Parser lesbar, haben den erwarteten Header, 500 Datenzeilen und
den Periodenbereich `1-500`.

| Datei | Zeilen | Perioden | SHA-256 |
| --- | ---: | --- | --- |
| `IMSVNR01.DAT` | 300 | `1-300` | `79cff0463c0bd9489459fd92694e4650b59c0a52c0703d879e5142aeaea4b9c9` |
| `IMSVNR02.DAT` | 300 | `1-300` | `695ca328675b1eb46bcb6e15c0e8c41ce78a48c98ac5216c7644423ced5a4eec` |
| `IMSVNR03.DAT` | 500 | `1-500` | `8491bec0736fbf4fb95c9b7649338d0142207265024ec5c5e9c3e649bd49ffd4` |
| `IMSVNR04.DAT` | 500 | `1-500` | `16bdf0b4329ec414990aaaec2ece0d48a8001b43d4a6bb8210625cfb56f3fce4` |
| `IMSVNR05.DAT` | 500 | `1-500` | `80a83f47de5451cb9b660025ca3c0e511aa268602b0ced2301f82b4467549dfa` |
| `IMSVNR06.DAT` | 500 | `1-500` | `1d18b3ce471f4b19f525956650b414e1fcfb8b93854eaaf60c8316b18b1eced0` |

Weitere lokale Kandidaten unter `incomming/` duerfen erst in separaten, kleinen
Schritten nach `tests/references/legacy_agrsich/` uebernommen werden. Dabei muss
jede Datei einzeln mit Quelle, Periodenbereich, Header und mindestens einer
Alignment-Zeile dokumentiert werden.

## Grenzen

- keine historische Vollgleichheitsbehauptung;
- keine neue VN-Regelentscheidung;
- kein Import weiterer nicht versionierter Rohdaten in diesem Schritt;
- keine Umdeutung von Writer-Referenzen als historische Baseline.

## Kontrollierter Erzeugungsstand

PR 83 erzeugt `imsvnr01.dat` bis `imsvnr03.dat` fuer Perioden 1-100 aus dem
kontrollierten modernen `Vdefmd6`-Zustand. Der Vergleich trifft 946/3.900
Felder, aber keine vollstaendige Zeile. Der historische, zwischen Regeln nicht
zurueckgesetzte Akkumulator und die Bedeutung der `Ev`-Spalten bleiben offene
fachliche Grenzen. Die Referenzen werden nicht als Erzeugungsinput verwendet.

PR 84 erzeugt auch `imsvnr04.dat` bis `imsvnr06.dat` fuer Perioden 1-100. Der
Vergleich trifft 926/3.900 Felder beziehungsweise 326/3.300 Fachwerte, aber
erneut keine vollstaendige Zeile. Fuer das Quellarchiv `WVEMOD1.ZIP` ist kein
zugeordneter Runreport mit Seed belegt. Ueber alle sechs Regeln treffen damit
1.872/7.800 Felder beziehungsweise 672/6.600 Fachwerte.

PR 85 soll als naechstes VN-Klassen und VN-SK1/all unter denselben Grenzen
vergleichen.
