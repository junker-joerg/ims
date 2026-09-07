# PR115: VN-Materialisierungseingaben atomar validieren

Stand: 2026-09-07

## Ziel

PR115 integriert die in PR114 fachlich beschriebenen verschachtelten
VN-Kontextformen und Periodenbedingungen in eine zustandslose, atomare
Validierung. Ein gueltiger PR108-Entwurf und sein PR112-Einperiodenkontext
werden gemeinsam geprueft. Nur wenn jeder VN-Eintrag besteht, ist der gesamte
Materialisierungseingang gueltig.

Der Schritt erzeugt keine Snapshots und fuehrt keine Regel aus.

## Historische und technische Grundlage

- `IMS.E`, `act Vrvn01` bis `act Vrvn06`: Startentscheidungen, aktive VU,
  Zufallsfallbacks, Werbung, Suchhistorie, Stichprobengroessen und
  Vollinformation;
- `vn_rules.py`: vorhandener Loader fuer zwei VN-Sektorentscheidungen;
- `vn_insurance_rules.py`: vorhandene Loader fuer Draw-, Werbe-, Praemien-
  und Historienformen;
- PR112: atomare Grundpruefung von Entwurf, Periode, Zieleintraegen und
  offenen Snapshotfeldern;
- PR114: neun loadergebundene verschachtelte Formen und sechs
  periodenabhaengige VN-Regelvertraege.

## Validierungsfolge

1. PR112-Kontext vollstaendig und atomar pruefen.
2. Bei einem Grundfehler keine verschachtelten Loader aufrufen.
3. Nur die VN-Eintraege des validierten PR110-Bauplans auswaehlen.
4. Nicht-null Pflichtwerte fuer Periode 1 oder Perioden ab 2 pruefen.
5. Verschachtelte Werte ohne Loader-Kulanz auf ihre exakte Form pruefen.
6. Den zu PR114 gehoerenden vorhandenen verschachtelten Loader aufrufen und
   sein Ergebnis nur fuer die weitere Pruefung im selben Aufruf verwenden.
7. Regel- und periodenabhaengige Bedingungen pruefen.
8. Den Gesamtbericht nur freigeben, wenn alle VN-Eintraege fehlerfrei sind.

## Fachliche Bedingungen

- Periode 1: je VN genau eine Anfangsentscheidung fuer Sektor 0 und 1;
- `Vrvn01` und `Vrvn02`: mindestens ein aktiver VU, keine doppelten IDs;
- `Vrvn03`: nicht leere Werbeeingaenge; Fallback-Ziehungen nur bei mindestens
  einem Sektor ohne positive Werbung erforderlich;
- `Vrvn04`: nur Historienperioden vor der Kontextperiode; Fallback-Ziehungen
  und mindestens ein aktiver VU, wenn einem Sektor versicherte Historie fehlt;
- `Vrvn05`: positive wirksame Normal- oder Schockstichprobengroessen und je
  Sektor ausreichend viele Ziehungen;
- `Vrvn05` und `Vrvn06`: nicht leere aktuelle VU-Praemieneingaenge und nicht
  negative Informationskostensaetze;
- `Vrvn03` und `Vrvn04`: nicht negative Schadenwahrscheinlichkeiten.

Einwertige Sektorlisten, String-IDs, nicht boolesche Statuswerte, unbekannte
verschachtelte Felder und stille ID-Deduplizierung werden abgewiesen. Damit
werden technische Normalisierungen vorhandener Loader nicht zu impliziten
Fachdefaults.

## Lieferumfang

- Validierungsbericht
  `ims.strategy-assignment-snapshot-materialization-validation.v1`;
- GET-Endpunkt
  `/api/strategies/assignment-snapshot-materialization-validation-contract`;
- POST-Endpunkt
  `/api/strategies/assignment-snapshot-materialization-validation`;
- synthetischer Periode-2-Gesamtkontext fuer alle sechs VN-Regeln;
- Positiv-, Negativ-, Atomaritaets-, API- und Dokumentationstests.

## Geschlossene Grenzen

- keine Aenderung an VU- oder VN-Regelkernen;
- keine Ableitung fehlender Kontextwerte oder Zufallsziehungen;
- keine Aufbewahrung normalisierter verschachtelter Loaderergebnisse;
- kein Aufruf von `vn_insurance_rule_snapshot_from_mapping`;
- keine Teilfreigabe;
- keine Snapshot-Materialisierung;
- keine Speicherung, Run-Control- oder Runner-Kopplung;
- kein Simulationsstart;
- keine historische RNG- oder Vollgleichheitsbehauptung.

## Validierung

- gueltige Periode 1 und Periode 2 getrennt belegen;
- alle sechs VN-Regeln in einem atomaren Positivfall pruefen;
- Grundfehler vor jedem verschachtelten Loader abbrechen;
- exakte Zwei-Sektor-Formen und vorhandene Loaderkompatibilitaet pruefen;
- beide Fallbackbedingungen, Suchzeitgrenze und Schockstichprobe negativ
  testen;
- belegen, dass weder Snapshotloader noch Regelausfuehrung erreicht werden;
- vollstaendige Regression und Windows-Release-Gate ohne Simulation starten.

## Anschlussplanung

PR116 kann ausschliesslich einen erfolgreich validierten PR115-Eingang
atomar mit den in PR110 deklarierten Snapshotloadern materialisieren. Die
Snapshotliste darf erst nach Erfolg aller Eintraege sichtbar werden. Eine
Speicherung, Runner-Kopplung und Simulation bleiben danach eigene Freigaben.
