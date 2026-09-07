# PR116: VN-Regel-Snapshots atomar materialisieren

Stand: 2026-09-07

## Ziel

PR116 uebertraegt einen vollstaendig gueltigen PR115-Eingang in die bereits
vorhandene `VNInsuranceRuleSnapshot`-Dataclass. Alle VN-Eintraege werden
zunaechst nur im Speicher aufgebaut. Die Ergebnisliste wird erst
veroeffentlicht, wenn jeder benoetigte verschachtelte Loader und jeder
Snapshot-Loader erfolgreich war.

Der Schritt speichert nichts und fuehrt keine VN-Regel aus.

## Historische und technische Grundlage

- `IMS.E`, `act Vrvn01` bis `act Vrvn06`: historische Auswahl-, Such- und
  Informationsregeln fuer Versicherungsnehmer;
- PR110: Ziel-ID, Regelart und typisierte Strategieparameter;
- PR112: expliziter Einperiodenkontext;
- PR114: periodenabhaengige Merge- und Loaderfolge;
- PR115: strenge, atomare Pruefung der VN-Kontextformen;
- `vn_insurance_rules.py`: vorhandene verschachtelte Loader und
  `vn_insurance_rule_snapshot_from_mapping`.

## Materialisierungsfolge

1. Den gesamten Eingang mit PR115 validieren.
2. Bei einem Fehler keinen Snapshot-Loader aufrufen.
3. Die VN-Bauplaene aus PR110 und ihre passenden Kontexteintraege bestimmen.
4. Nur die in der aktuellen Periode konsumierten Kontextfelder uebernehmen.
5. Verschachtelte Werte mit den in PR114 benannten Loadern typisieren.
6. Ziel-ID, Regelart, Parameter und Kontextwerte ohne Fachdefaults verbinden.
7. Den deklarierten Snapshot-Loader genau einmal je VN-Eintrag aufrufen.
8. Die typisierte Snapshotliste nur bei vollstaendigem Erfolg zurueckgeben.

Periode 1 uebernimmt je VN ausschliesslich `initial_decisions`. Ab Periode 2
gelten die in PR114 und PR115 belegten regelabhaengigen Felder und
Fallbackbedingungen.

## Atomare Fehlergrenze

PR115-Fehler verhindern jeden Snapshot-Loader-Aufruf. Ein defensiv
aufgefangener Fehler eines verschachtelten oder des eigentlichen
Snapshot-Loaders verwirft auch bereits lokal erzeugte Snapshots. Der Bericht
liefert in beiden Faellen `snapshots = []` und
`partial_results_returned = false`.

## Lieferumfang

- Materialisierungsbericht
  `ims.strategy-assignment-snapshot-materialization.v1`;
- POST-Endpunkt
  `/api/strategies/assignment-snapshot-materialization`;
- aktualisierter GET-Vertrag
  `/api/strategies/assignment-snapshot-materialization-contract`;
- typisierte In-Memory-Snapshots fuer `Vrvn01` bis `Vrvn06`;
- Positiv-, Perioden-1-, Loaderfehler-, Atomaritaets-, API- und
  Dokumentationstests.

## Geschlossene Grenzen

- keine Aenderung der historischen oder portierten VN-Fachlogik;
- keine Ableitung fehlender Werte oder Zufallsziehungen;
- keine Teilresultate;
- keine Speicherung und keine Metadatenbank-Schreibvorgaenge;
- keine Run-Control- oder Runner-Kopplung;
- kein Aufruf von `apply_vn_insurance_rule_snapshot`;
- kein Simulationsstart;
- keine historische RNG- oder Vollgleichheitsbehauptung.

## Validierung

- alle sechs VN-Regelarten in Periode 2 typisiert materialisieren;
- Periode 1 auf Startentscheidungen begrenzen;
- ungueltige PR115-Eingaenge vor dem Snapshot-Loader abweisen;
- bei einem spaeten Loaderfehler keine Teilliste zurueckgeben;
- API-Methodengrenzen und JSON-Fehler pruefen;
- Gesamtregression und Windows-Release-Gate ohne Simulation ausfuehren.

## Anschlussplanung

PR117 kann die rein im Speicher erzeugten Snapshots in der Workbench lesbar
anzeigen. Bearbeitung, Speicherung, Runner und Simulation bleiben danach
weiterhin eigene Freigaben.
