# IMS 2.x: Vertrag vor der Snapshot-Materialisierung

Stand: PR114, 2026-09-07

## Fachliche Einordnung

PR110 kennt fuer jede Strategie den vorhandenen Snapshottyp und bereitet
Ziel-ID, Regelart sowie Parameter vor. PR112 erfasst die noch fehlenden Werte
fuer eine Periode, prueft `draws`, `initial_decisions`, `insurer_inputs` und
`history` bislang aber nur als allgemeine JSON-Strukturen.

PR114 schliesst diese Beschreibungsluecke fuer die sechs VN-Regeln. Der neue
read-only Vertrag benennt die vorhandenen Python-Loader, die fachlichen
Objektformen und die periodenabhaengige Verwendung. Er materialisiert noch
nichts.

## Gemeinsame Form der Startperiode

In `IMS.E` uebernehmen `Vrvn01` bis `Vrvn06` in Periode 1 die gespeicherten
Versicherungsstatus und Versicherer beider Risiken. Die Python-Oberflaeche
bildet das als `initial_decisions` mit genau zwei Eintraegen ab:

| Feld | Pflicht | Bedeutung |
| --- | --- | --- |
| `sector_index` | ja | genau einmal 0 und genau einmal 1 |
| `insured` | ja | Versicherungsstatus der Sparte |
| `insurer_id` | bedingt | positive ID bei versichert, sonst nicht gesetzt |
| `premium` | nein | optionaler nicht negativer Startwert |

Der bestehende Loader
`load_vn_insurance_decisions_from_mapping` prueft diese Form. Andere offene
Felder des gemeinsamen `VNInsuranceRuleSnapshot` werden in Periode 1 vom
Versicherungsregel-Dispatch nicht konsumiert.

## Regelwerte ab Periode 2

| Regel | Pflichtwerte | Bedingte Werte | Fachliche Form |
| --- | --- | --- | --- |
| `Vrvn01` / `compulsory` | aktive VU, zwei VU-Wahlziehungen | keine | Pflichtversicherung mit aktiver Zufallsauswahl |
| `Vrvn02` / `random` | Schockstatus, aktive VU, je zwei Status- und VU-Wahlziehungen | keine | zufaelliger Status und aktive Zufallsauswahl |
| `Vrvn03` / `preference` | Schockstatus, zwei Schadenwahrscheinlichkeiten, aktive VU-Werbebloecke | zwei Fallback-Ziehungen bei fehlender positiver Werbung | maximaler Werbewert je Sparte |
| `Vrvn04` / `search_history` | Schockstatus, zwei Schadenwahrscheinlichkeiten, Suchhistorie, aktive VU | zwei Fallback-Ziehungen ohne versicherte Vorhistorie | guenstigste fruehere versicherte Praemie je Sparte |
| `Vrvn05` / `sample_search` | Schockstatus, Marktindikator, Informationskostensatz, aktuelle VU-Praemien, zwei Ziehungslisten | keine | Stichprobe je Sparte; Drawzahl deckt die wirksame Stichprobengroesse |
| `Vrvn06` / `best_info` | Schockstatus, Marktindikator, Informationskostensatz, aktuelle VU-Praemien | keine Wahlziehungen | vollstaendige Betrachtung aller gelieferten aktiven VU |

Die Parameter fuer `Vrvn02` bis `Vrvn06` stammen bereits typisiert aus der
PR110-Uebersetzung. `Vrvn01` besitzt keinen eigenen Parameterblock.

## Neun verschachtelte Formen

Der Vertrag bindet neun Formen an bestehende Loader:

1. gemeinsame `initial_decisions`;
2. Pflichtversicherungsziehungen;
3. Zufallsregelziehungen;
4. Praeferenz-Fallbackziehungen;
5. VU-Werbebloecke der Praeferenzregel;
6. Such-Fallbackziehungen;
7. periodische Suchhistorie;
8. zwei Stichproben-Ziehungslisten;
9. aktuelle VU-Praemienbloecke fuer Stichprobe und beste Information.

VU-IDs muessen positiv und innerhalb einer Liste eindeutig sein. Werbe- und
Praemienvektoren enthalten zwei nicht negative Sektorwerte. Ziehungen liegen
in `[0.0, 1.0)`. Suchhistorien sind nach positiver Periode und Sektor
eindeutig; ihre Perioden muessen vor der zu materialisierenden Periode liegen.

Die bestehenden Draw- und VU-Input-Loader koennen einzelne Sektorwerte intern
teilweise duplizieren. Diese technische Kulanz wird nicht zur fachlichen
Eingabeform erhoben: Der PR114-Vertrag verlangt zwei explizite Sektorwerte,
damit eine spaetere Materialisierung keine stillen Defaults einsetzt.

## Bezug zum Altcode

- `IMS.E:2185`, `act Vrvn01`: aktive Zufallsauswahl nach der Startperiode;
- `IMS.E:2406`, `act Vrvn02`: Statusziehungen und aktive Zufallsauswahl;
- `IMS.E:2627`, `act Vrvn03`: VU-Werbung und bedingter Zufallsfallback;
- `IMS.E:2948`, `act Vrvn04`: Suche in frueheren VN-Praemien;
- `IMS.E:3229`, `act Vrvn05`: VU-Stichprobe nach `g0/g1`;
- `IMS.E:3521`, `act Vrvn06`: Praemieninformation aller aktiven VU.

Die bekannte Risiko-2-Nenner-Eigenheit von `Vrvn03` bleibt wie im bestehenden
Praeferenz-Slice dokumentiert. PR114 aendert daran keine Fachlogik und leitet
aus dem C-Code keine neue Regel ab.

## Deterministische spaetere Materialisierung

Der Vertrag legt sieben Schritte fest: Entwurf atomar validieren, PR110-
Bauplaene erzeugen, passenden PR112-Kontext pruefen, verschachtelte Werte
regelabhaengig pruefen, Kontextwerte ohne Ueberschreiben vorbereiteter Felder
zusammenfuehren, je Eintrag genau den deklarierten Loader aufrufen und erst
nach Erfolg aller Eintraege die Snapshotliste veroeffentlichen.

Teilresultate und Defaults vor dem Loader sind ausgeschlossen. Diese Folge ist
in PR114 nur beschrieben; sie wird nicht ausgefuehrt.

## API und verbleibende Grenze

`GET /api/strategies/assignment-snapshot-materialization-contract` liefert
Merge-Policy, neun verschachtelte Definitionen, sechs VN-Regeldefinitionen
und die weiterhin geschlossenen Grenzen.

Der PR112-Validator verwendet diese engeren Definitionen noch nicht. Das ist
im Payload mit `context_validator_uses_nested_contract = false` sichtbar und
wird durch einen Grenztest belegt. Entsprechend bleiben
`snapshot_loader_invocation_enabled` und `snapshot_materialization_enabled`
ebenfalls `false`.

Es erfolgen keine Speicherung, keine Runner-Kopplung und kein
Simulationsstart. Aus dem Vertrag folgt weder historische RNG-Gleichheit noch
historische Vollgleichheit.

## Naechster Schritt

PR115 hat die verschachtelten Formen samt Periodenbedingungen rein
validierend in den Kontextpfad integriert. PR116 hat danach die atomare
Snapshot-Materialisierung als eigenen, weiterhin nicht ausfuehrenden Schritt
freigegeben.
