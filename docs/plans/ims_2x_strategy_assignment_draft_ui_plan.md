# PR109: Strategieentwuerfe in der Workbench erfassen und pruefen

Stand: 2026-09-02

## Ziel

PR109 macht das in PR108 festgelegte Strategiezuordnungsformat in der
Workbench bedienbar. Anwender koennen einen fluechtigen Entwurf fuer einzelne
VU und VN zusammenstellen und ihn gegen die vorhandene API-Pruefgrenze
validieren.

Der Schritt speichert keinen Entwurf, erzeugt keine Regel-Snapshots und startet
keinen Simulationslauf.

## Historische und technische Grundlage

- `IMSDATA.C`: `ACTION.st`, `vkrvu` und `vkrvn` als historische Bindung von
  Regeln an einzelne Akteure;
- `IMS.E`: `Vuauini`, `Vnauini` und `Vdefmd6` als belegte Zielpopulation und
  Quelle der Aktivierungsangaben;
- `ims.strategy-catalog.v1`: stabile Strategie-IDs und Akteurstypen;
- `ims.strategy-assignment-contract.v1`: Zielgrenzen und vorhandene
  Parameterschemata;
- `ims.strategy-assignment-draft.v1`: versioniertes Entwurfsformat;
- `POST /api/strategies/assignment-draft-validation`: zustandslose
  Serverpruefung aus PR108.

## Bedienpfad

1. Entwurfs-ID und Bezeichnung erfassen.
2. Akteurstyp, Ziel-ID und eine fuer den Akteur zulaessige Strategie waehlen.
3. Aktivierungsperiode, Laufgrenze und logische Zeit eintragen.
4. Bei parametrisierbaren Strategien alle vorhandenen Felder fuer die zwei
   historischen, weiterhin unbenannten Positionen erfassen.
5. Zuordnung in die lokale Entwurfsliste uebernehmen, bei Bedarf bearbeiten
   oder entfernen.
6. Den gesamten Entwurf serverseitig pruefen und Fehler mit Pfad und Meldung
   anzeigen.

Leere Fachwerte werden nicht mit neuen Defaults gefuellt. Die lokale
Vollstaendigkeitspruefung dient nur der Formbedienung; die API bleibt die
verbindliche Pruefgrenze.

## Lieferumfang

- vierter Workbench-Tab `Entwurf`;
- dynamisches Formular aus Katalog, Zielgrenzen und Parameterschemata;
- lokale Liste mit Hinzufuegen, Bearbeiten und Entfernen;
- Anzeige des serverseitigen Validierungsberichts;
- responsive Darstellung auf Desktop und Mobilgeraeten;
- fokussierte Frontend- und Dokumentationstests.

## Geschlossene Grenzen

- keine Datei-, Browser- oder Datenbankspeicherung;
- kein Laden oder Importieren fremder Entwuerfe;
- keine Gruppen- oder sektorweise Strategiezuordnung;
- keine neuen fachlichen Parametergrenzen oder Defaults;
- keine Uebersetzung in Regel-Snapshots;
- keine Kopplung an Run-Control, Runner oder Simulation;
- keine historische Vollgleichheitsbehauptung.

## Validierung

- Frontend-Quellvertrag fuer beide PR108-Endpunkte und den Entwurfs-Tab;
- UI-Zustaende fuer leeren, bearbeiteten, gueltigen und fehlerhaften Entwurf;
- Frontend-Produktionsbuild;
- bestehende Python-Regression ohne Simulationsstart;
- visuelle Pruefung der Workbench auf Desktop und Mobilgeraet.

## Anschlussplanung

PR110 soll die deterministische Uebersetzung eines gueltigen Entwurfs in die
bereits vorhandenen VU-/VN-Regel-Snapshotformen als eigenen, rein fachlichen
Vertrag definieren und testen. Speicherung und Ausfuehrung bleiben danach
weiterhin getrennte Schritte.
