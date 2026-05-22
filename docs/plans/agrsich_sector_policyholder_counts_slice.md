# Plan: Sektorisierte VU-Versichertenzaehler in Agrsich

## Ziel

Der Agrsich-Kern soll die bereits portierten sektorspezifischen VU-
Versichertenzaehler fuer die Exportfelder `Vn1` und `Vn2` verwenden.

## Ursprung im Altcode

- historische Versicherer-Agrsich-Ausgaben mit getrennten Spalten `Vn1` und
  `Vn2`
- portierter VN-Abrechnungskern aus `Vrvn01` bis `Vrvn03`, der
  `policyholders_current_sector` und den skalaren Gesamtzaehler gemeinsam
  fortschreibt

## Umsetzung

1. Sektorzugriff fuer `Insurer.policyholders_current_sector` im Agrsich-Service.
2. Skalarer Fallback bleibt erhalten, wenn programmgesteuerte Aufrufer keinen
   Sektorvektor setzen.
3. Export- und Replay-Erwartungen werden auf sektorspezifische `Vn1`-/`Vn2`-
   Werte umgestellt.

## Grenzen

- keine neue Aggregatstufe
- keine neue VN-Wahl-, Praeferenz- oder Zufallslogik
- keine Behauptung historischer Vollgleichheit
