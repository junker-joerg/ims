# PR118: VU-Snapshot-Materialisierung inventarisieren

## Ziel

PR118 legt eine separate, read-only Vertragsgrenze fuer die spaetere
Materialisierung der vorhandenen VU-Regel-Snapshottypen fest. Der Schritt
beschreibt die zehn katalogisierten VU-Strategien, acht Snapshottypen, offene
Snapshotfelder und zusaetzliche Laufzeitzustaende. Er validiert oder erzeugt
noch keine VU-Snapshots.

## Historischer und heutiger Ursprung

- `IMS.E`, `act Vrvu01` bis `act Vrvu10`: Periodengrenzen, Ziehungen,
  Vorperiodenwerte, Zins, Schock und BAV-Fremdinformation;
- `python_port/ims/model/vu_rules.py`: acht vorhandene Snapshottypen und deren
  Loader sowie die bereits portierten deterministischen Regelkerne;
- `python_port/ims/engine/vu_rule_runner.py`: heutige technische Fallbacks fuer
  Ziehungen, VU-Zustaende und aktive VN;
- `python_port/ims/strategies/assignment_snapshot_translation.py`: Zuordnung
  der zehn Strategien zu Snapshottyp, Loader und Collection.

`Vrvu07` bis `Vrvu09` teilen sich absichtlich den Typ
`VUForeignInfoRuleSnapshot`; die drei Fremdinformationsquellen werden ueber
`rule_kind` unterschieden. `Vrvu10` ist historisch vorhanden, gehoert aber
nicht zu den Vdefmd6-Regelgruppen. `Vrvu04` bleibt wegen der benoetigten zwei
Vorperioden bis einschliesslich Periode 2 im Fortschreibungszweig.

## Umsetzung

1. Eigenen versionierten VU-Bestandsvertrag anlegen.
2. Offene Snapshotfelder samt Form, Verbrauchszeitpunkt und bestehenden
   Loader-/Runner-Fallbacks dokumentieren.
3. Externe Zustandsabhaengigkeiten getrennt von Snapshotfeldern ausweisen.
4. Konsistenz gegen Strategiekatalog, PR110-Ziele und vorhandene Loader
   pruefen, ohne einen Loader aufzurufen.
5. Einen ausschliesslich lesenden API-Endpunkt bereitstellen.
6. Herkunft, Grenzen und Folgeentscheidung dokumentieren.

## Schutzgrenzen

- kein VU-Eingabeformat und keine Eingabevalidierung;
- keine Uebernahme technischer Fallbacks als fachliche Defaults;
- kein Loader-Aufruf und keine Snapshot-Erzeugung;
- keine Speicherung, Runner-Kopplung oder Simulation;
- keine Aussage zu historischer RNG- oder Vollgleichheit.

## Validierung

- Ziel-, Feld- und Loaderkonsistenz fuer alle zehn VU-Strategien;
- gesonderte Pruefung der gemeinsamen `Vrvu07`-bis-`Vrvu09`-Abbildung;
- API-Methodengrenze `GET` gegen schreibende Methoden;
- Dokumentations- und Indexnachweis.

## Naechster Schritt

Erst ein eigener Folge-PR darf auf dieser Bestandsaufnahme ein enges,
versioniertes VU-Eingabe- und Validierungsformat entwerfen. Dabei muessen die
fachlichen Quellen der Schwellenwerte sowie der Umgang mit Ziehungen und
Runner-Fallbacks explizit entschieden werden.
