# Plan: Expliziter VU/VN-Periodenrunner

## Ziel

Dieser Slice verbindet die bereits portierten expliziten VU-Regelkerne und den
expliziten VN-Schaden-/Abrechnungspfad in einem gemeinsamen Periodenschritt.

## Begrenzung

- Kein historischer Scheduler.
- Keine neue Versichererwahl oder VN-Praeferenzlogik.
- Keine versteckte RNG-Nutzung.
- Keine historische Vollgleichheitsbehauptung.

## Umsetzung

1. Geladenes Szenario zuerst durch den expliziten VU-Frmdinf-Regelpfad fuehren.
2. Danach im selben mutierten Szenario den expliziten VN-Settlement-Pfad anwenden.
3. Agrsich-Tabellen erst nach beiden Fachlogikschritten bauen.
4. Optionalen Mehrperiodenlauf mit strikt steigender Periodenfolge und
   expliziten Carryover-Flags bereitstellen.

## Validierung

- Test, dass ein VU-Premium aus dem Regelpfad in derselben Periode von der
  VN-Abrechnung verwendet wird.
- Tests fuer Mehrperiodenzaehlung, Carryover-Diagnose, Periodenfolge und
  Fixture-Flag-Validierung.
