# PR110: Strategieentwuerfe deterministisch in Snapshot-Bauplaene uebersetzen

Stand: 2026-09-02

## Ziel

PR110 verbindet das validierte Entwurfsformat aus PR108 mit den bereits
portierten VU- und VN-Regel-Snapshottypen. Die Uebersetzung ist rein im
Speicher, deterministisch und atomar: Nur ein vollstaendig gueltiger Entwurf
liefert Bauplaene; bei einem ungueltigen Entwurf entsteht keiner.

Ein Bauplan benennt den vorhandenen Snapshottyp und Loader, uebernimmt
ausschliesslich Ziel-ID, Regelvariante und die mit vorhandenen Loadern
typisierten Strategieparameter und weist alle noch fehlenden Snapshotfelder
aus. Er ist noch kein materialisierter oder ausfuehrbarer Snapshot.

## Historische und technische Grundlage

- `IMSDATA.C`: `ACTION.st`, `vkrvu` und `vkrvn` als historische Regelbindung;
- `IMS.E`: `Vrvu01` bis `Vrvu10`, `Vrvn01` bis `Vrvn06`, `Vuauini`,
  `Vnauini` und die Vdefmd6-Population;
- `ims.strategy-assignment-draft.v1`: validierter, fluechtiger Entwurf;
- vorhandene Parameter-Dataclasses und Loader in `vu_rules.py` und
  `vn_insurance_rules.py`;
- vorhandene Regel-Snapshot-Dataclasses und Snapshot-Loader derselben Module.

## Vertragsentscheidungen

1. Alle zehn VU- und sechs VN-Katalogstrategien erhalten genau ein explizites
   Snapshotziel.
2. `Vrvu07` bis `Vrvu09` werden auf den gemeinsamen
   `VUForeignInfoRuleSnapshot` mit `dumping`, `average` oder `attack`
   abgebildet.
3. `Vrvn01` bis `Vrvn06` werden auf `VNInsuranceRuleSnapshot` mit dem
   vorhandenen `rule_kind` abgebildet.
4. Die Strategieparameter werden erneut durch die vorhandenen Parameterloader
   typisiert. Es entstehen keine neuen Wertebereiche oder Defaults.
5. Noch fehlende Draws, Schockstatus, Zinssatz, Schwellen, Marktinputs und
   Vorperiodenzustaende bleiben als `unresolved_snapshot_fields` sichtbar.
6. Snapshot-Loader werden nicht aufgerufen. Insbesondere duerfen ihre
   technischen Fallbackwerte keine unbekannten Fachwerte ersetzen.
7. Aktivierungsperiode, Laufgrenze und logische Zeit bleiben Metadaten der
   Zuordnung und werden nicht still in eine Periodenauswahl umgedeutet.

## Lieferumfang

- Vertrag `ims.strategy-assignment-snapshot-translation.v1`;
- vollstaendiges Mapping fuer 16 Strategien auf vorhandene Snapshottypen;
- reine Funktion `translate_strategy_assignment_draft`;
- GET-Endpunkt
  `/api/strategies/assignment-snapshot-translation-contract`;
- POST-Endpunkt `/api/strategies/assignment-snapshot-translation`;
- Modul-, API- und Dokumentationstests.

## Geschlossene Grenzen

- keine Datei-, Browser- oder Datenbankspeicherung;
- keine Anwendung technischer Snapshot-Defaults;
- keine Materialisierung unvollstaendiger Snapshot-Bauplaene;
- keine Verbindung zu Run-Control oder einem Runner;
- kein Simulationsstart;
- keine historische Vollgleichheitsbehauptung.

## Validierung

- Katalogabdeckung und Eindeutigkeit aller 16 Abbildungen pruefen;
- reale Snapshot-Dataclasses, Loader und vollstaendige Feldpartition pruefen;
- Parameterobjekte gegen ihre vorhandenen Loader typisieren;
- deterministisch gleiche Ausgabe bei gleichem Entwurf pruefen;
- ungueltige Entwuerfe ohne Teiluebersetzung abweisen;
- fehlende VU-Schwellen und Laufzeitwerte explizit sichtbar halten;
- API-Schreibmethoden abweisen;
- vollstaendige Python-Regression ohne Simulationsstart ausfuehren.

## Anschlussplanung

PR111 kann die Bauplaene und ihre noch fehlenden Laufzeitwerte read-only in
der Workbench anzeigen. Danach braucht die Materialisierung einen eigenen
Vertrag fuer explizite Perioden-, Draw-, Markt- und Vorperiodenkontexte. Erst
ein weiterer, separat freizugebender Schritt darf vollstaendige Snapshots an
einen Runner uebergeben.
