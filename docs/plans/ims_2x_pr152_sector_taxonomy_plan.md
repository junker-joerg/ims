# PR152: Versionierte Spartentaxonomie

Stand: 2026-09-16

## Ziel

Vier stabile fachliche IDs fuer das IMS-2.x-Zielbild benennen: Kfz,
Sach-Haftpflicht, Leben und Kranken. Die Taxonomie ist ein rein lesender
Erweiterungsvertrag und noch kein Mehrsparten-Rechenmodell.

## Historische Grundlage

- `IMSDATA.C` begrenzt VU auf `MAXSPARTEN 2` und VN auf `MAXRISKS 2`.
- VU `Sp[1]`/`Sp[2]` und VN `Rk[1]`/`Rk[2]` enthalten
  Schaden-, Praemien- und Versicherungswerte.
- `IMS.E` verarbeitet diese Positionen getrennt. Der Python-Port haelt sie
  als 0-basierte Zweiervektoren in `ims.model.entities`.

Aus den Feldnamen und C-Typkuerzeln wird keine Zuordnung zu den vier neuen
Sparten abgeleitet. Das Mapping ist offen.

## Umsetzung

1. Unveraenderliche Taxonomie-Definitionen und JSON-serialisierbares
   `ims.sector-taxonomy.v1`-Payload in `ims.model.sector_taxonomy`.
2. Zwei getrennt beschriebene Legacy-Positionen mit C-/Python-Index und
   explizit leerer neuer Sparten-ID.
3. Read-only `GET /api/model/sector-taxonomy` fuer beide API-Varianten.
4. Fokus-Tests fuer IDs, Modellfamilien, offene Zuordnung, Unveraenderlichkeit,
   Serialisierung und schreibgeschuetzten API-Zugriff.

## Grenzen und Risiken

- Kfz und Sach-Haftpflicht sind neue Zielsegmente der Nichtleben-Modellierung,
  keine behauptete amtliche Berichtstaxonomie.
- Leben und Kranken benoetigen eigene Zustands- und Flussmodelle; die
  historischen Schadenregeln duerfen nicht stillschweigend uebernommen werden.
- Keine Aenderung an Entitaeten, Zweiervektoren, Runnern, Aggregaten, Exporten
  oder bestehenden Szenarien. Kein Lauf und kein Gleichheitsnachweis.
- PR153 entscheidet den Kompatibilitaetsadapter und belegt dessen Mapping.

## Validierung

Gezielte Modell- und API-Tests, danach der bestehende Release-Gate-Testlauf.
