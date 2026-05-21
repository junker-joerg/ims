# Plan: Globale Carryover-Diagnose im expliziten VU/VN-Runner

## Ziel

Der gemeinsame explizite VU/VN-Mehrperiodenrunner validiert seine Periodenfolge
bereits ueber globale Perioden. Dieser Slice macht dieselbe Zeitachse auch in der
kombinierten Carryover-Diagnose sichtbar.

## Ursprung im Altmodell

- periodische Fortschreibung der bereits portierten `Vrvu*`-Slices
- VN-Periodenwirkungen aus `Vrvn01` bis `Vrvn03`
- globale Agrsich-Zeitachse aus kontrollierten Mehrperiodenlaeufen

## Umsetzung

1. `ExplicitPeriodCarryover` um globale Quell- und Zielperioden erweitern.
2. Die Werte aus vorherigem Periodenergebnis und geladenem Folgeszenario ableiten.
3. Test fuer laufuebergreifende lokale Perioden mit unterschiedlichen globalen
   Perioden ergaenzen.
4. Migrationsnotiz aktualisieren.

## Grenzen

- Keine neue VU- oder VN-Regel.
- Keine neue automatische Zustandsfortschreibung.
- Keine Vollsimulation und keine Behauptung historischer Vollgleichheit.
