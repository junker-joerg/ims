# Plan: Vrvu10 Free-Linear-Slice

## Ziel

Portiere die frei definierbare VU-Regel `Vrvu10` als groesseren, aber
reviewbaren Fachlogik-Slice. Der Schritt soll den bestehenden expliziten
Snapshot-Pfad erweitern, ohne Scheduler, Vollsimulation oder historische
Parameterherleitung einzufuehren.

## Vorgehen

1. Historischen `Vrvu10`-Block in `IMS.E` auf die lineare Kernformel abbilden.
2. Dataclasses, Loader und Apply-Funktionen in `vu_rules.py` ergaenzen.
3. `vu_rule_runner.py` um `vu_free_linear_rule_snapshots` erweitern und in die
   bestehende Zielkonfliktvalidierung aufnehmen.
4. Loader-, Regel-, Runner- und Importtests ergaenzen.
5. Migrationsdokument `vu_free_linear_rule.md` mit Ursprung, Annahmen und Grenzen
   anlegen.

## Grenzen

- Keine freie Formel-Auswertung zur Laufzeit.
- Keine automatische historische Regelauswahl.
- Keine Aussage historischer Vollgleichheit.
