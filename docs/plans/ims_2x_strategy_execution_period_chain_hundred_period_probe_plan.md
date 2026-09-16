# PR149: Kontrollierte Wirkungsprobe ueber 100 Perioden

Stand: 2026-09-16

## Ziel und Grenze

Die bereits isolierte PR148-Wirkungsprobe wird nach eigener Messung fuer
genau 100 lokale Perioden freigegeben. Die historische Obergrenze aus
`IMSDATA.C:14` wird nicht zu 300 oder 500 verlaengert. Die Periodenfolge
und Carryover-Regeln bleiben unveraendert. Das ist ein technischer Lauf,
noch keine im Browser bedienbare und dauerhaft gespeicherte Simulation.

## Versionierung und Freigabe

- Der v1-Eingang bleibt auf 10, 25 und 50 Perioden beschraenkt.
- Ein v2-Eingang akzeptiert auch 100, ausschliesslich mit expliziter
  Run-Control-Freigabe, allen 100 gespeicherten Kandidaten, 99 kanonischen
  Uebergaengen und dem erneut geprueften Fuenf-Perioden-Nachweis.
- Die v2-Antwort kennzeichnet den 100er-Lauf; der v1-Antwortvertrag fuer
  bestehende Aufrufer bleibt erhalten. Der Horizontvertrag wird v3.
- Der separate Prozess, monotone Laufzeit- und Periodenlimits, Peak-RSS,
  Payloadgrenzen und freier Plattenplatz bleiben fail-closed. Es gibt
  keine Teilantwort, kein automatisches Retry und keinen Checkpoint.

## Abnahme

- Zwei identische 100er-Läufe haben denselben fachlichen Ergebnisdigest,
  genau 100 Perioden, 99 Uebergaenge und maximal 198 Carryover-Aufrufe.
- Der Prefix 1-5 ist vor Periode 6 semantisch und als kanonisches JSON
  exakt gleich dem gespeicherten Nachweis.
- Fehler in einer spaeten Periode sowie Ressourcenabbruch liefern weder
  Periode 100 noch ein Teilergebnis; gespeicherte Kandidaten bleiben
  unveraendert. Der alte v1-Eingang sperrt 100 weiterhin.
- Reale Messwerte der kleinen Testfixtur werden mit Plattform, Grenze und
  Aussagekraft in der Migrationsnotiz festgehalten.

## Offene Punkte

Keine neue VU-/VN-Fachlogik, kein Export, keine persistierte Idempotenz,
kein UI-Start. PR150 plant das versionierte Ergebnisbuendel; PR151 den
Ergebnisarbeitsplatz. Alte Zufallsfolgen und historische Vollgleichheit
werden nicht behauptet. `incomming/` bleibt unversioniert.
