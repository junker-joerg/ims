# Vrvu04: Vorperiodenbasis fuer Nettowechsler

Dieser Slice verbreitert den bereits portierten Vrvu04-/Mark-Up-II-Kern um eine
explizite Versicherer-Zustandsbasis fuer `Vn(t-2)`.

## Ursprung im Altcode

- `IMS.E`, `act Vrvu04`
- Kommentar: `Verhaltensregel: Mark-Up II`
- Kernformel: Nettowechsler je Sparte als `Vn(t-1) - Vn(t-2)`

## Python-Abbildung

- `Insurer.policyholders_prev` und `Insurer.policyholders_prev_sector` halten
  die zweite Vorperiodenbasis fuer VU-Regeln.
- Der Szenario-Loader liest diese Felder analog zu anderen Vorperiodenvektoren.
- `VUNetSwitcherMarkupRuleSnapshot.previous_policyholders_sector` bleibt als
  expliziter Override moeglich.
- Wenn der Snapshot keinen eigenen Wert setzt, verwendet
  `apply_vu_net_switcher_markup_rule_snapshots` den Versichererzustand.
- `apply_vu_foreign_info_carryover` bewahrt diese Basis beim kontrollierten
  Fortschreiben ueber Perioden hinweg.

## Validierung

- Vrvu04-Regeltest fuer Herleitung aus `Insurer.policyholders_prev_sector`
- VU-Periodenrunner-Test fuer Snapshot ohne explizites
  `previous_policyholders_sector`
- Mehrperioden-Test, der bestaetigt, dass Carryover die Nettowechslerbasis
  fuer den Folgeperiodenlauf erhaelt
- Szenario-Loader-Test fuer die neuen Vorperiodenfelder

## Grenzen

- keine automatische historische Auswahl von VU-Regeln
- keine Herleitung aus einem vollstaendigen historischen Scheduler
- keine neue Zufallslogik
- keine Vollsimulation und keine Behauptung historischer Vollgleichheit
