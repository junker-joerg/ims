# PR119: VU-Materialisierungseingang validieren

## Ziel

PR119 baut auf der read-only Bestandsaufnahme aus PR118 einen eigenen,
versionierten VU-Eingabe- und Validierungsvertrag. Er prueft die vorhandenen
PR108-Entwuerfe und PR112-Einperiodenkontexte fuer alle zehn katalogisierten
VU-Strategien, erzeugt aber noch keinen Snapshot.

## Quellenentscheidungen

- `reserve_thresholds` bezeichnet fuer den Ziel-VU die historischen Werte
  `A1[1]` und `A2[1]`, heute Position 0 der beiden Anspruchsprofile;
- `net_switcher_thresholds` bezeichnet `A1[2]` und `A2[2]`, heute Position 1;
- `market_share_thresholds` bezeichnet `A1[3]` und `A2[3]`, heute Position 2;
- `random_draws` und `normal_draws` werden als vier explizite Werte im
  Einperiodenkontext geliefert;
- technische Loader- und Runner-Fallbacks sind in diesem Eingang nicht
  zulaessig.

Die Eingabe deklariert diese drei Richtlinien mit festen Policy-IDs. Da sie
noch keinen vollstaendigen VU-Zustand enthaelt, kann PR119 die Schwellenwerte
nicht gegen ein konkretes Anspruchsprofil abgleichen. Diese Herkunftspruefung
bleibt ausdruecklich offen.

## Validierung

1. VU-spezifische Schema- und Policy-Versionen exakt pruefen.
2. Den unveraenderten PR112-Kontext atomar validieren.
3. Ausschliesslich die enthaltenen VU-Eintraege gegen PR118 pruefen.
4. Alle offenen VU-Snapshotfelder explizit und nicht `null` verlangen.
5. Gleichverteilungsziehungen in `[0.0, 1.0)` und Normalziehungen als vier
   endliche Zahlen pruefen.
6. Aktive VN-Zahl und VU-Bestaende als nicht negative Werte pruefen.
7. Nur bei fehlerfreiem Gesamteingang `valid = true` melden.

## Schutzgrenzen

- keine Aenderung der vorhandenen Snapshotloader oder Regelkerne;
- kein Abgleich mit einem geladenen VU-Zustand;
- kein Loader-Aufruf, keine Snapshot-Erzeugung und keine Teilresultate;
- keine Speicherung, Runner-Kopplung oder Simulation;
- keine historische RNG- oder Vollgleichheitsbehauptung.

## Nachweis

- positiver Validierungstest fuer jede der zehn VU-Strategien;
- negative Tests fuer Policy-Drift, `null`-Fallbacks, Ziehungsgrenzen und
  negative Bestandswerte;
- Test, dass kein Snapshotloader aufgerufen wird;
- GET-Vertrag und POST-Validierung mit klarer HTTP-Methodengrenze;
- Migrationsnotiz und aktualisierte Dokuindizes.

## Naechster Schritt

Ein Folge-PR kann die fachliche Herkunft der Schwellen und Vorperiodenwerte
gegen einen expliziten VU-Zustand pruefbar machen oder, nach dieser
Entscheidung, gueltige PR119-Eingaenge atomar in die vorhandenen
VU-Snapshottypen materialisieren. Beides bleibt in PR119 gesperrt.
