# Agrsich: sektorisierte VU-Versichertenzaehler

Dieser Slice schaerft den vorhandenen Versicherer-Agrsich-Pfad fuer die Felder
`Vn1` und `Vn2`.

## Ursprung im Altcode

- historische Versicherer-Agrsich-Tabellen weisen `Vn1` und `Vn2` als getrennte
  Spalten aus
- der portierte VN-Abrechnungskern aus `Vrvn01` bis `Vrvn03` schreibt bereits
  `policyholders_current_sector` je Sparte und `policyholders_current` als
  Gesamtzaehler fort

## Python-Abbildung

- `ims.model.agrsich_service` liest fuer Versicherer-Agrsich-Metriken
  `policyholders_current_sector[index]`
- wenn kein Sektorvektor gesetzt ist, bleibt `policyholders_current` der
  kontrollierte Fallback fuer bestehende Programmatic-Caller
- Aggregatstufen II bis IV mitteln die sektorspezifischen Zaehler analog zu
  Praemien, Werbung und Reserven

## Validierung

- direkter Agrsich-Service-Test fuer sektorisierte VU-Versichertenzaehler
- Replay-, VN-Agrsich- und explizite VU/VN-Runner-Tests mit aktualisierten
  `Vn1`-/`Vn2`-Referenzzeilen

## Grenzen

- keine neue historische Agrsich-Dateifamilie
- keine neue VN-Wahl-, Praeferenz- oder Zufallslogik
- keine Vollsimulation und keine Behauptung historischer Vollgleichheit
