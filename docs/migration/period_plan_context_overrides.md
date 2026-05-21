# Kontext-Overrides fuer Periodenplaene

## Ziel

Dieser Slice erlaubt kontrollierten Periodenplan-Adaptern, neben `period`,
`run_index` und `rng_seed` auch `logtime` und `max_periods` pro Periodenupdate
explizit zu setzen. Dadurch koennen mehrlauf- und mehrperiodenbezogene
Agrsich-Fenster beschrieben werden, ohne vollstaendige Snapshots pro Periode zu
duplizieren.

## Ursprung im Altcode

Die fachliche Bedeutung bleibt bei den bereits portierten VU- und VN-Pfaden:
`max_periods` und `run_index` bestimmen im Python-Port die globale
Agrsich-Periodennummer, waehrend `logtime` die periodische Kontextinformation
weitertraegt. Dieser Schritt portiert keinen historischen Scheduler und keine
neue Entscheidungslogik.

## Python-Abbildung

- `ReplayPeriodUpdate`, `VNAgrsichReplayPeriodUpdate` und
  `ExplicitPeriodPlanUpdate` tragen optionale Felder fuer `logtime` und
  `max_periods`.
- Beim Fixture-Aufbau ueberschreiben diese Werte den Basiskontext nur dann,
  wenn sie im jeweiligen Periodenupdate gesetzt sind.
- Fehlen die Felder, bleibt der Basissnapshot die Quelle fuer `logtime` und
  `max_periods`.

## Annahmen und Grenzen

- Periodenplaene bleiben explizite Eingaben. Es werden keine
  Periodenentscheidungen aus historischer Vollsimulation abgeleitet.
- Die bestehenden Validierungen fuer Periodenfolge, Entity-Updates und
  Carryover-Flags bleiben unveraendert.
- Der Slice behauptet keine historische Vollgleichheit, sondern erweitert nur
  den kontrollierten Eingaberaum fuer bereits portierte Regel- und
  Exportpfade.
