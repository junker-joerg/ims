# Historische 300-Perioden-Regelfenster aus ZINS000

## Ziel

PR95 bindet `imsvnr01.dat` und `imsvnr02.dat` als die zwei im
Horizontvertrag `pr92-v1` belegten 300-Perioden-Ziele an den weiterhin
gesperrten Produktionskorpusbericht. Der neue read-only Bericht
`ims.api.historical_300_period_rule_delivery` vergleicht beide Tabellen
vollstaendig mit den versionierten historischen Referenzen.

Der kumulierte Lieferstand steigt damit auf **4/15 Tabellen und 800/6.300
Zielperioden**. Die restlichen elf Tabellen mit 5.500 Zielperioden fehlen
weiterhin.

## Historischer Ursprung

| Referenz | Export | Identitaet | Fenster | SHA-256 |
| --- | --- | --- | ---: | --- |
| `IMSVNR01.DAT` | `imsvnr01.dat` | VN / II / Regel 1 | 1-300 | `79cff0463c0bd9489459fd92694e4650b59c0a52c0703d879e5142aeaea4b9c9` |
| `IMSVNR02.DAT` | `imsvnr02.dat` | VN / II / Regel 2 | 1-300 | `695ca328675b1eb46bcb6e15c0e8c41ce78a48c98ac5216c7644423ced5a4eec` |

PR89 und PR91 binden beide Dateien bytegenau an `ZINS000.ZIP` und halten sie
in der getrennten Referenzschicht `zins000_archive`. Fuer dieses Archiv sind
keine Laufmetadaten, kein Seed und keine gemeinsame Laufidentitaet mit den
anderen Referenzschichten belegt. Der erlaubte Provenienzanspruch bleibt daher
`archive_content_match_only`.

## Kontrollierter Vergleich

Der moderne Zustand stammt aus `pr94-v1`:

- fester Seed `20260001`;
- Zustandspfad bis Periode 300;
- VN-Regeltabellen fuer Regel 1 und Regel 2 mit jeweils 300 Zeilen;
- keine historischen Zeilen als Erzeugungseingabe;
- keine Writer-, Scheduler- oder Simulationsausfuehrung.

Vor dem historischen Vergleich prueft PR95 fuer beide Ziele:

- kanonische Exportidentitaet;
- VN-Header und Zeilenbreite;
- lueckenlose Perioden 1-300;
- Referenzpfad und SHA-256;
- Bindung an `zins000_archive`;
- exakte Stabilitaet des kontrollierten Prefixes 1-100.

## Beobachteter Feldbefund

Der Vergleich wurde fuer alle 600 historischen Zeilen und alle 7.800
Feldvergleiche ausgefuehrt. **600 von 600 Zeilen** unterscheiden sich in
mindestens einem Feld.

| Export | exakt gleiche Felder | tolerierte numerische Unterschiede | blockierende numerische Unterschiede | offene Feldfragen |
| --- | ---: | ---: | ---: | ---: |
| `imsvnr01.dat` | 931 | 0 | 2.967 | 2 |
| `imsvnr02.dat` | 608 | 79 | 2.628 | 585 |
| **Gesamt** | **1.539** | **79** | **5.595** | **587** |

Die zwei Header- und Periodenfelder je Zeile sind Teil der Feldzaehlung. Die
Abweichungen betreffen die fachlichen VN-Ausgabefelder. Sie sind ein
reproduzierbarer Befund zwischen dem kontrollierten modernen Zustand und den
getrennten ZINS000-Referenzen, aber noch keine Erklaerung ihrer Ursache.

Insbesondere folgt daraus weder, dass der moderne Kern fachlich falsch ist,
noch dass die ZINS000-Dateien zu demselben historischen Lauf wie andere
Referenzen gehoeren. Scheduler-, RNG-, Akkumulator- und Zustandsprovenienz
bleiben offen und werden durch PR95 nicht ergaenzt.

## Produktionsgrenze

Der Produktionskorpusbericht akzeptiert nun vier strukturell vollstaendige
Tabellen. Er bleibt mit elf fehlenden Tabellen und 5.500 fehlenden Perioden auf
`blocked_calculated_core_validation`.

PR95 behauptet ausdruecklich:

- keine historische Laufidentitaet;
- keine historische RNG-Gleichheit;
- keine historische Vollgleichheit;
- keine Produktionsfreigabe.

## Reproduzierbarer Aufruf

```powershell
$env:PYTHONPATH = "python_port"
python -m ims.api.historical_300_period_rule_delivery --root .
```

Der Aufruf liest nur versionierte Referenzen und erzeugt kontrollierte Tabellen
im Speicher. Er schreibt keine Ergebnisdateien und startet keine Simulation.

## Naechster Schritt

PR96 hat denselben kontrollierten Zustand deterministisch bis Periode 500
erweitert und die Prefixe 1-100 sowie 1-300 exakt stabil gehalten. PR97 hat die
VU-SK1-Zeitfenster als getrennte historische Referenztests angebunden. PR98
bindet als Naechstes `IMSVNR03.DAT` bis `IMSVNR06.DAT` an.
