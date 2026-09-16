# PR153: Kompatibilitaetsadapter fuer zwei historische Schadenpositionen

Stand: 2026-09-16

## Ziel

Die zwei bestehenden Schadenvektor-Positionen erhalten stabile
Legacy-Identitaeten. Ein reiner Adapter stellt Zweiervektoren verlustfrei
und ohne Zustandsaenderung als zwei benannte Eintraege bereit. Die
Zuordnung zu Kfz und Sach-Haftpflicht bleibt ausdruecklich offen.

## Historische Grundlage

- `DISS.pdf`, PDF-Seite 46: Markt mit zwei Schadenversicherungssparten.
- `DISS.pdf`, PDF-Seiten 73-74: Exportspalten fuer Sparte 1 und 2.
- `IMSDATA.C`: `MAXSPARTEN 2`, `MAXRISKS 2`, VU `Sp[1/2]`, VN `Rk[1/2]`.
- `IMS.E`: getrennte Berechnungen fuer beide Positionen.
- Python-Port: Zweiervektoren in `ims.model.entities`, 0-basiertes
  `sector_index` in der 100-Perioden-Ergebnistabelle.

## Umsetzung

1. `legacy.damage_1` und `legacy.damage_2` als stabile Legacy-IDs.
2. Reiner Adapter fuer skalare Zweiervektoren: C-Position 1/2 entspricht
   Python-/Exportindex 0/1. Werte und Reihenfolge bleiben unveraendert.
3. Versionierter, rein lesender API-Vertrag mit offenem modernem Mapping.
4. Positiv-, Negativ- und Nichtmutations-Tests; vorhandene Altpfadtests bleiben
   unveraendert.

## Grenzen

Der Adapter fuehrt keine Regel aus und veraendert weder Runner noch
Szenario, Aggregat, Export, Digest oder Persistenz. Er setzt keine neue
Spartentaxonomie im Simulationskern durch. Ein spaeterer Modellversuch,
die Altpositionen als Kfz/Sach-Haftpflicht zu *interpretieren*, benoetigt
eine ausdrueckliche, als Annahme markierte Bindung und eigene Tests.
Historische Vollgleichheit wird nicht behauptet.

## Anschluss

PR154 kann auf den stabilen Legacy-IDs und den vier Ziel-IDs einen
validierenden Vertrag fuer Strategie-/Parameterzuordnungen aufbauen,
ohne die offene historische Zuordnung zu verdecken.
