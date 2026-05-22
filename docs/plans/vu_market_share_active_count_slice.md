# Plan: Vrvu05-Aktivzaehlerbasis

## Ziel

Der Vrvu05-/Mark-Up-III-Pfad soll den historischen Nenner `akvn` kontrolliert aus dem
bereits berechneten BAV-Aktivitaetszustand nutzen koennen. Explizite Snapshot-Werte
bleiben als Override erhalten.

## Ursprung

- `IMS.E`, `act Vrvu05`
- Marktanteilsformel je Sparte: `Vn / akvn`

## Umsetzung

- `VUMarketShareMarkupRuleSnapshot.active_policyholder_count` wird optional.
- Die direkte Snapshot-Anwendung verlangt weiterhin eine konkrete Zaehlerquelle:
  Snapshot-Wert oder Runner-Wert.
- Der VU-Periodenrunner uebergibt nach `compute_extended_foreign_info` den aktuellen
  BAV-Aktivzaehler an Vrvu05.

## Risiken und Grenzen

- Keine Herleitung historischer Regelwahl.
- Keine Vollsimulation.
- Die BAV-Aktivitaetslogik ist die kontrollierte Python-Basis fuer `akvn`; eine
  staerkere historische Referenzvalidierung bleibt ein separater Schritt.
