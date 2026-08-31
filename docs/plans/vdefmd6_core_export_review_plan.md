# Plan: Gemeinsame Vdefmd6-Kernexportbewertung fuer PR 86

## Ziel

PR 86 fuehrt alle 15 Kernexportidentitaeten aus demselben kontrollierten
`Vdefmd6`-Zustand gemeinsam durch den vorhandenen berechneten
Legacy-Abweichungsbericht. Der gemeinsame Vergleich bleibt auf das von diesem
Zustand vollstaendig erzeugte Fenster 1-100 begrenzt und bereitet eine
konservative menschliche Freigabebewertung vor.

## Gemeinsamer Umfang

| Familie | Exporte | Zeilen |
| --- | ---: | ---: |
| VU14 | 1 | 100 |
| VU SK1/all und Klassen | 4 | 400 |
| VN-Regeln | 6 | 600 |
| VN SK1/all und Klassen | 4 | 400 |
| Gesamt | 15 | 1.500 |

`VUSK1L5.DAT` bleibt dabei das Referenzfenster 1-100 desselben
SK1-/all-Aggregats. `VUSK1L1.DAT` bis `VUSK1L4.DAT` sind dessen spaetere
Zeitfenster und keine weiteren Aggregatebenen.

## Umsetzung

1. Ein eigenes Bundle beschreibt genau die 15 Identitaeten und Perioden
   1-100.
2. Der bestehende kontrollierte Runner wird genau einmal mit dem modernen
   Seed `20260001` ausgefuehrt.
3. Seine 15 In-Memory-Tabellen werden ohne Dateischreiben an
   `build_calculated_legacy_deviation_report` uebergeben.
4. Der PR-86-Bericht fasst Strukturfelder, Fachwerte, volle Zielzeilen und
   Abweichungsklassen zusammen.
5. Ein eingefrorener Vertrag prueft Zielmenge, Gesamtwerte, Quellanker,
   Blocker und Freigabegrenzen.

## Freigabegrenzen

Die technische Demo- und Pruefkette ist bereits gruen. Eine historische oder
fachliche Produktionsfreigabe folgt daraus nicht. PR 86 empfiehlt weiterhin
`keep_blocked`, solange mindestens folgende Punkte offen sind:

- die konkrete historische Laufidentitaet und die Koharenz aller
  Referenzfamilien;
- historische Same-Slot-Reihenfolge und RNG-Ziehfolge;
- die Ableitung des historischen Versicherungsgrads;
- VU-Klassen-, VN-Regel- und VN-Klassenakkumulatorsemantik;
- die historische Initialisierung des VN-SK1-/all-Aggregats;
- die Bedeutung der VN-Felder `Ev1` und `Ev2`;
- die noch nicht erzeugten Pflichtfenster 101-300 beziehungsweise 101-500.

## Grenzen

- keine Legacy-Zeile als Erzeugungsinput;
- keine Exportdatei geschrieben;
- kein historischer Scheduler und keine allgemeine Simulation gestartet;
- keine automatische historische Regelwahl neu eingefuehrt;
- keine historische RNG-, Same-Slot- oder Vollgleichheitsbehauptung;
- keine Gleichsetzung von 1.500 kontrollierten Zielzeilen mit dem
  6.300-Zeilen-Produktionskorpus;
- keine automatische Produktionsfreigabe.

## Abschluss und Folgephase

PR 86 schliesst die geplante Mindestserie PR 72 bis PR 86 ab. PR 87 hat den
Folgeblock inzwischen in PR 88 bis PR 102 geschnitten: zuerst vier
Provenienz- und Referenzschicht-PRs, danach die kontrollierten Pflichtfenster
100, 300 und 500 sowie ein gemeinsamer 6.300-Zeilen-Abschlussbericht. Der Plan
steht in `docs/plans/historical_reference_provenance_and_full_window_plan.md`.
