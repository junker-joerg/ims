# Entity-Mapping

Dieses Dokument beschreibt eine erste, konservative Annäherung historischer Strukturen an neue Python-Entitäten.
Die Zuordnung bleibt vorläufig und dient nur dem datengetriebenen Einstieg.

## Historische Strukturen → neue Entitäten

- vermutete BAV-nahe Altstrukturen → `ims.model.entities.BAV`
- vermutete Versicherer-/Tarifträgerstrukturen → `ims.model.entities.Insurer`
- vermutete Vertrags- oder Bestandskundenstrukturen → `ims.model.entities.Policyholder`

## Bewusst minimale Felder

- `BAV`: nur `identifier`, `name`
- `Insurer`: nur `identifier`, `name`
- `Policyholder`: `identifier`, `name` sowie optionale Referenzen `insurer_id` und `bav_id`

## Bewusst noch fehlende Felder

- beitragsbezogene und tarifliche Details
- Status- und Regelattribute aus fachlichen Entscheidungswegen
- Markt-, Produkt-, Leistungs- oder Berechnungsparameter
- komplexe Relationen, die erst nach Sichtung des Altcodes stabil modelliert werden können

## Konservative Annahmen

- Identität und eine lesbare Bezeichnung reichen für ein erstes JSON-Szenario aus.
- Referenzen zwischen Entitäten werden nur als optionale IDs gehalten.
- Es wird keine Fachlogik, Validierung von Geschäftsregeln oder Ableitung weiterer Felder vorgenommen.

## Unsicherheiten

- Die Altstrukturen liegen aktuell nicht im Repository vor; das Mapping muss später validiert werden.
- Ob `Policyholder` die fachlich beste Entsprechung ist, bleibt bis zur Sichtung des Altcodes offen.
