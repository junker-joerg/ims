# Plan: Vrvu04-Vorperiodenbasis fuer Nettowechsler

## Ziel

Der Vrvu04-/Mark-Up-II-Pfad soll `Vn(t-2)` aus einem expliziten
Versicherer-Vorperiodenzustand lesen koennen. Dadurch muessen Vrvu04-Snapshots
die zweite Vorperiode nicht mehr zwingend selbst duplizieren.

## Ursprung im Altcode

- `IMS.E`, `act Vrvu04`
- historische Kernformel: Nettowechsler je Sparte als `Vn(t-1) - Vn(t-2)`

## Umsetzung

1. `Insurer` um `policyholders_prev` und `policyholders_prev_sector` erweitern.
2. Szenario-Loader liest diese Felder mit zweispartigem Fallback.
3. Vrvu04-Snapshots akzeptieren `previous_policyholders_sector` weiter
   explizit, koennen es aber weglassen.
4. Fehlt der Snapshot-Wert, nutzt der Snapshot-Anwender den Versicherer-
   Vorperiodenzustand.
5. VU-Carryover erhaelt die Vorperiodenbasis fuer Folgeperioden.

## Grenzen

- keine historische VU-Regelauswahl
- kein Scheduler-Anschluss
- keine neue RNG-Logik
- keine Vollsimulation und keine Behauptung historischer Vollgleichheit
