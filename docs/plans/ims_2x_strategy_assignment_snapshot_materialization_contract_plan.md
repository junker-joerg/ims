# PR114: Materialisierungsvertrag und verschachtelte VN-Kontexte

Stand: 2026-09-07

## Ziel

PR114 beschreibt deterministisch, wie ein gueltiger Strategieentwurf und ein
passender Einperiodenkontext spaeter in die vorhandenen Regel-Snapshotloader
eingehen duerfen. Der Schritt schliesst insbesondere die in PR112 bewusst
offen gelassenen Formen fuer VN-Ziehungen, Anfangsentscheidungen,
Versicherereingaben und Suchhistorie.

Der Vertrag ist rein lesend. Er validiert oder verbraucht noch keinen
Kontextwert und erzeugt keinen Snapshot.

## Ursprung und bestehende Zieltypen

- `IMS.E`, `act Vrvn01` bis `act Vrvn06`: Startperiode, VN-Regelwahl,
  aktive VU, Werbung, Praemien, Suchhistorie und Informationskosten;
- `vn_rules.py`: `VNInsuranceDecision` und der vorhandene Loader fuer genau
  eine Entscheidung je Sparte;
- `vn_insurance_rules.py`: die vorhandenen regelabhaengigen Draw-, VU-Input-
  und Historientypen sowie `VNInsuranceRuleSnapshot`;
- PR110: partielle Snapshot-Bauplaene mit Ziel-ID, Regelart und typisierten
  Parametern;
- PR112: formal gueltiger, aber bei verschachtelten VN-Werten noch generischer
  Einperiodenkontext.

## Vertragsentscheidungen

1. Der spaetere Materialisierer muss Entwurf, Bauplan und Kontext erneut
   atomar pruefen.
2. Basis ist `snapshot_payload` aus PR110. Nur die exakt passenden
   `values` aus PR112 duerfen ergaenzt werden. Ziel-ID, Regelart und Parameter
   duerfen nicht ueberschrieben werden.
3. Vor dem Aufruf eines Snapshotloaders muessen die regelabhaengigen
   verschachtelten Werte gegen neun explizite Loaderformen geprueft sein.
4. In Periode 1 benoetigen alle sechs VN-Regeln genau zwei
   `initial_decisions`, je eine fuer `sector_index` 0 und 1. Die spaetere
   Regelwahl wird dort nicht konsumiert.
5. Ab Periode 2 gelten getrennte Pflicht- und Bedingungsfelder je VN-Regel.
   Insbesondere sind Fallback-Ziehungen bei `Vrvn03` und `Vrvn04` nur dann
   erforderlich, wenn Werbung beziehungsweise versicherte Historie keine
   Auswahl liefern.
6. `Vrvn05` braucht zwei Ziehungslisten, deren Laengen die ausgewaehlten
   Stichprobengroessen abdecken. `Vrvn06` verbraucht keine Wahlziehungen.
7. Die vorhandenen Loader bleiben die einzige Typisierungsoberflaeche. Der
   Vertrag fuehrt weder parallele Snapshotklassen noch neue Fachlogik ein.
8. Kulante Loader-Normalisierungen wie das Duplizieren eines einzelnen
   Sektorwerts sind kein Bestandteil des Materialisierungsvertrags. Die
   spaetere Eingangspruefung muss zwei explizite Sektorwerte verlangen.

## Lieferumfang

- Vertrag
  `ims.strategy-assignment-snapshot-materialization-contract.v1`;
- neun loadergebundene Definitionen fuer `draws`, `initial_decisions`,
  `insurer_inputs` und `history`;
- sechs periodenabhaengige VN-Regeldefinitionen mit C-Quellankern;
- explizite atomare Merge- und Loader-Reihenfolge;
- GET-Endpunkt
  `/api/strategies/assignment-snapshot-materialization-contract`;
- synthetische Positivbeispiele fuer alle neun vorhandenen Loader;
- Modul-, API- und Dokumentationstests.

## Geschlossene Grenzen

- keine Aenderung des generischen PR112-Kontextvalidators;
- keine Verwendung oder Normalisierung eines Workbench-Kontexts;
- kein Aufruf von `vn_insurance_rule_snapshot_from_mapping`;
- keine Snapshot-Materialisierung oder Teilfreigabe;
- keine Speicherung, Run-Control- oder Runner-Kopplung;
- kein Simulationsstart;
- keine historische RNG- oder Vollgleichheitsbehauptung.

## Validierung

- alle sechs VN-Strategien exakt gegen die PR110-Ziele pruefen;
- alle neun verschachtelten Formen an vorhandene aufrufbare Loader binden;
- periodenabhaengige Pflicht-, Bedingungs- und nicht konsumierte Felder
  maschinenlesbar ausgeben;
- synthetische Beispiele direkt mit den jeweiligen verschachtelten Loadern
  laden;
- belegen, dass der GET-Endpunkt keinen Snapshotloader aufruft und keine
  schreibende HTTP-Methode zulaesst;
- vollstaendige Regression ohne Simulationsstart ausfuehren.

## Anschlussplanung

PR115 hat die neun PR114-Formen und die periodenabhaengigen Bedingungen in
eine atomare, rein validierende Erweiterung des Einperiodenkontexts
ueberfuehrt. Erst PR116 darf danach gueltige Bauplaene und Kontexte ueber die
vorhandenen Snapshotloader materialisieren. Run-Control, Runner und Simulation
bleiben weitere getrennte Freigaben.
