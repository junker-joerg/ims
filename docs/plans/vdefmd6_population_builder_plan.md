# Plan: Vdefmd6-Populationsbuilder fuer PR 74

## Ziel

Die in `IMS.E` belegte Ausgangspopulation des vordefinierten Modells 6 wird
als typisierte, deterministische Python-Struktur aufgebaut. Der Schnitt umfasst
25 Versicherer und 200 Versicherungsnehmer, aber noch keine Aktionsausfuehrung.

## Quellen

- `IMS.E:4137-4184`: Abbildung von `Vuauini`;
- `IMS.E:4191-4233`: Abbildung von `Vnauini`;
- `IMS.E:4566-4669`: konkrete `Vdefmd6`-Gruppen;
- `IMSDATA.C:14-16`: Perioden- und Populationsgrenzen;
- `IMSDATA.C:77-78`: Zuordnung von Regeln zu Regelklassen.

Die ausfuehrbaren VN-Schleifen `151-190` und `191-200` sind massgeblich. Der
abweichende, erst danach ausgegebene Bildschirmtext `151-180` und `181-200`
wird dokumentiert, aber nicht als Initialisierungsquelle verwendet.

## Umsetzung

1. VU- und VN-Initialisierungsdefinitionen mit Aktivierung, Aktionszeit,
   Startwerten, Anspruchsniveaus und 16er-Parametervektoren typisieren.
2. Daraus die vorhandenen `Insurer`- und `Policyholder`-Entitaeten fuer
   Periode 1 erzeugen.
3. Vollstaendigkeit, Gruppenverteilung, Grenzwerte und Herkunft durch einen
   read-only Bericht und Tests absichern.
4. Die bestehende VU14-Perioden-1-Pruefung an den Builder anschliessen.

## Grenzen

- keine Simulation und kein Runnerstart;
- keine Regel-, Scheduler-, RNG- oder Schadenberechnung;
- keine Rekonstruktion des historischen Seeds;
- keine Legacy-Ausgabezeile als Erzeugungsinput;
- keine historische Vollgleichheitsbehauptung.
