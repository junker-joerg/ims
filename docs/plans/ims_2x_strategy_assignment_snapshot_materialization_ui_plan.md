# PR117: Materialisierte VN-Snapshots in der Workbench anzeigen

Stand: 2026-09-07

## Ziel

PR117 macht die in PR116 atomar erzeugten `VNInsuranceRuleSnapshot`-Objekte
als siebten Strategie-Tab `VN-Snapshots` verstaendlich sichtbar. Die
Vorschau entsteht nur nach einer ausdruecklichen Aktion auf einem formal
gueltigen lokalen Entwurf und Kontext.

Der Schritt fuegt keinen Speicher-, Runner- oder Simulationspfad hinzu.

## Historische und technische Grundlage

- `IMS.E`, `act Vrvn01` bis `act Vrvn06`: historische VN-Regelfamilie;
- PR110 und PR111: Zuordnung und Workbench-Vorschau der Snapshot-Bauplaene;
- PR112 und PR113: expliziter Einperiodenkontext und lokaler Editor;
- PR114 und PR115: verschachtelte VN-Wertformen und strenge Eingangspruefung;
- PR116: atomare In-Memory-Materialisierung mit den vorhandenen
  Snapshot-Loadern.

## Bedienpfad

1. Einen Strategieentwurf lokal erfassen und pruefen.
2. Seine Snapshot-Bauplaene anzeigen.
3. Eine Periode und die offenen Kontextwerte erfassen und formal pruefen.
4. `VN-Snapshots anzeigen` ausdruecklich ausloesen.
5. Nur bei vollstaendigem PR116-Erfolg in den Tab `VN-Snapshots` wechseln.
6. Dort jeden VN nach Strategie und Regelart aufklappen.

Bei einem strengeren PR115-Fehler bleibt der Anwender im Kontext und erhaelt
die zugehoerigen Pfade und Meldungen. Eine Aenderung am Entwurf oder Kontext
verwirft eine vorhandene Vorschau sofort.

## Lesbare Gliederung

Die Workbench zeigt kein unkommentiertes Gesamt-JSON. Sie gruppiert die fuer
die gewaehlte Periode konsumierten oder bedingt relevanten Werte in:

- Strategieparameter;
- Ziehungen und Auswahl;
- Markt und Historie;
- Schock und Kosten.

Periode 1 zeigt ausschliesslich `initial_decisions`. Ab Periode 2 richtet sich
die sichtbare Feldmenge nach der in PR114 bis PR116 belegten VN-Regelart.
Neutrale Dataclass-Werte nicht konsumierter Felder werden dadurch nicht als
fachlich gelieferte Eingaben dargestellt.

## Geschlossene Grenzen

- keine Aenderung der historischen oder portierten VN-Fachlogik;
- keine vorbelegten Beispielwerte und keine Zufallsziehung;
- keine Bearbeitung eines bereits materialisierten Snapshots;
- keine Speicherung, kein Browser-Persistenzspeicher und kein Download;
- keine Run-Control-, Runner- oder Simulationskopplung;
- kein Aufruf von `apply_vn_insurance_rule_snapshot`;
- keine historische RNG- oder Vollgleichheitsbehauptung.

## Validierung

- Frontend-Build und vorhandene Frontend-Shell-Tests;
- Dokumentationstest fuer Bedienpfad, Periodengrenze und Sperren;
- bestehende PR116-API- und Materialisierungstests;
- Gesamtregression und Windows-Release-Gate ohne Simulation;
- visuelle Pruefung der Workbench auf Desktop und schmalem Viewport.

## Anschlussplanung

PR118 sollte vor jeder Laufkopplung die VU-Seite separat klaeren: vorhandene
VU-Bauplaene, benoetigte Einperiodenwerte und die atomare
Materialisierungsgrenze werden zuerst als kleiner read-only Vertrag
inventarisiert. Speicherung und Ausfuehrung bleiben auch dort gesperrt.
