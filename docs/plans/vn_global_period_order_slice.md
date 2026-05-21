# VN-Globale-Periodenordnung

## Ziel

Der explizite VN-Mehrperiodenrunner nutzt dieselbe globale Periodenachse wie
die VU- und kombinierten Periodenpfade. Damit koennen Szenarien aus mehreren
Runs kontrolliert verarbeitet werden, ohne lokale Periodennummern als alleinige
Ordnung zu interpretieren.

## Umfang

- `VNSettlementPeriodRunResult` berichtet die berechnete globale Periode.
- `VNSettlementMultiPeriodRunResult` berichtet neben lokalen Perioden auch die
  validierte globale Periodenfolge.
- `VNStateCarryover` berichtet lokale und globale Quell-/Zielperioden.
- Die Mehrperiodenvalidierung lehnt doppelte oder rueckwaerts laufende globale
  Perioden vor der Regelanwendung ab.

## Grenzen

- Keine neue VN-Wahl-, Praeferenz-, RNG- oder Schedulerlogik.
- Keine Vollsimulation.
- Keine Behauptung historischer Vollgleichheit.
