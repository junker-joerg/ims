# IMS 2.x: versionierte Spartentaxonomie

Stand: 2026-09-16
Vertrag: `ims.sector-taxonomy.v1`

## Fachliche Bedeutung

PR152 gibt den vier geplanten Modellsegmenten stabile IDs. Kfz und
Sach-Haftpflicht sind getrennte Nichtleben-Zielsegmente; Leben und Kranken
werden als eigenstaendige Modellfamilien gefuehrt. Sach-Haftpflicht ist hier
ein zusammengefasstes **Modellsegment**, keine amtliche Klassifikation.

| ID | Anzeigename | Modellfamilie | Stand |
| --- | --- | --- | --- |
| `motor` | Kfz | `non_life` | nur Taxonomie |
| `property_liability` | Sach-Haftpflicht | `non_life` | nur Taxonomie |
| `life` | Leben | `life` | nur Taxonomie |
| `health` | Kranken | `health` | nur Taxonomie |

`sector_id` ist die stabile Identitaet fuer kuenftige Vertraege. Reihenfolge,
Anzeigename und historische Vektorposition sind keine Identitaeten.

## Herkunft und Mapping

| Altcode | Bestehender Python-Port | Bedeutung in PR152 |
| --- | --- | --- |
| `IMSDATA.C`: `MAXSPARTEN 2`, `classVU.Sp[1/2]`; `IMS.E`: getrennte Spartenoperationen | `ims.model.entities.Insurer` mit 0-basierten Zweiervektoren | historische VU-Positionen 0 und 1 |
| `IMSDATA.C`: `MAXRISKS 2`, `classVN.Rk[1/2]`; `IMS.E`: getrennte Risikooperationen | `ims.model.entities.Policyholder` mit 0-basierten Zweiervektoren | historische VN-Positionen 0 und 1 |
| keine belegte Zuordnung zu den vier neuen Zielnamen | kein neuer Adapter | `mapped_sector_id = null`, `mapping_status = unresolved` |

Insbesondere sind `Sp[1]`/`Rk[1]` **nicht** als Kfz und
`Sp[2]`/`Rk[2]` **nicht** als Sach-Haftpflicht belegt. Auch die historischen
C-Typkuerzel liefern keinen Nachweis fuer Leben oder Kranken. Ein solcher
Schluss wuerde die Bedeutung vorhandener Ergebnisse veraendern.

## Technischer Vertrag

`ims.model.sector_taxonomy` liefert unveraenderliche Definitionen und ein
JSON-serialisierbares read-only Payload. `GET /api/model/sector-taxonomy`
stellt dasselbe Payload ueber FastAPI und den Starlette-Fallback bereit. Die
zwei historischen Positionen stehen getrennt von `sectors` unter
`legacy_vector`; fuer beide bleibt `mapped_sector_id` leer.

Der `extension_contract` sagt aus: Neue Sparten brauchen einen expliziten
Adapter und eigene Zustaende; es gibt noch keine spartenspezifische
Strategiezuordnung oder Bilanz. Bestehende Zweiervektoren, Regeln,
Runner, Exporte und gespeicherte Laeufe bleiben unveraendert.

## Offene Punkte

- PR153 muss das Kompatibilitaetsmapping fuer die beiden Schadenpositionen
  fachlich pruefen, ausdruecklich versionieren und den Altpfad stabil halten.
- PR154 kann erst danach Strategie- und Parameterzuordnungen je benannter
  Sparte validieren.
- Leben und Kranken brauchen spaeter getrennte Zustands-, Fluss- und
  Strategievertraege. Die Schadenlogik wird nicht einfach wiederverwendet.
- Es wird weder eine historische Vollgleichheit noch regulatorische
  Vollstaendigkeit behauptet. PR152 startet keine Simulation.
