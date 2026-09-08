# PR122: Materialisierte VU-Snapshots in der Workbench anzeigen

Stand: 2026-09-08

## Ziel

PR122 macht die in PR121 atomar erzeugten VU-Snapshots in der Workbench
verstaendlich sichtbar. Ein eigener achter Strategie-Tab `VU-Snapshots`
verbindet den bereits geprueften Entwurf und Einperiodenkontext mit einem
explizit erfassten PR120-Zustandsbeleg.

Die Ansicht zeigt vorbereitete Eingaben fuer VU-Regeln. Sie zeigt weder
berechnete Praemien, Werbung oder Reserven noch ein Simulationsergebnis.

## Historische und technische Grundlage

- `IMS.E`, `act Vrvu01` bis `act Vrvu10`: historische VU-Regelfamilie;
- PR110 und PR111: Bauplaene der vorhandenen VU-Snapshottypen;
- PR112 und PR113: lokaler Einperiodenkontext;
- PR118 und PR119: VU-Bestand, Eingabeform und gesperrte Fallbacks;
- PR120: getrennter Zustands- und Herkunftsbeleg;
- PR121: atomare In-Memory-Materialisierung aller VU-Eintraege.

## Bedienpfad

1. Strategieentwurf erfassen, pruefen und in Bauplaene uebersetzen.
2. Einperiodenkontext erfassen und formal pruefen.
3. In den Tab `VU-Snapshots` wechseln.
4. Den getrennten VU-Zustandsbeleg lokal anlegen.
5. Gemeinsamen Zinssatz, Schockstatus und aktive VN-Zahl eingeben.
6. Fuer `Vrvu03` bis `Vrvu05` die regelabhaengigen Anspruchsprofile und fuer
   `Vrvu04` zusaetzlich den Bestand `t-2` eingeben.
7. `VU-Snapshots anzeigen` ausdruecklich ausloesen.

Jede Aenderung am Entwurf, Kontext oder Zustandsbeleg verwirft eine bereits
erzeugte VU-Vorschau. Der Browser behaelt keine Daten dauerhaft.

## Lesbare Darstellung

Die Snapshotwerte werden je VU und Strategie in vier Gruppen angezeigt:

- Strategieparameter;
- Ziehungen;
- Schwellen und Markt;
- Periode.

Die Ansicht nennt Snapshottyp, Zielsammlung und gegebenenfalls die
Foreign-Info-Regelart. Sie zeigt ausserdem getrennt, ob der Herkunftsabgleich
vollstaendig war, Kontextwerte verwendet und Zustandswerte nur geprueft
wurden. Die nicht belegte Herkunft der Ziehungen aus einem Draw-Plan bleibt
sichtbar.

## Schutzgrenzen

- keine Aenderung oder Ausfuehrung der VU-Fachlogik;
- keine Ableitung des Zustandsbelegs aus den zu pruefenden Kontextwerten;
- keine Speicherung oder Browser-Persistenz;
- keine Run-Control-, Runner- oder Simulationskopplung;
- keine Teilergebnisse bei einem Eingabe-, Herkunfts- oder Loaderfehler;
- keine historische RNG- oder Vollgleichheitsbehauptung.

## Validierung

- Frontend-Build;
- Shell- und Dokumentationstests fuer Vertragsanbindung, Bedienpfad und
  Schutzgrenzen;
- bestehende PR120-/PR121-API- und Materialisierungstests;
- Gesamtregression und Windows-Release-Gate ohne Simulationsstart;
- visuelle Pruefung auf breitem und schmalem Viewport.

## Anschlussplanung

PR123 soll ausschliesslich den kontrollierten Ausfuehrungsanschluss fuer die
gemeinsamen VU- und VN-Snapshotlisten planen. Zustandsuebergang, atomarer
Abbruch, Persistenz, Freigabe und Beobachtbarkeit sind vor einer technischen
Runner-Anbindung getrennt zu entscheiden.
