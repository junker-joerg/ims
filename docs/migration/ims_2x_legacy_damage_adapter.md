# IMS 2.x: Kompatibilitaetsadapter fuer die zwei Schadenpositionen

Stand: 2026-09-16
Vertrag: `ims.legacy-damage-adapter.v1`

## Beleg und Grenze

Die Dissertation beschreibt auf PDF-Seite 46 einen Markt mit zwei
Schadenversicherungssparten. Auf PDF-Seiten 73-74 sind die Exportspalten
als Sparte 1 und Sparte 2 beschrieben. `IMSDATA.C` definiert dazu
`MAXSPARTEN 2`, `MAXRISKS 2`, VU `Sp[1/2]` und VN `Rk[1/2]`;
`IMS.E` berechnet beide Positionen getrennt.

| Historische Position | Python-/Exportindex | Stabile Legacy-ID | Neue Sparten-ID |
| --- | ---: | --- | --- |
| VU `Sp[1]`, VN `Rk[1]` | 0 | `legacy.damage_1` | offen (`null`) |
| VU `Sp[2]`, VN `Rk[2]` | 1 | `legacy.damage_2` | offen (`null`) |

Die Zuordnung **C 1/2 zu Python 0/1** ist durch die bestehenden
Zweiervektoren in `ims.model.entities` und den 0-basierten
`sector_index` der Ergebnistabelle belegt. Die Zuordnung **zu Kfz oder
Sach-Haftpflicht** ist es nicht. Auch `LV`/`KV` als C-Typkuerzel belegen
keine solchen modernen Produktsegmente. Die vier Ziel-IDs aus PR152
bleiben deshalb von den Legacy-IDs getrennt.

## Umsetzung

`ims.model.legacy_damage_adapter` liefert:

- `legacy_damage_sector_id(index)` fuer die exakte Indexabbildung;
- `adapt_legacy_damage_vector(values)` fuer eine neue, unveraenderliche
  Sicht auf genau zwei skalare Werte in unveraenderter Reihenfolge und
  ohne Typ- oder Wertkonvertierung;
- einen JSON-serialisierbaren Vertrag fuer
  `GET /api/model/legacy-damage-adapter-contract`.

Der Adapter akzeptiert bestehende numerische Zweiervektoren und
Versicherer-IDs mit `null`. Andere Laengen, Boolesche Werte, Text und
nicht endliche Zahlen werden am Adapterrand abgewiesen. Er veraendert
keinen Eingabevektor. Der API-Endpunkt ist nur lesend und in FastAPI
sowie Starlette verfuegbar.

## Abgrenzung

Der Adapter benennt Altpositionen neutral; er fuehrt weder eine
Spartenzuordnung im Simulationskern noch ein Label in bestehenden
Ergebnisdateien ein. Runner, Regeln, Szenarien, Aggregatdefinitionen,
Exportspalten, Digests und gespeicherte Laeufe sind unveraendert.

Ein kuenftiger Modellversuch darf die beiden Legacy-IDs nur mit einer
ausdruecklichen, als Annahme markierten Szenariobindung auf Kfz und
Sach-Haftpflicht beziehen. Das waere eine neue Modellinterpretation,
keine Rekonstruktion historischer Tatsachen. Leben und Kranken erhalten
eigene Zustaende und Regeln. Es gibt keinen historischen
Vollgleichheitsnachweis.

## Validierung und Anschluss

Fokus-Tests pruefen Index, Werte, Typen, negative Formen, unveraenderte
VU-/VN-Zustaende und den schreibgeschuetzten API-Vertrag. Die vorhandenen
Altpfadtests pruefen weiterhin den Rechenkern. PR154 validiert nun
getrennte, rein geplante Strategie- und Parameterzuordnungen fuer benannte
Nichtleben-Sparten; die historische Bindung und Ausfuehrung bleiben offen.
