# Kontrollierter Vdefmd6-Zustandsvertrag bis Periode 500

> Einordnung ab PR98: Dies ist ausschliesslich ein moderner deterministischer
> Langzeit- und Prefix-Stresstest. Historisches IMS war auf 100 Perioden je
> Lauf begrenzt. Historische Dateien mit 500 Ergebniszeilen enthalten fuenf
> getrennte 100-Perioden-Laeufe und werden nicht als ein historischer
> 500-Perioden-Lauf bewertet.

Stand: 2026-08-31
Vertrag: `pr96-v1`

## Ziel

PR96 erweitert den kontrollierten modernen Vdefmd6-Zustand aus `pr94-v1`
deterministisch bis Periode 500. Der Einstieg `run_vdefmd6_500_periods`
erzeugt alle 15 Kernexporttabellen fuer die Perioden 1-500 ausschliesslich im
Speicher. Der Bericht `ims.api.vdefmd6_500_period_state_report` vergleicht
diesen Lauf mit getrennt erzeugten 100er- und 300er-Laeufen.

Dies ist weiterhin nur eine Zustands- und Erzeugungsgrenze. PR96 bindet keine
historische 500er-Referenz an und aendert die Korpuslieferung von 4/15 Tabellen
und 800/6.300 Zielperioden nicht.

## Historischer Ursprung und Grenze

Der bekannte historische Anker `Vdefmd6` und die bereits portierte
Schockgrenze ab Periode 50 bleiben unveraendert. PR96 setzt ausschliesslich die
in `pr94-v1` dokumentierte moderne Reihenfolge fort:

1. Subjekte aktivieren;
2. BAV-Fremdinformation anwenden;
3. VU-Regeln nach ID anwenden;
4. VN-Regeln nach ID anwenden;
5. Aggregate im Speicher materialisieren.

Die historischen 500er-Ziele stammen gemaess `pr91-v1` aus getrennten
Referenzschichten. Insbesondere sind `VUSK1L1.DAT` bis `VUSK1L5.DAT`
Zeitfenster desselben SK1/all-Aggregats auf Stufe IV. PR96 leitet daraus weder
einen zusammengehoerigen historischen Lauf noch historische Scheduler-, RNG-
oder Akkumulatorsemantik ab.

## Umsetzung

- `build_vdefmd6_population_for_horizon(max_periods=500)` verlaengert nur die
  explizite moderne Laufgrenze `active_through_run`;
- die vorhandenen VU- und VN-Snapshot-Builder pruefen weiterhin gegen den
  Horizont der uebergebenen Population;
- `run_vdefmd6_500_periods` verwendet den festen Basis-Seed `20260001`, die
  vorhandene Ausfuehrungsreihenfolge und die eigene Policy
  `vdefmd6-modern-500-period-state-v1`;
- alle 15 Tabellen tragen lueckenlos die Perioden 1-500;
- die 100er- und 300er-Einstiege, Policies und Ergebnisse bleiben
  unveraendert.

## Kontrollierter Befund

| Kennzahl | Wert |
| --- | ---: |
| Zustandsuebergaenge 2-500 | 499 |
| Kernexporttabellen | 15 |
| erzeugte Exportzeilen | 7.500 |
| VU-Regelanwendungen | 12.475 |
| VN-Regelanwendungen | 97.400 |
| Schaden-/Settlement-Anwendungen | 97.400 |
| Uniform-Zufallswerte | 651.342 |
| Normal-Zufallswerte | 393.592 |
| Informationskosten | 833.712,0 |
| VN mit Informationskosten, aufsummiert | 29.940 |

Eine deterministische Wiederholung mit demselben Seed liefert dasselbe
`Vdefmd6PreShockRunResult`.

## Doppelte Prefix-Abnahme

Der Bericht vergleicht drei getrennt erzeugte Zustandsfolgen:

- alle 99 Zustandsresultate fuer Perioden 2-100 bleiben im 500er-Lauf exakt
  gleich;
- alle 299 Zustandsresultate fuer Perioden 2-300 bleiben im 500er-Lauf exakt
  gleich;
- Spezifikation, Header und alle 1.500 Exportzeilen fuer Perioden 1-100 sind
  fuer jede der 15 Tabellen wertgleich;
- Spezifikation, Header und alle 4.500 Exportzeilen fuer Perioden 1-300 sind
  fuer jede der 15 Tabellen wertgleich;
- jede 500er-Tabelle enthaelt lueckenlos die Perioden 1-500.

Eine geaenderte Policy, Zielmenge, Periodengrenze oder Zeile innerhalb eines
Prefix setzt den Bericht auf `error`. Die beiden Prefixgrenzen werden getrennt
ausgewiesen.

## Grenzen

- keine neue Fachlogik oder historische Regelwahl;
- keine Legacy-Zeile als Erzeugungsinput;
- keine Datei- oder Datenbankschreibvorgaenge;
- kein Schedulerstart und keine Simulation;
- kein historischer 500-Perioden-Vergleich;
- keine historische Scheduler- oder RNG-Gleichheit;
- keine historische 500-Perioden-Laufidentitaet;
- keine historische Vollgleichheitsbehauptung;
- keine Produktionsfreigabe.

## Reproduzierbarer Aufruf

```powershell
$env:PYTHONPATH = "python_port"
python -m ims.api.vdefmd6_500_period_state_report --repo-root .
```

Der Aufruf materialisiert die kontrollierten Tabellen nur im Speicher.

## Naechster Schritt

PR97 hat die eine berechnete 500-Perioden-Tabelle `imsvusk1.dat` gegen die
fuenf getrennten Zeitfenster `VUSK1L5.DAT` bis `VUSK1L1.DAT` angebunden.
`VUSK1L4.DAT` behaelt dabei seine isolierte Referenzschicht; eine
zusammengehoerige historische 500er-Laufquelle wird nicht behauptet. PR98 hat
diese Interpretation korrigiert und auf fuenf getrennte 100er-Laeufe
umgestellt. PR99 bindet als Naechstes die vier VN-Regeltabellen 3-6 an.
