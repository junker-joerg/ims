# Plan: VU14-Quellenbindung fuer PR 73

## Anlass

Der PR-72-Vertrag verlangt belegte Population, Startwerte, Regelzuordnung,
Aktionszeit und RNG-Grenze vor einer 100-Perioden-Erzeugung. Die Quellpruefung
hat in `IMS.E`, `Vdefmd6`, die konkrete VU14-Konfiguration gefunden. Zugleich
war die versionierte `VU14L1.DAT` eine linear konstruierte Testreihe und nicht
identisch mit dem dreifach bestaetigten lokalen Altdatenkandidaten.

## Schnitt

1. die historische VU14-Reihe gezielt versionieren;
2. `Vdefmd6`, BAV, 25 VU, 200 VN und VU14/`Vrvu06` maschinenlesbar binden;
3. die ausfuehrbaren Populationsgrenzen bei widerspruechlichem Bildschirmtext
   konservativ verwenden und den Konflikt dokumentieren;
4. Periode 1 aus Startzustand, vorhandenem Regelkern, Aggregation und Export im
   Speicher erzeugen und erst danach vergleichen;
5. RNG-Seed und VN-/Schadenpfad fuer Perioden 2-100 offen lassen.

## Nicht-Ziele

- keine Simulation und kein Runnerstart;
- keine Ableitung des unbekannten historischen Seeds aus Ergebnisdaten;
- keine direkte Verwendung von Legacy-Zeilen als Erzeugungsinput;
- keine neue Fachformel;
- keine historische Vollgleichheitsbehauptung.

## Danach

PR 74 baut die belegte `Vdefmd6`-Population typisiert auf. Aktionsfolge,
reproduzierbare moderne Seed-Policy und Perioden 2-100 folgen in getrennten
Slices.
