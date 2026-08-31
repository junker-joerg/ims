# Historischer Horizontvertrag 100/300/500

Stand: 2026-08-31
Vertrag: `pr92-v1`

## Ziel und Herkunft

Der read-only Vertrag `ims.api.historical_horizon_contract` friert die
Pflichtgrenzen 100, 300 und 500 fuer die 15 berechneten Kernexporte ein. Er
leitet die Exportidentitaeten und Periodenmengen aus dem versionierten
`legacy_validation_bundle.json` ab und bindet jedes Referenzfenster an seine
in `pr91-v1` festgelegte `layer_id`.

Der Vertrag berechnet keine Exporttabelle. Er startet weder Runner noch
Simulation und aendert weder das Legacy-Bundle noch historische Referenzen.
`incomming/` wird nicht gelesen oder versioniert.

## Eingefrorene Matrix

| Pflichtgrenze | Exporte | Tabellen | Zielperioden | Prefix-Pruefpunkte |
| --- | --- | ---: | ---: | --- |
| 100 | `imsvu014.dat`, `imsvnsk1.dat` | 2 | 200 | keine |
| 300 | `imsvnr01.dat`, `imsvnr02.dat` | 2 | 600 | 100 |
| 500 | `imsvusk1.dat`, `imsvnr03.dat` bis `imsvnr06.dat`, `imsvnvk1.dat` bis `imsvnvk3.dat`, `imsvuvk1.dat` bis `imsvuvk3.dat` | 11 | 5.500 | 100 und 300 |
| Gesamt | 15 Exportidentitaeten / 19 Referenzziele | 15 | 6.300 | - |

Die Pflichtgrenze kommt aus der belegten Zielmenge des Bundles. Daher bleibt
`imsvnsk1.dat` in diesem Vertrag ein 100-Perioden-Ziel, obwohl die physische
Referenzdatei weitere Zeilen enthaelt. Nicht eingetragene Perioden werden
nicht still in den Vergleich aufgenommen.

## Prefix-Vertrag

Der generische Prefix-Pruefer akzeptiert ausschliesslich bereits berechnete
`ExportTable`-Snapshots. Fuer jeden Snapshot werden geprueft:

- Exportidentitaet aus Subjekttyp, Aggregatstufe und Selektor;
- exakte, bis zum jeweiligen Horizont beruehrte `layer_id`-Folge aus
  `pr91-v1`;
- Header passend zu VU oder VN;
- lueckenlose Periodenfolge von 1 bis zur Snapshot-Grenze;
- Vorhandensein aller kleineren Pflicht-Pruefpunkte;
- exakte Gleichheit aller Zeilen im gemeinsamen Prefix ohne Toleranz.

Ein 300er-Snapshot muss daher mit seinem 100er-Snapshot uebereinstimmen. Ein
500er-Snapshot muss sowohl den 100er- als auch den 300er-Snapshot exakt als
Prefix enthalten. PR92 stellt diesen Pruefer bereit, fuehrt aber noch keinen
300-/500-Periodenlauf und keinen Vollfenstervergleich aus.

## VUSK1-Grenze

`imsvusk1.dat` bleibt eine Exportidentitaet auf Aggregatstufe IV mit
`selector_kind = all` und `selector_value = SK1`. Die fuenf Dateien
`VUSK1L5.DAT` bis `VUSK1L1.DAT` sind ihre aufeinanderfolgenden
100-Perioden-Zeitfenster 1-100 bis 401-500, keine unterschiedlichen Aggregate
oder Aggregatebenen.

Die Herkunftsschichten bleiben trotzdem getrennt:

- `VUSK1L5`, `VUSK1L3`, `VUSK1L2` und `VUSK1L1` tragen
  `wvemod2_archive` mit `archive_content_match_only`;
- `VUSK1L4` traegt die isolierte Schicht `vusk1l4_direct_04410ef` mit
  `versioned_fixture_regression_only`.

Der 500er-Horizont verbindet diese Fenster nur technisch mit derselben
berechneten Exportidentitaet. Er belegt weder eine gemeinsame historische
Archivquelle noch einen gemeinsamen historischen Lauf.

Fuer `imsvusk1.dat` traegt der 100er-Snapshot deshalb nur
`wvemod2_archive`. Ab dem 300er-Snapshot werden `wvemod2_archive` und
`vusk1l4_direct_04410ef` gemeinsam, aber weiterhin als getrennte Schichten,
ausgewiesen.

## Aussagegrenzen

Der Status `ready` bedeutet ausschliesslich, dass Zielmenge, Horizonte,
Referenzschichten und Prefix-Regeln widerspruchsfrei gebunden sind. Er bedeutet
nicht, dass berechnete Tabellen vorliegen oder historische Werte treffen.

Insbesondere behauptet PR92 keine neue Fachlogik, keine Seed- oder
Laufidentitaet, keine historische Vollgleichheit und keine fachliche
Produktionsfreigabe. Der bestehende Befund `keep_blocked` bleibt unberuehrt.

## Reproduzierbarer Aufruf

```powershell
$env:PYTHONPATH = "python_port"
python -m ims.api.historical_horizon_contract --root .
```

Der Aufruf liest nur versionierte Vertrage und Referenzen. Die Prefix-Pruefung
wird separat von Tests mit vorberechneten oder synthetischen Tabellen
aufgerufen.

## Naechster Schritt

PR93 hat `imsvu014.dat` und `imsvnsk1.dat` als die zwei vollstaendigen
100-Perioden-Ziele streng an den Produktionskorpusbericht gebunden. Der
Fortschritt betraegt 2/15 Tabellen und 200/6.300 Perioden; die Freigabe bleibt
blockiert. PR94 hat den kontrollierten Zustand bis 300 erweitert und den
Prefix 1-100 fuer alle 15 Tabellen exakt stabil gehalten. PR95 hat
`imsvnr01.dat` und `imsvnr02.dat` als getrennte 300er-Regelfenster
vollstaendig verglichen. PR96 hat den kontrollierten Zustand bis 500 erweitert
und beide Prefixgrenzen 100 und 300 exakt stabil gehalten. PR97 hat die
VU-SK1-Zeitfenster getrennt angebunden. PR98 bindet als Naechstes die vier
VN-Regeltabellen 3-6 an.
