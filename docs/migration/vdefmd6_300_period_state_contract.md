# Kontrollierter Vdefmd6-Zustandsvertrag bis Periode 300

> Einordnung ab PR98: Dies ist ausschliesslich ein moderner deterministischer
> Langzeit- und Prefix-Stresstest. Historisches IMS war auf 100 Perioden je
> Lauf begrenzt. Historische Dateien mit 300 Ergebniszeilen enthalten drei
> getrennte 100-Perioden-Laeufe und werden nicht als ein historischer
> 300-Perioden-Lauf bewertet.

Stand: 2026-08-31
Vertrag: `pr94-v1`

## Ziel

PR94 erweitert den bereits kontrollierten modernen Vdefmd6-Zustand aus
`pr81-v1` und `pr86-v1` deterministisch bis Periode 300. Der neue Einstieg
`run_vdefmd6_300_periods` erzeugt alle 15 Kernexporttabellen fuer die Perioden
1-300 im Speicher. Der Bericht
`ims.api.vdefmd6_300_period_state_report` prueft dabei insbesondere, dass der
bereits abgenommene Prefix 1-100 exakt unveraendert bleibt.

Dies ist eine Zustands- und Erzeugungsgrenze. PR94 uebergibt noch keine neue
Tabelle an den Produktionskorpusbericht und startet keinen historischen
300-Perioden-Vergleich.

## Historischer Ursprung und Grenze

Der bekannte historische Anker `Vdefmd6` ruft `Bavauin(50,0,0.8,0.02,1)`
auf. Damit beginnt das bereits portierte Schockregime in Periode 50. Fuer die
Perioden nach 100 fuehrt PR94 ausschliesslich dieselbe moderne Reihenfolge
weiter:

1. Subjekte aktivieren;
2. BAV-Fremdinformation anwenden;
3. VU-Regeln nach ID anwenden;
4. VN-Regeln nach ID anwenden;
5. Aggregate im Speicher materialisieren.

Der einzige direkte historische Laufbericht aus `VDEFMD5A.ZIP` protokolliert
zwar 300 `Frmdinf`-/`Agrsich`-Paare, aber als drei getrennte Sequenzen 1-100
mit zwei Ruecksetzungen. Er belegt keine historische 300-Perioden-
Laufidentitaet. Die Referenzschichten aus `pr91-v1` bleiben getrennt.

## Umsetzung

- `build_vdefmd6_population()` bleibt unveraendert auf dem 100er-Standard;
- `build_vdefmd6_population_for_horizon(max_periods=300)` verlaengert nur die
  explizite moderne Laufgrenze `active_through_run`;
- die VU- und VN-Schock-Snapshot-Builder pruefen gegen den Horizont der
  uebergebenen Population;
- `run_vdefmd6_300_periods` verwendet den festen Basis-Seed `20260001`, die
  bestehende Ausfuehrungsreihenfolge und die eigene Policy
  `vdefmd6-modern-300-period-state-v1`;
- alle Exportkontexte tragen denselben Horizont 300 und `run_index = 0`;
- der 49-/100-Perioden-Pfad behaelt Horizont, Policy und Ergebnisse.

## Kontrollierter Befund

| Kennzahl | Wert |
| --- | ---: |
| Zustandsuebergaenge 2-300 | 299 |
| Kernexporttabellen | 15 |
| erzeugte Exportzeilen | 4.500 |
| VU-Regelanwendungen | 7.475 |
| VN-Regelanwendungen | 57.400 |
| Schaden-/Settlement-Anwendungen | 57.400 |
| Uniform-Zufallswerte | 383.742 |
| Normal-Zufallswerte | 231.992 |
| Informationskosten | 497.712,0 |
| VN mit Informationskosten, aufsummiert | 17.940 |

Eine deterministische Wiederholung mit demselben Seed liefert dasselbe
`Vdefmd6PreShockRunResult`.

## Prefix-Abnahme

Der Bericht vergleicht den separaten 100er-Lauf mit dem 300er-Lauf exakt:

- alle 99 Zustandsresultate fuer Perioden 2-100 sind gleich;
- alle 15 Exportidentitaeten sind in beiden Laeufen eindeutig vorhanden;
- Spezifikation und Header jeder Tabelle sind gleich;
- alle 1.500 Exportzeilen fuer Perioden 1-100 sind wertgleich;
- jede erweiterte Tabelle enthaelt lueckenlos die Perioden 1-300.

Eine geaenderte Policy, Zielmenge, Periodengrenze oder Prefix-Zeile setzt den
Bericht auf `error`.

## Grenzen

- keine neue Fachlogik oder historische Regelwahl;
- keine Legacy-Zeile als Erzeugungsinput;
- keine Datei- oder Datenbankschreibvorgaenge;
- kein Schedulerstart und keine Simulation;
- kein historischer 300-Perioden-Vergleich;
- keine historische Scheduler- oder RNG-Gleichheit;
- keine historische 300-Perioden-Laufidentitaet;
- keine historische Vollgleichheitsbehauptung;
- keine Produktionsfreigabe.

## Reproduzierbarer Aufruf

```powershell
$env:PYTHONPATH = "python_port"
python -m ims.api.vdefmd6_300_period_state_report --repo-root .
```

Der Aufruf erzeugt die Tabellen nur im Speicher.

## Naechster Schritt

PR95 hat ausschliesslich `imsvnr01.dat` und `imsvnr02.dat` als die beiden im
Horizontvertrag belegten 300er-Regelfenster vollstaendig verglichen und an den
weiterhin gesperrten Korpusbericht gebunden. PR96 hat denselben kontrollierten
Zustand bis 500 erweitert und die Prefixe 1-100 und 1-300 exakt stabil
gehalten. PR98 hat die historische Wiederholungslesart korrigiert. PR99 hat
die vier VN-Regeltabellen 3-6 angebunden. PR100 bindet als Naechstes die drei
VN-Klassenaggregate an.
