# Legacy-Ziele im expliziten VU/VN-Periodenplan

## Ziel

Der explizite VU/VN-Periodenplan kann jetzt Legacy-Ziele und einen optionalen
Reportnamen beschreiben. Damit lassen sich gemeinsame VU/VN-Periodenlaeufe aus
einem Basissnapshot heraus direkt gegen kleine Agrsich-Referenzfenster pruefen.

## Ursprung im Altcode

Der fachliche Anschluss bleibt bei den historischen Agrsich-Ausgaben wie
`IMSVU*.DAT` und `IMSVNR*.DAT`. Die ausgefuehrte Fachlogik bleibt die bereits
portierte explizite VU-/VN-Kernlogik; dieser Slice portiert keine historische
Ablaufsteuerung.

## Python-Abbildung

- `ExplicitPeriodPlan` speichert optionale `legacy_targets` und
  `legacy_report_name`.
- `build_explicit_period_fixture_from_plan` uebernimmt diese Felder in das
  erzeugte Runner-Fixture.
- `run_explicit_multi_period_from_plan_fixture` loest relative Legacy-Pfade am
  Planverzeichnis auf und uebergibt `ExplicitLegacyTarget`-Objekte an den
  kombinierten Runner.

## Annahmen und Grenzen

- Legacy-Ziele bleiben explizite Referenzfenster.
- Fehlende `legacy_targets` bedeuten: keine Legacy-Validierung.
- Es wird keine historische Vollgleichheit behauptet.
