# PR120: VU-Zustands- und Herkunftsvertrag

## Ziel

PR120 ergaenzt den gueltigen PR119-Materialisierungseingang um einen
versionierten, expliziten Zustandsbeleg. Der neue Validator prueft, ob die
eingereichten VU-Kontextwerte aus demselben Perioden- und VU-Zustand stammen.
Er erzeugt weiterhin keinen Snapshot.

## Gepruefte Herkunft

- `interest_rate` und `change_shock` muessen bei jedem VU-Eintrag mit dem
  gemeinsamen Periodenzustand uebereinstimmen;
- `reserve_thresholds`, `net_switcher_thresholds` und
  `market_share_thresholds` muessen den Positionen 0, 1 und 2 der beiden
  VU-Anspruchsprofile entsprechen;
- `previous_policyholders_sector` von `Vrvu04` muss dem expliziten
  VU-Bestand `t-2` entsprechen;
- `active_policyholder_count` von `Vrvu05` muss der aktiven VN-Zahl des
  Periodenzustands entsprechen.

Der Zustandsbeleg enthaelt fuer andere VU-Regeln bewusst keinen ungenutzten
VU-Vollzustand. Die vier Ziehungen von `Vrvu01` und `Vrvu02` bleiben explizite
PR119-Kontextwerte; ihre Herkunft aus einem Draw-Plan oder Seed wird in PR120
nicht behauptet.

## Validierung

1. Den vollstaendigen PR119-Eingang zuerst atomar pruefen.
2. Version, Modell, Entwurf, Periode und Feldformen des Zustandsbelegs exakt
   pruefen.
3. Genau einen Zustandsbeleg je im Eingang enthaltenem VU verlangen.
4. Nur die fuer die jeweilige VU-Regel benoetigten Herkunftswerte zulassen.
5. Kontext- und Zustandswerte deterministisch und ohne Toleranz vergleichen.
6. Nur bei vollstaendigem Herkunftsabgleich `valid = true` melden.

## Schutzgrenzen

- Der eingereichte Zustandsbeleg wird nicht aus einem Runner geladen und
  authentifiziert keinen historischen Lauf.
- Keine Aenderung der VU-Regeln, Zustandscontainer oder Snapshotloader.
- Keine Loader-Aufrufe, Snapshot-Erzeugung, Speicherung oder Teilresultate.
- Keine Runner-Kopplung und keine Simulation.
- Keine historische RNG- oder Vollgleichheitsbehauptung.

## Nachweis

- positiver Herkunftstest fuer jede der zehn VU-Strategien;
- negative Tests fuer Perioden-, Schwellen-, Vorperioden- und Marktwerte;
- Tests fuer Version, exakte Feldform und vollstaendige VU-Zuordnung;
- Test, dass kein VU-Snapshotloader aufgerufen wird;
- GET-Vertrag und POST-Validierung mit klarer Methodengrenze;
- Migrationsnotiz und aktualisierte Dokuindizes.

## Restplanung

- PR121: Einen vollstaendig gueltigen PR120-Eingang atomar in die vorhandenen
  VU-Snapshottypen materialisieren, weiterhin ohne Speicherung, Runner oder
  Simulation.
- PR122: Materialisierte VU-Snapshots in der Workbench rein lesend und mit
  ihren Herkunftspruefungen anzeigen.
- Erst danach darf ein eigener Plan-PR die kontrollierte Verbindung mit einem
  Ausfuehrungspfad bewerten.
